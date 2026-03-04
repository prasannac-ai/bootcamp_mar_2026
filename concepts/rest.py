from fastapi import FastAPI , APIRouter, status, HTTPException


app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1",tags=["v1"])

users = ["user1", "user2", "user4"]

class User():
    def __init__(self, id: int, name: str, email: str, password: str):
        self.id = id
        self.name = name
        self.email = email
        self.password = password


@app_v1.get("/users/{id}",status_code=status.HTTP_200_OK)
def getuserbyid(id: int):
    user = User(id=id, name="John Doe", email="john.doe@example.com", password="password")
    return user

@app_v1.get("/users",status_code=status.HTTP_200_OK)
def get_users():
    return {"users": users }

@app_v1.post("/users",status_code=status.HTTP_200_OK)
def create_user(user: str):
    users.append(user)
    return {"message": "User created successfully" , "user": user}


app.include_router(app_v1)