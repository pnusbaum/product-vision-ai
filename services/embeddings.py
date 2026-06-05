from sentence_transformers import SentenceTransformer
from PIL import Image

model = SentenceTransformer("clip-ViT-B-32")

def generate_image_embedding(image_path: str) -> list[float]:
    image = Image.open(image_path).convert("RGB")
    embedding = model.encode(image)
    return embedding.tolist()

def generate_text_embedding(text: str) -> list[float]:
    embedding = model.encode(text)
    return embedding.tolist()