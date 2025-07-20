from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import os
import uvicorn

app = FastAPI()

# Pegando o token da variável de ambiente (mais seguro)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "meu_token_b12_supersecreto_987")

# ✅ Rota para validação do Webhook (GET)
@app.get("/")
async def verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    return PlainTextResponse(content="Unauthorized", status_code=403)

# ✅ Rota para receber eventos (POST)
@app.post("/")
async def receive_webhook(request: Request):
    body = await request.json()
    print("Recebido:", body)
    return {"status": "ok"}

# ✅ Executa corretamente no Render com porta dinâmica
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


