import boto3
from botocore.exceptions import NoCredentialsError, ClientError


def get_session(profile_name=None, role_arn=None):
    """
    Create and return a boto3 session.
    Priority: role assumption > named profile > default credentials.
    """
    try:
        if role_arn:
            return assume_role(role_arn)
        if profile_name:
            return boto3.Session(profile_name=profile_name)
        return boto3.Session()
    except NoCredentialsError:
        raise SystemExit(
            "❌  No AWS credentials found.\n"
            "    Run `aws configure` or set AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY."
        )


def assume_role(role_arn, session_name="AuditorSession"):
    """Assume an AWS IAM role and return a boto3 session with temporary credentials."""
    try:
        sts = boto3.client("sts")
        response = sts.assume_role(RoleArn=role_arn, RoleSessionName=session_name)
        creds = response["Credentials"]
        return boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )
    except ClientError as e:
        code = e.response["Error"]["Code"]
        raise SystemExit(
            f"❌  Could not assume role '{role_arn}'.\n"
            f"    AWS error: {code} — {e.response['Error']['Message']}"
        )