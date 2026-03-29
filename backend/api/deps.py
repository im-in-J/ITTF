"""FastAPI 의존성 주입"""

from backend.database.connection import get_db

# re-export
__all__ = ["get_db"]
