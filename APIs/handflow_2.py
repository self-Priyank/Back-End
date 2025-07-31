from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

client = MongoClient("mongodb://localhost:27017")
db = client["mydb"]
task_coll = db["Tasks"]
try:
    task_coll.create_index("task_order", unique=True)
except DuplicateKeyError:
    print("order value must be unique")
    raise

class TASK(BaseModel):
    id: str
    task_title: str
    username: str
    task_description: str
    task_order: int
    task_status: str
    start_time: float
    deadline: float
    completion_time: float
    is_pinned: bool

app = FastAPI()

@app.get("/")    
def read_URL():
    return "!! Bienvenue !!"

@app.get("/users_tasks", response_model=list[TASK])
def get_all_user_tasks():
    try:
        docs = task_coll.find()
    except: 
        raise HTTPException(status_code=500, detail="database error")
    tasks = []
    for d in docs:
        d["id"] = str(d["_id"])
        del d["_id"]
        tasks.append(d)
    return tasks
    

@app.get("/users_tasks/{usr_nm}", response_model=list[TASK])
def get_single_user_tasks(usr_nm: str):
    try:
        docs = task_coll.find({"username": usr_nm})
    except: 
        raise HTTPException(status_code=500, detail="database error")
    tasks = []
    for d in docs:
        d["id"] = str(d["_id"])
        del d["_id"]
        tasks.append(d)
    return tasks

# application function