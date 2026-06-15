from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import empresas, usuarios, fontes_dados, modelos_arquivo
from app.routers import conciliacoes, auth, arquivos, processamento, politicas_retencao, normalizacao
from app.routers import resultado_conciliacao
from app.routers import divergencias
from app.routers import extrato_anotado

app = FastAPI(
    title="iA16 Fechamento Inteligente",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(empresas.router)
app.include_router(usuarios.router)
app.include_router(fontes_dados.router)
app.include_router(modelos_arquivo.router)
app.include_router(conciliacoes.router)
app.include_router(auth.router)
app.include_router(arquivos.router)
app.include_router(processamento.router)
app.include_router(politicas_retencao.router)
app.include_router(normalizacao.router)
app.include_router(resultado_conciliacao.router)
app.include_router(divergencias.router)
app.include_router(extrato_anotado.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV, "schema": settings.DB_SCHEMA}
