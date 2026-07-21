import boto3
from moto import mock_aws


@mock_aws
def test_fake_aws():

    ec2 = boto3.client("ec2", region_name="us-east-1")

    ec2.create_volume(
        Size=100,
        AvailabilityZone="us-east-1a",
        VolumeType="gp3"
    )

    ec2.create_volume(
        Size=200,
        AvailabilityZone="us-east-1a",
        VolumeType="gp2"
    )

    response = ec2.describe_volumes()

    print("Volumes found:")

    for volume in response["Volumes"]:
        print(volume["VolumeId"])
        print("State:", volume["State"])
        print("Size:", volume["Size"])
        print("------")


if __name__ == "__main__":
    test_fake_aws()