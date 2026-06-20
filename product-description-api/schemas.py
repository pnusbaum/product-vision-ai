from pydantic import BaseModel, Field


class ProductFeatures(BaseModel):
    color: str | None = Field(description="Dominujący kolor produktu")
    material: str | None = Field(description="Prawdopodobny materiał")
    style: str | None = Field(description="Styl produktu")
    visible_elements: list[str] = Field(description="Widoczne elementy produktu")


class SEOData(BaseModel):
    title: str
    meta_description: str
    keywords: list[str]


class ProductDescriptionOutput(BaseModel):
    category: str
    tags: list[str]
    features: ProductFeatures
    marketing_description: str
    seo: SEOData