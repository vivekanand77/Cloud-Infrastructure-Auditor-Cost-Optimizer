from typing import TypedDict, Optional


class EBSVolumeRecord(TypedDict):
    volume_id: str
    size_gb: int
    volume_type: str
    region: str
    state: str
    attached_instance_id: Optional[str]
    tags: dict


class ElasticIPRecord(TypedDict):
    allocation_id: str
    public_ip: str
    region: str
    associated: bool
    instance_id: Optional[str]
    tags: dict


class UniformRecord(TypedDict):
    resource_id: str
    resource_type: str
    region: str
    status: str
    metric_value: float
    estimated_waste_usd: float
    tags: dict

class CPURecord(TypedDict):
    instance_id: str
    region: str
    avg_cpu_percent: float
    is_flagged: bool
    account_id: str
    flagged_at: str