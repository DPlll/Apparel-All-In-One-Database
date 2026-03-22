from fastapi import APIRouter, Depends
from api.deps import get_db
from pipeline.database import get_brands

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("")
def list_brands(db=Depends(get_db)):
    return get_brands(db)
