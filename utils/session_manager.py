import boto3

def get_session(profile_name = None):
    """
    Create and return a boto3 session. 
    if profile name is provided use it , 
    else fallback to default AWS credentials
    """
    if profile_name :
        return boto3.Session(profile_name = profile_name)
    return boto3.Session()