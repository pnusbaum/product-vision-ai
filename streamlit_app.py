import os
import streamlit as st
import requests

API_URL = "https://product-api-847285464691.europe-central2.run.app"
PRODUCT_DESCRIPTION_API_URL = "http://localhost:8081/generate-product-description"

st.set_page_config(page_title="Product Vision AI", layout="wide")

st.title("Product Vision AI")
st.write("Generator opisów produktów oraz wyszukiwarka podobnych produktów")


def render_product_description_tab():
    st.header("Generator opisów produktów")

    brand = st.text_input("Marka produktu")
    product_name = st.text_input("Nazwa produktu")
    uploaded_file = st.file_uploader(
        "Zdjęcie produktu",
        type=["jpg", "jpeg", "png", "webp"],
        key="description_file",
    )

    if st.button("Wygeneruj opis"):
        if not brand or not product_name or uploaded_file is None:
            st.warning("Uzupełnij markę, nazwę produktu i dodaj zdjęcie.")
            return

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type,
            )
        }

        data = {
            "brand": brand,
            "product_name": product_name,
        }

        with st.spinner("Analizuję produkt i generuję opis..."):
            response = requests.post(
                PRODUCT_DESCRIPTION_API_URL,
                data=data,
                files=files,
                timeout=120,
            )

        if response.status_code != 200:
            st.error("Błąd podczas generowania opisu.")
            st.code(response.text)
            return

        result = response.json()

        if not result.get("is_in_catalog"):
            st.warning(result.get("catalog_message", "Produkt poza katalogiem."))
            st.json(result)
            return

        st.success("Opis wygenerowany poprawnie.")

        st.subheader("Kategoria")
        st.write(result.get("category"))

        st.subheader("Tagi")
        st.write(", ".join(result.get("tags", [])))

        st.subheader("Rozpoznane cechy")
        st.json(result.get("features"))

        st.subheader("Opis marketingowy")
        st.write(result.get("marketing_description"))

        st.subheader("SEO")
        st.json(result.get("seo"))

        with st.expander("Pełny JSON"):
            st.json(result)


def display_products(products):
    cols = st.columns(3)

    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.image(product["image_url"], use_container_width=True)
            st.subheader(product["name"])
            st.write(f"Kategoria: {product['category']}")
            st.write(f"Distance: {round(product['distance'], 4)}")


def render_image_search_tab():
    st.header("Wyszukiwarka podobnych produktów")

    mode = st.radio(
        "Wybierz tryb wyszukiwania",
        ["Image search", "Text search"],
    )

    limit = st.slider("Liczba wyników", 1, 20, 5)

    if mode == "Image search":
        uploaded_file = st.file_uploader(
            "Prześlij zdjęcie produktu",
            type=["jpg", "jpeg", "png"],
            key="search_file",
        )

        if uploaded_file and st.button("Szukaj po obrazie"):
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type,
                )
            }

            response = requests.post(
                f"{API_URL}/search-by-image?limit={limit}",
                files=files,
            )

            if response.ok:
                products = response.json()
                display_products(products)
            else:
                st.error("Błąd API")
                st.code(response.text)

    if mode == "Text search":
        query = st.text_input("Wpisz opis produktu")

        if query and st.button("Szukaj po tekście"):
            response = requests.post(
                f"{API_URL}/search-by-text?limit={limit}",
                json={"query": query},
            )

            if response.ok:
                products = response.json()
                display_products(products)
            else:
                st.error("Błąd API")
                st.code(response.text)


tab1, tab2 = st.tabs([
    "Generator opisów produktów",
    "Wyszukiwarka podobnych produktów",
])

with tab1:
    render_product_description_tab()

with tab2:
    render_image_search_tab()