# El cartel de obra en Hyprland — Plan de implementación

> **Para trabajadores agénticos:** SUB-SKILL OBLIGATORIA: usa
> `superpowers:subagent-driven-development` (recomendado) o
> `superpowers:executing-plans` para ejecutar este plan tarea a tarea. Los pasos usan
> casillas (`- [ ]`) para el seguimiento. **Marca cada casilla en el momento**, no al
> final: `.claude/rules/speckit-progress-tracking.md`.

**Objetivo:** sustituir la tira de exposición de la obra en Hyprland por un cartel de cinco
titulares, con la captura a la altura de su titular que crece con GSAP Flip al pulsarla.

**Arquitectura:** patrón **aditivo**, el mismo que usó la placa. `projectScene.ts` gana nodos
nuevos que nacen con `display: none` para los tres temas; sólo el bloque Hyprland de `themes.css`
los enciende. El comportamiento vive en un componente propio con `destroy()`
(`src/components/obraCartel.ts`), montado sólo si `theme.id === "hyprland"`, siguiendo el
precedente de `hyprIgnition.ts` — **no** en `hypr.choreography.ts`, cuyo contrato `Choreography`
devuelve `void` y no tiene forma de limpiar listeners.

**Stack:** Vite 8 · TypeScript estricto · Tailwind 4 · GSAP 3.15 (`Flip`, `SplitText`,
`CustomEase` — todos presentes en `node_modules/gsap/`, ninguno requiere Club desde 3.13) ·
`simple-icons` vía `src/utils/icons.ts` · Playwright para los arneses.

**Spec:** `docs/superpowers/specs/2026-08-10-hyprland-obra-cartel-design.md`
**Prototipos aprobados:** `.superpowers/brainstorm/2704850-1786371390/content/obra-titular-z9.html`
(escritorio) y `obra-movil-m5.html` (móvil y tableta).

---

## Restricciones globales

Se aplican a **todas** las tareas.

- **Solo Hyprland.** Todo selector nuevo va bajo `:root[data-theme="hyprland"]`. Vice está cerrado
  (2026-08-05) y Caelestia debe quedar idéntico.
- **`src/data/content.ts` no cambia.** Ninguna cadena se inventa ni se reescribe.
- **`src/style.css` no se edita.** Su tratamiento de galería se anula localmente; Vice depende de él.
- **Nada de `gsap.from`.** Siempre `fromTo` con los dos extremos escritos a mano, y
  `Array.from(...)` para materializar colecciones vivas.
- **Nada de `any`.** `strict` está activo; usar `unknown` + guardas.
- **Nada de `clamp()` continuo sobre tokens de escala.** Escalonar en discreto con `@media`,
  cambiando de token. Escala cerrada: 12 / 16 / 21.33 / 28.43 / 37.9 / 50.52 / 67.4 / 89.85 /
  119.77 / 159.66 px.
- **Nada de opacidad para presentar o retirar contenido.** Recorte (`clip-path`) o relevo. La
  opacidad sólo se admite en el canto de brasa, que es una fuente de luz.
- **Dos curvas y ninguna más:** `--hard` `cubic-bezier(0.7,0,0.2,1)` y `--slow`
  `cubic-bezier(0.16,0.84,0.28,1)`. Se registran con `CustomEase` como `"hard"` y `"slow"`.
  **Única excepción, decidida por Aoshi el 2026-08-10:** la barra del barrido de entrada va con
  `ease: "none"`. El movimiento uniforme no es una curva de carácter — es el requisito de un
  barrido del que se derivan otros tiempos. El retardo de cada letra sale de `(x / ancho) × 1,05 s`,
  que es un mapeo lineal: si la barra acelerase, dejaría de estar donde la letra cree que está y
  el gesto se partiría en dos. La alternativa (curvar la barra y derivar los retardos con esa misma
  curva) es más código, más frágil y visualmente equivalente.
- **`--l1` significa una sola cosa:** esta pieza está activa.
- **Nada de `console.log`.** Sólo `console.error` justificado.
- **Sin pin de ScrollTrigger nuevo.** El cartel no es scrubbed.
- **`data-scene="obra"` se queda donde está.** Es como el sitio marca sus secciones.
- **Cero emojis** en código, commits y documentación.
- **Un commit por tarea**, en español, formato `tipo(scope): descripción`.

---

## Mapa de ficheros

| Fichero | Qué hace | Tarea |
|---|---|---|
| `src/sections/obra/projectScene.ts` | **Modificar.** Añade los nodos del cartel: `[data-obra-mini]`, `[data-obra-marcas]` y el `<button data-obra-abrir>` hermano del título. | 1, 5 |
| `src/utils/stackIcons.ts` | **Crear.** Mapa nombre de `stack` → slug de `simple-icons`. Aislado para que se pueda probar y ampliar sin tocar la escena. | 5 |
| `src/style.css` | **Modificar (sólo añadir).** Reglas base que dejan los nodos nuevos ocultos y neutralizan el `<button>` en Vice/Caelestia. | 1 |
| `src/themes/themes.css` | **Modificar.** Retira el bloque `LA TIRA DE EXPOSICION` y añade el bloque `EL CARTEL`. | 2, 4, 6, 7 |
| `src/themes/hypr.choreography.ts` | **Modificar.** Retira el Gesto 2 (`is-open` por `pointerenter`). | 2 |
| `src/components/obraCartel.ts` | **Crear.** Todo el comportamiento: entrada, relevo, apertura con Flip, teclado. Devuelve `{ destroy() }`. | 3, 4, 7, 8 |
| `src/main.ts` | **Modificar.** Monta el cartel si `theme.id === "hyprland"` y lo destruye en `pagehide`. | 3 |
| `scripts/measure-cartel.py` | **Crear.** Arnés Playwright del cartel. Cada tarea le añade aserciones. | 1-8 |
| `.claude/rules/verification.md` | **Modificar.** Documenta cómo se lanza el arnés nuevo. `verify.py` no invoca los `measure-*`, así que no hay integración que tocar. | 9 |
| `docs/superpowers/specs/2026-08-10-hyprland-obra-cartel-design.md` | **Modificar.** Corrige el apartado de marcas del stack. | 5 |

---

## Task 1: Los nodos del cartel, invisibles en los tres temas

**Ficheros:**
- Modificar: `src/sections/obra/projectScene.ts`
- Modificar: `src/style.css` (sólo añadir al final)
- Crear: `scripts/measure-cartel.py`

**Interfaces:**
- Consume: `CaseStudy` de `src/data/content.ts`, `el()` de `src/utils/dom.ts`.
- Produce: los ganchos `[data-obra-mini]` (un `<figure>` con `<img>` y `<figcaption>`),
  `[data-obra-marcas]` (un `<div>` vacío que rellena la Task 5) y
  `[data-obra-abrir]` (un `<button>` vacío, **hermano** del `<h2>`; su nombre accesible lo pone
  la Task 3).

**Por qué esta tarea existe sola:** el patrón aditivo del proyecto se ha roto cuatro veces por
olvidar el `display: none` de base (nota en `scripts/measure-placa.py`). Los nodos entran y se
comprueba que **no cambian nada** antes de que ningún tema los encienda.

- [ ] **Paso 1: Escribir el arnés que falla**

Crea `scripts/measure-cartel.py`:

```python
"""Arnes del cartel de obra en Hyprland.

Las aserciones nacen de fallos reales, como en `measure-placa.py`:
  1. Los nodos del cartel existen en el DOM y estan OCULTOS en Vice y en
     Caelestia. El patron aditivo se ha roto cuatro veces por olvidar el
     `display: none` de base.
  2. Hay CINCO disparadores y los cinco titulares conservan su texto. Un
     `querySelectorAll` vacio hace que el bucle de comprobacion no itere y
     el arnes salga verde sin comprobar nada: eso paso en la primera
     version de este mismo fichero.
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

TEMAS_AJENOS = ["vice", "caelestia"]


def abre(pg, base: str, tema: str) -> None:
    pg.goto(f"{base}/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(4000)


def nodos_ocultos(pg) -> list[str]:
    return pg.evaluate(
        """() => {
          const fallos = [];
          for (const sel of ['[data-obra-mini]', '[data-obra-marcas]']) {
            const nodos = Array.from(document.querySelectorAll(sel));
            if (nodos.length !== 5) { fallos.push(`${sel}: ${nodos.length} nodos, esperaba 5`); }
            for (const n of nodos) {
              if (getComputedStyle(n).display !== 'none') { fallos.push(`${sel} visible`); break; }
            }
          }
          return fallos;
        }"""
    )


def titulo_intacto(pg) -> list[str]:
    """El titular sigue diciendo lo que dice `content.ts` despues de que el
    tema lo parta en caracteres, y hay CINCO disparadores.

    El conteo no es decorativo: sin el, un `querySelectorAll` que devuelve 0
    hace que el bucle no itere, no se empuje ningun fallo y el arnes salga
    verde sin haber comprobado nada. Es el modo de fallo que destapo la
    revision de la Task 1.
    """
    return pg.evaluate(
        """() => {
          const fallos = [];
          const botones = document.querySelectorAll('[data-obra-abrir]');
          if (botones.length !== 5) fallos.push(`${botones.length} disparadores, esperaba 5`);
          const titulos = Array.from(document.querySelectorAll('[data-scene="obra"] h2.display-lg'));
          if (titulos.length !== 5) fallos.push(`${titulos.length} titulares, esperaba 5`);
          for (const t of titulos) {
            const texto = (t.textContent || '').trim();
            if (!texto) fallos.push('titular sin texto tras el split de caracteres');
          }
          return fallos;
        }"""
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://localhost:4173")
    args = p.parse_args()
    fallos: list[str] = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        for tema in TEMAS_AJENOS:
            abre(pg, args.base, tema)
            fallos += [f"[{tema}] {f}" for f in nodos_ocultos(pg)]
            fallos += [f"[{tema}] {f}" for f in titulo_intacto(pg)]
        b.close()
    for f in fallos:
        print(f"FALLO {f}")
    print(f"{len(fallos)} fallos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Paso 2: Ejecutarlo y ver que falla**

```bash
npm run build && npx vite preview --port 4173 &
sleep 4
python3 scripts/measure-cartel.py
```
Esperado: FALLA con `[vice] [data-obra-mini]: 0 nodos, esperaba 5`.

- [ ] **Paso 3: Añadir los nodos en `projectScene.ts`**

Dentro de `createProjectScene`, antes de construir `children`:

```ts
  // El cartel de Hyprland necesita UNA captura por proyecto, no el carril
  // arrastrable: `gallery.ts` construye un carril y aqui hace falta un solo
  // nodo que pueda viajar con Flip. Nace oculto para los tres temas
  // (`style.css`) y solo el bloque Hyprland lo enciende.
  const mini = el("figure", "obra-mini", []);
  mini.setAttribute("data-obra-mini", "");
  const primera = project.gallery[0];
  if (primera) {
    const shot = el("img", "obra-mini-img") as HTMLImageElement;
    shot.src = primera.src;
    shot.alt = primera.caption;
    shot.loading = "lazy";
    shot.decoding = "async";
    mini.append(shot, el("figcaption", "obra-mini-pie", [primera.caption]));
  }

  // Las marcas del stack las rellena `stackIcons.ts` en la Task 5.
  const marcas = el("div", "obra-marcas", []);
  marcas.setAttribute("data-obra-marcas", "");
  marcas.setAttribute("aria-hidden", "true");
```

Y el disparador accesible, que va **como hermano del `<h2>`, nunca dentro**. El `<h2>` conserva
su texto y sus atributos tal y como están hoy: no se toca.

**Por qué fuera y no dentro** (medido, no deducido): `src/utils/reveal.ts:19` y
`src/themes/vice.choreography.ts:32` parten el titular en caracteres haciendo
`target.textContent = ""` sobre `[data-title]`. Caelestia no declara `choreography` propia, así que
cae en las recetas genéricas de `reveal.ts`; Vice usa su propio `splitChars`. Un `<button>` anidado
en ese `<h2>` **se borra del DOM en los dos temas** a los pocos ms de cargar. Hyprland se salva
porque tiene coreografía propia, pero el gancho no puede depender de eso. Blindar el split queda
descartado: obligaría a editar `vice.choreography.ts`, y **Vice está cerrado**.

```ts
  // El disparador va FUERA del <h2>. Dentro no sobrevive: `reveal.ts` (que es
  // lo que usa Caelestia) y `vice.choreography.ts` parten el titular con
  // `target.textContent = ""` y se llevarian el boton por delante. En Hyprland
  // este boton cubre la fila entera; en los otros dos temas no existe.
  const abrir = el("button", "obra-abrir", []);
  abrir.setAttribute("data-obra-abrir", "");
  abrir.type = "button";
  // El nombre accesible lo pone el modulo del cartel (Task 3), que es quien
  // conoce el titulo ya partido en letras.
```

Añade `mini`, `marcas` y `abrir` a `children`, detrás de `columns`.

- [ ] **Paso 4: Neutralizar los nodos nuevos en `src/style.css`**

Al final del fichero:

```css
/*
 * Nodos del cartel de obra (`projectScene.ts`). Nacen apagados para los TRES
 * temas: solo el bloque Hyprland de `themes.css` los enciende. El patron
 * aditivo se ha roto cuatro veces por olvidar justo esto.
 *
 * `.obra-abrir` es HERMANO del <h2>, no hijo: dentro lo borraria el split de
 * caracteres de `reveal.ts` (Caelestia) y de `vice.choreography.ts`, que hacen
 * `target.textContent = ""`. Estando fuera basta con ocultarlo, y ademas no
 * hay que pelear con el `appearance` del agente de usuario.
 */
.obra-mini,
.obra-marcas,
.obra-abrir {
  display: none;
}
```

- [ ] **Paso 5: Ejecutar el arnés y verlo pasar**

```bash
npm run build && python3 scripts/measure-cartel.py
```
Esperado: `0 fallos`.

- [ ] **Paso 6: Confirmar que Vice y Caelestia no se han movido**

```bash
git worktree add /tmp/cartel-base HEAD~1
```
Levanta los dos y compara capturas de `?theme=vice` y `?theme=caelestia` a 1440×900.
**Nunca `git stash`**: un `stash --include-untracked` ya se llevó una sesión entera por delante.

- [ ] **Paso 7: Commit**

```bash
git add src/sections/obra/projectScene.ts src/style.css scripts/measure-cartel.py
git commit -m "feat(obra): nodos del cartel, ocultos en los tres temas"
```

---

## Task 2: El cartel en reposo

**Ficheros:**
- Modificar: `src/themes/themes.css` (retirar el bloque `LA TIRA DE EXPOSICION`, añadir `EL CARTEL`)
- Modificar: `src/themes/hypr.choreography.ts` (retirar el Gesto 2)
- Modificar: `scripts/measure-cartel.py`

**Interfaces:**
- Consume: los ganchos de la Task 1 y los que ya existen en `projectScene.ts`
  (`[data-ord]`, `.hero-kick`, `h2.display-lg`, `.scene-surface`, `[data-gallery]`).
- Produce: la fila en reposo. Clase de estado `is-abierto` en `[data-scene="obra"]`, que consume la
  Task 4.

**Las dos cosas van juntas** porque no pueden convivir: el Gesto 2 pone `is-open` por
`pointerenter` sobre los mismos nodos que el cartel usa para otra cosa.

- [ ] **Paso 1: Añadir las aserciones que fallan**

En `measure-cartel.py`, añade y llama desde `main()` con `--base` y tema `hyprland`:

```python
ESCALA = [12, 16, 21.33, 28.43, 37.9, 50.52, 67.4, 89.85, 119.77, 159.66]


def cartel_en_reposo(pg) -> list[str]:
    """El cartel se VE, las cinco filas caben, y la miniatura mide lo que las letras.

    Sin la primera comprobacion el arnes sale verde con el cartel apagado: los
    nodos existen en el DOM desde la Task 1, asi que contarlos no prueba nada.
    """
    return pg.evaluate(
        """() => {
          const fallos = [];
          const filas = Array.from(document.querySelectorAll('[data-scene="obra"]'));
          if (filas.length !== 5) return [`${filas.length} filas, esperaba 5`];
          const vp = window.innerHeight;
          for (const f of filas) {
            const r = f.getBoundingClientRect();
            if (r.height < 40) fallos.push('fila sin alto: el cartel no esta encendido');
            const t = f.querySelector('h2.display-lg');
            const m = f.querySelector('[data-obra-mini]');
            if (!t || !m) { fallos.push('falta titulo o miniatura'); continue; }
            const tr = t.getBoundingClientRect(), mr = m.getBoundingClientRect();
            // La miniatura mide EXACTAMENTE la caja del titulo: 2px de holgura
            // por redondeo de subpixel, ni uno mas.
            if (Math.abs(mr.height - tr.height) > 2) {
              fallos.push(`miniatura ${Math.round(mr.height)}px vs titulo ${Math.round(tr.height)}px`);
            }
            if (Math.abs((mr.top + mr.height / 2) - (tr.top + tr.height / 2)) > 3) {
              fallos.push('miniatura desalineada del titulo');
            }
            // El titulo NUNCA se corta: es el defecto que retira el acordeon.
            if (t.scrollWidth > t.clientWidth + 1) fallos.push('titulo recortado');
          }
          const total = filas[4].getBoundingClientRect().bottom - filas[0].getBoundingClientRect().top;
          if (total > vp) fallos.push(`las 5 filas miden ${Math.round(total)}px en un viewport de ${vp}`);
          return fallos;
        }"""
    )


def escala_tipografica(pg) -> list[str]:
    return pg.evaluate(
        """(escala) => {
          const fallos = [];
          const nodos = document.querySelectorAll('[data-scene="obra"] h2.display-lg, [data-scene="obra"] .hero-kick');
          for (const n of nodos) {
            const px = parseFloat(getComputedStyle(n).fontSize);
            if (!escala.some(p => Math.abs(p - px) < 0.6)) {
              fallos.push(`${n.className}: ${px}px fuera de la escala`);
            }
          }
          return fallos;
        }""",
        ESCALA,
    )
```

- [ ] **Paso 2: Ejecutarlo y ver que falla**

```bash
npm run build && python3 scripts/measure-cartel.py
```
Esperado: FALLA con `miniatura 0px vs titulo ...` (sigue oculta) y con las filas del acordeón.

- [ ] **Paso 3: Retirar el Gesto 2 de `hypr.choreography.ts`**

Borra el bloque completo `mm.add("(min-width: 821px) and (prefers-reduced-motion: no-preference)", …)`
que reparte `--hypr-e`, engancha `pointerenter`/`focusin` y pone `is-open`. Deja el Gesto 1
(`is-lit`, con su red por posición) y el Gesto 3 (la luz del titular), que el cartel sigue usando.
Si `mm` se queda sin usos, retira también `const mm = gsap.matchMedia()` — `tsc` fallará si no.

- [ ] **Paso 4: Retirar el bloque `LA TIRA DE EXPOSICION` de `themes.css`**

Borra el bloque entero, incluido su `@media (max-width: 820px), (prefers-reduced-motion: reduce)`
de degradación a pila. **No borres** las reglas de la placa que están justo encima ni el disparador
que está justo debajo.

- [ ] **Paso 5: Escribir el bloque `EL CARTEL`**

En su lugar:

```css
/*
  EL CARTEL — el dispositivo de la obra en Hyprland.

  Cinco titulares a tamano de cartel, siempre en pantalla. La tipografia ES el
  dispositivo: no hay tarjetas, ni cajas, ni radio. Sustituye a la tira de
  exposicion, que repetia el gesto de la hoja de contactos y abandonaba el
  patron bajo 821px.

  `.scene-surface` pasa a `display: contents` para que los hijos de la ficha
  participen directamente en la rejilla de la fila sin restructurar el DOM que
  comparten los tres temas. Solo aqui: en Caelestia sigue siendo la tarjeta.
*/
:root[data-theme="hyprland"] .obra-rail {
  border-top: 1px solid var(--rule);
  border-bottom: 1px solid var(--rule);
}
:root[data-theme="hyprland"] .obra-track {
  display: flex;
  flex-direction: column;
  transform: none;
}
:root[data-theme="hyprland"] [data-scene="obra"] {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  min-height: 0;
  padding: 0.25rem 0;
  border: 0;
  border-top: 1px solid var(--rule);
  overflow: visible;
}
:root[data-theme="hyprland"] [data-scene="obra"]:last-child {
  border-bottom: 1px solid var(--rule);
}
:root[data-theme="hyprland"] [data-scene="obra"] .scene-surface {
  display: contents;
}

/* el ordinal deja de ser telon y pasa a ser dato: `01`, y el `/ 05` es
   decorativo (el nodo ya es aria-hidden en projectScene.ts). */
:root[data-theme="hyprland"] [data-scene="obra"] [data-ord] {
  position: static;
  flex: 0 0 34px;
  align-self: flex-end;
  padding-bottom: 0.9rem;
  font-family: var(--font-display);
  font-size: var(--t-2);
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0.06em;
  color: var(--haze);
  transition: color 0.42s var(--hard);
}
:root[data-theme="hyprland"] [data-scene="obra"] [data-ord]::after {
  content: " / 05";
  color: var(--haze);
}
:root[data-theme="hyprland"] [data-scene="obra"].is-abierto [data-ord] {
  color: var(--l1);
}

:root[data-theme="hyprland"] [data-scene="obra"] h2.display-lg {
  order: 1;
  margin: 0;
  max-width: none;
  font-size: var(--t-8);
  line-height: 1.12;
  letter-spacing: -0.042em;
  white-space: nowrap;
  color: var(--haze);
}
:root[data-theme="hyprland"] [data-scene="obra"] .obra-abrir {
  /* El disparador cubre la fila entera: el objetivo tactil es la fila, no una
     palabra. Va por debajo del contenido en z para no taparlo, y sin fondo. */
  display: block;
  position: absolute;
  inset: 0;
  z-index: 0;
  appearance: none;
  margin: 0;
  padding: 0;
  border: 0;
  background: none;
  cursor: pointer;
}
:root[data-theme="hyprland"] [data-scene="obra"] .obra-abrir:focus-visible {
  outline: 2px solid var(--l1);
  outline-offset: -2px;
}
:root[data-theme="hyprland"] [data-scene="obra"] .hero-kick {
  order: 2;
  margin-left: auto;
  font-size: var(--t-1);
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: var(--haze);
}

/* el cuadro de imagen PROPIO: sin borde, sin radio, sin sombra, sin hover que
   levanta y sin rotulo en degradado encima. Nada que ver con el tratamiento
   generico de `style.css`, que se diseno para Vice. */
:root[data-theme="hyprland"] [data-scene="obra"] .obra-mini {
  display: block;
  order: 3;
  /* La miniatura mide EXACTAMENTE la caja del titulo. No se escribe el numero
     a mano: `--t-8` son 89,85px y 89,85 x 1,12 = 100,63 — el "90px" que decia
     antes este plan era un error de aritmetica, arrastrado del prototipo, que
     usaba interlinea 1. Derivarlo del token lo mantiene cuadrado solo.
     El ancho conserva la proporcion apaisada 16:10 de la captura. */
  flex: 0 0 calc(var(--t-8) * 1.12 * 1.6);
  height: calc(var(--t-8) * 1.12);
  margin: 0;
  position: relative;
  overflow: hidden;
  background: var(--shot-fondo);
  clip-path: inset(0 100% 0 0);   /* la abre el modulo, por corte */
}
:root[data-theme="hyprland"] .obra-mini-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* En una captura de aplicacion la informacion vive ARRIBA: barra de titulo y
     cabeceras. `50% 50%` recortaria justo la parte que no dice nada. */
  object-position: 50% 0%;
  filter: brightness(0.96);
}
:root[data-theme="hyprland"] .obra-mini::after {
  content: "";
  position: absolute;
  inset: 0;
  background: rgba(255, 90, 52, 0.08);
  pointer-events: none;
}
:root[data-theme="hyprland"] .obra-mini-pie {
  display: none;             /* el pie solo existe en el visor grande */
}

/* en reposo, la ficha no ocupa sitio */
:root[data-theme="hyprland"] [data-scene="obra"] .lead,
:root[data-theme="hyprland"] [data-scene="obra"] .obra-meta,
:root[data-theme="hyprland"] [data-scene="obra"] [data-mask],
:root[data-theme="hyprland"] [data-scene="obra"] [data-gallery] {
  display: none;
}
```

- [ ] **Paso 6: Ejecutar el arnés y verlo pasar**

```bash
npm run build && python3 scripts/measure-cartel.py
```
Esperado: `0 fallos`. Si «las 5 filas miden N px en un viewport de 900», baja el escalón del título
o el `padding` de la fila; **no** toques `line-height: 1.12`, del que depende el alto de la
miniatura.

- [ ] **Paso 7: Captura de verificación**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=hyprland', wait_until='domcontentloaded')
    pg.wait_for_timeout(9000)
    pg.screenshot(path='/tmp/cartel-reposo.png')
    b.close()
"
```

- [ ] **Paso 8: Commit**

```bash
git add src/themes/themes.css src/themes/hypr.choreography.ts scripts/measure-cartel.py
git commit -m "feat(obra): el cartel sustituye a la tira de exposicion en Hyprland"
```

---

## Task 3: El módulo — entrada por barrido y relevo

**Ficheros:**
- Crear: `src/components/obraCartel.ts`
- Modificar: `src/main.ts`
- Modificar: `scripts/measure-cartel.py`

**Interfaces:**
- Consume: los ganchos de las Tasks 1 y 2.
- Produce: `mountObraCartel(root: HTMLElement): ObraCartelHandle`, con
  `interface ObraCartelHandle { destroy: () => void }`. La Task 4 amplía este mismo módulo.

- [ ] **Paso 1: Añadir la aserción que falla**

```python
def relevo_es_ola(pg) -> list[str]:
    """El relevo RECORRE la palabra: a 70ms la primera letra se ha movido y la
    ultima no. Sin esta medida, un cambio simultaneo disfrazado pasaria el
    arnes. No se juzga por captura: `page.screenshot()` bloquea el compositor
    en headless y adelanta la timeline."""
    pg.eval_on_selector('[data-scene="obra"]:nth-child(2) .obra-abrir', "n => n.dispatchEvent(new PointerEvent('pointerenter', {bubbles:true}))")
    pg.wait_for_timeout(70)
    return pg.evaluate(
        """() => {
          const fila = document.querySelectorAll('[data-scene="obra"]')[1];
          const tiras = fila.querySelectorAll('.obra-rl');
          if (tiras.length < 4) return ['el titulo no esta partido en letras'];
          const y = e => new DOMMatrixReadOnly(getComputedStyle(e).transform).m42;
          const primera = y(tiras[0]), ultima = y(tiras[tiras.length - 1]);
          const fallos = [];
          if (primera >= -0.5) fallos.push('la primera letra no se ha movido a 70ms');
          if (ultima < -0.5) fallos.push('la ultima letra ya se movio: no es una ola');
          return fallos;
        }"""
    )
```

- [ ] **Paso 2: Ejecutarlo y ver que falla**

Esperado: `el titulo no esta partido en letras`.

- [ ] **Paso 3: Escribir `src/components/obraCartel.ts`**

```ts
import type { Gsap } from "../themes/choreography";

export interface ObraCartelHandle {
  destroy: () => void;
}

interface Fila {
  seccion: HTMLElement;
  boton: HTMLButtonElement;
  /** una tira por letra: arriba la apagada, debajo la encendida */
  tiras: HTMLElement[];
  /** capa de entrada, independiente de la del relevo */
  entradas: HTMLElement[];
  mini: HTMLElement;
}

const PASO_RELEVO = 0.024;
const BARRIDO = 1.05;

/**
 * El cartel: cinco titulares, la captura a la altura de su titular.
 *
 * Va aqui y no en `hypr.choreography.ts` porque el contrato `Choreography`
 * devuelve `void` y este dispositivo tiene estado y listeners que hay que
 * poder soltar. Mismo patron que `hyprIgnition.ts`.
 *
 * Cada letra lleva DOS transforms independientes: `.obra-en` para la entrada y
 * `.obra-rl` para el relevo. Sin esa separacion, la entrada y el hover se
 * pisan — se comprobo en el prototipo.
 */
export async function mountObraCartel(root: HTMLElement): Promise<ObraCartelHandle> {
  const { default: gsap } = await import("gsap");
  const { CustomEase } = await import("gsap/CustomEase");
  gsap.registerPlugin(CustomEase);
  CustomEase.create("hard", "0.7,0,0.2,1");
  CustomEase.create("slow", "0.16,0.84,0.28,1");

  const secciones = Array.from(root.querySelectorAll<HTMLElement>('[data-scene="obra"]'));
  const filas: Fila[] = secciones.map((seccion) => partirTitulo(seccion));
  const finoPuntero = window.matchMedia("(hover: hover)").matches;
  const motionReducido = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const sueltas: Array<() => void> = [];

  for (const fila of filas) {
    if (finoPuntero) {
      const entra = (): void => relevo(gsap, fila, true, motionReducido);
      const sale = (): void => relevo(gsap, fila, false, motionReducido);
      fila.seccion.addEventListener("pointerenter", entra);
      fila.seccion.addEventListener("pointerleave", sale);
      sueltas.push(() => {
        fila.seccion.removeEventListener("pointerenter", entra);
        fila.seccion.removeEventListener("pointerleave", sale);
      });
    }
  }

  if (!motionReducido) entrada(gsap, root, filas);
  else asentar(gsap, filas);

  return {
    destroy(): void {
      for (const soltar of sueltas) soltar();
      gsap.killTweensOf(filas.flatMap((f) => [...f.tiras, ...f.entradas, f.mini]));
    },
  };
}

/** Convierte el texto del boton en una letra por mirilla, con su gemela. */
function partirTitulo(seccion: HTMLElement): Fila {
  const boton = seccion.querySelector<HTMLButtonElement>("[data-obra-abrir]");
  const titulo = seccion.querySelector<HTMLElement>("h2.display-lg");
  const mini = seccion.querySelector<HTMLElement>("[data-obra-mini]");
  if (!boton || !titulo || !mini) throw new Error("Fila de obra sin boton, titulo o miniatura");

  // Se parte el TITULAR, no el boton: el boton es un hermano vacio que solo
  // hace de disparador accesible (ver Task 1).
  const texto = titulo.textContent ?? "";
  titulo.textContent = "";
  for (const caracter of texto) {
    const mirilla = document.createElement("span");
    mirilla.className = "obra-ch";
    if (caracter === " ") {
      mirilla.classList.add("obra-ch-hueco");
      titulo.appendChild(mirilla);
      continue;
    }
    const capaEntrada = document.createElement("span");
    capaEntrada.className = "obra-en";
    const tira = document.createElement("span");
    tira.className = "obra-rl";
    for (let i = 0; i < 2; i += 1) {
      const glifo = document.createElement("i");
      glifo.textContent = caracter;
      tira.appendChild(glifo);
    }
    capaEntrada.appendChild(tira);
    mirilla.appendChild(capaEntrada);
    titulo.appendChild(mirilla);
  }
  // El texto partido deja de ser legible para un lector de pantalla: se le
  // devuelve entero por `aria-label`.
  boton.setAttribute("aria-label", `Mostrar ${texto}`);

  return {
    seccion,
    boton,
    tiras: Array.from(titulo.querySelectorAll<HTMLElement>(".obra-rl")),
    entradas: Array.from(titulo.querySelectorAll<HTMLElement>(".obra-en")),
    mini,
  };
}

/** El hover no es un estado, es un recorrido. */
function relevo(gsap: Gsap, fila: Fila, encendido: boolean, reducido: boolean): void {
  gsap.killTweensOf(fila.tiras);
  gsap.to(fila.tiras, {
    yPercent: encendido ? -50 : 0,
    duration: reducido ? 0 : 0.42,
    ease: "hard",
    stagger: reducido ? 0 : { each: PASO_RELEVO, from: encendido ? "start" : "end" },
  });
}

/**
 * Entrada: UNA barra de brasa cruza el cartel y todo lo demas cuelga de ella.
 * El retardo de cada letra no se escribe a mano: sale de su posicion x real,
 * asi que la barra atraviesa los cinco titulares a la vez, por columnas.
 */
function entrada(gsap: Gsap, root: HTMLElement, filas: Fila[]): void {
  const pista = root.querySelector<HTMLElement>("[data-obra-track]");
  if (!pista) return;
  const caja = pista.getBoundingClientRect();
  const ancho = caja.width || 1;

  const barra = document.createElement("i");
  barra.className = "obra-barrido";
  barra.setAttribute("aria-hidden", "true");
  pista.appendChild(barra);

  const tl = gsap.timeline({ onComplete: () => barra.remove() });
  tl.set(barra, { opacity: 1, x: 0 })
    .to(barra, { x: ancho, duration: BARRIDO, ease: "none" }, 0)
    .to(barra, { opacity: 0, duration: 0.22, ease: "slow" }, BARRIDO);

  for (const fila of filas) {
    fila.entradas.forEach((capa) => {
      const x = capa.getBoundingClientRect().left - caja.left;
      const retardo = Math.max(0, (x / ancho) * BARRIDO);
      tl.fromTo(capa, { yPercent: 112 }, { yPercent: 0, duration: 0.46, ease: "hard" }, retardo);
    });
    const xm = fila.mini.getBoundingClientRect().left - caja.left;
    tl.fromTo(
      fila.mini,
      { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0 0 0)", duration: 0.42, ease: "hard" },
      Math.max(0, (xm / ancho) * BARRIDO),
    );
  }
}

/** Con movimiento reducido el cartel esta tejido desde el primer fotograma. */
function asentar(gsap: Gsap, filas: Fila[]): void {
  for (const fila of filas) {
    gsap.set(fila.entradas, { yPercent: 0 });
    gsap.set(fila.mini, { clipPath: "inset(0 0 0 0)" });
  }
}
```

- [ ] **Paso 4: Añadir el CSS de las letras y la barra en `themes.css`**

Dentro del bloque `EL CARTEL`:

```css
/* la mirilla por letra: arriba la apagada, debajo la encendida. `.obra-en` es
   la capa de entrada y `.obra-rl` la del relevo — dos transforms separados. */
:root[data-theme="hyprland"] .obra-ch {
  display: inline-block;
  overflow: hidden;
  height: 1.12em;
  vertical-align: top;
}
:root[data-theme="hyprland"] .obra-ch-hueco {
  width: 0.26em;
}
:root[data-theme="hyprland"] .obra-en,
:root[data-theme="hyprland"] .obra-rl {
  display: block;
}
:root[data-theme="hyprland"] .obra-rl i {
  display: block;
  height: 1.12em;
  font-style: normal;
}
:root[data-theme="hyprland"] .obra-rl i:first-child {
  color: var(--haze);
}
:root[data-theme="hyprland"] .obra-rl i:last-child {
  color: var(--color-paper);
}
:root[data-theme="hyprland"] .obra-barrido {
  position: absolute;
  top: -6px;
  bottom: -6px;
  width: 2px;
  background: var(--l1);
  box-shadow: 0 0 26px var(--l1);
  opacity: 0;
  pointer-events: none;
  z-index: 8;
}
:root[data-theme="hyprland"] .obra-track {
  position: relative;   /* ancla de la barra */
}
```

- [ ] **Paso 5: Montarlo en `src/main.ts`**

Junto a `ignitionHandle`:

```ts
let cartelHandle: { destroy: () => void } | null = null;
if (theme.id === "hyprland") {
  void import("./components/obraCartel").then(async ({ mountObraCartel }) => {
    cartelHandle = await mountObraCartel(app);
  });
}
```

Y en el listener de `pagehide`, junto a los demás: `cartelHandle?.destroy();`

- [ ] **Paso 6: Ejecutar el arnés y verlo pasar**

```bash
npm run build && npm run lint && python3 scripts/measure-cartel.py
```
Esperado: `0 fallos`.

- [ ] **Paso 7: Commit**

```bash
git add src/components/obraCartel.ts src/main.ts src/themes/themes.css scripts/measure-cartel.py
git commit -m "feat(obra): entrada por barrido y relevo de las letras del cartel"
```

---

## Task 4: La apertura con Flip

**Ficheros:**
- Modificar: `src/components/obraCartel.ts`
- Modificar: `src/themes/themes.css`
- Modificar: `scripts/measure-cartel.py`

**Interfaces:**
- Consume: `ObraCartelHandle` y `Fila` de la Task 3.
- Produce: la clase `is-abierto` en la sección elegida, los contenedores
  `[data-obra-lupa]` y `[data-obra-ficha]` creados por el módulo dentro de `.obra-track`, y la
  región `[data-obra-anuncio]` con `aria-live="polite"`.

- [ ] **Paso 1: Añadir las aserciones que fallan**

```python
def apertura(pg) -> list[str]:
    """La miniatura y la grande son EL MISMO nodo, la ficha no desborda, y la
    ficha cerrada no roba el puntero.

    Lo ultimo es un defecto medido en el prototipo: con `opacity: 0` el panel
    sigue siendo alcanzable y tapa las filas — el arnes se quedo 30s
    intentando pulsar hasta que Chrome dijo que elemento interceptaba.
    """
    fallos = pg.evaluate(
        """() => {
          const f = [];
          const ficha = document.querySelector('[data-obra-ficha]');
          if (!ficha) return ['no hay ficha'];
          if (getComputedStyle(ficha).pointerEvents !== 'none') {
            f.push('la ficha cerrada captura el puntero');
          }
          return f;
        }"""
    )
    for i in range(5):
        pg.eval_on_selector_all(
            "[data-obra-abrir]", f"ns => ns[{i}].click()"
        )
        pg.wait_for_timeout(900)
        fallos += pg.evaluate(
            """(i) => {
              const f = [];
              const secs = document.querySelectorAll('[data-scene="obra"]');
              const abierta = secs[i];
              if (!abierta.classList.contains('is-abierto')) f.push(`fila ${i}: no se abrio`);
              const lupa = document.querySelector('[data-obra-lupa]');
              const mini = abierta.querySelector('[data-obra-mini]');
              // el MISMO nodo, no una copia
              if (!lupa || mini.parentElement !== lupa) f.push(`fila ${i}: la captura no viajo a la lupa`);
              const ficha = document.querySelector('[data-obra-ficha]');
              const pista = document.querySelector('[data-obra-track]');
              const desborde = ficha.getBoundingClientRect().bottom - pista.getBoundingClientRect().bottom;
              if (desborde > 0) f.push(`fila ${i}: la ficha desborda ${Math.round(desborde)}px`);
              if (getComputedStyle(ficha).pointerEvents !== 'auto') f.push(`fila ${i}: ficha abierta sin puntero`);
              return f;
            }""",
            i,
        )
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(700)
    return fallos
```

- [ ] **Paso 2: Ejecutarlo y ver que falla**

Esperado: `no hay ficha`.

- [ ] **Paso 3: Implementar la apertura en `obraCartel.ts`**

Añade al módulo, y engancha `click` en cada `fila.boton` (más `pointerdown` en la sección para que
el objetivo táctil sea la fila entera):

```ts
  const { Flip } = await import("gsap/Flip");
  const { SplitText } = await import("gsap/SplitText");
  gsap.registerPlugin(Flip, SplitText);

  const pista = root.querySelector<HTMLElement>("[data-obra-track]");
  if (!pista) throw new Error("El cartel necesita [data-obra-track]");

  const lupa = document.createElement("div");
  lupa.className = "obra-lupa";
  lupa.setAttribute("data-obra-lupa", "");
  const ficha = document.createElement("div");
  ficha.className = "obra-ficha";
  ficha.setAttribute("data-obra-ficha", "");
  const anuncio = document.createElement("p");
  anuncio.className = "sr-only";
  anuncio.setAttribute("data-obra-anuncio", "");
  anuncio.setAttribute("aria-live", "polite");
  pista.append(lupa, ficha, anuncio);

  let abierta = -1;

  function abre(indice: number): void {
    if (abierta === indice) { cierra(); return; }
    if (abierta >= 0) { cierra(); }
    abierta = indice;
    const fila = filas[indice];
    fila.seccion.classList.add("is-abierto");
    relevo(gsap, fila, true, motionReducido);

    // La miniatura y la grande son EL MISMO nodo: Flip mide donde esta, se
    // reubica, y se anima el recorrido real entre las dos posiciones.
    const estado = Flip.getState(fila.mini);
    lupa.appendChild(fila.mini);
    Flip.from(estado, { duration: motionReducido ? 0 : 0.62, ease: "hard", absolute: true });

    const arriba = fila.seccion.offsetTop;
    filas.forEach((otra, j) => {
      const destino = j === indice ? -arriba : j < indice ? -(arriba + pista.clientHeight) : pista.clientHeight;
      gsap.to(otra.seccion, {
        y: destino,
        duration: motionReducido ? 0 : 0.62,
        ease: "hard",
        delay: motionReducido ? 0 : Math.abs(j - indice) * 0.03,
      });
    });

    ficha.replaceChildren(...bloquesDeFicha(fila.seccion));
    gsap.set(ficha, { opacity: 1, pointerEvents: "auto" });
    if (!motionReducido) {
      const partido = new SplitText(ficha.querySelectorAll("p, .obra-stack"), {
        type: "lines",
        mask: "lines",
      });
      gsap.fromTo(
        partido.lines,
        { yPercent: 110 },
        { yPercent: 0, duration: 0.42, ease: "hard", stagger: 0.045, delay: 0.24,
          onComplete: () => partido.revert() },
      );
    }
    anuncio.textContent = `${fila.boton.getAttribute("aria-label")?.replace("Mostrar ", "") ?? ""}, ficha abierta.`;
  }

  function cierra(): void {
    if (abierta < 0) return;
    const fila = filas[abierta];
    abierta = -1;
    fila.seccion.classList.remove("is-abierto");
    relevo(gsap, fila, false, motionReducido);
    const estado = Flip.getState(fila.mini);
    fila.seccion.appendChild(fila.mini);
    Flip.from(estado, { duration: motionReducido ? 0 : 0.52, ease: "hard", absolute: true });
    gsap.to(filas.map((f) => f.seccion), {
      y: 0, duration: motionReducido ? 0 : 0.52, ease: "hard", stagger: 0.03,
    });
    gsap.to(ficha, {
      opacity: 0, duration: motionReducido ? 0 : 0.24,
      onComplete: () => gsap.set(ficha, { pointerEvents: "none" }),
    });
    anuncio.textContent = "Ficha cerrada.";
  }

  /** Los bloques salen de los nodos que ya existen: content.ts no se toca. */
  function bloquesDeFicha(seccion: HTMLElement): HTMLElement[] {
    const piezas: HTMLElement[] = [];
    const lead = seccion.querySelector<HTMLElement>(".lead");
    const mascaras = Array.from(seccion.querySelectorAll<HTMLElement>("[data-mask]"));
    const meta = seccion.querySelector<HTMLElement>(".obra-meta");
    const marcas = seccion.querySelector<HTMLElement>("[data-obra-marcas]");
    for (const pieza of [lead, mascaras[1], marcas, mascaras[0], meta]) {
      if (pieza) piezas.push(pieza);
    }
    return piezas;
  }
```

**Ojo con `bloquesDeFicha`:** mueve nodos fuera de su sección. `cierra()` **no** los devuelve, y no
hace falta: el siguiente `abre()` los vuelve a reclamar y el CSS los oculta en reposo. Si el arnés
detecta que una fila pierde su ficha tras cerrar y volver a abrir otra, devuélvelos en `cierra()`.

- [ ] **Paso 4: Enganchar el clic y el teclado**

```ts
  filas.forEach((fila, i) => {
    const alPulsar = (evento: Event): void => { evento.preventDefault(); abre(i); };
    fila.boton.addEventListener("click", alPulsar);
    fila.seccion.addEventListener("click", alPulsar);
    sueltas.push(() => {
      fila.boton.removeEventListener("click", alPulsar);
      fila.seccion.removeEventListener("click", alPulsar);
    });
  });
  const alTeclado = (e: KeyboardEvent): void => { if (e.key === "Escape") cierra(); };
  window.addEventListener("keydown", alTeclado);
  sueltas.push(() => window.removeEventListener("keydown", alTeclado));
```

- [ ] **Paso 5: CSS de la lupa, la ficha y la utilidad `sr-only`**

`.sr-only` **no existe todavia en el proyecto** (comprobado con
`grep -rn "sr-only" src/`). Se crea aqui, en `src/style.css`, porque es donde se usa por primera
vez: sin ella la region de anuncio se pinta como un parrafo visible bajo el cartel.

```css
/* en src/style.css */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}
```

```css
/* en src/themes/themes.css */
:root[data-theme="hyprland"] .obra-lupa {
  position: absolute;
  left: 0;
  top: 132px;
  width: 760px;
  height: 475px;
  pointer-events: none;
}
:root[data-theme="hyprland"] .obra-ficha {
  position: absolute;
  left: 800px;
  top: 132px;
  width: 520px;
  opacity: 0;
  /* Sin esto la ficha cerrada tapa las filas y no se puede pulsar ninguna.
     Medido en el prototipo: el arnes se quedo 30s intentando el clic. */
  pointer-events: none;
}
:root[data-theme="hyprland"] .obra-ficha .lead,
:root[data-theme="hyprland"] .obra-ficha .obra-meta,
:root[data-theme="hyprland"] .obra-ficha [data-mask] {
  display: block;
}
:root[data-theme="hyprland"] [data-scene="obra"].is-abierto .obra-mini {
  clip-path: inset(0 0 0 0);
}
:root[data-theme="hyprland"] .obra-lupa .obra-mini-pie {
  display: block;
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 8px 12px;
  /* El pie va FUERA de la imagen, en banda solida. Nada de degradado encima de
     la foto: eso es el tratamiento generico que se abandona. */
  background: var(--color-ink);
  font-size: var(--t-1);
  letter-spacing: 0.04em;
  color: var(--haze);
}
```

**El ancho de 520 px está medido, no elegido.** A 412 px, tres de los cinco proyectos desbordaban:
WatchDog +64, TesisFar +39, «Editor de texto» +27. A 520 (con la lupa bajada de 824 a 760) los cinco
terminan entre 48 y 62 px por encima del borde.

- [ ] **Paso 6: Ejecutar el arnés y verlo pasar**

```bash
npm run build && npm run lint && python3 scripts/measure-cartel.py
```
Esperado: `0 fallos` en las cinco filas.

- [ ] **Paso 7: Commit**

```bash
git add src/components/obraCartel.ts src/themes/themes.css scripts/measure-cartel.py
git commit -m "feat(obra): la captura viaja de la fila a la lupa con Flip"
```

---

## Task 5: Las marcas del stack

**Ficheros:**
- Crear: `src/utils/stackIcons.ts`
- Modificar: `src/sections/obra/projectScene.ts`
- Modificar: `src/themes/themes.css`
- Modificar: `docs/superpowers/specs/2026-08-10-hyprland-obra-cartel-design.md`
- Modificar: `scripts/measure-cartel.py`

**Interfaces:**
- Consume: `getIconMarkup(slug: string): string` de `src/utils/icons.ts` — **lanza excepción** con un
  slug desconocido, a propósito.
- Produce: `slugDeStack(nombre: string): string | null` en `src/utils/stackIcons.ts`.

**Corrección del spec, dos cosas.**

**Primera:** el spec dice que las marcas serían monogramas dibujados a mano porque los logos «traen
su propio color». Es **falso** en este repo: `src/utils/icons.ts` ya inlinea `simple-icons`, que son
de un solo trazo y heredan `currentColor`. Se usan los iconos reales, monocromos. La conclusión
(monocromía) no cambia; el medio sí. **Zustand no existe en `simple-icons`**: un nombre sin marca no
pinta nada — el nombre ya está escrito en la línea de stack, así que no se pierde información y no
se inventa un logotipo.

**Segunda: el spec describe tiles cuadrados de 34 px con filete de brasa, y eso se retira.** Aoshi
decidió el 2026-08-10 que las marcas **comparten gramática con el catastro**, la sección «Con qué
construyo» que se está rediseñando en paralelo
(`docs/superpowers/specs/2026-08-10-hyprland-stack-catastro-design.md`, rama
`worktree-hyprland-stack-catastro`). Su elemento firma es **un friso de estas mismas marcas de
`simple-icons`**, a 14 px, en `--haze`, sin caja. Un tile con filete aquí haría que la misma marca
se leyera de dos formas distintas dentro del mismo tema.

Manda la firma: allí el friso **es** el dispositivo, aquí las marcas son un detalle de apoyo. Esta
ficha adopta el tratamiento y sólo cambia el tamaño, que es lo único que puede depender del
contexto. La regla común: **monocromas, `--haze` en reposo, `--l1` sólo cuando algo está activo, y
nunca un logotipo con su color de marca.**

Lo que **no** se comparte, y es correcto: el catastro apaga las marcas vecinas con `opacity: 0.42`
al apuntar una. Aquí eso lo prohíbe la ley de la sección. La gramática común es de **tratamiento**,
no de movimiento.

El paso 7 de esta tarea corrige el spec con las dos cosas.

- [ ] **Paso 1: Añadir la aserción que falla**

```python
STACK_SIN_MARCA = {"Zustand"}


def marcas_del_stack(pg) -> list[str]:
    return pg.evaluate(
        """(sinMarca) => {
          const f = [];
          for (const sec of document.querySelectorAll('[data-scene="obra"]')) {
            const nombres = Array.from(sec.querySelectorAll('.obra-meta dd'))
              .map(d => d.textContent).find(t => t && t.includes(' · '));
            if (!nombres) continue;
            const esperadas = nombres.split(' · ').filter(n => !sinMarca.includes(n)).length;
            const tiles = sec.querySelectorAll('[data-obra-marcas] .obra-marca').length;
            if (tiles !== esperadas) f.push(`${tiles} marcas, esperaba ${esperadas}`);
            for (const svg of sec.querySelectorAll('[data-obra-marcas] svg')) {
              const fill = getComputedStyle(svg).fill;
              if (fill !== getComputedStyle(svg.parentElement).color) {
                f.push(`marca con color propio: ${fill}`);
              }
            }
          }
          return f;
        }""",
        list(STACK_SIN_MARCA),
    )
```

- [ ] **Paso 2: Ejecutarlo y ver que falla**

Esperado: `0 marcas, esperaba 5`.

- [ ] **Paso 3: Crear `src/utils/stackIcons.ts`**

```ts
/**
 * Nombre de tecnologia tal y como aparece en `caseStudies[].stack` -> slug de
 * `simple-icons`. Se mantiene aparte de `icons.ts` porque aquello es el
 * registro de slugs disponibles y esto es la traduccion desde el contenido.
 *
 * Una tecnologia sin marca devuelve `null` y no pinta tile: el nombre ya
 * aparece escrito en la linea de stack, asi que no se pierde nada, y no se
 * inventa un logotipo que no existe. `Zustand` es el unico caso hoy.
 */
const SLUGS: Record<string, string> = {
  Python: "python",
  Django: "django",
  TypeScript: "typescript",
  JavaScript: "javascript",
  React: "react",
  Vite: "vite",
  "Next.js": "nextdotjs",
  RxDB: "rxdb",
  GSAP: "gsap",
  Electron: "electron",
  C: "c",
  GTK4: "gtk",
};

export function slugDeStack(nombre: string): string | null {
  return SLUGS[nombre] ?? null;
}
```

- [ ] **Paso 4: Rellenar `[data-obra-marcas]` en `projectScene.ts`**

Importa `elFromMarkup` de `../../utils/dom`, `getIconMarkup` y `slugDeStack`, y sustituye la
creación vacía de la Task 1:

```ts
  const marcas = el(
    "div",
    "obra-marcas",
    project.stack.flatMap((nombre) => {
      const slug = slugDeStack(nombre);
      if (!slug) return [];
      const tile = el("span", "obra-marca", [elFromMarkup("obra-marca-svg", getIconMarkup(slug))]);
      tile.title = nombre;
      return [tile];
    }),
  );
  marcas.setAttribute("data-obra-marcas", "");
  marcas.setAttribute("aria-hidden", "true");
```

`aria-hidden` es correcto: los nombres ya los anuncia la línea de stack, y repetirlos sería ruido.

- [ ] **Paso 5: CSS de los tiles**

```css
:root[data-theme="hyprland"] .obra-ficha .obra-marcas {
  display: flex;
  gap: 14px;
  margin-top: 12px;
  flex-wrap: wrap;
  color: var(--haze);
}
:root[data-theme="hyprland"] .obra-marca {
  /* Sin caja, sin filete, sin radio: misma gramatica que el friso del catastro,
     que es donde ese friso es la firma. Aqui solo cambia el tamano, que es lo
     unico que puede depender del contexto. */
  display: block;
  clip-path: inset(0 100% 0 0);   /* entran por corte, con escalonado */
}
:root[data-theme="hyprland"] .obra-marca-svg svg {
  width: 20px;
  height: 20px;
  fill: currentColor;   /* simple-icons es de un solo trazo: hereda el tema */
}
```

Y en `abre()`, tras la ficha:

```ts
    if (!motionReducido) {
      gsap.fromTo(
        ficha.querySelectorAll(".obra-marca"),
        { clipPath: "inset(0 100% 0 0)" },
        { clipPath: "inset(0 0 0 0)", duration: 0.42, ease: "hard", stagger: 0.05, delay: 0.42 },
      );
    } else {
      gsap.set(ficha.querySelectorAll(".obra-marca"), { clipPath: "inset(0 0 0 0)" });
    }
```

- [ ] **Paso 6: Ejecutar el arnés y verlo pasar**

```bash
npm run build && npm run lint && python3 scripts/measure-cartel.py
```

- [ ] **Paso 7: Corregir el spec**

En `2026-08-10-hyprland-obra-cartel-design.md`, apartado «Las marcas del stack», sustituye la
justificación de los monogramas por la real: se usan `simple-icons`, que son monocromos y heredan
`currentColor`; Zustand no tiene marca y no pinta tile.

- [ ] **Paso 8: Commit**

```bash
git add src/utils/stackIcons.ts src/sections/obra/projectScene.ts src/themes/themes.css \
  scripts/measure-cartel.py docs/superpowers/specs/2026-08-10-hyprland-obra-cartel-design.md
git commit -m "feat(obra): marcas del stack con simple-icons en la ficha del cartel"
```

---

## Task 6: Móvil y tableta

**Ficheros:**
- Modificar: `src/themes/themes.css`
- Modificar: `src/components/obraCartel.ts`
- Modificar: `scripts/measure-cartel.py`

**Interfaces:** ninguna nueva. Sólo escalones y la separación por capacidad de puntero.

**Regla:** el mismo dispositivo, no otro. La separación se hace con `@media (hover: hover)` —
**por capacidad del dispositivo, no por ancho de pantalla** — y los escalones tipográficos con
`@media (min-width: …)`.

- [ ] **Paso 1: Añadir las aserciones que fallan**

```python
ANCHOS = [("movil", 390, 844), ("tableta", 820, 1024), ("escritorio", 1440, 900)]


def movil(pg) -> list[str]:
    """La miniatura esta SIEMPRE puesta cuando no hay hover, el objetivo tactil
    llega a 44px, y ninguna fila degrada a pila generica."""
    return pg.evaluate(
        """() => {
          const f = [];
          for (const sec of document.querySelectorAll('[data-scene="obra"]')) {
            const mini = sec.querySelector('[data-obra-mini]');
            const cs = getComputedStyle(mini);
            if (cs.display === 'none') f.push('sin miniatura en movil');
            if (cs.clipPath !== 'none' && cs.clipPath.includes('100%')) {
              f.push('la miniatura espera a un hover que no existe');
            }
            if (sec.getBoundingClientRect().height < 44) f.push('fila por debajo del objetivo tactil');
          }
          return f;
        }"""
    )
```

Llama a `cartel_en_reposo`, `escala_tipografica` y `apertura` **en los tres anchos** de `ANCHOS`.

**Una aserción hay que acotarla por ancho, y es importante.** `cartel_en_reposo` exige que la
miniatura mida lo mismo que la caja del título. Eso **sólo se sostiene a partir de 1200 px**, que es
donde el título vale `--t-8`. Por debajo, el título encoge a `--t-6` (caja de 56,6 px) y a `--t-4`
(31,8 px), y una miniatura de ese tamaño no enseñaría nada: por eso el diseño le da medidas propias
(152×95 en tableta, 96×60 en móvil). Añade el ancho como parámetro y comprueba la igualdad sólo en
escritorio:

```python
def cartel_en_reposo(pg, ancho: int) -> list[str]:
    ...
            # La miniatura iguala la caja del titulo SOLO a partir de 1200px.
            # Por debajo el titulo encoge a --t-6 y --t-4 y la miniatura
            # tendria 90 y 51px de ancho: ilegible. Ahi lleva medida propia.
            if ancho >= 1200 and abs(mr.height - tr.height) > 2:
                fallos.push(...)
```

Lo que **sí** se comprueba en los tres anchos: que la miniatura está alineada verticalmente con el
título, que el título no se corta, y que las cinco filas caben en el viewport.

- [ ] **Paso 2: Ejecutarlo y ver que falla**

Esperado: a 390 y 820, `titulo recortado` (sigue a `--t-8`) y `la ficha desborda`.

- [ ] **Paso 3: Escalones tipográficos y geometría por ancho**

```css
/* Escalones DISCRETOS: se cambia de token, no se interpola. Un `clamp()` sobre
   tokens devuelve valores que no existen en la escala — regla dura del repo. */
:root[data-theme="hyprland"] [data-scene="obra"] h2.display-lg {
  font-size: var(--t-4);
}
@media (min-width: 821px) {
  :root[data-theme="hyprland"] [data-scene="obra"] h2.display-lg { font-size: var(--t-6); }
}
@media (min-width: 1200px) {
  :root[data-theme="hyprland"] [data-scene="obra"] h2.display-lg { font-size: var(--t-8); }
}

/* Bajo 821px el area baja debajo del titulo: el canto derecho lo ocupa la
   miniatura, que aqui esta siempre puesta. */
@media (max-width: 820px) {
  :root[data-theme="hyprland"] [data-scene="obra"] {
    flex-wrap: wrap;
    padding: 10px 0;
  }
  :root[data-theme="hyprland"] [data-scene="obra"] h2.display-lg { flex: 1 1 auto; }
  :root[data-theme="hyprland"] [data-scene="obra"] .hero-kick {
    order: 4;
    flex: 1 0 100%;
    margin-left: 34px;
    margin-top: 5px;
  }
  :root[data-theme="hyprland"] [data-scene="obra"] .obra-mini {
    flex: 0 0 96px;
    height: 60px;
    clip-path: none;   /* sin hover, la captura no se esconde */
  }
  :root[data-theme="hyprland"] .obra-lupa {
    top: 88px; width: 336px; height: 190px;
  }
  :root[data-theme="hyprland"] .obra-ficha {
    left: 0; top: 294px; width: 100%; bottom: 0;
    overflow-y: auto;
    scrollbar-width: none;
  }
  :root[data-theme="hyprland"] .obra-ficha::-webkit-scrollbar { display: none; }
}
@media (min-width: 821px) and (max-width: 1199px) {
  :root[data-theme="hyprland"] [data-scene="obra"] .obra-mini { flex: 0 0 152px; height: 95px; }
  :root[data-theme="hyprland"] .obra-lupa { top: 124px; width: 592px; height: 370px; }
  :root[data-theme="hyprland"] .obra-ficha { left: 0; top: 510px; width: 100%; bottom: 0; overflow-y: auto; }
}
```

**El scroll interno está medido y es el único que este diseño acepta:** entre 27 y 85 px en móvil y
entre 43 y 74 px en tableta, según el proyecto. Es el pie de Rol y Periodo quedando medio dedo bajo
el pliegue. Si sale mayor, reduce la lupa antes que el cuerpo del texto.

- [ ] **Paso 4: El relevo se dispara al abrir cuando no hay hover**

En `obraCartel.ts`, dentro de `abre()`, el `relevo(...)` ya se llama siempre. Lo único que hay que
comprobar es que el enganche de `pointerenter` sigue bajo `if (finoPuntero)`, que ya lo está.
Añade el comentario que lo explica:

```ts
  // Sin hover (movil) el relevo no tiene disparador propio: lo hace la apertura.
  // La separacion va por capacidad del puntero, no por ancho de pantalla: un
  // portatil tactil de 1440 tiene las dos cosas.
```

- [ ] **Paso 5: Ejecutar el arnés en los tres anchos**

```bash
npm run build && python3 scripts/measure-cartel.py
```
Esperado: `0 fallos`.

- [ ] **Paso 6: Capturas**

390×844 y 820×1024, en reposo y con una ficha abierta.

- [ ] **Paso 7: Commit**

```bash
git add src/themes/themes.css src/components/obraCartel.ts scripts/measure-cartel.py
git commit -m "feat(obra): el cartel en movil y tableta, mismo dispositivo sin hover"
```

---

## Task 7: Accesibilidad y movimiento reducido

**Ficheros:**
- Modificar: `src/components/obraCartel.ts`
- Modificar: `src/themes/themes.css`
- Modificar: `scripts/measure-cartel.py`

- [ ] **Paso 1: Añadir las aserciones que fallan**

```python
def accesibilidad(pg) -> list[str]:
    return pg.evaluate(
        """() => {
          const f = [];
          const botones = Array.from(document.querySelectorAll('[data-obra-abrir]'));
          if (botones.length !== 5) f.push(`${botones.length} disparadores, esperaba 5`);
          for (const b of botones) {
            const etiqueta = b.getAttribute('aria-label') || '';
            if (!etiqueta.startsWith('Mostrar ')) f.push('disparador sin nombre accesible');
            if (b.tabIndex < 0) f.push('disparador fuera del orden de tabulacion');
          }
          const anuncio = document.querySelector('[data-obra-anuncio]');
          if (!anuncio || anuncio.getAttribute('aria-live') !== 'polite') f.push('sin region aria-live');
          return f;
        }"""
    )


def movimiento_reducido(pg_reducido) -> list[str]:
    """Con `reduce` el dispositivo sigue COMPLETO: se pierde el movimiento, no
    la informacion. Es la diferencia entre degradar y desactivar."""
    return pg_reducido.evaluate(
        """() => {
          const f = [];
          for (const sec of document.querySelectorAll('[data-scene="obra"]')) {
            const mini = sec.querySelector('[data-obra-mini]');
            const cp = getComputedStyle(mini).clipPath;
            if (cp !== 'none' && cp.includes('100%')) f.push('captura oculta con movimiento reducido');
          }
          if (document.querySelector('.obra-barrido')) f.push('la barra de entrada existe con reduce');
          return f;
        }"""
    )
```

Para el contexto reducido: `b.new_context(reduced_motion="reduce")`.

- [ ] **Paso 2: Ejecutarlo y ver que falla**

- [ ] **Paso 3: Foco visible**

`.sr-only` entro en la Task 4, que es donde se usa por primera vez. Aqui solo se comprueba que el
anuncio no se ve y que el orden de tabulacion es el visual.

El `outline: 2px solid var(--l1)` con `outline-offset: -2px` ya entró en la Task 2. Hacia fuera
invadiría la fila vecina.

- [ ] **Paso 4: Guardas de movimiento reducido**

Ya están en el módulo (`motionReducido`). Verifica que **la barra de entrada no se crea** con
`reduce` — el `if (!motionReducido) entrada(...)` de la Task 3 lo garantiza.

- [ ] **Paso 5: Ejecutar el arnés y verlo pasar**

- [ ] **Paso 6: Commit**

```bash
git add src/components/obraCartel.ts src/themes/themes.css src/style.css scripts/measure-cartel.py
git commit -m "fix(obra): foco, anuncio y movimiento reducido del cartel"
```

---

## Task 8: La segunda captura

**Ficheros:**
- Modificar: `src/sections/obra/projectScene.ts`
- Modificar: `src/components/obraCartel.ts`
- Modificar: `src/themes/themes.css`
- Modificar: `scripts/measure-cartel.py`

**Por qué existe:** cuatro de los cinco proyectos declaran **dos** capturas en `content.ts` y el
cartel sólo enseña la primera. Perder la mitad de las capturas es una regresión de contenido
respecto al acordeón, que mostraba la galería entera. No estaba en el spec: **se añade aquí y hay
que anotarlo en el spec al cerrar.**

- [ ] **Paso 1: Añadir la aserción que falla**

```python
def segunda_captura(pg) -> list[str]:
    return pg.evaluate(
        """() => {
          const f = [];
          const secs = document.querySelectorAll('[data-scene="obra"]');
          secs[0].querySelector('[data-obra-abrir]').click();
          const tiles = document.querySelectorAll('[data-obra-lupa] ~ * .obra-otra, .obra-otras .obra-otra');
          if (tiles.length < 1) f.push('la segunda captura de EchoPlan no aparece');
          return f;
        }"""
    )
```

- [ ] **Paso 2: Ejecutarlo y ver que falla**

- [ ] **Paso 3: Emitir las capturas restantes**

En `projectScene.ts`, junto a `mini`:

```ts
  const otras = el(
    "div",
    "obra-otras",
    project.gallery.slice(1).map((shot) => {
      const tile = el("button", "obra-otra", []) as HTMLButtonElement;
      tile.type = "button";
      const img = el("img", "obra-otra-img") as HTMLImageElement;
      img.src = shot.src;
      img.alt = shot.caption;
      img.loading = "lazy";
      tile.append(img);
      tile.setAttribute("aria-label", `Ver ${shot.caption}`);
      return tile;
    }),
  );
  otras.setAttribute("data-obra-otras", "");
```

Añádelo a `children` y a la regla `display: none` de `style.css`.

- [ ] **Paso 4: Intercambio por corte, no por fundido**

En `abre()`, tras mover la ficha, engancha cada `.obra-otra` para que intercambie su `src` con el de
la lupa mediante un recorte lateral de 420 ms en `hard`, y actualiza el `figcaption`. **No** uses
`opacity`.

- [ ] **Paso 5: CSS**

Tiles de 96×60 bajo la lupa, mismo cuadro que la miniatura: sin borde, sin radio, sin sombra. El
activo lleva filete de 2 px de `--l1` a la izquierda.

- [ ] **Paso 6: Ejecutar el arnés y verlo pasar**

- [ ] **Paso 7: Commit**

```bash
git add src/sections/obra/projectScene.ts src/components/obraCartel.ts src/themes/themes.css \
  src/style.css scripts/measure-cartel.py
git commit -m "feat(obra): las capturas restantes del proyecto, bajo la lupa"
```

---

## Task 9: Verificación final y cierre

**Ficheros:**
- Modificar: `scripts/verify.py`
- Modificar: `docs/superpowers/specs/2026-08-10-hyprland-obra-cartel-design.md`
- Modificar: `.claude/CLAUDE.md` y `CLAUDE.md` si el estado del tema cambia

- [ ] **Paso 1: Dejar escrito cómo se corre el arnés**

**Comprobado:** `scripts/verify.py` **no invoca** los `measure-*.py` — no hay ni un `subprocess` en
él. Son arneses independientes que se lanzan a mano, igual que `measure-placa.py`. Así que **no
inventes una integración**: añade `measure-cartel.py` a la tabla de arneses de
`.claude/rules/verification.md` con su comando exacto, y déjalo ahí.

```bash
npm run build && npx vite preview --port 4173 &
python3 scripts/measure-cartel.py --base http://localhost:4173
```

- [ ] **Paso 2: Medir contraste contra el fondo REAL**

Es el punto que el spec deja pendiente. **El fondo no es un plano**: la página lleva el shader más
`--bg-fallback`, que sube hasta #3a1008. Mide bruma sobre la zona alta del cartel (donde el haz es
más brillante) y el papel del titular encendido. Referencias: `--haze` sobre tinta 6,81:1; sobre
#3a1008 5,54:1; `--l1` sobre tinta 6,61:1. Todo tiene que pasar AA (4,5:1).

- [ ] **Paso 3: Comprobar Vice y Caelestia contra `main`**

```bash
git worktree add /tmp/cartel-main main
```
Sirve los dos builds y compara capturas de `?theme=vice` y `?theme=caelestia` a 1440×900 y 390×844.
**Nunca `git stash`.**

- [ ] **Paso 4: Arnés completo y anti-mock**

```bash
npm run build && npm run lint
python3 scripts/verify.py
grep -rE "mockData|fakeData|hardcoded|TODO.*real|// fake|demo_data|placeholder|lorem ipsum|Lorem" \
  src/ --include="*.ts"
```

- [ ] **Paso 5: Actualizar la línea base si procede**

```bash
python3 scripts/verify.py --update-baseline   # y revisa el diff antes de commitear
```
Una línea base que se queda grande vuelve a esconder cosas.

- [ ] **Paso 6: Cerrar el spec**

Cambia `Estado: pendiente de plan` por `Estado: implementado`, añade la segunda captura (Task 8) al
apartado de composición y un `## Registro de implementación` con lo que se desvió del plan.
`check_spec_plan_consistency()` falla si el spec dice `implementado` y quedan casillas sin marcar.

- [ ] **Paso 7: Gates**

Lanza `lidia-naive-tester` y `vera-art-director` (umbral 7,5/10). Antes, **revisión de Aoshi en el
sitio real haciendo scroll**, no sobre capturas.

- [ ] **Paso 8: Commit de cierre**

```bash
git add -A
git commit -m "docs(obra): cerrar el cartel con el registro de implementacion"
```

---

## Autorrevisión del plan

**Cobertura del spec:** diagnóstico y retirada del acordeón → Task 2. Cuadro de imagen propio →
Tasks 2 y 4. Composición y anchos medidos → Tasks 2, 4, 6. Tipografía escalonada → Tasks 2 y 6.
Color y contraste → Task 9 (medición). Entrada por barrido → Task 3. Relevo → Task 3. Apertura con
Flip → Task 4. Marcas del stack → Task 5. Móvil y tableta → Task 6. Accesibilidad y movimiento
reducido → Task 7. Trampas conocidas → repartidas como comentarios en el código y aserciones del
arnés. Preguntas abiertas del spec: la miniatura (Task 1, nodo propio en vez de reutilizar la
galería), la reordenación de `projectScene.ts` (Task 1, aditiva, con `display: contents` en la
Task 2 para no restructurar) y el ordinal gigante (Task 2, se restila en vez de ocultarse).

**Hueco detectado y cubierto:** la segunda captura de cada proyecto no estaba en el spec y se habría
perdido en silencio. Es la Task 8.

**Consistencia de nombres:** `ObraCartelHandle`, `mountObraCartel`, `Fila`, `relevo()`, `entrada()`,
`asentar()`, `abre()`, `cierra()`, `bloquesDeFicha()`, `slugDeStack()`. Clase de estado
`is-abierto` (no `is-open`, que era del acordeón que se retira). Ganchos `data-obra-mini`,
`data-obra-marcas`, `data-obra-abrir`, `data-obra-otras`, `data-obra-lupa`, `data-obra-ficha`,
`data-obra-anuncio`.
