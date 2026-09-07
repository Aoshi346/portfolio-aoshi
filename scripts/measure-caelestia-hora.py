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
import time

from playwright.sync_api import sync_playwright

TOKENS = [
    "--cae-surface", "--cae-surface-container", "--cae-surface-container-high",
    "--cae-on-surface", "--cae-on-surface-variant", "--cae-outline",
    "--cae-primary", "--cae-on-primary",
    "--cae-primary-container", "--cae-on-primary-container",
    "--cae-anchor", "--cae-on-anchor",
]

# Pares que tienen que cumplir AA en TODAS las horas.
#
# El criterio es LO QUE DE VERDAD SE PINTA, no la pareja que sugiere el nombre
# del rol. Esa distincion es justo lo que fallo: la lista vigilaba
# `on-surface-variant` sobre `surface-container` (= `--cae-elev-1`), pero la
# barra, el dock y el aviso se pintan sobre `--cae-elev-2`
# (= `surface-container-high`), y `--cae-primary` no aparecia en ningun par.
# Trece aserciones en verde con el reloj de la barra — la pieza que el spec
# pone en el centro del tema — a 4.16:1 en el peor matiz de la manana.
#
# Reparto real del shell (ver el tramo Caelestia de `themes.css`):
#   .cae-bar / .cae-dock / .cae-toast  fondo  --cae-elev-2
#   .cae-mark, .cae-clock              texto  --cae-primary            sobre elev-2
#   .cae-ws, .cae-avail, .cae-toast-s  texto  --cae-on-surface-variant sobre elev-2
#   .cae-toast-t                       texto  --cae-on-surface         sobre elev-2
#   .cae-ws[aria-current]              texto  --cae-on-primary         sobre primary
#   .cae-ws:hover, .cae-dock-item      texto  --cae-on-surface-variant sobre elev-1
#   .cae-dock-item:hover               texto  --cae-on-anchor          sobre anchor
PARES = [
    ("--cae-on-surface", "--cae-surface"),
    ("--cae-on-surface-variant", "--cae-surface-container"),
    ("--cae-on-primary", "--cae-primary"),
    ("--cae-on-primary-container", "--cae-primary-container"),
    ("--cae-on-anchor", "--cae-anchor"),
    # Anadidos: el fondo real de la barra, el dock y el aviso.
    ("--cae-primary", "--cae-surface-container-high"),
    ("--cae-on-surface-variant", "--cae-surface-container-high"),
    ("--cae-on-surface", "--cae-surface-container-high"),
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


def is_dark_at(minutos):
    """Espejo de isDarkAt() en caelestia.color.ts. Si diverge, este arnes miente."""
    return minutos < 7 * 60 or minutos >= 20 * 60


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
                  sinAvail: b.querySelector('.cae-avail') === null,
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
            if not barra["sinAvail"]:
                fallos.append(
                    "la barra no lleva chapa de disponible (vive en la tarjeta del hero)"
                )
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

        # ---- 8. la notificacion ya NO salta al entrar; solo al cambio de esquema
        #
        # Decision de Aoshi (repaso de interfaces 2026-09-05): el aviso de
        # entrada a los 900ms se pisaba con la entrada de Titulo y con el
        # widget "Ahora mismo", que ya dice lo mismo. Se quita el disparo de
        # entrada y se queda solo el de `caelestia:esquema`.
        #
        # El corte se ancla al ESTADO (que la entrada de Titulo haya
        # aterrizado: `#hero .cae-term-typed` con "whoami" y
        # `#hero .cae-firma` con opacidad computada >= 0.99), nunca a un
        # cronometro fijo -- en esta sandbox rAF/setTimeout van a 200-400ms,
        # asi que un `wait_for_timeout` corto podria leer el toast ANTES de
        # que el disparo de 900ms (si siguiera vivo) llegara a abrirlo, y el
        # gate mentiria en verde. Se muestrea desde el `commit` cada ~50ms
        # hasta el aterrizaje y se exige que el toast NO haya estado
        # `is-open` en NINGUNA muestra: es la asercion que caza el disparo de
        # 900ms aunque se hubiera cerrado ya (4200ms de vida) antes de que la
        # entrada aterrizara.
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="commit", timeout=30000)

        # El shell (barra/dock/toast) monta via `import()` diferido, igual que
        # el resto de modulos de tema: no existe todavia en el instante del
        # `commit`, asi que su presencia se comprueba DESPUES del muestreo,
        # no antes -- comprobarla en caliente aqui confundiria "aun no ha
        # montado" con "no existe".
        LEE_ESTADO = """() => {
            const t = document.querySelector('[data-cae-toast]');
            const typed = document.querySelector('#hero .cae-term-typed');
            const firma = document.querySelector('#hero .cae-firma');
            const csFirma = firma ? getComputedStyle(firma) : null;
            return {
              toastExiste: !!t,
              toastOpen: t ? t.classList.contains('is-open') : false,
              typed: typed ? typed.textContent : null,
              firmaOp: csFirma ? parseFloat(csFirma.opacity) : null,
            };
        }"""

        t0 = time.monotonic()
        vistoAbiertoAntes = False
        vistoToast = False
        aterrizo = None
        while time.monotonic() - t0 < 30:
            try:
                m = page.evaluate(LEE_ESTADO)
            except Exception:
                m = None
            if m is not None:
                if m["toastExiste"]:
                    vistoToast = True
                if m["toastOpen"]:
                    vistoAbiertoAntes = True
                if (
                    m["typed"] == "whoami"
                    and m["firmaOp"] is not None
                    and m["firmaOp"] >= 0.99
                ):
                    aterrizo = m
                    break
            page.wait_for_timeout(50)

        if aterrizo is None:
            fallos.append("la entrada no aterrizo, no se puede juzgar la notificacion")
            ctx.close()
        elif not (vistoToast or aterrizo["toastExiste"]):
            fallos.append("no existe [data-cae-toast]")
            ctx.close()
        else:
            if vistoAbiertoAntes or aterrizo["toastOpen"]:
                fallos.append(
                    "la notificacion se abrio al cargar (debe quedar muda hasta el cambio de esquema)"
                )

            # El disparo por cambio de esquema sigue vivo.
            page.evaluate(
                "document.documentElement.dispatchEvent("
                "new CustomEvent('caelestia:esquema', {detail: {oscuro: true}}))"
            )
            page.wait_for_timeout(200)
            aviso = page.evaluate(
                """() => {
                    const t = document.querySelector('[data-cae-toast]');
                    return {
                      visible: t.classList.contains('is-open'),
                      live: t.getAttribute('aria-live'),
                      robaFoco: document.activeElement === t || t.contains(document.activeElement),
                    };
                }"""
            )
            if not aviso["visible"]:
                fallos.append("el cambio de esquema no abre la notificacion")
            if aviso["live"] != "polite":
                fallos.append(
                    "la notificacion tiene aria-live=%r, esperado 'polite'" % aviso["live"]
                )
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

        # ---- 10. el fondo sigue la hora: MATIZ y ESQUEMA
        #
        # Dos gates, no uno. El del matiz ya estaba; el de la luminancia es
        # nuevo y cubre la otra mitad del bug critico que tuvo esta tarea: el
        # matiz es IDENTICO de dia y de noche (`hueAt` no mira el esquema),
        # asi que si `uDark` se quedara clavado, el fondo dejaria de
        # oscurecerse por la noche y las trece aserciones seguirian en verde.
        #
        # Los dos comparan pixel (readPixels dentro del propio drawArrays,
        # ver HOOK_PIXEL) contra `caelestia.color.ts`: el matiz contra
        # `hueAt(minutos)`, la luminancia contra `isDarkAt(minutos)`. Las dos
        # tolerancias son ANCHAS a proposito -- es un fondo desenfocado, con
        # ruido y blobs animados, y una conversion OkLCH->sRGB aproximada en
        # el shader: un umbral fino mediria ruido, no el bug. El shader pide
        # L 0.975 de dia y 0.175 de noche (`lBase` en caelestiaBlobs.ts), que
        # en luminancia relativa sRGB son extremos opuestos de la escala.
        TOLERANCIA_GRADOS = 30
        LUM_MAX_NOCHE = 0.25
        LUM_MIN_DIA = 0.45
        muestras = {}
        for minutos in (300, 660, 1020, 1380):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            ctx.add_init_script("(%s)(%d)" % (RELOJ, minutos))
            ctx.add_init_script("(%s)()" % HOOK_PIXEL)
            page = ctx.new_page()
            page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(6000)
            png = page.screenshot(clip={"x": 0, "y": 0, "width": 200, "height": 200})
            muestras[minutos] = len(png)   # informativo, NO gate: ver mas abajo

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

            lum = rel_luminance(pixel[:3])
            oscuro = is_dark_at(minutos)
            print(
                "    fondo %02d:%02d  esquema=%s  luminancia=%.3f  matiz=%.1f"
                % (minutos // 60, minutos % 60, "noche" if oscuro else "dia", lum, medido)
            )
            if oscuro and lum > LUM_MAX_NOCHE:
                fallos.append(
                    "%02d:%02d: el fondo no se oscurece de noche: luminancia %.3f (> %.2f, pixel %s)"
                    % (minutos // 60, minutos % 60, lum, LUM_MAX_NOCHE, pixel)
                )
            if not oscuro and lum < LUM_MIN_DIA:
                fallos.append(
                    "%02d:%02d: el fondo no se aclara de dia: luminancia %.3f (< %.2f, pixel %s)"
                    % (minutos // 60, minutos % 60, lum, LUM_MIN_DIA, pixel)
                )

        # El proxy de bytes de PNG NO es gate y ahora el codigo lo respeta.
        # Antes el comentario decia "complementaria, nunca la unica prueba" y
        # justo debajo hacia `fallos.append(...)`, que saca el arnes con codigo
        # 1: era un gate, y ademas flaky por naturaleza (cuatro capturas de un
        # shader animado con ruido). Se degrada a informativo en vez de
        # quitarle el comentario porque lo que dice el comentario es cierto: se
        # comprobo con `git worktree` sobre el shader anterior -- el de cuatro
        # pasteles FIJOS, el caso que se supone que tiene que cazar -- y daba
        # cuatro tamanos distintos igual. No discrimina nada. Lo que de verdad
        # cubre esta tarea son los dos gates de arriba (matiz y luminancia).
        print("  [info] tamanos de PNG del fondo por hora: %s" % muestras)
        if len(set(muestras.values())) < 3:
            print("  [info] el proxy de bytes ve poca variacion; no es gate, ver arriba")

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

        # `.theme-signature` es compartida por los tres temas (bottom-5 right-5,
        # `themeSignature.ts`) y no llevaba CSS propio de Caelestia: a 390px
        # invadia el dock (medido antes del arreglo: dock [103,778,287,830] vs
        # firma [247.9,800,370,824], solape real en x e y). Se comprueba en las
        # cinco escenas, no solo en el hero: el dock no se mueve al cambiar de
        # workspace pero conviene no asumirlo.
        for indice in range(5):
            if indice > 0:
                page.eval_on_selector_all(
                    "[data-cae-ws]", "(bs, i) => bs[i].click()", indice
                )
                page.wait_for_timeout(600)
            solape = page.evaluate(
                """() => {
                    const dock = document.querySelector('[data-cae-dock]');
                    const sig = document.querySelector('.theme-signature');
                    if (!dock || !sig) return { ausente: true };
                    if (getComputedStyle(sig).display === 'none') return { oculta: true };
                    const dr = dock.getBoundingClientRect();
                    const sr = sig.getBoundingClientRect();
                    const overlap = !(dr.right < sr.left || dr.left > sr.right ||
                                       dr.bottom < sr.top || dr.top > sr.bottom);
                    return { overlap, dock: [dr.left, dr.top, dr.right, dr.bottom],
                             sig: [sr.left, sr.top, sr.right, sr.bottom] };
                }"""
            )
            if solape.get("ausente"):
                fallos.append("movil 390: dock o firma de tema ausentes (escena %d)" % indice)
            elif not solape.get("oculta") and solape.get("overlap"):
                fallos.append(
                    "movil 390: el dock y la firma de tema se solapan en la escena %d "
                    "(dock %s, firma %s)" % (indice, solape["dock"], solape["sig"])
                )
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

        # ---- 14. la barra baja y el dock sube (y con movimiento reducido no)
        #
        # Decision de Aoshi (repaso de interfaces 2026-09-05): la barra y el
        # dock aparecian de golpe. Ahora la barra ENTRA desde arriba
        # (`caeShellBaja`) y el dock desde abajo (`caeShellSube`), 0.4s,
        # `animation-fill-mode: both`.
        #
        # El shell monta via `import()` diferido (igual que el toast de la
        # seccion 8), asi que no existe en el instante del `commit` -- se
        # muestrea desde ahi, sin `wait_for_timeout` entre lecturas para no
        # perderse el fotograma intermedio con opacidad < 1 (la cadencia de un
        # `evaluate()` de ida y vuelta ya basta de por si). El corte de "ha
        # terminado" se ancla al ESTADO de `getAnimations()`
        # (`playState === 'finished'`), nunca a un cronometro: en esta sandbox
        # rAF/setTimeout van a 200-400ms, muy por encima de los 400ms
        # declarados, con lo que un plazo fijo mide la carga de la maquina, no
        # la animacion.
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="commit", timeout=30000)

        LEE_ENTRADA_SHELL = """() => {
            const leer = (el) => {
                if (!el) return null;
                const anims = el.getAnimations();
                const r = el.getBoundingClientRect();
                return {
                    opacity: parseFloat(getComputedStyle(el).opacity),
                    nombres: anims.map(a => a.animationName),
                    terminadas: anims.length > 0 && anims.every(a => a.playState === 'finished'),
                    top: r.top,
                    bottom: r.bottom,
                };
            };
            return {
                barra: leer(document.querySelector('[data-cae-bar]')),
                dock: leer(document.querySelector('[data-cae-dock]')),
            };
        }"""

        t0 = time.monotonic()
        primeraExistB = None
        primeraExistD = None
        nombresVistosB = set()
        nombresVistosD = set()
        vistoOpMenorB = False
        vistoOpMenorD = False
        final = None
        while time.monotonic() - t0 < 30:
            m = page.evaluate(LEE_ENTRADA_SHELL)
            ahora = time.monotonic()
            b, d = m["barra"], m["dock"]
            if b is not None:
                if primeraExistB is None:
                    primeraExistB = ahora
                nombresVistosB.update(b["nombres"])
                if b["opacity"] < 0.99:
                    vistoOpMenorB = True
            if d is not None:
                if primeraExistD is None:
                    primeraExistD = ahora
                nombresVistosD.update(d["nombres"])
                if d["opacity"] < 0.99:
                    vistoOpMenorD = True
            if b is not None and d is not None and b["terminadas"] and d["terminadas"]:
                final = m
                break
            # corte de seguridad: existen desde hace >2s y jamas hubo animacion
            if (
                b is not None and d is not None
                and not b["nombres"] and not d["nombres"]
                and primeraExistB is not None and ahora - primeraExistB > 2
                and primeraExistD is not None and ahora - primeraExistD > 2
            ):
                final = m
                break

        if final is None:
            fallos.append("la entrada de la barra/dock no aterrizo en 30s")
        else:
            if "caeShellBaja" not in nombresVistosB:
                fallos.append(
                    "la barra no llevo la animacion caeShellBaja (vistas: %s)" % nombresVistosB
                )
            if "caeShellSube" not in nombresVistosD:
                fallos.append(
                    "el dock no llevo la animacion caeShellSube (vistas: %s)" % nombresVistosD
                )
            if final["barra"]["opacity"] < 0.99:
                fallos.append("la barra no termino a opacity 1: %.2f" % final["barra"]["opacity"])
            if final["dock"]["opacity"] < 0.99:
                fallos.append("el dock no termino a opacity 1: %.2f" % final["dock"]["opacity"])
            if final["barra"]["top"] < 0 or final["barra"]["bottom"] > 900:
                fallos.append(
                    "la barra queda fuera del viewport al aterrizar: %s"
                    % [final["barra"]["top"], final["barra"]["bottom"]]
                )
            if final["dock"]["top"] < 0 or final["dock"]["bottom"] > 900:
                fallos.append(
                    "el dock queda fuera del viewport al aterrizar: %s"
                    % [final["dock"]["top"], final["dock"]["bottom"]]
                )
            if not vistoOpMenorB:
                fallos.append(
                    "nunca se vio la barra con opacity < 1 (aparece de golpe, no baja)"
                )
            if not vistoOpMenorD:
                fallos.append(
                    "nunca se vio el dock con opacity < 1 (aparece de golpe, no sube)"
                )
        ctx.close()

        # ---- 14b. con movimiento reducido no hay animacion de entrada
        ctx = nav.new_context(
            viewport={"width": 1440, "height": 900}, reduced_motion="reduce"
        )
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)

        t0 = time.monotonic()
        reducido = None
        while time.monotonic() - t0 < 15:
            r = page.evaluate(
                """() => {
                    const b = document.querySelector('[data-cae-bar]');
                    const d = document.querySelector('[data-cae-dock]');
                    if (!b || !d) return null;
                    return {
                        barraAnims: b.getAnimations().length,
                        dockAnims: d.getAnimations().length,
                        barraOp: parseFloat(getComputedStyle(b).opacity),
                        dockOp: parseFloat(getComputedStyle(d).opacity),
                    };
                }"""
            )
            if r is not None:
                reducido = r
                break
            page.wait_for_timeout(50)

        if reducido is None:
            fallos.append("movimiento reducido: la barra/dock nunca llegaron a existir")
        else:
            if reducido["barraAnims"] or reducido["dockAnims"]:
                fallos.append(
                    "movimiento reducido: quedan animaciones activas: %r" % reducido
                )
            if reducido["barraOp"] < 0.99 or reducido["dockOp"] < 0.99:
                fallos.append(
                    "movimiento reducido: opacity distinta de 1: %r" % reducido
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
