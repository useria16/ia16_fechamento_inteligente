from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_usuario_atual
from app.core.database import get_db
from app.core.permissoes import verificar_acesso_por_empresa_id
from app.models.politica_retencao_arquivo import PoliticaRetencaoArquivo
from app.models.empresa import Empresa
from app.models.usuario import Usuario
from app.schemas.politica_retencao_arquivo import (
    PoliticaRetencaoArquivoResponse,
    PoliticaRetencaoArquivoUpdate,
)
from app.schemas.resposta import RespostaSucesso
from app.services.retencao_arquivos_service import buscar_politica_ativa

router = APIRouter(prefix="/api/v1/empresas", tags=["politicas-retencao"])


def _verificar_empresa(empresa_id: str, db: Session) -> Empresa:
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa


@router.get(
    "/{empresa_id}/politica-retencao-arquivos",
    response_model=RespostaSucesso[PoliticaRetencaoArquivoResponse],
)
def obter_politica_retencao(
    empresa_id: str,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    _verificar_empresa(empresa_id, db)

    if usuario.perfil == "cliente_operador":
        raise HTTPException(status_code=403, detail="Sem permissão")

    verificar_acesso_por_empresa_id(empresa_id, usuario, db)

    politica = buscar_politica_ativa(empresa_id, db)
    db.commit()  # persiste caso política padrão tenha sido criada

    return RespostaSucesso(
        dados=PoliticaRetencaoArquivoResponse.model_validate(politica),
        mensagem="Política de retenção encontrada",
    )


@router.put(
    "/{empresa_id}/politica-retencao-arquivos",
    response_model=RespostaSucesso[PoliticaRetencaoArquivoResponse],
)
def atualizar_politica_retencao(
    empresa_id: str,
    dados: PoliticaRetencaoArquivoUpdate,
    usuario: Annotated[Usuario, Depends(get_usuario_atual)],
    db: Annotated[Session, Depends(get_db)],
):
    if usuario.perfil != "admin_ia16":
        raise HTTPException(status_code=403, detail="Apenas admin_ia16 pode alterar a política de retenção")

    _verificar_empresa(empresa_id, db)

    politica = db.query(PoliticaRetencaoArquivo).filter(
        PoliticaRetencaoArquivo.empresa_id == empresa_id,
    ).first()

    if politica is None:
        politica = PoliticaRetencaoArquivo(empresa_id=empresa_id)
        db.add(politica)

    politica.modo_retencao = dados.modo_retencao
    politica.salvar_arquivo_original = dados.salvar_arquivo_original
    politica.salvar_resultado_processado = dados.salvar_resultado_processado
    politica.salvar_linhas_processadas = dados.salvar_linhas_processadas
    politica.salvar_metadados = dados.salvar_metadados
    politica.tempo_retencao_horas = dados.tempo_retencao_horas
    politica.excluir_arquivo_original_apos_processamento = dados.excluir_arquivo_original_apos_processamento
    politica.permitir_download_original = dados.permitir_download_original
    politica.permitir_reprocessamento_sem_reenvio = dados.permitir_reprocessamento_sem_reenvio
    politica.ativo = dados.ativo

    db.commit()
    db.refresh(politica)

    return RespostaSucesso(
        dados=PoliticaRetencaoArquivoResponse.model_validate(politica),
        mensagem="Política de retenção atualizada com sucesso",
    )
