from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from dotenv import load_dotenv
from llm_client import generate_product_description

load_dotenv()

app = FastAPI(title="Product Description API")


@app.get("/")
def root():
    return {"status": "API product description is working v1"}


@app.post("/generate-product-description")
async def generate_product_description_endpoint(
    brand: str = Form(...),
    product_name: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    image_bytes = await file.read()

    result = generate_product_description(
        brand=brand,
        product_name=product_name,
        image_bytes=image_bytes,
        mime_type=file.content_type,
    )

    return result