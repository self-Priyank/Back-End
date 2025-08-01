from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError, PyMongoError
from typing import Optional
import time

try: 
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client["mydb"]
    task_coll = db["Tasks"]
    try:
        task_coll.create_index("task_order", unique=True)
    except DuplicateKeyError:
        print("order value must be unique")
        raise
except ServerSelectionTimeoutError:
    print("database error occured. Please, try again later!")
    raise

class TASK(BaseModel):
    id: str
    task_title: str
    username: str
    task_description: str
    task_order: int = Field(gt=0, description="order value must be greater than 0")
    task_status: str
    start_time: float
    deadline: Optional[float] = None
    completion_time: Optional[float] = None
    is_pinned: bool

class TASK_CREATE(BaseModel):
    task_title: str
    username: str
    task_description: str
    task_order: int = Field(gt=0, description="order value must be greater than 0")

total_status = ["complete", "delaycomplete", "pending", "overdue", "archived"]
def is_invalid_status(sv):
    if sv not in total_status:
        return True
    return False

app = FastAPI()

@app.get("/")    
def read_URL():
    return "!! Bienvenue !!"

@app.get("/users_tasks", response_model=list[TASK])
def get_tasks_by_():
    try:
        docs = task_coll.find()
    except PyMongoError: 
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
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database error")
    tasks = []
    for d in docs:
        d["id"] = str(d["_id"])
        del d["_id"]
        tasks.append(d)
    return tasks

@app.get("/users_tasks/{usr_nm}/{status}", response_model=list[TASK])
def get_tasks_from_single_User_n_Status(usr_nm: str, status: str):
    if is_invalid_status(status):
        raise HTTPException(status_code=400, detail="invalid status")
    try:
        docs = task_coll.find({"username": usr_nm, "task_status": status})
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database error")
    tasks = []
    for d in docs:
        d["id"] = str(d["_id"])
        del d["_id"]
        tasks.append(d)
    return tasks

@app.post("/create_task")
def create_tasks(t: TASK_CREATE): 
    tk = {"task_title": t.task_title, 
          "username": t.username, 
          "task_description": t.task_description,
          "task_order": t.task_order,
          "task_status": "pending", 
          "start_time": time.time(),
          "deadline": None,
          "completion_time": None,
          "is_pinned": False}
    
    try:
        insert_tk = task_coll.insert_one(tk)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="failed to create task because order value isn't unique")
    except PyMongoError:
        raise HTTPException(status_code=500, detail="failed to create task due to database error")
    return {"message": f"new task is created with ID {str(insert_tk.inserted_id)}"}

# application function