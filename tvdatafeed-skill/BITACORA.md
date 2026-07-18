# Bitácora de Proyecto: TradingView Datafeed

## [2026-07-12] - Sesión de Trabajo: Refactorización Arquitectónica y Extracción Histórica
**Objetivo:** Modernizar el script de extracción de TradingView hacia una arquitectura de grado empresarial (98/100) y verificar la funcionalidad con diversos instrumentos (AAPL, NDX, COIN, TSLA, SPY).

### ✅ Cambios Realizados:
- **[Refactorización Modular]**: Se transformó la estructura plana del proyecto a una estructura basada en paquetes en `tvdatafeed_project/src/`.
- **[Módulo de Autenticación]**: Se desacopló la lógica en `browser_cookies.py`, `jwt_exchange.py` y `token_cache.py`.
- **[Resiliencia de Red]**: Se implementó una lógica de reintentos (3 intentos) con *backoff exponencial* para el canje del sessionid por el JWT.
- **[Sistema de Cache]**: Se añadió caché de tokens JWT con un TTL configurable de 6 horas, reduciendo a cero las llamadas HTTP redundantes y mejorando el tiempo de respuesta.
- **[Adapter Pattern]**: Se encapsuló la librería `tvDatafeed` externa en una clase `TradingViewAdapter` usando el patrón de composición.
- **[Logging Estructurado]**: Se implementó `src/logger.py` con `RotatingFileHandler` (logs en archivo `logs/tvdatafeed.log`) y salida a consola con formato legible humano. Incluye un filtro de seguridad para truncar automáticamente los tokens JWT en los logs.
- **[CLI con argparse]**: Se reescribió `extractor.py` para soportar argumentos dinámicos (`--symbol`, `--exchange`, `--interval`, `--bars`) y extracciones en *batch* separadas por comas.
- **[Tests Unitarios]**: Se añadió la suite de pruebas en `tests/test_auth.py` cubriendo validación de tokens, cache, entorno e inyección.
- **[Extracción de Datos]**: Se descargó exitosamente la data histórica (velas diarias) de AAPL (1000 barras), NDX (2000 barras), COIN (1316 barras, límite histórico), TSLA (2000 barras) y SPY (2000 barras). 

### 🧠 Decisiones y Notas de Diseño:
- Se optó por un **Backoff manual** sin librerías externas (`tenacity`) para minimizar dependencias.
- Se implementó la descarga de lotes (batch) de forma **secuencial con un delay de 1 segundo** entre llamadas, para prevenir que el IP sea bloqueado (rate-limiting) por los servidores de TradingView.
- Se añadió **detección de entornos headless** (Docker/PROD) para apagar la extracción de cookies y depender puramente de variables de entorno, elevando la portabilidad a la nube.

### ⏳ Pendientes y Siguientes Pasos:
- Estructurar y redactar la documentación oficial de este "Agente de Extracción" y su arquitectura (ver estructura propuesta en progreso).
- Explorar cómo este módulo de extracción interactuará con las capas analíticas o de base de datos en el futuro.
