from dataclasses import dataclass


@dataclass
class Product:
    name: str
    description: str
    price: float
    category_id: str
    available: bool = True
    product_id: str | None = None
