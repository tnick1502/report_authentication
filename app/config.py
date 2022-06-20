from pydantic import BaseSettings
import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.normpath(os.path.join("/".join(os.getcwd().split("/")[:-1]), ".env")))

class Configs(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8555
    database_url: str = os.getenv('DATABASE_URI')
    jwt_secret: str = os.getenv('JWT_SECRET')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM')
    jwt_expiration: int = os.getenv('JWT_EXPIRATION')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

configs = Configs()
