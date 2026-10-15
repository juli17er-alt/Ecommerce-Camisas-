import pytest
from app.services.matcher import normalize_text, strip_accents, calculate_match
from app.models.schemas import ScrapedProduct, DataSource, MatchConfidence

def test_strip_accents():
    assert strip_accents("Camiseta de Algodón") == "camiseta de algodon"
    assert strip_accents("Colección Náutica") == "coleccion nautica"

def test_normalize_text():
    normalized = normalize_text("T-Shirt Oversized Black!")
    assert "camiseta" in normalized
    assert "oversize" in normalized
    assert "negro" in normalized

def test_match_high_confidence():
    prod = ScrapedProduct(
        id="test-1",
        competitor="Undergold",
        title="Basics Oversized Tshirt Black",
        url="https://undergoldapparel.com/test",
        price_cop=250000.0,
        available=True,
        color="Negro",
        category="Camisetas",
        sizes=["S", "M", "L"],
        timestamp="2026-10-14T12:00:00",
        data_source=DataSource.LIVE
    )
    score, confidence, explanation = calculate_match("Black oversized T-shirt", prod)
    assert score >= 75.0
    assert confidence == MatchConfidence.ALTA
    assert "Alta similitud" in explanation

def test_match_unrelated_product_low_confidence():
    prod = ScrapedProduct(
        id="test-2",
        competitor="Clement",
        title="Gorra Deportiva Storm Cap Roja",
        url="https://clemont.co/test",
        price_cop=180000.0,
        available=True,
        color="Rojo",
        category="Accesorios / Gorras",
        sizes=["UNICA"],
        timestamp="2026-10-14T12:00:00",
        data_source=DataSource.LIVE
    )
    score, confidence, explanation = calculate_match("Black oversized T-shirt", prod)
    # Should NOT falsely claim as high match
    assert score < 50.0
    assert confidence in [MatchConfidence.BAJA, MatchConfidence.SIN_COINCIDENCIA]
