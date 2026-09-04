"""Arnes de la escena Creditos de Caelestia (fase B4, la bandeja de paquetes).

Cada familia de aserciones nacio de un fallo real, documentado en su propio
docstring. Ninguna se acepta sin haberla visto dar rojo contra ese fallo.

Se corre SIEMPRE contra el build de produccion servido (`npm run build &&
npx vite preview --port 4173`), nunca contra `npm run dev`: el HMR corrompe
las medidas de layout y de ScrollTrigger, y miente en los dos sentidos.
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

FALLOS: list[str] = []

_JS_CONTRASTE = r"""() => {
  const px = c => { const k=document.createElement('canvas'); k.width=k.height=1;
    const x=k.getContext('2d'); x.fillStyle='#000'; x.fillRect(0,0,1,1);
    x.fillStyle=c; x.fillRect(0,0,1,1);
    const d=x.getImageData(0,0,1,1).data; return [d[0],d[1],d[2]]; };
  const lum = r => { const f=r.map(v=>{v/=255;
    return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4);});
    return 0.2126*f[0]+0.7152*f[1]+0.0722*f[2]; };
  const rat = (a,b) => { const la=lum(px(a)), lb=lum(px(b));
    const h=Math.max(la,lb), l=Math.min(la,lb); return (h+0.05)/(l+0.05); };
  const opaco = e => { let n=e; while(n && n!==document.documentElement){
    const bg=getComputedStyle(n).backgroundColor;
    if (bg && !/, *0\)$/.test(bg) && bg!=='transparent') return bg;
    n=n.parentElement; } return '#fff'; };

  let peor = 99, cual = '';
  const mide = (nom, el, color) => {
    if (!el || el.getClientRects().length === 0) return;
    const r = rat(color || getComputedStyle(el).color, opaco(el));
    if (r < peor) { peor = r; cual = nom; }
  };

  mide('nombre', document.querySelector('.cae-cred-nombre'));
  mide('detalle', document.querySelector('.cae-cred-detalle'));
  mide('territorio', document.querySelector('.cae-cred-terr'));
  mide('epigrafe', document.querySelector('.cae-cred-cruce > span'));
  mide('cruce', document.querySelector('.cae-cred-cruce-lista li'));
  document.querySelectorAll('.cae-cred-rot h4')
    .forEach((h, i) => mide('rotulo ' + (i + 1), h));
  // El icono se pinta con `fill`, no con `color`, y su fondo es LA FIGURA, no
  // la escena: leer el fondo de la escena daria un numero que nadie ve.
  document.querySelectorAll('.cae-cred-pieza').forEach(t => {
    const sv = t.querySelector('svg'), fg = t.querySelector('.cae-cred-fig');
    if (!sv || !fg || sv.getClientRects().length === 0) return;
    const r = rat(getComputedStyle(sv).fill, getComputedStyle(fg).backgroundColor);
    if (r < peor) { peor = r; cual = 'icono ' + t.dataset.pieza; }
  });
  document.querySelectorAll('.cae-cred-pieza figcaption')
    .forEach(f => mide('nombre ' + f.parentElement.dataset.pieza, f));

  return { peor, cual };
}"""


def check(ok: bool, etiqueta: str) -> None:
    print(("  OK   " if ok else "  FAIL ") + etiqueta)
    if not ok:
        FALLOS.append(etiqueta)


def abre(pagina, base: str) -> None:
    """Abre Creditos y espera a que el workspace asiente.

    Se cambia de workspace pulsando la pastilla del shell, no tocando el hash:
    el hash lo cambia el shell, y forzarlo desde fuera deja el carril a medio
    camino."""
    pagina.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=45000)
    pagina.wait_for_timeout(6000)
    pagina.eval_on_selector_all(
        ".cae-ws",
        "bs=>{const b=bs.find(x=>/Cr..?ditos/.test(x.textContent)); if(b) b.click();}",
    )
    pagina.wait_for_timeout(2500)


def gate_sin_scroll(pagina) -> None:
    """La escena NO puede desplazarse por dentro. Es la ley de la fase A: un
    espacio de trabajo no se desplaza, se cambia.

    Visto rojo con: el estado de partida, 758 / 748 — diez pixeles."""
    print("[1] la escena no tiene scroll interno")
    m = pagina.evaluate(
        """() => {
             const e = document.querySelector('[data-scene="credits"]');
             return {alto: e.scrollHeight, caja: e.clientHeight,
                     ancho: e.scrollWidth, cajaX: e.clientWidth};
           }"""
    )
    check(m["alto"] <= m["caja"], f"sin scroll vertical ({m['alto']} / {m['caja']})")
    check(m["ancho"] <= m["cajaX"], f"sin scroll horizontal ({m['ancho']} / {m['cajaX']})")


def gate_rotulos(pagina) -> None:
    """Los cuatro rotulos de territorio tienen que PINTARSE.

    Visto rojo con: el estado de partida, donde los cuatro existian en el DOM y
    no se pintaba ninguno. Contar nodos no es contar lo que se ve — es el modo
    de fallo central de esta fase, asi que se filtra por getClientRects()."""
    print("[3] los cuatro rotulos de territorio se pintan")
    n = pagina.evaluate(
        """() => [...document.querySelectorAll('[data-scene="credits"] .cae-cred-rot')]
                   .filter(e => e.getClientRects().length > 0).length"""
    )
    check(n == 4, f"cuatro rotulos pintados ({n} de 4)")


def gate_piezas(pagina) -> None:
    """Las 23 tecnologias tienen que estar DENTRO de la caja de la escena, sin
    desplazar. En el estado de partida cuatro de los cinco proyectos de Obra
    quedaban fuera de la ventana por el mismo motivo; aqui se comprueba antes de
    que pase.

    Se compara contra la caja de la escena, no contra el viewport: la ventana
    del workspace mide 1412 x 748 y el viewport 1440 x 900.

    El lado se lee con `offsetWidth`, no con `getBoundingClientRect().width`:
    ese ultimo incluye los transforms, y la Task 5 escala la pieza elegida a
    1,07 al rozarla — con `getBoundingClientRect()` el gate veria dos lados
    distintos y fallaria sin que nada estuviera roto."""
    print("[2] las 23 piezas estan dentro de la caja de la escena")
    m = pagina.evaluate(
        """() => {
             const e = document.querySelector('[data-scene="credits"]');
             const c = e.getBoundingClientRect();
             const t = [...e.querySelectorAll('.cae-cred-pieza')]
                         .filter(x => x.getClientRects().length > 0);
             const fuera = t.filter(x => { const r = x.getBoundingClientRect();
               return r.left < c.left - 1 || r.right > c.right + 1
                   || r.top < c.top - 1 || r.bottom > c.bottom + 1; });
             const lados = [...new Set(t.map(x =>
               x.querySelector('.cae-cred-fig').offsetWidth))];
             return {n: t.length, fuera: fuera.length, lados};
           }"""
    )
    check(m["n"] == 23, f"23 piezas pintadas ({m['n']})")
    check(m["fuera"] == 0, f"ninguna fuera de la caja ({m['fuera']})")
    # El tamano no codifica nada: las dos varas posibles mienten (vara global
    # infla Herramientas porque `tooling` esta en los cinco proyectos; vara por
    # territorio hace a JavaScript —una obra— tan grande como Git —cinco—).
    check(len(m["lados"]) == 1, f"un solo lado en todo el DOM ({m['lados']})")


def gate_cruce(pagina) -> None:
    """El cruce «Aparece en» tiene que caber en los 96 px de cabecera en LAS 23
    piezas, y el estado vacio tiene que leerse.

    Visto rojo con: TypeScript (tres obras) apilaba tres renglones, 111 px en
    una cabecera de 96 — se salia 15 contra el filete de la primera banda. Y
    «Sin obra publicada» iba en `--cae-outline`: 1,80:1 de noche, 2,34:1 a las
    09:00, en 7 de las 23 piezas.

    El contraste se mide PINTANDO el color en un lienzo 1x1 y leyendo el pixel.
    Leer `oklch(...)` con una regex como si fueran bytes RGB da 1.00:1 en todo
    — la trampa que ya costo la fase A."""
    print("[6] el cruce cabe en la cabecera y el estado vacio se lee")
    peor = pagina.evaluate(
        """() => {
          const px = c => { const k=document.createElement('canvas'); k.width=k.height=1;
            const x=k.getContext('2d'); x.fillStyle='#000'; x.fillRect(0,0,1,1);
            x.fillStyle=c; x.fillRect(0,0,1,1);
            const d=x.getImageData(0,0,1,1).data; return [d[0],d[1],d[2]]; };
          const lum = r => { const f=r.map(v=>{v/=255;
            return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4);});
            return 0.2126*f[0]+0.7152*f[1]+0.0722*f[2]; };
          const rat = (a,b) => { const la=lum(px(a)), lb=lum(px(b));
            const h=Math.max(la,lb), l=Math.min(la,lb); return (h+0.05)/(l+0.05); };
          // El contenedor de la escena es TRANSPARENTE: leer su backgroundColor
          // devuelve rgba(0,0,0,0) y el contraste sale contra negro (11,11:1
          // donde lo real era 8,05). Se sube hasta el primer ancestro opaco.
          const opaco = e => { let n=e; while(n && n!==document.documentElement){
            const bg=getComputedStyle(n).backgroundColor;
            if (bg && !/, *0\\)$/.test(bg) && bg!=='transparent') return bg;
            n=n.parentElement; } return '#fff'; };
          const cab = document.querySelector('.cae-cred-cab');
          const cru = document.querySelector('.cae-cred-cruce');
          const res = {sale: 0, peor: 99, cual: ''};
          for (const b of document.querySelectorAll('.cae-cred-pieza')) {
            b.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
            const rc = cru.getBoundingClientRect(), rb = cab.getBoundingClientRect();
            res.sale = Math.max(res.sale, Math.round(rc.bottom - rb.bottom));
            const li = cru.querySelector('li');
            if (li && li.getClientRects().length) {
              const r = rat(getComputedStyle(li).color, opaco(li));
              if (r < res.peor) { res.peor = r; res.cual = b.dataset.pieza; }
            }
          }
          return res;
        }"""
    )
    check(peor["sale"] <= 0, f"el cruce no se sale de la cabecera ({peor['sale']} px)")
    check(
        peor["peor"] >= 4.5,
        f"el cruce se lee en las 23 (peor {peor['peor']:.2f}:1 en «{peor['cual']}»)",
    )


def gate_seleccion(pagina) -> None:
    """Rozar ELIGE, sin pulsar, y el teclado llega a lo mismo que el raton.

    Se comprueba con `hover()` real de Playwright, NO con un MouseEvent
    sintetico: un evento fabricado no dispara `:hover`, asi que un gate escrito
    asi da verde con el hover roto. Ya paso en B2."""
    print("[7] rozar elige, y el foco hace lo mismo")
    antes = pagina.eval_on_selector(".cae-cred-nombre", "e=>e.textContent")
    pagina.hover('.cae-cred-pieza[data-pieza="Git"]')
    pagina.wait_for_timeout(700)
    tras_rozar = pagina.eval_on_selector(".cae-cred-nombre", "e=>e.textContent")
    check(tras_rozar == "Git" and antes != tras_rozar, f"rozar releva la ficha ({tras_rozar})")

    marcadas = pagina.eval_on_selector_all(
        '.cae-cred-pieza[aria-pressed="true"]', "es=>es.map(e=>e.dataset.pieza)"
    )
    check(marcadas == ["Git"], f"solo la elegida lleva aria-pressed ({marcadas})")

    pagina.eval_on_selector('.cae-cred-pieza[data-pieza="Python"]', "e=>e.focus()")
    pagina.wait_for_timeout(700)
    tras_foco = pagina.eval_on_selector(".cae-cred-nombre", "e=>e.textContent")
    check(tras_foco == "Python", f"el foco releva la ficha ({tras_foco})")


def gate_entrada_dispara(pagina, base: str) -> None:
    """La entrada no puede haber ocurrido YA cuando el visitante sigue en
    Titulo — tiene que disparar al llegar de verdad a Creditos, no al montar.

    Visto rojo con: el codigo original ponia `data-cred-entrando` en el mismo
    `mountCaelestiaCreditosBandeja()`, que corre al arrancar la pagina con el
    workspace activo en "1 Titulo". Medido en esa version: a los 1412 ms la
    animacion ya esta corriendo con la escena en x=0 (fuera de la vista del
    visitante, que sigue en Titulo); a los 2343 ms la escena esta a x=4334 px;
    a los 2803 ms ya ha terminado. Cuando el visitante pulsa la pastilla
    «4 Creditos» (aqui, a los ~5000 ms) la bandeja aterriza instalada y
    quieta — la unica escena de Caelestia sin entrada.

    Se mide leyendo el atributo desde dentro de la pagina, nunca con
    `page.screenshot()`: perturba GSAP en headless (bloquea el compositor y
    la timeline salta hacia delante), y aqui ademas moveria el momento exacto
    en que se lee el DOM."""
    print("[9] la entrada no se dispara antes de llegar a Creditos, y si al llegar")
    pagina.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=45000)
    pagina.wait_for_timeout(5000)
    antes = pagina.evaluate(
        """() => {
             const e = document.querySelector('[data-scene="credits"]');
             return e ? e.hasAttribute('data-cred-entrando') : null;
           }"""
    )
    check(antes is False, f"sin 'data-cred-entrando' mientras el visitante sigue en Titulo ({antes})")

    pagina.eval_on_selector_all(
        ".cae-ws",
        "bs=>{const b=bs.find(x=>/Cr..?ditos/.test(x.textContent)); if(b) b.click();}",
    )
    pagina.wait_for_timeout(150)
    tras = pagina.evaluate(
        """() => {
             const e = document.querySelector('[data-scene="credits"]');
             return e ? e.hasAttribute('data-cred-entrando') : null;
           }"""
    )
    check(tras is True, f"'data-cred-entrando' aparece al pulsar la pastilla de Creditos ({tras})")


def gate_entrada(pagina, base: str) -> None:
    """La entrada existe, y `prefers-reduced-motion` la salta ENTERA — al estado
    aterrizado, no a un fotograma intermedio.

    Se mide el estado aterrizado, no un fotograma de la entrada: agrupar por
    posicion mientras GSAP tiene desplazamientos por elemento da lineas fantasma
    de un solo nombre. Con `reduced_motion='reduce'` la animacion se salta y los
    numeros son los del layout."""
    print("[8] la entrada, y el movimiento reducido la salta")
    contexto = pagina.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, reduced_motion="reduce"
    )
    p2 = contexto.new_page()
    abre(p2, base)
    m = p2.evaluate(
        """() => {
             const f = [...document.querySelectorAll('.cae-cred-fig')];
             return {opacos: f.filter(e => +getComputedStyle(e).opacity === 1).length,
                     total: f.length,
                     sinEscala: f.filter(e => {
                       const t = getComputedStyle(e).transform;
                       return t === 'none' || t === 'matrix(1, 0, 0, 1, 0, 0)';
                     }).length};
           }"""
    )
    check(m["opacos"] == m["total"], f"con mov. reducido las 23 estan opacas ({m['opacos']}/{m['total']})")
    check(m["sinEscala"] >= m["total"] - 1, f"y sin escala de entrada ({m['sinEscala']}/{m['total']})")
    contexto.close()


def gate_horas(pagina) -> None:
    """Contraste de TODO lo que lleva tinta, en las 24 posiciones del reloj y en
    los DOS estados de la ficha (con obra y sin ella).

    Los dos estados no son un extra: con solo uno, «Sin obra publicada» —7 de
    las 23 piezas— no se mide nunca. El sabotaje lo demostro: la sonda daba
    verde con ese par a 1,80:1, porque el nodo no existia mientras medía.

    Visto rojo con: el territorio en `--cae-outline` — rojo en las 24 horas.

    El reloj se mueve con la sonda que expone `caelestia.color`; el fondo se
    resuelve subiendo al primer ancestro OPACO, no leyendo el de la escena, que
    es transparente y daria el ratio contra negro.

    Margen de espera tras el roce: `.cae-cred-fig` transiciona `background`
    en 0,22s. Con 260ms de espera (40ms de margen) la sonda cae flaky —
    peor caso saltando entre 3,78:1 y 4,25:1 en «icono Tailwind CSS», a horas
    DISTINTAS entre ejecuciones — porque mide a medio camino de la transicion:
    el `fill` del icono (`--cae-on-primary`, sin transition, cambia al
    instante) ya adelanto al `background` (`--cae-primary`, con transition),
    asi que el par se lee contra un fondo que todavia no ha llegado. Es ruido
    del instrumento, no del diseno: con 700ms el mismo barrido no baja nunca
    de ~5,9:1. 500ms deja mas del doble del margen que la transicion pide."""
    print("[5] contraste en las 24 horas, en los dos estados de la ficha")
    peor = (99.0, "", -1)
    for hora in range(24):
        pagina.evaluate("(m)=>window.__CAE_SET_MINUTOS__ && window.__CAE_SET_MINUTOS__(m)", hora * 60)
        pagina.wait_for_timeout(220)
        for pieza in ("Git", "Tailwind CSS"):
            pagina.hover(f'.cae-cred-pieza[data-pieza="{pieza}"]')
            pagina.wait_for_timeout(500)
            m = pagina.evaluate(_JS_CONTRASTE)
            if m["peor"] < peor[0]:
                peor = (m["peor"], m["cual"], hora)
    check(peor[0] >= 4.5, f"ningun par baja de AA (peor {peor[0]:.2f}:1 en «{peor[1]}» a las {peor[2]:02d}:00)")


def gate_foco(pagina) -> None:
    """El anillo de foco de las 23 piezas tiene que llegar a 3:1 contra su
    fondo (WCAG 2.2 SC 1.4.11, indicador de foco), en los DOS esquemas: es el
    unico indicador visible en los 23 controles interactivos de la escena.

    Visto rojo con: `outline: 2px solid var(--cae-anchor)` contra
    `--cae-elev-1` da 1,38:1 a las 09:00 — invisible 13 de las 24 horas
    (el ancla solo aguanta en esquema oscuro, 11,53:1 a las 03:00).

    Mismas dos trampas que el resto del arnes: el color se pinta en un lienzo
    1x1 y se lee el pixel (una regex sobre `oklch(...)` como si fueran bytes
    RGB da 1,00:1 en todo), y el fondo se resuelve subiendo al primer
    ancestro OPACO — la escena es transparente."""
    print("[4] el anillo de foco llega a 3:1 en los dos esquemas")
    for etiqueta, minutos in (("09:00", 9 * 60), ("03:00", 3 * 60)):
        pagina.evaluate(
            "(m)=>window.__CAE_SET_MINUTOS__ && window.__CAE_SET_MINUTOS__(m)", minutos
        )
        pagina.wait_for_timeout(220)
        r = pagina.evaluate(
            """() => {
              const px = c => { const k=document.createElement('canvas'); k.width=k.height=1;
                const x=k.getContext('2d'); x.fillStyle='#000'; x.fillRect(0,0,1,1);
                x.fillStyle=c; x.fillRect(0,0,1,1);
                const d=x.getImageData(0,0,1,1).data; return [d[0],d[1],d[2]]; };
              const lum = r => { const f=r.map(v=>{v/=255;
                return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4);});
                return 0.2126*f[0]+0.7152*f[1]+0.0722*f[2]; };
              const rat = (a,b) => { const la=lum(px(a)), lb=lum(px(b));
                const h=Math.max(la,lb), l=Math.min(la,lb); return (h+0.05)/(l+0.05); };
              const opaco = e => { let n=e; while(n && n!==document.documentElement){
                const bg=getComputedStyle(n).backgroundColor;
                if (bg && !/, *0\\)$/.test(bg) && bg!=='transparent') return bg;
                n=n.parentElement; } return '#fff'; };
              const b = document.querySelector('.cae-cred-pieza');
              b.focus();
              const anillo = getComputedStyle(b).outlineColor;
              return rat(anillo, opaco(b));
            }"""
        )
        check(r >= 3.0, f"foco a las {etiqueta}: {r:.2f}:1")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    with sync_playwright() as p:
        navegador = p.chromium.launch(
            headless=True, args=["--no-sandbox", "--use-gl=swiftshader"]
        )
        pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
        errores: list[str] = []
        pagina.on("pageerror", lambda e: errores.append(str(e)))
        pagina.on(
            "console",
            lambda m: errores.append(m.text) if m.type == "error" else None,
        )

        abre(pagina, args.base)
        gate_sin_scroll(pagina)
        gate_rotulos(pagina)
        gate_piezas(pagina)
        gate_foco(pagina)
        gate_cruce(pagina)
        gate_seleccion(pagina)
        gate_entrada(pagina, args.base)
        gate_entrada_dispara(pagina, args.base)
        gate_horas(pagina)

        print("[0] consola")
        check(not errores, f"cero errores de consola ({errores[:3]})")
        navegador.close()

    print(f"\n{'TODO OK' if not FALLOS else str(len(FALLOS)) + ' FALLOS'}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
