from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError, PyMongoError
from typing import Optional, List
import time

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
except ServerSelectionTimeoutError:
    print("database error occured. Please, try again later!")
    raise

class TASK(BaseModel):
    id: str
    task_title: str
    username: str
    task_description: str
    task_order: int = Field(gt=0, description="order value must be greater than 0")
    task_status: str = "pending"
    start_time: float
    deadline: Optional[float] = None
    completion_time: Optional[float] = None
    is_pinned: bool = False

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

def process_data(d):
    d["id"] = str(d["_id"])
    del d["_id"]
    return d

app = FastAPI()

@app.get("/")    
def read_URL():
    return "!! Bienvenue !!"

@app.get("/tasks", response_model=List[TASK])
def get_all_user_tasks():
    try:
        docs = list(task_coll.find().sort("task_order", 1))
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database error")
    
    tasks = []
    for d in docs:
        tasks.append(process_data(d))
    return tasks

@app.get("/tasks/by_user/{usr_nm}", response_model=List[TASK])
def get_tasks_by_username(usr_nm: str):
    try:
        docs = list(task_coll.find({"username": usr_nm}).sort("task_order", 1))
        if not docs:
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database error")
    
    tasks = []
    for d in docs:
        tasks.append(process_data(d))
    return tasks

@app.get("/tasks/by_user_status/{usr_nm}/{status}", response_model=List[TASK])
def get_tasks_by_username_and_status(usr_nm: str, status: str):
    if is_invalid_status(status):
        raise HTTPException(status_code=400, detail="invalid status")
    
    try:
        if not task_coll.find_one({"username": usr_nm}):
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
        docs = list(task_coll.find({"username": usr_nm, "task_status": status}).sort("task_order", 1))
        if not docs:
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm} and status = {status}")
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database server error")
    
    tasks = []
    for d in docs:
        tasks.append(process_data(d))
    return tasks

@app.post("/create_task")
def create_task(t: TASK_CREATE): 
    tk = TASK(id = "temp",
              task_title = t.task_title, 
              username = t.username, 
              task_description = t.task_description,
              task_order = t.task_order, 
              start_time = time.time()).model_dump(exclude={"id"})
    
    try:
        insert_tk = task_coll.insert_one(tk)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="failed to create task because order value isn't unique")
    except PyMongoError:
        raise HTTPException(status_code=500, detail="database server error")
    return {"message": f"new task is created with ID {str(insert_tk.inserted_id)}"}

@app.put("/pinning_task/{usr_nm}")
def pinning_task(usr_nm: str):
    try:
        docs = task_coll.find_one({"username": usr_nm})
        if not docs: 
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
        p_docs = process_data(docs)
        task_coll.update_one({"username": usr_nm}, {"$set": {"is_pinned": True}})   
        return {"message": f"Task ID {str(p_docs['id'])} is pinned"} 
    except PyMongoError:
        raise HTTPException(status_code=500, detail="database server error")