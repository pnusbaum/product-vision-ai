import base64
import os
from dotenv import load_dotenv
from openai import OpenAI

from schemas import ProductDescriptionOutput
from prompts import SYSTEM_PROMPT

load_dotenv()


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")

    return OpenAI(api_key=api_key)


def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def generate_product_description(
    brand: str,
    product_name: str,
    image_bytes: bytes,
    mime_type: str,
):
    client = get_client()

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    base64_image = encode_image(image_bytes)

    user_prompt = f"""
    Marka produktu: {brand}
    Nazwa produktu: {product_name}
    """

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        },
                    },
                ],
            },
        ],
        response_format=ProductDescriptionOutput,
    )

    return response.choices[0].message.parsed