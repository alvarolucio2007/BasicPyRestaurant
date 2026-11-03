import os

from bson import ObjectId
from pymongo import MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://admin:admin123@localhost:27017/BasicPyRestaurant?authSource=admin")
db = MongoClient(MONGO_URL)["BasicPyRestaurant"]

db.category.delete_many({})
db.products.delete_many({})
db.orders.delete_many({})

pizzas_id = ObjectId()
drinks_id = ObjectId()
desserts_id = ObjectId()

db.category.insert_many([
    {"_id": pizzas_id, "name": "Pizzas", "display_order": 1},
    {"_id": drinks_id, "name": "Bebidas", "display_order": 2},
    {"_id": desserts_id, "name": "Sobremesas", "display_order": 3},
])

db.products.insert_many([
    {"name": "Margherita", "description": "Molho, mussarela, manjericão", "price": 39.90, "category_id": str(pizzas_id), "available": True},
    {"name": "Calabresa", "description": "Molho, mussarela, calabresa", "price": 44.90, "category_id": str(pizzas_id), "available": True},
    {"name": "Quatro Queijos", "description": "Mussarela, gorgonzola, parmesão, catupiry", "price": 49.90, "category_id": str(pizzas_id), "available": True},
    {"name": "Coca-Cola 2L", "description": "Refrigerante", "price": 12.00, "category_id": str(drinks_id), "available": True},
    {"name": "Suco de Laranja", "description": "500ml natural", "price": 10.00, "category_id": str(drinks_id), "available": True},
    {"name": "Petit Gateau", "description": "Com sorvete de creme", "price": 25.00, "category_id": str(desserts_id), "available": True},
])

print(f"✅ {db.categories.count_documents({})} categorias, {db.products.count_documents({})} produtos")
