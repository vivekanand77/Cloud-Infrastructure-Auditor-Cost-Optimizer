import boto3
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

    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

    paginator = ec2.get_paginator("describe_volumes")

    unattached_volumes = []

    for page in paginator.paginate():

        for volume in page["Volumes"]:

            if volume["State"] == "available":

                unattached_volumes.append(
                    {
                        "volume_id": volume["VolumeId"],
                        "size_gb": volume["Size"],
                        "volume_type": volume["VolumeType"],
                        "region": "us-east-1",
                        "state": volume["State"],
                        "attached_instance_id": None,
                    }
                )

    return unattached_volumes

def get_unassociated_elastic_ips() -> list[ElasticIPRecord]:

    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

    response = ec2.describe_addresses()
    

    unassociated_ips = []

    for address in response["Addresses"]:

        if not address.get("InstanceId"):

            unassociated_ips.append(
                {
                    "allocation_id": address.get("AllocationId"),
                    "public_ip": address.get("PublicIp"),
                    "region": "us-east-1",
                    "associated": False,
                    "instance_id": None,
                }
            )

    return unassociated_ips