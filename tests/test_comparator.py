import pytest
from app.services.comparator import format_cop, compute_price_comparison
from app.models.schemas import ScrapedProduct, DataSource

def test_format_cop():
    assert format_cop(250000.0) == "$250.000 COP"
    assert format_cop(195000.0) == "$195.000 COP"
    assert format_cop(None) == "N/D"

def test_price_comparison_two_competitors():
    p1 = ScrapedProduct(
        id="ug-1",
        competitor="Undergold",
        title="Camiseta Undergold Basic",
        url="https://undergoldapparel.com/1",
        price_cop=250000.0,
        available=True,
        timestamp="2026-10-14T12:00:00",
        data_source=DataSource.LIVE
    )
    p2 = ScrapedProduct(
        id="cl-1",
        competitor="Clement",
        title="Camiseta Clement Estivo",
        url="https://clemont.co/1",
        price_cop=246000.0,
        available=True,
        timestamp="2026-10-14T12:00:00",
        data_source=DataSource.LIVE
    )
    p3 = ScrapedProduct(
        id="ug-2",
        competitor="Undergold",
        title="Camiseta Undergold Agnus Dei",
        url="https://undergoldapparel.com/2",
        price_cop=310000.0,
        available=True,
        timestamp="2026-10-14T12:00:00",
        data_source=DataSource.LIVE
    )

    summary, ranked = compute_price_comparison([p1, p2, p3])
    
    assert summary.total_products == 3
    assert summary.lowest_price == 246000.0
    assert summary.lowest_price_competitor == "Clement"
    assert summary.highest_price == 310000.0
    assert summary.highest_price_competitor == "Undergold"
    assert summary.is_comparable is True
    assert summary.cheaper_competitor == "Clement"
    assert summary.absolute_difference == 4000.0
    
    # Check rankings assigned
    assert ranked[0].id == "cl-1"
    assert ranked[0].price_rank == 1
    assert ranked[1].price_rank == 2
    assert ranked[2].price_rank == 3
