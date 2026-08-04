import numpy as np

def nlg_1_regimen_y_dimension(stats):
    """
    Régimen de volatilidad y su implicancia cualitativa según los umbrales T33 y T66.
    """
    regime = stats.get('regime', 'Desconocido')
    natr_last = stats.get('natr_last', 0.0)
    t33 = stats.get('t33', 0.0)
    t66 = stats.get('t66', 0.0)
    
    # Textos base (Clasificación)
    if regime == 'BAJO':
        clasificacion = f"**Régimen actual {regime}.** Volatilidad comprimida, ideal para estrategias no direccionales o acumulación."
    elif regime == 'ALTO':
        clasificacion = f"**Régimen actual {regime}.** Volatilidad crítica y expandida. Zona de reducción de lotaje y riesgo direccional masivo."
    else:
        clasificacion = f"**Régimen actual {regime}.** El mercado transita en la norma de ruido histórico."
        
    base = f"*Base histórica:* el activo navega estructuralmente entre los umbrales estáticos del {t33:.2f}% y {t66:.2f}%."
    
    # Cálculos cualitativos (sin asustar con números)
    if regime == 'BAJO':
        distance = t33 - natr_last
        if distance > (t33 * 0.2): # muy abajo
            contingencia = f"*Contingencia:* la volatilidad está **profundamente comprimida**, muy lejos de la zona media histórica."
        else:
            contingencia = f"*Contingencia:* la volatilidad está comprimida, pero **rozando la barrera hacia la zona Media histórica**."
        implicancia = "**Implicancia:** los rangos diarios están apagados. Es un entorno de bajo recorrido; los objetivos intradía deben dimensionarse en consecuencia."
        
    elif regime == 'ALTO':
        distance = natr_last - t66
        if distance > (t66 * 0.2):
            contingencia = f"*Contingencia:* la volatilidad ha **explotado por completo**, despegándose aceleradamente del límite histórico superior."
        else:
            contingencia = f"*Contingencia:* la volatilidad ha superado el techo histórico y está **entrando a la zona de pánico**."
        implicancia = "**Implicancia:** los rangos diarios están muy expandidos. Riesgo direccional elevado, exige stops más amplios y reducción de apalancamiento."
        
    else: # MEDIO
        mid_point = (t33 + t66) / 2
        if natr_last < mid_point:
            contingencia = f"*Contingencia:* la volatilidad está operando en la zona Media, **cerca del soporte de compresión histórica**."
        else:
            contingencia = f"*Contingencia:* la volatilidad está operando en la zona Media, **acercándose peligrosamente al techo de expansión**."
        implicancia = "**Implicancia:** rangos diarios dentro del comportamiento habitual. Adecuado para operativas estándar sin ajustes extraordinarios de dimensión."

    sub_text = f"Nivel técnico — NATR actual {natr_last:.2f}% frente a umbrales T33 ({t33:.2f}%) y T66 ({t66:.2f}%)."
    
    return f"""
<p style="margin: 0;"><strong>Nivel 1 — Clasificación:</strong> {clasificacion}</p>
<p style="margin: 10px 0 0 0;"><strong>Nivel 2 — Interpretación.</strong></p>
<p style="margin: 0;">{base}</p>
<p style="margin: 0;">{contingencia}</p>
<p style="margin: 0;">{implicancia}</p>
<p style="margin: 10px 0 0 0; font-size: 11px; color: #94a3b8;">{sub_text}</p>
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
    pilar2 = stats.get('pilar2', {})
    if not pilar2 or 'error' in pilar2:
        kurt = stats.get('kurt', 0)
        skw = stats.get('skw', 0)
        n_efectivo_str = ""
    else:
        kurt = pilar2.get("P2_02_curtosis", {}).get("global", {}).get("valor", 0)
        skw = pilar2.get("P2_01_asimetria", {}).get("global", {}).get("valor", 0)

    z_score = stats.get('z_score', 0)
    last_ret = stats.get('last_ret', 0)
    regime = stats.get('regime', 'MEDIO').upper()
    
    # Riesgo de Cola (P2.04 ES)
    es_msg = ""
    n_efectivo_str = ""
    if pilar2 and 'P2_03_04_riesgo_cola' in pilar2:
        riesgo = pilar2["P2_03_04_riesgo_cola"]["por_regimen"].get(regime, {}).get("1", {})
        largo = riesgo.get("largo", {})
        corto = riesgo.get("corto", {})
        
        fallback_msg = ""
        if not largo.get("publicable") or not corto.get("publicable"):
            riesgo = pilar2["P2_03_04_riesgo_cola"]["global"].get("1", {})
            largo = riesgo.get("largo", {})
            corto = riesgo.get("corto", {})
            fallback_msg = " Debido a insuficiencia estadística en este régimen específico, se expone el riesgo de cola de la distribución global."
        
        if largo.get("publicable") and corto.get("publicable"):
            es_l = largo['es_pct']
            var_l = largo['var_pct']
            n_eff_l = largo['n_efectivo']
            err_l = largo['error_estandar']
            
            es_c = corto['es_pct']
            var_c = corto['var_pct']
            n_eff_c = corto['n_efectivo']
            err_c = corto['error_estandar']
            
            es_msg = f" En el régimen actual, la pérdida esperada en 1 día ante el 5% de peores escenarios es de **{es_l}%** para largos y **{es_c}%** para cortos.{fallback_msg}"
            n_efectivo_str = f" · n_efectivo {n_eff_l} (err {err_l}%)"
            
            implicancia = f"**Implicancia:** Una de cada veinte sesiones pierde más de {var_l}% (largo) o {var_c}% (corto); cuando ocurre, la pérdida media es {es_l}% y {es_c}%. El dimensionamiento debe soportar la pérdida media esperada, no solo el percentil 5."
        else:
            implicancia = "**Implicancia:** el dimensionamiento no debe calibrarse solo con la media."
    else:
        if abs(z_score) < 1.5:
            implicancia = "**Implicancia:** aunque hoy no hay anomalía, el dimensionamiento no debe calibrarse solo con la media."
        else:
            implicancia = "**Implicancia:** detectamos un shock estadístico intradiario. Máxima alerta de riesgo de cola."
    
    class_1 = "Retorno de hoy **dentro de la norma**" if abs(z_score) < 1.5 else "Retorno de hoy **extremo**"
    class_2 = "**gruesas**" if kurt > 0 else "**normales**"
    
    base = f"*Base histórica:* los retornos se distribuyen con asimetría de {skw:.2f} y exceso de curtosis de {kurt:.2f}. "
    if kurt > 0:
         base += "Las **colas gruesas** indican que movimientos extremos ocurren mucho más de lo que predice una distribución normal."
    else:
         base += "Las colas se asemejan a una distribución normal."
         
    contingencia = f"*Contingencia:* el retorno de la última sesión fue **{last_ret:.2f}%**, equivalente a **{z_score:.2f} desviaciones**.{es_msg}"
        
    sub_text = f"Nivel técnico — Retorno último {last_ret:.2f}% · Z = {z_score:.2f} · asimetría {skw:.2f} · curtosis (exceso) {kurt:.2f}{n_efectivo_str}."

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
