from botocore.exceptions import ClientError
import json
from github import Github, GithubException
import sys
from helpers import load_token


def delete_repo(event):
    if 'repo_name' not in event:
        return {
            'statusCode': 400,
            'body': 'Must provide repo_name'
        }
    repo_name = event['repo_name']

    token = load_token()
    g = Github(token)

    org = g.get_organization('moco-learn-git')
    repo = org.get_repo(repo_name)
    repo.delete()

    return {'statusCode': 200}


def lambda_handler(event, context):
    try:
        return delete_repo(event)
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

