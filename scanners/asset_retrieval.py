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

    volumes = [
        {
            "volume_id": "vol-111",
            "size_gb": 50,
            "volume_type": "gp3",
            "region": "us-east-1",
            "state": "in-use",
            "attached_instance_id": "i-123",
        },
        {
            "volume_id": "vol-222",
            "size_gb": 100,
            "volume_type": "gp3",
            "region": "us-east-1",
            "state": "available",
            "attached_instance_id": None,
        },
        {
            "volume_id": "vol-333",
            "size_gb": 200,
            "volume_type": "gp2",
            "region": "us-west-2",
            "state": "available",
            "attached_instance_id": None,
        },
    ]

    unattached_volumes = []

    for volume in volumes:
        if volume["attached_instance_id"] is None:
            unattached_volumes.append(volume)

    return unattached_volumes

def get_unassociated_elastic_ips() -> list[ElasticIPRecord]:

    elastic_ips = [
        {
            "allocation_id": "eipalloc-111",
            "public_ip": "54.1.1.1",
            "region": "us-east-1",
            "associated": True,
            "instance_id": "i-123",
        },
        {
            "allocation_id": "eipalloc-222",
            "public_ip": "54.2.2.2",
            "region": "us-east-1",
            "associated": False,
            "instance_id": None,
        },
        {
            "allocation_id": "eipalloc-333",
            "public_ip": "54.3.3.3",
            "region": "us-west-2",
            "associated": False,
            "instance_id": None,
        },
    ]

    unassociated_ips = []

    for ip in elastic_ips:
        if ip["associated"] is False:
            unassociated_ips.append(ip)

    return unassociated_ips
if __name__ == "__main__":
    print(get_unattached_ebs_volumes())
    print(get_unassociated_elastic_ips())