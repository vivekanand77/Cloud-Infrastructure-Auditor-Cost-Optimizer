import time
from threading import Semaphore
from concurrent.futures import ThreadPoolExecutor, as_completed
from botocore.exceptions import ClientError
from utils.session_manager import get_session

RATE_LIMIT = Semaphore(2)  # max 2 AWS calls in flight at once, across ALL regions

def call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            with RATE_LIMIT:
                return func()
        except ClientError as e:
            if e.response["Error"]["Code"] == "Throttling":
                wait = 2 ** attempt
                print(f"Throttled — retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")

def scan_region(region, service="ec2"):
    session = get_session()
    client = session.client(service, region_name=region)

    call_count = {"n": 0}
    def maybe_throttled_call():
        call_count["n"] += 1
        if region == "us-west-2" and call_count["n"] == 1:
            raise ClientError(
                {"Error": {"Code": "Throttling", "Message": "Rate exceeded"}},
                "DescribeAvailabilityZones"
            )
        return client.describe_availability_zones()

    azs = call_with_retry(maybe_throttled_call)
    return region, len(azs["AvailabilityZones"])

def scan_regions_concurrently(regions, service="ec2"):
    results = {}
    with ThreadPoolExecutor(max_workers=len(regions)) as executor:
        futures = {executor.submit(scan_region, r, service): r for r in regions}
        for future in as_completed(futures):
            region = futures[future]
            try:
                region_name, count = future.result()
                results[region_name] = count
            except Exception as e:
                print(f"⚠️ {region} failed: {e}")
    return results