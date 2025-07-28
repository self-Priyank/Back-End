from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json       # read, edit & parse JSON file

# Parsing: convert JSON raw data into structured data by breaking into small parts & process them based on format. occurs in json.load() 
# most cases, reading & parsing are done in single call, reading occurs first (internally) & then parsing
try:
    with open("API_data.json", "r") as f:
        data = json.load(f)   # type = list of dict.
except FileNotFoundError:
    print("Error: 'API_data.json' file was not found")
    data = []
except json.JSONDecodeError:
    print("Error: 'API_data' file is wrongly formatted")    # Invalid JSON
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

@app.post("/sign_up")   
def sign_up_user(user: Person):
    for d in data:
        if user.email == d["email"]:
            raise HTTPException(status_code=409, detail="user already exist")
    data.append({
        "email": user.email,
        "password": user.password})
    with open("API_data.json", "w") as f:
        json.dump(data, f, indent=4)                # write data into file in JSO
    return {"message": "New user created"}
            

# Some additional updating I'm considering:
#   1. password hashing
#   2. security & token authentication