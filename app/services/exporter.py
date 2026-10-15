import csv
import io
from typing import List
from app.models.schemas import ScrapedProduct

def generate_csv(products: List[ScrapedProduct]) -> str:
    """
    Generates a CSV string encoded for Excel compatibility (UTF-8-sig).
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    
    # Headers
    writer.writerow([
        "Ranking Precio",
        "Competidor",
        "Nombre de Producto",
        "Precio Actual (COP)",
        "Precio Original (COP)",
        "Descuento (%)",
        "Disponibilidad",
        "Tallas Disponibles",
        "Color",
        "Categoría",
        "Similitud Algorítmica (%)",
        "Nivel Confianza",
        "Explicación Coincidencia",
        "Fuente de Datos",
        "Fecha Consulta",
        "URL Producto Oficial"
    ])
    
    for p in products:
        writer.writerow([
            p.price_rank if p.price_rank else "N/A",
            p.competitor,
            p.title,
            f"{int(round(p.price_cop))}",
            f"{int(round(p.original_price_cop))}" if p.original_price_cop else "",
            f"{p.discount_pct}%" if p.discount_pct else "0%",
            "En Stock" if p.available else "Agotado",
            ", ".join(p.sizes) if p.sizes else "N/D",
            p.color or "N/D",
            p.category or "Camisetas",
            f"{p.similarity_score}%",
            p.match_confidence.value,
            p.match_explanation,
            p.data_source.value,
            p.timestamp,
            p.url
        ])
        
    return output.getvalue()
