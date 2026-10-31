from domain.order import Order, OrderItem
from mongodb.order_repository import OrderRepository


class OrderNotFound(Exception): ...
class OrderValidationError(Exception): ...


VALID_STATUSES = {"pending", "preparing", "delivered", "cancelled"}


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self.repo = repo

    @staticmethod
    def create_order_item(
        *,
        product_id: str,
        product_name: str,
        unit_price: float,
        quantity: int,
        notes: str | None = "",
    ) -> OrderItem:
        if not product_id or not product_id.strip():
            raise OrderValidationError("Product ID is missing.")
        if not product_name or not product_name.strip():
            raise OrderValidationError("Product name is missing.")
        if unit_price is None or unit_price <= 0:
            raise OrderValidationError("Unit price must be greater than 0.")
        if quantity is None or quantity <= 0:
            raise OrderValidationError("Quantity must be greater than 0.")
        return OrderItem(
            product_id=product_id,
            product_name=product_name.strip(),
            unit_price=unit_price,
            quantity=quantity,
            subtotal=round(quantity * unit_price, 2),
            notes=notes or "",
        )

    def create(
        self,
        *,
        table_number: int,
        customer_name: str,
        items: list[OrderItem],
    ) -> Order:
        if table_number is None or table_number <= 0:
            raise OrderValidationError("Table number must be greater than 0.")
        if not customer_name or not customer_name.strip():
            raise OrderValidationError("Customer name is missing.")
        if not items:
            raise OrderValidationError("Order must have at least one item.")

        total_amount = round(sum(i.subtotal for i in items), 2)

        return self.repo.add(Order(
            table_number=table_number,
            customer_name=customer_name.strip(),
            items=items,
            total_amount=total_amount,
            status="pending",
        ))

    def fetch_by_id(self, *, order_id: str) -> Order:
        if not order_id or not order_id.strip():
            raise OrderValidationError("ID is missing.")
        order = self.repo.fetch_by_id(id=order_id)
        if order is None:
            raise OrderNotFound(order_id)
        return order

    def list_all(self) -> list[Order]:
        return self.repo.list_all()

    def list_by_status(self, *, status: str) -> list[Order]:
        if status not in VALID_STATUSES:
            raise OrderValidationError(f"Invalid status '{status}'.")
        return self.repo.list_by_status(status=status)

    def update_status(self, *, order_id: str, status: str) -> Order:
        if status not in VALID_STATUSES:
            raise OrderValidationError(f"Invalid status '{status}'.")
        order = self.fetch_by_id(order_id=order_id)
        if order.status in ("delivered", "cancelled"):
            raise OrderValidationError(f"Cannot change status of a '{order.status}' order.")
        order.status = status
        ok = self.repo.update(order=order)
        if not ok:
            raise OrderNotFound(order_id)
        return order

    def delete(self, *, order_id: str) -> None:
        if not order_id or not order_id.strip():
            raise OrderValidationError("ID is missing.")
        ok = self.repo.delete(id=order_id)
        if not ok:
            raise OrderNotFound(order_id)
