"""Contraste, caja y barrido de ancho de la cinta de contacto en Hyprland.

Nacio del defecto medido el 2026-08-13: los cuatro rotulos de la cinta salian
a 2,19-2,94:1 porque `.contacto-bar-label` heredaba `opacity: 0.6` de
style.css y el bloque de Hyprland nunca resetea la opacidad, cosa que Vice si
hace. Mide POR GLIFO: el haz del shader cruza la calle central vacia, asi que
medir el rectangulo entero sobreestima el contraste.

Ampliado el mismo dia (F-01) con un barrido de ancho: el arnes solo media
1440 y 390, y por eso dejo pasar un defecto que solo aparece entre 901 y
1200px (la cinta pierde el `gap` real que da `.contacto-bars` y los cuatro
`.contacto-bar-value` se apelmazan en una sola cadena ilegible, y por debajo
de ~965px desborda el viewport). Ver `sweep_anchos()`.

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

# Barrido de ancho (F-01, 2026-08-13): `.contacto-bars` es una fila flex con
# `gap: normal` -- SIN gap real. Toda la separacion entre las cuatro columnas
# sale del hueco sobrante despues de sumar los cuatro `.contacto-bar-value`.
# A --t-4 (28,43px) los cuatro suman 896px; contra el content-box
# (viewport - 2*7vw) eso deja gap 0 entre 901 y 1024px, y desborda el
# viewport por debajo de ~965px. El arnes solo media 1440 y 390 -- exactamente
# el hueco por el que se colo el defecto. GAP_MIN_PX es deliberadamente bajo
# (8px): no exige "bonito", exige que dos valores contiguos sean visualmente
# dos cadenas, no una sola corrida sin espacio (el caso medido era 0px).
SWEEP_WIDTHS = [901, 960, 1024, 1100, 1200, 1280, 1366, 1440]
GAP_MIN_PX = 8

def sweep_anchos(pw, base):
    fallos = []
    b = pw.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for w in SWEEP_WIDTHS:
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.goto(f"{base}/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(9000)
        pg.evaluate("document.querySelector('[data-scene=\"contacto\"]').scrollIntoView()")
        pg.wait_for_timeout(2500)
        datos = pg.evaluate("""() => {
          const scrollW = document.documentElement.scrollWidth;
          const viewportW = window.innerWidth;
          const valores = [...document.querySelectorAll('.contacto-bar-value')]
            .map(n => n.getBoundingClientRect())
            .sort((a, b) => a.left - b.left);
          const gaps = [];
          for (let i = 1; i < valores.length; i++) {
            gaps.push(Math.round(valores[i].left - valores[i - 1].right));
          }
          const correo = document.querySelector('.contacto-bar--correo .contacto-bar-value');
          const r = document.createRange(); r.selectNodeContents(correo);
          const renglones = [...r.getClientRects()].filter(x => x.width > 1).length;
          return {scrollW, viewportW, gaps, renglones};
        }""")
        overflow = datos["scrollW"] - datos["viewportW"]
        print(f"  {w:4}px  overflow={overflow:+d}  gaps={datos['gaps']}  renglones={datos['renglones']}")
        # Desbordamiento horizontal: la pagina entera se desplaza en lateral
        # (medido: +58px a 901px antes del fix).
        if overflow > 0:
            fallos.append(f"sweep {w}px: desborda {overflow}px horizontal")
        # Gap minimo entre columnas contiguas: 0px medido a 901-1024 antes
        # del fix -- las cuatro cadenas se leian como una sola.
        if datos["gaps"] and min(datos["gaps"]) < GAP_MIN_PX:
            fallos.append(
                f"sweep {w}px: gap de {min(datos['gaps'])}px entre valores "
                f"(minimo {GAP_MIN_PX})"
            )
        # El correo tiene que seguir en un solo renglon en todo el barrido
        # (reutiliza el mismo chequeo que ya existe para 1440/390).
        if datos["renglones"] != 1:
            fallos.append(f"sweep {w}px: el correo cae en {datos['renglones']} renglones")
        pg.close()
    b.close()
    return fallos

# Contraste en el estado enfriado (informe final, hallazgo P1, 2026-08-13):
# el arnes solo media reposo, y el apagado en grupo por hover (opacity 0.5
# en el padre `[class*="contacto-bar--"]`) es un estado interactivo que solo
# existe mientras otra via tiene el foco/hover. `.contacto-bar-value` pasaba
# de sobra en reposo pero el rotulo (`--haze`, 6,43:1 en reposo) se componia
# a 2,42-2,45:1 enfriado -- un defecto que solo aparece en ese estado, y que
# por tanto un arnes que solo mide reposo nunca ve, igual que el barrido de
# ancho de F-01 arriba.
HOVER_ANCHOS = [1024, 1440]

def hover_cooling_contrast(pw, base):
    fallos = []
    b = pw.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    from PIL import Image
    import io
    for w in HOVER_ANCHOS:
        pg = b.new_page(viewport={"width": w, "height": 900})
        pg.goto(f"{base}/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(9000)
        pg.evaluate("document.querySelector('[data-scene=\"contacto\"]').scrollIntoView()")
        pg.wait_for_timeout(2500)
        box = pg.eval_on_selector(".contacto-bar--correo", "n => { const r = n.getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height}; }")
        pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        pg.wait_for_timeout(1200)  # los 0,9s --slow del apagado en grupo, con margen
        datos = pg.evaluate("""() => {
          const enfriadas = ['linkedin', 'telefono', 'github'];
          return enfriadas.flatMap(id => {
            const bar = document.querySelector('.contacto-bar--' + id);
            return ['.contacto-bar-label', '.contacto-bar-value'].map(s => {
              const n = bar.querySelector(s);
              const r = document.createRange(); r.selectNodeContents(n);
              const c = r.getBoundingClientRect();
              return {sel: id + ' ' + s, caja: {x: c.x, y: c.y, w: c.width, h: c.height}};
            });
          });
        }""")
        for d in datos:
            c = d["caja"]
            if c["w"] < 1 or c["h"] < 1:
                fallos.append(f"hover {w}px: {d['sel']}: caja vacia"); continue
            png = pg.screenshot(clip={"x": c["x"], "y": c["y"],
                                      "width": c["w"], "height": c["h"]})
            pix = list(Image.open(io.BytesIO(png)).convert("RGB").getdata())
            r = ratio(max(pix, key=luminancia), min(pix, key=luminancia))
            print(f"  {'OK ' if r >= MIN_AA else 'FALLA'} hover {w}px {d['sel']:24} {r:.2f}:1")
            if r < MIN_AA:
                fallos.append(f"hover {w}px: {d['sel']} enfriado a {r:.2f}:1 (minimo {MIN_AA})")
        pg.close()
    b.close()
    return fallos

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://localhost:4173")
    args = p.parse_args()
    fallos = []
    with sync_playwright() as pw:
        fallos += sweep_anchos(pw, args.base)
        fallos += hover_cooling_contrast(pw, args.base)
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
        # Geometria real, no propiedades declaradas: `getComputedStyle(...).
        # paddingLeft` + `390 - 2*calle` daba un util de 330 cuando la caja
        # real de la banda media 335 (27..363, sin sangrar) -- el correo
        # cabia por 27px, no por los 82 que reportaba esa cuenta. Todo sale
        # de `getBoundingClientRect()` de la banda y de su rango de texto.
        m = pg390.evaluate("""() => {
          const banda = document.querySelector('.contacto-bar--correo');
          const bandaBox = banda.getBoundingClientRect();
          const csBanda = getComputedStyle(banda);
          const padL = parseFloat(csBanda.paddingLeft);
          const padR = parseFloat(csBanda.paddingRight);
          const v = banda.querySelector('.contacto-bar-value');
          const r = document.createRange(); r.selectNodeContents(v);
          const ren = [...r.getClientRects()].filter(x => x.width > 1);
          return {calle: padL, util: Math.round(bandaBox.width - padL - padR),
                  bandaBox: {left: Math.round(bandaBox.left), right: Math.round(bandaBox.right)},
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

        # Sangrado: las bandas tienen que llegar de borde a borde del
        # viewport. Si se quedan flotando dentro de la calle de la escena,
        # el fondo asoma por los dos costados -- justo lo que paso aqui.
        sangrado = pg390.evaluate("""() => {
          const b = document.querySelector('.contacto-bars').getBoundingClientRect();
          return {left: Math.round(b.left), right: Math.round(b.right)};
        }""")
        print("  sangrado:", sangrado)
        if sangrado["left"] != 0 or abs(sangrado["right"] - 390) > 1:
            fallos.append(f"movil: las bandas no sangran ({sangrado})")

        # Alineacion: el titular y el rotulo del correo tienen que arrancar
        # en la misma vertical. Es el invariante que rompio la calle doble
        # (titular en 57px, rotulo en 57px por la misma via, pero cuando solo
        # uno de los dos hereda el margen negativo se separan).
        alineacion = pg390.evaluate("""() => {
          const titulo = document.querySelector('.contacto-title').getBoundingClientRect();
          const rotulo = document.querySelector(
            '.contacto-bar--correo .contacto-bar-label').getBoundingClientRect();
          return {titulo: Math.round(titulo.left), rotulo: Math.round(rotulo.left)};
        }""")
        print("  alineacion:", alineacion)
        if abs(alineacion["titulo"] - alineacion["rotulo"]) > 1:
            fallos.append(f"movil: titular y rotulo desalineados ({alineacion})")
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
