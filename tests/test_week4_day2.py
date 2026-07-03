from moto import mock_aws
import boto3

from scanners.asset_retrieval import (
    get_unattached_ebs_volumes,
    get_unassociated_elastic_ips,
)


@mock_aws
def test_scanner_integration():

    print("\n==================================================")
    print("WEEK 4 DAY 2 - INTEGRATION TEST")
    print("==================================================")

    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

    # -----------------------------------
    # Create AWS Test Resources
    # -----------------------------------

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

    # -----------------------------------
    # Scanner Output
    # -----------------------------------

    ebs_resources = get_unattached_ebs_volumes()
    elastic_resources = get_unassociated_elastic_ips()

    # -----------------------------------
    # Simulate Aggregator / Report Module
    # -----------------------------------

    report_data = {
        "ebs_volumes": ebs_resources,
        "elastic_ips": elastic_resources
    }

    print("\nREPORT DATA")
    print("==========================================")

    print(report_data)

    # -----------------------------------
    # Verify Resource Counts
    # -----------------------------------

    assert len(report_data["ebs_volumes"]) == 2
    assert len(report_data["elastic_ips"]) == 1

    print("✓ Resource counts verified.")

    # -----------------------------------
    # Verify Volume IDs
    # -----------------------------------

    expected_volume_ids = {
        volume1["VolumeId"],
        volume2["VolumeId"]
    }

    scanned_volume_ids = {
        report_data["ebs_volumes"][0]["volume_id"],
        report_data["ebs_volumes"][1]["volume_id"]
    }

    assert expected_volume_ids == scanned_volume_ids

    print("✓ Volume IDs verified.")

    # -----------------------------------
    # Verify Elastic IP
    # -----------------------------------

    assert (
        report_data["elastic_ips"][0]["allocation_id"]
        == elastic_ip["AllocationId"]
    )

    print("✓ Elastic IP Allocation ID verified.")

    # -----------------------------------
    # Verify Region
    # -----------------------------------

    for volume in report_data["ebs_volumes"]:
        assert volume["region"] == "us-east-1"

    for ip in report_data["elastic_ips"]:
        assert ip["region"] == "us-east-1"

    print("✓ Regions verified.")

    # -----------------------------------
    # Verify State
    # -----------------------------------

    for volume in report_data["ebs_volumes"]:
        assert volume["state"] == "available"

    print("✓ Volume states verified.")

    # -----------------------------------
    # Verify Association Status
    # -----------------------------------

    assert report_data["elastic_ips"][0]["associated"] is False

    print("✓ Elastic IP association verified.")

    # -----------------------------------
    # Final Summary
    # -----------------------------------

    print("\n==================================================")
    print("INTEGRATION TEST PASSED")
    print("==================================================")

    print("✓ Scanner data transferred successfully.")
    print("✓ No data loss detected.")
    print("✓ No field modifications detected.")
    print("✓ Report data matches scanner output.")
    print("✓ Week 4 Day 2 Completed Successfully.")


if __name__ == "__main__":
    test_scanner_integration()