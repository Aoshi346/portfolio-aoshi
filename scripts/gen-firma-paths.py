#!/usr/bin/env python3
"""
Genera `src/themes/caelestia.firma.ts` — los contornos de Fraunces para el
trazo del nombre de la escena Titulo.

NO es una tipografia de imitacion: son los contornos reales de Fraunces
instanciada en opsz 9 / wght 900 / SOFT 0 / WONK 1, los mismos ejes que usa la
firma en reposo.

Se corre a mano cuando cambie `identity.name` o los ejes del display. El
resultado se COMMITEA: no hay descarga en tiempo de ejecucion.

    python3 -m venv /tmp/fenv && /tmp/fenv/bin/pip install fonttools
    curl -sL -o /tmp/fraunces.ttf \\
      'https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf'
    /tmp/fenv/bin/python scripts/gen-firma-paths.py /tmp/fraunces.ttf
"""
import re
import sys

from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

TEXTO = "Aoshi Blanco Sanz"
EJES = {"opsz": 9, "wght": 900, "SOFT": 0, "WONK": 1}
TAM = 100
DESTINO = "src/themes/caelestia.firma.ts"


def main(ttf: str) -> int:
    fuente = instantiateVariableFont(TTFont(ttf), EJES, inplace=True)
    glifos, cmap = fuente.getGlyphSet(), fuente.getBestCmap()
    upem, hmtx = fuente["head"].unitsPerEm, fuente["hmtx"]

    escala, x, salida = TAM / upem, 0.0, []
    for ch in TEXTO:
        nombre = cmap.get(ord(ch))
        if nombre is None:
            x += TAM * 0.30
            continue
        pluma = SVGPathPen(glifos)
        glifos[nombre].draw(TransformPen(pluma, Transform(escala, 0, 0, -escala, x, 0)))
        d = pluma.getCommands()
        if d:
            # Dos decimales: el trazo se dibuja a 780 px de ancho, asi que la
            # tercera cifra es ruido y son 8 KB menos en el bundle.
            #
            # UN SOLO regex sobre TODO el string, no un tokenizado por
            # espacios: fontTools no separa un numero de la letra de comando
            # que lo precede ("H47.05", "Q25.9…"), que es el primer numero de
            # CASI TODO segmento de trazo. El tokenizado por espacios (con el
            # truco de separar "-" a mano) solo redondeaba los numeros que ya
            # llevaban un espacio real delante — negativos separados por el
            # truco, y positivos que por casualidad no seguian a una letra
            # pegada. 543 numeros de la firma real se colaban enteros, con
            # los 15-17 digitos de ruido de un float64.
            d = re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.2f}", d)
            salida.append({"c": ch, "d": d})
        x += hmtx[nombre][0] * escala

    with open(DESTINO, "w", encoding="utf-8") as f:
        f.write(
            "/* GENERADO por scripts/gen-firma-paths.py — no editar a mano. */\n"
            "export interface Glifo {\n  readonly c: string;\n  readonly d: string;\n}\n\n"
            "export const FIRMA: { readonly ancho: number; readonly glifos: readonly Glifo[] } = {\n"
            f"  ancho: {x:.1f},\n  glifos: [\n"
        )
        for g in salida:
            f.write(f'    {{ c: {g["c"]!r}, d: "{g["d"]}" }},\n'.replace("'", '"'))
        f.write("  ],\n};\n")

    print(f"{DESTINO}: {len(salida)} glifos, ancho {x:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "/tmp/fraunces.ttf"))
