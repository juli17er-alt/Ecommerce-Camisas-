import pytest
from app.scrapers.base import clean_price, calculate_discount, extract_color
from app.scrapers.demo_data import get_demo_products
from app.models.schemas import DataSource

def test_clean_price():
    assert clean_price("250000.00") == 250000.0
    assert clean_price("250.000") == 250000.0
    assert clean_price("$ 250.000 COP") == 250000.0
    assert clean_price(180000) == 180000.0
    assert clean_price(None) is None
    assert clean_price("abc") is None

def test_calculate_discount():
    orig, pct = calculate_discount(250000.0, 300000.0)
    assert orig == 300000.0
    assert pct == 16.7

    orig_none, pct_none = calculate_discount(250000.0, None)
    assert orig_none is None
    assert pct_none is None

def test_extract_color():
    assert extract_color("Camiseta Oversized Negro Vintage") == "Negro"
    assert extract_color("T-Shirt White Minimal") == "Blanco"
    assert extract_color("Camiseta Estivo", ["taupe", "urban"]) == "Taupe"

def test_demo_products_provenance():
    demo_items = get_demo_products("t-shirt", ["Undergold", "Clement"])
    assert len(demo_items) > 0
    for item in demo_items:
        # Crucial requirement: Demo data must NEVER be confused with live data
        assert item.data_source == DataSource.DEMO
        assert item.collection_status == "DEMO"
        assert item.competitor in ["Undergold", "Clement"]
        assert item.price_cop > 0
