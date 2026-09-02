"""Genera dist/b2.html desde maqueta-b2/b2.html.

Dos cosas que ya fallaron y que aqui se comprueban SIEMPRE:

1. Una comilla invertida dentro del literal `const CSS = ...` cierra la
   plantilla y rompe el script entero. Paso dos veces (`outline`, `deformScale`
   escritos entre comillas invertidas en un comentario) y el sintoma es mudo:
   la escena se queda con su maquetacion vieja y no hay nada en pantalla que lo
   diga. Solo el `pageerror` de la consola lo caza.
2. Dos `polygon()` solo interpolan si tienen el MISMO numero de puntos. Con
   distinto numero el navegador no morfa: corta de golpe.
"""
import math
import pathlib
import sys

N = 240
RAIZ = pathlib.Path(__file__).resolve().parent.parent


def armonica(n, a, s):
    """r(t) = 1 + a*cos(n t) + s*cos(2n t) — las figuras con nombre de Material 3."""
    rmax = max(1 + a * math.cos(n * t) + s * math.cos(2 * n * t)
               for t in [i * 2 * math.pi / 2000 for i in range(2000)])
    puntos = []
    for i in range(N):
        t = i * 2 * math.pi / N
        r = (1 + a * math.cos(n * t) + s * math.cos(2 * n * t)) / rmax
        puntos.append(f'{50 + 50 * r * math.cos(t):.2f}% {50 + 50 * r * math.sin(t):.2f}%')
    return 'polygon(' + ', '.join(puntos) + ')'


def superelipse(pot):
    """|x|^pot + |y|^pot = 1. pot=2 es el circulo; pot=4, el icono de Material 3."""
    puntos = []
    for i in range(N):
        t = i * 2 * math.pi / N
        ct, st = math.cos(t), math.sin(t)
        x = math.copysign(abs(ct) ** (2 / pot), ct)
        y = math.copysign(abs(st) ** (2 / pot), st)
        puntos.append(f'{50 + 50 * x:.2f}% {50 + 50 * y:.2f}%')
    return 'polygon(' + ', '.join(puntos) + ')'


FIGURAS = {
    '__CIRCULO__': superelipse(2.0),
    '__SQUIRCLE__': superelipse(4.0),
    '__COOKIE__': armonica(12, -0.058, 0.012),
    '__TREBOL__': armonica(4, 0.265, -0.045),
}


def main():
    origen = RAIZ / 'maqueta-b2' / 'b2.html'
    html = origen.read_text()

    # --- Gate 1: ni una comilla invertida dentro del literal de CSS ---
    ini = html.index('  const CSS = `') + len('  const CSS = `')
    fin = html.index('`;', ini)
    sobras = html[ini:fin].count('`')
    if sobras:
        lineas = [f'    linea {i}: {l.strip()[:90]}'
                  for i, l in enumerate(html[ini:fin].split('\n'), 1) if '`' in l]
        print(f'ERROR: {sobras} comilla(s) invertida(s) dentro del literal de CSS.\n'
              + '\n'.join(lineas), file=sys.stderr)
        return 1

    # --- Gate 2: las cuatro figuras, con el mismo numero de puntos ---
    cuentas = {k: v.count('%') // 2 for k, v in FIGURAS.items()}
    if len(set(cuentas.values())) != 1:
        print(f'ERROR: las figuras no tienen el mismo numero de puntos: {cuentas}', file=sys.stderr)
        return 1

    for clave, valor in FIGURAS.items():
        if clave not in html:
            print(f'ERROR: la maqueta no usa {clave}', file=sys.stderr)
            return 1
        html = html.replace(clave, valor)

    (RAIZ / 'dist' / 'b2.html').write_text(html)
    print(f'dist/b2.html generado · 4 figuras a {cuentas["__COOKIE__"]} puntos · literal de CSS limpio')
    return 0


if __name__ == '__main__':
    sys.exit(main())
