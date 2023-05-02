import boto3
import os
from botocore.exceptions import ClientError

from config import configs

class S3:
    def __init__(self):
        self.s3 = boto3.resource(
            endpoint_url=configs.endpoint_url,
            aws_access_key_id=configs.aws_access_key_id,
            service_name=configs.service_name,
            aws_secret_access_key=configs.aws_secret_access_key,
            region_name=configs.region_name
        )

        self.bucket = configs.bucket

    def put_object_path(self, path: str, key: str):
        path = os.path.normcase(path)

        with open(path, 'rb') as data:
            self.s3.Bucket(self.bucket).put_object(Key=key, Body=data)
        return self.get_url(key)

    def put_object(self, data: bytes, key: str):
        self.s3.Bucket(self.bucket).put_object(Key=key, Body=data)

    def get_url(self, key: str):
        return f'{configs.endpoint_url}{self.bucket}/{key}'

    def get_file(self, key: str, filename: str):
        self.s3.Bucket(self.bucket).download_file(key, filename)

    def check(self, key):
        try:
            self.s3.Object(self.bucket, key).load()
        except ClientError as e:
            return int(e.response['Error']['Code']) != 404
        return True

s3 = S3()

if __name__ == '__main__':
    print(s3.check('cert_auth/tes2.png'))
    #print(s3.put_object_path('/Users/mac1/Downloads/341-15 - 11 - Трехосное нагружение.png', 'cert_auth/test2.png'))