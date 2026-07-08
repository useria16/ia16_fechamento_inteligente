"""
Endpoints de detecção de modelo e normalização de arquivos.
Apoio técnico para diagnóstico e validação da Sprint 6A.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.models.arquivo_enviado import ArquivoEnviado
from app.models.usuario import Usuario
from app.schemas.resposta import RespostaSucesso, RespostaErro
from app.services.normalizacao_arquivos_service import baixar_conteudo, normalizar_arquivo
from app.services.detectores_modelo_arquivo_service import detectar_modelo

router = APIRouter(prefix="/api/v1/arquivos", tags=["normalizacao"])


def _verificar_acesso_arquivo(
    arquivo_id: str,
    usuario: Usuario,
    db: Session,
) -> ArquivoEnviado:
    arquivo = db.query(ArquivoEnviado).filter(ArquivoEnviado.id == arquivo_id).first()
    if not arquivo:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    if usuario.perfil != "admin_ia16" and str(arquivo.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(status_code=403, detail="Sem permissão para acessar este arquivo")
    if not arquivo.arquivo_persistido or arquivo.excluido_em is not None:
        raise HTTPException(status_code=409, detail="Arquivo não está mais disponível no Storage")
    return arquivo


@router.post("/{arquivo_id}/detectar-modelo", response_model=RespostaSucesso[dict])
def detectar_modelo_arquivo(
    arquivo_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    arquivo = _verificar_acesso_arquivo(arquivo_id, usuario, db)
    conteudo = baixar_conteudo(arquivo.caminho_storage)
    deteccao = detectar_modelo(conteudo, arquivo.tipo_arquivo, db)

    dados = {
        "arquivo_id": arquivo_id,
        "tipo_arquivo": arquivo.tipo_arquivo,
        "modelo_identificado": deteccao.detectado,
        "modelo_arquivo_id": deteccao.modelo_arquivo_id,
        "codigo_modelo": deteccao.codigo_modelo,
        "confianca": deteccao.confianca,
        "motivos": deteccao.motivos,
    }

    if not deteccao.detectado:
        raise HTTPException(
            status_code=422,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "MODELO_ARQUIVO_NAO_IDENTIFICADO",
                    "mensagem": "Modelo de arquivo não identificado. Configure o modelo antes de processar.",
                    "detalhes": dados,
                },
            },
        )

    return RespostaSucesso(dados=dados, mensagem="Modelo identificado com sucesso")


@router.post("/{arquivo_id}/normalizar", response_model=RespostaSucesso[dict])
def normalizar_arquivo_endpoint(
    arquivo_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    arquivo = _verificar_acesso_arquivo(arquivo_id, usuario, db)
    conteudo = baixar_conteudo(arquivo.caminho_storage)

    deteccao, resultado = normalizar_arquivo(arquivo, db, conteudo=conteudo)

    if not deteccao.detectado or resultado is None:
        raise HTTPException(
            status_code=422,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "MODELO_ARQUIVO_NAO_IDENTIFICADO",
                    "mensagem": "Modelo de arquivo não identificado. Configure o modelo antes de processar.",
                    "detalhes": {
                        "arquivo_id": arquivo_id,
                        "tipo_arquivo": arquivo.tipo_arquivo,
                        "confianca": deteccao.confianca,
                        "motivos": deteccao.motivos,
                    },
                },
            },
        )

    dados = {
        "arquivo_id": arquivo_id,
        "tipo_arquivo": resultado.tipo_arquivo,
        "modelo_arquivo": resultado.codigo_modelo,
        "quantidade_registros": resultado.quantidade_registros,
        "amostra": resultado.amostra(n=3),
    }

    return RespostaSucesso(dados=dados, mensagem="Arquivo normalizado com sucesso")
