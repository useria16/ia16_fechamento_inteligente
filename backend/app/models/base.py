from app.core.config import settings
from app.core.database import Base

# Todos os models importados aqui para que o Alembic detecte via autogenerate
# Exemplo: from app.models.empresa import Empresa

SCHEMA = settings.DB_SCHEMA

__all__ = ["Base", "SCHEMA"]
