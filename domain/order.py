from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OrderItem:
    product_id: str
    product_name: str
    unit_price: float
    quantity: int
    subtotal: float                    # unit_price * quantity
    notes: str | None = ""


@dataclass
class Order:
    table_number: int
    customer_name: str
    items: list[OrderItem] = field(default_factory=list)
    total_amount: float = 0.0
    status: str = "pending"            # pending, preparing, delivered, cancelled
    created_at: datetime | None = None
    order_id: str | None = None
