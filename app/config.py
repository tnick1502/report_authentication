from pydantic import BaseSettings
import os
from sys import platform

class Configs(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 9000
    database_url: str = "postgresql+asyncpg://root:root@localhost:32700/reports"

    jwt_secret: str = "OOIOIPSJFBSFBSBGBBSB"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600


configs = Configs()
#    _env_file=".env",
#    _env_file_encoding="utf-8"
#)