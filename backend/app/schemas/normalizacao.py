from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass
class ResultadoDeteccao:
    detectado: bool
    modelo_arquivo_id: str | None
    codigo_modelo: str | None
    confianca: float
    motivos: list[str]


@dataclass
class ResultadoNormalizacaoArquivo:
    arquivo_id: str
    tipo_arquivo: str
    codigo_modelo: str
    tipo_estrutura: str
    quantidade_registros: int
    realizados: list[Any]  # list[LancamentoRealizado]
    previstos: list[Any]   # list[LancamentoPrevisto]

    def amostra_realizados(self, n: int = 3) -> list[dict]:
        return [
            {
                "data_realizada": str(r.data_realizada),
                "descricao_realizada": r.descricao_realizada[:60],
                "valor_realizado": float(r.valor_realizado),
                "tipo_movimento": r.tipo_movimento,
            }
            for r in self.realizados[:n]
        ]

    def amostra_previstos(self, n: int = 3) -> list[dict]:
        return [
            {
                "data_prevista": str(r.data_prevista),
                "descricao_prevista": r.descricao_prevista[:60],
                "valor_previsto": float(r.valor_previsto),
                "tipo_movimento": r.tipo_movimento,
            }
            for r in self.previstos[:n]
        ]

    def amostra(self, n: int = 3) -> list[dict]:
        return self.amostra_realizados(n) or self.amostra_previstos(n)
