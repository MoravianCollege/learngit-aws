
# learngit-aws

This repo contains code to create a collection of REST endpoints to manipulate Github repos in the `moco-learn-git` Github organization using the `csdevmv` Github user.

Each endpoint will be a separate Docker container that will be stored in [AWS ECR](https://console.aws.amazon.com/ecr/) and launched as needed by [AWS Lambda](https://console.aws.amazon.com/lambda/).  [AWS API Gateway](https://console.aws.amazon.com/apigateway/) provide the REST interface to trigger the Lambda functions.

## AWS Secrets Manager Setup

In [Secrets Manager](https://console.aws.amazon.com/secretsmanager), reate a new "Other type of secret" named `github/csdevmc` that contains

```
AUTH_TOKEN=<TOKEN>
```

## AWS IAM Setup

In [IAM](https://console.aws.amazon.com/iamv2/home) create a *Policy* named `AccessGithubCSdevMCSecret` that contains

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "<ARN for github/csdevmc secret>"
    }
  ]
}
```

Be sure you get the complete ARN - it should end something like `secret:github/csdevmc-r4ylAS` (note the 6 extra characters after the secret name).

## Local Credential Setup

Create a `.env` file containing AWS credentials that have the `AccessGithubCSdevMSecret` policy (I used my admin account that has access by default).  These credentials will be used inside the Docker containers when we launch them locally.

```
AWS_ACCESS_KEY_ID=<ID>
AWS_SECRET_ACCESS_KEY=<ACCESS_KEY>
```
  
## Test Locally Outside Docker

* Create a virtual environment

 ```
 python3 -m venv .venv
 ```

* Activate VENV and Install required libraries

 ```
 source .venv/bin/activate
 pip install -r requirements.txt
 ```

* Test `create_repo` (assumes virtual environment is active)

 ```
 python create_repo.py
 ```

* Test `delete_repo` (assumes virtaul environment is active)

 ```
 python delete_repo.py temp
 ```

## Test Locally in Docker Containers

Based on [Testing Images](https://docs.aws.amazon.com/lambda/latest/dg/images-test.html) AWS documentation
but with environment variables loaded from `.env` as described in the [Docker run](https://docs.docker.com/engine/reference/commandline/run/)
documentation.

* Build the Docker containers

  ```
  docker build -t create_repo:latest -f Dockerfile.create_repo .
  docker build -t delete_repo:latest -f Dockerfile.delete_repo .

  ```

* Run the docker containers using the credentials in `.env`

  ```
  docker run --env-file .env -d -p 9000:8080 --name create_repo create_repo:latest
  docker run --env-file .env -d -p 9001:8080 --name delete_repo delete_repo:latest
  ```

* Call the Lambda function inside the containers

  **`create_container`** is on port 9000 and requires no data (`{}`):
  ```
  curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
  ```

  Look for a 200 status code and check that the repo was created in the `moco-learn-git` Github organization.

  **`delete_container`** is on port 9001 and requires a `repo_name` as data:
  ```
  curl -XPOST "http://localhost:9001/2015-03-31/functions/function/invocations" -d '{"repo_name": "temp"}'
  ```
  
  Look for a 200 status code and check that the repo was delete in the `moco-learn-git` Github organization.

* Step and remove the containers

  ```
  docker rm -f create_repo
  docker rm -f delete_repo
  ```

## Build Containers and Deploy to AWS

These steps are based on the [AWS Lambda docs](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-images.html) and assume you have credentials for all services used.

* **ONE TIME ACTION** - Authenticate the Docker CLI to your Amazon ECR registry 

  ```
  aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS Account ID>.dkr.ecr.us-east-1.amazonaws.com
  ```
* **ONE TIME ACTION** - Create repos in ECR

  ```
  aws ecr create-repository --region us-east-1 --repository-name create_repo --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
  aws ecr create-repository --region us-east-1 --repository-name delete_repo --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
  ```

* Build Docker Containers

  ```
  docker build -t create_repo:latest -f Dockerfile.create_repo .
  docker build -t delete_repo:latest -f Dockerfile.delete_repo .
  ```

* Tag the local images to match the ECR repository name

  ```
  docker tag create_repo:latest <AWS Account ID>.dkr.ecr.us-east-1.amazonaws.com/create_repo:latest
  docker tag delete_repo:latest <AWS Account ID>.dkr.ecr.us-east-1.amazonaws.com/delete_repo:latest
  ```
* Push images to ECR

  ```
  docker push <AWS Account ID>.dkr.ecr.us-east-1.amazonaws.com/create_repo:latest
  docker push <AWS Account ID>.dkr.ecr.us-east-1.amazonaws.com/delete_repo:latest
  ```

## Lambda Functions Setup

FIXME: These steps require us to use the Console.  Figure out how to create an appropriate role with CloudWatch Logging and the SecretManager access using the CLI.

In the [Lambda Console](https://console.aws.amazon.com/lambda/home):

* Create a function based on a container image
  * Name: `create_repo`
  * Container Image URI: Browse Images and find `create_repo` and select `latest`
  * Other options can be defaults, select "Create function"
* Add the `AccessGithubCSdevMCSecret` policy to the persmissions
  * Select "Configuration" and "Permissions"
  * Under "Execution role" click on the name of the role (something like `create_repo-role-gka0tmkc`).  This will open an IAM window.
  * Click "Attach Policies" and then select `AccessGithubCSdevMCSecret`. Click "Attach Policy"
  * Close the IAM window


Repeat these steps to create a Lambda function named `delete_repo`.

## Test Lambda Functions

* In the Lambda function, click "Test"
* For `create_repo` we do not need data, so the HelloWorld template will work.
* For `delete_repo` we need

  ```
  {
    "repo_name": "temp"
  }
  ```

## API Gateway Setup

In the [API Gateway Console](https://console.aws.amazon.com/apigateway/):

* Click "Create API"
* Select "Build" under "REST API"
* API Name: learn-git-katacoda and then click "Create"
* Under Actions, click "Create Resource" and set the resource name to "create_repo". Click "Create Resource"
* Make sure `create_repo` is selected and under Actions click "Create Method".  In the drop down, select "GET" and click the check mark.  Specify the lambda function as `create_repo`.  When asked, Ok the "add permission to the lambda function."
* Make sure `/` is selected and then under Actions repeat the "Create Resource" (`delete_repo`) and "Create Method" ("POST").  Set this lambda function to `delete_repo`
* Under actions select "Deploy API."  Specify a "new deployment stage" named "prod"

## Test API

In the following, use the URL for the gateway, which is at the top of the page after you deploy.

* Test the `create_repo` endpoint

  ```
  curl <URL>/prod/create_repo
  ```

* Test the `delete_repo` endpoing

  ```
  curl -XPOST <URL>/prod/delete_repo -d '{"repo_name": "temp"}'
  ```

## Redeploy Changes

When code changes for either endpoint (examples show `create_repo`):

* Rebuild the Docker container

  ```
  docker build -t create_repo:latest -f Dockerfile.create_repo .
  ```

* Tag the container with the ECR name

  ```
  docker tag create_repo:latest <AWS ACCOUNT ID>.dkr.ecr.us-east-1.amazonaws.com/create_repo:latest
  ```

* Push to ECR

  ```
  docker push <AWS ACCOUNT ID>.dkr.ecr.us-east-1.amazonaws.com/create_repo:latest
  ```

* Tell Lambda to use the new image

  ```
  aws lambda update-function-code --function-name create_repo --image-uri <AWS ACCOUNT ID>.dkr.ecr.us-east-1.amazonaws.com/create_repo:latest
  ```

These steps are all in `deploy.sh`.
