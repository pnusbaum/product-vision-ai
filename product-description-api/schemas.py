
from pydantic import BaseModel, Field


class ProductFeatures(BaseModel):
    product_type: str | None = Field(description="Typ produktu, np. sneakersy, sandały, kurtka, doniczka")
    color: str | None = Field(description="Dominujący kolor produktu")
    secondary_colors: list[str] = Field(default_factory=list, description="Kolory dodatkowe")
    material: str | None = Field(description="Prawdopodobny materiał produktu")
    style: str | None = Field(description="Styl produktu, np. sportowy, elegancki, casual")
    target_group: str | None = Field(description="Prawdopodobna grupa docelowa")
    visible_elements: list[str] = Field(default_factory=list, description="Widoczne elementy produktu")
    uncertainty_notes: list[str] = Field(default_factory=list, description="Informacje, których nie da się pewnie rozpoznać ze zdjęcia")


class ProductAnalysisOutput(BaseModel):
    category: str = Field(description="Kategoria produktu")
    tags: list[str] = Field(description="Tagi produktowe")
    features: ProductFeatures


class SEOData(BaseModel):
    title: str = Field(description="Tytuł SEO")
    meta_description: str = Field(description="Opis meta SEO")
    keywords: list[str] = Field(description="Słowa kluczowe SEO")

class CopywritingOutput(BaseModel):
    marketing_description: str
    seo: SEOData
class ProductDescriptionOutput(BaseModel):
    is_in_catalog: bool
    catalog_message: str | None = None

    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    features: ProductFeatures | None = None

    marketing_description: str | None = None
    seo: SEOData | None = None
    
class ProductRoutingOutput(BaseModel):
    main_category: str | None
    confidence: str
    reason: str