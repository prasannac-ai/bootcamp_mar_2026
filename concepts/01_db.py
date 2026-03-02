from fastapi import Depends, FastAPI, HTTPException, status, APIRouter
from datetime import datetime
from pydantic import BaseModel
from typing import List
import uuid
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1",tags=["v1"])

Base = declarative_base()

class User(Base):
    __tablename__ = "users1"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name= Column(String(100), nullable=False)
    last_name= Column(String(100), nullable=False)
    email= Column(String(100), nullable=False)
    password= Column(String(100), nullable=False)
    phone= Column(String(100), nullable=False)
   
engine = create_engine("postgresql://agentchiguru:agentchiguru123@localhost:5532/agentchiguru_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class UserCreate(BaseModel):

    first_name: str
    last_name: str
    email: str
    password: str
    phone: str
    
    class Config:
        from_attributes = True
        
class UserResponse(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    password: str
    phone: str
    
    class Config:
        from_attributes = True

@app_v1.post("/users",status_code=status.HTTP_201_CREATED,response_model=UserCreate)
def create_user(user: UserCreate,db: Session = Depends(get_db)):
    user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
        phone=user.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    usercreated = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
        phone=user.phone,
    )
    return usercreated

@app_v1.post("/users_1",status_code=status.HTTP_201_CREATED,response_model=UserResponse)
def create_user(user: UserCreate,db: Session = Depends(get_db)):
    user = User(**user.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



app.include_router(app_v1)