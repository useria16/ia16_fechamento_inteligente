from typing import Annotated, Optional

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.models.divergencia_conciliacao import DivergenciaConciliacao
from app.models.empresa import Empresa
from app.models.fechamento_financeiro import FechamentoFinanceiro
from app.models.log_processamento import LogProcessamento
from app.models.usuario import Usuario
from app.models.lancamento_extrato_anotado import LancamentoExtratoAnotado
from app.schemas.aprovacao import AprovarFechamentoRequest, ReabrirFechamentoRequest, RespostaAprovacao, RespostaReabertura
from app.schemas.fechamento import ConciliacaoCreate, ConciliacaoDetalhe, ConciliacaoListagem, ResumoConciliacoes
from app.schemas.resposta import RespostaErro, RespostaLista, RespostaSucesso, paginar
from app.services.exportacao_fechamento_service import gerar_excel_fechamento

router = APIRouter(prefix="/api/v1/conciliacoes", tags=["conciliacoes"])


@router.get("", response_model=RespostaLista[ConciliacaoListagem])
def listar_conciliacoes(
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
    empresa_id: Optional[str] = Query(None),
    tipo_conciliacao: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    periodo_inicio: Optional[str] = Query(None),
    periodo_fim: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
):
    q = (
        db.query(FechamentoFinanceiro, Empresa.nome.label("empresa_nome"))
        .join(Empresa, Empresa.id == FechamentoFinanceiro.empresa_id)
    )

    # RLS por empresa
    if usuario.perfil != "admin_ia16":
        q = q.filter(FechamentoFinanceiro.empresa_id == usuario.empresa_id)
    elif empresa_id:
        q = q.filter(FechamentoFinanceiro.empresa_id == empresa_id)

    if tipo_conciliacao:
        q = q.filter(FechamentoFinanceiro.tipo_conciliacao == tipo_conciliacao)
    if status:
        q = q.filter(FechamentoFinanceiro.status == status)
    if periodo_inicio:
        q = q.filter(FechamentoFinanceiro.periodo_inicio >= periodo_inicio)
    if periodo_fim:
        q = q.filter(FechamentoFinanceiro.periodo_fim <= periodo_fim)
    if busca:
        q = q.filter(Empresa.nome.ilike(f"%{busca}%"))

    total = q.count()
    resultados = q.order_by(FechamentoFinanceiro.criado_em.desc()).offset((pagina - 1) * limite).limit(limite).all()

    dados = [
        ConciliacaoListagem(
            id=f.id,
            empresa_id=f.empresa_id,
            empresa_nome=nome,
            titulo=f.titulo,
            tipo_conciliacao=f.tipo_conciliacao,
            periodo_inicio=f.periodo_inicio,
            periodo_fim=f.periodo_fim,
            status=f.status,
            quantidade_divergencias=f.quantidade_divergentes,
            criado_em=f.criado_em,
        )
        for f, nome in resultados
    ]

    return RespostaLista(dados=dados, paginacao=paginar(total, pagina, limite))


@router.post("", response_model=RespostaSucesso[ConciliacaoListagem], status_code=status.HTTP_201_CREATED)
def criar_conciliacao(
    dados: ConciliacaoCreate,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil == "admin_ia16":
        if not dados.empresa_id:
            raise HTTPException(status_code=400, detail="empresa_id é obrigatório para admin_ia16")
        empresa_id = dados.empresa_id
    else:
        if not usuario.empresa_id:
            raise HTTPException(status_code=400, detail="Usuário sem empresa vinculada")
        empresa_id = usuario.empresa_id

    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    if dados.periodo_fim < dados.periodo_inicio:
        raise HTTPException(status_code=422, detail="periodo_fim deve ser posterior a periodo_inicio")

    fechamento = FechamentoFinanceiro(
        empresa_id=empresa_id,
        criado_por_usuario_id=usuario.id,
        titulo=dados.titulo,
        tipo_conciliacao=dados.tipo_conciliacao,
        periodo_inicio=dados.periodo_inicio,
        periodo_fim=dados.periodo_fim,
        status="rascunho",
        atualizado_em=datetime.now(timezone.utc),
    )
    db.add(fechamento)
    db.commit()
    db.refresh(fechamento)

    resposta = ConciliacaoListagem(
        id=fechamento.id,
        empresa_id=fechamento.empresa_id,
        empresa_nome=empresa.nome,
        titulo=fechamento.titulo,
        tipo_conciliacao=fechamento.tipo_conciliacao,
        periodo_inicio=fechamento.periodo_inicio,
        periodo_fim=fechamento.periodo_fim,
        status=fechamento.status,
        quantidade_divergencias=fechamento.quantidade_divergentes,
        criado_em=fechamento.criado_em,
    )
    return RespostaSucesso(dados=resposta, mensagem="Conciliação criada com sucesso")


@router.get("/resumo", response_model=RespostaSucesso[ResumoConciliacoes])
def resumo_conciliacoes(
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    q = db.query(FechamentoFinanceiro)

    if usuario.perfil != "admin_ia16":
        q = q.filter(FechamentoFinanceiro.empresa_id == usuario.empresa_id)

    todos = q.all()

    resumo = ResumoConciliacoes(
        total=len(todos),
        em_processamento=sum(1 for f in todos if f.status == "em_processamento"),
        com_divergencias=sum(1 for f in todos if f.status == "com_divergencias"),
        aprovadas=sum(1 for f in todos if f.status == "aprovado"),
    )

    return RespostaSucesso(dados=resumo)


@router.get("/{conciliacao_id}", response_model=RespostaSucesso[ConciliacaoDetalhe])
def obter_conciliacao(
    conciliacao_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    resultado = (
        db.query(FechamentoFinanceiro, Empresa.nome.label("empresa_nome"))
        .join(Empresa, Empresa.id == FechamentoFinanceiro.empresa_id)
        .filter(FechamentoFinanceiro.id == conciliacao_id)
        .first()
    )

    if not resultado:
        raise HTTPException(status_code=404, detail="Conciliação não encontrada")

    f, empresa_nome = resultado

    if usuario.perfil != "admin_ia16" and str(f.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(status_code=403, detail="Sem permissão para acessar esta conciliação")

    percentual = (
        round(f.quantidade_conciliados / f.quantidade_registros * 100, 1)
        if f.quantidade_registros > 0 else 0.0
    )

    detalhe = ConciliacaoDetalhe(
        id=f.id,
        empresa_id=f.empresa_id,
        empresa_nome=empresa_nome,
        titulo=f.titulo,
        tipo_conciliacao=f.tipo_conciliacao,
        periodo_inicio=f.periodo_inicio,
        periodo_fim=f.periodo_fim,
        status=f.status,
        quantidade_registros=f.quantidade_registros,
        quantidade_conciliados=f.quantidade_conciliados,
        quantidade_divergencias=f.quantidade_divergentes,
        quantidade_pendentes=f.quantidade_pendentes,
        percentual_conciliado=percentual,
        aprovado_em=f.aprovado_em,
        criado_em=f.criado_em,
        atualizado_em=f.atualizado_em,
    )
    return RespostaSucesso(dados=detalhe)


# ── helpers compartilhados ─────────────────────────────────────────────────────

_STATUS_NAO_APROVAVEL = {"rascunho", "arquivos_enviados", "em_processamento", "erro", "cancelado"}
_STATUS_EXPORTAVEL = {"processado", "com_divergencias", "aprovado", "reaberto"}


def _buscar_fechamento_com_acesso(
    conciliacao_id: str,
    usuario: Usuario,
    db: Session,
) -> FechamentoFinanceiro:
    fechamento = db.query(FechamentoFinanceiro).filter(FechamentoFinanceiro.id == conciliacao_id).first()
    if not fechamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"sucesso": False, "erro": {"codigo": "FECHAMENTO_NAO_ENCONTRADO", "mensagem": "Conciliação não encontrada."}},
        )
    if usuario.perfil != "admin_ia16" and str(fechamento.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"sucesso": False, "erro": {"codigo": "SEM_PERMISSAO_FECHAMENTO", "mensagem": "Sem permissão para acessar esta conciliação."}},
        )
    return fechamento


def _registrar_log(db: Session, fechamento: FechamentoFinanceiro, usuario: Usuario, evento: str, mensagem: str, detalhes: dict) -> None:
    db.add(LogProcessamento(
        empresa_id=fechamento.empresa_id,
        fechamento_id=fechamento.id,
        nivel="info",
        evento=evento,
        mensagem=mensagem,
        detalhes={"usuario_id": str(usuario.id), "usuario_email": usuario.email, **detalhes},
    ))


# ── POST /{id}/aprovar ─────────────────────────────────────────────────────────

@router.post(
    "/{conciliacao_id}/aprovar",
    response_model=RespostaSucesso[RespostaAprovacao],
    responses={
        403: {"model": RespostaErro},
        404: {"model": RespostaErro},
        409: {"model": RespostaErro},
    },
)
def aprovar_conciliacao(
    conciliacao_id: str,
    dados: AprovarFechamentoRequest,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil == "cliente_operador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"sucesso": False, "erro": {"codigo": "PERFIL_SEM_PERMISSAO_APROVACAO", "mensagem": "Operadores não podem aprovar fechamentos."}},
        )

    fechamento = _buscar_fechamento_com_acesso(conciliacao_id, usuario, db)

    if fechamento.status in _STATUS_NAO_APROVAVEL:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "FECHAMENTO_NAO_PODE_SER_APROVADO",
                    "mensagem": f"Fechamento com status '{fechamento.status}' não pode ser aprovado.",
                },
            },
        )

    # ── Verificar pendências conforme tipo ───────────────────────────────────
    if fechamento.tipo_conciliacao == "extrato_anotado":
        lancamentos_pendentes = (
            db.query(LancamentoExtratoAnotado)
            .filter(
                LancamentoExtratoAnotado.fechamento_id == fechamento.id,
                LancamentoExtratoAnotado.status_revisao.in_(["pendente", "em_revisao"]),
            )
            .count()
        )
        if lancamentos_pendentes > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "sucesso": False,
                    "erro": {
                        "codigo": "LANCAMENTOS_PENDENTES_IMPEDEM_APROVACAO",
                        "mensagem": "Existem lançamentos pendentes de revisão. Revise ou ignore todos antes de aprovar o fechamento.",
                        "detalhes": {"quantidade_pendentes": lancamentos_pendentes},
                    },
                },
            )
    else:
        divergencias_abertas = (
            db.query(DivergenciaConciliacao)
            .filter(
                DivergenciaConciliacao.fechamento_id == fechamento.id,
                DivergenciaConciliacao.status.in_(["aberta", "em_analise"]),
            )
            .count()
        )
        if divergencias_abertas > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "sucesso": False,
                    "erro": {
                        "codigo": "DIVERGENCIAS_ABERTAS_IMPEDEM_APROVACAO",
                        "mensagem": f"Existem {divergencias_abertas} divergência(s) em aberto ou em análise. Resolva ou ignore-as antes de aprovar.",
                        "detalhes": {"quantidade_pendentes": divergencias_abertas},
                    },
                },
            )

    agora = datetime.now(timezone.utc)
    status_anterior = fechamento.status
    fechamento.status = "aprovado"
    fechamento.aprovado_em = agora
    fechamento.aprovado_por_usuario_id = usuario.id
    fechamento.observacao_aprovacao = dados.observacao_aprovacao
    fechamento.atualizado_em = agora

    _registrar_log(db, fechamento, usuario, "fechamento_aprovado", f"Fechamento aprovado por '{usuario.email}'.", {
        "status_anterior": status_anterior,
        "observacao_aprovacao": dados.observacao_aprovacao or "",
    })

    db.commit()
    db.refresh(fechamento)

    return RespostaSucesso(
        dados=RespostaAprovacao(
            id=fechamento.id,
            status=fechamento.status,
            aprovado_em=agora,
            aprovado_por_usuario_id=usuario.id,
            observacao_aprovacao=fechamento.observacao_aprovacao,
        ),
        mensagem="Fechamento aprovado com sucesso.",
    )


# ── POST /{id}/reabrir ─────────────────────────────────────────────────────────

@router.post(
    "/{conciliacao_id}/reabrir",
    response_model=RespostaSucesso[RespostaReabertura],
    responses={
        403: {"model": RespostaErro},
        404: {"model": RespostaErro},
        409: {"model": RespostaErro},
    },
)
def reabrir_conciliacao(
    conciliacao_id: str,
    dados: ReabrirFechamentoRequest,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil == "cliente_operador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"sucesso": False, "erro": {"codigo": "PERFIL_SEM_PERMISSAO_REABERTURA", "mensagem": "Operadores não podem reabrir fechamentos."}},
        )

    fechamento = _buscar_fechamento_com_acesso(conciliacao_id, usuario, db)

    if fechamento.status != "aprovado":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "FECHAMENTO_NAO_ESTA_APROVADO",
                    "mensagem": f"Somente fechamentos aprovados podem ser reabertos. Status atual: '{fechamento.status}'.",
                },
            },
        )

    agora = datetime.now(timezone.utc)
    fechamento.status = "reaberto"
    fechamento.reaberto_em = agora
    fechamento.reaberto_por_usuario_id = usuario.id
    fechamento.motivo_reabertura = dados.motivo
    fechamento.atualizado_em = agora

    _registrar_log(db, fechamento, usuario, "fechamento_reaberto", f"Fechamento reaberto por '{usuario.email}'.", {
        "motivo": dados.motivo or "",
    })

    db.commit()
    db.refresh(fechamento)

    return RespostaSucesso(
        dados=RespostaReabertura(
            id=fechamento.id,
            status=fechamento.status,
            reaberto_em=agora,
            reaberto_por_usuario_id=usuario.id,
        ),
        mensagem="Fechamento reaberto para revisão.",
    )


# ── GET /{id}/exportar ─────────────────────────────────────────────────────────

@router.get(
    "/{conciliacao_id}/exportar",
    responses={
        403: {"model": RespostaErro},
        404: {"model": RespostaErro},
        409: {"model": RespostaErro},
    },
)
def exportar_conciliacao(
    conciliacao_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    fechamento = _buscar_fechamento_com_acesso(conciliacao_id, usuario, db)

    if fechamento.status not in _STATUS_EXPORTAVEL:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "sucesso": False,
                "erro": {
                    "codigo": "FECHAMENTO_SEM_PROCESSAMENTO",
                    "mensagem": f"Fechamento com status '{fechamento.status}' ainda não pode ser exportado. É necessário ter sido processado.",
                },
            },
        )

    try:
        conteudo, nome_arquivo = gerar_excel_fechamento(db, fechamento)
    except Exception as exc:
        _registrar_log(db, fechamento, usuario, "erro_exportacao_relatorio", f"Erro ao gerar relatório: {exc}", {})
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"sucesso": False, "erro": {"codigo": "ERRO_GERACAO_RELATORIO", "mensagem": "Erro ao gerar o relatório Excel."}},
        ) from exc

    _registrar_log(db, fechamento, usuario, "relatorio_fechamento_exportado", f"Relatório exportado por '{usuario.email}'.", {
        "nome_arquivo": nome_arquivo,
    })
    db.commit()

    return Response(
        content=conteudo,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )
