from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import empresas, usuarios

app = FastAPI(
    title="iA16 Fechamento Inteligente",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(empresas.router)
app.include_router(usuarios.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV, "schema": settings.DB_SCHEMA}
