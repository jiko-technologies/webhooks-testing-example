import uvicorn
from config import EnvironmentVariables

if __name__ == "__main__":
    env = EnvironmentVariables()

    uvicorn.run("app:app", port=env.port, log_config="./log_config.yaml")
