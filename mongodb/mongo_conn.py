from pymongo import MongoClient
from pymongo.collection import Collection


class MongoConnectionError(Exception): ...
def get_mongo_collection(url: str, database_name: str, collection_name: str) -> Collection:
    client = MongoClient(url)
    try:
        client.admin.command("ping")
    except Exception as e:  # noqa: BLE001
        raise MongoConnectionError(f"Erro ao conectar: {e}")
    return client[database_name][collection_name]
