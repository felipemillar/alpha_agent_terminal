---
name: tradingview-extractor
description: |
  Se activa exclusivamente cuando el usuario solicite descargar datos históricos de mercados, 
  buscar símbolos financieros, extraer data de TradingView, o mencione "bajar velas de [activo]".
author: "QRT Solutions"
version: 1.1.0
compatibility:
  os: ["linux", "darwin", "windows"]
  tools_required: ["python", "pip"]
tags: ["finance", "data-extraction", "tradingview"]
metadata:
  max_tokens_budget: 1500
---

# TradingView Extractor Agent Skill

Esta habilidad te permite (al Agente) orquestar de forma conversacional y autónoma la descarga de datos históricos desde TradingView, resolviendo el problema de multiplicidad de proveedores (exchanges) y de autenticación local mediante interacción dinámica con el usuario.

## ⚠️ GUARDRAILS DE SEGURIDAD (CRÍTICO)

1. **NUNCA** intentes adivinar el `exchange` o proveedor de datos por tu cuenta. Siempre debes usar el buscador de símbolos provisto en `scripts/search_symbol.py`.
2. **NUNCA** modifiques los archivos de Python durante la ejecución de esta habilidad. Estás operando en modo *solo lectura y ejecución*.
3. **DETECCION DE OS (OBLIGATORIO):** Antes de ejecutar comandos, detecta si el usuario está en **Windows** o en **macOS/Linux**:
   - **En Windows:** Usa barra invertida `\` y la ruta `.venv\Scripts\python` y `.venv\Scripts\pip`.
   - **En macOS/Linux:** Usa barra diagonal `/` y la ruta `.venv/bin/python` y `.venv/bin/pip`.
4. **AUTO-INSTALACIÓN (SELF-HEALING):** 
   - Verifica si la carpeta `.venv` existe en el directorio de la skill.
   - Si no existe, créala ejecutando `python -m venv .venv` (o `python3 -m venv .venv`).
   - Si el sistema no tiene Python instalado y el comando falla, detente de inmediato y explícale amigablemente al usuario cómo instalar Python en su sistema operativo.
   - Instala las dependencias necesarias ejecutando `pip install -r requirements.txt` (usando el ejecutable de pip dentro de `.venv`).

---

## Flujo de Ejecución Determinista

Sigue estrictamente esta secuencia paso a paso. No te saltes ningún paso.

### Paso 1: Identificar el Término de Búsqueda
Extrae el nombre del activo o símbolo del mensaje del usuario (ej. `Tesla`, `AAPL`, `Bitcoin`).

### Paso 2: Búsqueda de Proveedores
Asegúrate de que tu Directorio de Trabajo Actual (CWD) sea la raíz de la skill. Ejecuta el script de búsqueda:
- **OBLIGATORIO:** Añade siempre el flag `--json` para recibir un JSON estructurado.
- **Comando (macOS/Linux):** `.venv/bin/python scripts/search_symbol.py --symbol "[TÉRMINO]" --json`
- **Comando (Windows):** `.venv\Scripts\python scripts/search_symbol.py --symbol "[TÉRMINO]" --json`

**Manejo de Errores:**
- Si el comando falla porque faltan dependencias, ejecuta la auto-instalación (Paso 3 de Guardrails) e intenta nuevamente.
- Si el comando devuelve una lista vacía o un error de API: Notifica al usuario con un bloque `> [!WARNING]` y pídele que proporcione otro término.

### Paso 3: Puerta de Seguridad HITL (Human-in-the-Loop)
Presenta las opciones devueltas al usuario usando la herramienta interactiva (ej. `ask_question`).
- **Opciones:** En formato `[EXCHANGE] SYMBOL - Description`. Ejemplo: `[NASDAQ] TSLA - Tesla Inc.`
- **Parámetros Obligatorios:** Pídele al usuario el intervalo y la cantidad de barras si no los especificó. Indícale que use la opción "Other" o similar para ingresarlos (ej. `Pepperstone, 1h, 500`).

### Paso 4: Ejecutar la Extracción
Una vez que el usuario confirme los parámetros, ejecuta el extractor:
- **Comando (macOS/Linux):** `.venv/bin/python scripts/extractor.py --symbol "[SYMBOL]" --exchange "[EXCHANGE]" --interval "[INTERVAL]" --bars "[BARS]" --json`
- **Comando (Windows):** `.venv\Scripts\python scripts/extractor.py --symbol "[SYMBOL]" --exchange "[EXCHANGE]" --interval "[INTERVAL]" --bars "[BARS]" --json`

**Manejo de Autenticación y Errores (CRÍTICO):**
- Si el comando falla y el JSON de salida contiene `error_type: "AUTH_REQUIRED"`, **significa que no hay sesión activa de TradingView extraible localmente**:
  1. Detén la ejecución.
  2. Escribe al usuario en el chat con tono amigable y explícale la situación:
     > *"No he podido extraer automáticamente tu sesión de TradingView. Para resolverlo sin necesidad de copiar o pegar nada, por favor abre **Microsoft Edge** o **Firefox** en tu computadora, ingresa a `tradingview.com` e inicia sesión. Una vez que lo hayas hecho, avísame aquí en el chat para reintentar la descarga automáticamente."*
  3. Espera a que el usuario te responda confirmando que inició sesión.
  4. Ejecuta de nuevo el comando de extracción inmediatamente.
- Si el comando falla por cualquier otro error o hace timeout: Notifica al usuario usando `> [!ERROR]` y muéstrale el mensaje de error o las últimas líneas del archivo de log.

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
