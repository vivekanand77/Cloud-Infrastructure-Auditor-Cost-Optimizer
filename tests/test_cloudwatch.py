"""
tests/test_cloudwatch.py
Stubber-based tests for cloudwatch_metrics.py — moved out of the production module.
No real AWS calls are made here.
"""
import pytest
from datetime import datetime, timedelta, timezone
from botocore.stub import Stubber
import boto3

from cloudwatch_metrics import (
    calc_average_cpu,
    build_time_window,
    list_all_instance_ids,
    filter_underutilized,
    get_cpu_for_instance,
)

UTC = timezone.utc

# ── Helpers ────────────────────────────────────────────────────────────────────

NOW   = datetime(2026, 6, 28, 12, 0, 0, tzinfo=UTC)
START = NOW - timedelta(days=14)

def dp(offset_days, avg):
    """Build a fake CloudWatch datapoint."""
    return {"Timestamp": START + timedelta(days=offset_days), "Average": avg, "Unit": "Percent"}


# ── Unit tests: pure functions (no boto3 needed) ───────────────────────────────

def test_calc_average_cpu_normal():
    datapoints = [dp(0, 2.1), dp(2, 3.4), dp(5, 1.8), dp(9, 4.2), dp(13, 2.9)]
    assert calc_average_cpu(datapoints) == 2.88   # (2.1+3.4+1.8+4.2+2.9)/5

def test_calc_average_cpu_empty():
    assert calc_average_cpu([]) == 0.0

def test_build_time_window_spans_correct_days():
    start, end = build_time_window(days=14)
    assert (end - start).days == 14


# ── Integration tests: botocore Stubber ───────────────────────────────────────

def _make_stubbed_cw():
    """Return a (cloudwatch_client, Stubber) pair — caller must enter the stubber."""
    session = boto3.Session(region_name="us-east-1")
    cw = session.client("cloudwatch", region_name="us-east-1")
    return cw, Stubber(cw)


def test_list_all_instance_ids():
    cw, stub = _make_stubbed_cw()
    stub.add_response(
        "list_metrics",
        {"Metrics": [
            {"Namespace": "AWS/EC2", "MetricName": "CPUUtilization",
             "Dimensions": [{"Name": "InstanceId", "Value": "i-aaa"}]},
            {"Namespace": "AWS/EC2", "MetricName": "CPUUtilization",
             "Dimensions": [{"Name": "InstanceId", "Value": "i-bbb"}]},
        ], "ResponseMetadata": {}},
        {"Namespace": "AWS/EC2", "MetricName": "CPUUtilization"},
    )
    with stub:
        ids = list_all_instance_ids(cw)
    assert ids == ["i-aaa", "i-bbb"]


def test_filter_underutilized_flags_low_cpu_only():
    """i-aaa (avg 2.88%) and i-bbb (avg 3.10%) should be flagged; i-ccc (avg 45.5%) should not."""
    cw, stub = _make_stubbed_cw()

    base = {
        "Namespace": "AWS/EC2", "MetricName": "CPUUtilization",
        "StartTime": START, "EndTime": NOW, "Period": 86400, "Statistics": ["Average"],
    }

    stub.add_response("get_metric_statistics",
        {"Datapoints": [dp(0, 2.1), dp(2, 3.4), dp(5, 1.8), dp(9, 4.2), dp(13, 2.9)], "ResponseMetadata": {}},
        {**base, "Dimensions": [{"Name": "InstanceId", "Value": "i-aaa"}]},
    )
    stub.add_response("get_metric_statistics",
        {"Datapoints": [dp(1, 2.5), dp(4, 3.8), dp(8, 2.9), dp(12, 3.2)], "ResponseMetadata": {}},
        {**base, "Dimensions": [{"Name": "InstanceId", "Value": "i-bbb"}]},
    )
    stub.add_response("get_metric_statistics",
        {"Datapoints": [dp(3, 40.0), dp(10, 51.0)], "ResponseMetadata": {}},
        {**base, "Dimensions": [{"Name": "InstanceId", "Value": "i-ccc"}]},
    )

    with stub:
        results = filter_underutilized(["i-aaa", "i-bbb", "i-ccc"], cw, threshold=5.0,
                                       start_time=START, end_time=NOW)

    assert len(results) == 2
    ids_found = [r[0] for r in results]
    assert "i-aaa" in ids_found
    assert "i-bbb" in ids_found
    assert "i-ccc" not in ids_found

    # spot-check avg values
    avg_by_id = {r[0]: r[1] for r in results}
    assert avg_by_id["i-aaa"] == pytest.approx(2.88, abs=0.01)
    assert avg_by_id["i-bbb"] == pytest.approx(3.1, abs=0.01)
