import re
import unicodedata
from typing import List, Tuple, Set
from rapidfuzz import fuzz
from app.models.schemas import ScrapedProduct, MatchConfidence

# Common clothing & streetwear synonyms for normalization
SYNONYM_MAP = {
    "t-shirt": "camiseta",
    "tshirt": "camiseta",
    "tee": "camiseta",
    "playera": "camiseta",
    "remera": "camiseta",
    "shirt": "camisa",
    "hoodie": "buzo",
    "sueter": "buzo",
    "oversized": "oversize",
    "boxy": "oversize",
    "semi-oversized": "oversize",
    "negro": "negro",
    "negra": "negro",
    "black": "negro",
    "blanco": "blanco",
    "blanca": "blanco",
    "white": "blanco",
    "gris": "gris",
    "gray": "gris",
    "grey": "gris",
    "rojo": "rojo",
    "roja": "rojo",
    "red": "rojo",
    "azul": "azul",
    "blue": "azul",
}

# Stopwords to discard for keyword overlap
STOPWORDS = {
    "de", "la", "el", "los", "las", "un", "una", "unos", "unas", "con", "en",
    "por", "para", "y", "o", "al", "del", "a", "the", "in", "with", "for", "and", "hombre", "masculino", "mujer"
}

def strip_accents(text: str) -> str:
    """Normalize and strip diacritics/accents (e.g., 'algodón' -> 'algodon')."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()

def normalize_text(text: str) -> str:
    """Cleans text: removes punctuation, strips accents, maps synonyms."""
    if not text:
        return ""
    clean = strip_accents(text)
    # Replace non-alphanumeric with spaces
    clean = re.sub(r"[^\w\s-]", " ", clean)
    words = clean.split()
    normalized_words = [SYNONYM_MAP.get(w, w) for w in words]
    return " ".join(normalized_words)

def extract_meaningful_tokens(text: str) -> Set[str]:
    """Extract non-stopword tokens of length > 1."""
    norm = normalize_text(text)
    tokens = set()
    for w in norm.split():
        if w not in STOPWORDS and len(w) > 1:
            tokens.add(w)
    return tokens

def calculate_match(query: str, product: ScrapedProduct) -> Tuple[float, MatchConfidence, str]:
    """
    Computes fuzzy matching score, confidence level, and an honest explanatory note.
    """
    norm_query = normalize_text(query)
    target_str = f"{product.title} {product.color or ''} {product.category or ''}"
    norm_target = normalize_text(target_str)
    
    query_tokens = extract_meaningful_tokens(query)
    target_tokens = extract_meaningful_tokens(target_str)
    
    # 1. Fuzzy Token Set Ratio (compares sets of words, robust to word order)
    token_set = fuzz.token_set_ratio(norm_query, norm_target)
    
    # 2. Fuzzy Partial Ratio (substring matching)
    partial = fuzz.partial_ratio(norm_query, norm_target)
    
    # 3. Jaccard Keyword Overlap
    if query_tokens:
        overlap = query_tokens.intersection(target_tokens)
        overlap_score = (len(overlap) / len(query_tokens)) * 100.0
    else:
        overlap = set()
        overlap_score = token_set
        
    # Weighted combined score
    combined_score = round(0.50 * token_set + 0.25 * partial + 0.25 * overlap_score, 1)
    # Clamp between 0 and 100
    combined_score = max(0.0, min(100.0, combined_score))
    
    # Shared keywords list for explanation
    shared_kw = list(overlap)
    shared_str = f" Coincide en: {', '.join(shared_kw)}." if shared_kw else ""
    
    # Determine confidence level
    if combined_score >= 75.0:
        confidence = MatchConfidence.ALTA
        explanation = (
            f"Alta similitud ({combined_score}%).{shared_str} "
            "Estimación algorítmica: producto altamente comparable en atributos y tipo de prenda."
        )
    elif combined_score >= 50.0:
        confidence = MatchConfidence.MEDIA
        explanation = (
            f"Similitud moderada ({combined_score}%).{shared_str} "
            "Producto similar en categoría o corte, pero con posibles variaciones de diseño o tela."
        )
    elif combined_score >= 25.0:
        confidence = MatchConfidence.BAJA
        explanation = (
            f"Baja similitud ({combined_score}%).{shared_str} "
            "Coincidencia parcial o prenda de otra línea; comparar con precaución."
        )
    else:
        confidence = MatchConfidence.SIN_COINCIDENCIA
        explanation = (
            f"Sin coincidencia significativa ({combined_score}%). "
            "No se recomienda comparación directa."
        )
        
    return combined_score, confidence, explanation

def rank_and_score_products(query: str, products: List[ScrapedProduct]) -> List[ScrapedProduct]:
    """Scores each product against query and sorts by score descending."""
    scored: List[ScrapedProduct] = []
    for p in products:
        score, confidence, expl = calculate_match(query, p)
        p.similarity_score = score
        p.match_confidence = confidence
        p.match_explanation = expl
        scored.append(p)
        
    # Sort primarily by similarity score descending, secondarily by price
    scored.sort(key=lambda x: (x.similarity_score, -x.price_cop), reverse=True)
    return scored
