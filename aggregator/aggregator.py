import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from schemas import (
    EBSVolumeRecord,
    ElasticIPRecord,
    UniformRecord,
    CPURecord
)


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
            "estimated_waste_usd": 0.0,
            "tags": {}
        })

    for record in nancy_eip:
        combined.append({
            "resource_id": record["allocation_id"],
            "resource_type": "EIP",
            "region": record["region"],
            "status": "idle",
            "metric_value": 0.0,
            "estimated_waste_usd": 3.6,
            "tags": {}
        })
        
    for record in lahari_cpu:
        combined.append({
            "resource_id": record["instance_id"],
            "resource_type": "EC2-CPU",
            "region": record["region"],
            "status": "underutilized",
            "metric_value": record["avg_cpu_percent"],
            "estimated_waste_usd": 0.0,
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