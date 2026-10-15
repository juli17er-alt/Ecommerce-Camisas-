from datetime import datetime
from typing import List
from app.models.schemas import ScrapedProduct, DataSource

DEMO_PRODUCTS = [
    # Undergold Demo Items
    {
        "id": "demo-ug-1",
        "competitor": "Undergold",
        "title": "Basics Light Logo V2 T-Shirt Black",
        "url": "https://undergoldapparel.com/products/basics-light-logo-v2-t-shirt-black",
        "image_url": "https://cdn.shopify.com/s/files/1/0275/4671/4181/files/1_baf48949-f10f-444b-b81a-8a53ea43c634_jpg.png?v=1791500529",
        "price_cop": 250000.0,
        "original_price_cop": 280000.0,
        "discount_pct": 10.7,
        "available": True,
        "category": "Camisetas / T-Shirts",
        "color": "Negro",
        "sizes": ["S", "M", "L", "XL"],
    },
    {
        "id": "demo-ug-2",
        "competitor": "Undergold",
        "title": "Line Logo Oversized Tshirt Washed Gray",
        "url": "https://undergoldapparel.com/products/line-logo-tshirt-washed-gray",
        "image_url": "https://cdn.shopify.com/s/files/1/0275/4671/4181/files/2_99cb7726-9a53-4a6c-ab79-6adff43dc83a_jpg.png?v=1791500528",
        "price_cop": 250000.0,
        "original_price_cop": None,
        "discount_pct": None,
        "available": True,
        "category": "Camisetas / Oversized",
        "color": "Gris",
        "sizes": ["M", "L", "XL"],
    },
    {
        "id": "demo-ug-3",
        "competitor": "Undergold",
        "title": "Agnus Dei Sheep Graphic Tshirt Black",
        "url": "https://undergoldapparel.com/products/agnus-dei-sheep-tshirt-black",
        "image_url": "https://cdn.shopify.com/s/files/1/0275/4671/4181/files/1_baf48949-f10f-444b-b81a-8a53ea43c634_jpg.png?v=1791500529",
        "price_cop": 310000.0,
        "original_price_cop": 350000.0,
        "discount_pct": 11.4,
        "available": True,
        "category": "Camisetas / Graphic",
        "color": "Negro",
        "sizes": ["S", "M", "L"],
    },
    {
        "id": "demo-ug-4",
        "competitor": "Undergold",
        "title": "Minimal Script Boxy Fit White T-shirt",
        "url": "https://undergoldapparel.com/products/minimal-script-boxy-fit-white-tshirt",
        "image_url": "https://cdn.shopify.com/s/files/1/0275/4671/4181/files/2_99cb7726-9a53-4a6c-ab79-6adff43dc83a_jpg.png?v=1791500528",
        "price_cop": 230000.0,
        "original_price_cop": None,
        "discount_pct": None,
        "available": False,
        "category": "Camisetas / Regular",
        "color": "Blanco",
        "sizes": ["S", "XL"],
    },
    # Clement Demo Items
    {
        "id": "demo-cl-1",
        "competitor": "Clement",
        "title": "Camiseta Oversized Hombre Estivo Crema/Negro",
        "url": "https://clemont.co/products/camiseta-oversized-masculino-estivo-crema-negro",
        "image_url": "https://cdn.shopify.com/s/files/1/0572/3881/4908/files/IMG_1029_600x.jpg",
        "price_cop": 246000.0,
        "original_price_cop": None,
        "discount_pct": None,
        "available": True,
        "category": "Camisetas / Oversized",
        "color": "Crema",
        "sizes": ["S", "M", "L", "XL"],
    },
    {
        "id": "demo-cl-2",
        "competitor": "Clement",
        "title": "T-Shirt Hombre Saggezza Semi Oversized Black",
        "url": "https://clemont.co/products/t-shirt-hombre-saggezza",
        "image_url": "https://cdn.shopify.com/s/files/1/0572/3881/4908/files/IMG_1030_600x.jpg",
        "price_cop": 380000.0,
        "original_price_cop": 420000.0,
        "discount_pct": 9.5,
        "available": True,
        "category": "Camisetas / Luxury Streetwear",
        "color": "Negro",
        "sizes": ["S", "M", "L"],
    },
    {
        "id": "demo-cl-3",
        "competitor": "Clement",
        "title": "Camiseta Oversized Hombre Rifiorire Vinotinto",
        "url": "https://clemont.co/products/camiseta-oversized-masculino-rifiorire-rojo",
        "image_url": "https://cdn.shopify.com/s/files/1/0572/3881/4908/files/IMG_1031_600x.jpg",
        "price_cop": 282000.0,
        "original_price_cop": 310000.0,
        "discount_pct": 9.0,
        "available": True,
        "category": "Camisetas / Oversized",
        "color": "Vinotinto",
        "sizes": ["M", "L", "XL"],
    },
    {
        "id": "demo-cl-4",
        "competitor": "Clement",
        "title": "Camiseta Masculino Euforia Taupe Streetwear",
        "url": "https://clemont.co/products/camiseta-masculino-euforia-taupe-clemont",
        "image_url": "https://cdn.shopify.com/s/files/1/0572/3881/4908/files/IMG_1032_600x.jpg",
        "price_cop": 195000.0,
        "original_price_cop": None,
        "discount_pct": None,
        "available": True,
        "category": "Camisetas / Streetwear",
        "color": "Taupe",
        "sizes": ["S", "M", "L", "XL"],
    },
]

def get_demo_products(query: str, competitors: List[str]) -> List[ScrapedProduct]:
    now_iso = datetime.now().isoformat()
    q_lower = query.lower().strip()
    terms = [t for t in q_lower.split() if len(t) > 2]
    
    selected_competitors = set(competitors)
    results: List[ScrapedProduct] = []
    
    for item in DEMO_PRODUCTS:
        if item["competitor"] not in selected_competitors:
            continue
            
        title_lower = item["title"].lower()
        color_lower = item["color"].lower() if item["color"] else ""
        cat_lower = item["category"].lower()
        
        # Match if any term is in title/color/category, or if general query
        matches = True
        if terms:
            matches = any(t in title_lower or t in color_lower or t in cat_lower for t in terms)
            
        if matches or len(results) < 2:  # Ensure at least sample results for demo
            prod = ScrapedProduct(
                id=item["id"],
                competitor=item["competitor"],
                title=item["title"],
                url=item["url"],
                image_url=item["image_url"],
                price_cop=item["price_cop"],
                original_price_cop=item["original_price_cop"],
                discount_pct=item["discount_pct"],
                available=item["available"],
                category=item["category"],
                color=item["color"],
                sizes=item["sizes"],
                timestamp=now_iso,
                data_source=DataSource.DEMO,
                collection_status="DEMO"
            )
            results.append(prod)
            
    return results
