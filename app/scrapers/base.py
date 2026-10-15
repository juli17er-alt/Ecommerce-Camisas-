import re
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from app.models.schemas import ScrapedProduct

COLOR_KEYWORDS = {
    "negro": "Negro",
    "black": "Negro",
    "blanco": "Blanco",
    "white": "Blanco",
    "gris": "Gris",
    "gray": "Gris",
    "grey": "Gris",
    "taupe": "Taupe",
    "beige": "Beige",
    "crema": "Crema",
    "cream": "Crema",
    "rojo": "Rojo",
    "red": "Rojo",
    "vinotinto": "Vinotinto",
    "burgundy": "Vinotinto",
    "azul": "Azul",
    "blue": "Azul",
    "navy": "Azul Marino",
    "verde": "Verde",
    "green": "Verde",
    "olive": "Oliva",
    "cafe": "Café",
    "marron": "Marrón",
    "brown": "Marrón",
    "amarillo": "Amarillo",
    "yellow": "Amarillo",
    "morado": "Morado",
    "purple": "Morado",
    "naranja": "Naranja",
    "orange": "Naranja"
}

STANDARD_SIZES = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "2XL", "3XL", "UNICA", "OS"]

def clean_price(val: Any) -> Optional[float]:
    """Parse Colombian price strings, ints, or floats into float COP."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    
    s = str(val).strip()
    if not s:
        return None
        
    # Remove currency symbols and spaces
    s = re.sub(r"[^\d.,]", "", s)
    
    # Handle Colombian formats: "250.000,00" or "250000.00" or "250.000"
    if "." in s and "," in s:
        # e.g., 250.000,00 -> 250000.00
        s = s.replace(".", "").replace(",", ".")
    elif "." in s and len(s.split(".")[-1]) == 3:
        # e.g., 250.000 (thousands separator)
        s = s.replace(".", "")
    elif "," in s and len(s.split(",")[-1]) == 3:
        # e.g., 250,000 (thousands separator)
        s = s.replace(",", "")
    elif "." in s and len(s.split(".")[-1]) == 2:
        # e.g., 250000.00 (decimal cents)
        pass
        
    try:
        f = float(s)
        return f
    except ValueError:
        return None

def extract_color(title: str, tags: Any = None, description: str = "") -> Optional[str]:
    combined = f"{title} {description} "
    if isinstance(tags, list):
        combined += " ".join(tags)
    elif isinstance(tags, str):
        combined += f" {tags}"
        
    words = re.findall(r"\b[A-Za-zÁ-ú]+\b", combined.lower())
    for w in words:
        if w in COLOR_KEYWORDS:
            return COLOR_KEYWORDS[w]
    return "No especificado"

def extract_sizes(variants: List[Dict[str, Any]]) -> List[str]:
    sizes = []
    for var in variants:
        title = str(var.get("title", "")).strip().upper()
        # Look for standard sizes
        matched = False
        for sz in STANDARD_SIZES:
            if re.search(rf"\b{sz}\b", title):
                if sz not in sizes:
                    sizes.append(sz)
                matched = True
                break
        if not matched and title and title not in ["DEFAULT TITLE", "DEFAULT"]:
            # If variant title is just the size itself
            clean_title = title.split("/")[0].strip()
            if clean_title not in sizes:
                sizes.append(clean_title)
    return sizes if sizes else ["S", "M", "L", "XL"]

def calculate_discount(price: Optional[float], compare_at: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
    if not price or not compare_at or compare_at <= price:
        return None, None
    pct = round(((compare_at - price) / compare_at) * 100, 1)
    return compare_at, pct

class BaseScraper(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 15) -> Tuple[List[ScrapedProduct], str, bool]:
        """
        Executes a search against the competitor's official website.
        Returns: (List[ScrapedProduct], status_message, is_success)
        """
        pass
