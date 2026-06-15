import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

TipoArquivo = Literal[
    "extrato_bancario",
    "relatorio_vendas",
    "relatorio_recebiveis",
    "planilha_interna",
    "taxas_adquirente",
    "outro",
]


class ModeloArquivoCreate(BaseModel):
    nome: str
    tipo_arquivo: TipoArquivo
    mapeamento_colunas: dict[str, Any]
    empresa_id: uuid.UUID | None = None


class ModeloArquivoResponse(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID
    nome: str
    tipo_arquivo: TipoArquivo
    mapeamento_colunas: dict[str, Any]
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class ModeloArquivoPatch(BaseModel):
    nome: str | None = None
    mapeamento_colunas: dict[str, Any] | None = None
    ativo: bool | None = None
