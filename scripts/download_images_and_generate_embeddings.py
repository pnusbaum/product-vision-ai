import sys
from pathlib import Path

import requests
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from database import engine
from image-search-api.services.embeddings import generate_image_embedding


UPLOADS_DIR = BASE_DIR / "image-search-api/uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def download_file(url: str, target_path: Path):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    with open(target_path, "wb") as f:
        f.write(response.content)


def process_products(limit: int = 100):
    with engine.begin() as conn:
        products = conn.execute(
            text("""
                SELECT id, image_path
                FROM products
                WHERE image_path LIKE 'http%'
                  AND image_embedding IS NULL
                ORDER BY id
                LIMIT :limit
            """),
            {"limit": limit}
        ).mappings().all()

        for product in products:
            product_id = product["id"]
            image_url = product["image_path"]

            try:
                extension = image_url.split(".")[-1].split("?")[0]
                local_path = UPLOADS_DIR / f"{product_id}.{extension}"

                print(f"Pobieram produkt {product_id}: {image_url}")
                download_file(image_url, local_path)

                relative_path = f"uploads/{local_path.name}"

                print(f"Licze embedding dla produktu {product_id}")
                embedding = generate_image_embedding(str(local_path))

                conn.execute(
                    text("""
                        UPDATE products
                        SET image_path = :image_path,
                            image_embedding = :embedding
                        WHERE id = :product_id
                    """),
                    {
                        "image_path": relative_path,
                        "embedding": embedding,
                        "product_id": product_id,
                    }
                )

                print(f"OK produkt {product_id}")

            except Exception as e:
                print(f"Błąd produktu {product_id}: {e}")


if __name__ == "__main__":
    process_products(limit=1000)