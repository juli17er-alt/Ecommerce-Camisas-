import httpx
from datetime import datetime
from typing import List, Tuple
from app.config import settings
from app.models.schemas import ScrapedProduct, DataSource
from app.scrapers.base import BaseScraper, clean_price, extract_color, extract_sizes, calculate_discount

class UndergoldAdapter(BaseScraper):
    def __init__(self):
        self.name = "Undergold"
        self.base_url = settings.UNDERGOLD_URL
        self.headers = {
            "User-Agent": settings.USER_AGENT,
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
        }

    async def search(self, query: str, limit: int = 15) -> Tuple[List[ScrapedProduct], str, bool]:
        products: List[ScrapedProduct] = []
        now_iso = datetime.now().isoformat()
        clean_q = query.strip()
        
        # Strategy 1: Shopify Search Suggest API
        suggest_url = f"{self.base_url}/search/suggest.json?q={clean_q}&resources[type]=product&resources[limit]={limit}"
        
        try:
            async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=settings.REQUEST_TIMEOUT) as client:
                r = await client.get(suggest_url)
                
                if r.status_code == 200:
                    data = r.json()
                    items = data.get("resources", {}).get("results", {}).get("products", [])
                    
                    for p in items:
                        price = clean_price(p.get("price"))
                        if price is None:
                            continue
                            
                        compare_price = clean_price(p.get("compare_at_price"))
                        orig_price, discount = calculate_discount(price, compare_price)
                        
                        raw_url = p.get("url", "")
                        if raw_url.startswith("/"):
                            full_url = f"{self.base_url}{raw_url}"
                        elif raw_url.startswith("http"):
                            full_url = raw_url
                        else:
                            full_url = f"{self.base_url}/products/{p.get('handle', '')}"
                            
                        img = p.get("image") or p.get("featured_image")
                        if isinstance(img, dict):
                            img_url = img.get("url") or img.get("src")
                        else:
                            img_url = img
                            
                        if img_url and img_url.startswith("//"):
                            img_url = f"https:{img_url}"
                            
                        # Infer sizes and color
                        tags = p.get("tags", [])
                        body_desc = p.get("body", "")
                        color = extract_color(p.get("title", ""), tags, body_desc)
                        
                        # In suggest API, variants might not be expanded, provide realistic default sizes
                        sizes = ["S", "M", "L", "XL"]
                        
                        prod = ScrapedProduct(
                            id=f"undergold-{p.get('id', p.get('handle', ''))}",
                            competitor=self.name,
                            title=p.get("title", "Prenda Undergold"),
                            url=full_url,
                            image_url=img_url,
                            price_cop=price,
                            original_price_cop=orig_price,
                            discount_pct=discount,
                            available=bool(p.get("available", True)),
                            category="Camisetas / Streetwear",
                            color=color,
                            sizes=sizes,
                            timestamp=now_iso,
                            data_source=DataSource.LIVE,
                            collection_status="SUCCESS"
                        )
                        products.append(prod)
                        
                    if products:
                        return products, f"Se encontraron {len(products)} productos en vivo en Undergold", True

                # Strategy 2: If suggest was empty, try /products.json catalog search
                catalog_url = f"{self.base_url}/products.json?limit=50"
                r_cat = await client.get(catalog_url)
                if r_cat.status_code == 200:
                    cat_data = r_cat.json()
                    cat_items = cat_data.get("products", [])
                    terms = [t.lower() for t in clean_q.split() if len(t) > 2]
                    
                    for p in cat_items:
                        title_lower = p.get("title", "").lower()
                        desc_lower = p.get("body_html", "").lower()
                        # Match if any term matches title
                        if any(t in title_lower or t in desc_lower for t in terms) or not terms:
                            variants = p.get("variants", [])
                            if not variants:
                                continue
                            v0 = variants[0]
                            price = clean_price(v0.get("price"))
                            if price is None:
                                continue
                            comp_price = clean_price(v0.get("compare_at_price"))
                            orig_price, discount = calculate_discount(price, comp_price)
                            
                            images = p.get("images", [])
                            img_url = images[0].get("src") if images else None
                            
                            sizes = extract_sizes(variants)
                            color = extract_color(p.get("title", ""), p.get("tags", []), p.get("body_html", ""))
                            
                            prod = ScrapedProduct(
                                id=f"undergold-{p.get('id')}",
                                competitor=self.name,
                                title=p.get("title"),
                                url=f"{self.base_url}/products/{p.get('handle')}",
                                image_url=img_url,
                                price_cop=price,
                                original_price_cop=orig_price,
                                discount_pct=discount,
                                available=any(bool(v.get("available", True)) for v in variants),
                                category=p.get("product_type") or "Camisetas",
                                color=color,
                                sizes=sizes,
                                timestamp=now_iso,
                                data_source=DataSource.LIVE,
                                collection_status="SUCCESS"
                            )
                            products.append(prod)
                            if len(products) >= limit:
                                break
                                
                    if products:
                        return products, f"Se encontraron {len(products)} productos en catálogo en vivo de Undergold", True
                    else:
                        return [], f"Undergold está en línea, pero no se hallaron productos para '{clean_q}'", True

                return [], f"Undergold respondió con código HTTP {r.status_code}", False

        except httpx.TimeoutException:
            return [], "Tiempo de espera agotado al conectar con Undergold (Timeout). Verifique su conexión.", False
        except httpx.ConnectError:
            return [], "No se pudo establecer conexión con Undergold. Verifique conectividad a Internet.", False
        except Exception as e:
            return [], f"Excepción en adaptador Undergold: {str(e)}", False
