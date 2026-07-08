"""
Serviço de processamento para conciliações do tipo extrato_anotado.

Fluxo:
  1. Exige apenas 1 arquivo extrato_bancario.
  2. Normaliza o extrato via normalizador tabular.
  3. Sugere categoria automaticamente por regras determinísticas.
  4. Se previstos do fluxo de caixa estiverem disponíveis, executa conferência.
  5. Persiste os lançamentos em lancamentos_extrato_anotado.
  6. Retorna contadores para atualizar o fechamento.
"""
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models.arquivo_enviado import ArquivoEnviado
from app.models.lancamento_extrato_anotado import LancamentoExtratoAnotado
from app.services.conferencia_fluxo_service import conferir_lancamentos

# ── Regras de sugestão de categoria ──────────────────────────────────────────

_REGRAS_CATEGORIA: list[tuple[list[str], str]] = [
    (["REND PAGO", "RENDIMENTO", "APLIC AUT", "REND RECEBIDO"],   "Rendimento"),
    (["TARIFA", "TAR ", "ANUIDADE"],                               "Tarifa bancária"),
    (["PIX RECEBIDO", "TED RECEBIDA", "RECEBIMENTOS", "DOC RECEBIDO"], "Recebimento"),
    (["PIX ENVIADO", "PIX QR-CODE", "PIX PAGO"],                  "Pagamento PIX"),
    (["BOLETO PAGO", "BOLETO"],                                    "Pagamento boleto"),
    (["PAGAMENTOS TRANSF", "TRANSF CC", "TED ENVIADA"],           "Transferência"),
    (["PAGAMENTOS TRIB", "TRIB COD", "DARF", "GPS", "GNRE"],      "Tributo"),
    (["SISPAG", "PAGAMENTO FORNEC"],                               "Pagamento fornecedor"),
    (["SALARIO", "FOLHA", "PROLABORE", "PRÓ-LABORE", "RETIRADA"],  "Remuneração"),
    (["IOF"],                                                      "IOF"),
]


def _sugerir_categoria(descricao: str) -> tuple[str | None, Decimal | None]:
    desc_upper = (descricao or "").upper()
    for palavras_chave, categoria in _REGRAS_CATEGORIA:
        if any(p in desc_upper for p in palavras_chave):
            return categoria, Decimal("0.8")
    return None, None


# ── Processamento principal ───────────────────────────────────────────────────

class ResultadoExtratoAnotado:
    def __init__(self):
        self.quantidade_lancamentos: int = 0
        self.quantidade_com_sugestao: int = 0
        self.quantidade_encontrados_fluxo: int = 0
        self.quantidade_nao_encontrados_fluxo: int = 0
        self.valor_total_entradas: Decimal = Decimal("0")
        self.valor_total_saidas: Decimal = Decimal("0")


def processar_extrato_anotado(
    fechamento_id: uuid.UUID,
    empresa_id: uuid.UUID,
    arquivo: ArquivoEnviado,
    realizados: list[Any],
    db: Session,
    previstos: list[Any] | None = None,
) -> ResultadoExtratoAnotado:
    """
    Cria lançamentos anotáveis a partir dos realizados normalizados.
    Remove lançamentos anteriores (suporte a reprocessamento).
    Se previstos forem fornecidos, enriquece cada lançamento com dados de conferência.
    Não faz commit — responsabilidade do chamador.
    """
    # Limpar lançamentos anteriores
    db.query(LancamentoExtratoAnotado).filter(
        LancamentoExtratoAnotado.fechamento_id == fechamento_id
    ).delete(synchronize_session=False)

    resultado = ResultadoExtratoAnotado()

    # Conferência com fluxo de caixa (lista vazia = sem conferência disponível)
    conferencias = conferir_lancamentos(realizados, previstos or [])

    for r, conf in zip(realizados, conferencias):
        categoria_sugerida, confianca = _sugerir_categoria(r.descricao_realizada or "")

        lancamento = LancamentoExtratoAnotado(
            empresa_id=empresa_id,
            fechamento_id=fechamento_id,
            arquivo_id=arquivo.id,
            data_lancamento=r.data_realizada,
            descricao_banco=r.descricao_realizada or "",
            razao_social=r.razao_social,
            documento=r.documento,
            valor=abs(r.valor_realizado),
            tipo_movimento=r.tipo_movimento,
            saldo=r.saldo,
            linha_origem=r.linha_origem,
            categoria_sugerida=categoria_sugerida,
            confianca_sugestao=confianca,
            status_revisao="pendente",
            atualizado_em=datetime.now(timezone.utc),
            # Conferência com fluxo
            previsto_no_fluxo=conf.previsto_no_fluxo,
            tipo_conferencia_fluxo=conf.tipo_conferencia_fluxo,
            confianca_conferencia=conf.confianca_conferencia,
            observacao_sistema=conf.observacao_sistema,
            data_prevista=conf.data_prevista,
            valor_previsto=conf.valor_previsto,
            descricao_prevista=conf.descricao_prevista,
        )
        db.add(lancamento)

        resultado.quantidade_lancamentos += 1
        if categoria_sugerida:
            resultado.quantidade_com_sugestao += 1
        if conf.tipo_conferencia_fluxo == "encontrado":
            resultado.quantidade_encontrados_fluxo += 1
        elif conf.tipo_conferencia_fluxo == "nao_encontrado":
            resultado.quantidade_nao_encontrados_fluxo += 1
        if r.tipo_movimento == "entrada":
            resultado.valor_total_entradas += abs(r.valor_realizado)
        else:
            resultado.valor_total_saidas += abs(r.valor_realizado)

    return resultado
