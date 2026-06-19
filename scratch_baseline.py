from moto import mock_aws
from utils.concurrency_engine import scan_regions_concurrently

REGIONS = ["us-east-1", "us-west-2", "eu-west-1"]

@mock_aws
def run():
    results = scan_regions_concurrently(REGIONS)
    for region, count in results.items():
        print(f"{region}: {count} AZs")

run()