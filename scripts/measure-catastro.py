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
     Filtra nodos ocultos (`display: none`): con el plegado de movil (ronda
     de arreglo 1 de la tarea 7) tres de cada cuatro parcelas tienen sus
     nombres ocultos, y un nodo sin caja no puede "desbordarla" — medirlo de
     todas formas no falsea el resultado (scrollHeight/clientHeight son 0 en
     los dos lados), pero el filtro deja explicito que la aserción describe
     cajas RENDERIZADAS, no nodos en el DOM.
  6. El alto de la seccion en movil baja de 1100px. Hoy son 1134 y se corta.
  7. Las calles de movil son iguales y de 26px. A 390px el 5vw del tema deja
     20 y el rectangulo queda casi a sangre.
  8. La diana tactil de cada nombre llega a 44px en movil. Medida SOLO sobre
     nombres visibles: con el plegado de movil, tres parcelas ocultan sus
     `[data-credit]` (`display: none`, alto 0) y un `Math.min` sin filtrar
     mediria ese cero en vez de la diana real — un falso rojo que esconde el
     verde real detras. Si no queda ningun nombre visible (las cuatro
     plegadas a la vez, que no deberia poder pasar) el arnes falla explicito
     en vez de devolver `Infinity` en silencio.
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
  12. Las 23 lamparas siguen siendo `animation` de CSS, no tweens de GSAP,
      MIENTRAS ESTAN EN SU VENTANA DE ENTRADA. Reemplaza a un techo
      numerico de `document.getAnimations().length` que se probo y se
      descarto (ronda de arreglo 1 de la tarea 8): el diseño aprobado
      EXIGE 23 lamparas de `color` (barato, no dispara layout) y por
      construccion casi todas se solapan — medido, muestreo cada 16ms
      separando "en efecto" de "produciendo valores de verdad"
      (`effect.getComputedTiming().progress !== null`): ambas cuentas
      COINCIDEN siempre (`1/1 1/1 1/1 14/14 23/23 22/22 21/21 20/20 18/18
      15/15 13/13 10/10`), asi que ni filtrar por fase activa evita el 23.
      Una cuenta cruda no distingue eso de 23 tweens de GSAP escribiendo
      estilo inline por fotograma (caro, con un shader WebGL detras) — el
      numero por si solo no dice CUAL de los dos esta pasando. Lo que si
      lo dice es el mecanismo: si alguien reescribe la lampara como tween,
      `getComputedStyle(n).animationName` deja de ser `hypr-lampara` y esta
      aserción cae.

      IMPORTANTE, ronda de arreglo 2: la primera version de esta aserción
      medía sobre CUALQUIER nombre ya `is-caught`, sin distinguir si su
      entrada seguía en curso o ya se había asentado. Eso obligó al CSS del
      arreglo del destello en movil (`is-caught-still`, ver `themes.css`) a
      usar un `animation-delay` muy negativo en vez de `animation: none`
      — para no borrar `animationName` del computed style y no tirar esta
      misma aserción — cuando las dos soluciones dan EXACTAMENTE el mismo
      resultado visual (el fotograma 100% de `hypr-lampara` esta vacio). La
      asercion mal acotada estaba dictando la implementacion en vez de
      describir el invariante — el mismo defecto que el techo de 12 (ronda
      1). Se corrigio primero la asercion (ahora `ir_a_creditos` sondea
      DENTRO de la pagina, sin ida y vuelta de Playwright, hasta cazar un
      nombre `is-caught` pero AUN NO `is-caught-still` — la ventana real en
      la que la entrada esta en curso, no el estado ya asentado — o falla
      explicito si esa ventana nunca aparece) y DESPUES se simplifico el
      CSS a `animation: none`. Medida SOLO sobre nombres visibles, mismo
      motivo que la aserción 8.
  13. GSAP no toca mas de 13 nodos en el gesto de entrada (`window.__hyprSkills`):
      4 carriles + 4 rotulos + 4 chispas + 1 tween compartido sobre las 4
      franjas = 13. Cuenta los hijos de la timeline cuyos `targets()` son
      Elementos reales (`instanceof Element`), lo que excluye los 4
      `tl.call()` que reparten `.is-caught` — no tocan un nodo, disparan un
      callback. Es el complemento exacto de la 12: si las lamparas migraran
      a GSAP, esta aserción subiria de 13 a 26 (13 + 23 lamparas) y caeria
      aunque la 12 tambien cayera — dos redes sobre el mismo riesgo, cada
      una desde su lado.
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
GSAP_NODOS_MAXIMO = 13


def ir_a_creditos(pg) -> dict | None:
    """Baja hasta creditos y devuelve la ventana activa de la lampara
    (asercion 12), capturada DURANTE el mismo viaje — no despues de que
    todo se asiente, que ya es tarde para verla (ver docstring, asercion
    12). `None` si la escena no existe."""
    top = pg.evaluate(
        "() => { const s = document.querySelector('[data-scene=\"credits\"]');"
        " return s ? s.getBoundingClientRect().top + window.scrollY : -1; }"
    )
    if top < 0:
        return None
    pg.evaluate(f"window.scrollTo(0, {top})")
    # Sondeo DENTRO de la pagina (rapido, sin ida y vuelta de Playwright)
    # mientras Lenis sigue desplazando: caza el primer nombre `is-caught`
    # pero AUN NO `is-caught-still` — la ventana real en la que la entrada
    # esta en curso. Pasado ese punto (~1.1s despues de encenderse, ver
    # themes.css) la lampara se apaga (`animation: none`) y el conjunto
    # queda vacio: medir despues de asentarse deja ciega a la asercion 12.
    ventana = pg.evaluate(
        """
        async () => {
          const deadline = performance.now() + 3000;
          while (performance.now() < deadline) {
            const activos = Array.from(
              document.querySelectorAll('[data-credit].is-caught:not(.is-caught-still)')
            ).filter(n => getComputedStyle(n).display !== 'none');
            if (activos.length > 0) {
              return {
                found: true,
                malos: activos
                  .filter(n => getComputedStyle(n).animationName !== 'hypr-lampara')
                  .map(n => n.textContent.trim()),
                muestra: activos.length,
              };
            }
            await new Promise(r => setTimeout(r, 15));
          }
          return { found: false, malos: [], muestra: 0 };
        }
        """
    )
    # Lenis sigue desplazando despues de un scrollTo: medir antes de que
    # asiente da falsos positivos en las aserciones de posicion. El sondeo
    # de arriba ya ha consumido parte de esta espera.
    pg.wait_for_timeout(1200)
    return ventana


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
            ventana = ir_a_creditos(pg)
            if ventana is None:
                fallos.append(f"[{nombre}] no existe [data-scene=credits]")
                ctx.close()
                continue

            # 12. las lamparas siguen en CSS, MEDIDO EN SU VENTANA ACTIVA
            # (no en el estado ya asentado — ver docstring y `ir_a_creditos`).
            if not ventana["found"]:
                fallos.append(f"[{nombre}] la ventana activa de la lampara nunca aparecio")
            elif ventana["malos"]:
                fallos.append(
                    f"[{nombre}] lamparas sin animationName hypr-lampara"
                    f" en su ventana activa: {ventana['malos']}"
                )

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

            # 5. desbordes — solo sobre nodos renderizados (display !== 'none'):
            # el plegado de movil oculta 3 de cada 4 grupos de nombres, y un
            # nodo sin caja no desborda nada.
            desborda = pg.evaluate(
                "() => Array.from(document.querySelectorAll("
                "  '[data-credit-parcela], [data-credit], [data-credit-strip]'))"
                " .filter(n => getComputedStyle(n).display !== 'none')"
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

                # 13. GSAP no toca mas de 13 nodos en el gesto de entrada.
                # Cuenta los hijos de `window.__hyprSkills` cuyos `targets()`
                # son Elementos reales (excluye los 4 `tl.call()` que solo
                # disparan un callback, sin target de DOM).
                gsap_nodos = pg.evaluate(
                    "() => { const tl = window.__hyprSkills; if (!tl) return -1;"
                    " return tl.getChildren(false, true, false).filter(t => {"
                    "   try { return typeof t.targets === 'function'"
                    "     && t.targets().length > 0"
                    "     && t.targets().every(x => x instanceof Element); }"
                    "   catch (e) { return false; }"
                    " }).length; }"
                )
                if gsap_nodos < 0:
                    fallos.append("[escritorio] window.__hyprSkills no existe")
                elif gsap_nodos > GSAP_NODOS_MAXIMO:
                    fallos.append(
                        f"[escritorio] GSAP toca {gsap_nodos} nodos (tope {GSAP_NODOS_MAXIMO})"
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

                # 8. diana tactil — solo sobre nombres VISIBLES. Con el
                # plegado de movil, tres parcelas ocultan sus `[data-credit]`
                # (`display: none`, alto 0): un Math.min sin filtrar mide ese
                # cero, no la diana real, y falla en verde falso. Sin ningun
                # nombre visible (no deberia poder pasar: siempre hay una
                # parcela abierta) el arnes falla explicito en vez de callar.
                alturas_visibles = pg.evaluate(
                    "() => Array.from(document.querySelectorAll('[data-credit]'))"
                    " .filter(n => getComputedStyle(n).display !== 'none')"
                    " .map(n => n.getBoundingClientRect().height)"
                )
                if not alturas_visibles:
                    fallos.append("[movil] ningun nombre visible: no se puede medir la diana tactil")
                else:
                    diana = min(alturas_visibles)
                    if diana < DIANA_MINIMA:
                        fallos.append(f"[movil] diana tactil de {round(diana)}px (minimo {DIANA_MINIMA})")

            ctx.close()

        # 9. el catastro no existe en los otros dos temas
        for tema in ("vice", "caelestia"):
            ctx = b.new_context(viewport={"width": 1440, "height": 900})
            pg = ctx.new_page()
            pg.goto(f"{args.url}/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(9000)
            if ir_a_creditos(pg) is not None and catastro_visible(pg):
                fallos.append(f"[{tema}] el catastro se ve y no deberia")
            ctx.close()

        b.close()

    for f in fallos:
        print(f"FALLO {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
