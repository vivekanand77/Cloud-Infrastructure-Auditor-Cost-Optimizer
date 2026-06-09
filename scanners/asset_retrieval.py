from typing import TypedDict, Optional


class EBSVolumeRecord(TypedDict):
    """
    Schema representing an unattached EBS volume.
    """

    volume_id: str
    size_gb: int
    volume_type: str
    region: str
    state: str
    attached_instance_id: Optional[str]


class ElasticIPRecord(TypedDict):
    """
    Schema representing an unassociated Elastic IP.
    """

    allocation_id: str
    public_ip: str
    region: str
    associated: bool
    instance_id: Optional[str]


def get_unattached_ebs_volumes() -> list[EBSVolumeRecord]:
    """
    Retrieve unattached EBS volumes.

    Returns:
        List of EBS volume records.
    """
    return []


def get_unassociated_elastic_ips() -> list[ElasticIPRecord]:
    """
    Retrieve unassociated Elastic IP addresses.

    Returns:
        List of Elastic IP records.
    """
    return []