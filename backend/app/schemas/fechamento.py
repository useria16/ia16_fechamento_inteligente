import uuid
from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel

StatusFechamento = Literal[
    "rascunho", "arquivos_enviados", "em_processamento",
    "processado", "com_divergencias", "aprovado", "reaberto", "erro", "cancelado",
]


class ConciliacaoListagem(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID
    empresa_nome: str
    titulo: str
    tipo_conciliacao: str
    periodo_inicio: date
    periodo_fim: date
    status: StatusFechamento
    quantidade_divergencias: int
    criado_em: datetime

    model_config = {"from_attributes": True}


class ResumoConciliacoes(BaseModel):
    total: int
    em_processamento: int
    com_divergencias: int
    aprovadas: int


class ConciliacaoDetalhe(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID
    empresa_nome: str
    titulo: str
    tipo_conciliacao: str
    periodo_inicio: date
    periodo_fim: date
    status: StatusFechamento
    quantidade_registros: int
    quantidade_conciliados: int
    quantidade_divergencias: int
    quantidade_pendentes: int
    percentual_conciliado: float
    aprovado_em: datetime | None
    aprovado_por_usuario_id: uuid.UUID | None = None
    observacao_aprovacao: str | None = None
    reaberto_em: datetime | None = None
    reaberto_por_usuario_id: uuid.UUID | None = None
    motivo_reabertura: str | None = None
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class ConciliacaoCreate(BaseModel):
    titulo: str
    tipo_conciliacao: str
    periodo_inicio: date
    periodo_fim: date
    empresa_id: uuid.UUID
