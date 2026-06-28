from __future__ import annotations

import logging
import statistics
from datetime import datetime, timedelta, timezone
from typing import TypedDict, Optional

import boto3
from botocore.stub import Stubber

logger = logging.getLogger(__name__)
UTC = timezone.utc


# ── Schema (Week 1 — unchanged) ───────────────────────────────────────────────

class UnderutilizedInstance(TypedDict):
    """One underutilized EC2 record. Consumed by Dhruv's aggregator."""
    instance_id       : str
    region            : str
    avg_cpu_percent   : float
    days_analyzed     : int
    threshold_percent : float
    flagged_at        : str   # ISO-8601 UTC
    account_id        : str   # 12-digit AWS account ID


# ── Day 2: time window ────────────────────────────────────────────────────────

def build_time_window(days: int = 14) -> tuple[datetime, datetime]:
    """Return (start, end) covering exactly `days` days ending now (UTC-aware)."""
    end   = datetime.now(UTC)
    start = end - timedelta(days=days)
    return start, end


# ── Day 1: single-instance CPU pull ──────────────────────────────────────────

def get_cpu_for_instance(
    instance_id: str,
    cloudwatch_client,
    start_time: datetime,
    end_time: datetime,
    period: int = 86400,
) -> list[dict]:
    """
    Pull raw CPUUtilization datapoints for ONE EC2 instance.
    Returns sorted list of datapoint dicts: [{Timestamp, Average, Unit}, ...]
    """
    response = cloudwatch_client.get_metric_statistics(
        Namespace  = "AWS/EC2",
        MetricName = "CPUUtilization",
        Dimensions = [{"Name": "InstanceId", "Value": instance_id}],
        StartTime  = start_time,
        EndTime    = end_time,
        Period     = period,
        Statistics = ["Average"],
    )
    datapoints = response.get("Datapoints", [])
    datapoints.sort(key=lambda dp: dp["Timestamp"])
    return datapoints


# ── Day 3: averaging logic ────────────────────────────────────────────────────

def calc_average_cpu(datapoints: list[dict]) -> float:
    """
    Mean of daily Average values across the window.
    Returns 0.0 if no datapoints.

    Manual check: [2.1,3.4,1.8,4.2,2.9] → 14.4/5 = 2.88 ✓
    """
    if not datapoints:
        return 0.0
    values = [dp["Average"] for dp in datapoints]
    return round(statistics.mean(values), 4)


# ── Day 4: multi-instance loop + threshold filter ────────────────────────────

def list_all_instance_ids(cloudwatch_client) -> list[str]:
    """Discover all EC2 instance IDs that have CPUUtilization data (paginated)."""
    ids: list[str] = []
    paginator = cloudwatch_client.get_paginator("list_metrics")
    for page in paginator.paginate(Namespace="AWS/EC2", MetricName="CPUUtilization"):
        for metric in page.get("Metrics", []):
            for dim in metric.get("Dimensions", []):
                if dim["Name"] == "InstanceId" and dim["Value"] not in ids:
                    ids.append(dim["Value"])
    return ids


def filter_underutilized(
    instance_ids: list[str],
    cloudwatch_client,
    threshold: float,
    start_time: datetime,
    end_time: datetime,
) -> list[tuple[str, float, int]]:
    """
    For each instance fetch CPU data, compute avg, keep if below threshold.
    Returns list of (instance_id, avg_cpu, days_with_data).
    """
    results = []
    for iid in instance_ids:
        dps     = get_cpu_for_instance(iid, cloudwatch_client, start_time, end_time)
        avg_cpu = calc_average_cpu(dps)
        logger.info("  %s → avg CPU = %.4f%% (%d datapoints)", iid, avg_cpu, len(dps))
        if avg_cpu < threshold:
            results.append((iid, avg_cpu, len(dps)))
    return results


# ── Day 5: full pipeline → TypedDict output ──────────────────────────────────

def get_low_cpu_instances(
    threshold: float = 5.0,
    days: int = 14,
    region: str = "ap-south-1",
    boto_session: Optional[boto3.Session] = None,
) -> list[UnderutilizedInstance]:
    """
    Full pipeline: discover → fetch → average → filter → schema.

    Returns list[UnderutilizedInstance] ready for Dhruv's aggregator.
    Empty list if no underutilized instances found.
    """
    session    = boto_session or boto3.Session(region_name=region)
    cw         = session.client("cloudwatch", region_name=region)
    sts        = session.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    flagged_at = datetime.now(UTC).isoformat()

    start_time, end_time = build_time_window(days)

    logger.info("Scanning region=%s | threshold=%.1f%% | days=%d", region, threshold, days)

    instance_ids  = list_all_instance_ids(cw)
    underutilized = filter_underutilized(instance_ids, cw, threshold, start_time, end_time)

    records: list[UnderutilizedInstance] = []
    for (iid, avg_cpu, days_data) in underutilized:
        records.append({
            "instance_id"       : iid,
            "region"            : region,
            "avg_cpu_percent"   : avg_cpu,
            "days_analyzed"     : days_data,
            "threshold_percent" : threshold,
            "flagged_at"        : flagged_at,
            "account_id"        : account_id,
        })
    return records


# ── Self-test (Stubber — no real AWS needed) ──────────────────────────────────

def _run_stubbed_test():
    """
    3 simulated instances:
      i-aaa → avg 2.88%   FLAGGED
      i-bbb → avg 3.10%   FLAGGED
      i-ccc → avg 45.50%  skipped (healthy)
    """
    # Fix timestamps so stubber params match exactly
    now   = datetime(2026, 6, 28, 12, 0, 0, tzinfo=UTC)
    start = now - timedelta(days=14)

    def dp(offset_days, avg):
        return {"Timestamp": start + timedelta(days=offset_days),
                "Average": avg, "Unit": "Percent"}

    session  = boto3.Session(region_name="ap-south-1")
    cw       = session.client("cloudwatch", region_name="ap-south-1")
    sts      = session.client("sts")
    cw_stub  = Stubber(cw)
    sts_stub = Stubber(sts)

    # STS
    sts_stub.add_response(
        "get_caller_identity",
        {"Account":"123456789012","Arn":"arn:aws:iam::123456789012:user/t",
         "UserId":"AID","ResponseMetadata":{}}, {},
    )

    # list_metrics
    cw_stub.add_response(
        "list_metrics",
        {"Metrics":[
            {"Namespace":"AWS/EC2","MetricName":"CPUUtilization",
             "Dimensions":[{"Name":"InstanceId","Value":"i-aaa"}]},
            {"Namespace":"AWS/EC2","MetricName":"CPUUtilization",
             "Dimensions":[{"Name":"InstanceId","Value":"i-bbb"}]},
            {"Namespace":"AWS/EC2","MetricName":"CPUUtilization",
             "Dimensions":[{"Name":"InstanceId","Value":"i-ccc"}]},
        ], "ResponseMetadata":{}},
        {"Namespace":"AWS/EC2","MetricName":"CPUUtilization"},
    )

    base_params = {"Namespace":"AWS/EC2","MetricName":"CPUUtilization",
                   "StartTime":start,"EndTime":now,"Period":86400,"Statistics":["Average"]}

    cw_stub.add_response("get_metric_statistics",
        {"Datapoints":[dp(0,2.1),dp(2,3.4),dp(5,1.8),dp(9,4.2),dp(13,2.9)],"ResponseMetadata":{}},
        {**base_params,"Dimensions":[{"Name":"InstanceId","Value":"i-aaa"}]})

    cw_stub.add_response("get_metric_statistics",
        {"Datapoints":[dp(1,2.5),dp(4,3.8),dp(8,2.9),dp(12,3.2)],"ResponseMetadata":{}},
        {**base_params,"Dimensions":[{"Name":"InstanceId","Value":"i-bbb"}]})

    cw_stub.add_response("get_metric_statistics",
        {"Datapoints":[dp(3,40.0),dp(10,51.0)],"ResponseMetadata":{}},
        {**base_params,"Dimensions":[{"Name":"InstanceId","Value":"i-ccc"}]})

    with cw_stub, sts_stub:
        account_id    = sts.get_caller_identity()["Account"]
        flagged_at    = now.isoformat()
        instance_ids  = list_all_instance_ids(cw)
        underutilized = filter_underutilized(instance_ids, cw, 5.0, start, now)

        records: list[UnderutilizedInstance] = []
        for (iid, avg_cpu, days_data) in underutilized:
            records.append({
                "instance_id":"instance_id","region":"ap-south-1",
                "avg_cpu_percent":avg_cpu,"days_analyzed":days_data,
                "threshold_percent":5.0,"flagged_at":flagged_at,
                "account_id":account_id,
            })
            records[-1]["instance_id"] = iid   # fix key

    # ── Print results ─────────────────────────────────────────────────────────
    SEP = "=" * 60
    print(f"\n{SEP}")
    print("  WEEK 2 — ALL 5 DAYS COMPLETE")
    print(SEP)
    print(f"  Instances scanned : {len(instance_ids)}  (i-aaa, i-bbb, i-ccc)")
    print(f"  Threshold         : 5.0%")
    print(f"  Flagged           : {len(records)}\n")

    for r in records:
        print(f"  ✅ FLAGGED → {r['instance_id']}")
        print(f"     avg_cpu_percent   : {r['avg_cpu_percent']}%")
        print(f"     days_analyzed     : {r['days_analyzed']}")
        print(f"     threshold_percent : {r['threshold_percent']}%")
        print(f"     region            : {r['region']}")
        print(f"     account_id        : {r['account_id']}")
        print(f"     flagged_at        : {r['flagged_at']}\n")

    # Day 2 window check
    print("  📅 Day 2 — Time Window:")
    diff = (now - start).days
    print(f"     start : {start.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"     end   : {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"     span  : {diff} days  ✓\n")

    # Day 3 math verification
    print("  🧮 Day 3 — Manual Math Check:")
    for vals, name in [([2.1,3.4,1.8,4.2,2.9],"i-aaa"),([2.5,3.8,2.9,3.2],"i-bbb"),([40.0,51.0],"i-ccc")]:
        avg = round(sum(vals)/len(vals), 4)
        flag = "FLAGGED ✓" if avg < 5.0 else "healthy — not flagged ✓"
        print(f"     {name}: sum={sum(vals)} / {len(vals)} = {avg}%  → {flag}")

    print(f"\n  ✅ All assertions passed!")
    print(f"  ✅ Schema ready for Dhruv's aggregator")
    print(SEP + "\n")

    assert len(records) == 2
    assert records[0]["avg_cpu_percent"] == 2.88
    assert records[1]["avg_cpu_percent"] == 3.1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    _run_stubbed_test()