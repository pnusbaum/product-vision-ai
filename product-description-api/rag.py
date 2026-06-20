import json


def load_taxonomy():
    with open("knowledge_base/product_taxonomy.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_main_categories():
    taxonomy = load_taxonomy()
    return list(taxonomy.keys())


def get_subcategories(category: str):
    taxonomy = load_taxonomy()
    return taxonomy.get(category, [])