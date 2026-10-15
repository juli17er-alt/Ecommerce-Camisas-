from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class DataSource(str, Enum):
    LIVE = "LIVE"
    DEMO = "DEMO"
    MANUAL = "MANUAL"

class MatchConfidence(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"
    SIN_COINCIDENCIA = "SIN_COINCIDENCIA"

class CompetitorName(str, Enum):
    UNDERGOLD = "Undergold"
    CLEMENT = "Clement"

class ScrapedProduct(BaseModel):
    id: str
    competitor: str
    title: str
    url: str
    image_url: Optional[str] = None
    price_cop: float
    original_price_cop: Optional[float] = None
    discount_pct: Optional[float] = None
    available: bool = True
    category: Optional[str] = "Camisetas"
    color: Optional[str] = None
    sizes: List[str] = Field(default_factory=list)
    timestamp: str
    data_source: DataSource = DataSource.LIVE
    collection_status: str = "SUCCESS"
    similarity_score: float = 0.0
    match_confidence: MatchConfidence = MatchConfidence.MEDIA
    match_explanation: str = ""
    price_rank: Optional[int] = None

class CompetitorStatus(BaseModel):
    name: str
    official_url: str
    status: str  # "OK", "ERROR", "BLOCKED", "DEMO", "EMPTY"
    message: str
    products_found: int = 0
    response_time_ms: float = 0.0

class PriceComparisonSummary(BaseModel):
    total_products: int = 0
    lowest_price: Optional[float] = None
    lowest_price_product: Optional[str] = None
    lowest_price_competitor: Optional[str] = None
    highest_price: Optional[float] = None
    highest_price_product: Optional[str] = None
    highest_price_competitor: Optional[str] = None
    average_price: Optional[float] = None
    undergold_avg_price: Optional[float] = None
    clement_avg_price: Optional[float] = None
    absolute_difference: Optional[float] = None
    percentage_difference: Optional[float] = None
    cheaper_competitor: Optional[str] = None
    comparison_verdict: str = ""
    is_comparable: bool = False

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Término de búsqueda de la prenda")
    competitors: List[str] = Field(default=["Undergold", "Clement"])
    demo_mode: bool = False
    category_filter: Optional[str] = None
    color_filter: Optional[str] = None
    size_filter: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    only_in_stock: bool = False

class SearchResponse(BaseModel):
    query: str
    timestamp: str
    competitors_status: List[CompetitorStatus]
    summary: PriceComparisonSummary
    products: List[ScrapedProduct]
    demo_mode_active: bool = False

class ManualProductRequest(BaseModel):
    query: str
    competitor: str
    title: str
    price_cop: float
    original_price_cop: Optional[float] = None
    url: str
    image_url: Optional[str] = None
    available: bool = True
    color: Optional[str] = None
    sizes: List[str] = Field(default_factory=list)

class HistoryItem(BaseModel):
    id: int
    query: str
    competitors: str
    total_results: int
    min_price: Optional[float]
    max_price: Optional[float]
    avg_price: Optional[float]
    demo_mode: bool
    created_at: str
