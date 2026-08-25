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
            const centinela = '#010203';
            for (const t of tokens) {
              const raw = cs.getPropertyValue(t).trim();
              if (!raw) { out[t] = null; continue; }
              ctx.fillStyle = centinela;
              ctx.fillStyle = raw;
              if (ctx.fillStyle === centinela) {
                // fillStyle no acepto el valor y se quedo con el centinela:
                // el token esta vacio o el color no parsea.
                out[t] = null;
                continue;
              }
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
