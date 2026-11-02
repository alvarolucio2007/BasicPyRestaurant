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
    def top_selling_products(self, limit: int = 5) -> list[dict]:
        pipeline = [
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.product_id",
                "product_name": {"$first": "$items.product_name"},
                "total_quantity": {"$sum": "$items.quantity"},
                "total_revenue": {"$sum": "$items.subtotal"},
            }},
            {"$sort": {"total_quantity": -1}},
            {"$limit": limit},
            {"$project": {
                "_id": 0,
                "product_name": 1,
                "total_quantity": 1,
                "total_revenue": 1,
            }},
        ]
        return list(self.collection.aggregate(pipeline))
    def revenue_by_category(self) -> list[dict]:
        pipeline = [
            {"$unwind": "$items"},
            {"$group": {
                "_id": "$items.product_id",
                "total_revenue": {"$sum": "$items.subtotal"},
            }},
            {"$lookup": {
                "from": "products",
                "let": {"pid": {"$toObjectId": "$_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$pid"]}}},
                    {"$project": {"category_id": 1}},
                ],
                "as": "product",
            }},
            {"$unwind": "$product"},
            {"$group": {
                "_id": "$product.category_id",
                "total_revenue": {"$sum": "$total_revenue"},
            }},
            {"$lookup": {
                "from": "categories",
                "let": {"cid": {"$toObjectId": "$_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$_id", "$$cid"]}}},
                    {"$project": {"name": 1}},
                ],
                "as": "category",
            }},
            {"$unwind": "$category"},
            {"$sort": {"total_revenue": -1}},
            {"$project": {
                "_id": 0,
                "category_name": "$category.name",
                "total_revenue": 1,
            }},
        ]
        return list(self.collection.aggregate(pipeline))
    def order_summary_by_status(self) -> list[dict]:
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1},
                "total_revenue": {"$sum": "$total_amount"},
                "avg_ticket": {"$avg": "$total_amount"},
            }},
            {"$sort": {"count": -1}},
            {"$project": {
                "_id": 0,
                "status": "$_id",
                "count": 1,
                "total_revenue": {"$round": ["$total_revenue", 2]},
                "avg_ticket": {"$round": ["$avg_ticket", 2]},
            }},
        ]
        return list(self.collection.aggregate(pipeline))
