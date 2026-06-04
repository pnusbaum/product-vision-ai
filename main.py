from fastapi import FastAPI
from database import test_connection
from pydantic import BaseModel
from sqlalchemy import text
from database import engine
import os
import shutil
from fastapi import UploadFile, File

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
    
@app.get("/products")
def get_products():
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    id,
                    name,
                    description,
                    category,
                    created_at
                FROM products
                ORDER BY id
            """)
        )

        return [dict(row) for row in result.mappings()]
            
@app.post("/products/{product_id}/image")
def upload_product_image(product_id: int, file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)

    extension = file.filename.split(".")[-1]
    file_path = f"uploads/{product_id}.{extension}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE products
                SET image_path = :image_path
                WHERE id = :product_id
                RETURNING id, name, image_path
            """),
            {
                "image_path": file_path,
                "product_id": product_id
            }
        )

        row = result.mappings().first()

        if row is None:
            return {"error": "Product not found"}

        return dict(row)