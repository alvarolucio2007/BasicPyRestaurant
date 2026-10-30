from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection

from domain.order import Order, OrderItem


class OrderRepository:
    def __init__(self, collection: Collection) -> None:
        self.collection = collection

    @staticmethod
    def _item_to_document(item: OrderItem) -> dict:
        return {
            "product_id": item.product_id,
            "product_name": item.product_name,
            "unit_price": item.unit_price,
            "quantity": item.quantity,
            "subtotal": item.subtotal,
            "notes": item.notes,
        }

    @staticmethod
    def _document_to_item(doc: dict) -> OrderItem:
        return OrderItem(
            product_id=doc["product_id"],
            product_name=doc["product_name"],
            unit_price=doc["unit_price"],
            quantity=doc["quantity"],
            subtotal=doc["subtotal"],
            notes=doc.get("notes", ""),
        )

    @classmethod
    def _to_document(cls, order: Order) -> dict:
        return {
            "table_number": order.table_number,
            "customer_name": order.customer_name,
            "status": order.status,
            "total_amount": order.total_amount,
            "created_at": order.created_at or datetime.utcnow(),
            "items": [cls._item_to_document(i) for i in order.items],
        }

    @classmethod
    def _to_entity(cls, doc: dict) -> Order:
        return Order(
            order_id=str(doc["_id"]),
            table_number=doc["table_number"],
            customer_name=doc["customer_name"],
            items=[cls._document_to_item(i) for i in doc["items"]],
            total_amount=doc["total_amount"],
            status=doc["status"],
            created_at=doc["created_at"],
        )

    @staticmethod
    def _oid(order_id: str | None) -> ObjectId | None:
        try:
            return ObjectId(order_id)
        except (InvalidId, TypeError):
            return None

    def add(self, order: Order) -> Order:
        doc = self._to_document(order)
        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._to_entity(doc)

    def fetch_by_id(self, id: str) -> Order | None:
        oid = self._oid(id)
        if oid is None:
            return None
        doc = self.collection.find_one({"_id": oid})
        return self._to_entity(doc) if doc else None

    def list_all(self) -> list[Order]:
        cursor = self.collection.find().sort("created_at", -1)
        return [self._to_entity(d) for d in cursor]

    def list_by_status(self, status: str) -> list[Order]:
        cursor = self.collection.find({"status": status}).sort("created_at", 1)
        return [self._to_entity(d) for d in cursor]

    def update(self, order: Order) -> bool:
        oid = self._oid(order.order_id)
        if oid is None:
            return False
        update_operation = {"$set": {
            "table_number": order.table_number,
            "customer_name": order.customer_name,
            "items": [self._item_to_document(i) for i in order.items],
            "total_amount": order.total_amount,
            "status": order.status,
        }}
        result = self.collection.update_one({"_id": oid}, update_operation)
        return result.matched_count > 0

    def delete(self, id: str) -> bool:
        oid = self._oid(id)
        if oid is None:
            return False
        result = self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0
