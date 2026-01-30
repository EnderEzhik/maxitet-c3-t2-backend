from fastapi import APIRouter, HTTPException

from sqlalchemy import text

from src.database import SessionDep


router = APIRouter(prefix="/utils", tags=["Utils"])


@router.get("/check-db")
async def check_db(session: SessionDep):
    try:
        await session.execute(text("SELECT 1"))
        return { "status": "OK" }
    except Exception:
        raise HTTPException(status_code=503, detail="База данных недоступна")
