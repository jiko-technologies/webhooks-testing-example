# Jiko sandbox webhooks example

This example demonstrates the webhooks testing utility we have in
the Jiko partner sandbox. In this example, we set up a small FastAPI
server and [ngrok](https://ngrok.com) tunnel. We also create a webhook subscription
on startup. Once running, we are able to trigger a test webhook via http://localhost:8888/trigger.

The server will output some logs which will show the resulting webhook call come in.

### Requirements

- An ngrok authtoken
- Sandbox partner API credentials
- Python >=3.12 and uv installed

### Setup

1. Clone this repo
2. `uv venv && source .venv/bin/activate && uv sync`
3. Copy the env.example file into a .env file, and populate it with your configuration.
4. `source .your-env-file`
5. `python main.py`
6. Navigate to http://localhost:8888/trigger

### Example output

```sh

❯ python main.py
2025-08-29 10:08:02,785 - app - INFO - NGrok running on https://2f0e022ffcf8.ngrok-free.app
2025-08-29 10:08:04,655 - app - INFO - Created subscription a609db91-87ed-4c54-aad7-e098ae34e16c
2025-08-29 10:08:04,655 - app - INFO - ====================
2025-08-29 10:08:04,655 - app - INFO - Ready! Browse to http://localhost:8888/trigger to trigger some webhooks!
2025-08-29 10:08:04,655 - app - INFO - ====================
2025-08-29 10:08:10,625 - app - INFO - Triggered webhook event 4bf2facc-b055-4530-bb63-3a5ba753a637!
2025-08-29 10:08:14,066 - app - INFO - Webhook event 4bf2facc-b055-4530-bb63-3a5ba753a637 received! Received signature = heUhNunw6TvEKt+4nt/ARcwPFv7X5TCdzq1SCq9BOqQ=, expected signature = heUhNunw6TvEKt+4nt/ARcwPFv7X5TCdzq1SCq9BOqQ=
2025-08-29 10:08:14,066 - app - INFO -   -> Signatures match! We can now do something with the payload!

```
