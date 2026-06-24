from typing import TypedDict, Optional


class EBSVolumeRecord(TypedDict):
    volume_id: str
    size_gb: int
    volume_type: str
    region: str
    state: str
    attached_instance_id: Optional[str]


class ElasticIPRecord(TypedDict):
    allocation_id: str
    public_ip: str
    region: str
    associated: bool
    instance_id: Optional[str]


class UniformRecord(TypedDict):
    resource_id: str
    resource_type: str
    region: str
    status: str
    metric_value: float
    estimated_waste_usd: float
    tags: dict