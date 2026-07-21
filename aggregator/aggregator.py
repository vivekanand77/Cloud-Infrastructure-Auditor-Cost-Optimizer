import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from schemas import (
    EBSVolumeRecord,
    ElasticIPRecord,
    UniformRecord,
    CPURecord
)

# ── Cost constants ────────────────────────────────────────────────────────────

EIP_MONTHLY_COST: float = 3.60  # USD/month for an unassociated Elastic IP

_EBS_PRICE_PER_GB: dict[str, float] = {
    "gp2":  0.10,
    "gp3":  0.08,
    "io1":  0.125,
    "io2":  0.125,
    "st1":  0.045,
    "sc1":  0.025,
    "standard": 0.05,
}

# Average on-demand hourly price (t3.medium equivalent) used as a proxy for
# idle EC2 waste estimation when the actual instance type is not available.
_EC2_DEFAULT_HOURLY_RATE: float = 0.0416  # USD/h  (t3.medium, us-east-1)
_HOURS_PER_MONTH: int = 720


def estimate_ebs_cost(volume_type: str, size_gb: int | float) -> float:
    """Return estimated monthly cost in USD for an EBS volume."""
    price_per_gb = _EBS_PRICE_PER_GB.get(volume_type.lower(), 0.10)
    return round(price_per_gb * size_gb, 10)


def estimate_ec2_idle_cost(hourly_rate: float = _EC2_DEFAULT_HOURLY_RATE) -> float:
    """Return estimated monthly waste cost in USD for an idle EC2 instance."""
    return round(hourly_rate * _HOURS_PER_MONTH, 10)


def aggregate_data(
    nancy_ebs: list[EBSVolumeRecord],
    nancy_eip: list[ElasticIPRecord],
    lahari_cpu: list[CPURecord]
) -> list[UniformRecord]:

    combined: list[UniformRecord] = []

    for record in nancy_ebs:
        combined.append({
            "resource_id": record["volume_id"],
            "resource_type": "EBS",
            "region": record["region"],
            "status": "idle",
            "metric_value": float(record["size_gb"]),
            "estimated_waste_usd": estimate_ebs_cost(record["volume_type"], record["size_gb"]),
            "tags": {}
        })

    for record in nancy_eip:
        combined.append({
            "resource_id": record["allocation_id"],
            "resource_type": "EIP",
            "region": record["region"],
            "status": "idle",
            "metric_value": 0.0,
            "estimated_waste_usd": EIP_MONTHLY_COST,
            "tags": {}
        })
        
    for record in lahari_cpu:
        combined.append({
            "resource_id": record["instance_id"],
            "resource_type": "EC2-CPU",
            "region": record["region"],
            "status": "underutilized",
            "metric_value": record["avg_cpu_percent"],
            "estimated_waste_usd": estimate_ec2_idle_cost(),
            "tags": {}
        })

    return combined


if __name__ == "__main__":
    mock_ebs = [{
        "volume_id": "vol-0abc123",
        "size_gb": 100,
        "volume_type": "gp2",
        "region": "us-east-1",
        "state": "available",
        "attached_instance_id": None
    }]

    mock_eip = [{
        "allocation_id": "eipalloc-0xyz",
        "public_ip": "3.4.5.6",
        "region": "us-east-1",
        "associated": False,
        "instance_id": None
    }]

    mock_cpu = [
    {
        "instance_id": "i-aaa",
        "region": "us-east-1",
        "avg_cpu_percent": 2.88,
        "is_flagged": True,
        "account_id": "123456789012",
        "flagged_at": "2026-06-28T12:00:00+00:00"
    },
    {
        "instance_id": "i-bbb",
        "region": "us-east-1",
        "avg_cpu_percent": 3.1,
        "is_flagged": True,
        "account_id": "123456789012",
        "flagged_at": "2026-06-28T12:00:00+00:00"
    }
]

    result = aggregate_data(mock_ebs, mock_eip, mock_cpu)
    for item in result:
        print(item)