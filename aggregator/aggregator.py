from schemas import (
    EBSVolumeRecord,
    ElasticIPRecord,
    UniformRecord
)


def aggregate_data(
    nancy_ebs: list[EBSVolumeRecord],
    nancy_eip: list[ElasticIPRecord],
    lahari_cpu: list[dict]
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

    result = aggregate_data(mock_ebs, mock_eip, [])
    for item in result:
        print(item)