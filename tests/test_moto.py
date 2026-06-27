from moto import mock_aws
import boto3

from scanners.asset_retrieval import (
    get_unattached_ebs_volumes,
    get_unassociated_elastic_ips,
)


@mock_aws
def test_week3_day1():

    # Create fake EC2 client
    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

    # ---------------------------------
    # Create known test resources
    # ---------------------------------

    volume1 = ec2.create_volume(
        Size=100,
        AvailabilityZone="us-east-1a"
    )

    volume2 = ec2.create_volume(
        Size=200,
        AvailabilityZone="us-east-1a"
    )

    elastic_ip = ec2.allocate_address(
        Domain="vpc"
    )

    # ---------------------------------
    # Expected Resources
    # ---------------------------------

    print("\n==============================")
    print("EXPECTED RESOURCES")
    print("==============================")

    print(f"Volume 1 ID : {volume1['VolumeId']}")
    print("Size        : 100 GB")
    print("State       : available")

    print()

    print(f"Volume 2 ID : {volume2['VolumeId']}")
    print("Size        : 200 GB")
    print("State       : available")

    print()

    print(f"Elastic IP Allocation ID : {elastic_ip['AllocationId']}")
    print(f"Public IP                : {elastic_ip['PublicIp']}")
    print("Associated               : False")

    # ---------------------------------
    # Run your scanner
    # ---------------------------------

    ebs_results = get_unattached_ebs_volumes()
    elastic_results = get_unassociated_elastic_ips()

    # ---------------------------------
    # Scanner Output
    # ---------------------------------

    print("\n==============================")
    print("SCANNER OUTPUT")
    print("==============================")

    print("\nEBS Volumes Found:")

    for volume in ebs_results:
        print(volume)

    print("\nElastic IPs Found:")

    for ip in elastic_results:
        print(ip)

    # ---------------------------------
    # Verification
    # ---------------------------------

    print("\n==============================")
    print("VERIFICATION")
    print("==============================")

    assert len(ebs_results) == 2
    print("✓ Correct number of EBS volumes detected.")

    assert len(elastic_results) == 1
    print("✓ Correct number of Elastic IPs detected.")

    # Verify volume IDs
    volume_ids = {volume["volume_id"] for volume in ebs_results}

    assert volume1["VolumeId"] in volume_ids
    assert volume2["VolumeId"] in volume_ids

    print("✓ Volume IDs match.")

    # Verify sizes
    sizes = sorted(volume["size_gb"] for volume in ebs_results)

    assert sizes == [100, 200]

    print("✓ Volume sizes match.")

    # Verify Elastic IP

    assert (
        elastic_results[0]["allocation_id"]
        == elastic_ip["AllocationId"]
    )

    print("✓ Elastic IP Allocation ID matches.")

    assert elastic_results[0]["associated"] is False

    print("✓ Elastic IP is correctly reported as unassociated.")


if __name__ == "__main__":
    test_week3_day1()