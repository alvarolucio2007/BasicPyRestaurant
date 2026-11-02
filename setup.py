import streamlit as st
from pymongo import MongoClient

from front.streamlit import Streamlit
from mongodb.category_repository import CategoryRepository
from mongodb.mongo_conn import MongoConnectionError, get_mongo_collection
from mongodb.order_repository import OrderRepository
from mongodb.product_repository import ProductRepository
from service.category_service import CategoryService
from service.order_service import OrderService
from service.product_service import ProductService


def setup(mongo_url:str,database_name:str,app_url:str)->Streamlit:
    checked_db:str="product"
    try:
        product_coll=get_mongo_collection(url=mongo_url,database_name=database_name,collection_name="products")
        product_repo=ProductRepository(collection=product_coll)
        checked_db="category"
        category_coll=get_mongo_collection(url=mongo_url,database_name=database_name,collection_name="category")
        category_repo=CategoryRepository(collection=category_coll)
        checked_db="order"
        order_coll=get_mongo_collection(url=mongo_url,database_name=database_name,collection_name="orders")
        order_repo=OrderRepository(collection=order_coll)
    except MongoConnectionError:
        raise ConnectionError("Could not connect to the database.Last connection tried: ",checked_db)

    product_service=ProductService(repo=product_repo)
    category_service=CategoryService(repo=category_repo)
    order_service=OrderService(repo=order_repo)

    streamlit=Streamlit(category_service=category_service,product_service=product_service,order_service=order_service)
    return streamlit

@st.cache_resource
def get_container(url:str) -> dict:
    client = MongoClient(url)
    db = client["restaurant"]

    db.categories.create_index("name", unique=True)
    db.categories.create_index("display_order")
    db.products.create_index([("category_id", 1), ("name", 1)])
    db.products.create_index("available")
    db.orders.create_index([("status", 1), ("created_at", 1)])

    return {
        "category_service": CategoryService(CategoryRepository(db["categories"])),
        "product_service": ProductService(ProductRepository(db["products"])),
        "order_service": OrderService(OrderRepository(db["orders"])),
    }
