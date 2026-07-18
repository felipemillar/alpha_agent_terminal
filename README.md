# Alpha Agent Terminal — Quantitative Research Desk

Terminal de investigacion cuantitativa para analisis de volatilidad y gaps de apertura, con puente bidireccional a un agente de IA en el IDE.

---

## Requisitos

- **Python 3.10+**
- Navegador moderno (Chrome, Firefox, Safari)

## Inicio Rapido

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/alpha-agent-terminal.git
cd alpha-agent-terminal

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu GEMINI_API_KEY (ver https://aistudio.google.com/apikey)

# 3. Ejecutar
chmod +x run.sh
./run.sh
```

El script `run.sh` automaticamente:
1. Crea un entorno virtual Python (`.venv/`)
2. Instala las dependencias desde `requirements.txt`
3. Inicia el servidor en **http://localhost:8050**

> **Nota:** Si no configuras `GEMINI_API_KEY`, el dashboard funciona normalmente pero los reportes del agente IA no estaran disponibles.

---

## Estructura del Repositorio

```
alpha_agent_terminal/
├── .env.example          # Template de variables de entorno
├── .gitignore            # Exclusiones para Git
├── requirements.txt      # Dependencias Python (versiones fijadas)
├── run.sh                # Script de arranque autocontenido
├── README.md
│
├── src/                  # Backend Python
│   ├── config.py         # Configuracion centralizada (rutas, puerto, API keys)
│   ├── server.py         # Servidor HTTP y API REST
│   ├── engine.py         # Motor de ingesta de datos y pipeline de calculo
│   ├── kpis.py           # Biblioteca matematica (ATR, NATR, Markov, rachas)
│   └── generate_analysis.py  # Generador de reportes cuantitativos
│
├── frontend/             # Interfaz de usuario
│   ├── dashboard_volatilidad.html  # Dashboard principal (Plotly.js)
│   ├── mapa_arquitectura.html      # Diagrama de arquitectura interactivo
│   ├── examples_heatmaps.html      # Comparaciones de paletas
│   ├── examples_gaps_designs.html  # Layouts experimentales
│   └── assets/           # Logos e imagenes
│
├── bridge/               # Canal de comunicacion con el agente IA (JSON en disco)
│   ├── .gitkeep
│   ├── estado_dashboard.json             # (runtime) Activo seleccionado
│   ├── antigravity_bridge_request.json   # (runtime) Peticion de analisis 3D
│   └── antigravity_bridge_response.json  # (runtime) Respuesta del agente
│
├── tvdatafeed-skill/     # Skill de descarga de datos de TradingView
│   ├── data/             # Archivos CSV historicos por activo
│   ├── scripts/          # Scripts de extraccion
│   └── ...
│
└── docs/                 # Documentacion tecnica
    ├── ARCHITECTURE.md   # Mapa arquitectonico completo
    ├── BITACORA.md       # Registro cronologico de desarrollo
    └── research/         # Investigacion y transcripciones
```

---

## Endpoints de la API

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/` | Dashboard principal |
| GET | `/architecture.html` | Mapa de arquitectura |
| GET | `/api/assets` | Lista de activos disponibles |
| GET | `/api/volatility?asset=X` | Serie temporal y metricas de volatilidad |
| GET | `/api/streaks?asset=X&regime=Y` | Rachas de volatilidad |
| GET | `/api/markov?asset=X` | Matriz de transicion de Markov |
| GET | `/api/gaps?asset=X` | Analisis estadistico de gaps de apertura |
| POST | `/api/gaps/analyze_cell` | Inferencia Z-test + Bootstrap sobre celda de heatmap |
| POST | `/api/gaps/analyze_surface` | Analisis topografico 3D + confluencias |
| POST | `/api/agent/analyze` | Enviar puntos al bridge para el agente IA |
| GET | `/api/agent/read_bridge` | Leer respuesta del agente IA |

---

## Sincronizacion con el Agente (IDE)

1. En el Dashboard, selecciona tu activo (ej: `QQQ_NASDAQ` o `USDCLP_PEPPERSTONE`).
2. Ve al panel de la **Superficie de Probabilidad 3D** y presiona **Interpretar**.
3. El panel lateral muestra el veredicto operativo, la narrativa guiada y los datos tecnicos.
4. Para analisis avanzado, pidele a Antigravity en tu IDE:
   > *"Analiza la superficie 3D de QQQ_NASDAQ"*
5. Haz clic en **Leer Informe Antigravity** en el panel lateral del navegador.

> [!IMPORTANT]
> **Para Agentes de IA**: Este repositorio utiliza un canal de sincronización física en disco localizado en `bridge/`. Toda la información seleccionada por el usuario en el dashboard es exportada en tiempo real a `bridge/antigravity_bridge_request.json` y `bridge/estado_dashboard.json`. Los agentes **deben leer estas peticiones directamente del disco** y responder escribiendo en `bridge/antigravity_bridge_response.json`. **No deben** abrir navegadores secundarios (como `browser_subagent`) ni intentar grabar o capturar la pantalla.
> 
> **Atención**: Existe un estricto protocolo de escritura detallado en `.agents/AGENTS.md`. NUNCA se debe usar la herramienta genérica `write_to_file` directamente sobre el response JSON debido a riesgos de corrupción por HTML anidado.
>
> **Política Anti-Alucinaciones**: Todo *Event Study* o investigación web para buscar catalizadores de volatilidad debe limitarse EXCLUSIVAMENTE al ecosistema de fuentes institucionales (Bloomberg, Reuters, SEC Filings, Forex Factory, Investing.com) configurado en `.agents/AGENTS.md`. Queda estrictamente prohibido que el agente infiera motivos sin evidencia de estas plataformas.

---

## Documentacion

- [Arquitectura Completa](docs/ARCHITECTURE.md)
- [Bitacora de Desarrollo](docs/BITACORA.md)

## Licencia

Uso privado. Todos los derechos reservados.
