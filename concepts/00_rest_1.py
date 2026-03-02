from sys import api_version
from fastapi import FastAPI, HTTPException, status, APIRouter


# uvicorn 00_rest:app --reload --port 9001

app = FastAPI()

products = []

api_v1 = APIRouter(prefix="/api/v1", tags=["v1"])


@api_v1.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: dict):
    products.append(product)
    return {"message": "Product created successfully"}

@api_v1.get("/products", status_code=status.HTTP_200_OK)
def get_products():
    return products



app.include_router(api_v1)