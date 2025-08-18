from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError

def get_task_coll():
    try: 
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        client.server_info()
        db = client["mydb"]
        task_coll = db["Tasks"]
        try:
            task_coll.create_index([("task_order", 1)], unique=True)
        except DuplicateKeyError:
            print("order value must be unique")
            raise
        return task_coll
    except ServerSelectionTimeoutError:
        print("database is down. Please, try again later!")
        raise