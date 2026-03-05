from fastapi import FastAPI , APIRouter, status, HTTPException
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
from fastapi import Depends
from pydantic import BaseModel


app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1",tags=["v1"])

users = ["user1", "user2", "user4"]

engine = create_engine("postgresql://agriadmin:agriadmin123@localhost:5632/agri_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@app.on_event("startup")
def startup_db_client():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    
  
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    
class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    password: str
    
    class Config:
        from_attributes = True

@app_v1.get("/users/{id}",status_code=status.HTTP_200_OK)
def getuserbyid(id: int):
    user = User(id=id, name="John Doe", email="john.doe@example.com", password="password")
    return user

@app_v1.get("/users",status_code=status.HTTP_200_OK)
def get_users():
    return {"users": users }

@app_v1.post("/users",status_code=status.HTTP_200_OK,response_model=UserResponse)
def create_user(user: UserCreate,db: Session = Depends(get_db)):
    user = User(name=user.name, email=user.email, password=user.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


app.include_router(app_v1)