import boto3
import json

def load_token():
    """
    Load the Github AUTH Token from AWS Secrets Manager
    Throws a botocore.exceptions.ClientError if anything goes wrong
    """
    secret_name = 'github/csdevmc'
    region_name = 'us-east-1'

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = json.loads(get_secret_value_response['SecretString'])
    token = secret['AUTH_TOKEN']

    return token
