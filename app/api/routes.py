import time
import asyncio
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Response
from app.config import settings
from app.models.schemas import (
    SearchRequest, SearchResponse, CompetitorStatus,
    ManualProductRequest, HistoryItem, ScrapedProduct, DataSource, MatchConfidence
)
from app.scrapers.undergold import UndergoldAdapter
from app.scrapers.clement import ClementAdapter
from app.scrapers.demo_data import get_demo_products
from app.services.matcher import rank_and_score_products
from app.services.comparator import compute_price_comparison
from app.services.exporter import generate_csv
from app.database.db import (
    save_search_history, get_recent_history, clear_history,
    save_manual_entry, get_manual_entries_for_query
)

router = APIRouter(prefix="/api")

undergold_adapter = UndergoldAdapter()
clement_adapter = ClementAdapter()

@router.post("/search", response_model=SearchResponse)
async def search_competitors(req: SearchRequest):
    query = req.query.strip()
    if len(query) < 2:
        raise HTTPException(status_code=400, detail="El término de búsqueda debe tener al menos 2 caracteres.")

    competitors_status: List[CompetitorStatus] = []
    collected_products: List[ScrapedProduct] = []
    
    # 1. Check if user activated Demo Mode explicitly
    if req.demo_mode:
        t0 = time.time()
        demo_items = get_demo_products(query, req.competitors)
        elapsed_ms = round((time.time() - t0) * 1000, 1)
        
        for comp in req.competitors:
            comp_prods = [p for p in demo_items if p.competitor == comp]
            url = settings.UNDERGOLD_URL if comp == "Undergold" else settings.CLEMENT_URL
            competitors_status.append(CompetitorStatus(
                name=comp,
                official_url=url,
                status="DEMO",
                message=f"Modo Demostración Académica activo ({len(comp_prods)} prendas simuladas)",
                products_found=len(comp_prods),
                response_time_ms=elapsed_ms
            ))
        collected_products.extend(demo_items)
    else:
        # 2. Live Automated Scraping from Competitors
        tasks = []
        comp_names = []
        
        if "Undergold" in req.competitors:
            tasks.append(undergold_adapter.search(query))
            comp_names.append("Undergold")
            
        if "Clement" in req.competitors:
            tasks.append(clement_adapter.search(query))
            comp_names.append("Clement")

        if not tasks:
            raise HTTPException(status_code=400, detail="Debe seleccionar al menos una tienda competidora.")

        t0 = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time_ms = round((time.time() - t0) * 1000, 1)

        for name, res in zip(comp_names, results):
            official_url = settings.UNDERGOLD_URL if name == "Undergold" else settings.CLEMENT_URL
            
            if isinstance(res, Exception):
                competitors_status.append(CompetitorStatus(
                    name=name,
                    official_url=official_url,
                    status="ERROR",
                    message=f"Error inesperado al conectar: {str(res)}",
                    products_found=0,
                    response_time_ms=total_time_ms
                ))
            else:
                prods, msg, is_success = res
                st = "OK" if is_success and prods else ("EMPTY" if is_success else "ERROR")
                competitors_status.append(CompetitorStatus(
                    name=name,
                    official_url=official_url,
                    status=st,
                    message=msg,
                    products_found=len(prods),
                    response_time_ms=total_time_ms
                ))
                collected_products.extend(prods)

        # 3. Incorporate any manual entries for this search query
        manual_records = get_manual_entries_for_query(query)
        for m in manual_records:
            if m["competitor"] in req.competitors:
                collected_products.append(ScrapedProduct(
                    id=m["id"],
                    competitor=m["competitor"],
                    title=m["title"],
                    url=m["url"],
                    image_url=m["image_url"],
                    price_cop=m["price_cop"],
                    original_price_cop=m["original_price_cop"],
                    discount_pct=None,
                    available=m["available"],
                    category="Entrada Manual",
                    color=m["color"],
                    sizes=m["sizes"],
                    timestamp=m["created_at"],
                    data_source=DataSource.MANUAL,
                    collection_status="MANUAL"
                ))

    # 4. Apply Optional User Filters
    filtered = collected_products
    if req.only_in_stock:
        filtered = [p for p in filtered if p.available]
        
    if req.min_price is not None:
        filtered = [p for p in filtered if p.price_cop >= req.min_price]
        
    if req.max_price is not None:
        filtered = [p for p in filtered if p.price_cop <= req.max_price]
        
    if req.color_filter:
        col = req.color_filter.lower()
        filtered = [p for p in filtered if p.color and col in p.color.lower()]
        
    if req.size_filter:
        sz = req.size_filter.upper()
        filtered = [p for p in filtered if any(sz == s.upper() for s in p.sizes)]

    # 5. Product Matching & Confidence Scoring
    scored_products = rank_and_score_products(query, filtered)

    # 6. Price Comparison & Statistical Summary
    summary, ranked_products = compute_price_comparison(scored_products)

    # 7. Persist to History
    try:
        save_search_history(
            query=query,
            competitors=req.competitors,
            total_results=len(ranked_products),
            min_price=summary.lowest_price,
            max_price=summary.highest_price,
            avg_price=summary.average_price,
            demo_mode=req.demo_mode
        )
    except Exception as db_err:
        print(f"Warning: Failed to save search history: {db_err}")

    return SearchResponse(
        query=query,
        timestamp=datetime.now().isoformat(),
        competitors_status=competitors_status,
        summary=summary,
        products=ranked_products,
        demo_mode_active=req.demo_mode
    )

@router.get("/history", response_model=List[HistoryItem])
async def get_history():
    return get_recent_history(limit=20)

@router.delete("/history")
async def delete_history():
    clear_history()
    return {"message": "Historial de búsquedas limpiado con éxito."}

@router.post("/manual")
async def add_manual_product(req: ManualProductRequest):
    entry_id = save_manual_entry(req.model_dump())
    return {"message": "Producto manual registrado con éxito", "id": entry_id}

@router.post("/export/csv")
async def export_products_csv(products: List[ScrapedProduct]):
    csv_content = generate_csv(products)
    # Return with BOM for Excel UTF-8 compatibility
    encoded = ("\ufeff" + csv_content).encode("utf-8")
    filename = f"pricehunter_reporte_{int(time.time())}.csv"
    return Response(
        content=encoded,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat(),
        "competitors": {
            "Undergold": settings.UNDERGOLD_URL,
            "Clement": settings.CLEMENT_URL
        }
    }
