import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, model_validator

ModoRetencao = Literal["somente_memoria", "temporario", "persistente"]


class PoliticaRetencaoArquivoResponse(BaseModel):
    id: uuid.UUID
    empresa_id: uuid.UUID
    modo_retencao: ModoRetencao
    salvar_arquivo_original: bool
    salvar_resultado_processado: bool
    salvar_linhas_processadas: bool
    salvar_metadados: bool
    tempo_retencao_horas: int | None
    excluir_arquivo_original_apos_processamento: bool
    permitir_download_original: bool
    permitir_reprocessamento_sem_reenvio: bool
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class PoliticaRetencaoArquivoUpdate(BaseModel):
    modo_retencao: ModoRetencao
    salvar_arquivo_original: bool
    salvar_resultado_processado: bool
    salvar_linhas_processadas: bool
    salvar_metadados: bool
    tempo_retencao_horas: int | None = None
    excluir_arquivo_original_apos_processamento: bool
    permitir_download_original: bool
    permitir_reprocessamento_sem_reenvio: bool
    ativo: bool

    @model_validator(mode="after")
    def validar_consistencia(self) -> "PoliticaRetencaoArquivoUpdate":
        if self.modo_retencao == "temporario" and not self.tempo_retencao_horas:
            raise ValueError("tempo_retencao_horas é obrigatório para modo_retencao = temporario")
        if self.tempo_retencao_horas is not None and self.tempo_retencao_horas <= 0:
            raise ValueError("tempo_retencao_horas deve ser maior que zero")
        if self.modo_retencao == "somente_memoria" and self.salvar_arquivo_original:
            raise ValueError("salvar_arquivo_original deve ser false para modo_retencao = somente_memoria")
        if not self.salvar_arquivo_original:
            if self.permitir_download_original:
                raise ValueError("permitir_download_original deve ser false quando salvar_arquivo_original = false")
            if self.permitir_reprocessamento_sem_reenvio:
                raise ValueError("permitir_reprocessamento_sem_reenvio deve ser false quando salvar_arquivo_original = false")
        return self
