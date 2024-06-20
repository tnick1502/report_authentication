from config import configs
import botocore.exceptions
from modules.exceptions import exception_not_found_file

class S3Service:
    def __init__(self, client):
        self.client = client

    async def upload(self, key: str, data: bytes):
        return await self.client.put_object(
            Bucket=configs.bucket,
            Key=key,
            Body=data
        )

    async def delete(self, key: str):
        return await self.client.delete_object(
            Bucket=configs.bucket,
            Key=key
        )

    async def check_file_exists(self, key):
        try:
            await self.client.head_object(Bucket=configs.bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise exception_not_found_file

    async def get(self, key: str):
        await self.check_file_exists(key)
        return await self.client.get_object(
            Bucket=configs.bucket,
            Key=key
        )
