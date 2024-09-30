from config import configs
from typing import Union
from botocore.exceptions import ClientError

class S3Service:
    def __init__(self, client):
        self.client = client

    async def upload(self, key: str, data: bytes) -> dict:
        """
        Загружает объект в указанный бакет S3.

        :param key: Ключ объекта в S3.
        :param data: Данные объекта в формате bytes.
        :return: Ответ от AWS S3.
        :raises ClientError: Ошибка клиента AWS.
        """
        try:
            response = await self.client.put_object(
                Bucket=configs.bucket,
                Key=key,
                Body=data
            )
            return response
        except ClientError as e:
            raise

    async def delete(self, key: str) -> dict:
        """
        Удаляет объект из указанного бакета S3.

        :param key: Ключ объекта в S3.
        :return: Ответ от AWS S3.
        :raises ClientError: Ошибка клиента AWS.
        """
        try:
            response = await self.client.delete_object(
                Bucket=configs.bucket,
                Key=key
            )
            return response
        except ClientError as e:
            raise

    #async def check_file_exists(self, key):
    #    try:
    #        await self.client.head_object(Bucket=configs.bucket, Key=key)
    #    except botocore.exceptions.ClientError as e:
    #        if e.response['Error']['Code'] == '404':
    #            raise exception_not_found_file

    async def get(self, key: str) -> Union[dict, bytes]:
        """
        Получает объект из указанного бакета S3.

        :param key: Ключ объекта в S3.
        :return: Ответ от AWS S3, содержащий объект.
        :raises ClientError: Ошибка клиента AWS.
        """
        return await self.client.get_object(
            Bucket=configs.bucket,
            Key=key
        )
