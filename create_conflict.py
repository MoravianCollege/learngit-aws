from botocore.exceptions import ClientError
import git
from helpers import load_token
import json
from github import Github, GithubException
import os
import sys


def create_conflict(event):

    return {'statusCode': 200}


def lambda_handler(event, context):
    try:
        return create_conflict(event)
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'msg': 'Error while loading Github credentials'})
        }
    except GithubException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'msg': 'Error while contacting Github',
                                'data': e.data})
        }


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Give repo name')
        sys.exit(1)
    event = {'repo_name': sys.argv[1]}
    print(lambda_handler(event, 0))
