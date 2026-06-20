import base64
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from rag import get_main_categories, get_subcategories
from schemas import ProductRoutingOutput
from prompts import ROUTING_SYSTEM_PROMPT
from schemas import ProductAnalysisOutput, ProductDescriptionOutput, CopywritingOutput
from prompts import ANALYSIS_SYSTEM_PROMPT, COPYWRITING_SYSTEM_PROMPT

load_dotenv()


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")

    return OpenAI(api_key=api_key)


def encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")

def route_product(
    client: OpenAI,
    brand: str,
    product_name: str,
    image_bytes: bytes,
    mime_type: str,
) -> ProductRoutingOutput:
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    base64_image = encode_image(image_bytes)

    allowed_categories = get_main_categories()

    user_prompt = f"""
        Marka: {brand}
        Nazwa produktu: {product_name}

        Dozwolone główne kategorie:
        {allowed_categories}

        Wybierz najlepszą kategorię.
    """

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": ROUTING_SYSTEM_PROMPT},
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
        response_format=ProductRoutingOutput,
    )

    return response.choices[0].message.parsed


def analyze_product(
    client: OpenAI,
    brand: str,
    product_name: str,
    image_bytes: bytes,
    mime_type: str,
    allowed_subcategories: list[str],
) -> ProductAnalysisOutput:
    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    base64_image = encode_image(image_bytes)

    user_prompt = f"""
    Marka produktu: {brand}
    Nazwa produktu: {product_name}

    Dozwolone podkategorie:
    {allowed_subcategories}

    Musisz wybrać podkategorię tylko z tej listy.
    Jeśli produkt nie pasuje, zaznacz to w uncertainty_notes.
    """

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
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
        response_format=ProductAnalysisOutput,
    )

    return response.choices[0].message.parsed


def generate_copywriting(
    client: OpenAI,
    brand: str,
    product_name: str,
    analysis: ProductAnalysisOutput,
) -> CopywritingOutput:
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    user_prompt = f"""
    Marka produktu: {brand}
    Nazwa produktu: {product_name}

    Analiza produktu:
    {json.dumps(analysis.model_dump(), ensure_ascii=False, indent=2)}

    Wygeneruj opis marketingowy i dane SEO.
    """

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": COPYWRITING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format=CopywritingOutput,
    )

    return response.choices[0].message.parsed


def generate_product_description(
    brand: str,
    product_name: str,
    image_bytes: bytes,
    mime_type: str,
) -> ProductDescriptionOutput:
    client = get_client()

    routing = route_product(
        client=client,
        brand=brand,
        product_name=product_name,
        image_bytes=image_bytes,
        mime_type=mime_type,
    )


    if not routing.main_category:
        
        allowed_categories = get_main_categories()
        
        return ProductDescriptionOutput(
            is_in_catalog=False,
            catalog_message=(
                "Produkt nie należy do obsługiwanego katalogu. "
                "Obsługiwane kategorie to: " + ", ".join(allowed_categories)
            ),
            category=None,
            tags=[],
            features=None,
            marketing_description=None,
            seo=None,
        )

    allowed_subcategories = get_subcategories(routing.main_category)

    analysis = analyze_product(
        client=client,
        brand=brand,
        product_name=product_name,
        image_bytes=image_bytes,
        mime_type=mime_type,
        allowed_subcategories=allowed_subcategories
    )

    copywriting = generate_copywriting(
        client=client,
        brand=brand,
        product_name=product_name,
        analysis=analysis,
    )

    return ProductDescriptionOutput(
        is_in_catalog=True,
        catalog_message="Produkt należy do obsługiwanego katalogu.",
        category=analysis.category,
        tags=analysis.tags,
        features=analysis.features,
        marketing_description=copywriting.marketing_description,
        seo=copywriting.seo,
    )