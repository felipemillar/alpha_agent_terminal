import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import numpy as np
import pandas as pd
import traceback
import datetime

# Agregar la ruta del proyecto para importar modulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import engine
import kpis
import config
import textwrap

import google.generativeai as genai

# Configurar Gemini desde config centralizado
if config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY no encontrada en .env")

PORT = config.SERVER_PORT


class VolatilityAPIHandler(http.server.BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Endpoint 1: Servir el HTML del dashboard en la raíz
        if path == "/" or path == "/index.html":
            try:
                html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dashboard_volatilidad.html")
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self.send_error_response(500, f"Error cargando HTML: {type(e).__name__}")

        elif path == "/architecture" or path == "/architecture.html":
            try:
                html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "mapa_arquitectura.html")
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self.send_error_response(500, f"Error cargando HTML de arquitectura: {type(e).__name__}")

        elif path == "/examples.html":
            try:
                html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "examples_heatmaps.html")
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self.send_error_response(500, f"Error cargando HTML de ejemplos: {type(e).__name__}")

        elif path == "/examples_gaps_designs.html":
            try:
                html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "examples_gaps_designs.html")
                with open(html_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except Exception as e:
                self.send_error_response(500, f"Error cargando HTML de diseños: {type(e).__name__}")
        elif path == "/qrt_logo_light.png" or path == "/qrt_logo_dark.png":
            try:
                img_name = "qrt_logo_light.png" if "light" in path else "qrt_logo_dark.png"
                img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "assets", img_name)
                with open(img_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error_response(404, f"Logo no encontrado: {type(e).__name__}")

        # Health check
        elif path == "/api/health":
            try:
                assets = engine.get_available_assets()
                health = {
                    "status": "ok",
                    "port": PORT,
                    "assets_available": len(assets),
                    "gemini_configured": bool(config.GEMINI_API_KEY),
                    "timestamp": datetime.datetime.now().isoformat()
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(health).encode("utf-8"))
            except Exception as e:
                self.send_error_response(500, f"Health check failed: {type(e).__name__}")

        # Endpoint 2: Obtener activos disponibles
        elif path == "/api/assets":
            try:
                assets = engine.get_available_assets()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(assets).encode("utf-8"))
            except Exception as e:
                traceback.print_exc()
                self.send_error_response(500, f"Error obteniendo activos: {type(e).__name__}")

        # Endpoint 3: Obtener datos de volatilidad y gráficos para un activo
        elif path == "/api/volatility":
            asset_name = query_params.get("asset", [None])[0]
            if not asset_name:
                self.send_error_response(400, "Falta el parámetro 'asset'")
                return

            try:
                assets = engine.get_available_assets()
                asset_path = None
                for asset in assets:
                    if asset['name'] == asset_name:
                        asset_path = asset['path']
                        break

                if not asset_path:
                    self.send_error_response(404, f"Activo '{asset_name}' no encontrado.")
                    return

                # Ejecutar pipeline y guardar estado_dashboard.json
                result = engine.run_pipeline(asset_path, asset_name)

                # Cargar el dataframe completo para retornar las series de tiempo al frontend
                df = engine.fetch_data(asset_path)
                df = engine.calculate_atr(df)
                df = engine.calculate_natr(df)
                
                # Calcular retornos
                df['Prev_Close'] = df['Close'].shift(1)
                df['Return'] = ((df['Close'] - df['Prev_Close']) / df['Prev_Close']) * 100
                df = df.dropna(subset=['ATR', 'NATR', 'Return']).reset_index(drop=True)
                
                # Filtrar los últimos 5 años de datos históricos para el gráfico
                max_date = df['Date'].max()
                limit_date = max_date - pd.DateOffset(years=5)
                df_chart = df[df['Date'] >= limit_date].copy()

                # Clasificar regímenes para todo el historial usando kpis.py
                df['Regime'], df['Color'] = kpis.classify_regimes_full(df)
                df_chart = df[df['Date'] >= limit_date].copy()

                # Estructurar la data de las series de tiempo para Plotly.js en el frontend
                chart_data = {
                    "dates": df_chart['Date'].dt.strftime('%Y-%m-%d').tolist(),
                    "close": df_chart['Close'].tolist(),
                    "atr": df_chart['ATR'].tolist(),
                    "natr": df_chart['NATR'].tolist(),
                    "return": df_chart['Return'].tolist(),
                    "regimes": df_chart['Regime'].tolist(),
                    "colors": df_chart['Color'].tolist()
                }

                response_data = {
                    "metrics": result,
                    "chart_data": chart_data
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))

            except Exception as e:
                traceback.print_exc()
                self.send_error_response(500, f"Error analizando volatilidad: {type(e).__name__}")
        elif path == "/api/streaks":
            asset_name = query_params.get("asset", [None])[0]
            regime = query_params.get("regime", ["BAJO"])[0]
            if not asset_name:
                self.send_error_response(400, "Falta el parámetro 'asset'")
                return

            try:
                assets = engine.get_available_assets()
                asset_path = None
                for asset in assets:
                    if asset['name'] == asset_name:
                        asset_path = asset['path']
                        break

                if not asset_path:
                    self.send_error_response(404, f"Activo '{asset_name}' no encontrado.")
                    return

                df = engine.fetch_data(asset_path)
                df = engine.calculate_atr(df)
                df = engine.calculate_natr(df)
                df['Regime'], df['Color'] = kpis.classify_regimes_full(df)
                
                df_streaks = kpis.get_streak_metrics(df, 'Regime', regime)
                
                if df_streaks.empty:
                    streaks_list = []
                    summary = {
                        "total_streaks": 0,
                        "avg_duration": 0.0,
                        "median_duration": 0.0,
                        "pct_positive": 0.0,
                        "max_duration": 0
                    }
                else:
                    streaks_list = df_streaks.to_dict(orient="records")
                    
                    total_str = len(df_streaks)
                    avg_dur = float(df_streaks['duration'].mean())
                    med_dur = float(df_streaks['duration'].median())
                    max_dur = int(df_streaks['duration'].max())
                    pct_pos = float((df_streaks['change'] > 0).sum() / total_str) * 100
                    
                    summary = {
                        "total_streaks": total_str,
                        "avg_duration": round(avg_dur, 2),
                        "median_duration": round(med_dur, 1),
                        "pct_positive": round(pct_pos, 1),
                        "max_duration": max_dur
                    }

                response_data = {
                    "regime": regime,
                    "asset": asset_name,
                    "streaks": streaks_list,
                    "summary": summary
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))

            except Exception as e:
                traceback.print_exc()
                self.send_error_response(500, f"Error obteniendo rachas: {type(e).__name__}")

        elif path == "/api/markov":
            asset_name = query_params.get("asset", [None])[0]
            if not asset_name:
                self.send_error_response(400, "Falta el parámetro 'asset'")
                return

            try:
                assets = engine.get_available_assets()
                asset_path = None
                for asset in assets:
                    if asset['name'] == asset_name:
                        asset_path = asset['path']
                        break

                if not asset_path:
                    self.send_error_response(404, f"Activo '{asset_name}' no encontrado.")
                    return

                df = engine.fetch_data(asset_path)
                df = engine.calculate_atr(df)
                df = engine.calculate_natr(df)
                
                regime_series, _ = kpis.classify_regimes_full(df)
                markov_data = kpis.calculate_markov_matrix(regime_series)
                markov_data["asset"] = asset_name

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(markov_data).encode("utf-8"))

            except Exception as e:
                traceback.print_exc()
                self.send_error_response(500, f"Error calculando matriz de Markov: {type(e).__name__}")

        elif path == "/api/agent/read_bridge":
            try:
                if os.path.exists(config.BRIDGE_RESPONSE_PATH):
                    with open(config.BRIDGE_RESPONSE_PATH, "r", encoding="utf-8") as f:
                        raw_content = f.read()
                    try:
                        response_data = json.loads(raw_content)
                    except json.JSONDecodeError:
                        print(f"WARNING: antigravity_bridge_response.json contiene JSON inválido. Devolviendo error amigable.")
                        response_data = {"ai_raw_text": "<b>[ERROR DE SINCRONIZACIÓN]</b><br>El archivo de respuesta del bridge está dañado. Por favor, solicita un nuevo análisis al agente en el IDE."}
                else:
                    response_data = {"ai_raw_text": "Aún no hay respuesta de Antigravity."}
                    
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
            except Exception as e:
                self.send_error_response(500, f"Error leyendo puente: {type(e).__name__} (detalles omitidos por seguridad)")

        elif path == "/api/gaps":
            asset_name = query_params.get("asset", [None])[0]
            if not asset_name:
                self.send_error_response(400, "Falta el parámetro 'asset'")
                return

            try:
                assets = engine.get_available_assets()
                asset_path = None
                for asset in assets:
                    if asset['name'] == asset_name:
                        asset_path = asset['path']
                        break

                if not asset_path:
                    self.send_error_response(404, f"Activo '{asset_name}' no encontrado.")
                    return

                df = engine.fetch_data(asset_path)
                gap_results = engine.analyze_gaps(df)
                gap_results["asset"] = asset_name

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(gap_results).encode("utf-8"))

            except Exception as e:
                traceback.print_exc()
                self.send_error_response(500, f"Error analizando gaps: {type(e).__name__} (detalles omitidos por seguridad)")

        else:
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/agent/analyze":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                asset = data.get('asset', 'Unknown Asset')
                points = data.get('points', [])
                
                if not points:
                    self.send_error_response(400, "No points provided")
                    return

                # Calculate Mock Agent metrics
                x_vals = [p['x'] for p in points]
                y_vals = [p['y'] for p in points]
                
                min_x, max_x = min(x_vals), max(x_vals)
                min_y, max_y = min(y_vals), max(y_vals)
                
                avg_x = sum(x_vals) / len(x_vals)
                avg_y = sum(y_vals) / len(y_vals)
                
                # Expand box slightly
                pad_x = (max_x - min_x) * 0.1 if (max_x - min_x) != 0 else abs(max_x)*0.1
                pad_y = (max_y - min_y) * 0.1 if (max_y - min_y) != 0 else abs(max_y)*0.1
                
                if pad_x == 0: pad_x = 0.5
                if pad_y == 0: pad_y = 0.1

                shape = {
                    'type': 'rect',
                    'x0': min_x - pad_x,
                    'y0': min_y - pad_y,
                    'x1': max_x + pad_x,
                    'y1': max_y + pad_y,
                    'line': {'color': 'rgba(107, 142, 35, 1)', 'width': 2, 'dash': 'dot'},
                    'fillcolor': 'rgba(107, 142, 35, 0.2)'
                }
                
                dates_list = [p['date'] for p in points]
                
                # Escribir la solicitud para Antigravity
                request_data = {
                    "asset": asset,
                    "dates": dates_list,
                    "avg_ret": f"{avg_x:.2f}",
                    "avg_natr": f"{avg_y:.2f}",
                    "cluster_size": len(points)
                }
                
                with open(config.BRIDGE_REQUEST_PATH, "w", encoding="utf-8") as f:
                    json.dump(request_data, f, indent=4)
                
                # V3: Escribir placeholder en response para evitar que "Leer Respuesta" muestre datos obsoletos
                placeholder_response = {"ai_raw_text": "<i>Solicitud enviada al IDE. Esperando análisis del agente...</i>"}
                with open(config.BRIDGE_RESPONSE_PATH, "w", encoding="utf-8") as f:
                    json.dump(placeholder_response, f, indent=4)
                
                # Respuesta inmediata al frontend indicando que se guardó
                response_data = {
                    "shape": shape,
                    "annotation": {
                        'x': max_x + pad_x,
                        'y': max_y + pad_y,
                        'xref': 'x',
                        'yref': 'y',
                        'text': "<b>[ANTIGRAVITY BRIDGE]</b><br>Fechas enviadas al IDE.",
                        'showarrow': True, 'arrowhead': 2, 'arrowcolor': 'rgba(107, 142, 35, 1)', 'arrowsize': 1, 'arrowwidth': 2, 'ax': 60, 'ay': -60,
                        'bgcolor': 'rgba(255,255,255,0.95)', 'bordercolor': 'rgba(107, 142, 35, 1)',
                        'font': {'family': 'Inter', 'size': 10, 'color': '#111'}, 'align': 'left'
                    },
                    "ai_raw_text": "Fechas capturadas. Ve a tu IDE y pídele a Antigravity que investigue.",
                    "cluster_size": len(points),
                    "avg_ret": f"{avg_x:.2f}",
                    "avg_natr": f"{avg_y:.2f}"
                }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))

            except Exception as e:
                traceback.print_exc()
                self.send_error_response(500, f"Error en puente con Antigravity: {type(e).__name__}")

        elif path == "/api/gaps/analyze_cell":
            try:
                import math
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                asset_name = data.get('asset', '')
                dates_list = data.get('dates', [])
                min_fill_target = float(data.get('min_fill_target', 1.0))
                filters = data.get('filters', {})
                
                if not dates_list:
                    self.send_error_response(400, "No dates provided")
                    return
                
                assets = engine.get_available_assets()
                asset_path = None
                for asset in assets:
                    if asset['name'] == asset_name:
                        asset_path = asset['path']
                        break
                
                if not asset_path:
                    self.send_error_response(404, f"Asset '{asset_name}' not found")
                    return
                
                df = engine.fetch_data(asset_path)
                gap_results = engine.analyze_gaps(df)
                all_points = gap_results.get("points", [])
                
                cell_points = [p for p in all_points if p.get('date') in dates_list]
                n_cell = len(cell_points)
                n_all = len(all_points)
                
                if n_cell == 0:
                    self.send_error_response(400, "No matching points found for the provided dates")
                    return
                
                filled_all = [p for p in all_points if p.get('fill_depth', 0) >= min_fill_target]
                filled_cell = [p for p in cell_points if p.get('fill_depth', 0) >= min_fill_target]
                
                p_all = len(filled_all) / n_all if n_all > 0 else 0.0
                p_cell = len(filled_cell) / n_cell if n_cell > 0 else 0.0
                
                z_score = 0.0
                p_value = 1.0
                if n_cell > 0 and 0.0 < p_all < 1.0:
                    se = math.sqrt(p_all * (1 - p_all) / n_cell)
                    z_score = (p_cell - p_all) / se if se != 0 else 0.0
                    p_value = 1.0 - math.erf(abs(z_score) / math.sqrt(2.0))
                
                cell_success_indicators = [1.0 if p.get('fill_depth', 0) >= min_fill_target else 0.0 for p in cell_points]
                B = 5000
                resamples = np.random.choice(cell_success_indicators, size=(B, n_cell), replace=True)
                resample_means = np.mean(resamples, axis=1)
                ci_lower = float(np.percentile(resample_means, 2.5) * 100)
                ci_upper = float(np.percentile(resample_means, 97.5) * 100)
                
                fill_depths = [p.get('fill_depth', 0) for p in cell_points]
                skewness = 0.0
                kurtosis = 0.0
                if n_cell >= 3:
                    s_series = pd.Series(fill_depths)
                    skew = s_series.skew()
                    kurt = s_series.kurt()
                    skewness = float(skew) if not pd.isna(skew) else 0.0
                    kurtosis = float(kurt) if not pd.isna(kurt) else 0.0
                
                sig_text = "SIGNIFICATIVO" if p_value < 0.05 else "NO SIGNIFICATIVO"
                if p_value < 0.05:
                    if z_score > 0:
                        verdict = "La celda muestra una probabilidad de reversión estadísticamente superior al promedio global del activo."
                    else:
                        verdict = "La celda muestra una probabilidad de reversión estadísticamente inferior al promedio global del activo."
                else:
                    verdict = "La diferencia observada respecto al promedio global del activo no es estadísticamente significativa (p-value >= 0.05)."
                
                skew_desc = "Distribución asimétrica negativa (cola izquierda pesada): fallos raros pero severos." if skewness < -0.5 else "Distribución con asimetría positiva o moderada."
                kurt_desc = "Distribución leptocúrtica (colas gordas): riesgo de colas anómalas en esta celda." if kurtosis > 1.0 else "Distribución normal o platicúrtica: variaciones bajo control."
                
                ai_text = f"<h3>Reporte de Inferencia Cuantitativa (Opening Gaps)</h3>" \
                          f"<p><b>Hipótesis Nula H0:</b> La tasa de reversión en esta celda es igual a la media global de {p_all*100:.1f}%.<br>" \
                          f"<b>Hipótesis Alternativa H1:</b> La tasa de reversión difiere de la media global.<br>" \
                          f"<b>Veredicto:</b> {verdict}</p>" \
                          f"<table class='summary-table' style='width:100%; border-collapse:collapse; font-size:12px; margin-bottom:15px;'>" \
                          f"  <tr style='border-bottom:1px solid #eee; background:#f8fafc;'><th style='padding:6px; text-align:left;'>Parámetro</th><th style='padding:6px; text-align:right;'>Valor</th></tr>" \
                          f"  <tr style='border-bottom:1px solid #eee;'><td style='padding:6px;'>Muestras (n)</td><td style='padding:6px; text-align:right;'><b>{n_cell}</b></td></tr>" \
                          f"  <tr style='border-bottom:1px solid #eee;'><td style='padding:6px;'>SDFP Celda</td><td style='padding:6px; text-align:right;'><b>{p_cell*100:.1f}%</b></td></tr>" \
                          f"  <tr style='border-bottom:1px solid #eee;'><td style='padding:6px;'>SDFP Global</td><td style='padding:6px; text-align:right;'><b>{p_all*100:.1f}%</b></td></tr>" \
                          f"  <tr style='border-bottom:1px solid #eee;'><td style='padding:6px;'>Z-Score</td><td style='padding:6px; text-align:right;'><b>{z_score:.2f}</b></td></tr>" \
                          f"  <tr style='border-bottom:1px solid #eee; font-weight:bold; color: { '#28a745' if p_value < 0.05 else '#dc3545' };'><td style='padding:6px;'>p-value</td><td style='padding:6px; text-align:right;'>{p_value:.4f} ({sig_text})</td></tr>" \
                          f"  <tr style='border-bottom:1px solid #eee;'><td style='padding:6px;'>CI 95% (Bootstrap)</td><td style='padding:6px; text-align:right;'><b>[{ci_lower:.1f}%, {ci_upper:.1f}%]</b></td></tr>" \
                          f"  <tr style='border-bottom:1px solid #eee;'><td style='padding:6px;'>Sesgo (Skewness)</td><td style='padding:6px; text-align:right;'><b>{skewness:.2f}</b> ({skew_desc})</td></tr>" \
                          f"  <tr style='border-bottom:1px solid #eee;'><td style='padding:6px;'>Curtosis (Kurtosis)</td><td style='padding:6px; text-align:right;'><b>{kurtosis:.2f}</b> ({kurt_desc})</td></tr>" \
                          f"</table>" \
                          f"<p style='font-size:11px; color:#888; margin-top:10px;'>* Cálculos inferenciales generados mediante 5,000 simulaciones Monte Carlo con reemplazo para bootstrapping e integrales de error para Z-test.</p>"
                
                request_data = {
                    "type": "gap_cell_analysis",
                    "asset": asset_name,
                    "filters": filters,
                    "dates": dates_list,
                    "n_samples": n_cell,
                    "min_fill_target": min_fill_target,
                    "z_score": float(f"{z_score:.2f}"),
                    "p_value": float(f"{p_value:.4f}"),
                    "ci_lower": float(f"{ci_lower:.2f}"),
                    "ci_upper": float(f"{ci_upper:.2f}"),
                    "skewness": float(f"{skewness:.2f}"),
                    "kurtosis": float(f"{kurtosis:.2f}")
                }
                with open(config.BRIDGE_REQUEST_PATH, "w", encoding="utf-8") as f:
                    json.dump(request_data, f, indent=4)
                
                response_data = {
                    "cluster_size": n_cell,
                    "avg_ret": f"{p_cell*100:.1f}",
                    "avg_natr": f"{p_all*100:.1f}",
                    "ai_raw_text": ai_text
                }
                with open(config.BRIDGE_RESPONSE_PATH, "w", encoding="utf-8") as f:
                    json.dump(response_data, f, indent=4)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
                
            except Exception as err:
                print(f"Error analizando celda de gaps: {type(err).__name__} (detalles omitidos por seguridad)")
                self.send_error_response(500, f"Error analizando celda de gaps: {type(err).__name__}")

        elif path == "/api/gaps/analyze_surface":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                asset_name = data.get('asset', '')
                x_grid = data.get('x_grid', [])
                y_grid = data.get('y_grid', [])
                z_matrix = data.get('z_matrix', [])
                min_fill_target = float(data.get('min_fill_target', 1.0))
                
                if not x_grid or not y_grid or not z_matrix:
                    self.send_error_response(400, "Missing grid or matrix data")
                    return
                
                max_val = -999.0
                min_val = 999.0
                i_max, j_max = 0, 0
                i_min, j_min = 0, 0
                
                for i in range(len(z_matrix)):
                    for j in range(len(z_matrix[i])):
                        val = z_matrix[i][j]
                        if val > max_val:
                            max_val = val
                            i_max, j_max = i, j
                        if val < min_val:
                            min_val = val
                            i_min, j_min = i, j
                
                x_max = x_grid[j_max]
                y_max = y_grid[i_max]
                x_min = x_grid[j_min]
                y_min = y_grid[i_min]
                
                grad_x = []
                for i in range(len(z_matrix)):
                    for j in range(len(z_matrix[i]) - 1):
                        dZ = z_matrix[i][j+1] - z_matrix[i][j]
                        dX = x_grid[j+1] - x_grid[j]
                        if dX != 0:
                            grad_x.append(abs(dZ / dX))
                
                grad_y = []
                for i in range(len(z_matrix) - 1):
                    for j in range(len(z_matrix[i])):
                        dZ = z_matrix[i+1][j] - z_matrix[i][j]
                        dY = y_grid[i+1] - y_grid[i]
                        if dY != 0:
                            grad_y.append(abs(dZ / dY))
                
                mean_grad_x = np.mean(grad_x) if grad_x else 0.0
                mean_grad_y = np.mean(grad_y) if grad_y else 0.0
                
                ratio = mean_grad_x / mean_grad_y if mean_grad_y != 0 else 1.0
                
                efficient_points = 0
                total_points = len(z_matrix) * len(z_matrix[0])
                for i in range(len(z_matrix)):
                    for j in range(len(z_matrix[i])):
                        if z_matrix[i][j] >= 80.0:
                            efficient_points += 1
                efficient_pct = (efficient_points / total_points) * 100
                
                # Asimetría Direccional
                neg_values = []
                pos_values = []
                for i in range(len(z_matrix)):
                    for j in range(len(z_matrix[i])):
                        val = z_matrix[i][j]
                        gap_val = x_grid[j]
                        if gap_val < 0:
                            neg_values.append(val)
                        elif gap_val > 0:
                            pos_values.append(val)
                
                neg_mean = np.mean(neg_values) if neg_values else 0.0
                pos_mean = np.mean(pos_values) if pos_values else 0.0

                # Semáforo
                if efficient_pct > 15.0 or max_val > 75.0:
                    semaforo = "favorable"
                    semaforo_label = "Favorable"
                elif efficient_pct > 5.0 or max_val > 60.0:
                    semaforo = "moderado"
                    semaforo_label = "Moderado"
                else:
                    semaforo = "desfavorable"
                    semaforo_label = "Desfavorable"

                # Definir recomendaciones simplificadas basadas en el activo
                if "USDCLP" in asset_name:
                    operar_desc = "Gaps bajistas (aperturas con caída del USD) entre -0.3 y -0.8 ATR con volatilidad normal (NATR > 1.2%). Históricamente cierran con alta frecuencia."
                    evitar_desc = "Gaps alcistas mayores a +1.0 ATR en días de baja volatilidad (NATR < 0.8%), donde suele haber continuación de tendencia."
                    plain_desc = "En USD/CLP, las aperturas bajistas tienen alta tendencia a revertir a la media debido al flujo interbancario institucional. Las aperturas alcistas fuertes en días de bajo volumen tienden a consolidarse o continuar subiendo."
                elif "XAUUSD" in asset_name:
                    operar_desc = "Gaps pequeños (±0.4 ATR) en cualquier dirección. El oro tiende a ser altamente reversionista en micro-rangos."
                    evitar_desc = "Operar en contra de gaps expansivos mayores a ±1.5 ATR cuando el NATR supera el 3.5%, ya que la volatilidad extrema fomenta continuaciones violentas."
                    plain_desc = "En el Oro, la reversión es extremadamente eficiente en rangos normales de volatilidad. Sin embargo, en picos de pánico o euforia, los gaps grandes inician tendencias intradía fuertes."
                else: # Por defecto (QQQ, acciones)
                    if pos_mean > neg_mean + 5:
                        plain_desc = f"En {asset_name}, existe un sesgo alcista estructural claro. Las aperturas alcistas se venden con alta probabilidad de retorno a la media (promedio {pos_mean:.1f}%), mientras que las aperturas bajistas muestran mayor convicción de continuación."
                        operar_desc = "Buscar reversiones (fade) en gaps alcistas de magnitud moderada (entre +0.2 y +0.8 ATR) cuando la volatilidad es normal."
                        evitar_desc = "Operar cierres de gap en aperturas bajistas grandes, ya que suelen continuar la caída sin retornar al cierre previo."
                    else:
                        plain_desc = f"En {asset_name}, el comportamiento es balanceado o ligeramente bajista. Las aperturas bajistas tienen buena tasa de reversión (promedio {neg_mean:.1f}%), facilitando compras rápidas al inicio de la sesión."
                        operar_desc = "Comprar rebotes en gaps bajistas de -0.5 a -1.5 ATR combinados con volatilidad media."
                        evitar_desc = "Buscar retrocesos en gaps alcistas grandes cuando el mercado abre con fuerte convicción alcista."

                if ratio > 1.5:
                    sens_desc = f"el tamaño del gap es {ratio:.1f} veces más influyente que la volatilidad sobre la tasa de reversión."
                elif ratio < 0.65:
                    sens_desc = f"la volatilidad histórica es {1.0/ratio:.1f} veces más influyente que el tamaño del gap sobre la tasa de reversión."
                else:
                    sens_desc = "ambas variables influyen en proporciones balanceadas sobre la tasa de reversión."

                # ═══════════════════════════════════════════════════════════════════
                # CONTINUOUS-DISCRETE CONFLUENCE SCANNERS
                # ═══════════════════════════════════════════════════════════════════
                assets = engine.get_available_assets()
                asset_path = None
                for asset in assets:
                    if asset['name'] == asset_name:
                        asset_path = asset['path']
                        break
                
                confluences = []
                noises = []
                
                if asset_path:
                    try:
                        df_raw = engine.fetch_data(asset_path)
                        gap_results = engine.analyze_gaps(df_raw)
                        points = gap_results.get("points", [])
                        
                        weekdays_esp = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
                        for p in points:
                            dt = datetime.datetime.strptime(p['date'], "%Y-%m-%d")
                            p['weekday_name'] = weekdays_esp[dt.weekday()]
                        
                        def get_nearest_surface_val(target_x, target_y):
                            idx_x = min(range(len(x_grid)), key=lambda k: abs(x_grid[k] - target_x))
                            idx_y = min(range(len(y_grid)), key=lambda k: abs(y_grid[k] - target_y))
                            return z_matrix[idx_y][idx_x]
                        
                        # 1. Regime x Weekday Scan
                        regimes = ['BAJO', 'MEDIO', 'ALTO']
                        weekdays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
                        for reg in regimes:
                            for day in weekdays:
                                cell_points = [p for p in points if p['regime'] == reg and p['weekday_name'] == day]
                                n = len(cell_points)
                                if n >= 6:
                                    filled = len([p for p in cell_points if p['fill_depth'] >= min_fill_target])
                                    discrete_prob = (filled / n) * 100.0
                                    
                                    avg_gap = np.mean([p['gap_size_atr'] for p in cell_points])
                                    avg_natr = np.mean([p['natr'] for p in cell_points])
                                    continuous_val = get_nearest_surface_val(avg_gap, avg_natr)
                                    
                                    diff = abs(discrete_prob - continuous_val)
                                    item = {
                                        "title": f"{reg} en {day}",
                                        "desc": f"El Heatmap discreto registra un <b>{discrete_prob:.0f}%</b> de cierres (n={n}), confluente con un <b>{continuous_val:.0f}%</b> en la superficie continua suavizada.",
                                        "discrete": discrete_prob,
                                        "diff": diff,
                                        "type": "strong"
                                    }
                                    if diff < 12.0 and discrete_prob >= 65.0:
                                        confluences.append(item)
                                    elif diff >= 20.0 and n < 15:
                                        item["desc"] = f"El Heatmap muestra una probabilidad exagerada de <b>{discrete_prob:.0f}%</b> debido a muestra baja (n={n}). La superficie 3D suaviza la expectativa real a solo <b>{continuous_val:.0f}%</b>."
                                        item["type"] = "noise"
                                        noises.append(item)
                                        
                        # 2. Gap Size x Weekday Scan
                        size_buckets = [
                            { "label": "< 0.25 ATR", "min": 0, "max": 0.25 },
                            { "label": "0.25 – 0.50", "min": 0.25, "max": 0.50 },
                            { "label": "0.50 – 0.75", "min": 0.50, "max": 0.75 },
                            { "label": "0.75 – 1.00", "min": 0.75, "max": 1.00 },
                            { "label": "> 1.00 ATR", "min": 1.00, "max": float('inf') }
                        ]
                        for bucket in size_buckets:
                            for day in weekdays:
                                cell_points = [
                                    p for p in points 
                                    if p['weekday_name'] == day and bucket["min"] <= abs(p['gap_size_atr']) < bucket["max"]
                                ]
                                n = len(cell_points)
                                if n >= 6:
                                    filled = len([p for p in cell_points if p['fill_depth'] >= min_fill_target])
                                    discrete_prob = (filled / n) * 100.0
                                    
                                    avg_gap = np.mean([p['gap_size_atr'] for p in cell_points])
                                    avg_natr = np.mean([p['natr'] for p in cell_points])
                                    continuous_val = get_nearest_surface_val(avg_gap, avg_natr)
                                    
                                    diff = abs(discrete_prob - continuous_val)
                                    item = {
                                        "title": f"Gap {bucket['label']} en {day}",
                                        "desc": f"El Heatmap discreto muestra un <b>{discrete_prob:.0f}%</b> de éxito (n={n}), validado por un <b>{continuous_val:.0f}%</b> en la superficie 3D continua.",
                                        "discrete": discrete_prob,
                                        "diff": diff,
                                        "type": "strong"
                                    }
                                    if diff < 12.0 and discrete_prob >= 65.0:
                                        confluences.append(item)
                                    elif diff >= 20.0 and n < 15:
                                        item["desc"] = f"El Heatmap muestra una probabilidad aparente de <b>{discrete_prob:.0f}%</b> (n={n}). La superficie continua 3D revela que la expectativa de reversión real es de solo <b>{continuous_val:.0f}%</b>."
                                        item["type"] = "noise"
                                        noises.append(item)
                    except Exception as ex:
                        print(f"Error calculando confluencias: {type(ex).__name__} (detalles omitidos por seguridad)")

                # Generar HTML para la sección de confluencias
                confluence_cards_html = ""
                
                # Obtener top 2 confluencias fuertes
                top_confluences = sorted(confluences, key=lambda x: x["discrete"], reverse=True)[:2]
                for c in top_confluences:
                    confluence_cards_html += f"<div class='confluence-card strong'>" \
                                             f"  <div class='confluence-header'>" \
                                             f"    <span class='confluence-title'>{c['title']}</span>" \
                                             f"    <span class='confluence-badge strong'>Confluencia</span>" \
                                             f"  </div>" \
                                             f"  <div class='confluence-desc'>{c['desc']}</div>" \
                                             f"</div>"
                                             
                # Obtener top 1 ruido detectado
                top_noises = sorted(noises, key=lambda x: x["diff"], reverse=True)[:1]
                for n in top_noises:
                    confluence_cards_html += f"<div class='confluence-card noise'>" \
                                             f"  <div class='confluence-header'>" \
                                             f"    <span class='confluence-title'>{n['title']}</span>" \
                                             f"    <span class='confluence-badge noise'>Ruido Muestral</span>" \
                                             f"  </div>" \
                                             f"  <div class='confluence-desc'>{n['desc']}</div>" \
                                             f"</div>"
                                             
                if not confluence_cards_html:
                    confluence_cards_html = "<div style='font-size:10px; color:#64748b; font-style:italic;'>No se detectaron zonas de confluencia clara para el conjunto de datos de este activo.</div>"
                    
                confluence_section_html = f"<div class='confluence-section'>" \
                                          f"  <h4>Filtro de Confluencia (Superficie ↔ Heatmaps)</h4>" \
                                          f"  {confluence_cards_html}" \
                                          f"</div>"

                # Section 1: Veredicto
                verdict_html = f"<div class='verdict-box {semaforo}'>" \
                               f"  <span class='verdict-label {semaforo}'>{semaforo_label}</span>" \
                               f"  <div class='verdict-text'>{plain_desc}</div>" \
                               f"  <div class='action-row'>" \
                               f"    <div class='action-col do'><b>Operar</b>{operar_desc}</div>" \
                               f"    <div class='action-col dont'><b>Evitar</b>{evitar_desc}</div>" \
                               f"  </div>" \
                               f"</div>"

                # Section 2: Narrativa
                narrative_html = f"<div class='narrative-section'>" \
                                 f"  <div class='narrative-item'>" \
                                 f"    <h5>La Montaña (Cima)</h5>" \
                                 f"    <p>El punto óptimo de reversión está en un gap de <b>{x_max:.2f} ATR</b> con volatilidad de <b>{y_max:.2f}%</b>, donde la probabilidad de cierre alcanza su máximo de <b>{max_val:.1f}%</b>.</p>" \
                                 f"  </div>" \
                                 f"  <div class='narrative-item'>" \
                                 f"    <h5>El Valle (Escape)</h5>" \
                                 f"    <p>La zona de menor probabilidad (<b>{min_val:.1f}%</b>) se localiza en gap de <b>{x_min:.2f} ATR</b> y volatilidad de <b>{y_min:.2f}%</b>. En esta área el gap tiende a sostenerse e iniciar tendencias.</p>" \
                                 f"  </div>" \
                                 f"  <div class='narrative-item'>" \
                                 f"    <h5>La Pendiente (Sensibilidad)</h5>" \
                                 f"    <p>La superficie indica que {sens_desc}</p>" \
                                 f"  </div>" \
                                 f"  <div class='narrative-item'>" \
                                 f"    <h5>La Asimetría (Sesgo)</h5>" \
                                 f"    <p>Las aperturas alcistas muestran un promedio de cierre de <b>{pos_mean:.1f}%</b> frente a un <b>{neg_mean:.1f}%</b> de las aperturas bajistas.</p>" \
                                 f"  </div>" \
                                 f"</div>"

                # Section 3: Referencia Técnica
                technical_html = f"<button id='reference-tech-btn' class='reference-toggle-btn' onclick='toggleTechnicalReference()'>Ver datos técnicos</button>" \
                                 f"<div id='reference-tech-content' class='reference-content'>" \
                                 f"  <table class='summary-table' style='width:100%; border-collapse:collapse; font-size:11px; margin-bottom:15px;'>" \
                                 f"    <tr style='border-bottom:1px solid #eee; background:#f8fafc;'><th style='padding:5px; text-align:left;'>Descriptor Geométrico</th><th style='padding:5px; text-align:right;'>Valor</th></tr>" \
                                 f"    <tr style='border-bottom:1px solid #eee;'><td style='padding:5px;'>Cima de Reversión (SDFP Máx)</td><td style='padding:5px; text-align:right;'><b>{max_val:.1f}%</b> (Gap: {x_max:.2f} ATR | Vol: {y_max:.2f}%)</td></tr>" \
                                 f"    <tr style='border-bottom:1px solid #eee;'><td style='padding:5px;'>Valle de Fuga (SDFP Mín)</td><td style='padding:5px; text-align:right;'><b>{min_val:.1f}%</b> (Gap: {x_min:.2f} ATR | Vol: {y_min:.2f}%)</td></tr>" \
                                 f"    <tr style='border-bottom:1px solid #eee;'><td style='padding:5px;'>Área Eficiente (SDFP &ge; 80%)</td><td style='padding:5px; text-align:right;'><b>{efficient_pct:.1f}% del dominio</b></td></tr>" \
                                 f"    <tr style='border-bottom:1px solid #eee;'><td style='padding:5px;'>Ratio de Gradiente (dX/dY)</td><td style='padding:5px; text-align:right;'><b>{ratio:.2f}</b></td></tr>" \
                                 f"  </table>" \
                                 f"</div>"

                # Section 4: Botón "Leer Informe Antigravity"
                report_btn_html = f"<div style='border-top: 1px solid #eaecef; padding-top: 12px; margin-top: 15px; text-align: center;'>" \
                                  f"  <button onclick='syncAntigravity()' style='background:#1e293b; color:#ffffff; border:none; padding:6px 12px; border-radius:4px; font-size:11px; font-family:\"Inter\", sans-serif; font-weight:600; cursor:pointer; width:100%; transition: background 0.2s ease;' onmouseover='this.style.background=\"#0f172a\"' onmouseout='this.style.background=\"#1e293b\"'>Leer Informe Antigravity</button>" \
                                  f"  <div style='font-size:9px; color:#94a3b8; margin-top:4px;'>Requiere análisis previo solicitado al agente en el IDE</div>" \
                                  f"</div>"

                ai_text = f"<h3>Geometría de Superficie: {asset_name}</h3>" + verdict_html + narrative_html + confluence_section_html + technical_html + report_btn_html

                
                request_data = {
                    "type": "3d_surface_interpretation",
                    "asset": asset_name,
                    "min_fill_target": min_fill_target,
                    "max_val": float(max_val),
                    "x_max": float(x_max),
                    "y_max": float(y_max),
                    "min_val": float(min_val),
                    "x_min": float(x_min),
                    "y_min": float(y_min),
                    "ratio": float(ratio),
                    "efficient_pct": float(efficient_pct),
                    "x_grid": x_grid,
                    "y_grid": y_grid,
                    "z_matrix": z_matrix
                }
                with open(config.BRIDGE_REQUEST_PATH, "w", encoding="utf-8") as f:
                    json.dump(request_data, f, indent=4)
                
                response_data = {
                    "max_sdfp": f"{max_val:.1f}",
                    "min_sdfp": f"{min_val:.1f}",
                    "ai_raw_text": ai_text
                }
                with open(config.BRIDGE_RESPONSE_PATH, "w", encoding="utf-8") as f:
                    json.dump(response_data, f, indent=4)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
                
            except Exception as err:
                print(f"Error analizando superficie 3D: {type(err).__name__} (detalles omitidos por seguridad)")
                self.send_error_response(500, f"Error analizando superficie 3D: {type(err).__name__}")
        else:
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()

    def send_error_response(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))

def main():
    # Permitir reutilizar el puerto inmediatamente
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), VolatilityAPIHandler) as httpd:
        print(f"🚀 Servidor API de Volatilidad QRT corriendo en http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nApagando servidor...")
            httpd.shutdown()

if __name__ == "__main__":
    main()
