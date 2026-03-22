from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone


@dataclass
class Product:
    id: str
    brand: str
    brand_slug: str
    name: str
    price: float
    image_url: str
    affiliate_url: str
    style: str          # top / bottom / set / one-piece
    colors: list
    sizes: list
    in_stock: bool
    sale_price: Optional[float] = None
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        d = asdict(self)
        d["colors"] = self.colors
        d["sizes"] = self.sizes
        return d
