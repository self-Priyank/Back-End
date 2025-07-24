from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json       # use to read, edit & parse JSON file

# Parsing: converts JSON raw data into structured data based on its format. occurs in json.load() 
# most cases, reading & parsing are done in single call, reading occurs first (internally) & then parsing
try:
    with open("users.json", "r") as f:
        data = json.load(f)   # type = list of dict.
except FileNotFoundError:
    print("Error: 'user.json' file was not found")
    data = []
except json.JSONDecodeError:
    print("Error: 'user.json' file is wrongly formatted")    # Invalid JSON
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

@app.get("/users", response_model=list[Person])
def get_all_users():
    return data

@app.get("/login", response_model=list[Person])
def login_users():
    user_email = input("enter your email: ")
    user_pw = input("enter your password: ")
    pk = data.keys()
    for i in pk:
        if user_email == pk[i]:
            if user_pw == pk[i+1]:
                print(f"Login with the account {user_email} is successful")
                return
    print("Email Id doesn't exist")
    return     