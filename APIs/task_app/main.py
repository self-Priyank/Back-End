from fastapi import FastAPI, HTTPException
from schemas import TASK, TASK_CREATE
from db import get_task_coll
from pymongo.errors import DuplicateKeyError, PyMongoError
from others import is_invalid_status, process_data
from typing import List
import time

db = get_task_coll()
app = FastAPI()

@app.get("/")    
def read_URL():
    return {"message": "!! Bienvenue !!"}

@app.get("/tasks", response_model=List[TASK])
def get_all_user_tasks():
    try:
        docs = list(db.find().sort("task_order", 1))
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database error")
    
    tasks = []
    for d in docs:
        tasks.append(process_data(d))
    return tasks

@app.get("/tasks/{usr_nm}", response_model=List[TASK])
def get_tasks_by_username(usr_nm: str):
    try:
        docs = list(db.find({"username": usr_nm}).sort("task_order", 1))
        if not docs:
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database error")
    
    tasks = []
    for d in docs:
        tasks.append(process_data(d))
    return tasks

@app.get("/tasks/{usr_nm}/{status}", response_model=List[TASK])
def get_tasks_by_username_and_status(usr_nm: str, status: str):
    if is_invalid_status(status):
        raise HTTPException(status_code=400, detail="invalid status")
    
    try:
        if not db.find_one({"username": usr_nm}):
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
        docs = list(db.find({"username": usr_nm, "task_status": status}).sort("task_order", 1))
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
        insert_tk = db.insert_one(tk)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="failed to create task because order value isn't unique")
    except PyMongoError:
        raise HTTPException(status_code=500, detail="database server error")
    return {"message": f"new task is created with ID {str(insert_tk.inserted_id)}"}

@app.put("/pinning_task/{usr_nm}/{task_title}")
def pinning_task(usr_nm: str, task_title: str):
    try:
        if not db.find_one({"username": usr_nm}): 
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
        docs = db.find_one({"task_title": task_title, "username": usr_nm})
        if not docs:
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm} and task title {task_title}")
        p_docs = process_data(docs)
        db.update_one({"task_title": task_title, "username": usr_nm}, {"$set": {"is_pinned": True}})   
        return {"message": f"Task ID {p_docs['id']} is now pinned"}
    except PyMongoError:
        raise HTTPException(status_code=500, detail="database server error")

@app.put("/unpinning_task/{usr_nm}/{task_title}")
def unpinning_task(usr_nm: str, task_title: str):
    try:
        if not db.find_one({"username": usr_nm}): 
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
        docs = db.find_one({"task_title": task_title, "username": usr_nm})
        if not docs:
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm} and task title {task_title}")
        p_docs = process_data(docs)
        db.update_one({"task_title": task_title, "username": usr_nm}, {"$set": {"is_pinned": False}})   
        return {"message": f"Task ID {p_docs['id']} is now unpinned"} 
    except PyMongoError:
        raise HTTPException(status_code=500, detail="database server error")