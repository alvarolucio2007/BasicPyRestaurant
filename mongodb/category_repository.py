from bson import ObjectId
from bson.errors import InvalidId
from pymongo.collection import Collection

from domain.category import Category


class CategoryRepository:
    def __init__(self,collection:Collection) -> None:
        self.collection=collection
    @staticmethod
    def _to_entity(doc: dict) -> Category:
        return Category(
            category_id=str(doc["_id"]),
            name=doc["name"],
            display_order=doc["display_order"],
        )
    @staticmethod
    def _to_document(category: Category) -> dict:
        return {
            "name": category.name,
            "display_order": category.display_order,
        }
    @staticmethod
    def _oid(category_id: str) -> ObjectId | None:
        try:
            return ObjectId(category_id)
        except (InvalidId, TypeError):
            return None
    def add(self, *, category: Category) -> Category:
        doc = self._to_document(category)
        result = self.collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return self._to_entity(doc)
    def fetch_by_id(self,id:str)->Category|None:
        result=self.collection.find_one({"_id":ObjectId(id)})
        if result is None:
            return None
        return Category(
            category_id=str(result["_id"]),
            name=result["name"],
            display_order=result["display_order"]
        )
    def list_all(self) -> list[Category]:
        return [self._to_entity(d) for d in self.collection.find().sort("display_order", 1)]
    def update(self, *, category: Category) -> bool:
        result = self.collection.update_one(
            {"_id": ObjectId(category.category_id)},
            {"$set": self._to_document(category)},
        )
        return result.matched_count > 0
    def delete(self, *, id: str) -> bool:
            oid = self._oid(id)
            if oid is None:
                return False
            result = self.collection.delete_one({"_id": oid})
            return result.deleted_count > 0
