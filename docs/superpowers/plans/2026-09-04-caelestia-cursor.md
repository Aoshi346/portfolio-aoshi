# Caelestia — el cursor «la gota» · Plan de implementación

> **Para ejecutores agénticos:** SUB-SKILL OBLIGATORIA: usa
> `superpowers:subagent-driven-development` (recomendada) o
> `superpowers:executing-plans` para ejecutar este plan tarea a tarea. Los pasos
> llevan casilla (`- [ ]`) para marcarlos **en el momento**, no al final.

**Objetivo:** que Caelestia deje de usar el puntero del sistema y tenga su propio cursor —una gota
del pigmento de la hora que se tensa sobre lo pulsable, se derrama sobre lo que responde y deja
cerco al soltar—, con la misma limpieza y el mismo reparto de señales que los cursores de Vice y
Hyprland.

**Arquitectura:** un módulo nuevo (`src/components/caelestiaCursor.ts`) monta **tres elementos DOM**
en `#app` —la gota, la mancha del derrame y los cercos— y los mueve leyendo eventos de puntero.
**DOM y no `<canvas>`**, al revés que Hyprland: la perla necesita `backdrop-filter` y
`mix-blend-mode`, que un contexto 2D no da. **Sin GSAP**: todo el movimiento son transiciones y
animaciones CSS, así que el módulo no importa nada y el montaje no tiene que volverse `async`. El
color no se calcula en ningún sitio: se leen los tokens que escribe `caelestia.color.ts`.

**Stack:** Vite 8 · TypeScript ~6 `strict` · Tailwind 4. Sin framework, sin backend, **sin GSAP en
este módulo**. Los gates son un arnés Playwright en Python contra el **build de producción
servido** — no hay runner de tests JS en el repo y no se añade ninguno.

**Spec:** `docs/superpowers/specs/2026-09-04-caelestia-cursor-design.md` — **se lee entero antes de
empezar**, incluida la `### Corrección del 2026-09-04` de la sección `## El reparto de señales`, que
es la que fija dónde cuelga la lista blanca. El plan argumenta desde ahí.

## Estado de ejecución (2026-09-05)

Ejecutado con `superpowers:subagent-driven-development` en el worktree
`/home/aoshi/proyectos/portfolio-aoshi-cursor`, rama `design/caelestia-cursor`, desde `10fc4af`.

| tarea | estado | commits | rondas de arreglo |
|---|---|---|---|
| 1 · el arnés en rojo | **cerrada**, revisión limpia | `a004d2d` | 0 |
| 2 · el módulo y la lista blanca | **cerrada** | `dd0a699`, `b4ad045` | 1 |
| 3 · el derrame | **cerrada** | `c78f772`, `35128e4`, `b1ac3d7`, `5582599` | 3 |
| 4 · el cerco | **cerrada** | `9fae5be`, `3a97324` | 1 |
| 5 · lente, sombra, rebote y noche | **cerrada** | `85d9e3d`, `9c763c7` | 1 |
| 6 · el estado rancio | **cerrada** | `4b0c6cf`, `4c0eb85` | 1 |
| 7 · el barrido de 24 horas | **cerrada** | `8e1198e`, `6a4ad82` | 1 (la recalibración) |
| 8 · limpieza y consola | **cerrada** | `0b4b7b5` | 1 (la fuga de cercos, prevista en el Task 4) |
| 9 · cerrar documentación | **cerrada** salvo la fila de `.claude/` (queda para el merge) | — | 0 |

El arnés va por **53 aserciones en verde**, gate 6 incluido. La tarea 7 estuvo en rojo un día: el
derrame nocturno hundía la leyenda de Obra a 4,06:1. Se resolvió **calibrando, no cambiando de
mecanismo** — opacidad de noche 0,30 → 0,20, peor caso 4,92:1. La alternativa que preveía el spec
(`background-image` bajo el texto) habría sido peor: la tarjeta de Obra lleva un `<img>` que lo
habría tapado. Detalle y tabla en la pregunta 4 del spec.

**El registro de la ejecución vive en `.superpowers/sdd/2026-09-04-caelestia-cursor/progress.md`**
(directorio ignorado por git): lleva el barrido previo de conflictos, cada ronda de arreglo, los
hallazgos menores aparcados y **todas las decisiones que el controlador tomó en nombre de Aoshi**.
Si ese directorio se pierde, la historia de git es el registro que queda.

**Lo que la ejecución encontró y el plan no preveía**, resumido, porque cambia cómo hay que leer
los pasos de más abajo:

- **La lista blanca del CSS no podía funcionar como estaba escrita.** La raíz no alcanza a los
  pulsables: `<button>` y `<a>` declaran su propio `cursor` en la hoja del navegador, así que
  hacía falta una regla de opt-in explícita. Y la regla de rescate que este plan escribió para
  el enlace externo y la galería **rompía las dos señales que venía a proteger** — sobre un
  enlace, `cursor: auto` pisa el `pointer` nativo, y sobre `.gallery-track` pisaba su `grab`.
- **`cursor: auto` no computa a `"text"`**: el navegador devuelve la palabra clave tal cual, así
  que la regla y su aserción eran incoherentes. El texto corrido lleva `cursor: text` literal,
  que diverge de lo que hacen Vice y Hyprland.
- **El gate del estado rancio, tal como lo escribió este plan, era infalsificable.** Chromium
  dispara `pointerout` sobre el elemento mojado en cuanto su escena pasa a `inert`, unos 50 ms
  antes de que el carril termine, y eso sana el estado por la vía normal. Quitar el listener no
  ponía el gate en rojo. Ahora el gate tiene dos familias: el mecanismo propio con la sanación
  nativa suprimida, y el camino que de verdad recorre el visitante.
- **Las guardias de `prefers-reduced-motion` de este plan no ganaban la cascada** (`@media` no
  suma especificidad), así que no desactivaban nada.
- **El script de muestreo del rebote leía `transform`** cuando la animación mueve la propiedad
  `scale`: medía la propiedad equivocada.
- **Un umbral estaba puesto más fino que el ruido de su instrumento** (`> 0.9` tras una espera
  fija para una transición de 420 ms). Se sustituyó por una espera determinista a que el valor
  asiente, con la aserción más estricta, no más laxa.

---

## Restricciones globales

- **Cero `any`.** `strict` está activo; usa `unknown` + guardas.
- **Sin `console.log`** en producción. **Cero emojis** en código, docs y commits.
- **Todo módulo de tema devuelve un handle con `destroy()`**, y se llama en `pagehide`.
- **`prefers-reduced-motion`**: aquí el módulo **no se monta** (puerta en `main.ts`), y además el CSS
  lo apaga por si acaso. Recuerda que el selector universal `*` **no alcanza a los
  pseudo-elementos**: cada `::before` animado necesita su propia regla.
- **Nunca `gsap.from`** — en este módulo no hay GSAP en absoluto, así que la regla se cumple sola.
- **`src/data/content.ts` no se toca.** Este dispositivo no escribe ni un carácter en pantalla.
- **Vice y Hyprland no se tocan.** `viceCursor.ts` y `hyprCursor.ts` se leen como contrato y no se
  editan. Ningún cambio puede alterar una ruta de código que recorran esos dos temas.
- **Las fases A, B1, B2, B3 y B4 de Caelestia no se tocan.** Ni un atributo nuevo en sus módulos.
  La única regla que este plan escribe sobre un elemento de B4 (`.cae-cred-pieza`) vive **dentro del
  bloque del cursor y colgando de `.caelestia-cursor-ready`**, así que sin el cursor no existe.
- **Nada se llama antes de estar declarado.** Un `const` de nivel superior está en zona muerta
  hasta su línea, y esta sesión ya reventó dos maquetas por eso (`Cannot access 'tl' before
  initialization`). En el navegador el script muere en silencio y el dispositivo no existe: solo lo
  caza escuchar `pageerror`, que es el gate 8.
- **Ningún gate se acepta sin haberlo visto dar rojo** contra el fallo exacto que dice cazar. Cada
  tarea trae su sabotaje escrito; ejecútalo, mira el rojo, deshaz el sabotaje.
- **Ninguna aserción sobre algo inalcanzable.** `.gallery-track` existe en el DOM pero es invisible
  en Caelestia: no se afirma que se mide. Es el décimo instrumento tautológico lo que se está
  evitando aquí.
- Verifica **siempre** contra el build servido (`npm run build && npx vite preview --port 4173`),
  **nunca** contra `npm run dev`: el HMR corrompe las medidas.
- Antes de medir, comprueba de quién es el puerto: `ss -ltnp | grep 4173` y
  `readlink /proc/<pid>/cwd`. **Mata por PID**: `pkill -f "vite preview"` se mata a sí mismo desde
  el harness de Bash porque el patrón casa con su propia línea de comando.
- **Un `MouseEvent` sintético no dispara `:hover`.** Todo lo que hace este dispositivo ocurre en
  hover: usa `page.hover()` y `page.mouse.move()` reales, siempre.
- El tema se sortea por visita: **toda URL lleva `?theme=caelestia`**.
- `npm` necesita Node 22: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`.
- **Se trabaja en el worktree** `/home/aoshi/proyectos/portfolio-aoshi-cursor`, rama
  `design/caelestia-cursor`. El repo principal tiene otra sesión con su `vite preview` en el 4193:
  no la toques.
- Cada tarea acaba en commit, con `npm run build` y `npm run lint` verdes antes.

## Hechos medidos que este plan da por establecidos

No los vuelvas a averiguar; sí compruébalos si algo no cuadra. Medidos el 2026-09-04 en el build
servido, ventana 1440×900, `?theme=caelestia`:

| hecho | valor |
|---|---|
| los cinco workspaces | hijos directos de `main`: `#hero[data-scene=hero]`, `#quien-es[data-scene=about]`, **`#obra` (sin `data-scene`)**, `#creditos[data-scene=credits]`, `#contacto[data-scene=contacto]` |
| las tarjetas de Obra | `.cae-obra-card` → `.cae-obra-row` → `#obra.obra-rail` → `main`. **Fuera de `[data-scene]`** |
| barra y dock | hijos de `#app`, **fuera de `main`** |
| `[data-scene="obra"]` | existe, anidado en `#obra`, y mide **0×0** (B3 lo oculta) |
| `main` | lleva `transform` y `will-change: transform` (es el carril) |
| `#app` | **sin** `transform`: un `position: fixed` dentro suyo sí es relativo al viewport (probado) |
| `button[aria-pressed]` | **46 nodos**, de los que 23 son visibles (las piezas) y 23 son las filas `.credit` genéricas, ocultas |
| `.gallery-track` | 5 nodos, **0 visibles** |
| `a[target="_blank"]` visibles | `.cae-dock-item` ×2 y `.contacto-bar` ×2 |
| texto corrido alcanzable | `#quien-es`: `p.ficha-frase`, `dt.ficha-k`. `#contacto`: `p.contacto-lead`. `#creditos`: `p.cae-cred-detalle` |
| elementos con scroll interno | **ninguno hoy** (`.scene-surface` declara `overflow-y: auto` pero no desborda) |
| `sceneNav` | `display: none` en Caelestia — **no hace falta** la línea que Hyprland sí necesita |

## Estructura de ficheros

| fichero | responsabilidad |
|---|---|
| `src/components/caelestiaCursor.ts` **(nuevo)** | todo el dispositivo: crear los elementos, resolver la zona bajo el puntero, decidir la familia de la diana, mojar/secar, dejar cerco, y `destroy()`. Sin color calculado, sin GSAP, sin tocar el DOM de ninguna diana. |
| `src/themes/themes.css` **(modificar, al final del bloque de Caelestia)** | la lista blanca de `cursor`, el aspecto de la gota, la mancha y el cerco, y el material de noche. Todo colgando de `.caelestia-cursor-ready`. |
| `src/main.ts` **(modificar)** | la puerta de montaje con las tres condiciones, y `destroy()` en `pagehide`. |
| `scripts/measure-caelestia-cursor.py` **(nuevo)** | los ocho gates. |
| `.claude/rules/verification.md` **(modificar)** | una fila en la tabla de arneses. |
| `CLAUDE.md` y `.claude/CLAUDE.md` **(modificar, solo en la última tarea)** | el estado del dispositivo. |

**Dónde se montan los elementos:** en `#app` (el `host` que `main.ts` pasa, igual que los otros dos
cursores). **Nunca dentro de `main`**: `main` lleva `transform`, y un `position: fixed` dentro de un
elemento transformado deja de ser relativo al viewport — se posicionaría contra el carril, que está
desplazado 4320 px.

**Cómo crece el arnés:** cada tarea que añade un gate añade **dos** cosas, la función y su llamada
dentro de `main()`. Un gate definido y no llamado es un gate que nunca da rojo — la forma más
barata de tener un instrumento tautológico. El orden de llamada es el número de gate, y **el de
consola va siempre el último**: recoge los errores de toda la ejecución, así que llamarlo antes
mediría media página.

**Contrato del módulo con el arnés** (escríbelo en el docstring, porque es acoplamiento real):

- El módulo **nunca escribe `display`** en la mancha. El arnés se apoya en eso para apagar el
  derrame y hacer la comparación A/B sin que el siguiente fotograma se lo pise.
- La sonda `mancha()` devuelve el avance **pintado** (leído de `getComputedStyle`), no el valor
  objetivo que el módulo acaba de escribir. Un gate que leyera el objetivo sería tautológico:
  mediría la intención, no el resultado.

---

## Task 1: El arnés, con los dos gates que hoy ya dan rojo

Primero el instrumento. Hoy no existe el módulo, así que los dos gates de esta tarea **tienen que
fallar**: eso es lo que demuestra que miden algo.

**Files:**
- Create: `scripts/measure-caelestia-cursor.py`

**Interfaces:**
- Consumes: nada.
- Produces: para las tareas siguientes — `check(ok: bool, etiqueta: str) -> None`,
  `abre(pagina, base: str, escena: str = "creditos") -> None`,
  `FALLOS: list[str]`, y las constantes `PRESSABLE`, `NATIVE_ZONE`, `HOVER_SELECT`.

- [x] **Step 1: Escribe el arnés con el esqueleto y los gates 1 y 2**

```python
"""Arnes del cursor de Caelestia (la gota).

Cada familia de aserciones nacio de un fallo concreto y lo dice en su
docstring. Ninguna se acepta sin haberla visto dar rojo contra ese fallo.

Se corre SIEMPRE contra el build de produccion servido (`npm run build &&
npx vite preview --port 4173`), nunca contra `npm run dev`: el HMR corrompe
las medidas.

TODO hover es hover REAL (`page.hover` / `page.mouse.move`). Un `MouseEvent`
sintetico no dispara `:hover`, y todo lo que hace este dispositivo ocurre en
hover -- es la trampa que ya costo la fase B2.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

FALLOS: list[str] = []

# Los mismos tres selectores que el modulo. Si divergen, el arnes deja de
# medir el modulo y pasa a medir una copia suya.
PRESSABLE = 'button, a[href]:not([target="_blank"])'
NATIVE_ZONE = '.gallery-track, a[target="_blank"], p, li, dd, dt, figcaption, blockquote'
HOVER_SELECT = "button[aria-pressed]"

# Indice de cada escena en la barra de workspaces.
ESCENAS = {"hero": 0, "quien-es": 1, "obra": 2, "creditos": 3, "contacto": 4}


def check(ok: bool, etiqueta: str) -> None:
    print(("  OK   " if ok else "  FAIL ") + etiqueta)
    if not ok:
        FALLOS.append(etiqueta)


def abre(pagina, base: str, escena: str = "creditos") -> None:
    """Abre Caelestia y cambia al workspace pedido pulsando su pastilla.

    Se cambia pulsando, no tocando el hash: el hash lo cambia el shell, y
    forzarlo desde fuera deja el carril a medio camino (lecccion de B4).
    """
    pagina.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=45000)
    pagina.wait_for_timeout(6000)
    if escena != "hero":
        pagina.eval_on_selector_all(".cae-ws", "(bs, i) => bs[i].click()", ESCENAS[escena])
        pagina.wait_for_timeout(1500)


def estado(pagina) -> str:
    return pagina.evaluate("() => window.__caeCursor__ ? window.__caeCursor__.estado() : 'sin-modulo'")


def gate_presencia(navegador, base: str) -> None:
    """Gate 1 -- presencia por tema y las TRES puertas de montaje.

    Falla si el modulo monta donde no debe, y -- lo que de verdad importa --
    si en tactil o con movimiento reducido se DESCARGA el chunk. La puerta
    tiene que estar antes del `import()`, no dentro del modulo: en tactil el
    coste correcto es cero, no "cero animacion". Por eso se vigila la
    peticion de red, no el DOM.
    """
    print("[1] presencia por tema y puertas de montaje")

    for tema, debe in (("caelestia", True), ("vice", False), ("hyprland", False)):
        contexto = navegador.new_context(viewport={"width": 1440, "height": 900})
        pagina = contexto.new_page()
        pagina.goto(f"{base}/?theme={tema}", wait_until="domcontentloaded", timeout=45000)
        pagina.wait_for_timeout(6000)
        hay = pagina.evaluate("() => !!document.querySelector('.cae-cursor')")
        listo = pagina.evaluate(
            "() => document.documentElement.classList.contains('caelestia-cursor-ready')"
        )
        check(hay is debe, f"[1] {tema}: la gota {'monta' if debe else 'NO monta'}")
        check(listo is debe, f"[1] {tema}: la clase ready {'esta' if debe else 'NO esta'}")
        if debe:
            # Nada de esto puede llegar al arbol de accesibilidad: son tres
            # elementos decorativos que siguen al raton.
            ocultos = pagina.evaluate(
                """() => [...document.querySelectorAll('.cae-cursor, .cae-cursor-mancha')]
                     .every(e => e.getAttribute('aria-hidden') === 'true')"""
            )
            check(ocultos, "[1] los elementos del cursor van con aria-hidden")
        contexto.close()

    # Tactil y movimiento reducido: el chunk NO se pide.
    for etiqueta, kwargs in (
        ("movimiento reducido", {"reduced_motion": "reduce", "viewport": {"width": 1440, "height": 900}}),
        ("tactil", {"has_touch": True, "is_mobile": True, "viewport": {"width": 390, "height": 844}}),
    ):
        contexto = navegador.new_context(**kwargs)
        pagina = contexto.new_page()
        pedidos: list[str] = []
        pagina.on("request", lambda r: pedidos.append(r.url))
        pagina.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=45000)
        pagina.wait_for_timeout(6000)
        chunk = [u for u in pedidos if "caelestiaCursor" in u]
        check(not chunk, f"[1] {etiqueta}: el chunk del cursor no se descarga ({len(chunk)})")
        check(
            not pagina.evaluate("() => !!document.querySelector('.cae-cursor')"),
            f"[1] {etiqueta}: la gota no monta",
        )
        contexto.close()


def gate_senales(p_pagina, base: str) -> None:
    """Gate 2 -- el reparto de senales.

    Sustituir el puntero es legitimo; borrar las otras senales no. Y la
    trampa propia de esta pagina: `figcaption` esta en NATIVE_ZONE y vive
    DENTRO de los botones de Obra y de Creditos. Con la resolucion ingenua
    (`closest()` a secas, gana el mas cercano) la gota se apaga sobre la
    leyenda de cada tarjeta y sobre el nombre de cada pieza -- justo encima
    de las dianas.

    NO se afirma nada sobre `.gallery-track`: existe en el DOM pero es
    invisible en Caelestia (lo oculta B3), asi que una asercion suya seria
    tautologica. Su linea en el CSS es preventiva y esta declarada como tal
    en el spec.
    """
    print("[2] reparto de senales")
    pagina = p_pagina

    # Texto corrido: I-beam del sistema y gota apagada.
    abre(pagina, base, "contacto")
    pagina.hover("p.contacto-lead")
    pagina.wait_for_timeout(300)
    check(estado(pagina) == "apagada", "[2] sobre texto corrido la gota se apaga")
    check(
        pagina.eval_on_selector("p.contacto-lead", "el => getComputedStyle(el).cursor") == "text",
        "[2] sobre texto corrido manda el I-beam del sistema",
    )

    # Enlace externo: pointer nativo.
    check(
        pagina.eval_on_selector(
            '.contacto-bar[target="_blank"]', "el => getComputedStyle(el).cursor"
        )
        == "pointer",
        "[2] el enlace externo conserva el pointer nativo",
    )

    # La leyenda de una tarjeta de Obra: DENTRO de un pulsable, manda el pulsable.
    abre(pagina, base, "obra")
    pagina.hover(".cae-obra-card .cae-obra-caption")
    pagina.wait_for_timeout(300)
    check(estado(pagina) == "perla", "[2] sobre la leyenda de una tarjeta la gota sigue encendida")
    check(
        pagina.eval_on_selector(
            ".cae-obra-card .cae-obra-caption", "el => getComputedStyle(el).cursor"
        )
        == "none",
        "[2] la leyenda de una tarjeta no recupera el I-beam",
    )

    # El nombre de una pieza de Creditos: igual, y ademas es familia de roce.
    abre(pagina, base, "creditos")
    pagina.hover(".cae-cred-pieza .cae-cred-nom")
    pagina.wait_for_timeout(400)
    check(estado(pagina) == "derrame", "[2] sobre el nombre de una pieza la gota sigue derramada")


ARGS = ["--no-sandbox", "--use-gl=swiftshader"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=ARGS)
        contexto = navegador.new_context(viewport={"width": 1440, "height": 900})
        pagina = contexto.new_page()
        errores: list[str] = []
        pagina.on("pageerror", lambda e: errores.append(f"pageerror: {e}"))
        pagina.on(
            "console",
            lambda m: errores.append(f"console.error: {m.text}") if m.type == "error" else None,
        )

        gate_presencia(navegador, args.base)
        gate_senales(pagina, args.base)

        print("[8] consola")
        check(not errores, f"[8] cero errores de consola ({errores[:3]})")

        navegador.close()

    print()
    if FALLOS:
        print(f"FALLOS ({len(FALLOS)}):")
        for f in FALLOS:
            print("  - " + f)
        return 1
    print("Todo verde.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 2: Levanta el build servido y corre el arnés para verlo en ROJO**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
cd /home/aoshi/proyectos/portfolio-aoshi-cursor
npm run build
nohup npx vite preview --port 4173 --strictPort > /tmp/preview-cursor.log 2>&1 &
sleep 4
ss -ltnp | grep 4173                      # comprueba que el puerto es TUYO
readlink /proc/$(ss -ltnp | grep 4173 | grep -oP 'pid=\K[0-9]+')/cwd
python3 scripts/measure-caelestia-cursor.py --base http://localhost:4173
```

Esperado: **FAIL** en «caelestia: la gota monta», «caelestia: la clase ready esta», y en los cuatro
checks de estado del gate 2 (`estado()` devuelve `'sin-modulo'`). Los de Vice, Hyprland, táctil y
movimiento reducido salen **OK** desde ya, porque hoy no monta nada en ningún sitio: eso es correcto
y no es trampa, siempre que los de Caelestia estén en rojo. Si TODO sale verde, el arnés no está
midiendo: revísalo antes de seguir.

- [x] **Step 3: Commit**

```bash
git add scripts/measure-caelestia-cursor.py
git commit -m "test(cursor): arnes del cursor de Caelestia con los gates 1 y 2 en rojo"
```

---

## Task 2: El módulo mínimo — la perla, la resolución de zona y la lista blanca

Al final de esta tarea la gota existe, se mueve sin inercia, se apaga sobre texto y se enciende
sobre lo pulsable. Todavía no se derrama.

**Files:**
- Create: `src/components/caelestiaCursor.ts`
- Modify: `src/themes/themes.css` (al final del bloque de Caelestia)
- Modify: `src/main.ts`
- Modify: `scripts/measure-caelestia-cursor.py` (añade el gate 4)

**Interfaces:**
- Consumes: del Task 1 — `check`, `abre`, `estado`, `FALLOS`.
- Produces:
  - `mountCaelestiaCursor(host: HTMLElement): CaelestiaCursorHandle` con
    `CaelestiaCursorHandle = { destroy: () => void }`.
  - La sonda `window.__caeCursor__` con
    `{ estado(): "reposo" | "perla" | "derrame" | "apagada"; diana(): HTMLElement | null; mancha(): number; destroy(): void }`.
    En este Task `diana()` devuelve siempre `null` y `mancha()` siempre `0`; el Task 3 los llena.
  - Clases CSS: `.cae-cursor`, `.cae-cursor-perla`, `.cae-cursor-nucleo`, y la clase de raíz
    `.caelestia-cursor-ready`.

- [x] **Step 1: Escribe el módulo**

Crea `src/components/caelestiaCursor.ts`:

```ts
export interface CaelestiaCursorHandle {
  destroy: () => void;
}

/*
 * Cursor propio de Caelestia: una gota del pigmento de la hora.
 *
 * Spec: docs/superpowers/specs/2026-09-04-caelestia-cursor-design.md
 *
 * Sobre lo que se pulsa se tensa en perla y espera; al pulsar se derrama y
 * encharca la diana. Sobre lo que YA elige al rozarlo (las 23 piezas de
 * Creditos) se derrama al entrar: ya esta mojado. Los dos estados no son dos
 * simbolos -- son el MISMO gesto disparado en dos momentos, que es lo que
 * permite tener dos estados sin que el cursor necesite manual.
 *
 * Reparto de senales, identico al cerrado en Vice y en Hyprland porque el
 * problema es el mismo -- sustituir el puntero es legitimo, borrar las otras
 * senales no:
 *
 *   `pointer`  -> lo sustituye esta gota.
 *   `grab` / `grabbing` (`.gallery-track`) -> NATIVOS.
 *   I-beam en texto -> NATIVO.
 *   Enlaces `target="_blank"` -> NATIVOS. Abren pestana nueva.
 *
 * DOM y no `<canvas>`, al reves que Hyprland: la perla necesita
 * `backdrop-filter` y `mix-blend-mode`, que un contexto 2D no da.
 *
 * SIN GSAP. Todo el movimiento son transiciones y animaciones CSS: asi el
 * montaje no tiene que volverse `async` por un `import()` de la libreria, y
 * un dispositivo que se repinta con el raton no arrastra una timeline.
 *
 * NINGUN color se calcula aqui. Todo sale de los tokens que escribe
 * `caelestia.color.ts`, y el esquema lo dice `[data-cae-esquema]`.
 *
 * ---------------------------------------------------------------------
 * CONTRATO CON EL ARNES (`scripts/measure-caelestia-cursor.py`):
 *
 *  1. Este modulo NUNCA escribe `display` en la mancha. El arnes lo apaga
 *     con `display: none` para su comparacion A/B, y necesita que el
 *     siguiente fotograma no se lo pise.
 *  2. `__caeCursor__.mancha()` devuelve el avance PINTADO, leido de
 *     `getComputedStyle`, no el valor objetivo que este modulo acaba de
 *     escribir. Un gate que leyera el objetivo mediria la intencion y no el
 *     resultado: seria tautologico.
 * ---------------------------------------------------------------------
 */

// Pulsables que la gota viste. El enlace externo queda fuera aposta.
const PRESSABLE = 'button, a[href]:not([target="_blank"])';
// Zonas donde manda el navegador y la gota se apaga.
const NATIVE_ZONE = '.gallery-track, a[target="_blank"], p, li, dd, dt, figcaption, blockquote';
/*
 * De entre los pulsables, los que YA responden al roce: ahi la gota se
 * derrama al entrar, sin esperar clic.
 *
 * `aria-pressed` no es taxonomia inventada para el cursor: las 23 piezas de
 * Creditos lo llevan porque SON botones de estado
 * (`caelestiaCreditosBandeja.ts:76`), y ni las tarjetas de Obra ni las
 * pastillas del shell lo llevan. Si manana una diana nueva elige al rozar,
 * llevara `aria-pressed` porque es lo correcto para ella, y la gota la
 * vestira sola.
 *
 * OJO: el selector casa 46 nodos, no 23 -- las filas `.credit` del
 * `credits.ts` generico tambien lo llevan, ocultas por
 * `.credits-grid { display: none }`. No es un problema (un nodo oculto no
 * recibe `pointerover`), pero NADIE puede contar nodos para decidir nada.
 */
const HOVER_SELECT = "button[aria-pressed]";

type Estado = "reposo" | "perla" | "derrame" | "apagada";

export function mountCaelestiaCursor(host: HTMLElement): CaelestiaCursorHandle {
  const controller = new AbortController();
  const { signal } = controller;

  const perla = document.createElement("div");
  perla.className = "cae-cursor-perla";
  const nucleo = document.createElement("i");
  nucleo.className = "cae-cursor-nucleo";
  const cursor = document.createElement("div");
  cursor.className = "cae-cursor";
  cursor.setAttribute("aria-hidden", "true");
  cursor.dataset.estado = "reposo";
  cursor.append(perla, nucleo);

  /*
   * Se cuelga de `host` (`#app`) y NUNCA de `main`: `main` es el carril de
   * workspaces y lleva `transform`, y un `position: fixed` dentro de un
   * elemento transformado deja de ser relativo al viewport -- se colocaria
   * contra un carril desplazado 4320px. Medido: `#app` no tiene transform.
   */
  host.append(cursor);

  let x = 0;
  let y = 0;
  let dentro = false;
  let diana: HTMLElement | null = null;
  let estadoActual: Estado = "reposo";
  let stale = false;
  let frame = 0;

  const setEstado = (siguiente: Estado): void => {
    if (estadoActual === siguiente) return;
    estadoActual = siguiente;
    cursor.dataset.estado = siguiente;
  };

  /*
   * `closest()` con los dos selectores a la vez devuelve el ancestro (o el
   * propio nodo) MAS CERCANO que case cualquiera de los dos: el mas cercano
   * gana con independencia del orden en que se escriban. Eso ya resuelve el
   * caso de Hyprland (un boton anidado dentro de un `<p>`).
   *
   * Lo que NO resuelve es el inverso, que en esta pagina es la norma: la
   * leyenda de una tarjeta de Obra (`figcaption.cae-obra-caption`) y el
   * nombre de una pieza de Creditos (`figcaption.cae-cred-nom`) son zona
   * nativa y viven DENTRO del boton. Con `closest()` a secas la gota se
   * apagaria justo encima de las dianas. De ahi la segunda vuelta: si la
   * zona nativa esta dentro de un pulsable, manda el pulsable.
   *
   * El CSS lleva la misma inversion (`:not(button *, a[href] *)`), y las dos
   * tienen que moverse juntas: si divergen, el glifo del sistema y el estado
   * de la gota se contradicen sobre el mismo pixel.
   */
  const resolver = (objetivo: Element | null): void => {
    const zona = objetivo?.closest<HTMLElement>(`${PRESSABLE}, ${NATIVE_ZONE}`) ?? null;
    if (!zona) {
      diana = null;
      setEstado(dentro ? "reposo" : "apagada");
      return;
    }
    const pulsable = zona.matches(PRESSABLE)
      ? zona
      : (zona.parentElement?.closest<HTMLElement>(PRESSABLE) ?? null);
    if (!pulsable) {
      diana = null;
      setEstado("apagada");
      return;
    }
    diana = pulsable;
    setEstado("perla");
  };

  /*
   * La posicion se escribe en el propio evento, sin suavizar. Un cursor con
   * inercia miente sobre donde esta el raton, y en Creditos hay 23 dianas
   * contiguas donde eso se lee como retraso. Lo que se interpola es el
   * TAMANO y la opacidad, en CSS.
   */
  const alMover = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
    x = evento.clientX;
    y = evento.clientY;
    if (!dentro) {
      dentro = true;
      setEstado(diana ? "perla" : "reposo");
    }
    cursor.style.transform = `translate3d(${x}px, ${y}px, 0)`;
  };

  /*
   * El estado se resuelve en `pointerover`, que solo dispara al cambiar de
   * elemento: asi los `closest()` cuestan una vez por transicion y no sesenta
   * veces por segundo.
   */
  const alEntrar = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
    if (!(evento.target instanceof Element)) return;
    resolver(evento.target);
  };

  const alSalirDelDocumento = (): void => {
    dentro = false;
    diana = null;
    setEstado("apagada");
  };

  /*
   * Cuando cambia lo que hay bajo un raton QUIETO no llega ningun evento de
   * puntero. En Caelestia pasa de dos formas, y las dos son la norma y no la
   * excepcion: al cambiar de workspace (el carril se lleva la diana y deja
   * otra escena debajo) y si algun contenedor desplaza su contenido. La
   * comprobacion se aplaza al siguiente fotograma en vez de hacerse en el
   * propio evento, porque llegan en rafagas.
   *
   * El `scroll` va en fase de CAPTURA sobre `document`: los eventos de
   * scroll de un contenedor interno NO burbujean, asi que un oyente en
   * `window` no los ve. Hoy ningun contenedor de Caelestia desborda -- es
   * red preventiva, y esta escrito para que nadie la confunda con algo
   * medido.
   */
  const marcarRancio = (): void => {
    stale = true;
  };

  window.addEventListener("pointermove", alMover, { passive: true, signal });
  window.addEventListener("pointerover", alEntrar, { passive: true, signal });
  window.addEventListener("resize", marcarRancio, { passive: true, signal });
  document.addEventListener("scroll", marcarRancio, { passive: true, capture: true, signal });
  document.addEventListener("pointerleave", alSalirDelDocumento, { passive: true, signal });
  document.documentElement.addEventListener("caelestia:workspace", marcarRancio, {
    passive: true,
    signal,
  });

  const tick = (): void => {
    frame = window.requestAnimationFrame(tick);
    if (!stale) return;
    stale = false;
    if (!dentro) return;
    // Fuera de la ventana devuelve null: ahi no hay zona que resolver.
    resolver(document.elementFromPoint(x, y));
  };
  frame = window.requestAnimationFrame(tick);

  // La clase solo se pone tras montar con exito: si este modulo no llega a
  // cargar o revienta antes, el CSS no oculta nada y el cursor del sistema
  // sigue intacto en toda la pagina.
  document.documentElement.classList.add("caelestia-cursor-ready");

  const destroy = (): void => {
    window.cancelAnimationFrame(frame);
    controller.abort();
    document.documentElement.classList.remove("caelestia-cursor-ready");
    cursor.remove();
    delete (window as unknown as { __caeCursor__?: unknown }).__caeCursor__;
  };

  // Sonda de verificacion: la consume scripts/measure-caelestia-cursor.py.
  // No afecta al render mientras nadie la llame.
  Object.defineProperty(window, "__caeCursor__", {
    value: {
      estado: (): Estado => estadoActual,
      diana: (): HTMLElement | null => null,
      mancha: (): number => 0,
      destroy,
    },
    writable: false,
    configurable: true,
  });

  return { destroy };
}
```

- [x] **Step 2: Escribe el CSS**

Al **final** del bloque `:root[data-theme="caelestia"]` de `src/themes/themes.css` (al final del
fichero está bien: el bloque del cursor de Hyprland ya vive ahí). Va al final a propósito: la fase
B5 se está implementando en paralelo sobre el mismo bloque, y así el conflicto de fusión es de
adyacencia y no de solape.

```css
/* =====================================================================
 * Cursor propio de Caelestia — la gota
 *
 * `.caelestia-cursor-ready` la pone el JS SOLO tras montar con exito. Si
 * el modulo no carga, no existe ninguna de estas reglas y el cursor del
 * sistema queda intacto: ni una senal depende del JavaScript.
 *
 * La lista blanca cuelga de la RAIZ y no de `[data-scene]`, al reves que
 * en Vice y Hyprland. Medido: en Caelestia los cinco workspaces son los
 * hijos directos de `main`, y el de Obra (`div#obra.obra-rail`) NO lleva
 * `data-scene`; la barra y el dock cuelgan de `#app`, fuera de `main`.
 * Con la regla colgando de `[data-scene]`, el puntero del sistema seguiria
 * visible encima de las tarjetas de Obra, de las pastillas y del dock --
 * tres de las dianas que este cursor existe para vestir.
 *
 * Sigue siendo lista blanca por el mismo mecanismo de siempre: `cursor`
 * solo se hereda cuando el elemento no declara el suyo.
 * ===================================================================== */

.caelestia-cursor-ready:root[data-theme="caelestia"] {
  cursor: none;
}

/* Texto corrido recupera el I-beam que la herencia le habia quitado:
   ocultarlo borraria la senal de que esto se selecciona y se copia.
   EXCEPTO el que vive dentro de un pulsable -- la leyenda de una tarjeta
   de Obra, el nombre de una pieza de Creditos: ahi manda el pulsable,
   igual que en `resolver()` dentro del modulo. Las dos inversiones se
   mueven juntas o se contradicen sobre el mismo pixel. */
.caelestia-cursor-ready:root[data-theme="caelestia"]
  :is(p, li, dd, dt, figcaption, blockquote):not(button *, a[href] *) {
  cursor: auto;
}

/* El enlace externo abre pestana nueva y la certeza de "esto es un enlace
   real" no se toca. `.gallery-track` es PREVENTIVO: su `grab` es la unica
   pista de que la galeria se arrastra, pero hoy el `projectScene.ts` que
   la contiene esta oculto en Caelestia (B3), asi que esta linea no la
   vigila ningun gate -- y no puede, sin volverse tautologico. */
.caelestia-cursor-ready:root[data-theme="caelestia"]
  :is(a[target="_blank"], .gallery-track) {
  cursor: auto;
}

.cae-cursor {
  position: fixed;
  left: 0;
  top: 0;
  width: 0;
  height: 0;
  z-index: 72;
  pointer-events: none;
}

/* La perla. `--s` tamano, `--al` opacidad, `--brillo` la tension
   superficial. El pigmento es el de la hora: `--cae-primary` gira los 360
   grados de la rueda en 24 horas, asi que el visitante de las 09:00 y el
   de las 21:00 no llevan la misma gota en la mano. Aqui no se calcula
   ningun color. */
.cae-cursor-perla {
  position: absolute;
  left: 0;
  top: 0;
  width: var(--s, 20px);
  height: var(--s, 20px);
  translate: -50% -50%;
  border-radius: 50%;
  background: var(--cae-primary);
  opacity: var(--al, 0.42);
  mix-blend-mode: multiply;
  transition:
    width 0.3s cubic-bezier(0.2, 0, 0, 1),
    height 0.3s cubic-bezier(0.2, 0, 0, 1),
    opacity 0.2s linear,
    border-radius 0.3s cubic-bezier(0.2, 0, 0, 1),
    background 0.2s linear;
}

/* De noche el pigmento no puede multiplicar: sobre superficie oscura
   multiplicar es no hacer nada. Aclara. */
:root[data-cae-esquema="noche"] .cae-cursor-perla {
  mix-blend-mode: screen;
}

/* El brillo de la tension superficial: es lo que separa una gota de un
   disco. Regla propia y no `*`, porque el selector universal NO alcanza a
   los pseudo-elementos. */
.cae-cursor-perla::before {
  content: "";
  position: absolute;
  left: 22%;
  top: 18%;
  width: 30%;
  height: 22%;
  border-radius: 50%;
  background: var(--cae-surface);
  opacity: var(--brillo, 0.55);
  filter: blur(0.5px);
  transition: opacity 0.2s linear;
}

/* El nucleo marca la MANO: es el unico punto que dice donde esta el raton
   exactamente, y por eso no se mueve ni se interpola nunca. */
.cae-cursor-nucleo {
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 3px;
  translate: -50% -50%;
  border-radius: 50%;
  background: var(--cae-on-surface);
  transition: opacity 0.12s linear;
}

.cae-cursor[data-estado="reposo"] .cae-cursor-perla {
  --s: 20px;
  --al: 0.42;
  --brillo: 0.55;
}

.cae-cursor[data-estado="perla"] .cae-cursor-perla {
  --s: 15px;
  --al: 0.95;
  --brillo: 0.95;
  /* Ligeramente asimetrica: una gota tensada no es un circulo. */
  border-radius: 48% 52% 50% 50% / 55% 55% 45% 45%;
}

.cae-cursor[data-estado="apagada"] .cae-cursor-perla,
.cae-cursor[data-estado="apagada"] .cae-cursor-nucleo {
  opacity: 0;
  /* 120ms: el relevo con el cursor del sistema tiene que ser inmediato. Si
     la gota se apaga despacio, durante un cuarto de segundo hay dos
     cursores en pantalla. */
  transition: opacity 0.12s linear;
}

/* De noche la gota parte de mas arriba: sobre superficie oscura una
   opacidad de dia se lee como suciedad, no como pigmento. */
:root[data-cae-esquema="noche"] .cae-cursor[data-estado="reposo"] .cae-cursor-perla {
  --al: 0.55;
  --brillo: 0.35;
}

:root[data-cae-esquema="noche"] .cae-cursor[data-estado="perla"] .cae-cursor-perla {
  --al: 0.9;
  --brillo: 0.6;
}

/* Cinturon y tirantes: si el modulo llegara a montar bajo movimiento
   reducido, no se pinta nada. La puerta real esta en `main.ts`. */
@media (prefers-reduced-motion: reduce) {
  .cae-cursor {
    display: none;
  }
}
```

- [x] **Step 3: Monta el módulo en `main.ts`**

Detrás del bloque que monta el shell de Caelestia (`src/main.ts`, alrededor de la línea 262), añade:

```ts
/*
 * Cursor propio de Caelestia: la gota. Las mismas tres puertas que Vice y
 * Hyprland — el tema, el perfil de motion y que el puntero sea fino con
 * hover real. En tactil no hay hover que disparar ningun estado, asi que el
 * coste correcto ahi es cero, no "cero animacion": la puerta esta ANTES del
 * `import()`, no dentro del modulo.
 *
 * Se monta sin retardo, a diferencia de los otros dos: Caelestia no tiene
 * leader ni encendido que tapen la pantalla al abrir.
 */
let caeCursorHandle: { destroy: () => void } | null = null;
if (
  theme.id === "caelestia" &&
  !prefersReducedMotion &&
  window.matchMedia("(hover: hover) and (pointer: fine)").matches
) {
  void import("./components/caelestiaCursor").then(({ mountCaelestiaCursor }) => {
    caeCursorHandle = mountCaelestiaCursor(app);
  });
}
```

Y en el oyente de `pagehide`, junto a los demás:

```ts
    caeCursorHandle?.destroy();
```

- [x] **Step 4: Añade el gate 4 (sin inercia) al arnés**

Dentro de `main()`, después de `gate_senales(...)`:

```python
def gate_sin_inercia(pagina, base: str) -> None:
    """Gate 4 -- la posicion NO se suaviza.

    Un cursor con inercia miente sobre donde esta el raton, y en Creditos hay
    23 dianas contiguas donde eso se lee como retraso. La asercion es delta
    CERO tras UN fotograma, no "menor que": un umbral flojo deja pasar
    exactamente el `lerp` que viene a prohibir.
    """
    print("[4] sin inercia en la posicion")
    abre(pagina, base, "creditos")
    pagina.mouse.move(400, 400)
    pagina.wait_for_timeout(300)
    pagina.mouse.move(900, 500)
    medida = pagina.evaluate(
        """() => new Promise(res => requestAnimationFrame(() => {
             const m = new DOMMatrixReadOnly(getComputedStyle(document.querySelector('.cae-cursor')).transform);
             res([m.e, m.f]);
           }))"""
    )
    check(
        abs(medida[0] - 900) < 0.5 and abs(medida[1] - 500) < 0.5,
        f"[4] la gota esta exactamente donde el raton tras un fotograma {medida}",
    )
```

- [x] **Step 5: Build, lint y corre el arnés — gates 1, 2 y 4 en VERDE**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
kill $(ss -ltnp | grep 4173 | grep -oP 'pid=\K[0-9]+')   # por PID, nunca pkill -f
nohup npx vite preview --port 4173 --strictPort > /tmp/preview-cursor.log 2>&1 &
sleep 4 && python3 scripts/measure-caelestia-cursor.py --base http://localhost:4173
```

Esperado: todo OK salvo el check del gate 2 sobre el nombre de una pieza, que espera `derrame` y
todavía da `perla` — lo cierra el Task 3. Anótalo y sigue.

- [x] **Step 6: Mira la pantalla, que ningún número lo dice**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded', timeout=45000)
    pg.wait_for_timeout(6000)
    pg.eval_on_selector_all('.cae-ws', "(bs)=>bs[2].click()"); pg.wait_for_timeout(1500)
    pg.hover('.cae-obra-card', position={'x':200,'y':70}); pg.wait_for_timeout(600)
    pg.screenshot(path='/tmp/cursor-t2-perla.png')
    b.close()
PY
```

Ábrelo. La perla tiene que verse **sobre** la tarjeta, del color del pigmento de esa hora, no
debajo ni recortada. Si el `mix-blend-mode` se aplica contra el contexto equivocado, aquí se ve y
en ningún número.

- [x] **Step 7: Sabotea el gate 2 y míralo en rojo**

Quita la segunda vuelta de `resolver()` (deja solo `zona.matches(PRESSABLE) ? zona : null`),
reconstruye y corre el arnés: los dos checks de la leyenda de la tarjeta tienen que dar **FAIL**.
Restaura, reconstruye, verde otra vez.

- [x] **Step 8: Commit**

```bash
git add src/components/caelestiaCursor.ts src/themes/themes.css src/main.ts scripts/measure-caelestia-cursor.py
git commit -m "feat(cursor): la gota de Caelestia — perla, resolucion de zona y lista blanca"
```

---

## Task 3: El derrame y los dos momentos

**Files:**
- Modify: `src/components/caelestiaCursor.ts`
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-caelestia-cursor.py` (gate 3)

**Interfaces:**
- Consumes: del Task 2 — `resolver()`, `setEstado()`, `x`, `y`, `diana`, `host`, `signal`.
- Produces: `.cae-cursor-mancha` y `.cae-cursor-gota` en el DOM; la sonda pasa a devolver
  `diana(): HTMLElement | null` (la diana **mojada**, no la que está bajo el puntero) y
  `mancha(): number` (avance pintado, 0 a 1).

- [x] **Step 1: Añade la mancha al módulo**

Después de crear `cursor` y antes de `host.append(...)`:

```ts
  /*
   * El derrame es un elemento APARTE, no un `background-image` en la diana
   * como hace Hyprland. Aquel necesita quedar debajo del texto; este es
   * pigmento sobre papel y va encima de todo. La ventaja no es menor: este
   * modulo NO toca el DOM de ninguna diana, asi que no hay estado previo que
   * guardar ni que restaurar, que es la clase de fallo que a Hyprland le
   * costo una tarea entera.
   */
  const mancha = document.createElement("div");
  mancha.className = "cae-cursor-mancha";
  mancha.setAttribute("aria-hidden", "true");
  const gota = document.createElement("i");
  gota.className = "cae-cursor-gota";
  mancha.append(gota);
```

Y cambia el append a `host.append(cursor, mancha);` — **en ese orden**. La mancha va **después**
en el DOM porque el CSS la alcanza con el combinador de hermano posterior (`.cae-cursor[...] ~
.cae-cursor-mancha`), que solo mira hacia adelante. Quién se pinta encima lo decide el `z-index`
(65 la mancha, 72 la gota), no el orden, así que la lectura visual no depende de esto.

Declara el estado nuevo junto a los demás:

```ts
  let mojada: HTMLElement | null = null;
  let objetivo = 0;
  let cajaAncho = 0;
  let cajaAlto = 0;
  let pulsado = false;
```

Y las funciones, antes de `resolver()`:

```ts
  // Radio en px del circulo base de `.cae-cursor-gota` (20px de lado).
  const RADIO_GOTA = 10;

  /** Escala a la que la gota cubre la caja entera desde donde cayo. */
  const alcanceDe = (caja: DOMRect): number => {
    const dx = Math.max(x - caja.left, caja.right - x);
    const dy = Math.max(y - caja.top, caja.bottom - y);
    return Math.hypot(dx, dy) / RADIO_GOTA + 0.2;
  };

  /** Coloca la caja de la mancha sobre la diana mojada. */
  const colocarMancha = (caja: DOMRect): void => {
    mancha.style.left = `${caja.left}px`;
    mancha.style.top = `${caja.top}px`;
    mancha.style.width = `${caja.width}px`;
    mancha.style.height = `${caja.height}px`;
  };

  const mojar = (destino: HTMLElement): void => {
    mojada = destino;
    const caja = destino.getBoundingClientRect();
    colocarMancha(caja);
    cajaAncho = caja.width;
    cajaAlto = caja.height;
    // El radio se lee UNA vez por diana, no por fotograma: `getComputedStyle`
    // es caro y el radio de una diana no cambia mientras la senalas.
    mancha.style.borderRadius = getComputedStyle(destino).borderRadius;
    // El centro del derrame es donde cayo la gota, en coordenadas de la caja,
    // y se queda ahi: una mancha no persigue al raton.
    gota.style.left = `${x - caja.left}px`;
    gota.style.top = `${y - caja.top}px`;
    /*
     * Un fotograma a escala 0 antes de crecer. Sin esto el navegador no tiene
     * dos valores que interpolar -- si la gota venia de estar seca ya estaba
     * a 0, pero si venia de otra diana venia de su escala anterior, y el
     * derrame arrancaria a medio camino.
     */
    gota.style.transform = "translate(-50%, -50%) scale(0)";
    void gota.offsetWidth;
    objetivo = alcanceDe(caja);
    gota.style.transform = `translate(-50%, -50%) scale(${objetivo.toFixed(3)})`;
  };

  const secar = (): void => {
    if (!mojada) return;
    mojada = null;
    objetivo = 0;
    gota.style.transform = "translate(-50%, -50%) scale(0)";
  };
```

Reescribe el final de `resolver()` para repartir por familia:

```ts
    if (pulsable !== diana) {
      diana = pulsable;
      /*
       * La familia se decide UNA vez por diana, no por fotograma. Los dos
       * momentos del mismo gesto: la que ya elige al rozarla se moja al
       * entrar, la de clic espera al clic.
       */
      if (diana.matches(HOVER_SELECT) || pulsado) mojar(diana);
      else secar();
    }
    setEstado(mojada ? "derrame" : "perla");
```

Añade los dos manejadores y sus oyentes:

```ts
  const alPulsar = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
    pulsado = true;
    if (diana && !mojada) mojar(diana);
    if (diana) setEstado("derrame");
  };

  const alSoltar = (evento: PointerEvent): void => {
    if (evento.pointerType !== "mouse") return;
    pulsado = false;
    if (!diana) return;
    // La familia de roce se queda mojada: ahi el derrame no lo trajo el clic.
    if (!diana.matches(HOVER_SELECT)) secar();
    setEstado(mojada ? "derrame" : "perla");
  };

  window.addEventListener("pointerdown", alPulsar, { passive: true, signal });
  window.addEventListener("pointerup", alSoltar, { passive: true, signal });
```

En `resolver()`, en las dos ramas que se quedan sin diana, seca antes de salir: añade `secar();`
justo antes de cada `setEstado(...)` de esas dos ramas. Igual en `alSalirDelDocumento()`.

Extiende `tick()` para que la mancha siga a su diana:

```ts
  const tick = (): void => {
    frame = window.requestAnimationFrame(tick);
    if (stale) {
      stale = false;
      if (dentro) resolver(document.elementFromPoint(x, y));
    }
    if (!mojada) return;
    /*
     * defensive: el carril de workspaces puede llevarse la diana del arbol
     * mientras esta mojada. Sin esto la mancha se queda pintada sobre una
     * caja que ya no existe.
     */
    if (!mojada.isConnected) {
      secar();
      diana = null;
      setEstado(dentro ? "reposo" : "apagada");
      return;
    }
    const caja = mojada.getBoundingClientRect();
    colocarMancha(caja);
    /*
     * La escala objetivo solo se recalcula si la caja CAMBIA DE TAMANO -- la
     * tarjeta de Obra se endereza al rozarla y crece unos pixeles. Reescribir
     * la escala cada fotograma reiniciaria la transicion sesenta veces por
     * segundo y el derrame no llegaria a crecer nunca.
     */
    if (Math.abs(caja.width - cajaAncho) > 1 || Math.abs(caja.height - cajaAlto) > 1) {
      cajaAncho = caja.width;
      cajaAlto = caja.height;
      objetivo = alcanceDe(caja);
      gota.style.transform = `translate(-50%, -50%) scale(${objetivo.toFixed(3)})`;
    }
  };
```

Actualiza la sonda y `destroy()`:

```ts
      diana: (): HTMLElement | null => mojada,
      /*
       * El avance PINTADO, no el objetivo que este modulo acaba de escribir:
       * un gate que leyera el objetivo mediria la intencion y no el
       * resultado. Ver el contrato de la cabecera.
       */
      mancha: (): number => {
        if (!mojada || objetivo <= 0) return 0;
        const m = new DOMMatrixReadOnly(getComputedStyle(gota).transform);
        return Math.min(m.a / objetivo, 1);
      },
```

```ts
    mancha.remove();   // en destroy(), junto a cursor.remove()
```

- [x] **Step 2: Añade el CSS de la mancha**

```css
/* El derrame. Va ENCIMA de la diana, texto incluido: es pigmento sobre
   papel, no luz por detras. `z-index: 65` lo pone sobre la barra (60) y
   sobre el carril, y por debajo de la propia gota (72).

   El modulo NUNCA escribe `display` aqui: el arnes lo apaga con
   `display: none` para su A/B y necesita que el fotograma siguiente no se
   lo pise. Ver el contrato en la cabecera del modulo. */
.cae-cursor-mancha {
  position: fixed;
  left: 0;
  top: 0;
  width: 0;
  height: 0;
  z-index: 65;
  overflow: hidden;
  pointer-events: none;
  mix-blend-mode: multiply;
}

:root[data-cae-esquema="noche"] .cae-cursor-mancha {
  mix-blend-mode: screen;
}

/* El circulo que crece desde donde cayo la gota hasta llenar la caja. El
   recorte a la forma de la diana lo hace el `overflow: hidden` del padre
   con el `border-radius` que el modulo le copia: asi el liquido corre
   hasta los cantos de lo que ha mojado, sea una tarjeta de 3px de radio o
   una pastilla de 999px. */
.cae-cursor-gota {
  position: absolute;
  left: 0;
  top: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--cae-primary);
  opacity: 0.22;
  transform: translate(-50%, -50%) scale(0);
  transform-origin: 50% 50%;
  transition: transform 0.42s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-cae-esquema="noche"] .cae-cursor-gota {
  opacity: 0.3;
}

/* Recogerse tras el clic (180ms) va mas rapido que secarse al salir de la
   diana (300ms), y las dos mas que llenar (420ms): llenar es el gesto,
   recoger es su final, y secarse al marcharse no es ni una cosa ni la otra.
   Los tres numeros son los del spec. */
.cae-cursor[data-estado="perla"] ~ .cae-cursor-mancha .cae-cursor-gota {
  transition-duration: 0.18s;
}

.cae-cursor[data-estado="reposo"] ~ .cae-cursor-mancha .cae-cursor-gota,
.cae-cursor[data-estado="apagada"] ~ .cae-cursor-mancha .cae-cursor-gota {
  transition-duration: 0.3s;
}

/* La caja mojada de una pieza de Creditos. Sin esto el derrame es un
   rectangulo de esquina viva alrededor de una figura redonda. 10px es el
   radio que la pieza YA declara para su anillo de foco
   (`themes.css`, `.cae-cred-pieza:focus-visible`); se escribe aqui, en el
   bloque del cursor y colgando de la clase `ready`, para no tocar B4:
   sin el cursor esta regla no existe, y la pieza no tiene fondo ni borde
   propios, asi que el radio no cambia nada de lo que se ve. */
.caelestia-cursor-ready:root[data-theme="caelestia"] .cae-cred-pieza {
  border-radius: 10px;
}

/* La perla derramada pasa a TINTA, no pigmento: sobre la pieza elegida el
   pigmento es exactamente el color de la pieza (`--cae-primary` de fondo)
   y la gota desaparece. Medido en el prototipo. */
.cae-cursor[data-estado="derrame"] .cae-cursor-perla {
  --s: 30px;
  --al: 0.26;
  --brillo: 0;
  background: var(--cae-on-surface);
  mix-blend-mode: normal;
}

:root[data-cae-esquema="noche"] .cae-cursor[data-estado="derrame"] .cae-cursor-perla {
  --al: 0.3;
}

@media (prefers-reduced-motion: reduce) {
  .cae-cursor-mancha {
    display: none;
  }
}
```

> **El combinador `~` solo mira hacia adelante.** Las dos reglas de arriba exigen que
> `.cae-cursor-mancha` vaya **después** de `.cae-cursor` en el DOM, que es justo lo que da
> `host.append(cursor, mancha)`. Si alguna vez se invierte el append, esas dos reglas dejan de casar
> **en silencio**: el derrame seguiría funcionando y solo se recogería más lento. Compruébalo con el
> muestreo del Task 5, Step 3, que sí lo vería.

- [x] **Step 3: Añade el gate 3 al arnés**

```python
def gate_dos_momentos(pagina, base: str) -> None:
    """Gate 3 -- los dos momentos del mismo gesto.

    Es la tesis del dispositivo: la diana que YA elige al rozarla se moja al
    entrar, la de clic espera al clic. Si las dos se comportan igual, el
    cursor tiene un solo estado y el spec entero sobra.

    `mancha()` devuelve el avance PINTADO, no el objetivo escrito: sin eso la
    asercion mediria la intencion del modulo contra si misma.
    """
    print("[3] los dos momentos")

    # Familia de roce: se moja SIN ningun clic.
    abre(pagina, base, "creditos")
    pagina.hover(".cae-cred-pieza:nth-child(3)")
    pagina.wait_for_timeout(700)
    check(estado(pagina) == "derrame", "[3] la pieza de Creditos se moja al ENTRAR, sin clic")
    avance = pagina.evaluate("() => window.__caeCursor__.mancha()")
    check(avance > 0.9, f"[3] el derrame llega a llenar la pieza ({avance:.2f})")
    check(
        pagina.evaluate("() => window.__caeCursor__.diana()?.className || ''").startswith(
            "cae-cred-pieza"
        ),
        "[3] la diana mojada es la pieza",
    )

    # Familia de clic: perla al entrar, derrame solo al pulsar.
    abre(pagina, base, "obra")
    pagina.hover(".cae-obra-card", position={"x": 200, "y": 70})
    pagina.wait_for_timeout(700)
    check(estado(pagina) == "perla", "[3] la tarjeta de Obra NO se moja al entrar")
    check(
        pagina.evaluate("() => window.__caeCursor__.mancha()") == 0,
        "[3] sin clic la tarjeta esta seca",
    )
    pagina.mouse.down()
    pagina.wait_for_timeout(700)
    check(estado(pagina) == "derrame", "[3] la tarjeta se moja al PULSAR")
    avance = pagina.evaluate("() => window.__caeCursor__.mancha()")
    check(avance > 0.9, f"[3] el derrame llega a llenar la tarjeta ({avance:.2f})")
    pagina.mouse.up()
    pagina.wait_for_timeout(500)
    check(estado(pagina) == "perla", "[3] al soltar, la tarjeta se seca y vuelve la perla")
```

- [x] **Step 4: Build, arnés y captura**

Los tres gates (2, 3, 4) en verde, incluido el check del nombre de la pieza que quedó pendiente en
el Task 2. Y mira una captura del derrame lleno sobre la tarjeta y sobre la pieza, de día y de
noche (usa `window.__CAE_SET_MINUTOS__(180)` para la noche).

- [x] **Step 5: Sabotea y mira el rojo**

Cambia `HOVER_SELECT` por `"button[data-no-existe]"`, reconstruye y corre: los tres checks de la
pieza tienen que dar **FAIL** y los de la tarjeta seguir verdes. Restaura.

- [x] **Step 6: Commit**

```bash
git add src/components/caelestiaCursor.ts src/themes/themes.css scripts/measure-caelestia-cursor.py
git commit -m "feat(cursor): el derrame — la gota moja la diana en sus dos momentos"
```

---

## Task 4: El cerco al soltar

**Files:**
- Modify: `src/components/caelestiaCursor.ts`
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-caelestia-cursor.py` (gate 3-bis)

**Interfaces:**
- Consumes: `alSoltar()`, `host`, `x`, `y` del Task 3.
- Produces: la clase `.cae-cursor-cerco` y el conjunto `cercos: Set<HTMLElement>`, que el `destroy()`
  del Task 8 vacía.

- [x] **Step 1: Añade el cerco al módulo**

```ts
  /*
   * Los cercos vivos. Se guardan porque `destroy()` tiene que llevarselos:
   * un cerco lanzado en el ultimo clic antes de navegar sobrevive a su
   * modulo si nadie lo recoge, y eso es DOM huerfano.
   */
  const cercos = new Set<HTMLElement>();

  /*
   * El anillo que deja una gota al secarse sobre papel. Es la constancia de
   * que el clic ocurrio, sin escribir un solo caracter -- la regla dura
   * heredada de Hyprland: un cursor no puede tener manual.
   *
   * Solo en el clic REAL, nunca en el roce: la gota deja huella donde ha
   * actuado, nunca por donde pasa. (Por lo mismo no hay estela.)
   */
  const dejarCerco = (): void => {
    const anillo = document.createElement("i");
    anillo.className = "cae-cursor-cerco";
    anillo.setAttribute("aria-hidden", "true");
    anillo.style.left = `${x}px`;
    anillo.style.top = `${y}px`;
    anillo.addEventListener(
      "animationend",
      () => {
        cercos.delete(anillo);
        anillo.remove();
      },
      { once: true },
    );
    cercos.add(anillo);
    host.append(anillo);
  };
```

En `alSoltar()`, dentro de la rama que no es familia de roce:

```ts
    if (!diana.matches(HOVER_SELECT)) {
      secar();
      dejarCerco();
    }
```

- [x] **Step 2: CSS del cerco**

```css
/* El cerco: el anillo que deja una gota seca. Animacion CSS y no
   transicion, porque es un disparo de una sola vez y se limpia solo en
   `animationend`. */
@keyframes cae-cursor-cerco {
  from {
    transform: translate(-50%, -50%) scale(0.6);
    opacity: 0.9;
  }
  to {
    transform: translate(-50%, -50%) scale(2.1);
    opacity: 0;
  }
}

.cae-cursor-cerco {
  position: fixed;
  left: 0;
  top: 0;
  width: 18px;
  height: 18px;
  box-sizing: border-box;
  border: 1.4px solid var(--cae-primary);
  border-radius: 50%;
  z-index: 71;
  pointer-events: none;
  animation: cae-cursor-cerco 0.8s cubic-bezier(0.2, 0, 0, 1) forwards;
}

@media (prefers-reduced-motion: reduce) {
  .cae-cursor-cerco {
    display: none;
  }
}
```

- [x] **Step 3: Gate 3-bis**

Añade al final de `gate_dos_momentos`:

```python
    # El cerco: solo en el clic real, y se limpia solo.
    check(
        pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length") >= 1,
        "[3] el clic deja cerco",
    )
    pagina.wait_for_timeout(1400)
    check(
        pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length") == 0,
        "[3] el cerco se limpia solo antes de 1,4 s",
    )

    # El roce NO deja cerco: la gota deja huella donde actua, no por donde pasa.
    abre(pagina, base, "creditos")
    pagina.hover(".cae-cred-pieza:nth-child(2)")
    pagina.wait_for_timeout(400)
    pagina.hover(".cae-cred-pieza:nth-child(5)")
    pagina.wait_for_timeout(400)
    check(
        pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length") == 0,
        "[3] barrer piezas al roce no deja ningun cerco",
    )
```

- [x] **Step 4: Build, arnés verde, y sabotaje**

Sabotaje: llama a `dejarCerco()` también en la rama de roce. El último check tiene que dar **FAIL**.
Restaura.

- [x] **Step 5: Commit**

```bash
git add src/components/caelestiaCursor.ts src/themes/themes.css scripts/measure-caelestia-cursor.py
git commit -m "feat(cursor): el cerco que deja la gota al soltar el clic"
```

---

## Task 5: La lente, la sombra, el rebote y el material de noche

Los cuatro añadidos que quedan del prototipo aprobado. Son CSS puro; ninguno toca el módulo.
**La referencia es la maqueta**, `docs/superpowers/specs/2026-09-04-caelestia-cursor-maqueta.html`:
ábrela al lado y compara.

**Files:**
- Modify: `src/themes/themes.css`

**Interfaces:**
- Consumes: `.cae-cursor-perla` y sus estados del Task 2.
- Produces: nada nuevo para tareas posteriores.

- [x] **Step 1: Escribe las cuatro reglas**

```css
/* La lente. Es lo que separa una gota de un disco de color: lo que hay
   debajo se ve a traves de ella. De DIA satura y contrasta; de NOCHE eso
   no hace nada (sobre superficie oscura no hay nada que saturar), asi que
   aclara. Es la misma pieza con otra luz, no otra pieza. */
.cae-cursor-perla {
  backdrop-filter: saturate(1.7) contrast(1.06) blur(0.7px);
  -webkit-backdrop-filter: saturate(1.7) contrast(1.06) blur(0.7px);
}

:root[data-cae-esquema="noche"] .cae-cursor-perla {
  backdrop-filter: brightness(1.35) saturate(1.25) blur(0.7px);
  -webkit-backdrop-filter: brightness(1.35) saturate(1.25) blur(0.7px);
}

/* Derramada no refracta: ya no es una gota sobre la superficie, es una
   mancha extendida. */
.cae-cursor[data-estado="derrame"] .cae-cursor-perla {
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

/* La sombra dice que la gota esta SOBRE la superficie, no pintada en ella.
   De noche una sombra no se ve: el papel de "esto tiene volumen" lo hace
   un canto encendido y un halo. */
.cae-cursor-perla {
  box-shadow:
    0 1px 2px color-mix(in oklch, var(--cae-on-surface) 32%, transparent),
    inset 0 -1px 1px color-mix(in oklch, var(--cae-on-surface) 12%, transparent);
}

:root[data-cae-esquema="noche"] .cae-cursor-perla {
  box-shadow:
    inset 0 0 0 1px color-mix(in oklch, var(--cae-primary) 60%, white),
    inset 0 -2px 3px color-mix(in oklch, var(--cae-primary) 40%, transparent),
    0 0 6px color-mix(in oklch, var(--cae-primary) 45%, transparent);
}

.cae-cursor[data-estado="derrame"] .cae-cursor-perla,
:root[data-cae-esquema="noche"] .cae-cursor[data-estado="derrame"] .cae-cursor-perla {
  box-shadow: none;
}

/* De noche el brillo de tension se recoge y sube: con el canto encendido,
   un brillo grande convierte la gota en una pastilla. */
:root[data-cae-esquema="noche"] .cae-cursor-perla::before {
  left: 26%;
  top: 14%;
  width: 26%;
  height: 18%;
}

/* El rebote al posarse: la curva `expressive` de Material 3 hecha fisica.
   UN ciclo y corto. Si se repite, es gelatina. */
@keyframes cae-cursor-perla-posa {
  0% {
    scale: 1.35 0.8;
  }
  45% {
    scale: 0.9 1.1;
  }
  100% {
    scale: 1 1;
  }
}

.cae-cursor[data-estado="perla"] .cae-cursor-perla {
  animation: cae-cursor-perla-posa 0.42s cubic-bezier(0.2, 0, 0, 1) 1;
}

/* El selector universal de la guardia de movimiento reducido NO alcanza a
   los pseudo-elementos ni a las animaciones declaradas aparte: cada una
   necesita su regla. (Trampa pagada en B2 con `.ficha-k::before`.) */
@media (prefers-reduced-motion: reduce) {
  .cae-cursor-perla,
  .cae-cursor-perla::before,
  .cae-cursor-gota {
    animation: none;
    transition: none;
  }
}
```

- [x] **Step 2: Mira las cuatro capturas, que es el único juez aquí**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900}, device_scale_factor=2)
    pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded', timeout=45000)
    pg.wait_for_timeout(6000)
    pg.eval_on_selector_all('.cae-ws', "(bs)=>bs[2].click()"); pg.wait_for_timeout(1500)
    for minutos, tag in ((540, 'dia'), (180, 'noche')):
        pg.evaluate(f"window.__CAE_SET_MINUTOS__({minutos})"); pg.wait_for_timeout(400)
        pg.hover('.cae-obra-card', position={'x':200,'y':70}); pg.wait_for_timeout(700)
        caja = pg.locator('.cae-obra-card').bounding_box()
        pg.screenshot(path=f'/tmp/cursor-t5-{tag}.png', clip=caja)
    b.close()
PY
```

Compara con `2026-09-04-caelestia-cursor-perla-dia.png` y `…-perla-noche.png` del spec. De día tiene
que leerse como gota oscura con brillo; de noche, como gota encendida con el canto iluminado. **Si
de noche parece un disco plano, la lente o el canto no están llegando** — revísalo antes de seguir.

- [x] **Step 3: Comprueba que el rebote no se repite**

Con la velocidad del ojo no basta. Muestrea la escala desde dentro de la página:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded', timeout=45000)
    pg.wait_for_timeout(6000)
    pg.eval_on_selector_all('.cae-ws', "(bs)=>bs[2].click()"); pg.wait_for_timeout(1500)
    pg.hover('.cae-obra-card', position={'x':200,'y':70})
    muestras = pg.evaluate("""() => new Promise(res => {
      const el = document.querySelector('.cae-cursor-perla'); const out = [];
      const t0 = performance.now();
      const tomar = () => { const m = new DOMMatrixReadOnly(getComputedStyle(el).transform);
        out.push([Math.round(performance.now() - t0), +m.a.toFixed(3)]);
        if (performance.now() - t0 < 1500) requestAnimationFrame(tomar); else res(out); };
      tomar();
    })""")
    print(muestras[:6], '...', muestras[-3:])
    b.close()
PY
```

Esperado: la escala sale de ~1,35, cruza por debajo de 1 y **se asienta en 1** antes de los 500 ms,
sin volver a moverse. Si oscila después, el `animation` se está reiniciando cada fotograma.

- [x] **Step 4: Mide lo que cuesta la lente (pregunta abierta 3 del spec)**

`backdrop-filter` en un elemento que se mueve a 60 fps sobre un lienzo WebGL puede salir caro, y la
maqueta no lo dice: la maqueta no lleva shader detrás. Mide el reparto de fotogramas moviendo el
ratón en diagonal, con la lente y sin ella:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright

MEDIDA = '''() => new Promise(res => {
  const t = []; let previo = performance.now(); const t0 = previo;
  const paso = () => { const ahora = performance.now(); t.push(ahora - previo); previo = ahora;
    if (ahora - t0 < 3000) requestAnimationFrame(paso);
    else { t.sort((a,b)=>a-b); res({mediana: +t[t.length>>1].toFixed(2),
      p95: +t[Math.floor(t.length*0.95)].toFixed(2), n: t.length}); } };
  requestAnimationFrame(paso);
})'''

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded', timeout=45000)
    pg.wait_for_timeout(6000)
    pg.eval_on_selector_all('.cae-ws', "(bs)=>bs[2].click()"); pg.wait_for_timeout(1500)
    for etiqueta, css in (('con lente', ''), ('sin lente', 'backdrop-filter:none')):
        pg.eval_on_selector('.cae-cursor-perla', "(el, c) => el.style.cssText = c", css)
        for i in range(30):
            pg.mouse.move(300 + i*20, 300 + i*8)
            pg.wait_for_timeout(16)
        print(etiqueta, pg.evaluate(MEDIDA))
    b.close()
PY
```

Con swiftshader los números son lentos en absoluto y solo valen **comparados entre sí**. Criterio:
si la mediana con lente empeora más de un 25 % frente a sin lente, aplica la salida que el spec ya
dejó escrita — la lente se queda solo en `perla` (quieta sobre una diana) y se apaga en `reposo`:

```css
.cae-cursor[data-estado="reposo"] .cae-cursor-perla {
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}
```

Anota los dos números en el `Registro de implementación` del spec, decidas lo que decidas. Un
«no costaba nada» sin medida es exactamente lo que este proyecto ya no acepta.

- [x] **Step 5: Build, lint, arnés verde, commit**

```bash
git add src/themes/themes.css
git commit -m "feat(cursor): lente, sombra, rebote y el material de noche de la gota"
```

---

## Task 6: El estado rancio — cambiar de workspace con el ratón quieto

**Files:**
- Modify: `scripts/measure-caelestia-cursor.py` (gate 5)
- Modify: `src/components/caelestiaCursor.ts` solo si el gate lo pide

El código que lo resuelve (`marcarRancio` + la rama `stale` de `tick()`) ya está desde el Task 2.
Esta tarea es el gate que demuestra que sirve — y es la que caza la regresión concreta que B4
documentó una fase antes.

**Interfaces:**
- Consumes: la sonda `estado()` y `diana()`.
- Produces: nada nuevo.

- [x] **Step 1: Escribe el gate 5**

```python
def gate_rancio(pagina, base: str) -> None:
    """Gate 5 -- la diana que se va con el raton quieto.

    Al cambiar de workspace, el carril se lleva la diana y deja otra escena
    debajo del puntero, y eso NO emite ningun evento de puntero. Sin la
    escucha de `caelestia:workspace` la gota se queda mojada sobre una caja
    que ya no esta ahi -- una mancha flotando sobre la escena siguiente.

    El raton NO se mueve en toda la prueba: si se moviera, `pointerover` lo
    arreglaria solo y el gate no mediria nada. Por eso el workspace se cambia
    por TECLADO.
    """
    print("[5] estado rancio tras cambiar de workspace")
    abre(pagina, base, "creditos")
    pagina.hover(".cae-cred-pieza:nth-child(3)")
    pagina.wait_for_timeout(700)
    check(estado(pagina) == "derrame", "[5] partida: la pieza esta mojada")

    # Cambio de workspace SIN mover el raton: se pulsa la pastilla con el
    # teclado, desde el foco.
    pagina.evaluate("() => document.querySelectorAll('.cae-ws')[4].focus()")
    pagina.keyboard.press("Enter")
    pagina.wait_for_timeout(1500)

    check(
        pagina.evaluate("() => window.__caeCursor__.diana() === null"),
        "[5] tras cambiar de workspace la diana mojada se suelta",
    )
    check(estado(pagina) != "derrame", f"[5] la gota deja de estar derramada ({estado(pagina)})")
    check(
        pagina.evaluate("() => window.__caeCursor__.mancha()") == 0,
        "[5] la mancha queda seca",
    )
```

- [x] **Step 2: Córrelo. Si falla, arréglalo en el módulo**

Es posible que falle aunque el código esté: al enfocar la pastilla con teclado, el puntero sigue
sobre las coordenadas de la pieza y `document.elementFromPoint` puede devolver la propia pieza si
el carril todavía no ha terminado de moverse (520 ms de transición). Si es eso, **no relajes el
gate**: sube la espera a 1500 ms como está escrito, y comprueba que `mojada.isConnected` y la
resolución por punto hacen su trabajo. Si de verdad falta código, lo que falta es marcar rancio
también cuando el carril **termina** de moverse, no solo cuando empieza: añade

```ts
  document.documentElement.addEventListener("caelestia:workspace", () => {
    marcarRancio();
    // El carril tarda 520ms en asentar (curva `emphasized` de MD3): sin esta
    // segunda pasada, la resolucion ocurre mientras las cajas todavia viajan
    // y devuelve la diana que se esta yendo.
    window.setTimeout(marcarRancio, 600);
  }, { passive: true, signal });
```

y sustituye la escucha anterior por esta.

- [x] **Step 3: Sabotea y mira el rojo**

Quita la escucha de `caelestia:workspace` entera, reconstruye, corre: los tres checks del gate 5
tienen que dar **FAIL**. Restaura.

- [x] **Step 4: Commit**

```bash
git add scripts/measure-caelestia-cursor.py src/components/caelestiaCursor.ts
git commit -m "test(cursor): gate del estado rancio al cambiar de workspace"
```

---

## Task 7: El barrido de 24 horas — contraste bajo el derrame, y que se note

El gate que decide si el mecanismo elegido aguanta. **Es el que puede mandar a rehacer el
derrame**: si no aguanta AA, la mancha pasa a pintarse debajo del texto, como en Hyprland (pregunta
abierta 1 del spec).

**Files:**
- Modify: `scripts/measure-caelestia-cursor.py` (gate 6)
- Modify: `docs/superpowers/specs/2026-09-04-caelestia-cursor-design.md` (anotar el umbral medido)

**Interfaces:**
- Consumes: la sonda, y `window.__CAE_SET_MINUTOS__(minutos)` que ya expone `caelestia.color.ts`.
- Produces: `_contraste_glifo(pagina, caja) -> float` y `_media_canal(png_a, png_b) -> float`.

- [x] **Step 1: Escribe las dos utilidades de medida**

El contraste **no** se puede leer de `getComputedStyle`: la mancha va encima con `mix-blend-mode`,
así que el color pintado del texto y el del fondo no son los declarados. Hay que leer píxeles.

```python
import io
import math

from PIL import Image


def _lum(px: tuple[int, int, int]) -> float:
    f = []
    for v in px:
        v /= 255
        f.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2]


def _ratio(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = _lum(a) + 0.05, _lum(b) + 0.05
    return max(la, lb) / min(la, lb)


def _contraste_glifo(pagina, selector: str) -> float:
    """Contraste real del texto de `selector` contra su fondo, PIXEL A PIXEL.

    Dos capturas del mismo recorte: una normal y otra con la tinta apagada
    (`color: transparent`). Los pixeles que cambian entre las dos son los
    glifos; el mismo pixel en la segunda captura es su fondo exacto.

    Por que asi y no con `getComputedStyle`: el derrame va ENCIMA con
    `mix-blend-mode`, asi que ni el texto ni el fondo se pintan del color que
    declaran. Un numero sacado de los estilos seria de otra pagina.

    Por que el percentil 90 y no el minimo: el antialias deja un halo de
    pixeles a medio camino entre tinta y fondo, y su contraste es siempre
    peor que el del trazo. El minimo mediria el borde de la letra; el
    percentil 90 mide el NUCLEO SOLIDO, que es lo que se lee.
    """
    caja = pagina.locator(selector).first.bounding_box()
    recorte = {k: caja[k] for k in ("x", "y", "width", "height")}

    con = Image.open(io.BytesIO(pagina.screenshot(clip=recorte))).convert("RGB")
    previo = pagina.eval_on_selector(
        selector,
        "el => { const p = el.style.color;"
        " el.style.setProperty('color', 'transparent', 'important');"
        " el.querySelectorAll('*').forEach(d => d.style.setProperty('color','transparent','important'));"
        " return p; }",
    )
    sin = Image.open(io.BytesIO(pagina.screenshot(clip=recorte))).convert("RGB")
    pagina.eval_on_selector(
        selector,
        "(el, prev) => { if (prev) el.style.color = prev; else el.style.removeProperty('color');"
        " el.querySelectorAll('*').forEach(d => d.style.removeProperty('color')); }",
        previo,
    )

    pares = [
        (a, b)
        for a, b in zip(con.getdata(), sin.getdata())
        if math.dist(a, b) > 12  # pixel con tinta encima
    ]
    if not pares:
        return 0.0  # no hay glifo que medir: lo trata el llamador
    ratios = sorted(_ratio(a, b) for a, b in pares)
    return ratios[int(len(ratios) * 0.9)]


def _delta_medio(pagina, selector: str) -> float:
    """Diferencia media de canal entre la diana CON derrame y SIN el.

    Es la mitad que falta del gate: un derrame que no baje de AA porque no
    se ve no es un derrame. El arnes apaga la mancha con `display: none`,
    y puede hacerlo porque el modulo nunca escribe esa propiedad (contrato
    de la cabecera del modulo).

    La diana esta sobre un panel OPACO (la ventana o la propia tarjeta), asi
    que el shader del fondo no entra en el recorte y las dos capturas son
    comparables. Contra el fondo generativo no lo serian: se mueve solo.
    """
    caja = pagina.locator(selector).first.bounding_box()
    recorte = {k: caja[k] for k in ("x", "y", "width", "height")}
    con = Image.open(io.BytesIO(pagina.screenshot(clip=recorte))).convert("RGB")
    pagina.eval_on_selector(".cae-cursor-mancha", "el => { el.style.display = 'none'; }")
    sin = Image.open(io.BytesIO(pagina.screenshot(clip=recorte))).convert("RGB")
    pagina.eval_on_selector(".cae-cursor-mancha", "el => { el.style.removeProperty('display'); }")
    total = sum(
        abs(a[i] - b[i]) for a, b in zip(con.getdata(), sin.getdata()) for i in range(3)
    )
    return total / (con.size[0] * con.size[1] * 3)
```

- [x] **Step 2: Escribe el gate 6**

```python
# AA para texto normal. La leyenda de la tarjeta es Fraunces 14px y el texto
# de la pastilla 12px: ninguno llega a "texto grande", asi que el umbral es
# 4.5 y no 3.
AA = 4.5
# Se fija en el Step 3, con la primera medida: la MITAD del peor delta
# observado. Arranca en 0 para poder leer los numeros sin que el gate corte.
# No lo bajes despues para que pase: si el derrame no se nota, el derrame
# esta mal.
UMBRAL_NOTA = 0.0
# Cada 30 minutos: 48 posiciones del reloj. El matiz avanza 0,25 grados por
# minuto y la marea de croma es continua, asi que 30 min no se salta ningun
# extremo -- y el cruce de esquema (07:00 y 20:00) cae dentro del barrido.
PASO_MINUTOS = 30


def gate_contraste(pagina, base: str) -> None:
    """Gate 6 -- el contraste bajo el derrame, en las 24 horas.

    Lo que NO es invariante por construccion: la perla y la mancha mezclan
    (`multiply` de dia, `screen` de noche) con lo que hay debajo, y el
    pigmento pierde dos tercios de croma cuando la marea pasa por el naranja
    y el magenta. La invariancia del motor de color vale para los ROLES, no
    para una mezcla encima. Un cursor calibrado a una sola hora no esta
    calibrado.

    Antes de creerse un solo numero: la consola en verde. Toda la
    calibracion del cursor de Hyprland se midio contra una pagina cuya
    coreografia estaba rota, y ninguna asercion pudo detectarlo porque todas
    comparaban la pagina consigo misma.
    """
    print("[6] contraste bajo el derrame, barrido de 24 horas")

    peor_contraste = (99.0, "")
    peor_delta = (999.0, "")

    for escena, diana, texto, accion in (
        ("obra", ".cae-obra-card", ".cae-obra-caption", "clic"),
        ("creditos", ".cae-cred-pieza:nth-child(3)", ".cae-cred-pieza:nth-child(3) .cae-cred-nom", "roce"),
    ):
        abre(pagina, base, escena)
        pagina.hover(diana, position={"x": 40, "y": 30})
        if accion == "clic":
            pagina.mouse.down()
        pagina.wait_for_timeout(700)

        for minutos in range(0, 1440, PASO_MINUTOS):
            pagina.evaluate(f"() => window.__CAE_SET_MINUTOS__({minutos})")
            pagina.wait_for_timeout(120)
            ratio = _contraste_glifo(pagina, texto)
            etiqueta = f"{escena} {minutos // 60:02d}:{minutos % 60:02d}"
            if 0 < ratio < peor_contraste[0]:
                peor_contraste = (ratio, etiqueta)
            if ratio == 0.0:
                check(False, f"[6] {etiqueta}: no se encontro ni un pixel de glifo que medir")

        # La perceptibilidad se mide en dos horas, no en las 48: es una
        # propiedad del derrame, no del reloj.
        for minutos in (540, 180):
            pagina.evaluate(f"() => window.__CAE_SET_MINUTOS__({minutos})")
            pagina.wait_for_timeout(200)
            delta = _delta_medio(pagina, diana)
            if delta < peor_delta[0]:
                peor_delta = (delta, f"{escena} {minutos // 60:02d}:00")

        if accion == "clic":
            pagina.mouse.up()

    check(
        peor_contraste[0] >= AA,
        f"[6] AA bajo el derrame en las 24 horas (peor {peor_contraste[0]:.2f}:1 en {peor_contraste[1]})",
    )
    # UMBRAL_NOTA se fija con la primera medida y se anota en el spec. No lo
    # bajes para que pase: si el derrame no se nota, el derrame esta mal.
    check(
        peor_delta[0] >= UMBRAL_NOTA,
        f"[6] el derrame se NOTA (peor delta medio {peor_delta[0]:.2f} en {peor_delta[1]})",
    )
```

- [x] **Step 3: Corre una vez con `UMBRAL_NOTA = 0` para leer las medidas**

```bash
nohup python3 scripts/measure-caelestia-cursor.py --base http://localhost:4173 \
  > /tmp/cursor-gates.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -40 /tmp/cursor-gates.log
```

**Lánzalo con `nohup` y espera por PID**, nunca en primer plano ni con un bucle `pgrep -f` sobre su
propio nombre: el patrón casa con la línea de comando del propio bucle. El barrido son 96 medidas
con dos capturas cada una; cuenta varios minutos.

Anota el `delta medio` peor. Fija `UMBRAL_NOTA` en **la mitad** de ese valor (margen explícito
frente al ruido del compositor, no un umbral pegado a la medida: un umbral más fino que el ruido de
su instrumento mide carga de máquina).

- [x] **Step 4: El punto de decisión — si AA no aguanta**

Si el peor contraste baja de 4,5, **no toques el umbral**. Aplica la pregunta abierta 1 del spec: la
mancha pasa a pintarse **debajo del texto**. El cambio es acotado:

- La mancha deja de ser un elemento propio y pasa a ser un `background-image` en línea sobre la
  diana (un `radial-gradient` con el mismo centro y radio), guardando el valor previo y
  restaurándolo al cambiar de diana y en `destroy()` — el patrón de `hyprCursor.ts:restaurarImagen`.
- `_delta_medio` deja de poder apagar la mancha con `display`: expón `medirMancha(oculto: boolean)`
  en la sonda, como `hyprCursor.ts:medirImagen`, y **documenta por qué existe**.
- Anota el cambio de mecanismo en el `Registro de implementación` del spec, con los dos números.

- [x] **Step 5: Fija el umbral, anótalo en el spec y deja el gate verde**

Escribe en el spec, en `## Preguntas abiertas para el plan`, punto 4: el valor medido, el umbral
elegido y la fecha. Corre el arnés entero: verde.

- [x] **Step 6: Sabotea el gate por los dos lados**

1. Sube la opacidad de `.cae-cursor-gota` a `0.6`: el check de AA tiene que dar **FAIL**.
2. Bájala a `0`: el check de «se nota» tiene que dar **FAIL**.

Los dos sabotajes por separado, mirando el rojo cada vez. Restaura.

- [x] **Step 7: Commit**

```bash
git add scripts/measure-caelestia-cursor.py docs/superpowers/specs/2026-09-04-caelestia-cursor-design.md
git commit -m "test(cursor): barrido de 24 horas — contraste bajo el derrame y perceptibilidad"
```

---

## Task 8: Limpieza y consola

**Files:**
- Modify: `scripts/measure-caelestia-cursor.py` (gate 7; el 8 ya está desde el Task 1)
- Modify: `src/components/caelestiaCursor.ts` si el gate lo pide

**Interfaces:**
- Consumes: `__caeCursor__.destroy()`.
- Produces: nada nuevo.

- [x] **Step 1: Escribe el gate 7**

```python
def gate_limpieza(pagina, base: str) -> None:
    """Gate 7 -- `destroy()` no deja nada detras.

    Incluye el caso que se escapa solo: un cerco lanzado JUSTO antes de
    desmontar. Su animacion dura 800 ms y se limpia en `animationend`; si
    `destroy()` no se lo lleva, el anillo sobrevive a su modulo y se queda
    en el DOM hasta que termine -- DOM huerfano, y encima animandose.
    """
    print("[7] limpieza")
    abre(pagina, base, "obra")
    pagina.hover(".cae-obra-card", position={"x": 200, "y": 70})
    pagina.wait_for_timeout(400)
    pagina.mouse.down()
    pagina.mouse.up()  # deja un cerco vivo
    pagina.wait_for_timeout(80)
    check(
        pagina.evaluate("() => document.querySelectorAll('.cae-cursor-cerco').length") >= 1,
        "[7] partida: hay un cerco vivo",
    )

    pagina.evaluate("() => window.__caeCursor__.destroy()")
    pagina.wait_for_timeout(200)

    resto = pagina.evaluate(
        """() => ({
             nodos: document.querySelectorAll('[class^="cae-cursor"]').length,
             clase: document.documentElement.classList.contains('caelestia-cursor-ready'),
             sonda: '__caeCursor__' in window,
             glifo: getComputedStyle(document.querySelector('.cae-obra-card')).cursor,
           })"""
    )
    check(resto["nodos"] == 0, f"[7] no queda ningun nodo del cursor ({resto['nodos']})")
    check(not resto["clase"], "[7] la clase ready se retira")
    check(not resto["sonda"], "[7] la sonda desaparece de window")
    check(
        resto["glifo"] == "pointer",
        f"[7] vuelve el glifo del sistema sobre lo pulsable ({resto['glifo']})",
    )
```

- [x] **Step 2: Corre. Si falla, arréglalo**

Lo previsible es que fallen los cercos (si no los recoge `destroy()`) y `glifo` (si la clase `ready`
no se quita). Los dos tienen su código desde los Tasks 2 y 4; si fallan, es que falta llamarlo.

- [x] **Step 3: Comprueba el gate 8 con una página que sí ensucia la consola**

El gate 8 (cero errores de consola) existe desde el Task 1 y ha estado verde todo el rato — que es
justo lo que lo hace sospechoso. Sabotéalo: mete `window.noExiste.nada;` al principio de
`mountCaelestiaCursor`, reconstruye y corre. Tiene que dar **FAIL** con el texto del error.
Restaura y reconstruye.

Este es el gate que caza el modo de fallo más caro del proyecto: un `gsap is not defined` que `tsc`
y `eslint` dan por bueno y solo aparece en el navegador.

- [x] **Step 4: Commit**

```bash
git add scripts/measure-caelestia-cursor.py src/components/caelestiaCursor.ts
git commit -m "test(cursor): gate de limpieza de destroy() y de consola"
```

---

## Task 9: Cerrar — documentación y estado

**Files:**
- Modify: `.claude/rules/verification.md`
- Modify: `docs/superpowers/specs/2026-09-04-caelestia-cursor-design.md`
- Modify: `CLAUDE.md` y `.claude/CLAUDE.md`

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: el estado final del spec.

- [ ] **Step 1: Añade el arnés a la tabla de `rules/verification.md`** — QUEDA PARA EL MERGE

`.claude/` está en `.gitignore`: **no existe en este worktree y no viaja en esta rama**. Vive solo
en el directorio del repo principal, que es justo donde hay otra sesión trabajando en B5 con su
`vite preview` vivo, y que además va a escribir su propio párrafo en el mismo fichero. Editarlo
desde aquí no aporta nada a la rama y se pisa con esa sesión, así que la fila se aplica **al
fusionar**, no ahora. La fila lista para pegar es la de abajo; el `Estado:` del spec se queda en
`en ejecucion` hasta entonces, que es lo que de verdad pasa.

Una fila, con el mismo formato que las demás:

```markdown
| `measure-caelestia-cursor.py` | El cursor de Caelestia (la gota): presencia por tema y que en táctil y con movimiento reducido **no se descargue el chunk** (se vigila la petición de red, no el DOM); el reparto de señales, incluida la inversión que hace que la leyenda de una tarjeta y el nombre de una pieza **no** apaguen la gota aunque sean `figcaption`; los dos momentos del gesto (la pieza se moja al rozarla, la tarjeta al pulsarla) leyendo el avance **pintado** y no el objetivo escrito; que no haya inercia (delta cero tras un fotograma, no «menor que»); el estado rancio al cambiar de workspace **con el ratón quieto**; el contraste bajo el derrame medido **píxel a píxel** en las 24 horas —la mezcla `multiply`/`screen` hace que ni el texto ni el fondo se pinten del color que declaran, así que `getComputedStyle` mediría otra página— junto con que el derrame **se note**; la limpieza de `destroy()` incluido un cerco vivo; y la consola. **No juzga `.gallery-track`**: existe en el DOM pero es invisible en Caelestia, y una aserción suya sería tautológica. | `npm run build && npx vite preview --port 4173 &`<br>`nohup python3 scripts/measure-caelestia-cursor.py --base http://localhost:4173 > /tmp/cursor.log 2>&1 &`<br>`PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -40 /tmp/cursor.log` |
```

- [x] **Step 2: Escribe el `Registro de implementación` en el spec**

Añade una sección al final con: qué se desvió del diseño y por qué, los números finales del gate 6
(peor contraste y en qué hora, peor delta y umbral elegido), qué mecanismo quedó para el derrame
(encima con mezcla, o debajo del texto), y **qué instrumento resultó estar roto**, si alguno. Si
ninguno lo estuvo, escríbelo también: es un dato, no un hueco.

Cambia la cabecera a `Estado: implementado` y añade `Plan: docs/superpowers/plans/2026-09-04-caelestia-cursor.md`.

- [x] **Step 3: Marca las casillas de este plan**

Todas las de las tareas hechas. `scripts/verify.py` cruza el `Estado:` del spec contra las casillas
del plan: con el spec en `implementado` y casillas sin marcar, falla — y con razón.

- [x] **Step 4: Actualiza los dos `CLAUDE.md`**

Un párrafo en `## Theme Status` (inglés) y otro en `## ESTADO DE LOS TEMAS` (español), al estilo de
los del cursor de Hyprland. Tiene que decir: que Caelestia ya tiene cursor propio y cuál es su
tesis; que la lista blanca cuelga de la **raíz** y no de `[data-scene]`, con la razón medida; que
`button[aria-pressed]` es lo que separa las dos familias; y el arnés que lo vigila.

**No edites los `CLAUDE.md` a mitad de una sesión de trabajo** — invalida la caché de prompt. Esta
tarea es el final, así que aquí es el sitio correcto.

- [x] **Step 5: Verificación final completa**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
python3 scripts/verify.py                        # linea base y bloque [docs]
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173      # fase A intacta
python3 scripts/measure-caelestia-cursor.py --base http://localhost:4173    # el nuevo
python3 scripts/measure-cursor-luz.py --base http://localhost:4173          # Hyprland intacto
```

Los cuatro en verde. El de Hyprland es el que demuestra que no se ha tocado el cursor de al lado; el
de la hora, que la fase A sigue en pie.

- [x] **Step 6: Captura de las tres dianas, de día y de noche, y a ojo**

Última mirada antes de declarar nada: las tres dianas (tarjeta, pieza, pastilla), a 09:00 y a 03:00,
con el derrame lleno. Es lo que ningún número dice, y es lo que cazó el fallo de B4 que ningún gate
vio.

- [x] **Step 7: Commit**

```bash
git add .claude/rules/verification.md docs/superpowers/ CLAUDE.md .claude/CLAUDE.md
git commit -m "docs(cursor): cierra el cursor de Caelestia — registro, arnes y estado de los temas"
```

---

## Lo que este plan NO decide

- **Móvil**: fuera de alcance y sin deuda. El módulo no se descarga en táctil (gate 1), que es el
  mismo criterio de Vice y Hyprland.
- **El `lidia-naive-tester` y el `vera-art-director`**: son el gate de crítica antes de fusionar a
  `main`, no parte de este plan. Se lanzan después, con el dispositivo montado, y sus hallazgos se
  anotan en el spec como en las fases anteriores.
- **La fusión con B5**: las dos ramas escriben en el bloque de Caelestia de `themes.css`. Este plan
  pone su bloque al final para que el conflicto sea de adyacencia. Resolverlo es de quien fusione.
- **Si el prototipo y la implementación divergen en el acabado** (la maqueta es HTML suelto, el
  sitio lleva shader detrás): manda la captura contra la maqueta, y si hay que retocar un número de
  opacidad, se retoca y se anota. Lo que no se puede tocar sin volver al spec es el **gesto**: los
  dos momentos, el derrame que llena, el cerco solo en el clic, y nada de estela.
