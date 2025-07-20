import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

app = FastAPI()

# Configuração do token via variável de ambiente
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "default_token_seguro")


@app.get("/")
async def health_check():
    return {"status": "active", "message": "Instagram Webhook Service"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    # Log para depuração (aparecerá no Render)
    print(f"Recebida verificação: {request.query_params}")

    # Extrai parâmetros da URL
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Verifica se o token está configurado
    if not VERIFY_TOKEN:
        raise HTTPException(
            status_code=500,
            detail="VERIFY_TOKEN não configurado no servidor"
        )

    # Valida o token
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    # Log de erro detalhado
    error_detail = f"Falha na verificação: mode={mode}, token={token}"
    print(error_detail)

    return JSONResponse(
        content={"error": error_detail},
        status_code=403
    )


@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
        print(f"Evento recebido: {payload}")
        return {"status": "success"}
    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        return JSONResponse(
            content={"error": "Invalid payload"},
            status_code=400
        )





