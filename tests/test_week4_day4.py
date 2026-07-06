from moto import mock_aws
import boto3

from scanners.asset_retrieval import (
    get_unattached_ebs_volumes,
    get_unassociated_elastic_ips,
)


def display_resources(title, resources):
    """
    Helper function to print resources neatly.
    """

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    if not resources:
        print("No resources found.")
        return

    for index, resource in enumerate(resources, start=1):
        print(f"\nResource {index}")

        for key, value in resource.items():
            print(f"{key:<22}: {value}")


@mock_aws
def test_regression_after_cleanup():

    print("\n")
    print("=" * 70)
    print("WEEK 4 DAY 4 - REGRESSION TEST")
    print("=" * 70)

    ec2 = boto3.client(
        "ec2",
        region_name="us-east-1"
    )

    # -----------------------------------------
    # Create Resources
    # -----------------------------------------

    volume1 = ec2.create_volume(
        Size=100,
        AvailabilityZone="us-east-1a",
        VolumeType="gp2"
    )

    volume2 = ec2.create_volume(
        Size=200,
        AvailabilityZone="us-east-1a",
        VolumeType="gp2"
    )

    elastic1 = ec2.allocate_address(
        Domain="vpc"
    )

    # -----------------------------------------
    # Run Scanner
    # -----------------------------------------

    ebs = get_unattached_ebs_volumes()
    elastic = get_unassociated_elastic_ips()

    # -----------------------------------------
    # Display Results
    # -----------------------------------------

    display_resources(
        "UNATTACHED EBS VOLUMES",
        ebs
    )

    display_resources(
        "UNASSOCIATED ELASTIC IPS",
        elastic
    )

    # -----------------------------------------
    # Regression Verification
    # -----------------------------------------

    print("\n")
    print("=" * 70)
    print("RUNNING REGRESSION CHECKS")
    print("=" * 70)

    assert len(ebs) == 2
    assert len(elastic) == 1

    print("✓ Resource count unchanged.")

    ids = [volume["volume_id"] for volume in ebs]

    assert volume1["VolumeId"] in ids
    assert volume2["VolumeId"] in ids

    print("✓ Volume IDs unchanged.")

    allocation_ids = [
        ip["allocation_id"]
        for ip in elastic
    ]

    assert elastic1["AllocationId"] in allocation_ids

    print("✓ Elastic IP Allocation ID unchanged.")

    for volume in ebs:

        assert isinstance(volume["volume_id"], str)
        assert isinstance(volume["size_gb"], int)
        assert isinstance(volume["volume_type"], str)
        assert isinstance(volume["region"], str)
        assert isinstance(volume["state"], str)

    print("✓ Data types unchanged.")

    for volume in ebs:

        assert volume["state"] == "available"
        assert volume["region"] == "us-east-1"

    print("✓ Resource values unchanged.")

    assert elastic[0]["associated"] is False

    print("✓ Association status unchanged.")

    print("\n")
    print("=" * 70)
    print("REGRESSION TEST PASSED")
    print("=" * 70)

    print("✓ Scanner functionality preserved.")
    print("✓ Refactored code behaves correctly.")
    print("✓ No regressions detected.")
    print("✓ Week 4 Day 4 Completed Successfully.")


if __name__ == "__main__":
    test_regression_after_cleanup()