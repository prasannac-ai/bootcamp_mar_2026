from fastapi import FastAPI, HTTPException, status, APIRouter
from datetime import datetime
from pydantic import BaseModel



app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1",tags=["v1"])

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int
    created_at: datetime
    updated_at: datetime

products = [Product(id=1, name="Product 1", description="Product 1 description", price=100, quantity=10, created_at=datetime.now(), updated_at=datetime.now()), Product(id=2, name="Product 2", description="Product 2 description", price=200, quantity=20, created_at=datetime.now(), updated_at=datetime.now())]

@app_v1.get("/products",status_code=status.HTTP_200_OK)
def get_products():
    return {"products": products }

@app_v1.post("/products",status_code=status.HTTP_201_CREATED)
def create_product(product: Product):
    products.append(product)
    return product

@app_v1.delete("/products",status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str):
    return {"message": "Product deleted successfully"}

@app_v1.put("/products",status_code=status.HTTP_200_OK)
def update_product(product_id: str,product: dict):
    return {"message": "Product updated successfully"}

@app_v1.get("/products/{product_id}",status_code=status.HTTP_200_OK)
def get_product(product_id: str):
    return {"message": "Product retrieved successfully"}

app.include_router(app_v1)