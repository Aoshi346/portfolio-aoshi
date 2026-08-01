"""Arnes de la escena de contacto: geometria, dianas, contraste y reduced motion.

Criterios 1, 2, 3, 4, 5 y 7 del spec
docs/superpowers/specs/2026-07-30-contacto-carta-de-ajuste-design.md

El contraste se muestrea sobre el pixel RENDERIZADO, con el shader corriendo, en
tres fotogramas separados 2 s: el fondo es generativo y su luminancia se mueve.
Un solo fotograma no mide nada.
"""
import io
import sys
from PIL import Image
from playwright.sync_api import sync_playwright

DIANA_MIN = 24        # px CSS, WCAG 2.2 AA SC 2.5.8
HUECO_MAX = 120       # px sobre la primera letra
OCUPACION_MIN = 0.35  # fraccion del encuadre
CONTRASTE_MIN = 4.5
FOTOGRAMAS = 3


def luminancia(c):
    def canal(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * canal(c[0]) + 0.7152 * canal(c[1]) + 0.0722 * canal(c[2])


def ratio(a, b):
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def main() -> int:
    fallos = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto("http://localhost:4173/?theme=vice", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(9000)
        pg.evaluate("""() => {
            const s = document.querySelector('[data-scene="contacto"]');
            window.scrollTo({top: s.getBoundingClientRect().top + scrollY, behavior: 'instant'});
        }""")
        pg.wait_for_timeout(3500)

        geo = pg.evaluate("""() => {
            const vw = innerWidth, vh = innerHeight;
            const escena = document.querySelector('[data-scene="contacto"]');
            const titulo = document.querySelector('.contacto-title');
            const banda = document.querySelector('.contacto-band');
            const barras = [...document.querySelectorAll('.contacto-bar')];
            const tinta = [banda, ...barras].reduce((acc, n) => {
                const r = n.getBoundingClientRect();
                return acc + Math.max(0, r.width) * Math.max(0, r.height);
            }, 0);
            return {
                hueco_superior: titulo.getBoundingClientRect().top - escena.getBoundingClientRect().top,
                ocupacion: tinta / (vw * vh),
                dianas: barras.map(n => {
                    const r = n.getBoundingClientRect();
                    return [Math.round(r.width), Math.round(r.height)];
                }),
                valores: [...document.querySelectorAll('.contacto-bar-value')].map(n => {
                    const r = n.getBoundingClientRect();
                    return {x: r.left - 6, y: r.top + r.height / 2, color: getComputedStyle(n).color};
                }),
                estado: (() => {
                    const n = document.querySelector('.contacto-estado-value');
                    const r = n.getBoundingClientRect();
                    return {x: r.left + r.width * 0.3, y: r.top + r.height * 0.22,
                            color: getComputedStyle(n).color};
                })(),
            };
        }""")

        if geo["hueco_superior"] > HUECO_MAX:
            fallos.append(f"hueco_superior {geo['hueco_superior']:.0f} px > {HUECO_MAX}")
        if geo["ocupacion"] < OCUPACION_MIN:
            fallos.append(f"ocupacion {geo['ocupacion']:.1%} < {OCUPACION_MIN:.0%}")
        for i, (w, h) in enumerate(geo["dianas"]):
            if w < DIANA_MIN or h < DIANA_MIN:
                fallos.append(f"diana de la barra {i}: {w}x{h} px")

        # Contraste sobre el pixel renderizado, tres fotogramas separados 2 s.
        puntos = [(v["x"], v["y"], v["color"], f"valor {i}") for i, v in enumerate(geo["valores"])]
        puntos.append((geo["estado"]["x"], geo["estado"]["y"], geo["estado"]["color"], "estado"))
        for n in range(FOTOGRAMAS):
            im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
            for x, y, color, nombre in puntos:
                fondo = im.getpixel((int(x), int(y)))
                fg = tuple(int(v) for v in color.replace("rgb(", "").replace(")", "").split(",")[:3])
                r = ratio(fg, fondo)
                if r < CONTRASTE_MIN:
                    fallos.append(f"fotograma {n}: {nombre} {r:.1f}:1 < {CONTRASTE_MIN}")
                else:
                    print(f"OK fotograma {n} {nombre}: {r:.1f}:1")
            pg.wait_for_timeout(2000)
        pg.close()

        # Movimiento reducido: el hover no mueve nada.
        pg = b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        pg.goto("http://localhost:4173/?theme=vice", wait_until="networkidle", timeout=30000)
        pg.wait_for_timeout(3000)
        antes = pg.evaluate("""() => document.querySelector('.contacto-bar')
            .getBoundingClientRect().width""")
        pg.hover(".contacto-bar")
        pg.wait_for_timeout(900)
        despues = pg.evaluate("""() => document.querySelector('.contacto-bar')
            .getBoundingClientRect().width""")
        if abs(antes - despues) > 1:
            fallos.append(f"reduced motion: la barra se movio {antes:.0f} -> {despues:.0f}")
        else:
            print(f"OK reduced motion: la barra no se mueve ({antes:.0f} px)")
        pg.close()
        b.close()

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} criterios incumplidos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
