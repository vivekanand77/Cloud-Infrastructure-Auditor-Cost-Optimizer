from moto import mock_aws
import boto3

from scanners.asset_retrieval import (
    get_unattached_ebs_volumes,
    get_unassociated_elastic_ips,
)


@mock_aws
def test_complete_scanner():

    print("\n==================================================")
    print("WEEK 4 DAY 1 - COMPLETE SCANNER VERIFICATION")
    print("==================================================")

    # ---------------------------------------
    # Create Fake AWS Environment
    # ---------------------------------------

    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

    # ---------------------------------------
    # Create Test Resources
    # ---------------------------------------

    volume1 = ec2.create_volume(
        Size=100,
        AvailabilityZone="us-east-1a",
        VolumeType="gp2"
    )

    volume2 = ec2.create_volume(
        Size=50,
        AvailabilityZone="us-east-1a",
        VolumeType="gp2"
    )

    elastic_ip = ec2.allocate_address(
        Domain="vpc"
    )

    # ---------------------------------------
    # Display Expected Resources
    # ---------------------------------------

    print("\nEXPECTED RESOURCES")
    print("--------------------------------------------")

    print("Volume 1")
    print(volume1)

    print("\nVolume 2")
    print(volume2)

    print("\nElastic IP")
    print(elastic_ip)

    # ---------------------------------------
    # Run Scanner
    # ---------------------------------------

    ebs = get_unattached_ebs_volumes()
    elastic = get_unassociated_elastic_ips()

    # ---------------------------------------
    # Display Scanner Output
    # ---------------------------------------

    print("\n============================================")
    print("SCANNER OUTPUT")
    print("============================================")

    print("\nEBS Volumes")

    for volume in ebs:
        print(volume)

    print("\nElastic IPs")

    for ip in elastic:
        print(ip)

    # ---------------------------------------
    # Verify Resource Count
    # ---------------------------------------

    print("\n============================================")
    print("VERIFY RESOURCE COUNT")
    print("============================================")

    assert len(ebs) == 2
    assert len(elastic) == 1

    print("✓ Resource count verified.")

    # ---------------------------------------
    # Verify EBS Schema
    # ---------------------------------------

    print("\n============================================")
    print("VERIFY EBS SCHEMA")
    print("============================================")

    assert "volume_id" in ebs[0]
    assert "size_gb" in ebs[0]
    assert "volume_type" in ebs[0]
    assert "region" in ebs[0]
    assert "state" in ebs[0]
    assert "attached_instance_id" in ebs[0]

    print("✓ EBS schema verified.")

    # ---------------------------------------
    # Verify Elastic IP Schema
    # ---------------------------------------

    print("\n============================================")
    print("VERIFY ELASTIC IP SCHEMA")
    print("============================================")

    assert "allocation_id" in elastic[0]
    assert "public_ip" in elastic[0]
    assert "region" in elastic[0]
    assert "associated" in elastic[0]
    assert "instance_id" in elastic[0]

    print("✓ Elastic IP schema verified.")

    # ---------------------------------------
    # Verify Data Types
    # ---------------------------------------

    print("\n============================================")
    print("VERIFY DATA TYPES")
    print("============================================")

    # EBS Types

    assert isinstance(ebs[0]["volume_id"], str)
    assert isinstance(ebs[0]["size_gb"], int)
    assert isinstance(ebs[0]["volume_type"], str)
    assert isinstance(ebs[0]["region"], str)
    assert isinstance(ebs[0]["state"], str)

    # attached_instance_id may be None
    assert isinstance(
        ebs[0]["attached_instance_id"],
        (str, type(None))
    )

    # Elastic Types

    assert isinstance(elastic[0]["allocation_id"], str)
    assert isinstance(elastic[0]["public_ip"], str)
    assert isinstance(elastic[0]["region"], str)
    assert isinstance(elastic[0]["associated"], bool)

    assert isinstance(
        elastic[0]["instance_id"],
        (str, type(None))
    )

    print("✓ Data types verified.")

    # ---------------------------------------
    # Verify Actual Values
    # ---------------------------------------

    print("\n============================================")
    print("VERIFY VALUES")
    print("============================================")

    assert ebs[0]["region"] == "us-east-1"
    assert ebs[1]["region"] == "us-east-1"

    assert ebs[0]["state"] == "available"
    assert ebs[1]["state"] == "available"

    assert elastic[0]["region"] == "us-east-1"
    assert elastic[0]["associated"] is False

    print("✓ Resource values verified.")

    # ---------------------------------------
    # Compare IDs
    # ---------------------------------------

    print("\n============================================")
    print("VERIFY IDS")
    print("============================================")

    ebs_ids = {
        ebs[0]["volume_id"],
        ebs[1]["volume_id"]
    }

    expected_ids = {
        volume1["VolumeId"],
        volume2["VolumeId"]
    }

    assert ebs_ids == expected_ids

    assert elastic[0]["allocation_id"] == elastic_ip["AllocationId"]

    print("✓ IDs verified.")

    # ---------------------------------------
    # Final Result
    # ---------------------------------------

    print("\n==================================================")
    print("ALL TESTS PASSED")
    print("==================================================")

    print("✓ Resource detection successful.")
    print("✓ Schema verification successful.")
    print("✓ Data type verification successful.")
    print("✓ Resource values verified.")
    print("✓ Scanner integration verified.")
    print("✓ Week 4 Day 1 Completed Successfully.")


if __name__ == "__main__":
    test_complete_scanner()
    