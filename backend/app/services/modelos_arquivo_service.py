"""Service auxiliar para consulta de modelos de arquivo."""
from sqlalchemy.orm import Session

from app.models.modelo_arquivo import ModeloArquivo


def buscar_por_codigo(codigo: str, db: Session) -> ModeloArquivo | None:
    return db.query(ModeloArquivo).filter(
        ModeloArquivo.codigo == codigo,
        ModeloArquivo.ativo == True,  # noqa: E712
    ).first()


def listar_globais(db: Session) -> list[ModeloArquivo]:
    return (
        db.query(ModeloArquivo)
        .filter(
            ModeloArquivo.empresa_id == None,  # noqa: E711
            ModeloArquivo.ativo == True,  # noqa: E712
        )
        .order_by(ModeloArquivo.nome)
        .all()
    )
