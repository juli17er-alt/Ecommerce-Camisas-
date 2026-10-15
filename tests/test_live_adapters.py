import pytest
import asyncio
from app.scrapers.undergold import UndergoldAdapter
from app.scrapers.clement import ClementAdapter
from app.models.schemas import DataSource

@pytest.mark.asyncio
async def test_live_undergold_adapter():
    adapter = UndergoldAdapter()
    products, msg, is_success = await adapter.search("t-shirt", limit=5)
    # The adapter should return a boolean status and message
    assert isinstance(is_success, bool)
    assert isinstance(msg, str)
    if is_success and products:
        p = products[0]
        assert p.competitor == "Undergold"
        assert p.price_cop > 0
        assert p.url.startswith("http")
        assert p.data_source == DataSource.LIVE
        assert p.timestamp != ""

@pytest.mark.asyncio
async def test_live_clement_adapter():
    adapter = ClementAdapter()
    products, msg, is_success = await adapter.search("t-shirt", limit=5)
    assert isinstance(is_success, bool)
    assert isinstance(msg, str)
    if is_success and products:
        p = products[0]
        assert p.competitor == "Clement"
        assert p.price_cop > 0
        assert p.url.startswith("http")
        assert p.data_source == DataSource.LIVE
        assert p.timestamp != ""
