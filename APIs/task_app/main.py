from fastapi import FastAPI
from schemas import TASK, TASK_CREATE
from typing import List
import logic

app = FastAPI()

@app.get("/")
def read_URL():
    return {"message": "!! Bienvenue !!"}

@app.get("/tasks", response_model=List[TASK])
def get_tasks():
    tasks = logic.GT()
    return tasks

@app.get("/tasks/{usr_nm}", response_model=List[TASK])
def get_tasks_by_username(usr_nm: str):
    tasks = logic.GTU(usr_nm)
    return tasks

@app.get("/tasks/{usr_nm}/{status}", response_model=List[TASK])
def get_tasks_by_username_and_status(usr_nm: str, status: str):
    tasks = logic.GTUS(usr_nm, status)
    return tasks

@app.post("/create_task")
def create_task(t: TASK_CREATE): 
    return logic.CT(t)

@app.put("/pinning_task/{usr_nm}/{task_title}")
def pinning_task(usr_nm: str, task_title: str):
    return logic.is_pinned(usr_nm, task_title)

@app.put("/unpinning_task/{usr_nm}/{task_title}")
def unpinning_task(usr_nm: str, task_title: str):
    return logic.is_unpinned(usr_nm, task_title)