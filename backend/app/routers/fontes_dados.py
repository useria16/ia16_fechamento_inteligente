from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.core.permissoes import empresa_ids_do_usuario, verificar_acesso_por_empresa_id
from app.models.fonte_dados import FonteDados
from app.models.usuario import Usuario
from app.schemas.fonte_dados import FonteDadosCreate, FonteDadosPatch, FonteDadosResponse
from app.schemas.resposta import RespostaSucesso, RespostaLista, paginar

router = APIRouter(prefix="/api/v1/fontes-dados", tags=["fontes-dados"])


@router.get("", response_model=RespostaLista[FonteDadosResponse])
def listar_fontes_dados(
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    ativo: bool | None = Query(None),
):
    query = db.query(FonteDados)

    if usuario.perfil != "admin_ia16":
        ids_permitidos = empresa_ids_do_usuario(usuario, db)
        query = query.filter(FonteDados.empresa_id.in_(ids_permitidos))

    if ativo is not None:
        query = query.filter(FonteDados.ativo == ativo)

    total = query.count()
    itens = query.offset((pagina - 1) * limite).limit(limite).all()

    return RespostaLista(
        dados=[FonteDadosResponse.model_validate(f) for f in itens],
        paginacao=paginar(total, pagina, limite),
    )


@router.post("", response_model=RespostaSucesso[FonteDadosResponse], status_code=status.HTTP_201_CREATED)
def criar_fonte_dados(
    dados: FonteDadosCreate,
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

    fonte = FonteDados(
        empresa_id=empresa_id,
        nome=dados.nome,
        tipo=dados.tipo,
        configuracao=dados.configuracao,
    )
    db.add(fonte)
    db.commit()
    db.refresh(fonte)

    return RespostaSucesso(
        dados=FonteDadosResponse.model_validate(fonte),
        mensagem="Fonte de dados criada com sucesso",
    )


@router.get("/{fonte_id}", response_model=RespostaSucesso[FonteDadosResponse])
def obter_fonte_dados(
    fonte_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    fonte = db.query(FonteDados).filter(FonteDados.id == fonte_id).first()
    if not fonte:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fonte de dados não encontrada")

    verificar_acesso_por_empresa_id(fonte.empresa_id, usuario, db)

    return RespostaSucesso(dados=FonteDadosResponse.model_validate(fonte))


@router.patch("/{fonte_id}", response_model=RespostaSucesso[FonteDadosResponse])
def atualizar_fonte_dados(
    fonte_id: str,
    dados: FonteDadosPatch,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil not in ("admin_ia16", "cliente_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil sem permissão")

    fonte = db.query(FonteDados).filter(FonteDados.id == fonte_id).first()
    if not fonte:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fonte de dados não encontrada")

    verificar_acesso_por_empresa_id(fonte.empresa_id, usuario, db)

    if dados.nome is not None:
        fonte.nome = dados.nome
    if dados.ativo is not None:
        fonte.ativo = dados.ativo
    if dados.configuracao is not None:
        fonte.configuracao = dados.configuracao

    fonte.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(fonte)

    return RespostaSucesso(
        dados=FonteDadosResponse.model_validate(fonte),
        mensagem="Fonte de dados atualizada com sucesso",
    )


@router.delete("/{fonte_id}", response_model=RespostaSucesso[FonteDadosResponse])
def inativar_fonte_dados(
    fonte_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil not in ("admin_ia16", "cliente_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil sem permissão")

    fonte = db.query(FonteDados).filter(FonteDados.id == fonte_id).first()
    if not fonte:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fonte de dados não encontrada")

    verificar_acesso_por_empresa_id(fonte.empresa_id, usuario, db)

    fonte.ativo = False
    fonte.atualizado_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(fonte)

    return RespostaSucesso(
        dados=FonteDadosResponse.model_validate(fonte),
        mensagem="Fonte de dados inativada com sucesso",
    )
