# PriceHunter — Plataforma Automatizada de Inteligencia de Precios

> **"Inteligencia de precios para decisiones comerciales más informadas."**  
> *Proyecto Académico Universitario — Asignatura de Comercio Electrónico y Desarrollo Web (Colombia, 2026)*

---

## 1. Descripción del Proyecto

**PriceHunter** es una plataforma web completa y funcional concebida para una tienda en línea colombiana de camisetas (*streetwear*) que necesita monitorear, normalizar y comparar de manera automatizada los precios ofrecidos por dos de sus principales competidores directos en Colombia:

1. **Undergold**: Marca colombiana de ropa urbana de alto gramaje ([https://undergoldapparel.com](https://undergoldapparel.com)).
2. **Clement (Clemont)**: Marca colombiana de *streetwear* de lujo y moda urbana ([https://clemont.co](https://clemont.co)).

A diferencia de un prototipo estático o un mockup preliminar, PriceHunter es una aplicación de demostración académica funcional de recolección de datos web en tiempo real, normalización léxica, coincidencia difusa de productos (*fuzzy matching*), comparación estadística de precios en Pesos Colombianos (COP) y generación de reportes ejecutivos con exportación en formato CSV.

---

## 2. Verificación de Tiendas Oficiales

Antes de la implementación, se realizó una investigación rigurosa de las marcas:
* **Undergold**: Tienda oficial verificada en **`https://undergoldapparel.com`**.
* **Clement**: La marca de moda urbana colombiana opera comercialmente bajo el nombre de registro **Clemont**, con tienda online oficial verificada en **`https://clemont.co`**.

Ambas plataformas están construidas sobre infraestructura de comercio electrónico Shopify, lo cual permite la extracción estructurada mediante sus endpoints oficiales de sugerencias de búsqueda (`/search/suggest.json`), catálogos (`/products.json`) y páginas de búsqueda HTML con selectores CSS limpios.

---

## 3. Arquitectura del Sistema

El proyecto sigue una arquitectura desacoplada y mantenible con separación de responsabilidades:

```
Ecommerce Camisas/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Entrada FastAPI, middlewares, archivos estáticos y ciclo de vida
│   ├── config.py                  # Parámetros de configuración, URLs y timeouts
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Modelos Pydantic (ScrapedProduct, SearchRequest, Summary, etc.)
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                  # Persistencia en SQLite (historial y entradas manuales)
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base.py                # Adaptador abstracto BaseScraper, limpiador de COP y extractores
│   │   ├── undergold.py           # UndergoldAdapter (Shopify Suggest & Catalog fallback)
│   │   ├── clement.py             # ClementAdapter (Shopify Suggest & Catalog fallback)
│   │   └── demo_data.py           # Catálogo académico de demostración con datos verificados
│   ├── services/
│   │   ├── __init__.py
│   │   ├── matcher.py             # Algoritmo de normalización y Fuzzy Matching (RapidFuzz)
│   │   ├── comparator.py          # Comparación estadística de precios, rankings y veredictos
│   │   └── exporter.py            # Generación de reportes CSV compatibles con Microsoft Excel
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # Endpoints REST (/search, /history, /manual, /export/csv, /health)
│   └── static/
│       ├── index.html             # Interfaz SPA responsiva con estética streetwear colombiana
│       ├── css/
│       │   └── custom.css         # Clases de diseño, badges de procedencia y efectos visuales
│       └── js/
│           ├── api.js             # Cliente JavaScript asíncrono para consumir la API
│           └── app.js             # Controlador de estado reactivo, filtros, vistas y modales
├── tests/
│   ├── __init__.py
│   ├── test_matcher.py            # Pruebas de normalización y coincidencia difusa
│   ├── test_comparator.py         # Pruebas de cálculo de diferencias de precios y rankings
│   ├── test_scrapers.py           # Pruebas de limpiadores y procedencia de datos demo
│   ├── test_live_adapters.py      # Pruebas de conexión en vivo con Undergold y Clement
│   └── test_api.py                # Pruebas de integración de endpoints FastAPI
├── requirements.txt               # Dependencias del proyecto
├── Dockerfile                     # Configuración de contenedor para producción
├── Procfile                       # Definición de procesos para Render / Railway / Heroku
├── render.yaml                    # Blueprint para despliegue en un clic en Render
├── .env.example                   # Variables de entorno de ejemplo
├── .gitignore                     # Exclusiones de Git
├── run.py                         # Script de inicio rápido en un comando
└── README.md                      # Documentación académica y técnica
```

---

## 4. Fundamentos Académicos y Técnicos

### 4.1 ¿Qué es Web Scraping y para qué sirve?
El **Web Scraping** es el proceso automatizado mediante el cual un programa informático consulta documentos web (HTML, XML, JSON), los interpreta semánticamente y extrae campos de interés específicos (nombres de productos, precios, disponibilidad de tallas, imágenes). En el comercio electrónico de camisetas y moda urbana, permite sustituir el monitoreo manual de catálogos por recopilación sistemática de datos para la fijación estratégica de precios.

### 4.2 ¿Por qué se requiere un Backend?
Un navegador web tradicional (frontend) **no puede** realizar scraping directo por múltiples razones:
1. **Políticas de CORS (Cross-Origin Resource Sharing)**: Los navegadores bloquean peticiones JavaScript iniciadas hacia dominios de terceros que no incluyan encabezados explícitos de autorización.
2. **Seguridad y Privacidad**: Ejecutar la lógica de extracción en el navegador expondría algoritmos internos, selectores, tokens y configuraciones de red.
3. **Control de Conexiones y Resiliencia**: El backend en Python gestiona de manera controlada los tiempos de espera (*timeouts*), reintentos, análisis concurrente con `asyncio.gather` y almacenamiento en bases de datos.

### 4.3 Algoritmo de Coincidencia de Productos (Fuzzy Matching)
Para evitar comparar prendas incompatibles o asumir falsas identidades entre marcas, PriceHunter implementa un motor de coincidencia probabilística:
* **Normalización Léxica**: Se eliminan diacríticos y acentos (`algodón` $\rightarrow$ `algodon`), se suprimen signos de puntuación y se homologan términos del argot urbano mediante un diccionario de sinónimos (`t-shirt = tee = camiseta`, `oversized = boxy = holgada`, `black = negro`).
* **Puntuación Ponderada**:
  $$\text{Score} = 0.50 \times \text{TokenSetRatio} + 0.25 \times \text{PartialRatio} + 0.25 \times \text{JaccardKeywordOverlap}$$
* **Nivel de Confianza Transparente**:
  * **Alta ($\ge 75\%$)**: Prenda del mismo estilo, corte y color; altamente comparable.
  * **Media ($50\% - 74\%$)**: Prenda similar en categoría, pero con diferencias en modelo o arte gráfico.
  * **Baja ($< 50\%$)**: Prenda de otra categoría o estilo divergente.

### 4.4 Tratamiento de Divisas y Precios en COP
Los precios de la moda colombiana se expresan en Pesos Colombianos (COP) sin centavos. El módulo normaliza cadenas con separadores de miles (`$ 250.000` $\rightarrow$ `250000.0`), calcula la brecha absoluta ($|P_A - P_B|$) y la diferencia porcentual relativa sobre el precio base mínimo:
$$\Delta\% = \left(\frac{|P_{\text{Undergold}} - P_{\text{Clement}}|}{\min(P_{\text{Undergold}}, P_{\text{Clement}})}\right) \times 100$$

### 4.5 Honestidad en la Recolección de Datos y Manejo de Fallos
El sistema nunca oculta fallos ni reemplaza silenciosamente peticiones caídas con datos ficticios. Cada producto expone una etiqueta visible de procedencia:
* `🟢 En Vivo`: Obtenido en tiempo real de la tienda oficial mediante el adaptador.
* `🔵 Datos de Demostración`: Prenda simulada verificada perteneciente al modo demo académico.
* `🟠 Entrada Manual`: Prenda registrada manualmente por el usuario.

Si una tienda competidora bloquea el acceso o experimenta latencia excesiva, el sistema mantiene operativo al otro competidor, expone un diagnóstico claro con código de estado HTTP y ofrece un enlace directo a la tienda oficial o la opción de entrada manual.

### 4.6 Consideraciones Éticas y Responsables
* **Respeto a robots.txt y Términos de Uso**: No se realizan peticiones masivas ni ataques de denegación de servicio.
* **Intervalos y Caché**: Se usan tiempos de espera razonables (15 segundos) y límites de productos por consulta.
* **Sin Evasión de Controles**: No se vulneran CAPTCHAs, paywalls, sistemas de autenticación ni tokens de sesión privados.

---

## 5. Requisitos y Puesta en Marcha Local

### Prerrequisitos
* **Python 3.11** o superior instalado en el equipo.
* Acceso a Internet para consultas en vivo a las tiendas oficiales (o activación del Modo Demo si no hay conexión).

### Paso 1: Clonar o abrir el directorio del proyecto
```bash
cd "Ecommerce Camisas"
```

### Paso 2: Crear y activar entorno virtual (Recomendado)
* **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Linux / macOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Iniciar la aplicación
Ejecuta el script unificado de inicio:
```bash
python run.py
```
O directamente con Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Paso 5: Abrir la interfaz web
Abre tu navegador en:
```
http://127.0.0.1:8000
```

---

## 6. Ejecución de Pruebas Automatizadas

El proyecto cuenta con una suite completa de pruebas unitarias y de integración desarrolladas con `pytest` y `pytest-asyncio`. Para ejecutarlas:

```bash
python -m pytest -v
```

### Resumen de la Suite de Pruebas:
1. `tests/test_api.py`:
   - Endpoint de salud (`GET /api/health`).
   - Servido de la aplicación SPA (`GET /`).
   - Validación de entradas vacías o cortas (código 400/422).
   - Modo demostración (`POST /api/search` con `demo_mode=True`).
   - Persistencia de entrada manual e historial SQLite.
   - Exportación de reporte en formato CSV con codificación UTF-8 BOM.
2. `tests/test_comparator.py`:
   - Formato monetario colombiano (`$ 250.000 COP`).
   - Comparación bilateral, cálculo de brecha porcentual y asignación de ranking.
3. `tests/test_matcher.py`:
   - Normalización y eliminación de tildes.
   - Mapeo léxico de términos streetwear.
   - Clasificación de alta coincidencia vs productos no relacionados.
4. `tests/test_scrapers.py`:
   - Limpieza de formatos de precios colombianos.
   - Cálculo de descuentos.
   - Procedencia e integridad de datos del modo demo.
5. `tests/test_live_adapters.py`:
   - Conectividad real con los endpoints oficiales de Undergold y Clement.

---

## 7. Guía de Despliegue en Producción

La aplicación está completamente preparada para ser desplegada en plataformas en la nube públicas para la sustentación ante el docente y compañeros de clase.

### Opción A: Despliegue en Render (Recomendado)
Render permite alojar el backend FastAPI y los archivos estáticos en un único servicio web gratuito:
1. Sube el código a un repositorio en **GitHub**.
2. Inicia sesión en [Render.com](https://render.com) y selecciona **New +** $\rightarrow$ **Web Service**.
3. Conecta el repositorio de GitHub.
4. Configura los parámetros:
   * **Name**: `pricehunter-app`
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Haz clic en **Create Web Service**. Una vez finalizado el despliegue, Render proporcionará una URL pública segura (ejemplo: `https://pricehunter-app.onrender.com`).

*(Nota: El archivo `render.yaml` incluido en la raíz automatiza esta configuración como Blueprint de Infraestructura como Código).*

### Opción B: Despliegue con Docker
Construye y corre la imagen en cualquier servidor o VPS con Docker:
```bash
docker build -t pricehunter .
docker run -d -p 8000:8000 --name pricehunter_app pricehunter
```

---

## 8. Funcionalidades para la Sustentación en Clase

Durante la presentación del proyecto universitario, puedes demostrar los siguientes escenarios:

1. **Búsqueda en Vivo de Camisetas**:
   * Escribe en el buscador: `"Black oversized T-shirt"` o haz clic en uno de los botones de sugerencia rápida.
   * Observa la barra de estado de adaptadores: latencia en milisegundos y estado `En Vivo` de Undergold y Clement.
   * Revisa las tarjetas de productos con imagen oficial, precio en COP, porcentaje de descuento y nivel de coincidencia.
2. **Alternar Vistas**:
   * Cambia entre la vista de **Tarjetas** y la **Tabla Comparativa**.
   * Ordena por "Menor a mayor precio" para identificar al líder en costos.
3. **Exportación a CSV**:
   * Haz clic en **"Exportar CSV"** para descargar el informe compatible con Microsoft Excel.
4. **Demostración sin Conexión (Modo Demo)**:
   * Si la red Wi-Fi del aula universitaria falla o tiene restricciones de puertos, activa el interruptor **"Modo Demo"** en la barra superior.
   * La aplicación mostrará un banner azul de advertencia y cargará el catálogo de prueba verificado sin generar errores de red.
5. **Entrada Manual de Precios**:
   * Abre el modal **"Entrada Manual"** para registrar una prenda no encontrada en el catálogo web o un producto físico visto en tienda.
   * El producto se indexará en el ranking y quedará persistido en la base de datos SQLite.
6. **Historial de Consultas**:
   * Abre el modal **"Historial"** para ver las búsquedas ejecutadas, con un botón para recargarlas con un solo clic.

---

## 9. Licencia y Créditos

* **Proyecto**: PriceHunter — Automated Competitor Price Intelligence Platform
* **Asignatura**: Comercio Electrónico / Desarrollo Web
* **Año**: 2026
* **Licencia**: MIT License
