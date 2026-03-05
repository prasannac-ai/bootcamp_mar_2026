"""

Run:
    uvicorn concepts.01_crud_with_db:app --reload --port 9001

Test:
    http://localhost:9001/docs
"""

from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


# 1. DATABASE SETUP


DATABASE_URL = "postgresql://agriadmin:agriadmin123@localhost:5632/agri_db"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True logs SQL queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



# 2. MODEL (Database Table)


class Product(Base):
    """SQLAlchemy model — maps to 'products' table in PostgreSQL."""
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)





# 3. SCHEMAS (Request/Response Models)


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    name: str
    category: str
    price: float
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    """Schema for updating a product (all fields optional)."""
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None


class ProductResponse(BaseModel):
    """Schema for product response."""
    id: str
    name: str
    category: str
    price: float
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows ORM model → Pydantic conversion



# 4. DEPENDENCY — Database Session


def get_db():
    """
    Dependency Injection: yields a DB session per request.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# 5. FASTAPI APPLICATION


app = FastAPI(
    title="REST API + Database integration",
    description="Simple CRUD operations demonstrating REST API + Database integration",
    version="1.0.0",
)


# Create tables on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    print(" Database tables created")
    
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup
#     Base.metadata.create_all(bind=engine)
#     print("Database tables created")
#     yield
#     # shutdown
#     print("Any cleanup code here...")


# ─── CREATE ──────────────────────────────
@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    CREATE — POST /products
    Inserts a new product into the database.
    """
    db_product = Product(
        name=product.name,
        category=product.category,
        price=product.price,
        description=product.description,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  # Reload to get auto-generated fields (id, timestamps)

    return ProductResponse(
        id=str(db_product.id),
        name=db_product.name,
        category=db_product.category,
        price=db_product.price,
        description=db_product.description,
        created_at=db_product.created_at,
        updated_at=db_product.updated_at,
    )


# ─── READ ALL ────────────────────────────
@app.get("/products", response_model=List[ProductResponse])
def list_products(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """
    READ — GET /products
    Lists all products with optional pagination and filtering.
    """
    query = db.query(Product)

    skip = (page - 1) * page_size
    products = query.offset(skip).limit(page_size).all()

    return [
        ProductResponse(
            id=str(p.id),
            name=p.name,
            category=p.category,
            price=p.price,
            description=p.description,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in products
    ]


# ─── READ ONE ────────────────────────────
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    READ — GET /products/{id}
    Retrieve a single product by its ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )

    return ProductResponse(
        id=str(product.id),
        name=product.name,
        category=product.category,
        price=product.price,
        description=product.description,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


# ─── UPDATE ──────────────────────────────
@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, update: ProductUpdate, db: Session = Depends(get_db)):
    """
    UPDATE — PUT /products/{id}
    Updates specified fields of an existing product.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )

    # Only update fields that were actually provided
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return ProductResponse(
        id=str(product.id),
        name=product.name,
        category=product.category,
        price=product.price,
        description=product.description,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


# ─── DELETE ──────────────────────────────
@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    """
    DELETE — DELETE /products/{id}
    Permanently removes a product from the database.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found",
        )

    db.delete(product)
    db.commit()
    return None  # 204 No Content


# ─── SEARCH ──────────────────────────────
@app.get("/products/search/", response_model=List[ProductResponse])
def search_products(
    q: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """
    SEARCH — GET /products/search/?q=...
    Search products by name with optional price range filtering.
    """
    query = db.query(Product).filter(Product.name.ilike(f"%{q}%"))

    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    products = query.all()

    return [
        ProductResponse(
            id=str(p.id),
            name=p.name,
            category=p.category,
            price=p.price,
            description=p.description,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in products
    ]


