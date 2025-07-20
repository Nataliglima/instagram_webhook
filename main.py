from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

app = FastAPI()

VERIFY_TOKEN = "meu_token_b12_supersecreto_987"  # Substitua pelo seu token real

@app.get("/")
async def verify(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge, status_code=200)
    else:
        return PlainTextResponse(content="Unauthorized", status_code=403)

@app.post("/")
async def receive_webhook(request: Request):
    body = await request.json()
    print("Recebido:", body)
    return {"status": "ok"}

