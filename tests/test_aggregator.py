"""
tests/test_aggregator.py — Unit tests for aggregation and cost estimation.
"""
import pytest
from aggregator.aggregator import (
    aggregate_data,
    estimate_ebs_cost,
    estimate_ec2_idle_cost,
    EIP_MONTHLY_COST,
)


# ── Cost estimation unit tests ────────────────────────────────────────────────

def test_ebs_cost_gp2():
    assert estimate_ebs_cost("gp2", 100) == 10.0   # $0.10 * 100

def test_ebs_cost_gp3():
    assert estimate_ebs_cost("gp3", 100) == 8.0    # $0.08 * 100

def test_ebs_cost_io1():
    assert estimate_ebs_cost("io1", 200) == 25.0   # $0.125 * 200

def test_ebs_cost_unknown_type_defaults_to_gp2_rate():
    assert estimate_ebs_cost("unknown", 50) == 5.0  # falls back to $0.10

def test_ebs_cost_zero_size():
    assert estimate_ebs_cost("gp2", 0) == 0.0

def test_eip_monthly_cost_value():
    assert EIP_MONTHLY_COST == 3.60

def test_ec2_idle_cost_default():
    # default: 0.0416 * 720 = 29.952
    result = estimate_ec2_idle_cost()
    assert round(result, 3) == 29.952

def test_ec2_idle_cost_custom_rate():
    # $0.10/h * 720 = $72.00
    assert estimate_ec2_idle_cost(0.10) == 72.0


# ── aggregate_data integration tests ─────────────────────────────────────────

MOCK_EBS = [{
    "volume_id": "vol-0abc123",
    "size_gb": 100,
    "volume_type": "gp2",
    "region": "us-east-1",
    "state": "available",
    "attached_instance_id": None,
}]

MOCK_EIP = [{
    "allocation_id": "eipalloc-0xyz",
    "public_ip": "3.4.5.6",
    "region": "us-east-1",
    "associated": False,
    "instance_id": None,
}]

MOCK_CPU = [
    {
        "instance_id": "i-aaa",
        "region": "us-east-1",
        "avg_cpu_percent": 2.88,
        "is_flagged": True,
        "account_id": "123456789012",
        "flagged_at": "2026-06-28T12:00:00+00:00",
    },
]


def test_aggregate_data_returns_list():
    result = aggregate_data(MOCK_EBS, MOCK_EIP, MOCK_CPU)
    assert isinstance(result, list)


def test_aggregate_data_correct_count():
    result = aggregate_data(MOCK_EBS, MOCK_EIP, MOCK_CPU)
    # 1 EBS + 1 EIP + 1 CPU = 3 records
    assert len(result) == 3


def test_aggregate_data_ebs_record():
    result = aggregate_data(MOCK_EBS, [], [])
    ebs = result[0]
    assert ebs["resource_id"] == "vol-0abc123"
    assert ebs["resource_type"] == "EBS"
    assert ebs["region"] == "us-east-1"
    assert ebs["status"] == "idle"
    assert ebs["metric_value"] == 100.0


def test_aggregate_data_eip_record():
    result = aggregate_data([], MOCK_EIP, [])
    eip = result[0]
    assert eip["resource_id"] == "eipalloc-0xyz"
    assert eip["resource_type"] == "EIP"
    assert eip["estimated_waste_usd"] == 3.6


def test_aggregate_data_cpu_record():
    result = aggregate_data([], [], MOCK_CPU)
    cpu = result[0]
    assert cpu["resource_id"] == "i-aaa"
    assert cpu["resource_type"] == "EC2-CPU"
    assert cpu["status"] == "underutilized"
    assert cpu["metric_value"] == 2.88


def test_aggregate_data_empty_inputs():
    result = aggregate_data([], [], [])
    assert result == []
