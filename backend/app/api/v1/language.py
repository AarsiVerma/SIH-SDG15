"""Language catalog API endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.language import load_catalog

router = APIRouter(prefix="/language", tags=["language"])


@router.get("")
async def get_language_catalog(db: AsyncSession = Depends(get_db)):
    """Return full language catalog for frontend copy."""
    return load_catalog()