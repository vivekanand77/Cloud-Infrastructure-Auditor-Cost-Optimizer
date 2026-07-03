from moto import mock_aws
import boto3

from scanners.asset_retrieval import (
    get_unattached_ebs_volumes,
    get_unassociated_elastic_ips,
)


@mock_aws
def test_end_to_end_workflow():

    print("\n==================================================")
    print("WEEK 4 DAY 3 - END TO END TEST")
    print("==================================================")

    # -------------------------------------------------
    # Step 1 : Create Fake AWS Resources
    # -------------------------------------------------

    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

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

    print("\nAWS Resources Created Successfully")

    # -------------------------------------------------
    # Step 2 : Scanner
    # -------------------------------------------------

    ebs_results = get_unattached_ebs_volumes()
    elastic_results = get_unassociated_elastic_ips()

    print("\nScanner Completed Successfully")

    # -------------------------------------------------
    # Step 3 : Aggregator
    # -------------------------------------------------

    aggregated_data = {
        "ebs_volumes": ebs_results,
        "elastic_ips": elastic_results
    }

    print("\nAggregator Completed Successfully")

    # -------------------------------------------------
    # Step 4 : Simulated Report
    # -------------------------------------------------

    report = {
        "total_ebs_volumes": len(aggregated_data["ebs_volumes"]),
        "total_elastic_ips": len(aggregated_data["elastic_ips"]),
        "resources": aggregated_data
    }

    print("\nGenerated Report")
    print("============================================")

    print(report)

    # -------------------------------------------------
    # Step 5 : Verification
    # -------------------------------------------------

    print("\n============================================")
    print("VERIFY WORKFLOW")
    print("============================================")

    # Counts

    assert report["total_ebs_volumes"] == 2
    assert report["total_elastic_ips"] == 1

    print("✓ Resource counts verified.")

    # Volume IDs

    expected_ids = {
        volume1["VolumeId"],
        volume2["VolumeId"]
    }

    scanner_ids = {
        aggregated_data["ebs_volumes"][0]["volume_id"],
        aggregated_data["ebs_volumes"][1]["volume_id"]
    }

    assert expected_ids == scanner_ids

    print("✓ Volume IDs verified.")

    # Elastic Allocation ID

    assert (
        report["resources"]["elastic_ips"][0]["allocation_id"]
        == elastic_ip["AllocationId"]
    )

    print("✓ Elastic IP verified.")

    # Schema Validation

    assert "volume_id" in report["resources"]["ebs_volumes"][0]
    assert "size_gb" in report["resources"]["ebs_volumes"][0]
    assert "state" in report["resources"]["ebs_volumes"][0]

    assert "allocation_id" in report["resources"]["elastic_ips"][0]
    assert "public_ip" in report["resources"]["elastic_ips"][0]

    print("✓ Schema verified.")

    # -------------------------------------------------
    # Final Summary
    # -------------------------------------------------

    print("\n==================================================")
    print("END TO END TEST PASSED")
    print("==================================================")

    print("✓ AWS resources created.")
    print("✓ Scanner executed.")
    print("✓ Aggregator executed.")
    print("✓ Report generated.")
    print("✓ Data integrity maintained.")
    print("✓ No crashes occurred.")
    print("✓ Week 4 Day 3 Completed Successfully.")


if __name__ == "__main__":
    test_end_to_end_workflow()