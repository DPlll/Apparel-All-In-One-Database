from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from api.deps import get_db
from pipeline.database import get_products, get_product_by_id

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products(
    brand: Optional[str] = None,
    style: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = True,
    sort: str = Query("newest", enum=["newest", "price_asc", "price_desc"]),
    page: int = Query(1, ge=1),
    db = Depends(get_db),
):
    limit = 24
    offset = (page - 1) * limit
    items = get_products(
        db,
        brand=brand,
        style=style,
        color=color,
        size=size,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    return {"items": items, "page": page, "per_page": limit}


@router.get("/{product_id}")
async def get_product(product_id: str, db=Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
