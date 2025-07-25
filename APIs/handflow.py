from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json       # read, edit & parse JSON file

# Parsing: converts JSON raw data into structured data based on its format. occurs in json.load() 
# most cases, reading & parsing are done in single call, reading occurs first (internally) & then parsing
try:
    with open("users.json", "r") as f:
        data = json.load(f)   # type = list of dict.
except FileNotFoundError:
    print("Error: 'users.json' file was not found")
    data = []
except json.JSONDecodeError:
    print("Error: 'users.json' file is wrongly formatted")    # Invalid JSON
    data = []
except Exception as e:
    print(f"Unexpected error: {e}")
    data = []
# prog. opens database & loads its content by parsing it into list of dict.

class Person(BaseModel):
    email: str
    password: str

app = FastAPI()

@app.get("/")    
def read_URL():
    return "!! Bienvenue !!"

# Person return single profile
# list[Person] return all user profiles of same type
@app.get("/users", response_model=list[Person])
def get_all_users():
    return data

@app.post("/login")
def login_user(user: Person): 
    for d in data:
        if user.email == d["email"]:                                                # user is person class instance, not a dict
            if user.password == d["password"]:
                return {"message": "Login successful!"}
            else:
                raise HTTPException(status_code=401, detail="Incorrect password")     # calling HTTPException class constructor
    raise HTTPException(status_code=404, detail="user doesn't exist")     

# Some additional updating I'm considering:
#   1. password hashing
#   2. security & token authentication