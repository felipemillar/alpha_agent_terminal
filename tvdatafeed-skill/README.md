# TradingView Data Extractor Skill

Este paquete es una **Habilidad de Agente IA (Agent Skill)** universal, diseñada para inyectarse en cualquier sistema autónomo (Claude, ChatGPT, Cursor, Antigravity). Permite descargar datos históricos (velas) de TradingView evadiendo los bloqueos anti-bot de Cloudflare y resolviendo automáticamente los JWT requeridos para conexiones por WebSockets.

## Estructura del Paquete

- `SKILL.md`: Es el "cerebro". Contiene las instrucciones precisas para el Agente (LLM). Si estás usando ChatGPT o Claude web, copia el contenido de este archivo en el "System Prompt" o dáselo al modelo como instrucción base.
- `scripts/`: Contiene todo el código Python y la arquitectura modular. El LLM será quien orqueste su ejecución.

## Prerrequisitos (Uso Híbrido)

**Si vas a usar la habilidad mediante un Agente de IA:**
¡No necesitas hacer nada! El Agente está programado con rutinas de **Self-Healing** (Auto-Instalación). Al pedirle que extraiga datos, él mismo creará el entorno virtual aislado `.venv` y descargará las dependencias de forma silenciosa la primera vez.

**Si vas a usar la habilidad tú mismo en la consola (Modo Manual CLI):**
Debes preparar el entorno de ejecución aislando las dependencias:

1. Clonar este repositorio y navegar a su directorio (`cd tvdatafeed-skill`).
2. Crear su propio entorno virtual aislado (obligatorio para evitar conflictos con proyectos padre):
   ```bash
   python3 -m venv .venv
   ```
3. Instalar las dependencias directamente en ese entorno:
   ```bash
   .venv/bin/pip install -r requirements.txt
   ```
4. Opcional: Configura `.env` basándote en `.env.example` si quieres usar variables persistentes (útil en entornos Docker).

## Uso (Flujo del Agente)

Una vez configurado, simplemente chatea con tu Agente de IA y dile:

> *"Descarga datos de Amazon"*
> *"Descarga 2000 velas de 15 minutos para Bitcoin"*

El agente leerá su `SKILL.md`, realizará silenciosamente una búsqueda en la API de TradingView para identificar a los proveedores de liquidez disponibles (Exchanges), te lo presentará como opciones (ej. NASDAQ, XETR), y orquestará la extracción mediante `scripts/extractor.py`.

## Uso Manual (Humano en Consola)

Si no deseas usar un Agente de IA y prefieres operar la Habilidad tú mismo desde tu terminal (CLI), los scripts están diseñados para ser amigables con humanos siempre y cuando omitas el flag `--json`.

### 1. Buscar un Activo
Busca el símbolo para ver qué proveedores (exchanges) lo ofrecen.
```bash
.venv/bin/python scripts/search_symbol.py --symbol "AAPL"
```
*(Esto te devolverá una lista limpia en consola: `[NASDAQ] AAPL - Apple Inc.`, etc).*

### 2. Extraer Datos
Usa los datos de la búsqueda para ejecutar el extractor.
```bash
.venv/bin/python scripts/extractor.py --symbol "AAPL" --exchange "NASDAQ" --interval "daily" --bars "500"
```
*(El script mostrará una barra de carga y descargará el archivo CSV en la carpeta `data/`).*
