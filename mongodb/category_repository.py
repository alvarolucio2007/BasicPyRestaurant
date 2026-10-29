from bson import ObjectId
from pymongo.collection import Collection

from domain.category import Category


class CategoryRepository:
    def __init__(self,collection:Collection) -> None:
        self.collection=collection
    def add(self,name:str,display_order:int)->Category:
        result=self.collection.insert_one({
            "name":name,
            "display_order":display_order
        })
        return Category(name=name,display_order=display_order,category_id=str(result.inserted_id))
    def fetch_by_id(self,id:str)->Category|None:
        result=self.collection.find_one({"_id":ObjectId(id)})
        if result is None:
            return None
        return Category(
            category_id=str(result["_id"]),
            name=result["name"],
            display_order=result["display_order"]
        )
    def update(self,category:Category)->bool:
        query_filter={"_id":category.category_id}
        update_operation={"$set":
            { "name":category.name,
            "display_order":category.display_order,}
        }
        result=self.collection.update_one(query_filter,update_operation)
        return result.modified_count!=0
    def delete(self,id:str)->bool:
        result= self.collection.delete_one({"_id":ObjectId(id)})
        return result.acknowledged
