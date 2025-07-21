import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx  # para chamadas HTTP assíncronas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, prefira domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "default_token_seguro")

@app.on_event("startup")
async def startup_event():
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"✅ Servidor iniciado na porta {port}")

    if VERIFY_TOKEN and VERIFY_TOKEN != "default_token_seguro":
        logger.info(f"✅ VERIFY_TOKEN configurado: SIM")
        logger.info(f"🔐 Token verificação (mascarado): {VERIFY_TOKEN[:4]}...{VERIFY_TOKEN[-4:]}")
    else:
        logger.error("⚠️ AVISO CRÍTICO: VERIFY_TOKEN não configurado corretamente!")
        logger.info("ℹ️ Configure a variável de ambiente VERIFY_TOKEN no Render")

@app.get("/")
async def health_check():
    return {
        "status": "active",
        "message": "Instagram Webhook Service",
        "endpoints": {
            "GET /webhook": "Validação do webhook",
            "POST /webhook": "Recebe eventos do Instagram",
            "GET /callback": "Recebe o código de autorização do Instagram"
        }
    }

@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if not VERIFY_TOKEN:
        raise HTTPException(status_code=500, detail="VERIFY_TOKEN não configurado no servidor")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info(f"✅ Validação bem-sucedida! Challenge: {challenge}")
        return PlainTextResponse(content=challenge)

    token_esperado_mascarado = f"{VERIFY_TOKEN[:4]}...{VERIFY_TOKEN[-4:]}" if VERIFY_TOKEN else "N/A"
    error_detail = f"Falha na verificação: mode={mode}, token_recebido={token}, token_esperado={token_esperado_mascarado}"
    logger.error(f"❌ {error_detail}")

    return JSONResponse(content={"error": error_detail}, status_code=403)

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
        if os.environ.get("ENV") != "production":
            logger.info(f"✅ Payload recebido: {payload}")
        else:
            logger.info("✅ Payload recebido (conteúdo ocultado em produção)")

        return {"status": "success", "received": True}

    except Exception as e:
        logger.error(f"❌ Erro ao processar payload: {str(e)}")
        try:
            body = await request.body()
            body_text = body.decode('utf-8')
            logger.error(f"⚠️ Conteúdo bruto recebido (primeiros 500 caracteres): {body_text[:500]}")
        except Exception as body_error:
            logger.error(f"⚠️ Não foi possível decodificar o corpo da requisição: {str(body_error)}")

        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/callback")
async def instagram_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse(status_code=400, content={"error": "Código de autorização não encontrado na URL"})

    logger.info(f"📥 Código de autorização recebido: {code}")

    client_id = os.environ.get("INSTAGRAM_CLIENT_ID")
    client_secret = os.environ.get("INSTAGRAM_CLIENT_SECRET")
    redirect_uri = os.environ.get("INSTAGRAM_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        logger.error("⚠️ Variáveis de ambiente do Instagram não configuradas corretamente")
        return JSONResponse(status_code=500, content={"error": "Configuração incompleta do Instagram"})

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.instagram.com/oauth/access_token", data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            })
        response.raise_for_status()
        data = response.json()
        logger.info(f"✅ Resposta do token: {data}")

        return JSONResponse(content={"message": "Login autorizado com sucesso!", "token_data": data})

    except httpx.HTTPStatusError as http_err:
        logger.error(f"❌ Erro HTTP ao trocar code por token: {http_err.response.text}")
        return JSONResponse(status_code=http_err.response.status_code, content={"error": http_err.response.text})
    except Exception as e:
        logger.error(f"❌ Erro ao trocar o code por token: {e}")
        return JSONResponse(status_code=500, content={"error": "Erro ao processar o código"})

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"\n🌐 Requisição recebida: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"📤 Resposta enviada: {response.status_code}")
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.principal:app", host="0.0.0.0", port=port, reload=True)




