from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_db
from pipeline.database import get_product_by_id, log_click

router = APIRouter(prefix="/click", tags=["clicks"])


@router.post("/{product_id}")
def record_click(product_id: str, db=Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    log_click(db, product_id)
    return {"affiliate_url": product["affiliate_url"]}
