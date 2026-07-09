from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.core.permissoes import empresa_ids_do_usuario, verificar_acesso_por_empresa_id
from app.models.modelo_arquivo import ModeloArquivo
from app.models.usuario import Usuario
from app.schemas.modelo_arquivo import ModeloArquivoCreate, ModeloArquivoPatch, ModeloArquivoResponse
from app.schemas.resposta import RespostaSucesso, RespostaLista, paginar

router = APIRouter(prefix="/api/v1/modelos-arquivo", tags=["modelos-arquivo"])


@router.get("", response_model=RespostaLista[ModeloArquivoResponse])
def listar_modelos_arquivo(
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    tipo_arquivo: str | None = Query(None),
    ativo: bool | None = Query(None),
):
    query = db.query(ModeloArquivo)

    if usuario.perfil != "admin_ia16":
        ids_permitidos = empresa_ids_do_usuario(usuario, db)
        query = query.filter(ModeloArquivo.empresa_id.in_(ids_permitidos))

    if tipo_arquivo:
        query = query.filter(ModeloArquivo.tipo_arquivo == tipo_arquivo)
    if ativo is not None:
        query = query.filter(ModeloArquivo.ativo == ativo)

    total = query.count()
    itens = query.offset((pagina - 1) * limite).limit(limite).all()

    return RespostaLista(
        dados=[ModeloArquivoResponse.model_validate(m) for m in itens],
        paginacao=paginar(total, pagina, limite),
    )


@router.post("", response_model=RespostaSucesso[ModeloArquivoResponse], status_code=status.HTTP_201_CREATED)
def criar_modelo_arquivo(
    dados: ModeloArquivoCreate,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil not in ("admin_ia16", "cliente_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil sem permissão")

    if not dados.empresa_id:
        if usuario.empresa_id:
            dados.empresa_id = usuario.empresa_id  # fallback legado
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="empresa_id obrigatório")
    verificar_acesso_por_empresa_id(dados.empresa_id, usuario, db)
    empresa_id = dados.empresa_id

    modelo = ModeloArquivo(
        empresa_id=empresa_id,
        nome=dados.nome,
        tipo_arquivo=dados.tipo_arquivo,
        mapeamento_colunas=dados.mapeamento_colunas,
    )
    db.add(modelo)
    db.commit()
    db.refresh(modelo)

    return RespostaSucesso(
        dados=ModeloArquivoResponse.model_validate(modelo),
        mensagem="Modelo de arquivo criado com sucesso",
    )


@router.get("/{modelo_id}", response_model=RespostaSucesso[ModeloArquivoResponse])
def obter_modelo_arquivo(
    modelo_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    modelo = db.query(ModeloArquivo).filter(ModeloArquivo.id == modelo_id).first()
    if not modelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo de arquivo não encontrado")

    verificar_acesso_por_empresa_id(modelo.empresa_id, usuario, db)

    return RespostaSucesso(dados=ModeloArquivoResponse.model_validate(modelo))


@router.patch("/{modelo_id}", response_model=RespostaSucesso[ModeloArquivoResponse])
def atualizar_modelo_arquivo(
    modelo_id: str,
    dados: ModeloArquivoPatch,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil not in ("admin_ia16", "cliente_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil sem permissão")

    modelo = db.query(ModeloArquivo).filter(ModeloArquivo.id == modelo_id).first()
    if not modelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo de arquivo não encontrado")

    verificar_acesso_por_empresa_id(modelo.empresa_id, usuario, db)

    if dados.nome is not None:
        modelo.nome = dados.nome
    if dados.mapeamento_colunas is not None:
        modelo.mapeamento_colunas = dados.mapeamento_colunas
    if dados.ativo is not None:
        modelo.ativo = dados.ativo

    modelo.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(modelo)

    return RespostaSucesso(
        dados=ModeloArquivoResponse.model_validate(modelo),
        mensagem="Modelo de arquivo atualizado com sucesso",
    )
