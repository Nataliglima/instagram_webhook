import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

app = FastAPI()

# Configuração do token via variável de ambiente
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "default_token_seguro")


# Verificação na inicialização
@app.on_event("startup")
async def startup_event():
    port = os.environ.get("PORT", "8000")
    print(f"✅ Servidor iniciado na porta {port}")
    print(f"✅ VERIFY_TOKEN configurado: {bool(VERIFY_TOKEN)}")
    print(f"✅ Valor do token: {'*****' + VERIFY_TOKEN[-3:] if VERIFY_TOKEN else 'NÃO CONFIGURADO'}")

    if not VERIFY_TOKEN or VERIFY_TOKEN == "default_token_seguro":
        print("⚠️ AVISO CRÍTICO: VERIFY_TOKEN não configurado corretamente!")
        print("ℹ️ Configure a variável de ambiente VERIFY_TOKEN no Render")


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
    # Log detalhado para depuração
    print(f"\n🔍 Solicitação GET /webhook recebida")
    print(f"🔍 Query params: {dict(request.query_params)}")

    # Extrai parâmetros da URL
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Verificação crítica do token
    if not VERIFY_TOKEN:
        error_msg = "VERIFY_TOKEN não configurado no servidor"
        print(f"❌ {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

    # Validação do token
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print(f"✅ Validação bem-sucedida! Challenge: {challenge}")
        return PlainTextResponse(content=challenge)

    # Montagem de detalhes do erro
    error_detail = f"Falha na verificação: mode={mode}, token_recebido={token}, token_esperado={VERIFY_TOKEN[:2]}...{VERIFY_TOKEN[-2:]}"
    print(f"❌ {error_detail}")

    return JSONResponse(
        content={"error": error_detail},
        status_code=403
    )


@app.post("/webhook")
async def handle_webhook(request: Request):
    print("\n📨 Evento POST /webhook recebido")

    try:
        # Tentativa de obter JSON
        payload = await request.json()
        print(f"✅ Payload recebido: {payload}")
        return {"status": "success", "received": True}

    except Exception as e:
        # Log detalhado de erro
        error_msg = f"Erro ao processar payload: {str(e)}"
        print(f"❌ {error_msg}")

        # Tentativa de ler como texto para diagnóstico
        try:
            body = await request.body()
            body_text = body.decode('utf-8')
            print(f"⚠️ Conteúdo bruto recebido: {body_text[:500]}...")
        except:
            print("⚠️ Não foi possível decodificar o corpo da requisição")

        return JSONResponse(
            content={"error": error_msg},
            status_code=400
        )


# Middleware para log de todas as requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"\n🌐 Requisição recebida: {request.method} {request.url}")
    response = await call_next(request)
    print(f"📤 Resposta enviada: {response.status_code}")
    return response




