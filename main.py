from fastapi import FastAPI
from database import test_connection
from pydantic import BaseModel
from sqlalchemy import text
from database import engine

app = FastAPI()

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    
@app.get("/")
def root():
    return {"status": "API działa"}
    
@app.get("/db-test")
def db_test():
    return {"result": test_connection()}

@app.post("/products")
def create_product(product: ProductCreate):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO products (name, description, category)
                VALUES (:name, :description, :category)
                RETURNING id, name, description, category, created_at
            """),
            {
                "name": product.name,
                "description": product.description,
                "category": product.category,
            }
        )

        row = result.mappings().one()
        return dict(row)