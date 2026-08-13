# La cinta — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rehacer la escena de cierre `[data-scene="contacto"]` del tema Hyprland como una cinta a
sangre en escritorio y un mosaico de bandas en móvil, con entrada letra a letra, y arreglar de paso
los siete defectos medidos que arrastra el bloque actual.

**Architecture:** Todo el cambio vive en dos ficheros de tema —`src/themes/themes.css` (bloque
`Hyprland: las bandas`, regla de tamaño de `.contacto-title` y gramática de revelado) y
`src/themes/hypr.choreography.ts`—. El DOM compartido `src/sections/contacto.ts` **no se toca**:
el troceo del titular lo hace la coreografía (que es código de tema) y el filete de reposo reutiliza
el `<span>` vacío `.contacto-bar-mark` que ya existe. `src/style.css` tampoco se edita: sus valores
heredados se anulan localmente bajo `:root[data-theme="hyprland"]`.

**Tech Stack:** Vite 8, TypeScript ~6 (strict), Tailwind 4, GSAP 3 + ScrollTrigger, Lenis. Sin
framework y sin Three.js. Verificación con Playwright (Python).

**Spec:** `docs/superpowers/specs/2026-08-13-hyprland-contacto-cinta-design.md`

## Global Constraints

- **Rama y worktree:** todo el trabajo va en `/home/aoshi/proyectos/portfolio-hyprland-contacto`,
  rama `design/hyprland-contacto`. Nunca en `main`.
- **Node 22 obligatorio.** Con Node 18 el build cae con
  `SyntaxError: The requested module 'node:util' does not provide an export named 'styleText'`.
  Prefija el PATH: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`.
- **Solo Hyprland.** Cada regla nueva va bajo `:root[data-theme="hyprland"]`. **Vice está cerrado
  y no se toca.** Caelestia no se toca y se comprueba que sigue idéntica.
- **No editar** `src/sections/contacto.ts`, `src/data/content.ts` ni `src/style.css`.
- **Nunca `gsap.from`** — siempre `fromTo` con los dos extremos escritos a mano. `Array.from(...)`
  para colecciones vivas.
- **Nunca `any`** (`strict` está activo). `unknown` + type guards si hace falta.
- **Prohibido dimensionar tipo con una función continua sobre los tokens de la escala.**
  `clamp(var(--t-3), 2.4vw, var(--t-4))` está vetado: se escalona con `@media` cambiando un token
  por otro.
- **Vocabulario de movimiento:** encender es un corte, 420 o 500ms con
  `--hard: cubic-bezier(0.7,0,0.2,1)`. Apagar es enfriarse, 900ms con
  `--slow: cubic-bezier(0.16,0.84,0.28,1)`. Escalón `--hypr-d = n * 70ms`. Ningún otro número.
- **Ninguna regla de hover puede colgar de `.is-lit`**: bajo `prefers-reduced-motion` esa clase no
  se añade nunca, así que todo estado en reposo debe quedar asentado sin ella.
- **Cero emojis** en código, documentación y mensajes de commit.
- **Verificación visual antes de DONE.** Ningún paso se marca sin haber corrido su comprobación.
- Servir siempre el **build de producción** (`npx vite preview --port 4173`), nunca `npm run dev`:
  el HMR corrompe las medidas de layout y de ScrollTrigger.
- Verificar siempre con `?theme=hyprland` — el tema se sortea por visita.

---

### Task 1: Los defectos heredados

Arregla los siete defectos medidos que ya están en `main` antes de tocar la composición. Es la
tarea que se podría entregar sola.

**Files:**
- Modify: `src/themes/themes.css` (bloque `Hyprland: las bandas`, L5596-5684; regla de tamaño de
  `.contacto-title`, L1334-1337)

**Interfaces:**
- Consumes: nada.
- Produces: `--cinta-h`, `--franja-h` y `--mosaico-h`, declaradas sobre
  `[data-scene="contacto"]` —el ancestro común de la cinta y del estado, que no cuelga de ella— y
  que las tareas 2, 3 y 4 usan para que la franja de estado y la cinta no puedan separarse.

- [x] **Step 1: Levantar el arnés de contraste y verlo fallar**

Crea `scripts/measure-contacto-cinta.py`. Mide **por glifo**, no por rectángulo: el haz del shader
cruza la calle central vacía y una medida a lo ancho sobreestima el contraste.

```python
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
        print("fallos:", fallos or "ninguno")
        b.close()
    return 1 if fallos else 0

if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 2: Correrlo y verlo FALLAR**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && (npx vite preview --port 4173 &) && sleep 4
python3 scripts/measure-contacto-cinta.py --base http://localhost:4173
```
Esperado: **salida 1**, con los cuatro `.contacto-bar-label` y el `.contacto-estado-label` marcados
`FALLA` entre 2,19 y 2,94:1. Si sale 0 a la primera, el arnés no está midiendo lo que crees:
comprueba que la escena está en pantalla y que las cajas no son vacías antes de seguir.

- [x] **Step 3: Resetear la opacidad heredada y quitar la calle doble**

En `src/themes/themes.css`, dentro del bloque `Hyprland: las bandas`, sustituye la regla de
`[class*="contacto-bar--"]` (hoy L5610-5617) y la de `.contacto-bar-label` (L5631-5643):

```css
/* Alturas en UN solo sitio, y sobre la SECCION, no sobre `.contacto-bars`:
   `.contacto-estado` vive dentro de `.contacto-band` y no cuelga de la cinta,
   asi que una variable declarada en la cinta no le llegaria nunca — las custom
   properties solo se heredan hacia abajo, y la seccion es el ancestro comun.
   La franja de estado se coloca en absoluto y se ata a estas, para que no
   puedan separarse cuando alguien cambie una y olvide la otra.
   `--mosaico-h` es la altura del mosaico movil: 132 + 96*3 + 3 juntas. */
:root[data-theme="hyprland"] [data-scene="contacto"] {
  --franja-h: 27px;
  --cinta-h: 140px;
  --mosaico-h: 423px;
}
:root[data-theme="hyprland"] .contacto-bars {
  flex-direction: column;
  border-top: 1px solid var(--rule);
}
:root[data-theme="hyprland"] [class*="contacto-bar--"] {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 0 0 auto;
  /* 1.4rem 0, no 1.4rem 7vw: la calle de 7vw ya la pone la escena y sumarlas
     arrancaba el texto en x=201,6 en vez de los x=100,8 de la placa y el
     catastro. Es la misma calle doble que el catastro ya corrigio. */
  padding: 1.4rem 0;
  border-bottom: 1px solid var(--rule);
  background: none;
  overflow: hidden;
}
:root[data-theme="hyprland"] .contacto-bar-label,
:root[data-theme="hyprland"] .contacto-estado-label {
  /* style.css deja estos rotulos a `opacity: 0.6` y el bloque de Hyprland les
     daba color pero nunca reseteaba la opacidad. Medido por glifo contra el
     shader vivo: 2,19-2,94:1, cuando AA pide 4,5. Vice ya tiene este mismo
     reset explicito en su propia regla; Hyprland nunca lo copio. */
  opacity: 1;
  color: var(--haze);
}
```

- [x] **Step 4: Quitar el número fuera de vocabulario y las dos funciones continuas**

Misma hoja. La inundación pasa de `0.45s` a `0.42s` (L5629), y las dos `clamp()` se escalonan:

```css
/* 0.42s, no 0.45: el tema solo tiene 0,42/0,5 para encender y 0,9 para
   enfriar. 0,45 no pertenece a ninguno de los dos regimenes. */
:root[data-theme="hyprland"] [class*="contacto-bar--"]::before {
  transition: transform 0.42s var(--hard);
}

/* El valor se escalona con @media cambiando un token por otro. Una funcion
   continua sobre los tokens devuelve cualquier real entre sus topes y esconde
   el fallo justo en 390 y 1440, que es donde cae en sus paradas limpias. */
:root[data-theme="hyprland"] .contacto-bar-value {
  font-size: var(--t-4);
}
@media (max-width: 900px) {
  :root[data-theme="hyprland"] .contacto-bar-value { font-size: var(--t-3); }
}

/* `.contacto-title` comparte con `.display-xl` la regla de L1334-1337, que usa
   clamp. No se toca esa: se le da aqui la suya propia, escalonada, para no
   cambiar ni el hero ni el about. */
:root[data-theme="hyprland"] .contacto-title { font-size: var(--t-9); }
@media (max-width: 900px) {
  :root[data-theme="hyprland"] .contacto-title { font-size: var(--t-6); }
}
```

- [x] **Step 5: Volver a correr el arnés y verlo pasar**

Run: `npm run build && python3 scripts/measure-contacto-cinta.py --base http://localhost:4173`
Esperado: los ocho nodos por encima de 4,5:1 y **salida 0**. Si un rótulo sigue fallando, el reset
de opacidad no está llegando: comprueba `getComputedStyle(node).opacity` antes de tocar el scrim —
subir el scrim para tapar un problema de especificidad oscurece el fondo generativo sin motivo.

- [x] **Step 6: Commit**

```bash
git add src/themes/themes.css scripts/measure-contacto-cinta.py
git commit -m "fix(contacto): los rotulos de hyprland fallaban AA por una opacidad heredada

Reset explicito de opacity, calle doble de 7vw eliminada, la inundacion vuelve
al vocabulario (0.42s) y las dos funciones continuas sobre la escala pasan a
escalones discretos. Arnes nuevo que mide el contraste por glifo."
```

---

### Task 2: La cinta en escritorio

**Files:**
- Modify: `src/themes/themes.css` (bloque `Hyprland: las bandas`)

**Interfaces:**
- Consumes: `--cinta-h` y `--franja-h` de la Task 1.
- Produces: `.contacto-bars` anclada al pie de la sección con `position: absolute`; el
  `.contacto-bar-mark` reconvertido en filete de reposo.

- [x] **Step 1: Comprobar qué relleno pone la escena**

Antes de anclar nada hay que saber si `[data-scene]` mete relleno propio en Hyprland.

```bash
grep -n 'data-theme="hyprland"\] \[data-scene\]' src/themes/themes.css
```
Anota el valor. Si existe, la banda de título necesitará `padding-bottom` suficiente para no
chocar con la cinta; si no, basta con el que ya trae de `style.css`.

- [x] **Step 2: Escribir la cinta**

```css
/* LA CINTA. No hay celdas: los cuatro valores repartidos sobre un filete a
   sangre pegado al pie de la escena. Es la unica composicion donde el correo
   puede ir a 28,43px, porque ninguna columna lo encierra: medido, los cuatro
   ocupan 1265 de 1440 y sobran 175 para repartir. */
@media (min-width: 901px) {
  :root[data-theme="hyprland"] .contacto-bars {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: calc(var(--cinta-h) + var(--franja-h));
    padding: var(--franja-h) 7vw 0;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    /* Scrim calibrado CONTRA ESTA FRANJA con el fondo generativo en su punto
       mas brillante. No se reutiliza de ningun otro tema: un porcentaje se
       calibra contra una superficie, no contra un token. */
    background: rgb(11 4 4 / 0.88);
    border-top: 1px solid var(--rule);
  }
  /* EL FILETE de ventana activa del gestor. En el prototipo era un <span>;
     aqui no hay nodo para el y no se va a anadir uno a `contacto.ts`, que es
     DOM compartido — asi que es un pseudo-elemento. Llega hasta el borde
     derecho: muriendo antes se leia como una linea sin terminar. */
  :root[data-theme="hyprland"] .contacto-bars::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--l1), var(--l2) 46%, rgb(224 29 60 / 0.35));
    transform-origin: left;
  }
  :root[data-theme="hyprland"] [class*="contacto-bar--"] {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0;
    padding: 0;
    border-bottom: 0;
    overflow: visible;
  }
  /* El rotulo va ENCIMA del valor: cuesta alto y no ancho, asi que no le quita
     nada a los 28,43px del dato. Sin el, "Aoshi346" no dice nada. */
  :root[data-theme="hyprland"] .contacto-bar-label {
    width: auto;
    margin-bottom: 12px;
    transition: color 0.9s var(--slow);
  }
  :root[data-theme="hyprland"] [class*="contacto-bar--"]:hover .contacto-bar-label,
  :root[data-theme="hyprland"] [class*="contacto-bar--"]:focus-visible .contacto-bar-label {
    color: var(--l3);
    transition: color 0.42s var(--hard);
  }
  /* El <span> vacio que hoy es una rayita decorativa pasa a ser el filete de
     reposo: la senal de que esto es un enlace. En tactil no hay hover, asi que
     un enlace que solo lo parece al apuntarlo no lo parece nunca. */
  :root[data-theme="hyprland"] .contacto-bar-mark {
    order: 2;
    width: 100%;
    height: 1px;
    margin: 10px 0 0;
    opacity: 1;
    background: rgb(255 160 60 / 0.42);
    position: relative;
  }
  :root[data-theme="hyprland"] .contacto-bar-mark::after {
    content: "";
    position: absolute;
    inset: -1px 0 0;
    height: 2px;
    background: var(--l1);
    transform: scaleX(0);
    transform-origin: left;
    /* Apagar es enfriarse: 0,9s --slow. Encender es un corte: 0,5s --hard.
       Asimetrico, que es la ley del tema. */
    transition: transform 0.9s var(--slow);
  }
  :root[data-theme="hyprland"] [class*="contacto-bar--"]:hover .contacto-bar-mark::after,
  :root[data-theme="hyprland"] [class*="contacto-bar--"]:focus-visible .contacto-bar-mark::after {
    transform: scaleX(1);
    transition: transform 0.5s var(--hard);
  }
  /* Los tres vecinos se enfrian. Un gesto de GRUPO, no cuatro independientes:
     bajan a la vez y sin escalon. Con :has(), sin JavaScript ni listeners. */
  :root[data-theme="hyprland"] [class*="contacto-bar--"] {
    transition: opacity 0.9s var(--slow);
  }
  :root[data-theme="hyprland"] .contacto-bars:has([class*="contacto-bar--"]:hover)
    [class*="contacto-bar--"]:not(:hover),
  :root[data-theme="hyprland"] .contacto-bars:has([class*="contacto-bar--"]:focus-visible)
    [class*="contacto-bar--"]:not(:focus-visible) {
    opacity: 0.5;
  }
}
/* Foco de teclado. Offset negativo porque la banda lleva overflow hidden en
   movil y un offset positivo se recortaria contra el. */
:root[data-theme="hyprland"] [class*="contacto-bar--"]:focus-visible {
  outline: 3px solid var(--l1);
  outline-offset: -3px;
}
```

- [x] **Step 3: Medir que el correo cabe en un renglón y que la cinta está al pie**

Añade a `scripts/measure-contacto-cinta.py`:

```python
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
```

Run: `npm run build && python3 scripts/measure-contacto-cinta.py --base http://localhost:4173`
Esperado: `renglones: 1`, `pie: 0`, `alto: 167`, salida 0.

- [x] **Step 4: Captura de escritorio y revisión a ojo**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=hyprland', wait_until='domcontentloaded')
    pg.wait_for_timeout(9000)
    pg.evaluate('document.querySelector(\"[data-scene=+chr(39)+contacto+chr(39)+\"]\").scrollIntoView()')
    pg.wait_for_timeout(2500)
    pg.screenshot(path='/tmp/cinta-desktop.png')
    b.close()
"
```
**Mira la captura.** Los arneses salen verdes con el resultado roto: comprueba que los cuatro
valores están repartidos de margen a margen, que el rótulo cae encima del dato y que el filete de
reposo se ve bajo los cuatro.

- [x] **Step 5: Commit**

```bash
git add src/themes/themes.css scripts/measure-contacto-cinta.py
git commit -m "feat(contacto): la cinta sustituye a la lista de barras en hyprland

Cuatro valores repartidos sobre un filete al pie de la escena, rotulo encima
del dato y el <span> vacio de la marca reconvertido en filete de reposo. Hover
con filo de 2px, rotulo caliente y los tres vecinos enfriandose con :has()."
```

---

### Task 3: La franja de estado

**Files:**
- Modify: `src/themes/themes.css` (bloque `Hyprland: las bandas`)

**Interfaces:**
- Consumes: `--cinta-h` y `--franja-h` de la Task 1.
- Produces: `.contacto-estado` colocada en absoluto coronando la cinta.

- [x] **Step 1: Colocar el estado como módulo del extremo**

```css
/* EL ESTADO, modulo del extremo. Es la convencion real de una barra de estado
   de gestor de ventanas: a la izquierda lo que haces, a la derecha el estado
   del sistema. Y es lo unico de la cinta sin filete de reposo, porque es lo
   unico que no es un enlace.

   Va en absoluto porque NO SE PUEDE MOVER en el DOM: vive dentro de
   `.contacto-band` y Vice depende de esa posicion para sus marcas de esquina.
   Se ata a las mismas dos variables que la cinta para que no se separen; el
   arnes comprueba que los dos bordes coinciden. */
@media (min-width: 901px) {
  :root[data-theme="hyprland"] .contacto-estado {
    position: absolute;
    left: 0;
    right: 0;
    bottom: var(--cinta-h, 140px);
    height: var(--franja-h, 27px);
    margin: 0;
    padding: 0 7vw;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 14px;
    font-size: var(--t-1);
    border-bottom: 1px solid var(--rule);
    background: rgb(255 90 52 / 0.06);
  }
  :root[data-theme="hyprland"] .contacto-estado-label {
    letter-spacing: 0.24em;
    text-transform: uppercase;
  }
  /* El separador "·" sobra cuando los dos trozos ya estan separados por el
     hueco del flex. */
  :root[data-theme="hyprland"] .contacto-estado-sep { display: none; }
  :root[data-theme="hyprland"] .contacto-estado-value {
    letter-spacing: 0.06em;
    color: var(--color-paper);
  }
  /* La banda de titulo deja sitio a la cinta entera mas aire. */
  :root[data-theme="hyprland"] .contacto-band {
    padding-bottom: calc(var(--cinta-h, 140px) + var(--franja-h, 27px) + 2rem);
  }
}
```

- [x] **Step 2: Asertar que la franja y la cinta no se han separado**

Añade a `scripts/measure-contacto-cinta.py`:

```python
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
```

Run: `npm run build && python3 scripts/measure-contacto-cinta.py --base http://localhost:4173`
Esperado: `separacion: 0`, salida 0.

- [x] **Step 3: Commit**

```bash
git add src/themes/themes.css scripts/measure-contacto-cinta.py
git commit -m "feat(contacto): el estado pasa a ser el modulo del extremo de la cinta

Coronandola en una franja de 27px alineada a la derecha, atada a las mismas
variables de altura que la cinta. En absoluto porque el nodo no se puede mover
del DOM sin romper Vice; el arnes asierta que los dos bordes coinciden."
```

---

### Task 4: El mosaico en móvil

**Files:**
- Modify: `src/themes/themes.css` (bloque `Hyprland: las bandas`, incluida la media query
  `max-width: 520px` de L5670-5684, que se sustituye)

**Interfaces:**
- Consumes: la cinta de la Task 2 y la franja de la Task 3, ambas ya bajo `min-width: 901px`.
- Produces: nada que consuman tareas posteriores.

- [x] **Step 1: Borrar la media query de 520px y escribir el mosaico**

La regla `@media (max-width: 520px)` actual (L5670-5684) se elimina entera: el breakpoint pasa a
900px, que es el que ya usa el resto del tema, y la composición es otra.

```css
/* EL MOSAICO. Apilar la cinta da un pie de pagina generico. La idea no era una
   lista: eran bandas a sangre pegadas al borde, y en una pantalla alta eso se
   dice TESELANDO el borde inferior — lo que hace un gestor en mosaico con un
   monitor vertical. Medido a 390x844: 703 de 844 de alto, sin desbordar. */
@media (max-width: 900px) {
  :root[data-theme="hyprland"] .contacto-bars {
    /* La calle deja de ser un porcentaje. 7vw son 101px en 1440 y 27 en 390:
       el mismo numero da una calle generosa alla y asfixiante aqui. Un valor
       calibrado contra un ancho no viaja a otro, igual que una opacidad no
       viaja entre dos superficies. */
    --calle: 30px;
    display: grid;
    grid-template-rows: 132px 96px 96px 96px;
    gap: 1px;
    background: none;   /* la junta no se pinta: deja ver el ascua de detras */
    border-top: 0;
  }
  :root[data-theme="hyprland"] [class*="contacto-bar--"] {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    gap: 11px;
    padding: 0 var(--calle);
    min-height: 0;      /* la altura la manda la fila de la rejilla */
    border-bottom: 0;
    background: rgb(11 4 4 / 0.90);
    overflow: hidden;
    -webkit-tap-highlight-color: transparent;
  }
  :root[data-theme="hyprland"] .contacto-bar-label { margin-bottom: 0; }
  :root[data-theme="hyprland"] .contacto-bar-mark { display: none; }
  /* Pulsar enciende el canto: 3px de --l1 a la izquierda, la marca de ventana
     con foco del gestor. En tactil no hay hover, asi que el unico estado que
     importa es el de pulsacion. */
  :root[data-theme="hyprland"] [class*="contacto-bar--"]::after {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--l1);
    transform: scaleY(0);
    transition: transform 0.9s var(--slow);
  }
  :root[data-theme="hyprland"] [class*="contacto-bar--"]:active::after,
  :root[data-theme="hyprland"] [class*="contacto-bar--"]:focus-visible::after {
    transform: scaleY(1);
    transition: transform 0.42s var(--hard);
  }
  :root[data-theme="hyprland"] [class*="contacto-bar--"]:active {
    background: rgb(30 8 5 / 0.94);
  }
  /* El mosaico se ancla al pie de la seccion, que es flex column con
     min-h-screen: `margin-top: auto` lo empuja abajo. */
  :root[data-theme="hyprland"] .contacto-bars { margin-top: auto; }
  /* El estado es el modulo del extremo: en una pila, el extremo es ARRIBA.
     Va en absoluto por lo mismo que en escritorio — el nodo no se puede mover
     del DOM sin romper Vice — atado a `--mosaico-h` para que corone el mosaico
     en vez de quedarse a media pantalla detras del lead. */
  :root[data-theme="hyprland"] .contacto-estado {
    position: absolute;
    left: 0;
    right: 0;
    bottom: var(--mosaico-h, 423px);
    margin: 0;
    height: 46px;
    padding: 0 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    font-size: var(--t-1);
    border-top: 2px solid var(--l1);
    background: linear-gradient(180deg, rgb(255 90 52 / 0.13), rgb(11 4 4 / 0.92));
  }
  :root[data-theme="hyprland"] .contacto-estado-sep { display: none; }
  :root[data-theme="hyprland"] .contacto-band { padding-inline: var(--calle, 30px); }
}
```

- [x] **Step 2: Medir a 390 de verdad**

**Nunca midas el móvil con un `div` de 390px dentro de una ventana ancha:** `vw` y `vh` se resuelven
contra la ventana del navegador, no contra el `div`, y las medidas salen falsas. Playwright con
`viewport={'width': 390}` es el único laboratorio honesto.

Añade a `scripts/measure-contacto-cinta.py` una segunda pasada:

```python
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
```

Run: `npm run build && python3 scripts/measure-contacto-cinta.py --base http://localhost:4173`
Esperado: `calle: 30`, `renglones: 1`, `correo: 248`, `bandas: [132, 96, 96, 96]`, salida 0.

- [x] **Step 3: Mirar `/tmp/cinta-movil.png`**

Comprueba que nada toca el marco, que las juntas de 1px dejan ver el ascua y que el mosaico no
desborda los 844px.

- [x] **Step 4: Commit**

```bash
git add src/themes/themes.css scripts/measure-contacto-cinta.py
git commit -m "feat(contacto): el mosaico sustituye al apilado en movil

Cuatro bandas a sangre teselando el borde inferior, junta de 1px sin pintar,
la del correo mas alta por area. La calle deja de ser un porcentaje y pasa a
30px fijos bajo 900px. El breakpoint sube de 520 a 900, el del resto del tema."
```

---

### Task 5: El titular letra a letra

**Files:**
- Modify: `src/themes/hypr.choreography.ts` (la `RECETA`, L~88-95; gesto nuevo al final)
- Modify: `src/themes/themes.css` (herencia del degradado por glifo)

**Interfaces:**
- Consumes: el mecanismo `.is-lit` existente (`hypr.choreography.ts:161-169`: un ScrollTrigger por
  escena a `top 90%` que añade la clase, más una red por posición).
- Produces: nodos `.contacto-title-glyphs` (contenedor, `aria-hidden`) y `.contacto-glyph` (uno por
  letra), cada uno con `.hypr-cut` y su propio `--hypr-d`.

**Por qué CSS y no una timeline de GSAP.** La primera versión de este plan disparaba los glifos con
un ScrollTrigger propio a `top 82%`. Está mal: `is-lit` se dispara a `top 90%`, así que la cinta
habría entrado **antes** que el titular — justo al revés de lo diseñado. Los glifos van al mismo
mecanismo que todo lo demás, que además es lo que el propio fichero se impone en su comentario del
gesto 1: *"el CSS sigue siendo la fuente de los tiempos"*. Se ahorra una timeline, un ScrollTrigger
y su limpieza.

- [x] **Step 1: Sacar `.contacto-title` de la receta**

En `src/themes/hypr.choreography.ts`, la fila de la `RECETA`:

```ts
    [".display-xl, .display-lg, .contacto-title, .about-name", "hypr-up"],
```
pasa a:
```ts
    // `.contacto-title` sale de aqui: recibe su propio gesto letra a letra. Si
    // se queda, `hypr-up` le pone opacity 0 y translateY(14px) a la vez que
    // sus glifos hacen su clip-path — dos gestos peleando por el mismo nodo.
    [".display-xl, .display-lg, .about-name", "hypr-up"],
```

- [x] **Step 2: Trocear el titular**

Justo después del bucle de la `RECETA` en `hyprChoreography` (para que el troceo no reciba las
clases genéricas):

```ts
  // Gesto 0c — el titular de cierre, letra a letra.
  // El corte horizontal por glifo NO es un gesto nuevo: es el mismo que
  // `.hero-name-word` usa para encender el nombre al abrir el sitio. La escena
  // que cierra cita a la que abre en vez de estrenar un verbo.
  const titulo = root.querySelector<HTMLElement>('[data-scene="contacto"] .contacto-title');

  if (titulo && !titulo.querySelector(".contacto-title-glyphs")) {
    const texto = titulo.textContent ?? "";
    // Ocho <span> de una letra hacen que un lector de pantalla DELETREE
    // "H-a-b-l-e-m-o-s". El arbol troceado se oculta y el texto real va en el
    // aria-label del h2. Esto es distinto de `.hero-name-word`, que trocea por
    // PALABRA: a nivel de palabra el lector concatena sin problema.
    titulo.setAttribute("aria-label", texto);
    const caja = document.createElement("span");
    caja.className = "contacto-title-glyphs";
    caja.setAttribute("aria-hidden", "true");
    // Array.from y no split(""): parte por punto de codigo, no por unidad
    // UTF-16, asi que un caracter fuera del plano basico no se rompe en dos.
    Array.from(texto).forEach((ch, i) => {
      const glifo = document.createElement("span");
      glifo.className = "contacto-glyph hypr-cut";
      glifo.textContent = ch;
      // 140ms de cabeza (el kick ya ha entrado) y 70 de escalon por letra.
      glifo.style.setProperty("--hypr-d", `${140 + i * 70}ms`);
      caja.appendChild(glifo);
    });
    titulo.replaceChildren(caja);
  }
```

El guard `!titulo.querySelector(...)` es lo que impide que un remonte (el HMR de Vite recargando
este módulo) trocee un titular ya troceado y deje 64 glifos.

- [x] **Step 3: Hacer que el degradado sobreviva al troceo**

En `src/themes/themes.css`, junto al bloque del titular (L1314-1332):

```css
/*
  Al transformar o recortar un <span> hijo, este sale del pintado del padre y
  el `background-clip: text` del padre deja de alcanzarlo: la letra se pintaria
  transparente sobre nada, es decir, desapareceria. Los glifos heredan el
  degradado, igual que ya hace `.hero-name-word`. Como es `fixed` se ancla al
  viewport y no a la caja, asi que los ocho trozos ensenan ocho rebanadas de
  UNO continuo, no ocho degradados cortados.
*/
:root[data-theme="hyprland"] .contacto-title-glyphs,
:root[data-theme="hyprland"] .contacto-glyph {
  background: inherit;
  -webkit-background-clip: inherit;
  background-clip: inherit;
}
:root[data-theme="hyprland"] .contacto-glyph {
  display: inline-block;
}
```

- [x] **Step 4: Verificar que ninguna letra desapareció**

```bash
npm run build
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=hyprland', wait_until='domcontentloaded')
    pg.wait_for_timeout(9000)
    pg.evaluate(\"document.querySelector('[data-scene=\\\"contacto\\\"]').scrollIntoView()\")
    pg.wait_for_timeout(3000)
    print(pg.evaluate('''() => {
      const g = [...document.querySelectorAll(\".contacto-glyph\")];
      return {n: g.length,
              anchos: g.map(x => Math.round(x.getBoundingClientRect().width)),
              retardos: g.map(x => x.style.getPropertyValue(\"--hypr-d\")),
              clips: g.map(x => getComputedStyle(x).clipPath),
              aria: document.querySelector(\".contacto-title\").getAttribute(\"aria-label\")};
    }'''))
    pg.screenshot(path='/tmp/titulo-glifos.png')
    b.close()
"
```
Esperado: `n: 8`, ocho anchos mayores que 0, retardos de `140ms` a `630ms` de 70 en 70, todos los
`clips` ya asentados (la escena está encendida) y `aria: 'Hablemos'`.
**Mira `/tmp/titulo-glifos.png`:** el degradado tiene que leerse continuo de la H a la s. Si se ven
ocho rebanadas cortadas, el `background: inherit` no está funcionando y hay que repetir el
degradado literal en `.contacto-glyph` antes de seguir.

- [x] **Step 5: Commit**

```bash
git add src/themes/hypr.choreography.ts src/themes/themes.css
git commit -m "feat(contacto): el titular de cierre enciende letra a letra

Mismo corte horizontal con el que el hero enciende el nombre al abrir: 420ms
--hard, escalon de 70. Los glifos heredan el degradado recortado al texto,
porque un hijo transformado sale del pintado del padre y se volveria invisible.
El arbol troceado va aria-hidden con el texto real en aria-label: ocho spans de
una letra hacen que un lector de pantalla deletree la palabra."
```

---

### Task 6: La entrada de la cinta

**Files:**
- Modify: `src/themes/themes.css` (gramática de revelado, L1786-1835)
- Modify: `src/themes/hypr.choreography.ts` (`RECETA`)

**Interfaces:**
- Consumes: la `RECETA` y el mecanismo `.is-lit` existentes.
- Produces: clases `.hypr-cut-h` y `.hypr-cut-v`.

- [x] **Step 1: Leer cómo se aplica `.is-lit`**

```bash
grep -n 'is-lit' src/themes/hypr.choreography.ts | head -20
```
Sigue ese mismo mecanismo. No inventes uno nuevo.

- [x] **Step 2: Añadir los dos ejes que faltan**

En `src/themes/themes.css`, junto a `.hypr-cut` / `.hypr-up` / `.hypr-rule`:

```css
/*
  Dos ejes con dos sentidos. `.hypr-cut` abre en horizontal porque se usa en
  palabras, que se leen de izquierda a derecha. `.hypr-cut-v` sube desde el
  borde inferior porque se usa en la cinta, que es de donde viene una barra de
  estado. `.hypr-rule` es vertical (scaleY); `.hypr-cut-h` es su gemela
  horizontal, para filetes que cruzan la pantalla.
*/
:root[data-theme="hyprland"] .hypr-cut-h {
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.5s var(--hard);
  transition-delay: var(--hypr-d, 0ms);
}
:root[data-theme="hyprland"] .is-lit .hypr-cut-h {
  transform: scaleX(1);
}
:root[data-theme="hyprland"] .hypr-cut-v {
  clip-path: inset(0 0 100% 0);
  transition: clip-path 0.42s var(--hard);
  transition-delay: var(--hypr-d, 0ms);
}
:root[data-theme="hyprland"] .is-lit .hypr-cut-v {
  /* -30% por abajo y no 0: a 0 el recorte cortaria el filete de reposo y el
     anillo de foco, que viven en el borde inferior de la banda. */
  clip-path: inset(0 0 -30% 0);
}
```

Y súmalas al bloque de `prefers-reduced-motion` que ya existe (L1824-1832), junto a `.hypr-cut`,
`.hypr-up` y `.hypr-rule`:

```css
  :root[data-theme="hyprland"] .hypr-cut-h,
  :root[data-theme="hyprland"] .hypr-cut-v,
```

- [x] **Step 3: Cambiar las dos filas de la receta**

En `hypr.choreography.ts`:

```ts
    // El estado y las vias cambian de familia: dejan de "asentarse" (900ms
    // slow) y pasan a "encenderse" (420ms hard), que es lo que hace una barra
    // de estado. Y de eje: suben desde el borde en vez de deslizar en Y.
    [".contacto-estado", "hypr-cut-v"],
    ['[class*="contacto-bar--"]', "hypr-cut-v"],
```

- [x] **Step 4: Escribir el horario explícito de la escena de cierre**

El contador genérico de la `RECETA` reparte `n * 70ms` por orden de aparición, lo que dejaría el
lead en 70ms y las vías pegadas al titular. La escena de cierre tiene un horario propio, así que se
sobreescribe justo después del bucle de la receta y **después** del troceo del titular (Task 5):

```ts
  // Gesto 0d — el horario de la escena de cierre.
  // Un solo sentido, de izquierda a derecha, y dos ejes con dos sentidos: el
  // titular abre en horizontal porque es una palabra que se lee; la cinta sube
  // desde el borde inferior porque es de donde viene una barra de estado.
  // El dato de contacto entra ANTES que el estado a proposito: lo que importa
  // es el correo. El estado remata donde la luz del filete acabo su viaje.
  const cierre = root.querySelector<HTMLElement>('[data-scene="contacto"]');
  if (cierre) {
    const HORARIO: ReadonlyArray<readonly [string, number]> = [
      [".hero-kick", 0],
      [".contacto-lead", 760],
      [".contacto-estado", 900],
    ];
    for (const [selector, ms] of HORARIO) {
      const nodo = cierre.querySelector<HTMLElement>(selector);
      nodo?.style.setProperty("--hypr-d", `${ms}ms`);
    }
    Array.from(cierre.querySelectorAll<HTMLElement>('[class*="contacto-bar--"]')).forEach(
      (via, i) => {
        via.style.setProperty("--hypr-d", `${1040 + i * 70}ms`);
      },
    );
  }
```

El filete es un pseudo-elemento de `.contacto-bars` y no puede llevar clase propia, así que su
retardo va en la hoja, en el bloque de la Task 2:

```css
  :root[data-theme="hyprland"] .contacto-bars::before {
    transform: scaleX(0);
    transition: transform 0.5s var(--hard);
    transition-delay: 900ms;
  }
  :root[data-theme="hyprland"] .is-lit .contacto-bars::before {
    transform: scaleX(1);
  }
```
Y en el bloque de `prefers-reduced-motion`, con `transform: none; transition: none;`, porque un
pseudo-elemento no lo cubre el selector de clases de la gramática.

- [x] **Step 5: Comprobar que en reposo todo queda asentado sin `is-lit`**

```bash
npm run build
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    ctx = b.new_context(viewport={'width':1440,'height':900}, reduced_motion='reduce')
    pg = ctx.new_page()
    pg.goto('http://localhost:4173/?theme=hyprland', wait_until='domcontentloaded')
    pg.wait_for_timeout(6000)
    pg.evaluate(\"document.querySelector('[data-scene=\\\"contacto\\\"]').scrollIntoView()\")
    pg.wait_for_timeout(2500)
    print(pg.evaluate('''() => {
      const n = [...document.querySelectorAll(\"[class*=contacto-bar--]\")];
      return {glifos: document.querySelectorAll(\".contacto-glyph\").length,
              clips: n.map(x => getComputedStyle(x).clipPath),
              visibles: n.map(x => x.getBoundingClientRect().height > 40)};
    }'''))
    pg.screenshot(path='/tmp/cinta-reduce.png')
    b.close()
"
```
Esperado: `glifos: 0` (bajo `reduce` la coreografía no corre y el titular ni se trocea), todos los
`clips` en `none` y todos los `visibles` en `true`. **Mira la captura:** la escena tiene que verse
completa y legible, sin ninguna pieza a medio revelar.

- [x] **Step 6: Commit**

```bash
git add src/themes/themes.css src/themes/hypr.choreography.ts
git commit -m "feat(contacto): la cinta se enciende en vez de asentarse

Dos clases nuevas en la gramatica: hypr-cut-h para filetes que cruzan y
hypr-cut-v para lo que sube desde el borde. El estado y las cuatro vias cambian
de familia (900ms slow a 420ms hard) y de eje. Las dos entran en el bloque de
prefers-reduced-motion."
```

---

### Task 7: El gate

**Files:**
- Modify: `scripts/measure-contacto.py` (si sus aserciones dan por buena la composición vieja)
- Modify: `scripts/verify-baseline.json` (solo si esta tarea arregla un fallo que estaba en la base)

- [x] **Step 1: Build y lint**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
```
Esperado: cero errores de TypeScript, cero de ESLint. Un `tsc` roto no es DONE.

- [x] **Step 2: Los arneses que ya existen**

```bash
python3 scripts/measure-contacto.py --base http://localhost:4173
python3 scripts/measure-contacto-matriz.py --base http://localhost:4173
python3 scripts/measure-type-scale.py --base http://localhost:4173
```
`measure-contacto.py` y `measure-contacto-matriz.py` fueron escritos contra la composición vieja:
si fallan por eso, **actualiza sus aserciones**, no las borres. `measure-type-scale.py` tiene que
pasar sin excepciones nuevas: los dos `clamp()` ya no existen.

- [x] **Step 3: Comprobar que Vice y Caelestia no se han movido**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for tema in ['vice','caelestia']:
        pg = b.new_page(viewport={'width':1440,'height':900})
        pg.goto(f'http://localhost:4173/?theme={tema}', wait_until='domcontentloaded')
        pg.wait_for_timeout(9000)
        pg.evaluate(\"document.querySelector('[data-scene=\\\"contacto\\\"]').scrollIntoView()\")
        pg.wait_for_timeout(2500)
        pg.screenshot(path=f'/tmp/contacto-{tema}.png')
        pg.close()
    b.close()
"
```
Compara las dos capturas contra las mismas tomadas desde `main` en otro worktree. **Nunca uses
`git stash` para esto:** un `stash --include-untracked` ya se llevó por delante una sesión entera.

- [x] **Step 4: El arnés general**

```bash
python3 scripts/verify.py
```
Esperado: salida 0 contra `scripts/verify-baseline.json`. Si esta tarea **arregla** un fallo que
estaba en la base, la base tiene que encogerse o el arnés sale 1 a propósito:
```bash
python3 scripts/verify.py --update-baseline    # y revisa el diff antes de commitear
```

- [x] **Step 5: Cerrar el estado del spec**

En `docs/superpowers/specs/2026-08-13-hyprland-contacto-cinta-design.md`, `Estado:` pasa de
`pendiente de plan` a `implementado`, y se marcan las casillas de `## Criterios de aceptación`.
`check_spec_plan_consistency()` de `verify.py` falla si el spec dice `implementado` con pasos de
este plan sin marcar.

- [x] **Step 6: Actualizar PROGRESS.json y commitear**

```bash
git add scripts/ docs/superpowers/specs/2026-08-13-hyprland-contacto-cinta-design.md PROGRESS.json
git commit -m "test(contacto): gate de la cinta y cierre del spec

Arneses actualizados a la composicion nueva, contraste medido por glifo,
Vice y Caelestia comprobadas sin cambios."
```

- [ ] **Step 7: Los dos gates críticos**

Lanza `lidia-naive-tester` (flujo y primera impresión) y `vera-art-director` (ejecución visual)
contra el build servido, con `?theme=hyprland`, escritorio y móvil. **En el brief de los dos, di
explícitamente que no editen ningún fichero**: estos subagentes llevan `Write`/`Edit` y los usan
por su cuenta si no se les prohíbe.

---

## Notas de ejecución

- **El parche de la especialista de UX** está en
  `/tmp/claude-0/-home-aoshi-proyectos-portfolio-aoshi/dce7bfb8-f5d8-424f-b6c9-196617196d59/scratchpad/ux-agent-propuesta.patch`.
  No se aplica tal cual: propone clonar un nodo de estado en `contacto.ts` que este plan no
  necesita, y un `<wbr>` en el correo que **está medido como perjudicial** (con él, Chromium parte
  la dirección en dos renglones aunque la cadena pida 248px y la caja dé 335; sin él, un renglón).
  Sirve como referencia para el `overflow-wrap` y para los valores de foco.
- **Los arneses salen verdes con el resultado roto.** Cada tarea tiene un paso de mirar la captura
  a propósito: es lo que caza lo que los números no.
