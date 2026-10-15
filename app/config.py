import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "PriceHunter"
    APP_TAGLINE: str = "Inteligencia de precios para decisiones comerciales más informadas."
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Official Competitor Store URLs
    UNDERGOLD_URL: str = "https://undergoldapparel.com"
    CLEMENT_URL: str = "https://clemont.co"
    
    # Scraping Configuration
    REQUEST_TIMEOUT: float = 15.0
    USER_AGENT: str = (

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (PriceHunter/1.0 Academic Scraper)"
    )
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "pricehunter.db")
    
    # Cache TTL in seconds (to avoid redundant requests in short window)
    CACHE_TTL_SECONDS: int = 180

settings = Settings()
