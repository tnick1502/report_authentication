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
    database_url: str = f'postgresql+asyncpg://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_NAME")}'
    jwt_secret: str = os.getenv('JWT_SECRET')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM')
    jwt_expiration: int = os.getenv('JWT_EXPIRATION')
    superuser_name: str = os.getenv('SUPERUSER_NAME')
    superuser_password: str = os.getenv('SUPERUSER_PASSWORD')

class Configs_docker_compose(BaseSettings):
    host_ip: str = get_self_public_ip()
    database_url: str = Field(..., env='DATABASE_URL')
    jwt_secret: str = Field(..., env='JWT_SECRET')
    jwt_algorithm: str = Field(..., env='JWT_ALGORITHM')
    jwt_expiration: int = Field(..., env='JWT_EXPIRATION')
    superuser_name: str = Field(..., env='SUPERUSER_NAME')
    superuser_password: str = Field(..., env='SUPERUSER_PASSWORD')


try:
    configs = Configs_docker_compose()
except ValidationError:
    configs = Configs_env()