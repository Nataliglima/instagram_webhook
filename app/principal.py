import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente do .env
load_dotenv()

app = FastAPI()

# 🔓 Suporte ao CORS — necessário se houver frontend consumindo a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua "*" por domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do token via variável de ambiente
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "default_token_seguro")

# Verificação na inicialização
@app.on_event("startup")
async def startup_event():
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"✅ Servidor iniciado na porta {port}")
    logger.info(f"✅ VERIFY_TOKEN configurado: {bool(VERIFY_TOKEN)}")

    if not VERIFY_TOKEN or VERIFY_TOKEN == "default_token_seguro":
        logger.error("⚠️ AVISO CRÍTICO: VERIFY_TOKEN não configurado corretamente!")
        logger.info("ℹ️ Configure a variável de ambiente VERIFY_TOKEN no Render")

@app.get("/")
async def health_check():
    return {
        "status": "active",
        "message": "Instagram Webhook Service",
        "endpoints": {
            "GET /webhook": "Validação do webhook",
            "POST /webhook": "Recebe eventos do Instagram"
        }
    }

@app.get("/webhook")
async def verify_webhook(request: Request):
    logger.info(f"\n🔍 Solicitação GET /webhook recebida")
    logger.info(f"🔍 Query params: {dict(request.query_params)}")

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if not VERIFY_TOKEN:
        error_msg = "VERIFY_TOKEN não configurado no servidor"
        logger.error(f"❌ {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info(f"✅ Validação bem-sucedida! Challenge: {challenge}")
        return PlainTextResponse(content=challenge)

    # Mascarar o token esperado para logs
    token_esperado_mascarado = f"{VERIFY_TOKEN[:2]}...{VERIFY_TOKEN[-2:]}" if VERIFY_TOKEN else "N/A"
    error_detail = f"Falha na verificação: mode={mode}, token_recebido={token}, token_esperado={token_esperado_mascarado}"
    logger.error(f"❌ {error_detail}")

    return JSONResponse(
        content={"error": error_detail},
        status_code=403
    )

@app.post("/webhook")
async def handle_webhook(request: Request):
    logger.info("\n📨 Evento POST /webhook recebido")

    try:
        payload = await request.json()
        # Em produção, não logamos o payload completo por segurança
        if os.environ.get("ENV") != "production":
            logger.info(f"✅ Payload recebido: {payload}")
        else:
            logger.info("✅ Payload recebido (conteúdo ocultado em produção)")

        return {"status": "success", "received": True}

    except Exception as e:
        error_msg = f"Erro ao processar payload: {str(e)}"
        logger.error(f"❌ {error_msg}")

        try:
            body = await request.body()
            body_text = body.decode('utf-8')
            logger.error(f"⚠️ Conteúdo bruto recebido (primeiros 500 caracteres): {body_text[:500]}")
        except Exception as body_error:
            logger.error(f"⚠️ Não foi possível decodificar o corpo da requisição: {str(body_error)}")

        return JSONResponse(
            content={"error": error_msg},
            status_code=400
        )

# Middleware para log de todas as requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"\n🌐 Requisição recebida: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"📤 Resposta enviada: {response.status_code}")
    return response

# Ponto de entrada para execução local
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("principal:app", host="0.0.0.0", port=port, reload=True)




