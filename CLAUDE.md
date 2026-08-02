# Alpha Agent Terminal — Contexto Operativo del Agente

Terminal de investigación cuantitativa (volatilidad + gaps de apertura) con un puente
bidireccional en disco hacia un agente de IA en el IDE. Todo el proyecto se documenta y
comenta en **español**; el código y los nombres de archivo van en ASCII sin emojis.

---

## 1. Protocolo de Inicio de Sesión (OBLIGATORIO)

Antes de ejecutar cualquier acción, responder preguntas o proponer cambios:

1. Leer completa la bitácora en [docs/BITACORA.md](docs/BITACORA.md).
2. Confirmar al usuario con un resumen breve: total de hitos, último hito registrado y
   decisiones de arquitectura vigentes que afecten la sesión.
3. No proponer cambios que contradigan decisiones ya documentadas, salvo petición explícita.

Al cerrar un hito significativo durante la sesión, **agregar la fila correspondiente** a la
tabla de `docs/BITACORA.md` y documentar toda decisión de arquitectura nueva en su sección.

El reglamento completo del agente vive en [.agents/AGENTS.md](.agents/AGENTS.md) — es la
fuente de verdad; este archivo es el resumen operativo.

---

## 2. Ejecución

```bash
./run.sh          # crea .venv, instala requirements.txt y levanta el servidor
```

- Dashboard: **http://localhost:8050** (puerto configurable con `SERVER_PORT`).
- Python 3.10+. Dependencias fijadas en `requirements.txt` (pandas 3.0.3, numpy 2.5.1,
  google-genai, python-dotenv).
- `.env` opcional: sin `GEMINI_API_KEY` el dashboard funciona igual; el pipeline de
  reportes ya no depende de la API de Gemini (ver hito 47 de la bitácora).

---

## 3. Mapa Rápido del Repositorio

| Ruta | Rol |
|---|---|
| `src/config.py` | Rutas centralizadas, `SERVER_PORT`, API keys. Único lugar para rutas. |
| `src/engine.py` | Ingesta de CSV, pipelines, escritura de `estado_dashboard.json`. |
| `src/kpis.py` | Biblioteca matemática: ATR/NATR, regímenes, rachas, Markov, Hurst, Kaufman ER, Z-Score. |
| `src/server.py` | `http.server` nativo + API REST + análisis de celda/superficie. Archivo más grande (~55 KB). |
| `src/generate_analysis.py` | Generador de reportes con gráficos para el bridge. |
| `frontend/dashboard_volatilidad.html` | Dashboard monolítico Plotly.js (~220 KB, todo el JS inline). |
| `frontend/mapa_arquitectura.html` | Diagrama interactivo servido en `/architecture.html`. |
| `bridge/*.json` | Canal de sincronización con el agente (gitignored, runtime). |
| `data/*.csv` | Datos históricos. **Gitignored** (`data/` y `*.csv`). |
| `docs/ARCHITECTURE.md` | Mapa arquitectónico función por función. |
| `docs/BITACORA.md` | Ledger cronológico de hitos. |
| `docs/research/` | Marco teórico y especificaciones de los informes. |
| `docs/reports/` | Informes de volatilidad por activo, escritos a mano por el agente. |
| `tvdatafeed-skill/`, `yfinance-skill/` | Skills de extracción dual-provider. |
| `scratch/` | Scripts temporales de QA y pruebas. |

---

## 4. El Bridge (reglas críticas)

Comunicación **exclusiva por archivos JSON en `bridge/`**. Prohibido usar navegador,
`browser_subagent` o captura de pantalla para "ver" el dashboard: todas las coordenadas ya
están exportadas en disco.

**Lectura:** `antigravity_bridge_request.json` (contexto de la selección) +
`estado_dashboard.json` (activo y régimen actual).

**Escritura de la respuesta:**

- **NUNCA** escribir `antigravity_bridge_response.json` con herramientas de escritura de
  archivos: el HTML embebido en `ai_raw_text` corrompe el JSON.
- Usar `src/generate_analysis.py`, o un script Python con `json.dump()`.
- Validar siempre después:
  `python3 -c "import json; json.load(open('bridge/antigravity_bridge_response.json'))"`

**Tipos de request** (campo `type`):

| `type` | Acción | Fuentes |
|---|---|---|
| `3d_surface_interpretation` | Cruzar cima de ineficiencia con el régimen para dictar sizing y asimetría. | Solo internas |
| `gap_cell_analysis` | Z-Score + Bootstrap sobre la celda. | Solo internas |
| `asset_full_report` | Informe completo del activo. | Internas |
| *(sin `type`, con array `dates`)* | Event Study de outliers. | **Web obligatoria** |

---

## 5. Política Anti-Alucinaciones

Para cualquier Event Study, la búsqueda web se limita **exclusivamente** a: Reuters,
Bloomberg, CNBC, FT, WSJ, Investing.com, Forex Factory, bancos centrales (FED, ECB, IMF,
Banco Central de Chile), SEC Filings y transcripciones de earnings. Está prohibido inferir
motivos de un movimiento sin evidencia de estas fuentes.

---

## 6. Estilo de los Informes (`ai_raw_text` y `docs/reports/`)

Persona: **experto en estadísticas financieras y backtesting**, tono educativo y descriptivo.
Explicar el "por qué"; traducir la estadística a ideas accionables; cerrar siempre con
gestión de riesgo (qué invalida la estrategia, cuándo no operar).

Formato HTML obligatorio: `font-family: 'Inter', sans-serif`, `13px`, `line-height: 1.7`;
tres bloques exactos `// A. Diagnóstico del Patrón`, `// B. Evidencia del Backtesting`,
`// C. Conclusión Estratégica`; títulos en mayúscula `#64748b`, `11px`,
`letter-spacing: 1.2px`, `font-weight: 700`; separador
`border-bottom: 1px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 16px`.
**Cero emojis, cero SVG, cero fondos de color.** Ancho del panel lateral: 480px.

La especificación editorial de los informes de `docs/reports/` está en
[docs/research/Especificacion_Informe_Volatilidad.md](docs/research/Especificacion_Informe_Volatilidad.md).

---

## 7. Convenciones de Código y Diseño

- **Paleta:** fondo Slate Metallic Grey `#e2e7ec` / `#f1f5f9` (nunca blanco puro); heatmaps
  en escala Viridis con contraste dinámico de texto.
- **Nomenclatura cuantitativa formal:** "Errático", no "Serrucho". Sin jerga críptica.
- **Rutas:** siempre vía `src/config.py`; nunca rutas duras.
- **Datos:** las skills son stateless y reciben `--output-dir ../data` por CLI (12-Factor).
- **Frontend:** el dashboard es un único HTML con JS inline; los cambios de UI se hacen ahí.

---

## 8. Control de Versiones

**Prohibido `git push`, `pull`, `fetch`, `merge` o tocar el remoto de forma autónoma.**
Solo si el usuario lo pide textualmente ("sube los cambios", "haz push"). Los commits
locales sí se pueden hacer cuando se solicite. `data/` y `*.csv` están gitignored.

---

## 9. Estado al 2026-08-02

- **51 hitos** registrados en la bitácora, todos completados.
- Hay **trabajo local sin commitear** relevante: hitos 14–51 (matriz 7x3 Hurst/Kaufman,
  mapa de síntesis 2D animado, Z-Score con doble campana, pipeline local de reportes,
  centralización de `data/`) más los CSV de `tvdatafeed-skill/data/` borrados por la
  migración al directorio global.
- Última línea de trabajo: informes de volatilidad por activo en `docs/reports/`
  (QQQ, SP500, Ford, USDCLP, XAUUSD) generados a mano siguiendo la especificación.
- `docs/research/Informe_Prueba_USDCLP.md` tiene la primera línea corrupta (texto basura
  antes del frontmatter) — pendiente de limpiar.
- Próximo candidato de trabajo según `brainstorming_canvas.md`: **histograma de
  persistencia de regímenes** (`N_OBS`, `MEDIAN(D)`, `MAX(D)`, `HIT_RATIO`) — diseño 100%
  definido, implementación pendiente en el dashboard.
