from bson import ObjectId
from pymongo.collection import Collection

from domain.product import Product


class ProductRepository:
    def __init__(self,collection:Collection) -> None:
        self.collection=collection
    def add(self,product:Product)->Product:
        result=self.collection.insert_one({
            "name":product.name,
            "description":product.description,
            "price":product.price,
            "category_id":product.category_id,
            "available":product.available,
        })
        return Product(name=product.name,description=product.description,price=product.price,category_id=product.category_id,available=product.available,product_id=str(result.inserted_id))
    def fetch_by_id(self,id:str)->Product|None:
        result=self.collection.find_one({"_id":ObjectId(id)})
        if result is None:
            return None
        return Product(
            name=result["name"],
            description=result["description"],
            price=result["price"],
            category_id=result["category_id"],
            available=result.get("available",True),
            product_id=str(result["_id"]),
        )
    def update(self,product:Product)->bool:
        query_filter={"_id":ObjectId(product.product_id)}
        update_operation={"$set":
            { "name":product.name,
            "description":product.description,
            "price":product.price,
            "category_id":product.category_id,
            "available":product.available,
            }
        }
        result=self.collection.update_one(query_filter,update_operation)
        return result.modified_count!=0
    def delete(self,id:str)->bool:
        result= self.collection.delete_one({"_id":ObjectId(id)})
        return result.deleted_count>0
