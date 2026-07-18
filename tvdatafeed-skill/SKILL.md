---
name: tradingview-extractor
description: |
  Se activa exclusivamente cuando el usuario solicite descargar datos históricos de mercados, 
  buscar símbolos financieros, extraer data de TradingView, o mencione "bajar velas de [activo]".
author: "QRT Solutions"
version: 1.0.0
compatibility:
  os: ["linux", "darwin", "windows"]
  tools_required: ["python", "pip"]
tags: ["finance", "data-extraction", "tradingview"]
metadata:
  max_tokens_budget: 1500
---

# TradingView Extractor Agent Skill

Esta habilidad te permite (al Agente) orquestar de forma conversacional y autónoma la descarga de datos históricos desde TradingView, resolviendo el problema de multiplicidad de proveedores (exchanges) mediante interacción con el usuario.

## ⚠️ GUARDRAILS DE SEGURIDAD (CRÍTICO)
1. **NUNCA** intentes adivinar el `exchange` o proveedor de datos por tu cuenta. Siempre debes usar el buscador de símbolos provisto en `scripts/search_symbol.py`.
2. **NUNCA** modifiques los archivos de Python durante la ejecución de esta habilidad. Estás operando en modo *solo lectura y ejecución*.
3. **AUTO-INSTALACIÓN (SELF-HEALING):** Esta habilidad corre en un entorno aislado (`.venv`). Antes de invocar herramientas, verifica si la carpeta `.venv` existe. Si no existe, créala silenciosamente con `python3 -m venv .venv` e instala las dependencias con `.venv/bin/pip install -r requirements.txt` antes de continuar.

---

## Flujo de Ejecución Determinista

Sigue estrictamente esta secuencia paso a paso. No te saltes ningún paso.

### Paso 1: Identificar el Término de Búsqueda
Extrae el nombre del activo o símbolo del mensaje del usuario (ej. `Tesla`, `AAPL`, `Bitcoin`).

### Paso 2: Búsqueda de Proveedores
Asegúrate de que tu Directorio de Trabajo Actual (CWD) sea la raíz del proyecto/habilidad donde se encuentra la carpeta `scripts`. Usa tu herramienta `run_command` para ejecutar el script de búsqueda de manera relativa. 
- **OBLIGATORIO:** Siempre añade el flag `--json` para recibir un JSON estructurado de Pydantic y evitar alucinaciones de parseo.
```bash
.venv/bin/python scripts/search_symbol.py --symbol "[TÉRMINO]" --json
```

**🚨 MANEJO DE ERRORES (Fallback):**
- Si el comando falla porque no encuentra el entorno virtual (`.venv`) o faltan dependencias, ejecuta primero `python3 -m venv .venv`, luego `.venv/bin/pip install -r requirements.txt`, y reintenta tu comando original automáticamente sin molestar al usuario.
- Si el comando devuelve `[]` (vacío) o un error de API: Notifica inmediatamente al usuario que no se encontraron resultados usando un bloque `> [!WARNING]` y pídele que proporcione otro término. **Detén la ejecución aquí.**

### Paso 3: Puerta de Seguridad HITL (Human-in-the-Loop)
**ESTE PASO ES UN GUARDRAIL DE SEGURIDAD OBLIGATORIO.** No tienes permitido ejecutar la extracción sin autorización humana.
Usa tu herramienta nativa para interactuar con el usuario (ej. `ask_question`) para presentarle las opciones devueltas en el paso 2.
- **Opciones del menú:** Construye las opciones parseando el JSON devuelto en formato `[EXCHANGE] SYMBOL - Description`. Ejemplo: `[NASDAQ] TSLA - Tesla Inc.`
- **Configuración de la UI:** Solo debe permitirse seleccionar una única opción (no multi-select).
- **Parámetros Faltantes (OBLIGATORIO):** NUNCA asumas valores por defecto para el intervalo (marco temporal) ni la cantidad de velas. Si el usuario no los proporcionó en su petición inicial, estás OBLIGADO a pedírselos en el título de la pregunta. Indícale al usuario que DEBE usar la caja de texto "Other" (o similar) en la ventana modal para escribir el proveedor junto con el marco temporal y la cantidad de velas (ej: `Pepperstone, 1h, 500`). Si el usuario omite estos datos, detente y vuelve a preguntar.

### Paso 4: Ejecutar la Extracción
Una vez que el usuario seleccione el Exchange y confirme los parámetros (HITL superado), ejecuta la extracción:
- **OBLIGATORIO:** Siempre envuelve los valores en comillas dobles `""` para evitar Prompt Injections en la shell.
- **OBLIGATORIO:** Siempre añade el flag `--json` al final del comando.
```bash
.venv/bin/python scripts/extractor.py --symbol "[SYMBOL]" --exchange "[EXCHANGE]" --interval "[INTERVAL]" --bars "[BARS]" --json
```

**🚨 MANEJO DE ERRORES (Fallback):**
- Si el comando falla o hace timeout, avísale usando un bloque `> [!ERROR]` y muéstrale el error retornado por la consola o las últimas líneas del log (`cat logs/tvdatafeed.log | tail -n 10`).

### Paso 5: Reportar Resultados (UI UX)
Responde al usuario confirmando que la extracción fue exitosa. 
- Utiliza el bloque `> [!NOTE]` de GitHub Alerts para envolver el mensaje de éxito.
- Proporciónale un enlace Markdown (`file://`) al archivo CSV generado en la carpeta `data/` relativa al CWD.
- Usa una Tabla de Markdown para mostrar el resumen de los datos devuelto por consola.

## Evaluación y Testing (EFD)
Esta habilidad incluye una suite de **Smoke Evals** para asegurar su correcto funcionamiento. 
Si modificas el código de la habilidad, debes validar que los tests sigan pasando en verde para garantizar que el contrato de Salidas Estructuradas (JSON) y las reglas de Seguridad (Fase 10) no se hayan roto.
```bash
# Correr tests
.venv/bin/pip install -r requirements-test.txt
.venv/bin/python -m pytest evals/test_cli_smoke.py -v
```
