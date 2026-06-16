import boto3

def get_session(profile_name = None, role_arn = None):
    """
    Create and return a boto3 session. 
    if profile name is provided use it , 
    else fallback to default AWS credentials
    priority : role assumption > named profile > default credentials
    """
    if role_arn:
        return assume_role(role_arn)
    if profile_name :
        return boto3.Session(profile_name = profile_name)
    return boto3.Session()


def assume_role(role_arn,session_name = "AuditorSession"):
        """Assume an AWS IAM role and return a boto3 session
        with temporary credentials""" 
        sts = boto3.client("sts")
        response = sts.assume_role(
            RoleArn = role_arn,
            RoleSessionName = session_name 
        )
        creds = response["Credentials"]
        return boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key = creds["SecretAccessKey"],
            aws_session_token = creds["SessionToken"]
        )