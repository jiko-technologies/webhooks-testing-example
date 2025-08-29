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
2025-08-29 10:20:16,345 - app - INFO - NGrok running on https://7bb109f54658.ngrok-free.app
2025-08-29 10:20:18,209 - app - INFO - Created subscription 3bb0fe21-441e-4834-a780-d5e7eaef45c2
2025-08-29 10:20:18,210 - app - INFO - ====================
2025-08-29 10:20:18,210 - app - INFO - Ready! Browse to http://localhost:8888/trigger to trigger some webhooks!
2025-08-29 10:20:18,210 - app - INFO - ====================
2025-08-29 10:20:22,618 - app - INFO - Triggered webhook event 2283fb4b-64fe-42d4-acf6-24c0c0d0ceb6!
2025-08-29 10:20:24,347 - app - INFO - Webhook event 2283fb4b-64fe-42d4-acf6-24c0c0d0ceb6 received!
2025-08-29 10:20:24,347 - app - INFO -   -> Signatures match! We can now do something with the payload!

```
