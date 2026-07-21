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
    region: str = "us-east-1",
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

# ── Tests live in tests/test_cloudwatch.py ────────────────────────────────────

if __name__ == "__main__":
    print("Run:  pytest tests/test_cloudwatch.py -v")