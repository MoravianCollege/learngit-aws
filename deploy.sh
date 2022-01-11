#!/bin/bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
docker build -t create_repo:latest -f Dockerfile.create_repo .
docker build -t delete_repo:latest -f Dockerfile.delete_repo .
docker build -t create_conflict:latest -f Dockerfile.create_conflict .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag create_repo:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/create_repo:latest
docker tag delete_repo:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/delete_repo:latest
docker tag create_conflict:latest $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/create_conflict:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/create_repo:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/delete_repo:latest
docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/create_conflict:latest
aws lambda update-function-code --function-name create_repo --image-uri $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/create_repo:latest
aws lambda update-function-code --function-name delete_repo --image-uri $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/delete_repo:latest
aws lambda update-function-code --function-name create_conflict --image-uri $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/create_conflict:latest
