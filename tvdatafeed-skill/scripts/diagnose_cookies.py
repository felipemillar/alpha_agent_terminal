import sys
import os

# Asegurar que el path de src esté disponible
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    import rookiepy
except ImportError:
    print("[-] rookiepy no está instalado en el entorno virtual.")
    sys.exit(1)

from src.auth.browser_cookies import _validate_sessionid

extractors = [
    ("Firefox", rookiepy.firefox),
    ("Edge", rookiepy.edge),
    ("Brave", rookiepy.brave),
    ("Chrome", rookiepy.chrome),
    ("Opera", rookiepy.opera),
    ("Vivaldi", rookiepy.vivaldi),
    ("Safari", rookiepy.safari),
    ("Chromium", rookiepy.chromium),
]

print("=== DIAGNÓSTICO DE COOKIES DE TRADINGVIEW ===")
print(f"Sistema Operativo: {sys.platform}")
print(f"Versión de Python: {sys.version}\n")

found_any = False

for name, load_cookies in extractors:
    try:
        cookies = load_cookies(domains=["tradingview.com"])
        print(f"[+] {name}: Conexión exitosa a la base de datos de cookies.")
        
        sessionid = None
        for cookie in cookies:
            c_name = cookie.get("name")
            c_value = cookie.get("value")
            c_domain = cookie.get("domain", "")
            
            if c_name == "sessionid" and "tradingview.com" in c_domain:
                sessionid = c_value
                break
                
        if sessionid:
            valid = _validate_sessionid(sessionid)
            print(f"    -> ¡sessionid encontrado! (Validez: {valid}, Longitud: {len(sessionid)})")
            found_any = True
        else:
            print("    -> Conexión exitosa, pero no se encontró la cookie 'sessionid' para tradingview.com.")
            print("       (Asegúrate de tener la sesión iniciada en este navegador).")
            
    except Exception as e:
        err_type = type(e).__name__
        print(f"[-] {name}: Falló la extracción ({err_type}).")
        # Mostrar detalles amigables sobre fallos comunes
        if "CryptProtectData" in str(e) or "App-Bound" in str(e) or "decryption" in str(e).lower():
            print("    -> Causa probable: Cifrado del navegador (App-Bound Encryption o DPAPI restringido).")
        elif "No such file" in str(e) or "find" in str(e).lower():
            print("    -> Causa probable: El navegador no está instalado o no se encontró su perfil.")
        else:
            print(f"    -> Detalle: {str(e)[:100]}")

print("\n=============================================")
if found_any:
    print("[ÉXITO] Al menos un navegador tiene una sesión de TradingView extraible.")
else:
    print("[FALLO] No se pudo extraer ninguna sesión activa de ningún navegador.")
    print("Recomendación para Windows: Instala Firefox, inicia sesión en tradingview.com, y vuelve a intentar.")
