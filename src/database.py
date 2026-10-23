from pymongo import MongoClient

from src import config

_client = None


def get_db(db_name=None):
    """Trả về database MongoDB; cả ứng dụng dùng chung một kết nối."""
    global _client
    if _client is None:
        _client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=3000)
    return _client[db_name or config.MONGODB_DB]
