import os
import boto3
import requests
import zipfile
from functools import partial
from django.conf import settings


class LambdaDeployer:
    def __init__(self, deployment):
        self.deployment = deployment
        self.lmbd = boto3.client('lambda')
        self.api_gateway = boto3.client('apigateway')

    def deploy(self):
        resp = self.lmbd.create_function(
            FunctionName=self.deployment.name,
            Runtime=self.deployment.runtime.name,
            Code={
                'ZipFile': self.prepare_package()
            },
            MemorySize=1536,
            Handler=self.deployment.config['handler'],
            Timeout=300,
            Role='arn:aws:iam::860100747351:role/lambda_basic_execution',
        )
        self.deployment.config['function_arn'] = resp['FunctionArn']
        if 'rest_api_id' not in self.deployment.config:
            self.create_project_api()

        # create resource
        resource_resp = self.api_gateway.create_resource(
            restApiId=self.deployment.config['rest_api_id'],
            pathPart=self.deployment.name
        )

        # create POST method
        self.api_gateway.put_method(
            restApiId=self.deployment.config['rest_api_id'],
            resourceId=resource_resp['id'],
            httpMethod="GET",
            authorizationType="NONE",
            apiKeyRequired=False,
        )

        lambda_version = self.lmbd.meta.service_model.api_version

        uri_data = {
            "aws-region": settings.AWS_DEFAULT_REGION,
            "api-version": lambda_version,
            "aws-acct-id": settings.AWS_ACCOUNT_ID,
            "lambda-function-name": self.deployment.name,
        }

        uri = "arn:aws:apigateway:{aws-region}:lambda:path/{api-version}/functions/arn:aws:lambda:{aws-region}:{aws-acct-id}:function:{lambda-function-name}/invocations".format(**uri_data)

        # create integration
        self.api_gateway.put_integration(
            restApiId=self.deployment.config['rest_api_id'],
            resourceId=resource_resp['id'],
            httpMethod="GET",
            type="AWS",
            integrationHttpMethod="POST",
            uri=uri,
        )
        self.deployment.config['endpoint'] = f"https://{self.deployment.config['rest_api_id']}.execute-api.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{self.deployment.name}"
        self.deployment.save()

    def create_project_api(self):
        resp = self.api_gateway.create_rest_api(
            name=f'{self.deployment.project.name}-{self.deployment.project.pk}',
        )
        self.deployment.config['rest_api_id'] = resp['id']

    def prepare_package(self) -> bytes:
        resp = requests.get(self.deployment.framework.url)
        resp.raise_for_status()
        tmp_path = f'/tmp/{self.deployment.pk}.zip'
        with open(tmp_path, 'wb') as tmp:
            for chunk in resp.iter_content(1024):
                if chunk:
                    tmp.write(chunk)
        with zipfile.ZipFile(tmp_path, 'a') as package:
            join = partial(os.path.join, self.deployment.volume_path)
            for user_file in self.deployment.config['files']:
                package.write(join(user_file), arcname=user_file)
        with open(tmp_path, 'rb') as tp:
            return tp.read()
        return b''
