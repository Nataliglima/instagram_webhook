import os
from fastapi import FastAPI, Request

app = FastAPI()

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")  # <- assim que lê do Render

@app.get("/")
async def root():
    return {"message": "Servidor está rodando 🚀"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"status": "Erro na verificação"}, 403


