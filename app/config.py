from pydantic import BaseSettings, Field, ValidationError
import os
from dotenv import load_dotenv
import http.client

load_dotenv(dotenv_path=os.path.normpath(".env"))

def get_self_public_ip():
    conn = http.client.HTTPConnection("ifconfig.me")
    conn.request("GET", "/ip")
    return conn.getresponse().read().decode()

class Configs_env(BaseSettings):
    host_ip: str = get_self_public_ip()
    database_url: str = f'postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{str(os.getenv("POSTGRES_PASSWORD"))}@{str(os.getenv("POSTGRES_HOST"))}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_NAME")}'
    jwt_secret: str = os.getenv('JWT_SECRET')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM')
    jwt_expiration: int = os.getenv('JWT_EXPIRATION')
    superuser_name: str = os.getenv('SUPERUSER_NAME')
    superuser_password: str = os.getenv('SUPERUSER_PASSWORD')
    endpoint_url: str = os.getenv('AWS_URI')
    aws_access_key_id: str = os.getenv('AWS_ACCCESS_KEY')
    service_name: str = os.getenv('AWS_SERVICE_NAME')
    aws_secret_access_key: str = os.getenv('AWS_SECRET_KEY')
    region_name: str = os.getenv('AWS_REGION')
    bucket: str = os.getenv('AWS_BUCKET')

class Configs_docker_compose(BaseSettings):
    host_ip: str = get_self_public_ip()
    database_url: str = Field(..., env='DATABASE_URL')
    jwt_secret: str = Field(..., env='JWT_SECRET')
    jwt_algorithm: str = Field(..., env='JWT_ALGORITHM')
    jwt_expiration: int = Field(..., env='JWT_EXPIRATION')
    superuser_name: str = Field(..., env='SUPERUSER_NAME')
    superuser_password: str = Field(..., env='SUPERUSER_PASSWORD')
    endpoint_url: str = Field(..., env='AWS_URI')
    aws_access_key_id: str = Field(..., env='AWS_ACCCESS_KEY')
    service_name: str = Field(..., env='AWS_SERVICE_NAME')
    aws_secret_access_key: str = Field(..., env='AWS_SECRET_KEY')
    region_name: str = Field(..., env='AWS_REGION')
    bucket: str = Field(..., env='AWS_BUCKET')


try:
    configs = Configs_docker_compose()
except ValidationError:
    configs = Configs_env()