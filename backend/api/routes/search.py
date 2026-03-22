from fastapi import APIRouter, Depends, Query
from api.deps import get_db
from pipeline.database import search_products

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(q: str = Query(..., min_length=1), db=Depends(get_db)):
    return {"items": search_products(db, q)}
