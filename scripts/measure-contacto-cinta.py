"""Contraste y caja de la cinta de contacto en Hyprland.

Nacio del defecto medido el 2026-08-13: los cuatro rotulos de la cinta salian
a 2,19-2,94:1 porque `.contacto-bar-label` heredaba `opacity: 0.6` de
style.css y el bloque de Hyprland nunca resetea la opacidad, cosa que Vice si
hace. Mide POR GLIFO: el haz del shader cruza la calle central vacia, asi que
medir el rectangulo entero sobreestima el contraste.

  npm run build && npx vite preview --port 4173 &
  python3 scripts/measure-contacto-cinta.py --base http://localhost:4173
"""
import argparse, sys
from playwright.sync_api import sync_playwright

MIN_AA = 4.5

def luminancia(rgb):
    def c(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (c(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(a, b):
    la, lb = luminancia(a), luminancia(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://localhost:4173")
    args = p.parse_args()
    fallos = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(f"{args.base}/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(9000)
        pg.evaluate("document.querySelector('[data-scene=\"contacto\"]').scrollIntoView()")
        pg.wait_for_timeout(2500)   # Lenis sigue desplazando despues de scrollIntoView
        datos = pg.evaluate("""() => {
          const sel = ['.contacto-bar-label', '.contacto-bar-value',
                       '.contacto-estado-label', '.contacto-estado-value'];
          return sel.flatMap(s => [...document.querySelectorAll(s)].map(n => {
            const r = document.createRange(); r.selectNodeContents(n);
            const c = r.getBoundingClientRect();
            return {sel: s, color: getComputedStyle(n).color,
                    caja: {x: c.x, y: c.y, w: c.width, h: c.height}};
          }));
        }""")
        from PIL import Image
        import io
        for d in datos:
            c = d["caja"]
            if c["w"] < 1 or c["h"] < 1:
                fallos.append(f"{d['sel']}: caja vacia"); continue
            # Recorte a la caja del TEXTO: el pixel mas claro y el mas oscuro
            # dentro de ella son el glifo y el fondo que de verdad tiene debajo.
            png = pg.screenshot(clip={"x": c["x"], "y": c["y"],
                                      "width": c["w"], "height": c["h"]})
            pix = list(Image.open(io.BytesIO(png)).convert("RGB").getdata())
            r = ratio(max(pix, key=luminancia), min(pix, key=luminancia))
            print(f"  {'OK ' if r >= MIN_AA else 'FALLA'} {d['sel']:26} {r:.2f}:1")
            if r < MIN_AA:
                fallos.append(f"{d['sel']} a {r:.2f}:1 (minimo {MIN_AA})")
        caja = pg.evaluate("""() => {
          const bars = document.querySelector('.contacto-bars');
          const sec = document.querySelector('[data-scene="contacto"]');
          const v = document.querySelector('.contacto-bar--correo .contacto-bar-value');
          const r = document.createRange(); r.selectNodeContents(v);
          const ren = [...r.getClientRects()].filter(x => x.width > 1);
          return {pie: Math.round(sec.getBoundingClientRect().bottom
                                  - bars.getBoundingClientRect().bottom),
                  renglones: ren.length,
                  correo: Math.round(Math.max(...ren.map(x => x.width))),
                  alto: Math.round(bars.getBoundingClientRect().height)};
        }""")
        print("  cinta:", caja)
        if caja["renglones"] != 1:
            fallos.append(f"el correo cae en {caja['renglones']} renglones")
        if abs(caja["pie"]) > 1:
            fallos.append(f"la cinta no esta al pie de la seccion ({caja['pie']}px)")
        if caja["alto"] != 167:
            fallos.append(f"alto de cinta {caja['alto']}, esperado 167")
        junta = pg.evaluate("""() => {
          const sec = document.querySelector('[data-scene="contacto"]');
          // La franja se lee del DOM, no se escribe 27 a pelo: un umbral fijo
          // deja de medir el diseno en cuanto alguien cambia la variable.
          const fr = parseFloat(getComputedStyle(sec).getPropertyValue('--franja-h'));
          const e = document.querySelector('.contacto-estado').getBoundingClientRect();
          const b = document.querySelector('.contacto-bars').getBoundingClientRect();
          return {franja: fr,
                  separacion: Math.round(e.bottom - (b.top + fr)),
                  derecha: Math.round(b.right - e.right)};
        }""")
        print("  junta franja/cinta:", junta)
        if abs(junta["separacion"]) > 1:
            fallos.append(f"la franja de estado se separo de la cinta ({junta['separacion']}px)")

        # Segunda pasada: el mosaico movil (Task 4). Nunca con un div de
        # 390px dentro de una ventana ancha -- vw/vh se resuelven contra la
        # ventana real, no contra el div, y las medidas salen falsas.
        pg390 = b.new_page(viewport={"width": 390, "height": 844})
        pg390.goto(f"{args.base}/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
        pg390.wait_for_timeout(9000)
        pg390.evaluate("document.querySelector('[data-scene=\"contacto\"]').scrollIntoView()")
        pg390.wait_for_timeout(2500)
        m = pg390.evaluate("""() => {
          const v = document.querySelector('.contacto-bar--correo .contacto-bar-value');
          const r = document.createRange(); r.selectNodeContents(v);
          const ren = [...r.getClientRects()].filter(x => x.width > 1);
          const calle = parseFloat(getComputedStyle(
            document.querySelector('.contacto-bar--correo')).paddingLeft);
          return {calle, util: 390 - 2 * calle,
                  renglones: ren.length,
                  correo: Math.round(Math.max(...ren.map(x => x.width))),
                  bandas: [...document.querySelectorAll('[class*="contacto-bar--"]')]
                            .map(n => Math.round(n.getBoundingClientRect().height))};
        }""")
        print("  movil 390:", m)
        if m["renglones"] != 1:
            fallos.append(f"movil: el correo cae en {m['renglones']} renglones")
        if min(m["bandas"]) < 56:
            fallos.append(f"movil: banda de {min(m['bandas'])}px, minimo 56 (WCAG 2.2 SC 2.5.8)")
        # Misma asercion de junta que en escritorio: el estado va en absoluto y
        # tiene que coronar el mosaico, no quedarse detras del lead.
        j390 = pg390.evaluate("""() => {
          const e = document.querySelector('.contacto-estado').getBoundingClientRect();
          const b = document.querySelector('.contacto-bars').getBoundingClientRect();
          return Math.round(e.bottom - b.top);
        }""")
        print("  junta movil:", j390)
        if abs(j390) > 1:
            fallos.append(f"movil: el estado no corona el mosaico ({j390}px de separacion)")
        pg390.screenshot(path="/tmp/cinta-movil.png", full_page=False)

        print("fallos:", fallos or "ninguno")
        b.close()
    return 1 if fallos else 0

if __name__ == "__main__":
    sys.exit(main())
