from pymongo import MongoClient
from config import Config

class MongoDB:
    _client = None

    @staticmethod
    def get_client():
        if MongoDB._client is None:
            MongoDB._client = MongoClient(Config.MONGO_URI)
        return MongoDB._client

try:
    db = MongoDB.get_client().get_default_database()
except Exception:
    db = None

# If the URI doesn't include a default DB name, select by Config.MONGO_DB_NAME
if db is None:
    if not Config.MONGO_DB_NAME:
        raise RuntimeError(
            "MongoDB database not found. Add a database name in MONGO_URI (e.g. mongodb://.../jobportal) "
            "or set MONGO_DB_NAME in .env."
        )
    db = MongoDB.get_client()[Config.MONGO_DB_NAME]
