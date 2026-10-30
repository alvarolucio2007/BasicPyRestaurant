from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection

from domain.product import Product


class ProductRepository:
    def __init__(self, collection: Collection) -> None:
        self.collection = collection

    @staticmethod
    def _to_document(product: Product) -> dict:
        return {
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "category_id": product.category_id,
            "available": product.available,
        }

    @staticmethod
    def _to_entity(doc: dict) -> Product:
        return Product(
            product_id=str(doc["_id"]),
            name=doc["name"],
            description=doc["description"],
            price=doc["price"],
            category_id=doc["category_id"],
            available=doc.get("available", True),
        )

    @staticmethod
    def _oid(product_id: str | None) -> ObjectId | None:
        try:
            return ObjectId(product_id)
        except (InvalidId, TypeError):
            return None

    def add(self, product: Product) -> Product:
        doc = self._to_document(product)
        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._to_entity(doc)

    def fetch_by_id(self, id: str) -> Product | None:
        oid = self._oid(id)
        if oid is None:
            return None
        doc = self.collection.find_one({"_id": oid})
        return self._to_entity(doc) if doc else None

    def list_all(self) -> list[Product]:
        cursor = self.collection.find().sort("name", 1)
        return [self._to_entity(d) for d in cursor]

    def list_by_category(self, category_id: str) -> list[Product]:
        cursor = self.collection.find({"category_id": category_id}).sort("name", 1)
        return [self._to_entity(d) for d in cursor]

    def list_available(self) -> list[Product]:
        cursor = self.collection.find({"available": True}).sort("name", 1)
        return [self._to_entity(d) for d in cursor]

    def update(self, product: Product) -> bool:
        oid = self._oid(product.product_id)
        if oid is None:
            return False
        result = self.collection.update_one(
            {"_id": oid},
            {"$set": self._to_document(product)},
        )
        return result.matched_count > 0

    def delete(self, id: str) -> bool:
        oid = self._oid(id)
        if oid is None:
            return False
        result = self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0
