from typing import Annotated
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class EnvironmentVariables(BaseSettings):
    ngrok_authtoken: str = ""
    partner_api_url: str = "https://partner-api.sandbox-api.jikoservices.com"
    partner_api_username: str = ""
    partner_api_password: str = ""
    partner_api_shared_secret: str = ""
    partner_id: str | None = None
    subscription_shared_secret: str = ""
    port: int = 8888
