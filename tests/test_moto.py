import boto3
from moto import mock_aws
from scanners.asset_retrieval import get_unattached_ebs_volumes


@mock_aws
def test_fake_aws_creates_volumes():
    """moto smoke-test: two new volumes should both show up as 'available'."""
    ec2 = boto3.client("ec2", region_name="us-east-1")

    ec2.create_volume(Size=100, AvailabilityZone="us-east-1a", VolumeType="gp3")
    ec2.create_volume(Size=200, AvailabilityZone="us-east-1a", VolumeType="gp2")

    response = ec2.describe_volumes()
    volumes = response["Volumes"]

    assert len(volumes) == 2
    types = {v["VolumeType"] for v in volumes}
    assert "gp3" in types
    assert "gp2" in types
    for v in volumes:
        assert v["State"] == "available"


@mock_aws
def test_scanner_picks_up_unattached_volumes():
    """get_unattached_ebs_volumes() should return the volumes we just created."""
    ec2 = boto3.client("ec2", region_name="us-east-1")
    ec2.create_volume(Size=50, AvailabilityZone="us-east-1a", VolumeType="gp2")

    results = get_unattached_ebs_volumes(region="us-east-1")

    assert len(results) == 1
    assert results[0]["size_gb"] == 50
    assert results[0]["volume_type"] == "gp2"
    assert results[0]["region"] == "us-east-1"
    assert results[0]["state"] == "available"