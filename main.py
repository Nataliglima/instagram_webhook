import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI()

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")


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
        return PlainTextResponse(content=challenge)

    return JSONResponse(content={"status": "Erro na verificação"}, status_code=403)





