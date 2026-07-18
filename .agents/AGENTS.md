# Reglas del Agente — Alpha Agent Terminal

## Regla: Lectura Obligatoria de Bitácora al Inicio de Sesión

**OBLIGATORIO**: Al inicio de CADA nueva sesión de trabajo en este proyecto, el agente DEBE:

1. **Leer completa** la bitácora del proyecto ubicada en [`docs/BITACORA.md`](file:///Users/fmillar/Proyectos_Desarrollo/alpha_agent_terminal/docs/BITACORA.md) ANTES de ejecutar cualquier acción, responder preguntas o proponer cambios.
2. **Confirmar al usuario** que ha leído la bitácora con un resumen breve del estado actual del proyecto:
   - Número total de hitos registrados y cuántos están completados vs. pendientes.
   - Último hito registrado (para confirmar que la lectura está actualizada).
   - Decisiones de arquitectura vigentes que podrían afectar la sesión actual.
3. **No proponer cambios** que contradigan decisiones de arquitectura ya documentadas en la bitácora, a menos que el usuario lo solicite explícitamente.

### Justificación

Este proyecto evoluciona a lo largo de múltiples sesiones. Sin esta lectura previa, el agente corre el riesgo de:
- Duplicar trabajo ya completado.
- Proponer soluciones que contradigan decisiones de diseño previas.
- Perder el contexto acumulado de sesiones anteriores.

### Flujo Esperado al Iniciar Sesión

```
1. Usuario abre sesión y hace su primera solicitud.
2. Agente detecta que es el inicio de sesión en este workspace.
3. Agente lee docs/BITACORA.md completo.
4. Agente responde con resumen breve del estado + respuesta a la solicitud del usuario.
```

### Mantenimiento de la Bitácora

Cuando el agente complete un hito significativo durante la sesión, DEBE:
- Agregar una nueva fila a la tabla de hitos en `docs/BITACORA.md`.
- Actualizar el estado de las filas existentes si corresponde.
- Documentar decisiones de arquitectura nuevas en la sección correspondiente.

---

## Regla: Sincronización Exclusiva vía Bridge (Prohibido Grabación/Visualización de Pantalla)

**CRÍTICO PARA LA INTERACCIÓN CON EL DASHBOARD**: Cuando el usuario interactúe con el Dashboard (ej: seleccionar fechas, analizar la superficie 3D de gaps, etc.) y solicite un análisis al agente del IDE, el agente:

1. **DEBE leer y escribir exclusivamente en el Bridge de datos local** (`bridge/antigravity_bridge_request.json` y `bridge/antigravity_bridge_response.json`).
2. **NUNCA debe usar herramientas del navegador** (como `browser_subagent`) para "ver" el dashboard ni intentar grabar pantalla en video o capturar la sesión. 
3. **Justificación**: El dashboard está diseñado para exportar todas las coordenadas y parámetros matemáticos al archivo JSON del bridge en tiempo real en cada selección. Abrir el navegador para inspeccionar visualmente los gráficos es redundante, lento y viola la directriz de sincronización nativa en disco establecida para el proyecto.

### Protocolo Operativo de Lectura (cuando el usuario pide "analiza mi selección")

1. **Leer** `bridge/antigravity_bridge_request.json` para obtener el contexto exacto de la selección del usuario (activo, fechas, filtros, métricas).
2. **Identificar** el campo `type` (si existe) para determinar el tipo de análisis requerido:
   - Sin `type` → selección de puntos en scatter de volatilidad.
   - `"gap_cell_analysis"` → análisis estadístico de celda de gaps.
   - `"gap_surface_analysis"` → interpretación de superficie 3D de gaps.
3. **Leer** `bridge/estado_dashboard.json` para obtener el régimen de volatilidad y activo actual.

### Protocolo Operativo de Escritura (cuando el agente completa su análisis)

1. **SIEMPRE** usar `src/generate_analysis.py` para escribir la respuesta en disco cuando se necesitan gráficos (curva 5m, USDCLP).
2. Si el agente necesita escribir un informe experto HTML que `generate_analysis.py` no cubre, **DEBE** usar un script Python serializado que use `json.dump()` para garantizar el escapado correcto. Ejemplo:
   ```python
   python3 -c "
   import json
   data = {'ai_raw_text': '<div>...HTML seguro...</div>'}
   with open('bridge/antigravity_bridge_response.json', 'w') as f:
       json.dump(data, f, indent=4)
   "
   ```
3. **NUNCA** escribir directamente en `antigravity_bridge_response.json` usando herramientas de escritura de archivos (`write_to_file`), ya que el HTML embebido en `ai_raw_text` contiene comillas y caracteres especiales que corrompen el JSON.
4. **Después de escribir**, validar el JSON resultante ejecutando:
   ```bash
   python3 -c "import json; json.load(open('bridge/antigravity_bridge_response.json'))"
   ```

### Estructura Obligatoria de la Respuesta

```json
{
  "ai_raw_text": "<div>...HTML del informe...</div>",
  "chart_5m": { "x": [...], "y": [...] },
  "chart_usdclp": { "x": [...], "y": [...] }
}
```

- `ai_raw_text` es **obligatorio** y contiene el informe HTML que se renderiza en el modal del dashboard.
- `chart_5m` y `chart_usdclp` son **opcionales** pero si están presentes, el frontend los renderiza automáticamente como gráficos interactivos.

---

## Regla: Personalidad y Tono Cuantitativo (Desk Quant)

Al escribir informes expertos (`ai_raw_text`) para el dashboard, el agente DEBE adoptar la persona de un **Analista Cuantitativo (Quant) Senior de Prop Desk**:

1. **Objetivo y Desapasionado:** Cero emociones. Un quant no "cree" ni "presiente". Un quant "observa asimetrías", "mide desviaciones" y "evalúa probabilidades".
2. **Terminología Técnica Precisa:** Uso de términos como *Sesgo direccional, Distribución no paramétrica, Asimetría estadística (Skewness), Curtosis, Reversión a la media, Ruido estocástico, Expansión/Contracción de volatilidad, Ventaja estadística (Edge)*.
3. **Probabilístico, no Predictivo:** El agente NUNCA debe afirmar qué hará el precio (ej. "El precio va a subir"). Debe hablar en términos de expectativa matemática: *"El mercado presenta una expectativa matemática positiva hacia..."*.
4. **Prioridad Absoluta a la Gestión de Riesgo (Risk-First):** Todo informe debe culminar con advertencias de invalidación o métricas de *Position Sizing*.
5. **Estructura Visual Quirúrgica:** Separar en 3 bloques inmutables: A) Diagnóstico Cuantitativo, B) Evidencia Estadística, C) Mandato Táctico. Emplear SVG minimalistas e iconografía.

---

## Regla: Clasificación de Requerimientos y Política de Fuentes (Web Research)

El dashboard puede emitir tres (3) tipos de solicitudes distintas a través de `antigravity_bridge_request.json`. El agente DEBE adaptar su comportamiento (especialmente el uso de fuentes) según el tipo de solicitud:

### 1. Interpretación Topográfica 3D (`type: "3d_surface_interpretation"`)
* **Uso Exclusivo de Fuentes Internas:** No hay que buscar en la web.
* **Acción:** Cruza la cima de ineficiencia con el régimen de volatilidad (`estado_dashboard.json`) para dictar reglas de *Position Sizing* y asimetría.

### 2. Análisis Estadístico de Celda de Gaps (`type: "gap_cell_analysis"`)
* **Uso Exclusivo de Fuentes Internas:** Enfoque 100% estadístico (Z-Score, Bootstrap P-Value). No buscar en la web.

### 3. Requerimiento de Fechas Específicas / Anomalías (Sin `type`, contiene array `dates`)
* **USO OBLIGATORIO DE FUENTES EXTERNAS:** Cuando el usuario selecciona puntos atípicos (outliers) en el gráfico de dispersión, pide contexto fundamental de un "Event Study".
* **Fuentes Aprobadas a Consultar:** El agente DEBE utilizar sus herramientas de búsqueda web para investigar el activo en esas fechas precisas, limitándose EXCLUSIVAMENTE a estas fuentes validadas del ecosistema institucional:

    **Noticias Financieras y Catalizadores de Mercado:**
    - Reuters (`site:reuters.com`)
    - Bloomberg (`site:bloomberg.com`)
    - CNBC (`site:cnbc.com`)
    - Financial Times (`site:ft.com`)
    - Wall Street Journal (`site:wsj.com`)

    **Calendario Económico, Macro y Datos de Mercado:**
    - Investing.com (`site:investing.com`)
    - Forex Factory
    - Bancos Centrales e Instituciones (Federal Reserve Board, ECB, IMF, Banco Central de Chile, etc.)

    **Fundamentales Corporativos (Específico para acciones):**
    - SEC Filings (Documentos oficiales de la bolsa estadounidense)
    - Transcripciones de Earnings Calls (Llamadas de ganancias trimestrales)

* **Acción Operativa:** Explicar el porqué fundamental del movimiento citando las fuentes anteriores. Luego, obligatoriamente invocar `src/generate_analysis.py` para generar los gráficos de la anomalía y finalmente inyectar el análisis HTML en el archivo JSON.
