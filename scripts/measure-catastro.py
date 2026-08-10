"""Arnes del catastro de "Con que construyo" en Hyprland.

Ocho aserciones, y todas nacieron de un fallo real o de una trampa ya pagada:

  1. El catastro se VE en Hyprland. Sin esto el arnes sale verde con todo
     apagado: los nodos existen en el DOM de los tres temas desde que se
     anaden, y una caja con `display: none` no desborda ni descuadra. Las
     otras siete aserciones se autoanulan si esta falta.
  2. Los cuatro pies cierran a la misma cota en escritorio. Con altura
     minima en vez de fija, la parcela cuyo cruce ocupa mas lineas sube su
     pie y el rectangulo deja de cerrar. Distingue "faltan franjas" (menos
     de 4 nodos `[data-credit-strip]`) de "las franjas existentes no
     alinean" (4 nodos, cotas distintas): son dos defectos distintos y en
     un estado intermedio de la implementacion (1-3 franjas) confundirlos
     habria dado un mensaje que miente.
  3. Ningun nombre lleva acento en reposo, en los dos viewports. El acento
     es estado; seis nombres se leian como apuntados sin estarlo, y en
     movil lo provocaba ademas la siembra inicial de la franja.
  4. Ninguna franja arranca vacia. Llenar no es encender: la 3 y la 4 van
     juntas o se arregla una rompiendo la otra.
  5. Nada desborda su caja, ni las parcelas ni los nombres en su celda.
  6. El alto de la seccion en movil baja de 1100px. Hoy son 1134 y se corta.
  7. Las calles de movil son iguales y de 26px. A 390px el 5vw del tema deja
     20 y el rectangulo queda casi a sangre.
  8. La diana tactil de cada nombre llega a 44px en movil.
  9. El catastro no existe en Vice ni en Caelestia. El patron aditivo se ha
     roto cuatro veces por olvidar el `display: none` de base.
  10. El alto de `.credits-grid` en escritorio baja de 700px. Nacio de un
      falso verde real (ronda de arreglo 1 de la tarea 4): el `gap` heredado
      de la base compartida (`clamp(1.4rem, 4vw, 3.4rem)`, 54.4px a 1440)
      nunca se reseteaba en Hyprland, la rejilla media 1106px en vez de los
      562px del prototipo y los cuatro pies cerraban fuera de la pantalla —
      y la aserción 2 (pies a la misma cota) seguía en verde porque los
      cuatro seguían cerrando a la MISMA cota, solo que esa cota estaba a
      1146px. El tope de 700px deja margen sobre los 562px del prototipo
      para variaciones de fuente sin dejar pasar un descuadre del doble.
  11. Los tres niveles (`data-credit-tier`) tienen tamanos de fuente
      distintos entre si, medidos sobre el nodo que PINTA el texto. Nacio de
      un falso verde real (ronda de arreglo 2 de la tarea 4): la aserción 3
      ya media color sobre `[data-credit]`, pero `.credit-name` (el `<span>`
      de dentro) trae su propio `font-size: 1.2rem` y su propio `color` en
      la base de `style.css` — al estar en el hijo ganaba a todo lo que
      declarara el boton, y los tres niveles se veian iguales (19.2px fijo)
      aunque `[data-credit-tier]` si tuviera `font-size` distinto por nivel
      (28.43 / 21.33 / 16px). "El nivel se dice SOLO con tipografia" es el
      contenido de la escena: sin esta aserción esa frase era una intención,
      no algo verificable.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

VIEWPORTS = [("escritorio", 1440, 900), ("movil", 390, 844)]
ACENTOS = {"rgb(255, 90, 52)", "rgb(255, 160, 60)"}  # --l1, --l3
CALLE_MOVIL = 26
DIANA_MINIMA = 44
ALTO_MAXIMO_MOVIL = 1100
ALTO_MAXIMO_REJILLA_ESCRITORIO = 700


def ir_a_creditos(pg) -> bool:
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"credits\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        return False
    pg.evaluate(f"window.scrollTo(0, {top})")
    # Lenis sigue desplazando despues de un scrollTo: medir antes de que
    # asiente da falsos positivos.
    pg.wait_for_timeout(2500)
    return True


def catastro_visible(pg) -> bool:
    return pg.evaluate(
        "() => { const ns = document.querySelectorAll('[data-credit-parcela]');"
        " if (ns.length !== 4) return false;"
        " return Array.from(ns).every(n => {"
        "   const r = n.getBoundingClientRect();"
        "   return getComputedStyle(n).display !== 'none' && r.width > 0 && r.height > 0; }); }"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:4173")
    args = ap.parse_args()

    fallos: list[str] = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])

        for nombre, ancho, alto in VIEWPORTS:
            ctx = b.new_context(viewport={"width": ancho, "height": alto})
            pg = ctx.new_page()
            pg.goto(f"{args.url}/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(9000)
            if not ir_a_creditos(pg):
                fallos.append(f"[{nombre}] no existe [data-scene=credits]")
                ctx.close()
                continue

            # 1. visibilidad
            if not catastro_visible(pg):
                fallos.append(f"[{nombre}] el catastro no se ve: 4 parcelas con caja")

            # 3. acento en reposo — medido sobre el nodo que PINTA el texto
            # (`.credit-name` si existe, si no el propio boton). El color se
            # fija en `.credit`, pero un hijo con su propio `color` gana:
            # medir el boton daba un falso verde real (ronda 2 de la tarea 4,
            # el mismo defecto que "el tamano" mas abajo).
            encendidos = pg.evaluate(
                "(acentos) => Array.from(document.querySelectorAll('[data-credit]'))"
                " .map(n => n.querySelector('.credit-name') ?? n)"
                " .filter(n => acentos.includes(getComputedStyle(n).color))"
                " .map(n => n.textContent.trim())",
                list(ACENTOS),
            )
            if encendidos:
                fallos.append(f"[{nombre}] acento en reposo: {encendidos}")

            # 4. ninguna franja vacia
            vacias = pg.evaluate(
                "() => Array.from(document.querySelectorAll('[data-credit-strip]'))"
                " .filter(s => !s.textContent.trim()).length"
            )
            if vacias:
                fallos.append(f"[{nombre}] {vacias} franjas arrancan vacias")

            # 5. desbordes
            desborda = pg.evaluate(
                "() => Array.from(document.querySelectorAll("
                "  '[data-credit-parcela], [data-credit], [data-credit-strip]'))"
                " .filter(n => n.scrollHeight > n.clientHeight + 1"
                "           || n.scrollWidth > n.clientWidth + 1)"
                " .map(n => (n.dataset.creditParcela !== undefined ? 'parcela' : n.textContent.trim()))"
            )
            if desborda:
                fallos.append(f"[{nombre}] desborda: {desborda}")

            if nombre == "escritorio":
                # 2. los cuatro pies a la misma cota
                cotas = pg.evaluate(
                    "() => Array.from(document.querySelectorAll('[data-credit-strip]'))"
                    " .map(s => Math.round(s.getBoundingClientRect().top))"
                )
                if len(cotas) != 4:
                    fallos.append(f"[escritorio] faltan franjas: {len(cotas)} de 4 [data-credit-strip]")
                elif len(set(cotas)) != 1:
                    fallos.append(f"[escritorio] los pies no cierran a la misma cota: {cotas}")

                # 10. la rejilla no se desborda por un gap heredado
                alto_rejilla = pg.evaluate(
                    "() => Math.round(document.querySelector('.credits-grid')"
                    " .getBoundingClientRect().height)"
                )
                if alto_rejilla > ALTO_MAXIMO_REJILLA_ESCRITORIO:
                    fallos.append(
                        f"[escritorio] la rejilla mide {alto_rejilla}px"
                        f" (tope {ALTO_MAXIMO_REJILLA_ESCRITORIO})"
                    )

                # 11. el nivel se dice con tipografia — medido sobre el nodo
                # que pinta, no sobre el boton. Un `.credit-name` con su
                # propio `font-size` en la base ganaba al boton y los tres
                # niveles se veian iguales aunque el boton si variara.
                tamanos = pg.evaluate(
                    "() => { const porNivel = {};"
                    " document.querySelectorAll('[data-credit-tier]').forEach(n => {"
                    "   const t = n.dataset.creditTier;"
                    "   const pintor = n.querySelector('.credit-name') ?? n;"
                    "   const size = parseFloat(getComputedStyle(pintor).fontSize);"
                    "   (porNivel[t] ??= new Set()).add(size);"
                    " });"
                    " return Object.fromEntries("
                    "   Object.entries(porNivel).map(([k, v]) => [k, [...v]])); }"
                )
                planos = {t: sorted(vs) for t, vs in tamanos.items()}
                representativos = {t: vs[0] for t, vs in planos.items() if vs}
                if len(set(representativos.values())) != len(representativos):
                    fallos.append(
                        f"[escritorio] los niveles no tienen tamanos distintos: {planos}"
                    )
            else:
                # 6. alto de la seccion
                alto_seccion = pg.evaluate(
                    "() => Math.round(document.querySelector('[data-scene=\"credits\"]')"
                    " .getBoundingClientRect().height)"
                )
                if alto_seccion >= ALTO_MAXIMO_MOVIL:
                    fallos.append(f"[movil] la seccion mide {alto_seccion}px (tope {ALTO_MAXIMO_MOVIL})")

                # 7. calles iguales
                calles = pg.evaluate(
                    "() => { const g = document.querySelector('.credits-grid');"
                    " const r = g.getBoundingClientRect();"
                    " return [Math.round(r.left), Math.round(window.innerWidth - r.right)]; }"
                )
                if calles[0] != CALLE_MOVIL or calles[1] != CALLE_MOVIL:
                    fallos.append(f"[movil] calles {calles}, se esperaban [{CALLE_MOVIL}, {CALLE_MOVIL}]")

                # 8. diana tactil
                diana = pg.evaluate(
                    "() => Math.min(...Array.from(document.querySelectorAll('[data-credit]'))"
                    " .map(n => n.getBoundingClientRect().height))"
                )
                if diana < DIANA_MINIMA:
                    fallos.append(f"[movil] diana tactil de {round(diana)}px (minimo {DIANA_MINIMA})")

            ctx.close()

        # 9. el catastro no existe en los otros dos temas
        for tema in ("vice", "caelestia"):
            ctx = b.new_context(viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            pg.goto(f"{args.url}/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(9000)
            if ir_a_creditos(pg) and catastro_visible(pg):
                fallos.append(f"[{tema}] el catastro se ve y no deberia")
            ctx.close()

        b.close()

    for f in fallos:
        print(f"FALLO {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
