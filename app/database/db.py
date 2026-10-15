import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.config import settings
from app.models.schemas import HistoryItem

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table: search_history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        competitors TEXT NOT NULL,
        total_results INTEGER NOT NULL,
        min_price REAL,
        max_price REAL,
        avg_price REAL,
        demo_mode BOOLEAN NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    
    # Table: manual_entries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manual_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        competitor TEXT NOT NULL,
        title TEXT NOT NULL,
        price_cop REAL NOT NULL,
        original_price_cop REAL,
        url TEXT NOT NULL,
        image_url TEXT,
        available BOOLEAN NOT NULL DEFAULT 1,
        color TEXT,
        sizes TEXT,
        created_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

def save_search_history(
    query: str,
    competitors: List[str],
    total_results: int,
    min_price: Optional[float],
    max_price: Optional[float],
    avg_price: Optional[float],
    demo_mode: bool
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO search_history (query, competitors, total_results, min_price, max_price, avg_price, demo_mode, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            query,
            ", ".join(competitors),
            total_results,
            min_price,
            max_price,
            avg_price,
            1 if demo_mode else 0,
            now_iso
        )
    )
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_recent_history(limit: int = 15) -> List[HistoryItem]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, query, competitors, total_results, min_price, max_price, avg_price, demo_mode, created_at
        FROM search_history
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [
        HistoryItem(
            id=row["id"],
            query=row["query"],
            competitors=row["competitors"],
            total_results=row["total_results"],
            min_price=row["min_price"],
            max_price=row["max_price"],
            avg_price=row["avg_price"],
            demo_mode=bool(row["demo_mode"]),
            created_at=row["created_at"]
        )
        for row in rows
    ]

def clear_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search_history")
    conn.commit()
    conn.close()

def save_manual_entry(data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    sizes_str = ",".join(data.get("sizes", [])) if isinstance(data.get("sizes"), list) else str(data.get("sizes", ""))
    cursor.execute(
        """
        INSERT INTO manual_entries (query, competitor, title, price_cop, original_price_cop, url, image_url, available, color, sizes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["query"],
            data["competitor"],
            data["title"],
            data["price_cop"],
            data.get("original_price_cop"),
            data["url"],
            data.get("image_url"),
            1 if data.get("available", True) else 0,
            data.get("color"),
            sizes_str,
            now_iso
        )
    )
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_manual_entries_for_query(query: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM manual_entries
        WHERE LOWER(query) = LOWER(?)
        ORDER BY id DESC
        """,
        (query,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    entries = []
    for row in rows:
        sizes_list = [s.strip() for s in row["sizes"].split(",") if s.strip()] if row["sizes"] else []
        entries.append({
            "id": f"manual-{row['id']}",
            "competitor": row["competitor"],
            "title": row["title"],
            "price_cop": row["price_cop"],
            "original_price_cop": row["original_price_cop"],
            "url": row["url"],
            "image_url": row["image_url"],
            "available": bool(row["available"]),
            "color": row["color"],
            "sizes": sizes_list,
            "created_at": row["created_at"]
        })
    return entries
