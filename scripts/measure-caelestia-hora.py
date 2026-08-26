#!/usr/bin/env python3
"""
Arnes del motor de color de Caelestia.

Nacio de un fallo real detectado a mano el 2026-08-19 a las 19:43: con una
banda de transicion de 45 min entre esquemas, superficie y texto intercambian
el orden de claridad y se cruzan. En el cruce el contraste es 1:1. Ninguna
curva lo evita — hay que cortar en seco.

Se lanza contra el BUILD DE PRODUCCION servido, nunca contra `npm run dev`:
el HMR de Vite corrompe las medidas.

    npm run build && npx vite preview --port 4173 &
    python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

TOKENS = [
    "--cae-surface", "--cae-surface-container", "--cae-surface-container-high",
    "--cae-on-surface", "--cae-on-surface-variant", "--cae-outline",
    "--cae-primary", "--cae-on-primary",
    "--cae-primary-container", "--cae-on-primary-container",
    "--cae-anchor", "--cae-on-anchor",
]

# Pares que tienen que cumplir AA en TODAS las horas.
PARES = [
    ("--cae-on-surface", "--cae-surface"),
    ("--cae-on-surface-variant", "--cae-surface-container"),
    ("--cae-on-primary", "--cae-primary"),
    ("--cae-on-primary-container", "--cae-primary-container"),
    ("--cae-on-anchor", "--cae-anchor"),
]

# Se inyecta antes de que cargue nada: el motor lee la hora una sola vez, al
# arrancar, asi que parchear Date despues no serviria de nada.
RELOJ = """(minutos) => {
  const Real = Date;
  const base = new Real(2026, 0, 1, Math.floor(minutos / 60), minutos % 60, 0);
  class Fija extends Real {
    constructor(...args) { super(...(args.length ? args : [base.getTime()])); }
    static now() { return base.getTime(); }
  }
  window.Date = Fija;
}"""

# Lee el pixel (1,1) del canvas del fondo justo dentro de gl.drawArrays (antes
# de que el navegador intercambie el buffer): preserveDrawingBuffer es false
# en shaderBackground.ts (a proposito, no se toca), asi que leer despues del
# hecho devuelve basura. El hook expone window.__caePixel para recogerlo.
HOOK_PIXEL = """() => {
  window.__caePixel = null;
  const proto = WebGLRenderingContext.prototype;
  const orig = proto.drawArrays;
  proto.drawArrays = function(...args) {
    const r = orig.apply(this, args);
    try {
      const px = new Uint8Array(4);
      this.readPixels(1, 1, 1, 1, this.RGBA, this.UNSIGNED_BYTE, px);
      window.__caePixel = Array.from(px);
    } catch (e) { /* swiftshader a veces tira en el primer frame, se reintenta */ }
    return r;
  };
}"""


def hue_at(minutos):
    """Espejo de hueAt() en caelestia.color.ts. Si diverge, este arnes miente."""
    return ((minutos / 1440 * 360 + 60) % 360 + 360) % 360


def _srgb_a_lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _matiz_oklab_deg(rgb255):
    """RGB 0-255 (sRGB, gamma) -> matiz OkLab en grados. Round-trip completo
    (EOTF sRGB -> lineal -> LMS -> OkLab), matrices canonicas de Bjorn Ottosson."""
    import math
    r, g, b = (_srgb_a_lineal(v / 255.0) for v in rgb255[:3])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (max(x, 0.0) ** (1 / 3) for x in (l, m, s))
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b_ = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return math.degrees(math.atan2(b_, a)) % 360


def _dist_angular(h1, h2):
    d = abs(h1 - h2) % 360
    return min(d, 360 - d)


def rel_luminance(rgb):
    def canal(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = rel_luminance(a), rel_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def leer(page, minutos):
    """Devuelve {token: (r,g,b)} resolviendo oklch() a sRGB en el navegador.

    `getComputedStyle(...).color` en esta version de Chromium devuelve el
    color en su propia notacion (`oklch(...)`) en vez de `rgb(...)`, asi que
    parsear con una regex de numeros leia los propios L/C/H como si fueran
    bytes RGB — daba 1.00:1 en todos los pares, siempre, incluso con el motor
    ya montado. Un canvas 2D fuerza la conversion real a bytes sRGB via
    `getImageData`, que es donde el navegador si tiene que resolver el
    espacio de color contra el display.
    """
    return page.evaluate(
        """(tokens) => {
            const cs = getComputedStyle(document.documentElement);
            const canvas = document.createElement('canvas');
            canvas.width = 1;
            canvas.height = 1;
            const ctx = canvas.getContext('2d', { willReadFrequently: true });
            const out = {};
            for (const t of tokens) {
              const raw = cs.getPropertyValue(t).trim();
              if (!raw) { out[t] = null; continue; }
              // Indicador dedicado, no una comparacion de valor resultante:
              // `CSS.supports('color', raw)` es el parser real del
              // navegador diciendo si la cadena es un color valido, asi que
              // no puede colisionar con ningun color legitimo (a diferencia
              // de comparar `fillStyle` contra un centinela como '#010203',
              // que un rol futuro podria alcanzar de verdad).
              if (!CSS.supports('color', raw)) { out[t] = null; continue; }
              ctx.fillStyle = raw;
              ctx.fillRect(0, 0, 1, 1);
              const d = ctx.getImageData(0, 0, 1, 1).data;
              out[t] = [d[0], d[1], d[2]];
            }
            out.__hue = parseFloat(cs.getPropertyValue('--cae-hue'));
            return out;
        }""",
        TOKENS,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    fallos = []
    with sync_playwright() as p:
        nav = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])

        # ---- 1. barrido de las 24 horas, cada 20 minutos
        for minutos in range(0, 1440, 20):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            ctx.add_init_script("(%s)(%d)" % (RELOJ, minutos))
            page = ctx.new_page()
            page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1200)
            vals = leer(page, minutos)

            for t in TOKENS:
                if vals.get(t) is None:
                    fallos.append("%02d:%02d token ausente %s" % (minutos // 60, minutos % 60, t))

            for fg, bg in PARES:
                if vals.get(fg) and vals.get(bg):
                    r = ratio(vals[fg], vals[bg])
                    if r < 4.5:
                        fallos.append(
                            "%02d:%02d %s sobre %s = %.2f:1 (< 4.5)"
                            % (minutos // 60, minutos % 60, fg, bg, r)
                        )

            # ---- rampa tonal: las tres superficies tienen que ser DISTINTAS.
            # El tema viejo usaba `#ffffff 62%` para todas y por eso no habia
            # jerarquia de elevacion: todo flotaba a la misma altura.
            rampa = [
                vals.get("--cae-surface"),
                vals.get("--cae-surface-container"),
                vals.get("--cae-surface-container-high"),
            ]
            if all(rampa):
                lums = [rel_luminance(c) for c in rampa]
                pasos = [abs(lums[i + 1] - lums[i]) for i in range(2)]
                if min(pasos) < 0.008:
                    fallos.append(
                        "%02d:%02d rampa plana: pasos de luminancia %s"
                        % (minutos // 60, minutos % 60, [round(p, 4) for p in pasos])
                    )

            # ---- 2. el matiz a las 11:00 es 225 +/- 1
            if minutos == 660:
                hue = vals.get("__hue")
                if hue is None or abs(hue - 225.0) > 1.0:
                    fallos.append("matiz a las 11:00 = %s (esperado 225 +/- 1)" % hue)

            ctx.close()

        # ---- 3. el umbral no tiene estados intermedios
        for antes, despues in ((1199, 1200), (419, 420)):
            claves = []
            for minutos in (antes, despues):
                ctx = nav.new_context(viewport={"width": 1440, "height": 900})
                ctx.add_init_script("(%s)(%d)" % (RELOJ, minutos))
                page = ctx.new_page()
                page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1200)
                v = leer(page, minutos)
                claves.append(ratio(v["--cae-on-surface"], v["--cae-surface"]))
                ctx.close()
            for r in claves:
                if r < 4.5:
                    fallos.append("umbral %d/%d: contraste %.2f:1 (< 4.5)" % (antes, despues, r))

        # ---- 4. las tres familias cargan y el display lleva sus ejes
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2500)
        tipos = page.evaluate(
            """() => {
                const cs = getComputedStyle(document.documentElement);
                const h1 = document.querySelector('h1');
                return {
                  display: cs.getPropertyValue('--font-display').trim(),
                  cargadas: [...document.fonts].map(f => f.family),
                  ejes: h1 ? getComputedStyle(h1).fontVariationSettings : null,
                };
            }"""
        )
        for familia in ("Fraunces", "Hanken Grotesk", "Martian Mono"):
            if familia not in tipos["cargadas"]:
                fallos.append("tipografia no cargada: %s" % familia)
        if tipos["ejes"] is None or "WONK" not in str(tipos["ejes"]):
            fallos.append("el display no lleva los ejes: %s" % tipos["ejes"])
        ctx.close()

        # ---- 5. la barra: cinco pastillas, reloj y bandeja
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script("(%s)(%d)" % (RELOJ, 660))
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        barra = page.evaluate(
            """() => {
                const b = document.querySelector('[data-cae-bar]');
                if (!b) return null;
                return {
                  pastillas: b.querySelectorAll('[data-cae-ws]').length,
                  reloj: (b.querySelector('[data-cae-clock]') || {}).textContent,
                  activa: b.querySelectorAll('[data-cae-ws][aria-current="true"]').length,
                };
            }"""
        )
        if barra is None:
            fallos.append("no existe [data-cae-bar]")
        else:
            if barra["pastillas"] != 5:
                fallos.append("la barra tiene %d pastillas, esperadas 5" % barra["pastillas"])
            if barra["reloj"] != "11:00":
                fallos.append("el reloj marca %r, esperado '11:00'" % barra["reloj"])
            if barra["activa"] != 1:
                fallos.append("pastillas activas: %d, esperada 1" % barra["activa"])
        ctx.close()

        # ---- 6. los otros dos temas NO montan el shell
        for otro in ("vice", "hyprland"):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            page.goto(args.base + "/?theme=" + otro, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            if page.query_selector("[data-cae-bar]"):
                fallos.append("el shell de Caelestia se ha montado en %s" % otro)
            ctx.close()

        # ---- 7. el dock: cuatro accesos con etiqueta accesible y rel seguro
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        dock = page.evaluate(
            """() => {
                const d = document.querySelector('[data-cae-dock]');
                if (!d) return null;
                const enlaces = [...d.querySelectorAll('a')];
                return {
                  n: enlaces.length,
                  sinLabel: enlaces.filter(a => !a.getAttribute('aria-label')).length,
                  externosSinRel: enlaces.filter(
                    a => a.target === '_blank' && !(a.rel || '').includes('noopener')
                  ).length,
                  sinIcono: enlaces.filter(a => !a.querySelector('svg')).length,
                };
            }"""
        )
        if dock is None:
            fallos.append("no existe [data-cae-dock]")
        else:
            if dock["n"] < 4:
                fallos.append("el dock tiene %d accesos, esperados 4 o mas" % dock["n"])
            if dock["sinLabel"]:
                fallos.append("%d accesos del dock sin aria-label" % dock["sinLabel"])
            if dock["externosSinRel"]:
                fallos.append("%d enlaces externos sin rel noopener" % dock["externosSinRel"])
            if dock["sinIcono"]:
                fallos.append("%d accesos del dock sin icono" % dock["sinIcono"])
        ctx.close()

        # ---- 8. la notificacion de disponibilidad aparece y no roba el foco
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        aviso = page.evaluate(
            """() => {
                const t = document.querySelector('[data-cae-toast]');
                if (!t) return null;
                return {
                  visible: t.classList.contains('is-open'),
                  live: t.getAttribute('aria-live'),
                  robaFoco: document.activeElement === t || t.contains(document.activeElement),
                };
            }"""
        )
        if aviso is None:
            fallos.append("no existe [data-cae-toast]")
        else:
            if not aviso["visible"]:
                fallos.append("la notificacion de disponibilidad no llego a mostrarse")
            if aviso["live"] != "polite":
                fallos.append("la notificacion tiene aria-live=%r, esperado 'polite'" % aviso["live"])
            if aviso["robaFoco"]:
                fallos.append("la notificacion roba el foco")
        ctx.close()

        # ---- 9. cambio de workspace: la pagina no desplaza, el carril si
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        alturaDoc = page.evaluate("document.documentElement.scrollHeight - window.innerHeight")
        if alturaDoc > 4:
            fallos.append("la pagina sigue desplazando en Caelestia: sobran %dpx" % alturaDoc)

        page.eval_on_selector_all("[data-cae-ws]", "bs => bs[2].click()")
        page.wait_for_timeout(900)
        estado = page.evaluate(
            """() => {
                const t = document.querySelector('[data-cae-track]');
                const activa = document.querySelector('[data-cae-ws][aria-current="true"]');
                return {
                  transform: t ? getComputedStyle(t).transform : null,
                  activa: activa ? activa.dataset.caeWs : null,
                };
            }"""
        )
        if estado["activa"] != "obra":
            fallos.append("tras pulsar la tercera pastilla, la activa es %r" % estado["activa"])
        if not estado["transform"] or estado["transform"] == "none":
            fallos.append("el carril no se ha movido: transform %r" % estado["transform"])

        # Los anclas siguen resolviendo en los tres temas (sceneNav depende de ellos).
        ctx.close()
        for tema in ("vice", "hyprland", "caelestia"):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            page.goto(args.base + "/?theme=" + tema, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            faltan = page.evaluate(
                """() => ['hero','quien-es','obra','creditos','contacto']
                     .filter(id => !document.getElementById(id))"""
            )
            if faltan:
                fallos.append("%s: anclas ausentes %s" % (tema, faltan))
            ctx.close()

        # ---- 10. el fondo sigue el matiz de la hora, no trae color propio
        #
        # El proxy de bytes de PNG (comentado en el codigo, no borrado) NO es
        # gate: el shader viejo de 4 pasteles fijos tambien produce PNGs de
        # tamanos distintos por el ruido/animacion de los blobs -- se
        # comprobo con git worktree sobre el shader anterior y da 4 tamanos
        # distintos igual, o sea que "OK" incluso en el caso que se supone
        # que tiene que cazar. Se deja como asercion COMPLEMENTARIA de "no
        # esta congelado", nunca como la unica prueba de esta tarea.
        #
        # El gate real: matiz medido por pixel (readPixels dentro del propio
        # drawArrays, ver HOOK_PIXEL) contra hueAt(minutos) de
        # caelestia.color.ts, con tolerancia -- es un fondo desenfocado con
        # ruido y una conversion OkLCH->sRGB aproximada en el shader, un
        # umbral fino mediria ruido, no el bug.
        TOLERANCIA_GRADOS = 30
        muestras = {}
        for minutos in (300, 660, 1020, 1380):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            ctx.add_init_script("(%s)(%d)" % (RELOJ, minutos))
            ctx.add_init_script("(%s)()" % HOOK_PIXEL)
            page = ctx.new_page()
            page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(6000)
            png = page.screenshot(clip={"x": 0, "y": 0, "width": 200, "height": 200})
            muestras[minutos] = len(png)   # complementario: solo "no congelado"

            pixel = page.evaluate("() => window.__caePixel")
            ctx.close()
            if not pixel:
                fallos.append("%02d:%02d: no se pudo leer el pixel del canvas" % (minutos // 60, minutos % 60))
                continue

            esperado = hue_at(minutos)
            medido = _matiz_oklab_deg(pixel)
            d = _dist_angular(esperado, medido)
            if d > TOLERANCIA_GRADOS:
                fallos.append(
                    "%02d:%02d: matiz del fondo %.1f, esperado %.1f +/- %d (pixel %s)"
                    % (minutos // 60, minutos % 60, medido, esperado, TOLERANCIA_GRADOS, pixel)
                )

        if len(set(muestras.values())) < 3:
            fallos.append("el fondo apenas cambia con la hora (proxy de bytes): %s" % muestras)

        # ---- 11. movil: nada se sale del viewport
        ctx = nav.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        desbordes = page.evaluate(
            """() => ['[data-cae-bar]','[data-cae-dock]','[data-cae-toast]']
                 .map(sel => {
                   const n = document.querySelector(sel);
                   if (!n) return sel + ' ausente';
                   const r = n.getBoundingClientRect();
                   return (r.right > 391 || r.left < -1) ? sel + ' se sale: ' + JSON.stringify([r.left, r.right]) : null;
                 }).filter(Boolean)"""
        )
        for d in desbordes:
            fallos.append("movil 390: %s" % d)
        if page.evaluate("document.documentElement.scrollWidth > 391"):
            fallos.append("movil 390: la pagina desplaza en horizontal")
        ctx.close()

        # ---- 12. movimiento reducido: el cambio de workspace es instantaneo
        #
        # El umbral de 120 ms lleva margen a proposito contra los 520 ms de la
        # animacion: uno mas ajustado mediria carga de maquina, no la
        # animacion (ver CLAUDE.md). Con `reduce` el carril no se anima, LLEGA.
        ctx = nav.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        page.eval_on_selector_all("[data-cae-ws]", "bs => bs[4].click()")
        page.wait_for_timeout(120)   # muy por debajo de los 520 ms de la animacion
        llegado = page.evaluate(
            """() => {
                const t = document.querySelector('[data-cae-track]');
                if (!t) return 0;
                const m = getComputedStyle(t).transform.match(/-?[\\d.]+/g);
                return m ? Math.abs(Number(m[4])) : 0;
            }"""
        )
        ancho = page.evaluate("window.innerWidth")
        if llegado < ancho * 3.5:
            fallos.append(
                "con movimiento reducido el carril no llego de golpe: %.0f de %.0f"
                % (llegado, ancho * 4)
            )
        ctx.close()

        # ---- 13. el foco es visible y usa el ancla
        #
        # Antes solo leia `outlineStyle`, y eso da verde con un anillo de
        # anchura 0 (invisible) o de cualquier color: demostrado inyectando
        # `:focus-visible { outline-width: 0 }`, el anillo desaparece de la
        # pantalla y la version vieja de esta asercion seguia en verde. Ahora
        # comprueba las tres cosas que promete el titulo: que el contorno
        # existe, que tiene anchura real, y que su color es el del ancla
        # (`--cae-anchor`) -- resuelto por el propio navegador via canvas 2D
        # para no comparar cadenas oklch()/rgb() con distinta notacion.
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        contorno = page.evaluate(
            """() => {
                const e = document.activeElement;
                if (!e) return null;
                const cs = getComputedStyle(e);
                const anclaRaw = getComputedStyle(document.documentElement)
                  .getPropertyValue('--cae-anchor').trim();
                const canvas = document.createElement('canvas');
                canvas.width = 1; canvas.height = 1;
                const c2d = canvas.getContext('2d', { willReadFrequently: true });
                const bytesDe = (raw) => {
                  if (!raw || !CSS.supports('color', raw)) return null;
                  c2d.fillStyle = raw;
                  c2d.fillRect(0, 0, 1, 1);
                  return Array.from(c2d.getImageData(0, 0, 1, 1).data.slice(0, 3));
                };
                return {
                  style: cs.outlineStyle,
                  width: cs.outlineWidth,
                  colorBytes: bytesDe(cs.outlineColor),
                  anclaBytes: bytesDe(anclaRaw),
                };
            }"""
        )
        if contorno is None:
            fallos.append("no hay elemento con foco tras dos Tab")
        else:
            if contorno["style"] in (None, "none"):
                fallos.append("el elemento con foco no tiene contorno")
            if contorno["width"] in (None, "0px"):
                fallos.append("el contorno de foco tiene anchura 0 (invisible)")
            cb, ab = contorno["colorBytes"], contorno["anclaBytes"]
            if not cb or not ab:
                fallos.append("no se pudo resolver el color del contorno o del ancla")
            else:
                # Tolerancia en sRGB (no igualdad de cadena): el navegador
                # puede devolver outline-color y --cae-anchor en notaciones
                # distintas (oklch/rgb) para el mismo color percibido.
                dist = sum((a - b) ** 2 for a, b in zip(cb, ab)) ** 0.5
                if dist > 12:
                    fallos.append(
                        "el contorno de foco no usa el color del ancla: %s vs %s (dist %.1f)"
                        % (cb, ab, dist)
                    )
        ctx.close()

        nav.close()

    if fallos:
        print("FALLOS (%d):" % len(fallos))
        for f in fallos:
            print("  -", f)
        sys.exit(1)
    print("OK — motor de color de Caelestia en verde")
    sys.exit(0)


if __name__ == "__main__":
    main()
