from moto import mock_aws
import boto3

from scanners.asset_retrieval import (
    get_unattached_ebs_volumes,
    get_unassociated_elastic_ips,
)


@mock_aws
def test_week3_day2():

    # ------------------------------------
    # Create fake EC2 client
    # ------------------------------------

    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

    # ------------------------------------
    # Create known AWS resources
    # ------------------------------------

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

    # ------------------------------------
    # Expected Resources
    # ------------------------------------

    print("\n========================================")
    print("EXPECTED AWS RESOURCES")
    print("========================================")

    print("\nVolume 1")
    print(f"Volume ID : {volume1['VolumeId']}")
    print("Size      : 100 GB")
    print("State     : available")
    print("Region    : us-east-1")

    print("\nVolume 2")
    print(f"Volume ID : {volume2['VolumeId']}")
    print("Size      : 200 GB")
    print("State     : available")
    print("Region    : us-east-1")

    print("\nElastic IP")
    print(f"Allocation ID : {elastic_ip['AllocationId']}")
    print(f"Public IP     : {elastic_ip['PublicIp']}")
    print("Associated    : False")
    print("Region         : us-east-1")

    # ------------------------------------
    # Run Scanner
    # ------------------------------------

    ebs_results = get_unattached_ebs_volumes()
    elastic_results = get_unassociated_elastic_ips()

    # ------------------------------------
    # Scanner Output
    # ------------------------------------

    print("\n========================================")
    print("SCANNER OUTPUT")
    print("========================================")

    print("\nEBS Volumes")

    for volume in ebs_results:
        print(volume)

    print("\nElastic IPs")

    for ip in elastic_results:
        print(ip)

    # ------------------------------------
    # Manual Field Comparison
    # ------------------------------------

    print("\n========================================")
    print("FIELD BY FIELD COMPARISON")
    print("========================================")

    # ---------- Volume 1 ----------

    print("\nVolume 1")

    print(f"AWS Volume ID      : {volume1['VolumeId']}")
    print(f"Scanner Volume ID  : {ebs_results[0]['volume_id']}")

    print(f"AWS Size           : 100")
    print(f"Scanner Size       : {ebs_results[0]['size_gb']}")

    print(f"AWS State          : available")
    print(f"Scanner State      : {ebs_results[0]['state']}")

    print(f"AWS Region         : us-east-1")
    print(f"Scanner Region     : {ebs_results[0]['region']}")

    # ---------- Volume 2 ----------

    print("\n----------------------------------------")

    print("\nVolume 2")

    print(f"AWS Volume ID      : {volume2['VolumeId']}")
    print(f"Scanner Volume ID  : {ebs_results[1]['volume_id']}")

    print(f"AWS Size           : 200")
    print(f"Scanner Size       : {ebs_results[1]['size_gb']}")

    print(f"AWS State          : available")
    print(f"Scanner State      : {ebs_results[1]['state']}")

    print(f"AWS Region         : us-east-1")
    print(f"Scanner Region     : {ebs_results[1]['region']}")

    # ---------- Elastic IP ----------

    print("\n----------------------------------------")

    print("\nElastic IP")

    print(f"AWS Allocation ID      : {elastic_ip['AllocationId']}")
    print(f"Scanner Allocation ID  : {elastic_results[0]['allocation_id']}")

    print(f"AWS Public IP          : {elastic_ip['PublicIp']}")
    print(f"Scanner Public IP      : {elastic_results[0]['public_ip']}")

    print(f"AWS Associated         : False")
    print(f"Scanner Associated     : {elastic_results[0]['associated']}")

    print(f"AWS Region             : us-east-1")
    print(f"Scanner Region         : {elastic_results[0]['region']}")

    # ------------------------------------
    # Verification
    # ------------------------------------

    print("\n========================================")
    print("DAY 2 VERIFICATION")
    print("========================================")

    # Number of resources

    assert len(ebs_results) == 2
    assert len(elastic_results) == 1

    print("✓ Correct number of resources detected.")

    # Volume 1

    assert volume1["VolumeId"] == ebs_results[0]["volume_id"]
    assert ebs_results[0]["size_gb"] == 100
    assert ebs_results[0]["state"] == "available"
    assert ebs_results[0]["region"] == "us-east-1"

    print("✓ Volume 1 verified.")

    # Volume 2

    assert volume2["VolumeId"] == ebs_results[1]["volume_id"]
    assert ebs_results[1]["size_gb"] == 200
    assert ebs_results[1]["state"] == "available"
    assert ebs_results[1]["region"] == "us-east-1"

    print("✓ Volume 2 verified.")

    # Elastic IP

    assert elastic_ip["AllocationId"] == elastic_results[0]["allocation_id"]
    assert elastic_ip["PublicIp"] == elastic_results[0]["public_ip"]
    assert elastic_results[0]["associated"] is False
    assert elastic_results[0]["region"] == "us-east-1"

    print("✓ Elastic IP verified.")

    print("\n========================================")
    print("RESULT")
    print("========================================")

    print("✓ Scanner output matches AWS resources.")
    print("✓ All fields verified successfully.")
    print("✓ Week 3 Day 2 Completed.")


if __name__ == "__main__":
    test_week3_day2()