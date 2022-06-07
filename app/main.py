import uvicorn
from config import configs
from app import app

if __name__ == "__main__":


    uvicorn.run(
        app,
        host=configs.server_host,
        port=configs.server_port,
    )



