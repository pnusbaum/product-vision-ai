import streamlit as st
import requests

API_URL = "https://product-api-847285464691.europe-central2.run.app/"

st.set_page_config(page_title="Product Vision AI", layout="wide")

st.title("Product Vision AI")
st.write("Wyszukiwanie podobnych produktów po zdjęciu lub tekście")


mode = st.radio(
    "Wybierz tryb wyszukiwania",
    ["Image search", "Text search"]
)

limit = st.slider("Liczba wyników", 1, 20, 5)


def display_products(products):
    cols = st.columns(3)

    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.image(product["image_url"], use_container_width=True)
            st.subheader(product["name"])
            st.write(f"Kategoria: {product['category']}")
            st.write(f"Distance: {round(product['distance'], 4)}")


if mode == "Image search":
    uploaded_file = st.file_uploader(
        "Prześlij zdjęcie produktu",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file and st.button("Szukaj po obrazie"):
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        response = requests.post(
            f"{API_URL}/search-by-image?limit={limit}",
            files=files
        )

        if response.ok:
            products = response.json()
            display_products(products)
        else:
            st.error("Błąd API")


if mode == "Text search":
    query = st.text_input("Wpisz opis produktu")

    if query and st.button("Szukaj po tekście"):
        response = requests.post(
            f"{API_URL}/search-by-text?limit={limit}",
            json={"query": query}
        )

        if response.ok:
            products = response.json()
            display_products(products)
        else:
            st.error("Błąd API")