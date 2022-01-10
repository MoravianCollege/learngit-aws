
from botocore.exceptions import ClientError
import json
from github import Github, GithubException
from helpers import load_token


def create_repo():
    g = Github(load_token())

    org = g.get_organization('moco-learn-git')
    repo = org.create_repo('temp2', 'temp repo')

    return {
        'statusCode': 200,
        'body': json.dumps({'repo_name': repo.name}),
    }


def lambda_handler(event, context):

    try:
        return create_repo()
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'msg': 'Error while loading Github credentials'}),
            'details': json.dumps(e.response)
        }
    except GithubException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'msg': 'Error while contacting Github',
            'data': e.data})
        }


if __name__ == '__main__':
    print(lambda_handler(0, 0))
