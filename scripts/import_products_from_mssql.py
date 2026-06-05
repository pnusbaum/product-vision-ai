import os
import sys
from pathlib import Path

import pymssql
from dotenv import load_dotenv
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from database import engine


load_dotenv()

IMAGE_BASE_URL = os.getenv("IMAGE_BASE_URL", "https://st.mediaport.pl/")


def build_image_url(relative_path: str | None) -> str | None:
    if not relative_path:
        return None

    return IMAGE_BASE_URL.rstrip("/") + "/" + relative_path.lstrip("/")


def import_products(limit: int = 10):
    conn = pymssql.connect(
        server=os.getenv("MSSQL_HOST"),
        port=int(os.getenv("MSSQL_PORT", "1433")),
        user=os.getenv("MSSQL_USER"),
        password=os.getenv("MSSQL_PASSWORD"),
        database=os.getenv("MSSQL_DATABASE"),
    )

    query = f"""
        SELECT TOP {limit}
            pn.Name,
            p.FirstPicture
        FROM WSProduct p
        INNER JOIN WSProductName pn
            ON p.ProductID = pn.ProductID
            AND pn.LanguageID = 1
        WHERE Accepted = 1
          AND NameDescription IS NOT NULL
        ORDER BY p.ProductID DESC
    """

    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    conn.close()

    with engine.begin() as pg:
        for row in rows:
            image_url = build_image_url(row["FirstPicture"])

            pg.execute(
                text("""
                    INSERT INTO products (name, image_path)
                    VALUES (:name, :image_path)
                """),
                {
                    "name": row["Name"],
                    "image_path": image_url,
                }
            )

    print(f"Zaimportowano produktów: {len(rows)}")


if __name__ == "__main__":
    import_products(limit=1000)