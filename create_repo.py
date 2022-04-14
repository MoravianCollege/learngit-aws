
from botocore.exceptions import ClientError
import json
from github import Github, GithubException
from helpers import load_token
import wonderwords
import tempfile
import shutil
import git
import os


def create_repo():
    token = load_token()
    g = Github(token)

    org = g.get_organization('moco-learn-git')

    repo_name = create_repo_name()
    while repo_name in org.get_repos():
        repo_name = create_repo_name()
    repo = org.create_repo(repo_name, 'Practice the Github Workflow')

    t = tempfile.TemporaryDirectory()
    repo_dir = os.path.join(t.name, repo_name)
    origin_url = 'https://github.com/moco-learn-git/{}.git'.format(repo_name)
    r = git.Repo.clone_from(origin_url, repo_dir)

    src = 'README_start_version.md'
    dst = os.path.join(repo_dir, "README.md")
    shutil.copy(src, dst)

    origin = r.remote('origin')
    # adding access token to remote for authentication
    with origin.config_writer as cw:
        cw.set("url", "https://{}@github.com/moco-learn-git/{}.git".format(token, repo_name))

    index = r.index
    index.add(['README.md'])
    index.commit('initial commit')
    r.remote('origin').push('main')

    return {
        'statusCode': 200,
        'body': json.dumps({'repo_name': repo.name,
                            'repo_url': 'https://github.com/moco-learn-git/{}.git'.format(repo_name)}),
    }

def create_repo_name():
    r = wonderwords.RandomWord()
    noun = r.word(include_parts_of_speech=['noun'])
    adjective = r.word(include_parts_of_speech=['adjective'])
    repo_name = adjective + '-' + noun
    return repo_name

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
