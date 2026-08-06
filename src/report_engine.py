import json
import os
import math

def _format_frequency(ratio):
    if ratio <= 0:
        return "casi nunca"
    freq = int(round(1 / ratio))
    if freq == 1:
        return "casi todos los días"
    return f"uno de cada {freq} días"

def generate_informe1(asset_name, p1_data):
    """
    Caracterización Estructural (B1-B7).
    Retorna un diccionario con 'html' o 'error'.
    """
    hallazgos = []

    # B1: ¿Cambió de naturaleza?
    bloques = p1_data.get("P1_02_reparto_por_epoca", {}).get("bloques", [])
    if len(bloques) >= 2:
        bloques_sorted = sorted(bloques, key=lambda x: x["natr_medio"])
        min_b = bloques_sorted[0]
        max_b = bloques_sorted[-1]
        if min_b["natr_medio"] > 0:
            ratio = max_b["natr_medio"] / min_b["natr_medio"]
            if ratio > 1.5:
                if max_b["bloque"] < min_b["bloque"]:
                    t = "Hoy es un activo mucho más tranquilo que en el pasado"
                    p = f"En su bloque de {max_b['bloque']}, el activo registró una volatilidad media de {max_b['natr_medio']:.1f}%. En el período de {min_b['bloque']}, esta cifra bajó a {min_b['natr_medio']:.1f}%, marcando un claro descenso en su nivel de agitación."
                    pq = "El sistema decide qué es volatilidad alta mirando toda la historia, incluidos esos años agitados. Por eso, cuando veas la etiqueta alta hoy, es porque de verdad se está moviendo mucho. La vara con que se mide es exigente."
                else:
                    t = "Hoy es un activo mucho más agitado que en sus inicios"
                    p = f"En su bloque de {min_b['bloque']}, el activo registró una volatilidad media de solo {min_b['natr_medio']:.1f}%. En el período de {max_b['bloque']}, esta cifra subió a {max_b['natr_medio']:.1f}%, mostrando un cambio hacia una mayor agitación estructural."
                    pq = "Los umbrales históricos arrastran los años tranquilos del pasado. Si hoy el activo es más volátil, la etiqueta de volatilidad alta saltará con mayor facilidad y será una señal menos excepcional que antes."
                hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    # B2: ¿El peor período es el que el operador recuerda?
    if len(bloques) >= 3:
        # Sort by alto_pct descending
        bloques_altos = sorted(bloques, key=lambda x: x["alto_pct"], reverse=True)
        peor = bloques_altos[0]
        # Sort chronologically to get the two most recent
        bloques_crono = sorted(bloques, key=lambda x: x["bloque"], reverse=True)
        recientes = [bloques_crono[0]["bloque"], bloques_crono[1]["bloque"]]
        if peor["bloque"] not in recientes:
            t = "El episodio que más recuerdas no fue el peor"
            p = f"Mucha gente recuerda los años recientes como los más difíciles, por cercanía. Para este activo no lo fueron. El período {peor['bloque']} fue peor y acumuló mayor proporción de días de alta volatilidad ({peor['alto_pct']:.1f}% de sus sesiones)."
            pq = "Si tu idea del peor escenario posible es lo que viviste recientemente, te estás quedando corto al medir el riesgo histórico que este activo puede llegar a desarrollar."
            hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    # B3: ¿Qué dirección predomina cuando la volatilidad es alta?
    reparto = p1_data.get("P1_05_dependencia_ejes", {}).get("reparto", [])
    alto_reparto = next((r for r in reparto if r["regimen"] == "ALTO"), None)
    if alto_reparto:
        exp = alto_reparto.get("EXPANSIÓN", 0)
        con = alto_reparto.get("CONTRACCIÓN", 0)
        if exp > 55:
            t = "Cuando está agitado, lo normal es que siga construyendo volatilidad"
            p = f"La volatilidad alta en este activo tiende a ocurrir mientras el precio se expande direccionalmente ({exp:.1f}% de las veces). Los sustos suelen coincidir con recorridos largos del precio."
            pq = "Encontrar este activo en volatilidad alta suele significar que el movimiento fuerte está en pleno desarrollo. Es una advertencia directa de no intentar frenar el movimiento prematuramente."
            hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})
        elif con > 55:
            t = "Cuando está agitado, lo normal es que ya se esté calmando"
            p = f"Uno esperaría que volatilidad alta signifique que viene lo peor. En este activo suele ser al revés. Predomina la contracción ({con:.1f}% de las veces), lo que implica que los peaks de volatilidad ocurren mientras el precio recorta agresivamente pero sin expandir direccionalmente la tendencia."
            pq = "Encontrar este activo en volatilidad alta suele significar que el episodio está resolviéndose. No entres en pánico si la agitación ya es evidente, porque lo peor del movimiento direccional ya podría haber pasado."
            hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    # B4: ¿Sube más rápido de lo que baja?
    pers = p1_data.get("P1_04_persistencia_estado", {})
    p_con = pers.get("CONTRACCIÓN", {})
    p_exp = pers.get("EXPANSIÓN", {})
    if p_con and p_exp:
        med_con, p80_con, max_con = p_con.get("mediana", 0), p_con.get("p80", 0), p_con.get("maxima", 0)
        med_exp, p80_exp, max_exp = p_exp.get("mediana", 0), p_exp.get("p80", 0), p_exp.get("maxima", 0)
        if med_con > med_exp and p80_con > p80_exp and max_con > max_exp:
            t = "Se agita rápido, pero tarda en calmarse"
            p = "Las fases de expansión de volatilidad duran menos que las de contracción. La volatilidad sube de una forma y baja de otra: los estallidos son rápidos, pero el mercado requiere mucho tiempo para volver a la calma."
            pq = "Debes adaptar tu paciencia. Si esperas que la calma regrese a la misma velocidad con la que se perdió, cerrarás posiciones de forma prematura."
            hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})
        elif med_exp > med_con and p80_exp > p80_con and max_exp > max_con:
            t = "Se agita despacio, pero se calma rápido"
            p = "Las fases de expansión de volatilidad duran más que las de contracción. El mercado construye la agitación gradualmente, pero cuando la tendencia se frena, la volatilidad cae abruptamente."
            pq = "Si notas que el mercado lleva tiempo agitándose, ten cuidado porque la resolución (la caída de la volatilidad) puede ser violenta y repentina."
            hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    # B5: Riesgo fuera de sesión
    desc = p1_data.get("P1_07_descomposicion_sesion", {})
    n3 = desc.get("n3", {})
    if "share_pct" in n3: # Solo si cotiza con pausas y es fiable
        val = n3["share_pct"]
        if val > 0:
            nivel = "bajo" if val < 15 else ("moderado" if val <= 30 else "alto")
            t = f"El riesgo fuera de sesión es {nivel}"
            p = f"Aproximadamente el {val:.1f}% del movimiento diario de este activo ocurre mientras el mercado está cerrado, es decir, entre el cierre de una sesión y la apertura de la siguiente."
            pq = "Un stop loss solo te protege con el mercado abierto. Si dejas operaciones abiertas de un día para otro, el precio puede abrir más allá de tu nivel fijado. Tu única protección en ese tramo es el tamaño de la posición."
            hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    # B6: Historia como referencia
    rpe = p1_data.get("P1_02_reparto_por_epoca", {})
    p_hist = rpe.get("percentil_historia_completa", 0)
    p_5a = rpe.get("percentil_ultimos_5a", 0)
    if abs(p_hist - p_5a) > 15:
        t = "Tu lectura del activo depende de qué historia mires"
        p = f"Actualmente la volatilidad se ubica en el percentil {p_hist:.1f} de toda su historia, pero si miramos solo los últimos 5 años, salta al percentil {p_5a:.1f}. La lectura cambia significativamente según la ventana temporal."
        pq = "Ten cuidado con los indicadores por defecto que miran muy hacia atrás. En este activo, el pasado lejano distorsiona la percepción de lo que es normal hoy."
        hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    # B7: Estrés raro
    vrr = p1_data.get("P1_08_vrr", {})
    exp_pct = vrr.get("expansion_pct", 100)
    if exp_pct < 10:
        t = "El estrés sostenido es genuinamente excepcional"
        p = f"Solo en un {exp_pct:.1f}% de su historia este activo logró sostener un nivel de volatilidad alto frente a su media de mediano plazo. Lo normal es que los peaks se evaporen rápido."
        pq = "Alcanzar el nivel de estrés es una señal poco frecuente. Cuando la veas, asume que es una anomalía transitoria y no el nuevo comportamiento estándar."
        hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    final_hallazgos = hallazgos[:4]
    
    # HTML FORMAT: Adhering EXACTLY to INSTRUCCIONES_INFORME_CARACTERIZACION_ESTRUCTURAL.md (No Emojis)
    html = f"<div>\n"
    html += f"<h1 style=\"font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px;\">Lo que la historia de {asset_name} te enseña sobre este activo</h1>\n"
    html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; font-style: italic; color: #64748b; line-height: 1.6; margin-bottom: 24px;\">Cuatro cosas que conviene saber antes de operarlo. Todo sale de su historia.</p>\n"

    if len(final_hallazgos) == 0:
        html += "<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 16px;\">El instrumento no presenta rasgos estructurales destacables en sus dimensiones históricas. Un activo estadísticamente anodino y regular.</p>\n"
    else:
        for i, h in enumerate(final_hallazgos, 1):
            html += f"<h3 style=\"font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: #475569; letter-spacing: 0.5px; margin-top: 24px; margin-bottom: 12px;\">{i} &middot; {h['titulo']}</h3>\n"
            html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 12px;\">{h['parrafo']}</p>\n"
            html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 24px; border-bottom: 1px solid #f1f5f9; padding-bottom: 16px;\"><strong style=\"font-weight: 600; color: #0f172a;\">Por qué te importa.</strong> {h['porque']}</p>\n"
            if len(final_hallazgos) < 3 and i == len(final_hallazgos):
                html += "<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; font-style: italic; color: #64748b; line-height: 1.6; margin-bottom: 24px;\">Nota: El instrumento no presenta rasgos estructurales destacables en las dimensiones restantes.</p>\n"

    html += f"<h3 style=\"font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: #475569; letter-spacing: 0.5px; margin-top: 24px; margin-bottom: 12px;\">En una frase</h3>\n"
    html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 16px;\">Conocer cómo ha cambiado la agitación de {asset_name} te permite contextualizar cualquier lectura de volatilidad actual para no sobredimensionar el riesgo.</p>\n"
    html += "<p style=\"font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.6; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 16px; margin-top: 24px;\"><strong style=\"font-weight: 600; color: #475569;\">Dos cosas que este análisis no te dice.</strong> No predice cuánto se moverá mañana: describe lo que ha hecho antes. Y no distingue entre comprar y vender, porque mide cuánto se mueve el precio, no hacia dónde.</p>\n"
    html += "</div>"

    return {"html": html}

def generate_informe2(asset_name, chart_data):
    """
    Magnitud de Volatilidad (D1-D5).
    Retorna un diccionario con 'html' o 'error'.
    chart_data es la lista de objetos devuelta por el endpoint /api/volatility en 'chart_data'
    """
    if not chart_data:
        return {"error": "No chart_data provided"}
    
    # Extraer NATR
    natrs = [d['natr'] for d in chart_data if 'natr' in d and d['natr'] is not None]
    if not natrs:
        return {"error": "No NATR data"}
    
    natrs_sorted = sorted(natrs)
    n = len(natrs_sorted)
    
    tipico = natrs_sorted[n // 2]
    promedio = sum(natrs_sorted) / n
    p95 = natrs_sorted[int(n * 0.95)]
    maximo = natrs_sorted[-1]
    
    hallazgos = []
    
    # D1: Dia corriente frente al promedio
    if promedio > tipico * 1.2:
        t = f"Un día corriente se mueve {tipico:.1f}%, pero el promedio dice {promedio:.1f}%"
        p = f"Si buscas el día del medio en toda su historia, se movió un {tipico:.1f}%. Esa es la cifra normal. El promedio ({promedio:.1f}%) es engañoso: unas pocas sesiones gigantes lo elevan."
        pq = f"Si calculas el tamaño de tus posiciones con el promedio, asumes un día más agitado del que vivirás casi siempre. Memoriza {tipico:.1f}%."
        hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})
    else:
        # Variante: activo regular
        t = f"Un día corriente se mueve {tipico:.1f}%, muy alineado a su promedio ({promedio:.1f}%)"
        p = "Este activo tiene un comportamiento diario altamente regular, sin sesiones extremas que distorsionen severamente la media. Lo que ves es lo que hay."
        pq = f"Puedes confiar en el promedio para calcular tu riesgo. La cifra normal es {tipico:.1f}%."
        hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    # D2: Dia extremo
    ratio_ext = p95 / tipico if tipico > 0 else 0
    if ratio_ext > 2:
        t = f"Un día extremo se mueve {ratio_ext:.1f} veces más que uno corriente"
        p = f"El 5% de días más agitados se mueven alrededor de {p95:.1f}%. Y el día más volátil de toda su historia llegó a {maximo:.1f}%, un pico extremo."
        pq = "Un stop pensado para un día normal no aguanta un día extremo. Tu gestión de riesgo debe contemplar que los peaks multiplican severamente la volatilidad normal."
        hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})
        
    # D3: Frecuencia de dias grandes (Siempre se publica)
    doble = tipico * 2
    dias_grandes = sum(1 for x in natrs if x > doble)
    prop = dias_grandes / n
    frec_str = _format_frequency(prop)
    t = f"{frec_str.capitalize()} dobla al día corriente"
    p = f"Un {prop*100:.1f}% de las sesiones se mueven más del doble que una jornada normal. Traducido: {frec_str}."
    pq = "No estás ante un evento excepcional que ocurre una vez al año. Si operas este activo, te encontrarás con días así habitualmente. Tu riesgo debe contarlos como normales."
    hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})
    
    # D4: Distancia hasta etiqueta alta
    t66 = natrs_sorted[int(n * 0.66)]
    distancia_pct = ((t66 - tipico) / tipico) if tipico > 0 else 0
    if distancia_pct < 0.25:
        t = "Basta un pequeño salto para encender la etiqueta alta"
        p = f"El régimen de volatilidad alta arranca a solo un {distancia_pct*100:.0f}% de distancia del día típico. La etiqueta aparece con facilidad."
        pq = "La etiqueta alta es sensible. No te asustes solo por el color; mira siempre la magnitud real del porcentaje, porque saltará a la mínima provocación."
        hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})
    else:
        t = "La etiqueta alta exige un cambio brusco"
        p = f"El régimen de volatilidad alta está a un {distancia_pct*100:.0f}% de distancia del día típico. Para encenderla el activo debe sacudirse con fuerza."
        pq = "En este activo la etiqueta alta es una señal contundente. Cuando aparece, el mercado realmente ha cambiado de fase."
        hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    # D5: Peaks historicos
    top_dates = sorted(chart_data, key=lambda x: x.get('natr', 0), reverse=True)[:3]
    fechas_top = [d['date'][:4] for d in top_dates if 'date' in d and len(d['date']) >= 4]
    fechas_unicas = list(set(fechas_top))
    if len(fechas_unicas) > 0 and len(fechas_unicas) <= 2:
        anios = ", ".join(fechas_unicas)
        t = f"Sus momentos más volátiles se concentran en pocos años ({anios})"
        p = f"Los períodos de mayor volatilidad de su historia ocurrieron en esos años, llegando a peaks de {maximo:.1f}%."
        pq = "Ese es el techo que este activo ha demostrado alcanzar. No significa que vaya a repetirse mañana, pero sí que está dentro de lo que es capaz de hacer en pánico."
        hallazgos.append({"titulo": t, "parrafo": p, "porque": pq})

    final_hallazgos = hallazgos[:4]
    
    html = f"<div>\n"
    html += f"<h1 style=\"font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px;\">Cuánto se mueve {asset_name} y hasta dónde puede llegar</h1>\n"
    html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; font-style: italic; color: #64748b; line-height: 1.6; margin-bottom: 24px;\">Cifras que conviene memorizar sobre este activo, sacadas de su historia.</p>\n"

    for i, h in enumerate(final_hallazgos, 1):
        html += f"<h3 style=\"font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: #475569; letter-spacing: 0.5px; margin-top: 24px; margin-bottom: 12px;\">{i} &middot; {h['titulo']}</h3>\n"
        html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 12px;\">{h['parrafo']}</p>\n"
        html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 24px; border-bottom: 1px solid #f1f5f9; padding-bottom: 16px;\"><strong style=\"font-weight: 600; color: #0f172a;\">Por qué te importa.</strong> {h['porque']}</p>\n"

    html += f"<h3 style=\"font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: #475569; letter-spacing: 0.5px; margin-top: 24px; margin-bottom: 12px;\">En una frase</h3>\n"
    html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 16px;\">{asset_name} se mueve normalmente alrededor de un {tipico:.1f}% al día, pero su historia demuestra que puede rebasar esa cifra drásticamente.</p>\n"
    html += "<p style=\"font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.6; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 16px; margin-top: 24px;\"><strong style=\"font-weight: 600; color: #475569;\">Dos cosas que este análisis no te dice.</strong> No predice cuánto se moverá mañana: describe lo que ha hecho antes. Y no distingue entre comprar y vender, porque mide cuánto se mueve el precio, no hacia dónde.</p>\n"
    html += "</div>"

    return {"html": html}

def generate_informe3(asset_name, df):
    """
    Distribución de Retornos (Pilar 2).
    Retorna un diccionario con 'html' o 'error'.
    df es el dataframe completo devuelto por fetch_data y procesado con retornos.
    """
    if df is None or df.empty or 'Return' not in df.columns:
        return {"error": "No dataframe or Return data"}
    
    import math
    import pandas as pd

    def format_freq_years(ratio):
        if ratio <= 0: return "nunca"
        days = int(round(1/ratio))
        years = days // 252
        if years > 0:
            return f"uno de cada {days} días (unos {years} años)"
        return f"uno de cada {days} días"

    n_total = len(df)
    std = df['Return'].std()
    
    hallazgos = []

    # E2: Campana y extremos
    count_2 = len(df[df['Return'].abs() > 2 * std])
    count_4 = len(df[df['Return'].abs() > 4 * std])
    prop_2 = count_2 / n_total if n_total > 0 else 0
    prop_4 = count_4 / n_total if n_total > 0 else 0

    freq_2_real_str = format_freq_years(prop_2)
    freq_4_real_str = format_freq_years(prop_4)

    t_e2 = "La campana funciona en el centro y falla en los extremos"
    p_e2 = f"La teoría dice que un movimiento mayor a dos desviaciones ocurre el 4.5% de las veces. En este activo ocurre {freq_2_real_str}, lo cual es razonablemente fiel. Sin embargo, un evento extremo de cuatro desviaciones que según la campana debería ocurrir una vez cada 62 años, aquí pasa {freq_4_real_str}."
    pq_e2 = "El umbral marcado en el gráfico es una referencia útil; más allá de él, la curva subestima gravemente lo que este activo puede hacer en un solo día."
    hallazgos.append({"titulo": t_e2, "parrafo": p_e2, "porque": pq_e2})

    # E1: Desviación típica (Siempre se publica)
    t_e1 = f"Una desviación típica equivale a un movimiento de {std:.1f}%"
    p_e1 = f"La dispersión histórica de los retornos diarios de este activo sitúa su desviación típica en {std:.1f}%. En consecuencia, el umbral de dos desviaciones marcado en el gráfico corresponde a un {2*std:.1f}%."
    pq_e1 = f"Cuando el indicador Z-Score (Evaluación Estocástica) alcance la marca de ±2, sabrás instantáneamente que estás ante un movimiento cercano al {2*std:.1f}% diario."
    hallazgos.append({"titulo": t_e1, "parrafo": p_e1, "porque": pq_e1})

    # E4: Tamaño vs Volatilidad
    df['AbsReturn'] = df['Return'].abs()
    if 'Regime' in df.columns:
        mean_alto = df[df['Regime'] == 'ALTO']['AbsReturn'].mean()
        mean_bajo = df[df['Regime'] == 'BAJO']['AbsReturn'].mean()
        if pd.notna(mean_alto) and pd.notna(mean_bajo) and mean_bajo > 0:
            ratio = mean_alto / mean_bajo
            if ratio > 2 or mean_alto <= mean_bajo:
                t_e4 = "El tamaño del movimiento cambia bruscamente según el régimen"
                p_e4 = f"Una sesión de régimen alto se mueve en promedio {ratio:.1f} veces más que una de régimen bajo."
                pq_e4 = "El mismo tamaño de posición representa un riesgo drásticamente distinto dependiendo del régimen en el que te encuentres operando. El panel de dispersión muestra esto como dos nubes claramente separadas."
                hallazgos.append({"titulo": t_e4, "parrafo": p_e4, "porque": pq_e4})

    # E3: Asimetría
    skew = df['Return'].skew()
    if pd.notna(skew):
        if abs(skew) > 0.3:
            sentido = "Las caídas extremas superan en tamaño a las subidas" if skew < 0 else "Las subidas extremas superan en tamaño a las caídas"
            p_e3 = "La distribución es marcadamente asimétrica. Los episodios extremos hacia abajo son sistemáticamente más violentos que los días de euforia hacia arriba." if skew < 0 else "La distribución es marcadamente asimétrica. Los episodios de euforia hacia arriba son sistemáticamente más violentos que los días de pánico hacia abajo."
            pq_e3 = "Sabiendo esto, debes gestionar tu stop-loss de forma asimétrica, dándole más margen protector al lado que concentra los movimientos violentos."
            hallazgos.append({"titulo": sentido, "parrafo": p_e3, "porque": pq_e3})
        else:
            t_e3 = "Las subidas y bajadas son de tamaño comparable"
            p_e3 = "La distribución es simétrica. Las sesiones extremas tienen un tamaño parecido en ambos sentidos de dirección."
            pq_e3 = "No debes esperar que un lado te castigue mucho más fuerte que el otro por razón de tamaño de los eventos de cola."
            hallazgos.append({"titulo": t_e3, "parrafo": p_e3, "porque": pq_e3})

    # E5: Tendencia Media
    mean_ret = df['Return'].mean()
    se_ret = std / math.sqrt(n_total) if n_total > 0 else 1
    if abs(mean_ret) > 2 * se_ret:
        t_e5 = "El activo presenta una tendencia direccional intrínseca"
        p_e5 = f"A lo largo de su historia, muestra una inclinación media anualizada apreciable de {mean_ret*252:.1f}%."
        pq_e5 = "Hay una deriva de largo plazo que te favorece si operas a favor de ella."
        hallazgos.append({"titulo": t_e5, "parrafo": p_e5, "porque": pq_e5})
    else:
        t_e5 = "El activo no muestra una inclinación media apreciable"
        p_e5 = "A lo largo de toda su historia, la media de retornos no es estadísticamente distinguible de cero."
        pq_e5 = "El resultado de operarlo no proviene de mantenerlo ciegamente, sino estrictamente de la selección del momento en que se entra y se sale (market timing)."
        hallazgos.append({"titulo": t_e5, "parrafo": p_e5, "porque": pq_e5})

    # Ensamblar HTML
    anios = n_total // 252
    html = f"<div>\n"
    html += f"<h1 style=\"font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px; border-bottom: 1px solid #e2e8f0; padding-bottom: 12px;\">Cómo se reparten las ganancias y pérdidas de {asset_name}</h1>\n"
    html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; font-style: italic; color: #64748b; line-height: 1.6; margin-bottom: 24px;\">{len(hallazgos[:4])} cosas que conviene entender para leer este panel, sacadas de {anios} años de historia.</p>\n"

    for i, h in enumerate(hallazgos[:4], 1):
        html += f"<h3 style=\"font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: #475569; letter-spacing: 0.5px; margin-top: 24px; margin-bottom: 12px;\">{i} &middot; {h['titulo']}</h3>\n"
        html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 12px;\">{h['parrafo']}</p>\n"
        html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 24px; border-bottom: 1px solid #f1f5f9; padding-bottom: 16px;\"><strong style=\"font-weight: 600; color: #0f172a;\">Por qué te importa.</strong> {h['porque']}</p>\n"

    html += f"<h3 style=\"font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; color: #475569; letter-spacing: 0.5px; margin-top: 24px; margin-bottom: 12px;\">En una frase</h3>\n"
    html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 13px; line-height: 1.7; color: #334155; margin-bottom: 16px;\">Entender la distribución te libera de la ilusión teórica de la campana normal, mostrándote exactamente con qué frecuencia ocurren las sorpresas en {asset_name}.</p>\n"
    html += f"<p style=\"font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.6; color: #64748b; border-top: 1px solid #e2e8f0; padding-top: 16px; margin-top: 24px;\"><strong style=\"font-weight: 600; color: #475569;\">Dos cosas que este análisis no te dice.</strong> No predice el retorno de mañana: describe cómo se repartieron los de toda su historia. Y no indica si conviene comprar o vender.</p>\n"
    html += "</div>"

    return {"html": html}
