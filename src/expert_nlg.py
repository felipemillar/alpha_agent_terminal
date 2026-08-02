import numpy as np

def generate_magnitud_nlg(stats):
    natr_last = stats.get('natr_last', 0)
    natr_p = stats.get('natr_p', 50)
    natr_median = stats.get('natr_median', 0)
    natr_p90 = stats.get('natr_p90', 0)
    natr_max = stats.get('natr_max', 0)
    atr_14 = stats.get('atr_14', 0)
    price = stats.get('price', 0)
    
    # Nivel 1
    if natr_p < 33:
        clasificacion = "Volatilidad actual **Baja**."
    elif natr_p > 66:
        clasificacion = "Volatilidad actual **Alta**."
    else:
        clasificacion = "Volatilidad actual **Media**."
        
    # Nivel 2
    base = f"*Base histórica:* en una sesión típica, el activo se mueve alrededor de **±{natr_median:.2f}%** respecto al día anterior; en periodos de estrés el rango diario llega a **±{natr_p90:.2f}%** y, en su extremo histórico, a **±{natr_max:.2f}%**."
    
    if natr_p < 33:
        contingencia = f"*Contingencia:* hoy el movimiento diario esperado es de **±{natr_last:.2f}%**, en el **percentil {natr_p:.0f}** de su historia completa — es decir, **más contenido que su norma reciente**."
        implicancia = "**Implicancia:** los rangos diarios están comprimidos. Es un entorno de bajo recorrido; los objetivos intradía deben dimensionarse en consecuencia."
    elif natr_p > 66:
        contingencia = f"*Contingencia:* hoy el movimiento diario esperado es de **±{natr_last:.2f}%**, en el **percentil {natr_p:.0f}** de su historia completa — es decir, **con alta expansión respecto a la norma**."
        implicancia = "**Implicancia:** los rangos diarios están muy expandidos. Riesgo direccional elevado, exige stops más amplios y reducción de apalancamiento."
    else:
        contingencia = f"*Contingencia:* hoy el movimiento diario esperado es de **±{natr_last:.2f}%**, en el **percentil {natr_p:.0f}** de su historia completa — en equilibrio con su promedio reciente."
        implicancia = "**Implicancia:** rangos diarios dentro del comportamiento habitual. Adecuado para operativas estándar sin ajustes extraordinarios de dimensión."

    sub_text = f"Nivel técnico — NATR hoy {natr_last:.2f}% (percentil {natr_p:.0f}/100, historia completa) · NATR mediano histórico {natr_median:.2f}% · p90 (estrés) {natr_p90:.2f}% · máx {natr_max:.2f}% · ATR(14) {atr_14:.2f} · precio {price:.2f}."
    
    return f"""
<p style="margin: 0;"><strong>Nivel 1 — Clasificación:</strong> {clasificacion}</p>
<p style="margin: 10px 0 0 0;"><strong>Nivel 2 — Interpretación.</strong></p>
<p style="margin: 0;">{base}</p>
<p style="margin: 0;">{contingencia}</p>
<p style="margin: 0;">{implicancia}</p>
<br><sub style="color: #94a3b8; font-size: 10px;">{sub_text}</sub>
"""

def generate_regimen_nlg(stats):
    regime = stats.get('regime', 'Medio')
    state = stats.get('state', 'Contracción')
    prob_b_b = stats.get('prob_b_b', 0.92)
    prob_a_a = stats.get('prob_a_a', 0.92)
    prob_m_m = stats.get('prob_m_m', 0.79)
    prob_same = prob_b_b if regime == 'Bajo' else (prob_a_a if regime == 'Alto' else prob_m_m)
    
    # Nivel 1
    clasificacion = f"Régimen **{regime}**, en **{state.lower()}**."
    
    # Base histórica
    base = f"*Base histórica:* el activo reparte su historia en regímenes que son fuertemente persistentes: la probabilidad de continuar en el mismo estado es del **{prob_same*100:.0f}%**. Además, los cambios de régimen pasan habitualmente por el estado Medio."
    
    # Contingencia e implicancia
    if state == 'Contracción':
        contingencia = f"*Contingencia:* el activo está en régimen {regime} y con la volatilidad aún **descendiendo** (contracción). La probabilidad de continuar igual mañana es alta."
        implicancia = f"**Implicancia:** la calma actual tiende a persistir; no conviene anticipar un salto de volatilidad inmediato."
    else:
        contingencia = f"*Contingencia:* el activo está en régimen {regime} y con la volatilidad **aumentando** (expansión). La inercia de expansión es fuerte."
        implicancia = f"**Implicancia:** la expansión tiende a persistir; alerta de movimientos direccionales agresivos a corto plazo."
        
    sub_text = f"Nivel técnico — Markov P(Bajo→Bajo)={prob_b_b:.2f}, P(Alto→Alto)={prob_a_a:.2f}, P(Medio→Medio)={prob_m_m:.2f} · Estado actual: {regime} - {state}."

    return f"""
<p style="margin: 0;"><strong>Nivel 1 — Clasificación:</strong> {clasificacion}</p>
<p style="margin: 10px 0 0 0;"><strong>Nivel 2 — Interpretación.</strong></p>
<p style="margin: 0;">{base}</p>
<p style="margin: 0;">{contingencia}</p>
<p style="margin: 0;">{implicancia}</p>
<br><sub style="color: #94a3b8; font-size: 10px;">{sub_text}</sub>
"""

def generate_estructura_nlg(stats):
    hurst_hist = stats.get('hurst_hist', 0.5)
    hurst_cond = stats.get('hurst_cond', 0.5)
    er_hist = stats.get('er_hist', 0.16)
    er_cond = stats.get('er_cond', 0.16)
    
    if hurst_hist < 0.45:
        class_str = "**ruidosa / reversión a la media** (baja eficiencia)"
        base = f"*Base histórica:* la memoria del activo tiene un sesgo claro a la reversión (Hurst {hurst_hist:.2f}): sus movimientos **no tienden a extenderse**. Eficiencia muy baja (ER {er_hist:.2f})."
    elif hurst_hist > 0.55:
        class_str = "**tendencial / persistente** (alta eficiencia)"
        base = f"*Base histórica:* la memoria del activo es persistente (Hurst {hurst_hist:.2f}): sus movimientos **tienden a autoperpetuarse**. Eficiencia direccional notable (ER {er_hist:.2f})."
    else:
        class_str = "**ruidosa / sin dirección** (caminata aleatoria)"
        base = f"*Base histórica:* la memoria del activo es próxima a una caminata aleatoria (Hurst {hurst_hist:.2f}). Su eficiencia es baja (ER {er_hist:.2f}) — es un instrumento **de zigzag, no de tendencia limpia**."
        
    contingencia = f"*Contingencia:* condicionado al régimen actual, el comportamiento muestra un Hurst de {hurst_cond:.2f} y eficiencia de {er_cond:.2f}."
    
    diff = abs(hurst_hist - hurst_cond)
    if diff < 0.05:
        implicancia = "**Contraste e implicancia:** la lectura actual **confirma la norma histórica**."
    else:
        implicancia = "**Contraste e implicancia:** la lectura actual **difiere de la norma histórica**, mostrando una anomalía estructural a corto plazo."
        
    sub_text = f"Nivel técnico — Hurst serie completa {hurst_hist:.2f}; condicional {hurst_cond:.2f} · Kaufman ER global {er_hist:.2f}, condicional {er_cond:.2f}."

    return f"""
<p style="margin: 0;"><strong>Nivel 1 — Clasificación:</strong> Estructura {class_str}.</p>
<p style="margin: 10px 0 0 0;"><strong>Nivel 2 — Interpretación.</strong></p>
<p style="margin: 0;">{base}</p>
<p style="margin: 0;">{contingencia}</p>
<p style="margin: 0;">{implicancia}</p>
<br><sub style="color: #94a3b8; font-size: 10px;">{sub_text}</sub>
"""

def generate_distribucion_nlg(stats):
    kurt = stats.get('kurt', 0)
    skw = stats.get('skw', 0)
    z_score = stats.get('z_score', 0)
    last_ret = stats.get('last_ret', 0)
    
    class_1 = "Retorno de hoy **dentro de la norma**" if abs(z_score) < 1.5 else "Retorno de hoy **extremo**"
    class_2 = "**gruesas**" if kurt > 3 else "**normales**"
    
    base = f"*Base histórica:* los retornos se distribuyen con asimetría de {skw:.2f} y exceso de curtosis de {kurt:.2f}. "
    if kurt > 3:
         base += "Las **colas gruesas** indican que movimientos extremos ocurren mucho más de lo que predice una distribución normal."
    else:
         base += "Las colas se asemejan a una distribución normal."
         
    contingencia = f"*Contingencia:* el retorno de la última sesión fue **{last_ret:.2f}%**, equivalente a **{z_score:.2f} desviaciones**."
    
    if abs(z_score) < 1.5:
        implicancia = "**Implicancia:** aunque hoy no hay anomalía, el dimensionamiento no debe calibrarse solo con la media."
    else:
        implicancia = "**Implicancia:** detectamos un shock estadístico intradiario. Máxima alerta de riesgo de cola."
        
    sub_text = f"Nivel técnico — Retorno último {last_ret:.2f}% · Z = {z_score:.2f} · asimetría {skw:.2f} · curtosis (exceso) {kurt:.2f}."

    return f"""
<p style="margin: 0;"><strong>Nivel 1 — Clasificación:</strong> {class_1}; colas históricas {class_2}.</p>
<p style="margin: 10px 0 0 0;"><strong>Nivel 2 — Interpretación.</strong></p>
<p style="margin: 0;">{base}</p>
<p style="margin: 0;">{contingencia}</p>
<p style="margin: 0;">{implicancia}</p>
<br><sub style="color: #94a3b8; font-size: 10px;">{sub_text}</sub>
"""

def generate_trayectoria_nlg(stats):
    return """<p style="margin: 0;"><strong>Nivel 2 — Interpretación.</strong> La trayectoria reciente consolida la inercia del estado actual. No se observan divergencias dramáticas entre las ventanas cortas y largas en el corto plazo.</p>"""

def generate_sintesis_nlg(stats):
    return """<p style="margin: 0;"><strong>Operativa recomendada:</strong> Evaluar rupturas solo si el contexto macro acompaña, manteniendo una estricta gestión del riesgo ante distribuciones de cola gruesa.</p>"""

def generate_resumen_nlg(stats):
    regime = stats.get('regime', 'Medio')
    hurst = stats.get('hurst_hist', 0.5)
    
    perfil = "ruidoso y poco eficiente" if hurst < 0.55 else "tendencial"
    
    return f"""<p style="margin: 0;"><strong>Perfil estructural:</strong> Activo {perfil}.</p>
<p style="margin: 0;"><strong>Estado de contingencia:</strong> En régimen {regime}.</p>"""
