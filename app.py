from contextlib import asynccontextmanager
import logging
from typing import Annotated, Any
from uuid import uuid4
from fastapi import Body, FastAPI, Header, Request
from fastapi.responses import HTMLResponse

from partner_api import PartnerAPIClient, sign
import ngrok
from config import EnvironmentVariables


env = EnvironmentVariables()

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifecycle(app: FastAPI):
    listener = await ngrok.default()

    async with PartnerAPIClient.from_env(env) as client:
        app.state.client = client

        listener.forward(f"localhost:{env.port}")
        LOGGER.info(f"NGrok running on {listener.url()}")

        subscription_id = await client.create_subscription(
            events=["application.approved"],
            url=f"{listener.url()}/webhook",
            shared_secret=env.subscription_shared_secret,
        )
        LOGGER.info(f"Created subscription {subscription_id}")

        LOGGER.info("=" * 20)
        LOGGER.info(
            f"Ready! Browse to http://localhost:{env.port}/trigger to trigger some webhooks!"
        )
        LOGGER.info("=" * 20)

        try:
            yield
        finally:
            LOGGER.info("Cleaning up subscription...")
            await client.delete_subscription(subscription_id)


app = FastAPI(lifespan=lifecycle)


@app.post("/webhook", status_code=202)
async def handle_webhook(
    x_jiko_signature: Annotated[str, Header()],
    request: Request,
    payload: Annotated[dict[str, Any], Body()],
) -> None:
    LOGGER.info(f"Webhook event {payload['event_id']} received!")

    calculated_signature = sign(
        await request.body(), env.subscription_shared_secret.encode()
    )

    if calculated_signature == x_jiko_signature:
        LOGGER.info("\t -> Signatures match! We can now do something with the payload!")


@app.get("/trigger", status_code=200)
async def trigger_webhook(request: Request) -> HTMLResponse:
    client: PartnerAPIClient = request.app.state.client

    event_id = await client.trigger_webhook(
        event_type="application.approved", payload={"application_id": str(uuid4())}
    )

    LOGGER.info(f"Triggered webhook event {event_id}!")

    return HTMLResponse(
        content=f"""
    <html><head><style> h1 {{ font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100%; }}</style></head>
    <body>
        <h1>Webhook event {event_id} triggered, please check the terminal again to see the resulting webhook call!</h1>
    </body>
    </html>
    """
    )
