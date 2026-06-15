"""
Endpoint de processamento da conciliação — Sprint 6B.

Fluxo: normalização de arquivos → motor de conciliação → persistência de itens e divergências.
"""
import io
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.models.arquivo_enviado import ArquivoEnviado
from app.models.fechamento_financeiro import FechamentoFinanceiro
from app.models.log_processamento import LogProcessamento
from app.models.usuario import Usuario
from app.schemas.processamento import ResultadoProcessamento
from app.schemas.resposta import RespostaErro, RespostaSucesso
from app.services.motor_conciliacao_service import ResultadoMotor, executar_motor
from app.services.normalizacao_arquivos_service import normalizar_arquivo
from app.services.processamento_extrato_anotado_service import processar_extrato_anotado
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/conciliacoes", tags=["processamento"])

STATUS_PERMITIDOS = {"rascunho", "arquivos_enviados", "erro"}
STATUS_BLOQUEADOS = {
    "em_processamento": "CONCILIACAO_EM_PROCESSAMENTO",
    "aprovado": "CONCILIACAO_APROVADA",
    "cancelado": "CONCILIACAO_CANCELADA",
}


def _log(
    db: Session,
    empresa_id: uuid.UUID,
    fechamento_id: uuid.UUID,
    nivel: str,
    evento: str,
    mensagem: str,
    arquivo_id: uuid.UUID | None = None,
    detalhes: dict | None = None,
) -> None:
    db.add(LogProcessamento(
        empresa_id=empresa_id,
        fechamento_id=fechamento_id,
        arquivo_id=arquivo_id,
        nivel=nivel,
        evento=evento,
        mensagem=mensagem,
        detalhes=detalhes,
    ))


def _mensagem_preparacao(status: str, motor: ResultadoMotor) -> str:
    if status == "erro":
        return "Falha no processamento: nenhum arquivo pôde ser lido."
    if status == "processado":
        return (
            f"Fechamento preparado sem divergências. "
            f"{motor.quantidade_conciliados} lançamento(s) conciliado(s)."
        )
    partes = []
    if motor.quantidade_divergentes > 0:
        partes.append(f"{motor.quantidade_divergentes} divergência(s) de valor")
    if motor.quantidade_pendentes > 0:
        partes.append(f"{motor.quantidade_pendentes} lançamento(s) pendente(s)")
    descricao = " e ".join(partes)
    return f"Fechamento preparado para revisão — {descricao} encontrado(s)."


@router.post(
    "/{conciliacao_id}/processar",
    response_model=RespostaSucesso[ResultadoProcessamento],
    responses={
        400: {"model": RespostaErro},
        403: {"model": RespostaErro},
        404: {"model": RespostaErro},
        409: {"model": RespostaErro},
    },
)
def processar_conciliacao(
    conciliacao_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    # ── 1. Verificar fechamento ───────────────────────────────────────────
    fechamento = db.query(FechamentoFinanceiro).filter(
        FechamentoFinanceiro.id == conciliacao_id
    ).first()
    if not fechamento:
        raise HTTPException(status_code=404, detail="Conciliação não encontrada")

    # ── 2. Verificar acesso ───────────────────────────────────────────────
    if usuario.perfil != "admin_ia16" and str(fechamento.empresa_id) != str(usuario.empresa_id):
        raise HTTPException(status_code=403, detail="Sem permissão para acessar esta conciliação")

    # ── 3. Verificar status bloqueado ─────────────────────────────────────
    if fechamento.status in STATUS_BLOQUEADOS:
        codigo = STATUS_BLOQUEADOS[fechamento.status]
        mensagens = {
            "CONCILIACAO_EM_PROCESSAMENTO": "Esta conciliação já está em processamento.",
            "CONCILIACAO_APROVADA": "Conciliação aprovada não pode ser reprocessada por este endpoint.",
            "CONCILIACAO_CANCELADA": "Conciliação cancelada não pode ser processada.",
        }
        raise HTTPException(status_code=409, detail={
            "sucesso": False,
            "erro": {
                "codigo": codigo,
                "mensagem": mensagens[codigo],
                "detalhes": {"conciliacao_id": conciliacao_id},
            },
        })

    # ── 4. Verificar arquivos disponíveis ─────────────────────────────────
    arquivos = db.query(ArquivoEnviado).filter(
        ArquivoEnviado.fechamento_id == conciliacao_id,
        ArquivoEnviado.status != "invalido",
        ArquivoEnviado.arquivo_persistido == True,  # noqa: E712
        ArquivoEnviado.excluido_em == None,  # noqa: E711
    ).all()

    if not arquivos:
        raise HTTPException(status_code=400, detail={
            "sucesso": False,
            "erro": {
                "codigo": "CONCILIACAO_SEM_ARQUIVOS",
                "mensagem": "Não é possível processar uma conciliação sem arquivos vinculados.",
                "detalhes": {"conciliacao_id": conciliacao_id},
            },
        })

    # ── 5. Branch: extrato_anotado ────────────────────────────────────────
    if fechamento.tipo_conciliacao == "extrato_anotado":
        return _processar_extrato_anotado(fechamento, arquivos, usuario, db)

    # ── 6. Iniciar processamento (bilateral) ──────────────────────────────
    fechamento.status = "em_processamento"
    fechamento.atualizado_em = datetime.now(timezone.utc)
    db.flush()

    _log(db, fechamento.empresa_id, fechamento.id,
         nivel="info", evento="processamento_iniciado",
         mensagem=f"Processamento iniciado. {len(arquivos)} arquivo(s) a processar.",
         detalhes={"quantidade_arquivos": len(arquivos), "usuario_id": str(usuario.id)})

    # ── 6. Normalizar arquivos ────────────────────────────────────────────
    total_registros = 0
    arquivos_ok = 0
    arquivos_sem_modelo = 0
    arquivos_com_erro = 0

    realizados_motor: list[tuple[uuid.UUID, Any]] = []
    previstos_motor: list[tuple[uuid.UUID, Any]] = []

    for arquivo in arquivos:
        try:
            deteccao, resultado = normalizar_arquivo(arquivo, db)

            if deteccao.detectado and resultado is not None:
                _log(db, fechamento.empresa_id, fechamento.id,
                     nivel="info", evento="modelo_arquivo_detectado",
                     mensagem=(
                         f"Modelo '{deteccao.codigo_modelo}' detectado para "
                         f"'{arquivo.nome_original}' (confiança: {deteccao.confianca:.0%})."
                     ),
                     arquivo_id=arquivo.id,
                     detalhes={
                         "nome_original": arquivo.nome_original,
                         "tipo_arquivo": arquivo.tipo_arquivo,
                         "codigo_modelo": deteccao.codigo_modelo,
                         "confianca": deteccao.confianca,
                         "motivos": deteccao.motivos,
                     })

                _log(db, fechamento.empresa_id, fechamento.id,
                     nivel="info", evento="arquivo_normalizado",
                     mensagem=(
                         f"'{arquivo.nome_original}' normalizado: "
                         f"{resultado.quantidade_registros} registro(s) "
                         f"via modelo '{resultado.codigo_modelo}'."
                     ),
                     arquivo_id=arquivo.id,
                     detalhes={
                         "quantidade_registros": resultado.quantidade_registros,
                         "codigo_modelo": resultado.codigo_modelo,
                         "tipo_estrutura": resultado.tipo_estrutura,
                         "amostra": resultado.amostra(n=2),
                     })

                # Separar por tipo de estrutura para o motor
                for r in resultado.realizados:
                    realizados_motor.append((arquivo.id, r))
                for p in resultado.previstos:
                    previstos_motor.append((arquivo.id, p))

                total_registros += resultado.quantidade_registros
                arquivo.status = "lido"
                arquivo.mensagem_erro = None
                arquivo.atualizado_em = datetime.now(timezone.utc)
                arquivos_ok += 1

            else:
                # Fallback genérico — conta linhas mas não contribui para conciliação
                _log(db, fechamento.empresa_id, fechamento.id,
                     nivel="aviso", evento="modelo_arquivo_nao_identificado",
                     mensagem=(
                         f"Modelo não identificado para '{arquivo.nome_original}' "
                         f"(tipo: {arquivo.tipo_arquivo}, confiança: {deteccao.confianca:.0%}). "
                         f"Leitura genérica aplicada — arquivo não contribuirá para conciliação."
                     ),
                     arquivo_id=arquivo.id,
                     detalhes={
                         "nome_original": arquivo.nome_original,
                         "tipo_arquivo": arquivo.tipo_arquivo,
                         "confianca": deteccao.confianca,
                         "motivos": deteccao.motivos,
                     })

                conteudo = _baixar_conteudo_fallback(arquivo.caminho_storage)
                df = pd.read_excel(io.BytesIO(conteudo), engine="openpyxl")
                total_registros += len(df)
                arquivo.status = "lido"
                arquivo.mensagem_erro = None
                arquivo.atualizado_em = datetime.now(timezone.utc)
                arquivos_sem_modelo += 1

        except Exception as exc:
            arquivos_com_erro += 1
            arquivo.status = "invalido"
            arquivo.mensagem_erro = str(exc)
            arquivo.atualizado_em = datetime.now(timezone.utc)

            _log(db, fechamento.empresa_id, fechamento.id,
                 nivel="erro", evento="erro_normalizacao_arquivo",
                 mensagem=f"Falha ao processar '{arquivo.nome_original}': {exc}",
                 arquivo_id=arquivo.id,
                 detalhes={"nome_original": arquivo.nome_original, "erro": str(exc)})

    arquivos_processados = arquivos_ok + arquivos_sem_modelo

    # ── 7. Executar motor de conciliação ──────────────────────────────────
    motor: ResultadoMotor | None = None
    motor_erro: str | None = None

    tem_registros_para_conciliar = len(realizados_motor) + len(previstos_motor) > 0

    if arquivos_processados > 0 and tem_registros_para_conciliar:
        _log(db, fechamento.empresa_id, fechamento.id,
             nivel="info", evento="motor_conciliacao_iniciado",
             mensagem=(
                 f"Motor iniciado: {len(realizados_motor)} lançamento(s) realizado(s), "
                 f"{len(previstos_motor)} lançamento(s) previsto(s)."
             ),
             detalhes={
                 "quantidade_realizados": len(realizados_motor),
                 "quantidade_previstos": len(previstos_motor),
             })

        try:
            motor = executar_motor(
                fechamento_id=fechamento.id,
                empresa_id=fechamento.empresa_id,
                realizados=realizados_motor,
                previstos=previstos_motor,
                db=db,
            )

            _log(db, fechamento.empresa_id, fechamento.id,
                 nivel="info", evento="motor_conciliacao_concluido",
                 mensagem=(
                     f"Motor concluído: {motor.quantidade_conciliados} conciliado(s), "
                     f"{motor.quantidade_divergentes} divergente(s), "
                     f"{motor.quantidade_pendentes} pendente(s)."
                 ),
                 detalhes={
                     "quantidade_conciliados": motor.quantidade_conciliados,
                     "quantidade_divergentes": motor.quantidade_divergentes,
                     "quantidade_pendentes": motor.quantidade_pendentes,
                     "valor_total_processado": str(motor.valor_total_processado),
                 })

        except Exception as exc:
            motor_erro = str(exc)
            _log(db, fechamento.empresa_id, fechamento.id,
                 nivel="erro", evento="motor_conciliacao_erro",
                 mensagem=f"Falha no motor de conciliação: {exc}",
                 detalhes={"erro": str(exc)})

    # ── 8. Determinar status final ────────────────────────────────────────
    if arquivos_processados == 0 or motor_erro:
        status_final = "erro"
    elif not tem_registros_para_conciliar:
        # Arquivos lidos apenas pelo fallback genérico — nenhum modelo reconhecido
        status_final = "erro"
    elif motor and (motor.quantidade_divergentes + motor.quantidade_pendentes) == 0:
        status_final = "processado"
    else:
        status_final = "com_divergencias"

    motor_result = motor or ResultadoMotor(
        quantidade_conciliados=0,
        quantidade_divergentes=0,
        quantidade_pendentes=0,
        valor_total_processado=Decimal("0"),
        valor_total_conciliado=Decimal("0"),
        valor_total_divergente=Decimal("0"),
    )
    mensagem_final = _mensagem_preparacao(status_final, motor_result)

    # ── 9. Atualizar fechamento ───────────────────────────────────────────
    fechamento.status = status_final
    fechamento.quantidade_registros = len(realizados_motor) + len(previstos_motor)
    fechamento.quantidade_conciliados = motor_result.quantidade_conciliados
    fechamento.quantidade_divergentes = motor_result.quantidade_divergentes
    fechamento.quantidade_pendentes = motor_result.quantidade_pendentes
    fechamento.valor_total_processado = motor_result.valor_total_processado
    fechamento.valor_total_conciliado = motor_result.valor_total_conciliado
    fechamento.valor_total_divergente = motor_result.valor_total_divergente
    fechamento.atualizado_em = datetime.now(timezone.utc)

    _log(db, fechamento.empresa_id, fechamento.id,
         nivel="info" if status_final != "erro" else "erro",
         evento="processamento_concluido",
         mensagem=mensagem_final,
         detalhes={
             "status_final": status_final,
             "total_registros": fechamento.quantidade_registros,
             "quantidade_conciliados": motor_result.quantidade_conciliados,
             "quantidade_divergentes": motor_result.quantidade_divergentes,
             "quantidade_pendentes": motor_result.quantidade_pendentes,
             "arquivos_com_modelo": arquivos_ok,
             "arquivos_sem_modelo": arquivos_sem_modelo,
             "arquivos_com_erro": arquivos_com_erro,
         })

    db.commit()

    resultado = ResultadoProcessamento(
        conciliacao_id=fechamento.id,
        status=status_final,
        quantidade_arquivos=len(arquivos),
        quantidade_registros=fechamento.quantidade_registros,
        quantidade_conciliados=motor_result.quantidade_conciliados,
        quantidade_divergentes=motor_result.quantidade_divergentes,
        quantidade_pendentes=motor_result.quantidade_pendentes,
        valor_total_processado=motor_result.valor_total_processado,
        mensagem_processamento=mensagem_final,
    )

    return RespostaSucesso(dados=resultado, mensagem=mensagem_final)


def _processar_extrato_anotado(
    fechamento: FechamentoFinanceiro,
    arquivos: list[ArquivoEnviado],
    usuario: Usuario,
    db: Session,
):
    """
    Fluxo específico para tipo_conciliacao = extrato_anotado.
    Normaliza o extrato bancário e, se disponível, o fluxo de caixa para conferência.
    O fluxo de caixa é opcional — sem ele, processa normalmente sem campos de conferência.
    """
    arquivo_extrato = next(
        (a for a in arquivos if a.tipo_arquivo == "extrato_bancario"), None
    )
    if not arquivo_extrato:
        raise HTTPException(status_code=400, detail={
            "sucesso": False,
            "erro": {
                "codigo": "EXTRATO_AUSENTE",
                "mensagem": "Conciliações do tipo extrato_anotado requerem um arquivo extrato_bancario.",
            },
        })

    # Arquivos adicionais (qualquer arquivo que não seja extrato — ex: planilha_interna = fluxo de caixa)
    arquivos_apoio = [a for a in arquivos if a.tipo_arquivo != "extrato_bancario"]

    qtd_arquivos = 1 + len(arquivos_apoio)
    fechamento.status = "em_processamento"
    fechamento.atualizado_em = datetime.now(timezone.utc)
    db.flush()

    _log(db, fechamento.empresa_id, fechamento.id,
         nivel="info", evento="processamento_iniciado",
         mensagem=(
             f"Processamento extrato_anotado iniciado. "
             f"{qtd_arquivos} arquivo(s): extrato bancário"
             + (f" + {len(arquivos_apoio)} arquivo(s) de apoio." if arquivos_apoio else ". Nenhum arquivo de apoio — conferência indisponível.")
         ),
         detalhes={
             "arquivo_extrato_id": str(arquivo_extrato.id),
             "arquivos_apoio_ids": [str(a.id) for a in arquivos_apoio],
             "usuario_id": str(usuario.id),
         })

    try:
        # ── Normalizar extrato bancário ───────────────────────────────────
        deteccao, resultado = normalizar_arquivo(arquivo_extrato, db)

        if not deteccao.detectado or resultado is None:
            raise ValueError(
                f"Modelo não identificado para '{arquivo_extrato.nome_original}' "
                f"(confiança: {deteccao.confianca:.0%}). Motivos: {deteccao.motivos}"
            )

        _log(db, fechamento.empresa_id, fechamento.id,
             nivel="info", evento="modelo_arquivo_detectado",
             mensagem=(
                 f"Modelo '{deteccao.codigo_modelo}' detectado para "
                 f"'{arquivo_extrato.nome_original}' (confiança: {deteccao.confianca:.0%})."
             ),
             arquivo_id=arquivo_extrato.id,
             detalhes={"codigo_modelo": deteccao.codigo_modelo, "confianca": deteccao.confianca})

        _log(db, fechamento.empresa_id, fechamento.id,
             nivel="info", evento="arquivo_normalizado",
             mensagem=(
                 f"'{arquivo_extrato.nome_original}' normalizado: "
                 f"{resultado.quantidade_registros} lançamento(s)."
             ),
             arquivo_id=arquivo_extrato.id)

        arquivo_extrato.status = "lido"
        arquivo_extrato.atualizado_em = datetime.now(timezone.utc)

        # ── Normalizar arquivos de apoio e coletar previstos (opcional) ───
        # Coleta previstos de qualquer arquivo que normalize para formato transposto
        # (ex: planilha_interna = fluxo de caixa Daxx)
        previstos_fluxo: list[Any] = []
        for arq_apoio in arquivos_apoio:
            try:
                deteccao_apoio, resultado_apoio = normalizar_arquivo(arq_apoio, db)
                if deteccao_apoio.detectado and resultado_apoio and resultado_apoio.previstos:
                    previstos_fluxo.extend(resultado_apoio.previstos)
                    arq_apoio.status = "lido"
                    arq_apoio.atualizado_em = datetime.now(timezone.utc)
                    _log(db, fechamento.empresa_id, fechamento.id,
                         nivel="info", evento="fluxo_caixa_normalizado",
                         mensagem=(
                             f"Arquivo de apoio '{arq_apoio.nome_original}' normalizado: "
                             f"{len(resultado_apoio.previstos)} previsto(s)."
                         ),
                         arquivo_id=arq_apoio.id)
                else:
                    arq_apoio.status = "lido"
                    arq_apoio.atualizado_em = datetime.now(timezone.utc)
                    _log(db, fechamento.empresa_id, fechamento.id,
                         nivel="aviso", evento="arquivo_apoio_sem_previstos",
                         mensagem=(
                             f"Arquivo '{arq_apoio.nome_original}' não gerou previstos "
                             f"(tipo: {arq_apoio.tipo_arquivo}). Não contribuirá para conferência."
                         ),
                         arquivo_id=arq_apoio.id)
            except Exception as exc_apoio:
                arq_apoio.status = "invalido"
                arq_apoio.mensagem_erro = str(exc_apoio)
                arq_apoio.atualizado_em = datetime.now(timezone.utc)
                _log(db, fechamento.empresa_id, fechamento.id,
                     nivel="aviso", evento="arquivo_apoio_erro",
                     mensagem=f"Falha ao normalizar '{arq_apoio.nome_original}': {exc_apoio}. Não contribuirá para conferência.",
                     arquivo_id=arq_apoio.id,
                     detalhes={"erro": str(exc_apoio)})

        # ── Processar e persistir lançamentos anotados ────────────────────
        resultado_anotado = processar_extrato_anotado(
            fechamento_id=fechamento.id,
            empresa_id=fechamento.empresa_id,
            arquivo=arquivo_extrato,
            realizados=resultado.realizados,
            db=db,
            previstos=previstos_fluxo,
        )

        n = resultado_anotado.quantidade_lancamentos
        status_final = "com_divergencias" if n > 0 else "processado"
        fechamento.status = status_final
        fechamento.quantidade_registros = n
        fechamento.quantidade_conciliados = 0
        fechamento.quantidade_divergentes = n
        fechamento.quantidade_pendentes = 0
        fechamento.valor_total_processado = (
            resultado_anotado.valor_total_entradas + resultado_anotado.valor_total_saidas
        )
        fechamento.valor_total_conciliado = Decimal("0")
        fechamento.valor_total_divergente = resultado_anotado.valor_total_saidas
        fechamento.atualizado_em = datetime.now(timezone.utc)

        sugestoes = resultado_anotado.quantidade_com_sugestao
        encontrados = resultado_anotado.quantidade_encontrados_fluxo
        nao_encontrados = resultado_anotado.quantidade_nao_encontrados_fluxo

        if previstos_fluxo:
            mensagem_final = (
                f"Extrato normalizado — {n} lançamento(s) prontos para revisão. "
                f"{sugestoes} com sugestão de categoria. "
                f"Conferência com fluxo: {encontrados} encontrado(s), "
                f"{nao_encontrados} não localizado(s)."
            )
        else:
            mensagem_final = (
                f"Extrato normalizado — {n} lançamento(s) prontos para revisão. "
                f"{sugestoes} com sugestão automática de categoria."
            )

        _log(db, fechamento.empresa_id, fechamento.id,
             nivel="info", evento="processamento_concluido",
             mensagem=mensagem_final,
             detalhes={
                 "status_final": status_final,
                 "quantidade_lancamentos": n,
                 "quantidade_com_sugestao": sugestoes,
                 "quantidade_encontrados_fluxo": encontrados,
                 "quantidade_nao_encontrados_fluxo": nao_encontrados,
                 "fluxo_disponivel": bool(previstos_fluxo),
             })

        db.commit()

        return RespostaSucesso(
            dados=ResultadoProcessamento(
                conciliacao_id=fechamento.id,
                status=status_final,
                quantidade_arquivos=qtd_arquivos,
                quantidade_registros=n,
                quantidade_conciliados=0,
                quantidade_divergentes=n,
                quantidade_pendentes=0,
                valor_total_processado=fechamento.valor_total_processado,
                mensagem_processamento=mensagem_final,
            ),
            mensagem=mensagem_final,
        )

    except Exception as exc:
        arquivo_extrato.status = "invalido"
        arquivo_extrato.mensagem_erro = str(exc)
        arquivo_extrato.atualizado_em = datetime.now(timezone.utc)

        fechamento.status = "erro"
        fechamento.atualizado_em = datetime.now(timezone.utc)

        _log(db, fechamento.empresa_id, fechamento.id,
             nivel="erro", evento="erro_normalizacao_arquivo",
             mensagem=f"Falha ao processar extrato anotado: {exc}",
             arquivo_id=arquivo_extrato.id,
             detalhes={"erro": str(exc)})

        db.commit()
        raise HTTPException(status_code=500, detail={
            "sucesso": False,
            "erro": {"codigo": "ERRO_PROCESSAMENTO_EXTRATO", "mensagem": str(exc)},
        }) from exc


def _baixar_conteudo_fallback(caminho: str) -> bytes:
    import httpx
    from app.core.config import settings
    url = f"{settings.SUPABASE_URL}/storage/v1/object/arquivos-originais/{caminho}"
    headers = {"Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}"}
    resp = httpx.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise ValueError(f"Falha ao baixar arquivo: HTTP {resp.status_code}")
    return resp.content
