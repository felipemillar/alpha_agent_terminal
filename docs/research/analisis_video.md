# Análisis de Video: Plotly Studio enters the Agentic Era

Este documento analiza el webinar **"Plotly Studio enters the agentic era"** presentado por **Matt Brown** (Senior Product Manager en Plotly) y moderado por **Adam**. El análisis detalla el contenido general del video, con un foco especial en la sección señalada a partir del minuto **23:22 (1402 segundos)**.

---

## 🎯 El Punto Clave: Minuto 23:22 (Plan Enterprise y Privacidad)

En el segundo **1402** del video, el orador realiza la transición desde la explicación del modelo SaaS de **Plotly Cloud** (incluyendo el plan Pro enfocado en usuarios individuales y pequeñas consultoras por $50 USD mensuales) hacia la presentación del **Plan Enterprise**, detallando los siguientes aspectos clave:

* **Arquitectura Híbrida/Local (On-Premises):** Permite a las grandes corporaciones ejecutar la plataforma completamente dentro de sus servidores locales (*on-prem*) o usar su nube dedicada.
* **LLMs Privados (Seguridad de Datos):** La característica más crítica para empresas preocupadas por la seguridad es que **los datos no pasan a través de los servidores de Plotly ni de LLMs públicos**. En su lugar, el sistema se conecta a los **LLMs privados** de la propia empresa (por ejemplo, alojados en AWS Bedrock, GCP o Azure), manteniendo toda la información confidencial de forma segura detrás del firewall corporativo.
* **Garantías Corporativas:** Cumplimiento de estándares de seguridad estrictos mediante soporte para **Single Sign-On (SSO)**, acceso a librerías propietarias exclusivas de Plotly y certificación de seguridad **SOC 2**.

---

## 🔍 Resumen Estructurado del Webinar

A continuación se presenta un desglose de los temas principales presentados a lo largo del webinar:

### 1. La Era de la Analítica Agente (*Agentic Analytics*)
* **El Problema del Chatbot Común:** Herramientas como Claude o ChatGPT son muy capaces para analizar datos, pero devuelven "paredes de texto", ocultan las llamadas a herramientas y no ofrecen una interfaz interactiva ni visual directa.
* **La Filosofía de Plotly Studio:** El análisis complejo debe ser interactivo, visual y fácil de verificar por cualquier usuario (no solo desarrolladores). Plotly Studio integra agentes de IA en un lienzo interactivo donde los datos y los gráficos ocupan el centro de la pantalla.
* **Flujo Multistep:** El agente puede planificar y ejecutar de 10 a 70 pasos de forma autónoma (conexión, exploración, análisis, visualización e iteración).

### 2. Demostración en Vivo en Plotly Studio
* **Conexión a Datos:** Permite conectar bases de datos, APIs (en el ejemplo se usa la API de datos económicos FRED) o subir archivos locales (CSV, Excel, Parquet).
* **Seguridad de Credenciales:** Las API keys y accesos se guardan cifrados de manera local en el llavero del sistema operativo (*OS keyring*). Nunca se envían al LLM en texto plano; el código generado hace referencia a ellas localmente.
* **Prevención de Alucinaciones:** Toda cifra o métrica resaltada en negrita en las descripciones y resúmenes de la app **no es inventada por el LLM**, sino calculada e interpolada directamente a partir del código Python que el agente ejecuta en segundo plano.
* **Interactividad de Gráficos:** Los gráficos generados son interactivos de forma nativa (Plotly charts), permitiendo hacer zoom, filtrar series de datos y visualizar tooltips sin recargar la página.
* **Reportes Computacionales (*Write-ups*):** El sistema puede compilar el análisis entero en un informe detallado que incluye de manera obligatoria una sección de **Metodología, Fuentes de Datos y Limitaciones**, promoviendo la transparencia.
* **Construcción e Iteración de Dash Apps:** Con un prompt simple (ej. *"construye una app para este análisis"*), el agente genera una aplicación Dash real en Python. El usuario puede refinarla iterativamente pidiéndole al agente que realice modificaciones en lenguaje natural (vibe coding), para luego publicarla con un clic.
* **Panel de Skills:** Permite encapsular prompts complejos o directrices de estilo (ej. paletas de colores corporativas) en comandos de barra (`/`) reutilizables.

### 3. El Roadmap de Desarrollo (Próximos 4-6 meses)
* **Projects (Proyectos):** Un contenedor de nivel superior para agrupar múltiples sesiones de análisis, compartir conexiones de datos comunes entre el equipo y habilitar un control de versiones robusto para revertir cambios.
* **Scheduled Sessions (Sesiones Programadas):** Capacidad del agente para correr análisis periódicos de forma autónoma, crear reportes automáticos antes de que los empleados lleguen a la oficina o alertar automáticamente si encuentra anomalías en los datos.

### 4. Sesión de Preguntas y Respuestas (Q&A)
* **Soporte MCP (Model Context Protocol):** Se anunció que Plotly está trabajando en integrar la compatibilidad con servidores MCP. En el corto plazo, cada aplicación de Dash podrá actuar como un servidor MCP, permitiendo a los agentes de codificación usarlas como recursos.
* **Tratamiento de PII (Información Personal Identificable):** Para la versión en la nube, se recomienda anonimizar o retirar los datos sensibles antes del análisis. Para entornos corporativos regulados, se aconseja el Plan Enterprise para usar LLMs propios en un entorno seguro.
* **Manejo de Datos no Limpios:** El agente puede sugerir y aplicar correcciones de limpieza de datos de manera interactiva o seguir directrices directas si el usuario se las especifica.
* **Fórmulas Complejas:** El prompt de Plotly Studio acepta fórmulas matemáticas avanzadas y fragmentos de código, que el agente traduce y adapta correctamente al código Python del backend.
