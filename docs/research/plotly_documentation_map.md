# Mapa y Guía de Documentación Oficial de Plotly

Esta guía sirve como punto de acceso unificado a toda la documentación de Plotly, tanto para **Python (Plotly.py)** como para **JavaScript (Plotly.js)**. Se organiza en función de los flujos de trabajo habituales de visualización y personalización de dashboards interactivos.

---

## 🌐 Recursos Oficiales Principales

*   **Plotly Python:** [https://plotly.com/python/](https://plotly.com/python/) — Biblioteca de graficación interactiva de nivel profesional para Python.
*   **Plotly JavaScript:** [https://plotly.com/javascript/](https://plotly.com/javascript/) — La base de visualización que impulsa las versiones de Python y R, ideal para dashboards basados en HTML estático o dinámico.
*   **Dash (Framework Web):** [https://dash.plotly.com/](https://dash.plotly.com/) — Framework para crear aplicaciones analíticas web reactivas en Python puro sin necesidad de escribir JavaScript.
*   **Repositorios de Código Abierto (GitHub):**
    *   [Plotly.py en GitHub](https://github.com/plotly/plotly.py)
    *   [Plotly.js en GitHub](https://github.com/plotly/plotly.js)

---

## 🐍 1. Documentación de Plotly para Python (Plotly.py)

La biblioteca de Python se estructura en dos subinterfaces principales para crear figuras:

### A. Plotly Express (`plotly.express` o `px`)
Es la API de alto nivel recomendada para la creación ágil de gráficos estándar con una sola línea de código. Maneja de manera automática la estructuración del layout y el mapeo de colores.
*   **Guía y Ejemplos de Plotly Express:** [https://plotly.com/python/plotly-express/](https://plotly.com/python/plotly-express/)
*   **Tipos de Gráficos Comunes:** Scatter, Line, Bar, Histograms, Box, Violin, etc.

### B. Graph Objects (`plotly.graph_objects` o `go`)
Es la API de bajo nivel. Otorga un control quirúrgico sobre cada elemento de la figura. Es ideal para crear combinaciones complejas de trazas (*subplots*), geometrías personalizadas y lógicas de datos sofisticadas.
*   **Guía de Graph Objects:** [https://plotly.com/python/graph-objects/](https://plotly.com/python/graph-objects/)
*   **Referencia de API de Figuras (Completa):** [https://plotly.com/python/reference/index/](https://plotly.com/python/reference/index/) *(Esencial para buscar atributos exactos de layout o marker).*

### C. Personalización de Diseño y Plantillas (Themes / Templates)
Plotly utiliza **Templates** para definir la apariencia global (tipografías, grillas, paletas de colores) de los gráficos.
*   **Documentación de Templates y Temas:** [https://plotly.com/python/templates/](https://plotly.com/python/templates/)
*   **Templates Incorporados:** `plotly`, `plotly_white` *(diseño minimalista y limpio)*, `plotly_dark` *(modo oscuro)*, `ggplot`, `seaborn`, `simple_white`, `none`.
*   **Ejemplo rápido para registrar un tema personalizado:**
    ```python
    import plotly.graph_objects as go
    import plotly.io as pio

    # Definir la estructura base
    tema_personalizado = go.layout.Template(
        layout=dict(
            font=dict(family="Inter, sans-serif", size=14, color="#333333"),
            paper_bgcolor="#FAFAFA",
            plot_bgcolor="#FFFFFF",
            xaxis=dict(gridcolor="#E5E5E5", zeroline=False),
            yaxis=dict(gridcolor="#E5E5E5", zeroline=False)
        )
    )
    # Registrar e implementar
    pio.templates["mi_tema_corporate"] = tema_personalizado
    pio.templates.default = "mi_tema_corporate"
    ```

### D. Visualización de Volatilidad y Gráficos Financieros
Para análisis técnico, trading y volatilidad cuantitativa:
*   **Gráficos Candlestick (Velas):** [https://plotly.com/python/candlestick-charts/](https://plotly.com/python/candlestick-charts/)
*   **Gráficos OHLC (Open-High-Low-Close):** [https://plotly.com/python/ohlc-charts/](https://plotly.com/python/ohlc-charts/)
*   **Indicadores de Dispersión / Tendencia (Scatter):** [https://plotly.com/python/line-and-scatter/](https://plotly.com/python/line-and-scatter/)

---

## ☕ 2. Documentación de Plotly para JavaScript (Plotly.js)

Cuando exportas gráficos a páginas web o escribes interactividad dinámica directamente en el navegador (`.html` + `.js`).

### A. Uso básico mediante CDN
Importa la biblioteca oficial en tu documento HTML:
```html
<script src="https://cdn.plot.ly/plotly-2.35.0.min.js" charset="utf-8"></script>
```

### B. Inicialización en DOM
*   **Estructura fundamental:**
    ```javascript
    var trace1 = {
      x: [1, 2, 3, 4],
      y: [10, 15, 13, 17],
      type: 'scatter',
      mode: 'markers'
    };

    var data = [trace1];

    var layout = {
      title: 'Mi Gráfico en JS',
      font: { family: 'Inter, sans-serif' }
    };

    Plotly.newPlot('miDivGrafico', data, layout, {responsive: true});
    ```
*   **Configuración del Gráfico (Interactividad / Modo):** [https://plotly.com/javascript/configuration-options/](https://plotly.com/javascript/configuration-options/) *(Permite ocultar/mostrar el menú superior "Modebar", configurar marcas de agua, y habilitar scroll-zoom).*

### C. Actualizaciones Dinámicas y Rendimiento
Para cambiar el aspecto de la gráfica de manera fluida sin recrear el objeto desde cero (ideal para responder a selectores o inputs del usuario):
*   **Plotly.restyle:** Actualiza los datos y configuraciones de las trazas gráficas.
    ```javascript
    // Cambia el color de la primera traza a azul
    Plotly.restyle('miDivGrafico', 'marker.color', 'blue', [0]);
    ```
*   **Plotly.relayout:** Actualiza las propiedades del diseño (márgenes, títulos, ejes, fondos, rangos temporales).
    ```javascript
    // Cambia el título de la gráfica dinámicamente
    Plotly.relayout('miDivGrafico', {title: 'Nuevo Título del Eje X'});
    ```
*   **Guía de API de funciones y métodos en JS:** [https://plotly.com/javascript/plotlyjs-function-reference/](https://plotly.com/javascript/plotlyjs-function-reference/)

### D. Captura de Eventos del Usuario
Permite ejecutar código JS personalizado (como mostrar tablas, alertas o modificar otros elementos del dashboard) en respuesta a las acciones del usuario en el gráfico:
*   **Eventos Disponibles:** `plotly_click`, `plotly_hover`, `plotly_unhover`, `plotly_selected`, `plotly_relayout`.
*   **Documentación de Eventos en JS:** [https://plotly.com/javascript/hover-events/](https://plotly.com/javascript/hover-events/)
    ```javascript
    var myPlot = document.getElementById('miDivGrafico');
    myPlot.on('plotly_click', function(data){
        var pts = '';
        for(var i=0; i < data.points.length; i++){
            pts = 'x = '+data.points[i].x +'\ny = '+data.points[i].y;
        }
        alert('Hiciste clic en el punto:\n\n'+pts);
    });
    ```

---

## 💡 Recursos de Referencia Rápida para el Proyecto

1.  **¿Cómo incrustar un gráfico de Python en HTML?:**
    *   Puedes exportar tus figuras de Python directamente como código HTML parcial utilizando:
        ```python
        import plotly.io as pio
        # Devuelve solo el tag <div> y la lógica <script> para insertarlo limpiamente en tu plantilla HTML
        div_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
        ```
2.  **Combinar estilos CSS y Fuentes Google:**
    *   Asegúrate de importar fuentes modernas (como *Inter* u *Outfit*) en la cabecera de tus HTML y configurarlas en el Layout del gráfico:
        ```html
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        ```
