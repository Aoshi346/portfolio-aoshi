# Cartel de reparto en "Con que construyo" — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir la escena `[data-scene="credits"]` del tema Vice en el bloque
de creditos del pie de un cartel de cine — tipografia condensada, centrado, sin
recuadros — conservando intacto el comportamiento de datos actual.

**Architecture:** Un solo DOM para los tres temas. Todo cambio de marcado es
**aditivo** (un nodo nuevo: el friso de marcas) y la presentacion la decide el
CSS colgado de `[data-theme]`. El panel de detalle existente no se elimina: se
re-skinea por CSS como pie de cartel a dos alturas. Los separadores del cartel
salen de CSS, no de nodos, para no alterar los hijos directos que anima GSAP.

**Tech Stack:** Vite 8 · TypeScript ~6 strict · Tailwind 4 · GSAP 3 ·
simple-icons 16 · Playwright (verificacion) — sin framework, sin backend.

**Spec:** `docs/superpowers/specs/2026-07-29-creditos-cartel-reparto-design.md`

---

## Global Constraints

- **No hay runner de tests unitarios.** `package.json` solo expone `dev`,
  `build`, `preview` y `lint`. El ciclo de prueba de cada tarea es:
  `npm run build` + `npm run lint` + una asercion medida sobre el DOM con
  Playwright + `python3 scripts/verify.py`. No inventes un `vitest`.
- **Node del sistema es 18.19.1 y Vite 8 exige >= 20.** Antes de cualquier
  comando npm: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`.
- **El tema se sortea al azar por visita.** Toda URL de verificacion lleva
  `?theme=vice`.
- **Linea base de `verify.py`: exactamente 12 FAIL preexistentes** (9 rellenos
  de galeria en `public/media/obra/`, 3 ficheros `public/media/vice-*`).
  Cualquier fallo distinto de esos 12 lo has introducido tu.
- **TypeScript strict, cero `any`.** Usar `unknown` + guards si hace falta.
- **Cero emojis** en codigo, docs, commits y chat.
- **Comentarios en espanol sin tildes**, densos, que expliquen POR QUE y no QUE,
  incluyendo la medicion que motivo la decision. Es el estilo del repo.
- **`gsap.from` esta prohibido de facto.** Deduce un extremo leyendo el DOM y ha
  causado tres regresiones reales. Usar `fromTo` con los dos extremos escritos a
  mano, y materializar colecciones con `Array.from(...)`.
- **Un `transform` inline de GSAP gana siempre a una regla CSS.** Si un elemento
  recibe entrada con GSAP, su hover no puede usar `transform` en CSS.
- **`.credit-role` no se puede eliminar del DOM.** `verify.py` exige que exista y
  este oculto por CSS para validar el re-skin a pildoras de Hyprland/Caelestia.
- **No tocar `--font-display` (Passion One) ni `--font-body` (Manrope).**
  `verify.py` comprueba ambos y que ninguno resuelva a monoespaciada.
- **No tocar `wireFocusScroll`** (`src/utils/reveal.ts`): solo actua con
  `:focus-visible` y solo si el elemento no se ve entero.
- **Solo cambia Vice.** Hyprland y Caelestia deben seguir renderizando su lista
  de pildoras sin cambio visible.
- **Commit por tarea**, formato `tipo(scope): descripcion`.

### Nota de medicion

`page.screenshot()` en headless perturba las animaciones: bloquea el compositor y
GSAP salta hacia delante, con lo que una timeline parece completarse antes de
tiempo sin que sea cierto. Para medir ritmo, muestrear desde dentro de la pagina
con `setInterval` sobre `tl.progress()`. Para depurar sin que el shader lo haga
lentisimo: `page.route("**/viceHaze*", r => r.abort())`.

Chromium de Playwright: lanzar con `p.chromium.launch(headless=True,
args=['--no-sandbox'])`. **No** pasar `executable_path='/usr/bin/chromium-browser'`
— no existe en esta maquina.

---

## File Structure

| Archivo | Responsabilidad tras el cambio |
|---|---|
| `src/data/content.ts` | Unica fuente de contenido: 6 grupos, 23 tecnologias, frases cortas, `tooling` por proyecto |
| `src/utils/icons.ts` | Registro de SVG de marca. Gana 11 slugs |
| `src/components/credits.ts` | DOM compartido. Gana el friso y el cruce con `tooling` |
| `src/style.css` | Base compartida. Declara el friso oculto por defecto |
| `src/themes/themes.css` | Bloque Vice: cartel, pie a dos alturas, friso visible, movil |
| `src/themes/vice.ts` | `fontHref` con Pathway Gothic One |
| `index.html` | `fontHrefs.vice` con Pathway Gothic One |
| `src/themes/vice.choreography.ts` | `scene4Credits` gana la entrada del friso |

---

## Task 1: Datos y iconos

Contenido y marcas van juntos: cada tecnologia nueva necesita su SVG o
`getIconMarkup()` lanza excepcion **en los tres temas**, no solo en Vice.

**Files:**
- Modify: `src/data/content.ts` (`skillGroups`, `secondarySkills`, `CaseStudy`, `caseStudies`)
- Modify: `src/utils/icons.ts`

**Interfaces:**
- Consumes: nada.
- Produces: `skillGroups: SkillGroup[]` con **6 grupos y 23 items**;
  `secondarySkills` **eliminado**; `CaseStudy.tooling?: string[]`;
  `getIconMarkup(slug)` acepta los 23 slugs usados.

- [x] **Step 1: Registrar los 11 slugs nuevos en `src/utils/icons.ts`**

Anadir junto a los imports existentes:

```ts
import nextdotjs from "simple-icons/icons/nextdotjs.svg?raw";
import nodedotjs from "simple-icons/icons/nodedotjs.svg?raw";
import gsap from "simple-icons/icons/gsap.svg?raw";
import rxdb from "simple-icons/icons/rxdb.svg?raw";
import electron from "simple-icons/icons/electron.svg?raw";
import gtk from "simple-icons/icons/gtk.svg?raw";
import git from "simple-icons/icons/git.svg?raw";
import github from "simple-icons/icons/github.svg?raw";
import n8n from "simple-icons/icons/n8n.svg?raw";
import claude from "simple-icons/icons/claude.svg?raw";
import googlegemini from "simple-icons/icons/googlegemini.svg?raw";
```

Y anadirlos al mapa `icons`:

```ts
const icons: Record<string, string> = {
  react,
  typescript,
  tailwindcss,
  vite,
  python,
  django,
  mysql,
  javascript,
  html5,
  css,
  c,
  cplusplus,
  nextdotjs,
  nodedotjs,
  gsap,
  rxdb,
  electron,
  gtk,
  git,
  github,
  n8n,
  claude,
  googlegemini,
};
```

- [x] **Step 2: Reescribir `skillGroups` en `src/data/content.ts`**

Sustituir el `skillGroups` actual y **borrar** `secondarySkills` entero. Solo lo
consumia `credits.ts`, comprobado con grep sobre `src/`, asi que no queda ningun
llamante huerfano.

```ts
export const skillGroups: SkillGroup[] = [
  {
    label: "Frontend",
    items: [
      { name: "React", slug: "react", detail: "Interfaces con estado complejo." },
      { name: "Next.js", slug: "nextdotjs", detail: "Para apps con rutas y render en servidor." },
      { name: "TypeScript", slug: "typescript", detail: "Tipado en todo lo que escribo." },
      { name: "Tailwind CSS", slug: "tailwindcss", detail: "Maquetación rápida y consistente." },
      { name: "Vite", slug: "vite", detail: "Mi bundler por defecto." },
      { name: "GSAP", slug: "gsap", detail: "Las animaciones y las transiciones." },
    ],
  },
  {
    label: "Backend y datos",
    items: [
      { name: "Python", slug: "python", detail: "Automatización, datos y APIs." },
      { name: "Django", slug: "django", detail: "Backend robusto: ORM, admin y auth." },
      { name: "Node.js", slug: "nodedotjs", detail: "JavaScript fuera del navegador." },
      { name: "MySQL", slug: "mysql", detail: "Donde persisto los datos." },
      { name: "RxDB", slug: "rxdb", detail: "Datos locales en el navegador." },
    ],
  },
  {
    label: "Lenguajes base",
    items: [
      { name: "JavaScript", slug: "javascript", detail: "Base de todo lo que corre en el navegador." },
      { name: "HTML", slug: "html5", detail: "Estructura semántica antes que nada." },
      { name: "CSS", slug: "css", detail: "Lo que no cubre Tailwind, lo escribo a mano." },
      { name: "C", slug: "c", detail: "Donde aprendí a pensar en memoria y punteros." },
      { name: "C++", slug: "cplusplus", detail: "Sistemas y aplicaciones nativas." },
    ],
  },
  {
    label: "Escritorio",
    items: [
      { name: "Electron", slug: "electron", detail: "Aplicaciones de escritorio con tecnología web." },
      { name: "GTK4", slug: "gtk", detail: "Interfaces nativas en C." },
    ],
  },
  {
    label: "Herramientas",
    items: [
      { name: "Git", slug: "git", detail: "Control de versiones en todo lo que hago." },
      { name: "GitHub", slug: "github", detail: "Donde publico y comparto el código." },
      { name: "n8n", slug: "n8n", detail: "Automatizo tareas repetitivas entre servicios." },
    ],
  },
  {
    label: "IA",
    items: [
      { name: "Claude Code", slug: "claude", detail: "Asistente en terminal para escribir y revisar código." },
      { name: "Gemini CLI", slug: "googlegemini", detail: "Consultas rápidas desde la terminal." },
    ],
  },
];
```

- [x] **Step 3: Anadir `tooling` a `CaseStudy` y rellenarlo**

En la interfaz, junto a `stack`:

```ts
  stack: string[];
  /**
   * Lo transversal: control de versiones y asistentes que se usaron para
   * construir el proyecto, no para hacerlo funcionar. Va aparte de `stack`
   * porque `stack` se pinta literal en la ficha de obra
   * (`projectScene.ts`) y meter aqui cuatro nombres repetidos identicos en
   * los cinco proyectos alargaba esa linea sin distinguir nada: Git no
   * separa un proyecto de otro. Alimenta el cruce de creditos y nada mas —
   * la ficha de obra sigue mostrando solo `stack`.
   */
  tooling?: string[];
```

Y en `caseStudies`, tras el `stack` de cada uno:

```ts
// EchoPlan, TesisFar, HyprFinance, WatchDog:
tooling: ["Git", "GitHub", "Claude Code", "Gemini CLI"],

// Editor de texto:
tooling: ["Git", "GitHub"],
```

**`src/sections/obra/projectScene.ts` NO se toca.** Sigue pintando
`project.stack.join(" · ")` y nada mas. Que `tooling` no aparezca en la ficha de
obra es la decision, no un olvido: no lo anadas "para que se vea".

- [x] **Step 4: Verificar que compila y que los 23 slugs resuelven**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
```

Esperado: build verde. Si falla con `Missing simple-icons SVG for slug "..."`,
falta un slug del Step 1.

- [x] **Step 5: Asercion sobre el DOM — 23 creditos y 6 encabezados**

Con `npm run dev` corriendo:

```python
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:5173/?theme=vice"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.route("**/viceHaze*", lambda r: r.abort())
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(U, wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(3000)
    assert errs == [], errs
    assert pg.eval_on_selector_all("[data-credit]", "e=>e.length") == 23
    assert pg.eval_on_selector_all("[data-credit-group]", "e=>e.length") == 6
    # Git cruza contra tooling, no contra stack: los cinco proyectos.
    pg.eval_on_selector_all(
        "[data-credit]",
        "e=>e.find(x=>x.textContent.includes('Git') && !x.textContent.includes('GitHub'))"
        ".dispatchEvent(new MouseEvent('mouseenter'))")
    pg.wait_for_timeout(200)
    assert pg.eval_on_selector_all("[data-credit-used-list] > *", "e=>e.length") == 5
    b.close()
print("OK")
```

Esperado: `OK`. Si `[data-credit-used-list]` da 0 para Git, falta el cruce con
`tooling` — se implementa en la Task 3; hasta entonces esta asercion concreta
fallara. **Ejecutala completa despues de la Task 3**; en esta tarea comprueba
solo los dos primeros `assert`.

- [x] **Step 6: Commit**

```bash
git add src/data/content.ts src/utils/icons.ts
git commit -m "feat(credits): ampliar el reparto a 23 tecnologias en seis bloques"
```

---

## Task 2: Tipografia — token `--font-billing`

Se hace antes que el CSS del cartel porque ese CSS ya referencia el token.

**Files:**
- Modify: `index.html` (`fontHrefs.vice` en el script inline)
- Modify: `src/themes/vice.ts` (`fontHref`)
- Modify: `src/themes/themes.css` (declaracion del token en el bloque Vice)

**Interfaces:**
- Consumes: nada.
- Produces: variable CSS `--font-billing` disponible bajo `[data-theme="vice"]`.

- [x] **Step 1: Alta de la fuente en `index.html`**

En el objeto `fontHrefs` del script inline, sustituir el valor de `vice`:

```js
vice: "https://fonts.googleapis.com/css2?family=Passion+One:wght@900&family=Manrope:wght@200;300;400;600;700&family=Pathway+Gothic+One&display=swap",
```

- [x] **Step 2: Alta de la fuente en `src/themes/vice.ts`**

Mismo valor en `fontHref`, y ampliar el comentario existente:

```ts
  // Passion One 900: alternativa libre mas cercana a Pricedown, cuya licencia
  // gratuita prohibe incrustarla como webfont. Manrope cubre lead y cuerpo.
  // Pathway Gothic One es la condensada del cartel de reparto: ya viene
  // dibujada estrecha, asi que el bloque no necesita el `scaleX(.88)` del
  // mockup, que no condensa sino que aplasta (adelgaza los verticales y deja
  // intactos los horizontales). Un solo peso, 400: el nombre activo se realza
  // con color, no con grosor.
  //
  // Este href y el `fontHrefs.vice` del script inline de `index.html` tienen
  // que ir SIEMPRE a la par: el inline es quien pide las fuentes antes del
  // primer pintado y, si solo se toca uno, la carga degrada a la via lenta en
  // silencio.
  fontHref:
    "https://fonts.googleapis.com/css2?family=Passion+One:wght@900&family=Manrope:wght@200;300;400;600;700&family=Pathway+Gothic+One&display=swap",
```

- [x] **Step 3: Declarar el token en `src/themes/themes.css`**

Junto al resto de tokens de Vice:

```css
  /*
   * Tipografia del cartel de reparto, y SOLO del cartel. No sustituye a
   * --font-display ni a --font-body: `scripts/verify.py` comprueba que el
   * primero contenga "Passion One" y el segundo "Manrope", y que ninguno
   * resuelva a monoespaciada.
   */
  --font-billing: "Pathway Gothic One", "Oswald", sans-serif;
```

- [x] **Step 4: Verificar que la fuente carga de verdad**

```python
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:5173/?theme=vice"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto(U, wait_until="networkidle", timeout=30000)
    pg.wait_for_timeout(2500)
    tok = pg.evaluate("getComputedStyle(document.documentElement)"
                      ".getPropertyValue('--font-billing').trim()")
    loaded = pg.evaluate("document.fonts.check('16px \"Pathway Gothic One\"')")
    print("token:", tok, "| cargada:", loaded)
    assert "Pathway Gothic One" in tok
    assert loaded is True
    b.close()
```

Esperado: `cargada: True`. Si sale `False`, el href quedo mal en uno de los dos
sitios.

- [x] **Step 5: Confirmar que los tokens protegidos siguen intactos**

```bash
python3 scripts/verify.py 2>&1 | grep -E "display es Passion One|cuerpo es Manrope|monoespaciada"
```

Esperado: las tres lineas en `OK`.

- [x] **Step 6: Commit**

```bash
git add index.html src/themes/vice.ts src/themes/themes.css
git commit -m "feat(vice): anadir Pathway Gothic One como token --font-billing"
```

---

## Task 3: `credits.ts` — cruce con `tooling` y friso de marcas

**Files:**
- Modify: `src/components/credits.ts`

**Interfaces:**
- Consumes: `skillGroups` de la Task 1 (6 grupos), `CaseStudy.tooling`,
  `getIconMarkup(slug)`.
- Produces: en el DOM, `.credits-marks` con `data-credit-marks` como **tercer
  hijo de `.credits-grid`**, conteniendo un `.credits-mark[data-mark-slug]` por
  tecnologia; el activo lleva `.is-active`.

- [x] **Step 1: Cruzar tambien contra `tooling`**

En `toEntry()`:

```ts
    usedIn: caseStudies
      .filter((project) => [...project.stack, ...(project.tooling ?? [])].includes(item.name))
      .map((project) => project.title),
```

- [x] **Step 2: Simplificar la construccion de `groups`**

`secondarySkills` ya no existe. Sustituir el bloque actual por:

```ts
  const groups: SkillGroup[] = skillGroups;
```

Y quitar `secondarySkills` del import de la linea 1.

- [x] **Step 3: Declarar el registro de marcas ANTES del bucle de grupos**

**El orden importa:** `select()` se define dentro del bucle que recorre los
grupos y cierra sobre `marks`. Si `marks` se declara despues del bucle,
TypeScript falla con "Block-scoped variable 'marks' used before its
declaration". Va junto a `rows` y `listChildren`, antes del `for`:

```ts
  /*
   * Friso de marcas: donde un cartel de cine pone los logos de estudio y
   * distribuidora. Va al pie y no delante de cada nombre porque una marca por
   * nombre convierte la linea de reparto en una lista con vinetas — el
   * defecto exacto que esta direccion elimina.
   *
   * El Map indexa por slug para que `select()` encienda la marca en O(1) sin
   * volver a recorrer el DOM en cada `mouseenter`, que se dispara muchas
   * veces por segundo al pasar el raton por el cartel.
   */
  const marks = new Map<string, HTMLElement>();
  const markNodes: HTMLElement[] = [];
```

- [x] **Step 4: Crear cada marca dentro del bucle de items**

En el mismo `for (const item of group.items)` que ya construye la fila, justo
despues de crear `row` y antes de definir `select`:

```ts
      /*
       * Decorativa pura: `aria-hidden` (fuera del arbol de accesibilidad) y
       * `data-decorative` (exento del gate de contraste — nunca `aria-hidden`
       * para eso, ver `scripts/verify.py::check_contrast_wcag`).
       */
      const mark = elFromMarkup("credits-mark", getIconMarkup(entry.slug));
      mark.dataset.markSlug = entry.slug;
      marks.set(entry.slug, mark);
      markNodes.push(mark);
```

- [x] **Step 5: Encender la marca activa dentro de `select()`**

Anadir al final del cuerpo de `select()`, tras la linea de `used.hidden`:

```ts
        // La marca encendida es una segunda senal de seleccion que no depende
        // del hover: en tactil no lo hay, y el cartel no tiene recuadros que
        // delaten que un nombre responde.
        for (const [slug, mark] of marks) {
          mark.classList.toggle("is-active", slug === entry.slug);
        }
```

- [x] **Step 6: Montar el friso y devolverlo en el grid**

Tras el bucle de grupos, junto a la creacion de `list`:

```ts
  /*
   * Hermano de la lista y del panel, nunca hijo de `[data-credit-roll]`:
   * `scene4Credits` anima los hijos DIRECTOS de ese contenedor y meter aqui
   * 23 nodos mas reduciria el escalonado del reparto a ruido.
   */
  const frieze = el("div", "credits-marks", markNodes);
  frieze.setAttribute("data-credit-marks", "");
  frieze.setAttribute("aria-hidden", "true");
  frieze.setAttribute("data-decorative", "");

  return el("div", "credits-grid", [list, panel, frieze]);
```

- [x] **Step 7: Verificar**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
```

Y con `npm run dev` corriendo, la asercion completa del Step 5 de la Task 1
(ahora si debe pasar entera), mas:

```python
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:5173/?theme=vice"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.route("**/viceHaze*", lambda r: r.abort())
    pg.goto(U, wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(3000)
    assert pg.eval_on_selector_all("[data-credit-marks] .credits-mark", "e=>e.length") == 23
    # Al arrancar, React es la entrada activa y su marca la unica encendida.
    on = pg.eval_on_selector_all("[data-credit-marks] .is-active", "e=>e.map(x=>x.dataset.markSlug)")
    assert on == ["react"], on
    # El friso es hermano de la lista, no hijo: el escalonado no debe crecer.
    hijos = pg.eval_on_selector("[data-credit-roll]", "e=>e.children.length")
    assert hijos == 29, hijos  # 23 creditos + 6 encabezados
    b.close()
print("OK")
```

Esperado: `OK`. `hijos == 29` es la guarda de la restriccion dura 4: si sale 30,
alguien metio el friso o un separador dentro del rodillo.

- [x] **Step 8: Commit**

```bash
git add src/components/credits.ts
git commit -m "feat(credits): cruzar contra tooling y anadir el friso de marcas"
```

**No tocar en esta tarea:** `.credit-role` sigue en el DOM (lo exige
`verify.py`), el panel sigue siendo `role="status"` / `aria-live="polite"`, y
cada credito sigue siendo un `<button>` con `aria-pressed` y `aria-controls`.
Nada de eso cambia: el cartel es un re-skin, no una reescritura del componente.

---

## Task 4: Base compartida en `style.css`

El friso se declara oculto por defecto para que Hyprland y Caelestia no tengan
que saber que existe.

**Files:**
- Modify: `src/style.css`

**Interfaces:**
- Consumes: `.credits-marks` / `.credits-mark` de la Task 3.
- Produces: nada nuevo para tareas posteriores.

- [x] **Step 1: Anadir el bloque, junto al resto de reglas de creditos**

```css
/*
 * El friso de marcas es una pieza del cartel de Vice y de nadie mas: en
 * Hyprland y Caelestia la seccion son pildoras, y ahi 23 logos al pie serian
 * ruido sin funcion. Oculto por defecto y encendido solo por Vice, para que
 * los otros dos temas no tengan que conocer este nodo.
 */
.credits-marks {
  display: none;
}

.credits-mark svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
}
```

- [x] **Step 2: Verificar que Hyprland y Caelestia no cambian**

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    for tema in ["hyprland", "caelestia"]:
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(f"http://127.0.0.1:5173/?theme={tema}",
                wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(2500)
        vis = pg.eval_on_selector("[data-credit-marks]",
                                  "e=>getComputedStyle(e).display")
        print(tema, "friso:", vis)
        assert vis == "none"
        pg.close()
    b.close()
print("OK")
```

Esperado: `none` en los dos.

- [x] **Step 3: Commit**

```bash
git add src/style.css
git commit -m "feat(credits): declarar el friso de marcas oculto por defecto"
```

---

## Task 5: El cartel en escritorio (`themes.css`, bloque Vice)

**Files:**
- Modify: `src/themes/themes.css` (bloque `[data-theme="vice"]` de creditos,
  aprox. lineas 420-570 y la media query de 860px)

**Interfaces:**
- Consumes: `--font-billing` (Task 2), `.credits-marks` (Tasks 3 y 4).
- Produces: el cartel compuesto. La Task 6 solo ajusta el interlineado en movil.

- [x] **Step 1: Grid a una sola columna**

Sustituir la regla de `.credits-grid` dentro de la media query de 860px por una
columna unica centrada. El cartel, el pie y el friso se apilan en ese orden.

```css
:root[data-theme="vice"] .credits-grid {
  display: block;
  max-width: 880px;
  margin-inline: auto;
  text-align: center;
}
```

- [x] **Step 2: Los nombres fluyen como un parrafo compuesto**

`.credit` es `display: flex; width: 100%` en la base — eso es lo que lo hace
fila. En Vice pasa a comportarse como una palabra dentro de un renglon:

```css
/*
 * El nucleo del cartel: los nombres dejan de ser filas y fluyen como
 * palabras de un parrafo compuesto. `inline-block` y no `inline` porque el
 * area pulsable en movil se consigue con interlineado (ver Task 6) y un
 * `inline` puro no la tendria.
 *
 * Sin `scaleX`: Pathway Gothic One ya viene dibujada estrecha. El
 * `scaleX(.88)` del mockup no condensa, aplasta — adelgaza los trazos
 * verticales y deja intactos los horizontales.
 */
:root[data-theme="vice"] .credit {
  display: inline-block;
  width: auto;
  min-height: 0;
  padding: 0.28rem 0.1rem;
  border-bottom: 0;
  font-family: var(--font-billing);
  font-size: clamp(1rem, 2.05vw, 1.55rem);
  line-height: 1.24;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  color: var(--color-paper);
  transition: color 180ms ease;
}

:root[data-theme="vice"] .credit:hover,
:root[data-theme="vice"] .credit:focus-visible,
:root[data-theme="vice"] .credit.is-active {
  border-color: transparent;
  color: var(--color-accent);
}
```

**Ojo:** el realce va por `color`, nunca por `transform`. `.credit` recibe la
entrada de `scene4Credits` y un transform inline de GSAP gana siempre a la regla
CSS (restriccion dura 6).

- [x] **Step 3: Separadores sin tocar el DOM**

```css
/*
 * El punto medio entre nombres sale de CSS, no de nodos: metido en el DOM
 * seria un hijo directo mas de `[data-credit-roll]` y `scene4Credits` lo
 * animaria como si fuera un credito, descuadrando el escalonado.
 *
 * `.credit + .credit` acierta solo: entre dos creditos seguidos hay punto, y
 * tras un encabezado de grupo no, porque ahi el hermano previo no es
 * `.credit`.
 */
:root[data-theme="vice"] .credit + .credit::before {
  content: "·";
  padding: 0 0.4rem;
  color: color-mix(in srgb, var(--color-paper) 30%, transparent);
}

/* El "+" de afordancia de la base sobra: aqui la senal es el friso. */
:root[data-theme="vice"] .credit::after {
  content: none;
}
```

- [x] **Step 4: Encabezados de bloque**

Sustituir la regla existente de `.credit-group-label` en Vice (hoy tiene
`border-bottom`, que es de la version lista):

```css
:root[data-theme="vice"] .credit-group-label {
  display: block;
  margin: 1.05rem 0 0.25rem;
  padding-bottom: 0;
  border-bottom: 0;
  font-family: var(--font-billing);
  font-weight: 400;
  font-size: 0.56rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--color-accent-legible);
}
```

- [x] **Step 5: El panel se re-skinea como pie a dos alturas**

```css
/*
 * El panel de detalle no se elimina: los otros dos temas lo usan como ficha
 * y `verify.py` valida ese re-skin. Aqui se le quita la caja y se le dejan
 * ver solo los dos renglones del pie del cartel.
 */
:root[data-theme="vice"] .credits-panel {
  max-width: 760px;
  margin: 1.6rem auto 0;
  padding: 0;
  border: 0;
  background: none;
  box-shadow: none;
  text-align: center;
  /* Altura reservada: el pie no puede cambiar de alto al cambiar de nombre. */
  min-height: 66px;
}

:root[data-theme="vice"] .credits-icon,
:root[data-theme="vice"] .credits-panel-name,
:root[data-theme="vice"] .credits-panel-role {
  display: none;
}

:root[data-theme="vice"] .credits-panel-detail {
  margin: 0;
  font-family: var(--font-body);
  font-weight: 300;
  font-size: 0.92rem;
  line-height: 1.5;
}

:root[data-theme="vice"] .credits-used {
  margin-top: 0.6rem;
  font-family: var(--font-billing);
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--color-accent);
}

/*
 * Siete de las 23 tecnologias no aparecen en ningun proyecto publicado.
 * `visibility` y no `display`: con `display: none` la altura colapsa y el
 * cartel entero da un salto al pasar de una tecnologia con proyecto a una
 * sin el.
 */
:root[data-theme="vice"] .credits-used[hidden] {
  display: block;
  visibility: hidden;
}
```

- [x] **Step 6: El friso**

```css
:root[data-theme="vice"] .credits-marks {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 1.2rem;
  max-width: 780px;
  margin: 1.75rem auto 0;
  padding-top: 1.25rem;
  border-top: 1px solid color-mix(in srgb, var(--color-accent) 16%, transparent);
}

:root[data-theme="vice"] .credits-mark {
  width: 18px;
  height: 18px;
  color: var(--color-paper);
  opacity: 0.26;
  transition: opacity 200ms ease, color 200ms ease;
}

:root[data-theme="vice"] .credits-mark.is-active {
  color: var(--color-accent);
  opacity: 1;
}
```

- [x] **Step 7: Verificar composicion y que el pie no salta**

```python
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:5173/?theme=vice"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.route("**/viceHaze*", lambda r: r.abort())
    pg.goto(U, wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(3000)

    def alto_pie():
        return pg.eval_on_selector("[data-credit-panel]",
                                   "e=>Math.round(e.getBoundingClientRect().height)")

    def hover(nombre):
        pg.eval_on_selector_all(
            "[data-credit]",
            f"e=>e.find(x=>x.textContent.trim()==='{nombre}')"
            ".dispatchEvent(new MouseEvent('mouseenter'))")
        pg.wait_for_timeout(250)

    hover("React")          # con proyecto
    con = alto_pie()
    hover("MySQL")          # sin proyecto: "Aparece en" invisible
    sin = alto_pie()
    print("pie con proyecto:", con, "| sin proyecto:", sin)
    assert con == sin, "el pie cambia de altura y el cartel da un salto"

    vis = pg.eval_on_selector("[data-credit-used]", "e=>getComputedStyle(e).visibility")
    assert vis == "hidden", vis

    # Sin scaleX en ninguna parte del cartel.
    tr = pg.eval_on_selector("[data-credit-roll]", "e=>getComputedStyle(e).transform")
    assert tr in ("none", "matrix(1, 0, 0, 1, 0, 0)"), tr
    b.close()
print("OK")
```

Esperado: los dos altos iguales y `OK`.

- [x] **Step 8: Capturas de escritorio**

```python
pg.screenshot(path="/tmp/cartel-1440.png", full_page=False)
```

Mirarla. El cartel debe leerse centrado, sin recuadros, con los seis bloques y el
friso al pie.

- [x] **Step 9: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(vice): componer la seccion de creditos como cartel de reparto"
```

---

## Task 6: Movil — disposicion D

**Files:**
- Modify: `src/themes/themes.css`

**Interfaces:**
- Consumes: el cartel de la Task 5.
- Produces: area pulsable >= 44px por debajo de 860px.

- [x] **Step 1: Interlineado 2.7 por debajo de 860px**

```css
/*
 * Disposicion D: la composicion del cartel se mantiene en 390px y lo unico
 * que cambia es el interlineado. 2.7 no es un valor estetico — es el minimo
 * exacto con el que el area pulsable de cada nombre alcanza los 44px sin que
 * las filas se pisen (medido: 44px justos con font-size 1.02rem).
 *
 * Las alternativas se midieron en 390px: apilar un nombre por linea daba
 * 1623px de alto y volver a la lista 1619px, casi el doble que estos 867px,
 * en una pagina que ya tiene dos zonas fijadas. El objetivo de 44px es el
 * liston AAA que se marca el proyecto (SC 2.5.5); el requisito AA es SC
 * 2.5.8, de 24x24, que ya se cumplia sin esto.
 */
@media (max-width: 859px) {
  :root[data-theme="vice"] .credit {
    font-size: 1.02rem;
    line-height: 2.7;
    padding: 0 0.06rem;
  }

  :root[data-theme="vice"] .credits-marks {
    gap: 0.95rem;
  }
}
```

- [x] **Step 2: Verificar el objetivo tactil en 390x844**

```python
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:5173/?theme=vice"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.route("**/viceHaze*", lambda r: r.abort())
    pg.goto(U, wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(3000)
    altos = pg.eval_on_selector_all(
        "[data-credit]", "e=>e.map(x=>Math.round(x.getBoundingClientRect().height))")
    print("min:", min(altos), "| max:", max(altos))
    assert min(altos) >= 44, altos
    ancho = pg.evaluate("document.documentElement.scrollWidth")
    assert ancho <= 390, f"desbordamiento horizontal: {ancho}px"
    pg.screenshot(path="/tmp/cartel-390.png", full_page=True)
    b.close()
print("OK")
```

Esperado: `min >= 44` y sin desbordamiento horizontal.

- [x] **Step 3: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(vice): conservar el cartel en movil con objetivo tactil de 44px"
```

---

## Task 7: Coreografia — entrada del friso

**Files:**
- Modify: `src/themes/vice.choreography.ts` (`scene4Credits`, desde la linea 712)

**Interfaces:**
- Consumes: `[data-credit-marks]` de la Task 3.
- Produces: nada para tareas posteriores.

- [x] **Step 1: Anadir la entrada, tras el `fromTo` del rodillo**

```ts
  /*
   * El friso entra despues del reparto, no a la vez: en un cartel las marcas
   * del pie son lo ultimo que se lee, asi que son lo ultimo que aparece.
   *
   * `fromTo` sobre `Array.from(...)`, nunca `from` sobre una HTMLCollection
   * viva: es el mismo fallo que dejo doce filas de creditos desplazadas 34px
   * para siempre y el pie de contacto invisible.
   */
  const frieze = root.querySelector<HTMLElement>("[data-credit-marks]");
  if (frieze) {
    gsap.fromTo(
      Array.from(frieze.children),
      { opacity: 0, y: 10 },
      {
        opacity: 1,
        y: 0,
        duration: 0.4,
        ease: "power2.out",
        stagger: 0.02,
        scrollTrigger: {
          id: CREDITS_MARKS_TRIGGER_ID,
          trigger: frieze,
          start: "top 92%",
          toggleActions: "play none none reverse",
        },
      },
    );
  }
```

- [x] **Step 2: Declarar el id del trigger y matarlo al re-ejecutar**

Junto a `CREDITS_TRIGGER_ID`:

```ts
const CREDITS_MARKS_TRIGGER_ID = "vice-credits-marks";
```

Y junto al `ScrollTrigger.getById(CREDITS_TRIGGER_ID)?.kill();` existente:

```ts
  ScrollTrigger.getById(CREDITS_MARKS_TRIGGER_ID)?.kill();
```

- [x] **Step 3: Verificar que el friso termina visible y sin desplazamiento**

El fallo que esto previene es exactamente el que documenta el traspaso: una
entrada que deja el elemento desplazado para siempre.

```python
from playwright.sync_api import sync_playwright
U = "http://127.0.0.1:5173/?theme=vice"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.route("**/viceHaze*", lambda r: r.abort())
    pg.goto(U, wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(1500)
    pg.eval_on_selector("[data-scene='credits']", "e=>e.scrollIntoView()")
    pg.wait_for_timeout(2500)
    estado = pg.eval_on_selector_all(
        "[data-credit-marks] .credits-mark",
        "e=>e.map(x=>({o:getComputedStyle(x).opacity, t:getComputedStyle(x).transform}))")
    trasladados = [s for s in estado if s["t"] not in ("none", "matrix(1, 0, 0, 1, 0, 0)")]
    print("marcas:", len(estado), "| aun trasladadas:", len(trasladados))
    assert len(trasladados) == 0, trasladados[:3]
    assert all(float(s["o"]) > 0.2 for s in estado)
    b.close()
print("OK")
```

Esperado: cero marcas trasladadas al acabar la entrada.

- [x] **Step 4: Verificar `prefers-reduced-motion`**

```python
pg = b.new_page(viewport={"width": 1440, "height": 900},
                reduced_motion="reduce")
```

Repetir la asercion anterior con esa pagina: el friso debe quedar visible y sin
transform. `initScrollReveal` hace early-return con reduced-motion, asi que nada
puede depender de que la timeline llegue a ejecutarse.

- [x] **Step 5: Commit**

```bash
git add src/themes/vice.choreography.ts
git commit -m "feat(vice): entrada escalonada del friso de marcas"
```

---

## Task 8: Verificacion final y cierre

**Files:**
- Modify: `.docs/HANDOFF-creditos-cartel.md` (marcar las decisiones cerradas)
- Modify: `PROGRESS.json`

**Interfaces:**
- Consumes: todo lo anterior.
- Produces: nada.

- [x] **Step 1: Build y lint limpios**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
```

- [x] **Step 2: `verify.py` en su linea base**

```bash
python3 scripts/verify.py 2>&1 | tail -3
```

Esperado: `FALLOS: 12`. Si sale mas de 12, comparar contra la lista base (9
galerias + 3 `vice-*`) y arreglar lo nuevo.

- [x] **Step 3: Contraste AA remedido**

El cartel prescinde del scrim de `.credits-list`, asi que el contraste **no se da
por hecho**: hay que volver a medirlo, no asumir los 7:1-15:1 de la version
anterior.

```bash
python3 scripts/verify.py 2>&1 | grep -iE "contraste|contrast"
```

Esperado: sin fallos nuevos. Si alguno de los textos del cartel baja de AA, subir
el scrim propio de la seccion antes de dar nada por hecho.

- [x] **Step 4: Anti-mock**

```bash
grep -rE "mockData|fakeData|hardcoded|TODO.*real|// fake|demo_data|placeholder|lorem ipsum|Lorem" \
  src/ --include="*.ts" --include="*.tsx"
```

Esperado: sin resultados en las secciones publicadas.

- [x] **Step 5: Los otros dos temas, intactos**

Capturar Hyprland y Caelestia en 1440x900 y comprobar que la seccion sigue siendo
la lista de pildoras de siempre, con el friso oculto.

- [x] **Step 6: Capturas finales**

`?theme=vice` en 1440x900 y 390x844. Confirmar: cartel centrado sin recuadros,
pie a dos alturas que no salta, friso con la marca activa encendida, cero errores
de consola.

- [x] **Step 7: Actualizar traspaso y PROGRESS.json, y commit**

```bash
git add .docs/HANDOFF-creditos-cartel.md PROGRESS.json
git commit -m "docs(credits): cerrar el traspaso del cartel de reparto"
```

---

## Riesgos conocidos

1. **Contraste.** Es el riesgo real de esta tarea: el cartel quita el scrim de
   `.credits-list` y el fondo es la bruma generativa. Medir, no asumir.
2. **`getIconMarkup` lanza.** Un slug mal escrito en `content.ts` tumba los tres
   temas, no solo Vice. La Task 1 lo cubre, pero es el fallo mas facil de meter.
3. **Los dos sitios de la fuente.** Tocar solo uno degrada a la via lenta en
   silencio, sin error visible. La asercion del Step 4 de la Task 2 lo detecta.
4. **Hijos de `[data-credit-roll]`.** La asercion `hijos == 29` de la Task 3 es la
   guarda; si alguien mete separadores o el friso dentro, salta ahi y no tres
   tareas despues.

---

## Estado: COMPLETADO y mergeado a `main` (29-jul-2026)

Las ocho tareas se ejecutaron y estan commiteadas. Merge a `main` en `5211743`
(`--no-ff`, siguiendo la forma que ya usaba `4187de5` para la rama de rediseno).

Verificacion de cierre: `npm run build` verde, `npx eslint src/` limpio,
`scripts/verify.py` en sus 12 fallos de base (todos fixtures de `public/media`,
previos a esta rama) y cero fallos de contraste — 35 elementos de la escena de
creditos medidos, el peor a 6.97:1 sobre un minimo de 3.0. Cero errores de
consola. Hyprland y Caelestia sin cambios.

`npm run lint` (eslint sobre todo el repo) esta en rojo por causa **ambiental**,
no por este trabajo: existe un worktree de otra sesion en
`.claude/worktrees/about-afirmacion-prueba` y typescript-eslint se niega a elegir
`tsconfigRootDir` con dos candidatos, asi que falla el parseo de los 33 ficheros
del repo tambien. `npx eslint src/` sale limpio.

### Divergencias respecto a lo planificado

Cuatro, todas posteriores al plan y todas con su motivo medido:

1. **Cuatro bloques de 8/5/5/5, no seis de 6/5/5/2/3/2.** Se decidio despues del
   gate visual, sobre mockup vivo. Tres bloques de dos y tres nombres se leian
   como sobras. Se descarto el 6/5/5/7 porque el rotulo mentiria: Electron y GTK4
   no son herramientas con las que se trabaja, son aquello con lo que se
   construye la interfaz. Afecta al Step 2 de la Task 1 (`skillGroups`) y al
   Step 5 (la asercion es de **4** encabezados, no 6). Commit `cd2a784`.
2. **Interlineado 2.75, no 2.7** (Task 6, Step 1). Por debajo de 860px el clamp
   del cuerpo resuelve al minimo exacto de 1rem, asi que 16 x 2.75 = 44px justos
   y 2.7 se quedaba en 43.2.
3. **El separador va DETRAS del nombre anterior**, no delante del siguiente
   (Task 5, Step 3). Se implemento como `.credit + .credit::before` y se cambio a
   `.credit:has(+ .credit)::after` al medir dos defectos: el subrayado del activo
   cubria el punto anterior y al partir linea la linea abria con el punto, que se
   lee como vineta. Commit `82f92d4`.
4. **Cinco arreglos del gate visual que el plan no preveia**, porque salieron de
   la revision de vera y lidia: titulo de cartel para la escena, falso negrita
   fuera de la etiqueta, subrayado como segunda senal del activo, ancho de
   objetivo tactil y ratio de proximidad en movil. Commit `c01ef84`.

### Lo que NO entro, y sigue abierto

- Normalizar el juego de iconos del friso (F-006).
- El espacio vacio preexistente en Hyprland/Caelestia (F-009); vera lo dejo en
  "cuentalo, P0 a la tercera aparicion".
- El hueco largo antes de contacto en movil: es del padding de `[data-scene]`, no
  de esta escena.
- Zustand, que sigue fuera por no tener entrada en `simple-icons`.
