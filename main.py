from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

VERIFY_TOKEN = "meu_token_b12_supersecreto_987"  # personalize aqui

@app.get("/")
async def verify(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Token inválido"}

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    print("📩 Webhook recebido:", data)
    return {"status": "recebido"}

