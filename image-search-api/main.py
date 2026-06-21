from fastapi import FastAPI
from database import test_connection
from pydantic import BaseModel
from sqlalchemy import text
from database import engine
import os
import shutil
from fastapi import UploadFile, File
from services.embeddings import generate_image_embedding
from services.embeddings import generate_text_embedding

app = FastAPI(title="Image Search & Product Description API")

class TextSearchRequest(BaseModel):
    query: str
    
class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None
    
GCS_PUBLIC_BASE_URL = "https://storage.googleapis.com/mineral-seat-498521-p0-product-images"

def build_image_url(relative_path: str | None) -> str | None:
    if not relative_path:
        return None

    normalized = relative_path.replace("\\", "/")

    if normalized.startswith("uploads/"):
        normalized = normalized.replace("uploads/", "product-images/", 1)

    return f"{GCS_PUBLIC_BASE_URL}/{normalized}"

def map_products_with_image_urls(rows):
    products = []

    for row in rows:
        product = dict(row)
        product["image_url"] = build_image_url(product.get("image_path"))
        products.append(product)

    return products

@app.get("/")
def root():
    return {"status": "API Image comparer is working v3"}
    
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
                    created_at,
                    image_path
                FROM products
                ORDER BY id
            """)
        )

        return map_products_with_image_urls(result.mappings())
            
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
    
    
    
@app.post("/products/{product_id}/generate-image-embedding")
def generate_product_image_embedding(product_id: int):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                SELECT image_path
                FROM products
                WHERE id = :product_id
            """),
            {"product_id": product_id}
        )

        row = result.mappings().first()

        if row is None:
            return {"error": "Product not found"}

        if row["image_path"] is None:
            return {"error": "Product has no image"}

        embedding = generate_image_embedding(row["image_path"])

        
        conn.execute(
            text("""
                UPDATE products
                SET image_embedding = :embedding
                WHERE id = :product_id
            """),
            {
                "embedding": embedding,
                "product_id": product_id
            }
        )

        return {
            "product_id": product_id,
            "embedding_size": len(embedding),
            "status": "image embedding generated"
        }
        
@app.get("/products/{product_id}/similar")
def find_similar_products(product_id: int, limit: int = 5):
    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT image_embedding
                FROM products
                WHERE id = :product_id
            """),
            {"product_id": product_id}
        )

        source = result.mappings().first()

        if source is None:
            return {"error": "Product not found"}

        if source["image_embedding"] is None:
            return {"error": "Product has no embedding"}

        result = conn.execute(
            text("""
                SELECT
                    id,
                    name,
                    category,
                    image_path,
                    image_embedding <=> :embedding AS distance
                FROM products
                WHERE id <> :product_id
                AND image_embedding IS NOT NULL
                ORDER BY image_embedding <=> :embedding
                LIMIT :limit
            """),
            {
                "embedding": source["image_embedding"],
                "product_id": product_id,
                "limit": limit
            }
        )

        return map_products_with_image_urls(result.mappings())
    
@app.post("/search-by-image")
def search_by_image(file: UploadFile = File(...), limit: int = 5):
    print(f"Otrzymano zapytanie o podobne produkty dla przesłanego obrazu: {file.filename}")

    os.makedirs("uploads/search", exist_ok=True)

    temp_path = f"uploads/search/{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    query_embedding = generate_image_embedding(temp_path)

    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    id,
                    name,
                    image_path,
                    category,
                    image_embedding <=> CAST(:embedding AS vector) AS distance
                FROM products
                WHERE image_embedding IS NOT NULL
                ORDER BY image_embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """),
            {
                "embedding": embedding_str,
                "limit": limit,
            }
        )

    return map_products_with_image_urls(result.mappings())
    

@app.post("/search-by-text")
def search_by_text(request: TextSearchRequest, limit: int = 5):
    query_embedding = generate_text_embedding(request.query)

    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    id,
                    name,
                    image_path,
                    category,
                    image_embedding <=> CAST(:embedding AS vector) AS distance
                FROM products
                WHERE image_embedding IS NOT NULL
                ORDER BY image_embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
            """),
            {
                "embedding": embedding_str,
                "limit": limit,
            }
        )

        return map_products_with_image_urls(result.mappings())
    