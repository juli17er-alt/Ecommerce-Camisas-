from typing import List, Tuple, Optional
from app.models.schemas import ScrapedProduct, PriceComparisonSummary

def format_cop(val: Optional[float]) -> str:
    """Formats a number as Colombian Pesos, e.g. 250000 -> '$ 250.000 COP'"""
    if val is None:
        return "N/D"
    int_val = int(round(val))
    formatted = f"{int_val:,}".replace(",", ".")
    return f"${formatted} COP"

def compute_price_comparison(products: List[ScrapedProduct]) -> Tuple[PriceComparisonSummary, List[ScrapedProduct]]:
    if not products:
        return PriceComparisonSummary(
            total_products=0,
            comparison_verdict="No se encontraron productos disponibles para comparar.",
            is_comparable=False
        ), products

    # Sort products by price ascending to assign price ranks
    sorted_by_price = sorted(products, key=lambda p: p.price_cop)
    for idx, prod in enumerate(sorted_by_price):
        prod.price_rank = idx + 1

    lowest_prod = sorted_by_price[0]
    highest_prod = sorted_by_price[-1]
    
    prices = [p.price_cop for p in products]
    avg_price = round(sum(prices) / len(prices), 2)
    
    undergold_prods = [p for p in products if p.competitor == "Undergold"]
    clement_prods = [p for p in products if p.competitor == "Clement"]
    
    undergold_avg = round(sum(p.price_cop for p in undergold_prods) / len(undergold_prods), 2) if undergold_prods else None
    clement_avg = round(sum(p.price_cop for p in clement_prods) / len(clement_prods), 2) if clement_prods else None
    
    is_comparable = bool(undergold_prods and clement_prods)
    cheaper_comp = None
    abs_diff = None
    pct_diff = None
    verdict = ""

    if is_comparable:
        ug_min = min(p.price_cop for p in undergold_prods)
        cl_min = min(p.price_cop for p in clement_prods)
        
        abs_diff = round(abs(ug_min - cl_min), 2)
        base_min = min(ug_min, cl_min)
        pct_diff = round((abs_diff / base_min) * 100, 1) if base_min > 0 else 0.0
        
        if ug_min < cl_min:
            cheaper_comp = "Undergold"
            verdict = (
                f"Undergold ofrece el precio base más bajo ({format_cop(ug_min)} vs {format_cop(cl_min)} de Clement), "
                f"siendo {format_cop(abs_diff)} ({pct_diff}%) más económico en la entrada de gama analizada. "
                "Importante: los productos son comparables en categoría/estilo urbano, pero pueden presentar diferencias en gramaje de algodón y patronaje."
            )
        elif cl_min < ug_min:
            cheaper_comp = "Clement"
            verdict = (
                f"Clement ofrece el precio base más bajo ({format_cop(cl_min)} vs {format_cop(ug_min)} de Undergold), "
                f"siendo {format_cop(abs_diff)} ({pct_diff}%) más accesible en esta categoría. "
                "Importante: los productos son comparables en categoría/estilo urbano, pero pueden presentar diferencias en gramaje de algodón y patronaje."
            )
        else:
            cheaper_comp = "Empate"
            verdict = (
                f"Ambas marcas registran el mismo precio mínimo de entrada ({format_cop(ug_min)}). "
                "Se recomienda evaluar valor agregado (detalles gráficos, bordados y disponibilidad de tallas)."
            )
    else:
        competitor_present = "Undergold" if undergold_prods else "Clement"
        verdict = (
            f"Solo se obtuvieron resultados para {competitor_present}. "
            f"El precio varía entre {format_cop(lowest_prod.price_cop)} y {format_cop(highest_prod.price_cop)} con un promedio de {format_cop(avg_price)}. "
            "Para una comparación cruzada completa, intente nuevamente o use la función de Entrada Manual para registrar datos de la otra marca."
        )

    summary = PriceComparisonSummary(
        total_products=len(products),
        lowest_price=lowest_prod.price_cop,
        lowest_price_product=lowest_prod.title,
        lowest_price_competitor=lowest_prod.competitor,
        highest_price=highest_prod.price_cop,
        highest_price_product=highest_prod.title,
        highest_price_competitor=highest_prod.competitor,
        average_price=avg_price,
        undergold_avg_price=undergold_avg,
        clement_avg_price=clement_avg,
        absolute_difference=abs_diff,
        percentage_difference=pct_diff,
        cheaper_competitor=cheaper_comp,
        comparison_verdict=verdict,
        is_comparable=is_comparable
    )

    return summary, sorted_by_price
