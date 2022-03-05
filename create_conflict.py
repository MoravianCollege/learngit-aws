from botocore.exceptions import ClientError
import git
from helpers import load_token
import json
from github import Github, GithubException
import os
import sys
import tempfile
import shutil


def create_conflict(event):
    if 'repo_name' not in event:
        return {
            'statusCode': 400,
            'body': 'Must provide repo_name'
        }
    repo_name = event['repo_name']

    token = load_token()
    g = Github(token)

    t = tempfile.TemporaryDirectory()
    repo_dir = os.path.join(t.name, repo_name)
    origin_url = 'https://github.com/moco-learn-git/{}.git'.format(repo_name)
    r = git.Repo.clone_from(origin_url, repo_dir)

    src = 'README_conflict_version.md'
    dst = os.path.join(repo_dir, "README.md")
    shutil.copy(src, dst)

    origin = r.remote('origin')
    # adding access token to remote for authentication
    with origin.config_writer as cw:
        cw.set("url", "https://{}@github.com/moco-learn-git/{}.git".format(token, repo_name))

    index = r.index
    index.add(['README.md'])
    index.commit('Change to an enumerated list')
    r.remote('origin').push('main')

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
