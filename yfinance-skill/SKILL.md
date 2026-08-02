---
name: yfinance-extractor
description: |
  Se activa exclusivamente cuando el usuario solicite descargar datos históricos de mercados, 
  buscar símbolos financieros (acciones, divisas, cripto), extraer data de Yahoo Finance, o mencione "bajar velas de [activo]".
author: "QRT Solutions"
version: 1.0.0
compatibility:
  os: ["linux", "darwin", "windows"]
  tools_required: ["python", "pip"]
tags: ["finance", "data-extraction", "yfinance", "yahoo"]
metadata:
  max_tokens_budget: 1500
---

# Yahoo Finance Extractor Agent Skill

Esta habilidad te permite (al Agente) orquestar de forma conversacional y autónoma la descarga de datos históricos desde Yahoo Finance. Está diseñada para usuarios sin conocimientos técnicos, por lo que **tu rol es guiar al usuario de forma amigable y sin fricciones**.

## ⚠️ GUARDRAILS DE SEGURIDAD (CRÍTICO)

1. **NUNCA** intentes adivinar el símbolo o ticker por tu cuenta. Siempre debes usar el buscador de símbolos provisto en `scripts/search_symbol.py`.
2. **NUNCA** modifiques los archivos de Python durante la ejecución de esta habilidad. Estás operando en modo *solo lectura y ejecución*.
3. **DETECCION DE OS (OBLIGATORIO):** Antes de ejecutar comandos, detecta si el usuario está en **Windows** o en **macOS/Linux**:
   - **En Windows:** Usa barra invertida `\` y la ruta `.venv\Scripts\python` y `.venv\Scripts\pip`.
   - **En macOS/Linux:** Usa barra diagonal `/` y la ruta `.venv/bin/python` y `.venv/bin/pip`.
4. **AUTO-INSTALACIÓN (SELF-HEALING):** 
   - Verifica si la carpeta `.venv` existe en el directorio de la skill (`yfinance-skill/.venv`).
   - Si no existe, créala ejecutando `python -m venv .venv` (o `python3 -m venv .venv`).
   - Si el sistema no tiene Python instalado y el comando falla, detente de inmediato y explícale amigablemente al usuario cómo instalar Python en su sistema operativo.
   - Instala las dependencias necesarias ejecutando `pip install -r requirements.txt` (usando el ejecutable de pip dentro de `.venv`).

---

## Flujo de Ejecución Determinista

Sigue estrictamente esta secuencia paso a paso. No te saltes ningún paso.

### Paso 1: Identificar el Término de Búsqueda
Extrae el nombre del activo o símbolo del mensaje del usuario (ej. `Tesla`, `AAPL`, `Bitcoin`, `USDCLP`).

### Paso 2: Búsqueda de Proveedores
Asegúrate de que tu Directorio de Trabajo Actual (CWD) sea la raíz de la skill (`yfinance-skill`). Ejecuta el script de búsqueda:
- **OBLIGATORIO:** Añade siempre el flag `--json` para recibir un JSON estructurado.
- **Comando (macOS/Linux):** `.venv/bin/python scripts/search_symbol.py --symbol "[TÉRMINO]" --json`
- **Comando (Windows):** `.venv\Scripts\python scripts/search_symbol.py --symbol "[TÉRMINO]" --json`

**Manejo de Errores:**
- Si el comando falla porque faltan dependencias, ejecuta la auto-instalación (Paso 4 de Guardrails) e intenta nuevamente.
- Si el comando devuelve una lista vacía o un error de red: Notifica al usuario con un bloque `> [!WARNING]` y pídele que proporcione otro término.

### Paso 3: Puerta de Seguridad HITL (Human-in-the-Loop)
Presenta las opciones devueltas al usuario usando la herramienta interactiva (ej. `ask_question`).
- **Opciones:** En formato `[EXCHANGE] SYMBOL - Name (Type)`. Ejemplo: `[NMS] TSLA - Tesla, Inc. (EQUITY)`
- **Parámetros Obligatorios:** Pídele al usuario el intervalo y la cantidad de barras (o periodo) si no los especificó. Indícale que use la opción "Other" o similar para ingresarlos (ej. `Diario, 500 velas`).

### Paso 4: Ejecutar la Extracción
Una vez que el usuario confirme los parámetros, ejecuta el extractor:
- **Comando (macOS/Linux):** `.venv/bin/python scripts/extractor.py --symbol "[SYMBOL]" --interval "[INTERVAL]" --bars "[BARS]" --output-dir "../data" --json`
- **Comando (Windows):** `.venv\Scripts\python scripts/extractor.py --symbol "[SYMBOL]" --interval "[INTERVAL]" --bars "[BARS]" --output-dir "..\data" --json`

**Manejo de Errores:**
- Si el comando falla (por timeout, símbolo deslistado, u otro error): Notifica al usuario usando `> [!ERROR]` y muéstrale el mensaje de error o las últimas líneas del archivo de log de forma amigable.

### Paso 5: Reportar Resultados (UI/UX)
Responde al usuario confirmando el éxito:
- Usa el bloque `> [!NOTE]` de GitHub Alerts.
- Proporciona un enlace Markdown (`file://`) al archivo CSV generado en la carpeta `data/`.
- Usa una Tabla de Markdown para mostrar una muestra de los datos devueltos.

---

## Evaluación y Testing (EFD)
Si se modifica el código de la skill, valida que los tests pasen en verde:
- **macOS/Linux:** `.venv/bin/python -m pytest evals/test_cli_smoke.py -v`
- **Windows:** `.venv\Scripts\python -m pytest evals\test_cli_smoke.py -v`
