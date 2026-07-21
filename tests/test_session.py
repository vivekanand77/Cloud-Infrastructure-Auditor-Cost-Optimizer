from moto import mock_aws
import boto3
from utils.session_manager import get_session

@mock_aws
def test_session():
    #create fake aws credentials
    boto3.setup_default_session(
        aws_access_key_id = "vivek",
        aws_secret_access_key = "vivekk",
        region_name = "us-west-1"
    )
    session = get_session()
    sts = session.client("sts",region_name = "us-west-1")
    identity = sts.get_caller_identity()
    print(f"Account : {identity['Account']}")
    print(f"Arn : {identity['Arn']}")
    print(f"UserId:{identity['UserId']}")
test_session()