# Bitacora de Desarrollo — Alpha Agent Terminal

Este documento registra cronologicamente las solicitudes del usuario, los hitos alcanzados y las decisiones de diseno tomadas durante el desarrollo del proyecto.

## Historial de Solicitudes y Hitos de Desarrollo

| N | Solicitud / Requerimiento | Hito / Solucion Implementada | Estado | Archivo Relacionado |
| :---: | :--- | :--- | :---: | :--- |
| 1 | Estructuracion inicial y API local | Creacion de un servidor API local en Python para servir HTML estatico y evitar problemas de CORS. | **Completado** | `src/server.py` |
| 2 | Grafico de 5 anos e Historial | Filtros de fecha dinamicos usando offsets de Pandas para visualizar 5 anos de datos en los graficos de Plotly. | **Completado** | `src/engine.py` |
| 3 | Analisis de Rachas e Inferencia | Motor inferencial para analizar rachas de volatilidad baja, incluyendo Z-Score, pruebas de hipotesis y bootstrap Monte Carlo. | **Completado** | `src/kpis.py` |
| 4 | Paleta Viridis y Contraste | Unificacion de los tres heatmaps usando colorscale Viridis y contraste dinamico de texto (blanco/gris oscuro). | **Completado** | `frontend/dashboard_volatilidad.html` |
| 5 | Renovacion de Marca Cuantitativa | Cambio de nombre a **Alpha Agent Terminal**, eliminacion total de emojis y caracteres no minimalistas. | **Completado** | Todo el frontend y backend |
| 6 | Histograma de Volatilidad | Reemplazo de la matriz de Markov en el Escritorio 1 por un histograma de volatilidad NATR con calculo dinamico de momentos estadisticos. | **Completado** | `frontend/dashboard_volatilidad.html` |
| 7 | Layout Simetrico de Ancho Completo | Remocion de los paneles Fill Depth y Calculadora, expansion vertical (550px) y horizontal de la superficie 3D. | **Completado** | `frontend/dashboard_volatilidad.html` |
| 8 | Panel Lateral Interactivo 3D | Creacion de barra lateral interactiva con zone tags para overlay de zonas y rotacion animada de camara en la superficie 3D. | **Completado** | `frontend/dashboard_volatilidad.html` |
| 9 | Comprension Progresiva en 3 Capas | Reestructuracion del reporte de superficie a: Veredicto (Capa 1), Narrativa (Capa 2) y Datos Tecnicos colapsables (Capa 3). | **Completado** | `src/server.py` |
| 10 | Confluencia Continuo-Discreta | Motor de filtro de ruido que cruza las confluencias reales entre la superficie 3D y las matrices 2D de los heatmaps. | **Completado** | `src/server.py` |
| 11 | Repositorio Limpio e Independiente | Creacion de la carpeta `alpha_agent_terminal/` y migracion final de toda la estructura de archivos y documentacion. | **Completado** | Raiz del proyecto |
| 12 | Robustecimiento del Bridge Dashboard-IDE | Auditoria de 5 flujos de contacto, fix de 5 vulnerabilidades (resiliencia JSON, rutas centralizadas, placeholder F1, eliminacion de texto viejo, protocolo operativo expandido en AGENTS.md). | **Completado** | `src/server.py`, `src/engine.py`, `src/generate_analysis.py`, `.agents/AGENTS.md` |
| 13 | Política Anti-Alucinaciones y Fuentes Institucionales | Configuración estricta en el agente y en la documentación (`AGENTS.md`, `README.md`, `ARCHITECTURE.md`) exigiendo uso exclusivo de fuentes validadas (Bloomberg, Reuters, SEC, Forex Factory) para la investigación web de eventos atípicos. | **Completado** | `.agents/AGENTS.md`, `README.md`, `docs/ARCHITECTURE.md` |

---

## Decisiones Significativas de Arquitectura

1.  **Puente de Sincronizacion en Disco (`estado_dashboard.json`):**
    Para permitir que Antigravity (el agente de chat) conozca el contexto exacto en pantalla sin necesidad de llamadas de red complejas o dependencias de navegador cruzadas, el backend del dashboard escribe un archivo JSON ligero en disco cada vez que el usuario cambia de activo.
2.  **API Hibrida http.server / Plotly.js:**
    Para evitar problemas de CORS, incompatibilidades con servidores pesados y asegurar la maxima velocidad, se opto por un servidor nativo de Python que no requiere instalacion de dependencias mediante `pip`, sirviendo el HTML en el puerto por defecto `8050` (configurable dinamicamente mediante la variable de entorno `SERVER_PORT`) y atendiendo peticiones JSON de series temporales de forma asincrona, desacoplando el puerto en el frontend usando `window.location`.
3.  **Filtrado por Offset de Fecha para Historial de 5 anos:**
    Para admitir mercados que cotizan 7 dias a la semana (cripto) y 5 dias a la semana (Forex/Acciones), el recorte temporal para el grafico se calcula dinamicamente restando 5 anos de la fecha maxima del CSV, asegurando visualizaciones precisas y sin desfases.
4.  **Biblioteca Centralizada de KPIs (`kpis.py`):**
    Para evitar la redundancia y garantizar la consistencia matematica, se centralizaron todos los calculos de volatilidad y analisis de rachas en un unico modulo reutilizable.
5.  **Doble Entrada para el Analisis de Agente:**
    Se diseno un flujo de dos niveles: una interpretacion rapida auto-contenida que el servidor web calcula inmediatamente al hacer clic en "Interpretar", y un informe cuantitativo profundo que el agente escribe en disco cuando el usuario lo solicita en el chat, cargado mediante el boton "Leer Informe Antigravity".

---

## Trazabilidad de Hitos y Consolidados

Este registro historico e hitos se consolidaron a partir de las siguientes fuentes operativas del repositorio original (`Plotly/plotly/`):

| Hito / Solicitud | Archivo Origen (repo historico) | Detalle del Aporte |
|---|---|---|
| **Estructura Inicial y API** | `plotly/server.py` (repo Plotly) | Creacion de endpoints y primer enrutamiento para evitar CORS. |
| **Filtro de 5 Anos** | `plotly/server.py` (repo Plotly) | Calculo dinamico de corte temporal de Pandas. |
| **KPIs de Volatilidad** | `plotly/kpis.py` (repo Plotly) | Biblioteca unificada de logica y momentos estadisticos. |
| **Consolidacion Estetica** | `plotly/dashboard_volatilidad.html` (repo Plotly) | Aplicacion de la paleta Viridis, margenes exactos de 280px y limpieza de emojis. |
| **Confluencia Cruzada** | `src/server.py` | Algoritmo de filtrado de confluencias de primer orden. |
