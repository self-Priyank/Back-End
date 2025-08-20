from fastapi import HTTPException
from schemas import TASK, TASK_CREATE
from pymongo.errors import DuplicateKeyError, PyMongoError
import others, my_db, time

db = my_db.get_task_coll()

def GT():
    try:
        docs = list(db.find().sort("task_order", 1))
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database error")
    
    t = []
    for d in docs:
        t.append(others.process_data(d))
    return t

def GTU(usr_nm: str):
    try:
        docs = list(db.find({"username": usr_nm}).sort("task_order", 1))
        if not docs:
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database error")
    
    t = []
    for d in docs:
        t.append(others.process_data(d))
    return t

def GTUS(usr_nm: str, status: str):
    if others.is_invalid_status(status):
        raise HTTPException(status_code=400, detail="invalid status")
    
    try:
        if not db.find_one({"username": usr_nm}):
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
        docs = list(db.find({"username": usr_nm, "task_status": status}).sort("task_order", 1))
        if not docs:
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm} and status = {status}")
    except PyMongoError: 
        raise HTTPException(status_code=500, detail="database server error")
    
    t = []
    for d in docs:
        t.append(others.process_data(d))
    return t

def CT(t: TASK_CREATE):
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

def is_pinned(usr_nm: str, task_title: str): 
    try:
        docs = others.is_exist(usr_nm, task_title)
        db.update_one({"task_title": task_title, "username": usr_nm}, {"$set": {"is_pinned": True}})   
        return {"message": f"Task ID {docs['id']} is now pinned"}
    
    except PyMongoError:
        raise HTTPException(status_code=500, detail="database server error")
    
def is_unpinned(usr_nm: str, task_title: str):
    try:
        docs = others.is_exist(usr_nm, task_title)
        db.update_one({"task_title": task_title, "username": usr_nm}, {"$set": {"is_pinned": False}})   
        return {"message": f"Task ID {docs['id']} is now unpinned"} 
    
    except PyMongoError:
        raise HTTPException(status_code=500, detail="database server error")