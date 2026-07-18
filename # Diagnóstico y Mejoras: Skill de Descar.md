# Diagnóstico y Mejoras: Skill de Descarga de Datos (tvdatafeed-skill)

## Contexto del Proyecto

El proyecto **Alpha Agent Terminal** incluye una skill modular (`tvdatafeed-skill/`) cuyo objetivo es descargar datos históricos de TradingView de forma portable, sin requerir credenciales hardcodeadas. Al intentar ejecutar la descarga de `META (NASDAQ)` con velas diarias y 5000 barras, la skill falló consistentemente con el mensaje:

```json
{"status": "error", "files": [], "error_message": "Fallo al conectar con TradingView"}
```

---

## Arquitectura de Autenticación Actual

La skill utiliza una **cadena de prioridad de 5 pasos** definida en `scripts/src/settings.py → resolve_auth_token()`:

| Paso | Fuente | Comportamiento |
|------|--------|----------------|
| 1 | Cache local de JWT (archivo en disco) | Omitido — primera ejecución, sin cache previo |
| 2 | `.env` → `TV_AUTH_TOKEN` como JWT largo (>500 chars) | Omitido — no configurado |
| 3 | `.env` → `TV_AUTH_TOKEN` como sessionid corto | Omitido — no configurado |
| **4** | **Extracción automática de cookies del navegador** | **FALLA — ver causas abajo** |
| 5 | Fallback a cache expirado | Omitido — sin cache |

El sistema falla en el **Paso 4** y no tiene recuperación, por lo que `connect()` retorna `False` y la extracción aborta.

---

## Causas Raíz del Fallo

### Causa 1 — `browser_cookie3` no está en `requirements.txt`
La librería que implementa la extracción de cookies del navegador (`browser_cookie3`) **no está declarada como dependencia** en `tvdatafeed-skill/requirements.txt`. El código en `scripts/src/auth/browser_cookies.py` la importa con un `try/except ImportError` que silencia el error y retorna `None`.

```python
# browser_cookies.py — línea 58
try:
    import browser_cookie3
except ImportError:
    logger.warning("La librería browser-cookie3 no está instalada.")
    return None  # ← Falla silenciosamente, sin alertar al usuario
```

### Causa 2 — Chrome ≥ v127 en Windows cifra las cookies con App-Bound Encryption
A partir de Chrome 127, Google introdujo **App-Bound Encryption** (cifrado DPAPI vinculado al proceso del navegador). Esto hace que `browser_cookie3` —y su sucesor `rookiepy`— **no puedan descifrar las cookies de Chrome** en Windows sin elevar privilegios o usar workarounds específicos de versión.

### Causa 3 — Sin degradación elegante (no hay wizard de fallback)
Cuando todos los pasos de la cadena fallan, la skill no ofrece ninguna alternativa interactiva al usuario. Simplemente termina con un error genérico, sin indicar qué hacer para resolverlo.

---

## Problemas Secundarios Detectados (misma sesión)

| Problema | Archivo | Descripción |
|---|---|---|
| `pandas==3.0.3` incompatible | `tvdatafeed-skill/requirements.txt` y `requirements.txt` raíz | `pandas 3.x` requiere Python ≥ 3.11. El sistema corre Python 3.10.11. Corregido cambiando a `pandas` sin versión fija. |
| `numpy==2.5.1` incompatible | `requirements.txt` raíz | Misma causa. Corregido. |
| Emoji en `server.py` | `src/server.py` línea 954 | `print(f"🚀 Servidor...")` causaba `UnicodeEncodeError` en la consola cp1252 de Windows, impidiendo que el servidor arrancara. Corregido eliminando el emoji. |

---

## Opciones de Mejora Propuestas

### Opción A — Reemplazar `browser_cookie3` por `rookiepy` (mejora incremental)
`rookiepy` es el sucesor activo con mejor soporte para navegadores modernos.

- **Ventaja:** Cero fricción para el usuario si Chrome está instalado y la sesión es accesible.
- **Desventaja:** Sigue siendo frágil en Chrome ≥ v127 en Windows por App-Bound Encryption.
- **Acción:** Agregar `rookiepy` a `requirements.txt` y actualizar `browser_cookies.py`.

### Opción B — Wizard de Setup Asistido con `keyring` (recomendada para portabilidad)
Un script de configuración único (`scripts/setup_auth.py`) que guía al usuario para que copie manualmente el `sessionid` desde las DevTools del navegador (F12 → Application → Cookies → tradingview.com) y lo almacena cifrado en el **Credential Manager del OS** usando la librería `keyring`.

```bash
# El usuario ejecuta una sola vez:
.venv/Scripts/python scripts/setup_auth.py --sessionid "abc123xyz..."
```

- **Ventaja:** 100% portable (Windows/Mac/Linux). No depende del navegador instalado. El sessionid de TradingView dura semanas.
- **Desventaja:** Requiere una acción manual inicial del usuario.
- **Seguridad:** El token se guarda cifrado por el OS (Windows Credential Manager / macOS Keychain / libsecret en Linux), nunca en texto plano en disco.

### Opción C — Cadena híbrida A + B con degradación elegante (solución completa)
Combinar ambas opciones y añadir un **fallback interactivo** cuando la extracción automática falla:

```
1. Cache local cifrado (keyring)
2. rookiepy → extracción automática del navegador
3. Si falla → wizard interactivo: instrucciones precisas + input del usuario → cifrado + cache
4. Fallback: cache expirado como último recurso
```

Esto garantiza que la skill **nunca termina con un error silencioso**: o funciona automáticamente, o le explica exactamente al usuario qué hacer.

---

## Estado Actual de los Archivos Clave

| Archivo | Estado |
|---|---|
| `tvdatafeed-skill/requirements.txt` | `pandas` sin versión fija (corregido). Falta `browser_cookie3` o `rookiepy`. |
| `tvdatafeed-skill/scripts/src/auth/browser_cookies.py` | Implementado pero dependencia ausente. Lógica de extracción funcional para Mac/Linux. |
| `tvdatafeed-skill/scripts/src/settings.py` | Cadena de auth de 5 pasos implementada. Sin wizard de fallback. |
| `tvdatafeed-skill/.env` | No existe (el usuario no lo ha creado desde `.env.example`). |

---

## Próximos Pasos Sugeridos

1. **Implementar Opción C** — cadena híbrida con wizard interactivo y `keyring`.
2. **Agregar `rookiepy`** a `requirements.txt` como primera línea de defensa automática.
3. **Crear `scripts/setup_auth.py`** — script de onboarding para configurar el sessionid manualmente de forma segura.
4. **Mejorar el mensaje de error** en `extractor.py` para que, cuando falla la conexión, imprima instrucciones claras en lugar del mensaje genérico actual.
