import boto3
from typing import Optional
from aggregator.schemas import EBSVolumeRecord, ElasticIPRecord

def get_unattached_ebs_volumes(
    session: Optional[boto3.Session] = None,
    region: str = "us-east-1"
) -> list[EBSVolumeRecord]:
    """
    Return all EBS volumes in 'available' state (not attached to any instance).
    """
    sess = session or boto3.Session(region_name=region)
    ec2 = sess.client("ec2", region_name=region)

    paginator = ec2.get_paginator("describe_volumes")
    unattached_volumes: list[EBSVolumeRecord] = []

    for page in paginator.paginate():
        for volume in page["Volumes"]:
            if volume["State"] == "available":
                unattached_volumes.append(
                    {
                        "volume_id": volume["VolumeId"],
                        "size_gb": volume["Size"],
                        "volume_type": volume["VolumeType"],
                        "region": region,
                        "state": volume["State"],
                        "attached_instance_id": None,
                        "tags": {t["Key"]: t["Value"] for t in volume.get("Tags", [])} if "Tags" in volume else {}
                    }
                )

    return unattached_volumes

def get_unassociated_elastic_ips(
    session: Optional[boto3.Session] = None,
    region: str = "us-east-1"
) -> list[ElasticIPRecord]:
    """
    Return all Elastic IPs that are not associated with any instance or network interface.
    """
    sess = session or boto3.Session(region_name=region)
    ec2 = sess.client("ec2", region_name=region)

    paginator = ec2.get_paginator("describe_addresses")
    unassociated_ips: list[ElasticIPRecord] = []

    for page in paginator.paginate():
        for address in page["Addresses"]:
            if "InstanceId" not in address:
                unassociated_ips.append(
                    {
                        "allocation_id": address.get("AllocationId", ""),
                        "public_ip": address.get("PublicIp", ""),
                        "region": region,
                        "associated": False,
                        "instance_id": None,
                        "tags": {t["Key"]: t["Value"] for t in address.get("Tags", [])} if "Tags" in address else {}
                    }
                )

    return unassociated_ips
