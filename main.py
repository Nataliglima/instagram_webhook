from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
import os
import uvicorn

app = FastAPI()

VERIFY_TOKEN = "meu_token_b12_supersecreto_987"  # Use o mesmo token configurado no Instagram

@app.get("/")
async def verify(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    return PlainTextResponse(content="Unauthorized", status_code=403)

@app.post("/")
async def receive_webhook(request: Request):
    body = await request.json()
    print("Recebido:", body)
    return {"status": "ok"}

# 👇 ESTE BLOCO FINAL É A DICA EXTRA
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

