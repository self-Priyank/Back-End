from fastapi import HTTPException
import my_db

db = my_db.get_task_coll()

total_status = ["complete", "delaycomplete", "pending", "overdue", "archived"]
def is_invalid_status(sv):
    if sv not in total_status:
        return True
    return False

def process_data(d):
    d["id"] = str(d["_id"])
    del d["_id"]
    return d

def is_exist(usr_nm: str, task_title: str):
    d = db.find_one({"task_title": task_title, "username": usr_nm})
    if not d:
        if not db.find_one({"username": usr_nm}): 
            raise HTTPException(status_code=404, detail=f"No task found with username {usr_nm}")
        raise HTTPException(status_code=404, detail=f"Task title {task_title} not found for username {usr_nm}")
    
    process_form = process_data(d)
    return process_form