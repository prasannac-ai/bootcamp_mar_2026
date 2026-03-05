from fastapi import FastAPI , APIRouter, status, HTTPException
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
from fastapi import Depends

from pydantic import BaseModel

engine = create_engine("postgresql://agriadmin:agriadmin123@db_service:5432/agri_db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



    

app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1",tags=["v1"])

users = ["user1", "user2", "user4"]

@app.on_event("startup")
def startup_db_client():
    Base.metadata.create_all(bind=engine)
    


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = (String(100), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    
class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
  
    
@app_v1.post("/users",status_code=status.HTTP_200_OK)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user = User(name=user.name, email=user.email, password=user.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    response= UserResponse(id=user.id, name=user.name, email=user.email)
    return response


@app_v1.get("/users/{id}",status_code=status.HTTP_200_OK)
def getuserbyid(id: uuid.UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id} not found")
    found_user = UserResponse(id=user.id, name=user.name, email=user.email)
    return found_user

@app_v1.get("/users",status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users }




app.include_router(app_v1)