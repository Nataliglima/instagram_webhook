from fastapi import FastAPI, Request

app = FastAPI()

# Token secreto que você define e usa no Facebook Developers
VERIFY_TOKEN = "meu_token_b12_supersecreto_987"

# Endpoint GET para validação do webhook pelo Instagram
@app.get("/")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Token inválido"}

# Endpoint POST para receber eventos (menções, comentários, etc)
@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    print("📩 Webhook recebido:", data)
    return {"status": "recebido"}
