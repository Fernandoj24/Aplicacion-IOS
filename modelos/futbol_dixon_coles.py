#!/usr/bin/env python3
"""Poisson con corrección Dixon-Coles (rho=-0.08), matriz 10x10 normalizada.

Uso: python3 futbol_dixon_coles.py LAMBDA_LOCAL LAMBDA_VISITA
"""
import math
import sys

RHO = -0.08
N = 10
FRAC_1T = 0.44


def poisson(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def tau(i, j, lh, la, rho):
    if i == 0 and j == 0:
        return 1 - lh * la * rho
    if i == 0 and j == 1:
        return 1 + lh * rho
    if i == 1 and j == 0:
        return 1 + la * rho
    if i == 1 and j == 1:
        return 1 - rho
    return 1.0


def matriz(lh, la, rho=RHO, n=N):
    m = [[poisson(i, lh) * poisson(j, la) * tau(i, j, lh, la, rho)
          for j in range(n)] for i in range(n)]
    total = sum(sum(f) for f in m)
    return [[p / total for p in f] for f in m]


def suma(m, cond):
    return sum(p for i, f in enumerate(m) for j, p in enumerate(f) if cond(i, j))


def pct(x):
    return f"{x * 100:5.1f}%"


def resumen_1x2(m):
    return (suma(m, lambda i, j: i > j),
            suma(m, lambda i, j: i == j),
            suma(m, lambda i, j: i < j))


def tabla(titulo, filas):
    print(f"\n{titulo}")
    for nombre, p in filas:
        print(f"  {nombre:<22}{pct(p)}")


def main():
    if len(sys.argv) != 3:
        sys.exit("Uso: futbol_dixon_coles.py lambda_local lambda_visita")
    lh, la = float(sys.argv[1]), float(sys.argv[2])
    m = matriz(lh, la)
    pl, pe, pv = resumen_1x2(m)

    print(f"Dixon-Coles | λ local={lh:.2f}  λ visita={la:.2f}  rho={RHO}")
    tabla("1X2", [("Local", pl), ("Empate", pe), ("Visita", pv)])
    tabla("Doble oportunidad", [("1X (local o empate)", pl + pe),
                                ("12 (sin empate)", pl + pv),
                                ("X2 (empate o visita)", pe + pv)])

    tabla("Hándicap ±1.5", [
        ("Local -1.5", suma(m, lambda i, j: i - j >= 2)),
        ("Visita +1.5", suma(m, lambda i, j: i - j <= 1)),
        ("Local +1.5", suma(m, lambda i, j: i - j >= -1)),
        ("Visita -1.5", suma(m, lambda i, j: j - i >= 2)),
    ])

    filas = []
    for linea in (1.5, 2.5, 3.5, 4.5):
        over = suma(m, lambda i, j: i + j > linea)
        filas += [(f"Over {linea}", over), (f"Under {linea}", 1 - over)]
    tabla("Over/Under", filas)

    btts = suma(m, lambda i, j: i > 0 and j > 0)
    tabla("Ambos anotan", [("Sí", btts), ("No", 1 - btts)])

    top = sorted(((p, i, j) for i, f in enumerate(m) for j, p in enumerate(f)),
                 reverse=True)[:8]
    tabla("Top 8 marcadores exactos", [(f"{i}-{j}", p) for p, i, j in top])

    m1 = matriz(lh * FRAC_1T, la * FRAC_1T)
    a, b, c = resumen_1x2(m1)
    o05 = suma(m1, lambda i, j: i + j > 0.5)
    o15 = suma(m1, lambda i, j: i + j > 1.5)
    tabla(f"Primer tiempo ({FRAC_1T * 100:.0f}% de los goles)", [
        ("1T Local", a), ("1T Empate", b), ("1T Visita", c),
        ("1T Over 0.5", o05), ("1T Over 1.5", o15)])

    print("\nSensibilidad (equipo más fuerte)")
    fuerte = "local" if lh >= la else "visita"
    print(f"  Equipo fuerte: {fuerte}")
    print(f"  {'factor':<8}{'Local':>8}{'Empate':>8}{'Visita':>8}{'Over2.5':>9}")
    for f in (0.9, 1.0, 1.1):
        l2, a2 = (lh * f, la) if fuerte == "local" else (lh, la * f)
        ms = matriz(l2, a2)
        x, y, z = resumen_1x2(ms)
        o = suma(ms, lambda i, j: i + j > 2.5)
        print(f"  x{f:<7}{pct(x):>8}{pct(y):>8}{pct(z):>8}{pct(o):>9}")


if __name__ == "__main__":
    main()
