# Calibración del Pilar 2: Riesgo de Cola

**Fecha de calibración:** 2026-08-04
**Estado:** ACTIVO (P2.01, P2.02, P2.03, P2.04)

## Protocolo de pruebas (BTCUSD)

1. **Endpoint API:** `GET /api/adn/pilar2?asset=BTCUSD`
2. **Validaciones cruzadas:**
   - Asimetría global: -0.0527
   - Curtosis global: 5.4158 (Excede el umbral base 0, confirmando fat tails)
   - Lado Largo (Régimen Medio): ES al 5% estimado en ~ -5.60%, n_efectivo superando umbral de 20.
   - Lado Corto (Régimen Medio): ES al 5% estimado en ~ -6.21%, n_efectivo superando umbral de 20.

## Integración NLG

El flujo semántico en `generate_analysis.py` -> `expert_nlg.py` inyecta correctamente el ES 1D y activa la oración de fallback global si `n_efectivo < 20`. Se verificó que los umbrales directos de Z-Score y curtosis dirigen correctamente los condicionales de clase ("Retorno extremo", "colas gruesas").

## Nota Analítica: Razón Pérdida Esperada / VaR
De la evidencia recopilada se observa que la razón entre Pérdida Esperada (ES) y el umbral de pérdida extrema (VaR) se mantiene típicamente en torno a **~1.5**. 
**Precisión de auditoría:** Es crítico notar que este factor de 1.5 es un parámetro **incondicional (global)**. Al segmentar por regímenes condicionales de alta entropía (por ejemplo, en régimen ALTO u horizontes cortos), las colas se comprimen de manera diferente y la razón desciende (ej. ~1.36 para QQQ en ALTO a 1D). Por lo tanto, el múltiplo de 1.5 nunca debe ser usado como heurística para estimar ES condicional sin correr la muestra empírica.
