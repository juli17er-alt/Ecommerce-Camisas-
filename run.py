import sys
import uvicorn
from app.config import settings

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    print(f"==================================================")
    print(f"    {settings.APP_NAME} v{settings.VERSION}")
    print(f"    {settings.APP_TAGLINE}")
    print(f"==================================================")
    print(f" [INFO] Servidor local listo en: http://127.0.0.1:{settings.PORT}")
    print(f" [INFO] Presiona CTRL+C para detener el servidor.")
    print(f"==================================================")

    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
