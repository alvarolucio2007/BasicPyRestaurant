from datetime import datetime

from bson import ObjectId
from pymongo.collection import Collection

from domain.order import Order,OrderItem


class OrderRepository:
    def __init__(self, collection: Collection) -> None:
        self.collection = collection
    def add(self, order: Order) -> Order:
        order_dict = {
            "table_number": order.table_number,
            "customer_name": order.customer_name,
            "status": order.status,
            "total_amount": order.total_amount,
            "created_at": order.created_at or datetime.utcnow(),
            "items": [
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "unit_price": item.unit_price,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal,
                    "notes": item.notes
                }
                for item in order.items
            ]
        }
        result = self.collection.insert_one(order_dict)
        order.order_id = str(result.inserted_id)
        return order
    def fetch_by_id(self,id:str)->Order|None:
        result=self.collection.find_one({"_id":ObjectId(id)})
        if result is None:
            return None
        items_list = [
            OrderItem(
                product_id=item["product_id"],
                product_name=item["product_name"],
                unit_price=item["unit_price"],
                quantity=item["quantity"],
                subtotal=item["subtotal"],
                notes=item.get("notes", "")
            )
            for item in result["items"]
        ]
        return Order(
            table_number=result["table_number"],
            customer_name=result["customer_name"],
            items=items_list,
            total_amount=result["total_amount"],
            status=result["status"],
            created_at=result["created_at"],
            order_id=str(result["_id"])
        )
    def update(self,order:Order)->bool:
        query_filter={"_id":ObjectId(order.order_id)}
        items_dicts = [
                    {
                        "product_id": item.product_id,
                        "product_name": item.product_name,
                        "unit_price": item.unit_price,
                        "quantity": item.quantity,
                        "subtotal": item.subtotal,
                        "notes": item.notes
                    }
                    for item in order.items
                ]
        update_operation={"$set":
            {
            "table_number":order.table_number,
            "customer_name":order.customer_name,
            "items":items_dicts,
            "total_amount":order.total_amount,
            "status":order.status,
            }
        }
        result=self.collection.update_one(query_filter,update_operation)
        return result.modified_count!=0
    def delete(self,id:str)->bool:
        result= self.collection.delete_one({"_id":ObjectId(id)})
        return result.deleted_count>0
