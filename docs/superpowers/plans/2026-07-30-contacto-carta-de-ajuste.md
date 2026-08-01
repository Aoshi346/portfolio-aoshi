# La carta de ajuste — plan de implementación

> **Para agentes:** SUB-SKILL OBLIGATORIA: usa `superpowers:subagent-driven-development`
> (recomendada) o `superpowers:executing-plans` para ejecutar tarea a tarea. Los pasos usan
> casillas (`- [ ]`) para el seguimiento. **Marca cada casilla en el momento en que terminas su
> paso**, no al final de la tarea (`.claude/rules/speckit-progress-tracking.md`).

**Objetivo:** rehacer la escena de contacto de Vice como una carta de ajuste con barras-gelatina,
cerrar la escala tipográfica del tema entera y dar al sitio una navegación de corte seco.

**Arquitectura:** un solo DOM para los tres temas, como todo el proyecto: `contacto.ts` monta
una banda de título y cuatro barras a partir de `contactChannels` (nuevo, en `content.ts`), y
quien decide la piel es el CSS. Vice pinta las barras como gelatinas translúcidas para que el
fondo generativo siga vivo debajo; Hyprland y Caelestia las apilan en vertical con estilo base.
La escala tipográfica pasa a ser diez tokens en `themes.css` y todo `clamp()` del tema apunta a
ellos. La navegación es un componente nuevo fuera de `.cinema-chrome`, porque ese contenedor es
`aria-hidden="true"` y los tres temas necesitan el menú.

**Stack:** Vite 8, TypeScript estricto, Tailwind 4, GSAP 3 + ScrollTrigger, Lenis. Sin
framework, sin Three.js, **sin framework de test**: lo que aquí hace de test son los scripts de
medida con Playwright sobre el build de producción.

## Spec

`docs/superpowers/specs/2026-07-30-contacto-carta-de-ajuste-design.md`. Léelo entero antes de
empezar: contiene los diez criterios de aceptación con su instrumento y su umbral.

## Restricciones globales

Copiadas literales del spec y de `CLAUDE.md`. Aplican a **todas** las tareas.

- **Cero `gsap.from`.** Siempre `fromTo` con los dos extremos escritos a mano, y
  `Array.from(...)` para colecciones vivas.
- **Cero `any`.** `strict` está puesto; usa `unknown` con guardas si hace falta.
- **Cero `console.log`** en código de producción.
- **Cero emojis** en código, docs y commits.
- **Nada de `innerHTML` con datos externos.** El contenido propio de `content.ts` sí puede.
- **`rel="noopener noreferrer"`** en todo enlace con `target="_blank"`.
- **`prefers-reduced-motion`** tiene degradación en cada gesto nuevo.
- **Limpieza obligatoria:** todo módulo que monte algo devuelve un handle con `destroy()` y se
  llama en `pagehide`.
- **Un `transform` inline de GSAP gana siempre a una regla CSS.** Si un elemento recibe entrada
  con GSAP, su hover se anima en un hijo o en el envoltorio.
- **Una animación CSS con `fill-mode: both` retiene su `transform` al terminar y gana a la regla
  del hover.** Usa `backwards`. Ya mordió en la maqueta.
- **Medir siempre en el build de producción** (`npm run build && npm run preview`, puerto 4173),
  **nunca en dev**: el HMR de Vite corrompe las medidas de ScrollTrigger. Y siempre con
  `?theme=vice`, que el tema se sortea por visita.
- **`npm run build` verde es requisito de DONE** en cada tarea. `npm run lint` limpio también.
- Node 22 es obligatorio para construir (`export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`).
  Con Node 18 el build de rolldown revienta con `styleText`.
- **Nunca `git stash` para comparar contra HEAD**: `git worktree add`. Ya se llevó por delante
  una sesión entera.

## Estructura de ficheros

| fichero | responsabilidad |
|---|---|
| `src/data/content.ts` (modificar) | añade `identity.invitation` y `contactChannels`. Única fuente de contenido |
| `src/sections/contacto.ts` (reescribir) | monta banda de título + cuatro barras. Sin decisiones de piel |
| `src/style.css` (modificar) | estilo base de la escena nueva, el que ven Hyprland y Caelestia |
| `src/themes/themes.css` (modificar) | tokens de la escala + piel Vice de la carta de ajuste + piel de la navegación |
| `src/themes/vice.choreography.ts` (modificar) | `scene5Contact` reescrito, sin `gsap.from` |
| `src/components/sceneNav.ts` (crear) | navegación de corte seco. Handle con `destroy()` |
| `src/main.ts` (modificar) | ids de escena, monta la navegación, la desmonta en `pagehide` |
| `scripts/measure-type-scale.py` (crear) | audita tamaños tipográficos contra la escala |
| `scripts/measure-contacto.py` (crear) | geometría, dianas, contraste y movimiento reducido de la escena |
| `scripts/measure-nav.py` (crear) | precisión de aterrizaje de cada ancla, cinco escenas por tres temas |
| `docs/superpowers/plans/2026-07-30-obra-rail-ritmo.md` (modificar) | tabla de mesetas re-medida tras la escala |

---

## Tarea 1: la escala tipográfica del tema

**Ficheros:**
- Modificar: `src/themes/themes.css` (bloque de tokens de Vice)
- Modificar: `src/style.css` (`.display-xl`, `.display-lg`, `.lead`, `.hero-kick`)
- Crear: `scripts/measure-type-scale.py`

**Interfaces:**
- Produce: diez custom properties `--t-1` … `--t-10` en `:root[data-theme="vice"]`. Todas las
  tareas siguientes usan estos nombres y **ningún tamaño literal en píxeles**.

- [x] **Paso 1: escribe el arnés que falla**

Crea `scripts/measure-type-scale.py`:

```python
"""Audita que ningun tamano tipografico de Vice cae fuera de la escala.

Se mide en el build de produccion (puerto 4173) con ?theme=vice, y con
prefers-reduced-motion: el layout puro se mide sin animacion, o se acaban
midiendo fotogramas de la entrada en vez de la maquetacion.
"""
import sys
from playwright.sync_api import sync_playwright

ESCALA = [12, 16, 21.33, 28.43, 37.90, 50.52, 67.40, 89.85, 119.77, 159.66]
TOLERANCIA = 0.5  # px: el redondeo del navegador, no una licencia de diseno
ANCHOS = [(390, 844), (1440, 900)]


def fuera_de_escala(valor: float) -> bool:
    return all(abs(valor - paso) > TOLERANCIA for paso in ESCALA)


def main() -> int:
    fallos = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        for ancho, alto in ANCHOS:
            pg = b.new_page(viewport={"width": ancho, "height": alto}, reduced_motion="reduce")
            pg.goto("http://localhost:4173/?theme=vice", wait_until="networkidle", timeout=30000)
            pg.wait_for_timeout(2000)
            medidas = pg.evaluate(
                """() => {
                    const out = [];
                    for (const n of document.querySelectorAll('[data-scene] *')) {
                      if (!n.textContent || !n.textContent.trim()) continue;
                      if (n.children.length) continue;   // solo hojas: el texto vive ahi
                      const r = n.getBoundingClientRect();
                      if (!r.width || !r.height) continue;
                      out.push({
                        px: parseFloat(getComputedStyle(n).fontSize),
                        escena: n.closest('[data-scene]').dataset.scene,
                        clase: n.className || n.tagName.toLowerCase(),
                      });
                    }
                    return out;
                }"""
            )
            for m in medidas:
                if fuera_de_escala(m["px"]):
                    fallos.append(f"{ancho}x{alto} {m['escena']} {m['clase']} -> {m['px']}px")
            pg.close()
        b.close()

    vistos = sorted(set(fallos))
    for f in vistos:
        print("FUERA DE ESCALA:", f)
    print(f"\n{len(vistos)} tamanos fuera de escala")
    return 1 if vistos else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Paso 2: córrelo y comprueba que falla**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && (npm run preview &) && sleep 3
python3 scripts/measure-type-scale.py
```

Esperado: FALLA. Debe listar al menos los 10,56 px y los 9,6 px de contacto y los títulos de
escena a 152 / 73,6 / 64 / 57,6 px.

Anota el número exacto de fallos: es la línea base de la tarea.

- [x] **Paso 3: declara los tokens**

En `src/themes/themes.css`, dentro del bloque `:root[data-theme="vice"]` que ya declara los
tokens del tema, añade:

```css
  /*
   * Escala tipografica del tema: cuarta, razon 1,333, base 16, suelo duro 12.
   * Existe porque los tamanos del tema iban por su tercera aparicion en la
   * auditoria visual (10,56 y 9,6 en contacto; 152 / 73,6 / 64 / 57,6 en los
   * titulos de escena, que eran cuatro tamanos para un mismo papel).
   *
   * Dos reglas, y son parte de la escala tanto como los numeros:
   *   1. Todo clamp() lleva LOS DOS extremos en pasos de esta escala.
   *   2. Maximo cuatro tamanos por encuadre.
   */
  --t-1: 12px;
  --t-2: 16px;
  --t-3: 21.33px;
  --t-4: 28.43px;
  --t-5: 37.9px;
  --t-6: 50.52px;
  --t-7: 67.4px;
  --t-8: 89.85px;
  --t-9: 119.77px;
  --t-10: 159.66px;
```

- [x] **Paso 4: aplica la escala escena por escena**

Sustituye cada tamaño literal por su paso. Los que salen del arnés del paso 2 y sus destinos:

| dónde | antes | después |
|---|---|---|
| `.hero-kick` (`style.css`) | tamaño propio | `font-size: var(--t-1)` |
| `.lead` (`style.css`) | tamaño propio | `font-size: var(--t-3)` |
| `.display-lg` (`style.css`) | clamp propio | `font-size: clamp(var(--t-5), 5vw, var(--t-7))` |
| `.display-xl` (`style.css`) | clamp propio | `font-size: clamp(var(--t-7), 9vw, var(--t-10))` |
| título de escena en obra, créditos y contacto | 73,6 / 57,6 / 64 | `clamp(var(--t-6), 6vw, var(--t-7))` |
| rótulos de 10,56 y 9,6 en contacto | dos tamaños | `var(--t-1)`, uno solo |

Los tokens solo existen bajo `:root[data-theme="vice"]`. En `style.css`, que es compartido,
declara el respaldo en la propia función para no romper Hyprland ni Caelestia:

```css
.hero-kick {
  font-size: var(--t-1, 0.75rem);
}
```

- [x] **Paso 5: córrelo y comprueba que pasa**

```bash
npm run build && python3 scripts/measure-type-scale.py
```

Esperado: `0 tamanos fuera de escala`, en 390x844 y en 1440x900.

Si queda alguno, arréglalo. **No amplíes `ESCALA` ni `TOLERANCIA` para que pase**: eso convierte
el arnés en un sello de goma, que es exactamente el modo de fallo que ya tuvo el gate documental
de este proyecto.

- [x] **Paso 6: comprueba que los otros dos temas siguen en pie**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for t in ['hyprland','caelestia']:
        pg = b.new_page(viewport={'width':1440,'height':900})
        errs = []
        pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.goto(f'http://localhost:4173/?theme={t}', wait_until='networkidle', timeout=30000)
        pg.wait_for_timeout(3000)
        alto = pg.evaluate('document.documentElement.scrollHeight')
        print(t, 'alto', alto, 'errores', errs)
        pg.close()
    b.close()
"
```

Esperado: los dos con altura de documento distinta de cero y cero errores de consola.

- [x] **Paso 7: commit**

```bash
git add src/themes/themes.css src/style.css scripts/measure-type-scale.py
git commit -m "feat(themes): escala tipografica de Vice en diez pasos, con arnes"
```

---

## Tarea 2: rehacer la tabla de mesetas del carril de obra

Va **después** de la escala y **antes** de tocar contacto: la escala mueve la maquetación del
carril, y una tabla de traspaso desactualizada no falla, miente.

**Ficheros:**
- Modificar: `docs/superpowers/plans/2026-07-30-obra-rail-ritmo.md` (tabla de mesetas)

**Interfaces:**
- Consume: la escala de la Tarea 1 ya aplicada.

- [x] **Paso 1: re-mide con el instrumento que ya existe**

```bash
npm run build && (npm run preview &) && sleep 3
python3 scripts/measure-obra-rail.py
```

`scripts/measure-obra-rail.py` reimplementa la timeline maestra del carril para saber dónde
*debería* estar la pista. Si `OBRA_TRANSIT` u `OBRA_REST` de `vice.choreography.ts` cambian, hay
que cambiarlos también ahí: desincronizados no fallan, mienten.

- [x] **Paso 2: comprueba las cinco mesetas**

Las posiciones nominales son `u = 0,225 / 1,675 / 3,125 / 4,575 / 6,025`. Compara la salida con
la tabla del plan del carril.

- [x] **Paso 3: actualiza la tabla con los números nuevos**

Sustituye los valores de la tabla y añade una línea debajo:

```markdown
> Re-medido el 2026-07-30 tras aplicar la escala tipográfica del tema
> (`docs/superpowers/plans/2026-07-30-contacto-carta-de-ajuste.md`, Tarea 2).
```

Si algún número **no** cambió, déjalo y dilo. Reescribir a ojo lo que no se movió es igual de
falso que dejar lo que sí.

- [x] **Paso 4: commit**

```bash
git add docs/superpowers/plans/2026-07-30-obra-rail-ritmo.md
git commit -m "docs(obra): mesetas del carril re-medidas tras la escala"
```

---

## Tarea 3: el contenido y el DOM de la escena

**Ficheros:**
- Modificar: `src/data/content.ts`
- Reescribir: `src/sections/contacto.ts`
- Modificar: `src/style.css` (estilo base de la escena, el de Hyprland y Caelestia)

**Interfaces:**
- Produce: `identity.invitation: string`; `contactChannels: ContactChannel[]`;
  `createContacto(): HTMLElement`.
- Produce, para la Tarea 4 (piel) y la Tarea 5 (coreografía), estas clases exactas:
  `.contacto-band`, `.contacto-title`, `.contacto-lead`, `.contacto-estado`,
  `.contacto-estado-label`, `.contacto-estado-sep`, `.contacto-estado-value`,
  `.contacto-bars`, `.contacto-bar`, `.contacto-bar-label`, `.contacto-bar-mark`,
  `.contacto-bar-value`, y el modificador `.contacto-bar--<key>` con
  `key ∈ {correo, linkedin, telefono, github}`.

- [x] **Paso 1: añade el contenido**

En `src/data/content.ts`, añade `invitation` a la interfaz `Identity` y al objeto:

```ts
  /**
   * La frase de la escena de cierre. Elegida por el autor entre once
   * alternativas: corta, en el lado de quien lee y sin prometer un plazo de
   * respuesta, que es la promesa mas facil de incumplir.
   */
  invitation: string;
```

```ts
  invitation: "Cuéntame tu idea.",
```

Y al final del fichero, las cuatro vías:

```ts
export interface ContactChannel {
  key: "correo" | "linkedin" | "telefono" | "github";
  label: string;
  /** Lo que se lee en pantalla. No siempre es el href: LinkedIn muestra el nombre. */
  value: string;
  href: string;
  external: boolean;
}

/**
 * Las cuatro barras de la carta de ajuste, en orden de encuadre. El correo va
 * primero porque es la via principal, y su barra es la unica en magenta.
 */
export const contactChannels: ContactChannel[] = [
  {
    key: "correo",
    label: "Correo",
    value: identity.email,
    href: `mailto:${identity.email}`,
    external: false,
  },
  {
    key: "linkedin",
    label: "LinkedIn",
    value: identity.name,
    href: identity.linkedin,
    external: true,
  },
  {
    key: "telefono",
    label: "Teléfono",
    value: identity.phone,
    // Sin espacios ni guiones: el marcador del movil no los tolera.
    href: `tel:${identity.phone.replace(/[^+\d]/g, "")}`,
    external: false,
  },
  {
    key: "github",
    label: "GitHub",
    value: "Aoshi346",
    href: identity.github,
    external: true,
  },
];
```

- [x] **Paso 2: reescribe la sección**

Sustituye `src/sections/contacto.ts` entero:

```ts
import { contactChannels, identity, type ContactChannel } from "../data/content";
import { el } from "../utils/dom";

/**
 * Cierre del portfolio: carta de ajuste. Termino la emision y lo que queda en
 * pantalla es como localizar a quien emite — cuatro barras a sangre, una por
 * via, sobre una banda de titulo.
 *
 * Un solo DOM para los tres temas. Vice pinta las barras como gelatinas
 * translucidas para que el fondo generativo siga vivo debajo; Hyprland y
 * Caelestia las apilan en vertical con el estilo base de style.css.
 */
function createBar(channel: ContactChannel): HTMLAnchorElement {
  const bar = el("a", `contacto-bar contacto-bar--${channel.key}`, [
    el("span", "contacto-bar-label", [channel.label]),
    el("span", "contacto-bar-mark", []),
    // El dato se lee SIEMPRE, sin hover: en tactil no hay hover y el correo no
    // puede depender de el.
    el("span", "contacto-bar-value", [channel.value]),
  ]) as HTMLAnchorElement;

  bar.href = channel.href;
  if (channel.external) {
    bar.target = "_blank";
    bar.rel = "noopener noreferrer";
  }
  return bar;
}

export function createContacto(): HTMLElement {
  const estado = el("p", "contacto-estado", [
    el("span", "contacto-estado-label", ["Estado"]),
    // El mismo separador con el que el sitio ya escribe un estado en el chrome
    // de cine ("05 · Fundido"), no una chapa con punto latiendo.
    el("span", "contacto-estado-sep", ["·"]),
    el("span", "contacto-estado-value", [identity.availability]),
  ]);

  const band = el("div", "contacto-band", [
    el("p", "hero-kick", ["Contacto"]),
    el("h2", "contacto-title display-xl", ["Hablemos"]),
    el("p", "contacto-lead", [identity.invitation]),
    estado,
  ]);

  const bars = el("div", "contacto-bars", contactChannels.map(createBar));

  const section = el("section", "contacto relative flex min-h-screen flex-col", [band, bars]);
  section.setAttribute("data-scene", "contacto");
  return section;
}
```

- [x] **Paso 3: estilo base para los otros dos temas**

En `src/style.css`, junto al resto de estilo base de secciones:

```css
/*
 * Estilo base de la carta de ajuste: el que ven Hyprland y Caelestia. Aqui las
 * barras no son barras, son una lista de vias apilada. La piel de Vice
 * (themes.css) es la que las pone a sangre y en horizontal.
 */
.contacto-band {
  padding: 4rem 1.5rem 2rem;
}

.contacto-lead {
  font-size: var(--t-3, 1.25rem);
  margin-top: 1rem;
}

.contacto-estado {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 2rem;
  font-size: var(--t-2, 1rem);
}

.contacto-estado-label {
  font-size: var(--t-1, 0.75rem);
  letter-spacing: 0.24em;
  text-transform: uppercase;
  opacity: 0.6;
}

.contacto-bars {
  display: flex;
  flex-direction: column;
}

.contacto-bar {
  display: block;
  /* 24x24 CSS px es el minimo de WCAG 2.2 AA SC 2.5.8. El pie anterior media
     14,4 px de alto y lo incumplia. */
  min-height: 3.5rem;
  padding: 1rem 1.5rem;
  text-decoration: none;
}

.contacto-bar-label {
  display: block;
  font-size: var(--t-1, 0.75rem);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  opacity: 0.6;
}

.contacto-bar-value {
  display: block;
  font-size: var(--t-3, 1.25rem);
  margin-top: 0.25rem;
}

.contacto-bar-mark {
  display: block;
  width: 1.75rem;
  height: 2px;
  margin: 0.5rem 0;
  background: currentColor;
  opacity: 0.5;
}
```

- [x] **Paso 4: comprueba que compila y que los tres temas montan la escena**

```bash
npm run build && npm run lint
(npm run preview &) && sleep 3
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for t in ['vice','hyprland','caelestia']:
        pg = b.new_page(viewport={'width':1440,'height':900})
        errs = []
        pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.goto(f'http://localhost:4173/?theme={t}', wait_until='networkidle', timeout=30000)
        pg.wait_for_timeout(3000)
        print(t, pg.evaluate('''() => ({
          barras: document.querySelectorAll('.contacto-bar').length,
          frase: document.querySelector('.contacto-lead')?.textContent,
          estado: document.querySelector('.contacto-estado-value')?.textContent,
        })'''), 'errores', errs)
        pg.close()
    b.close()
"
```

Esperado en los tres: `barras: 4`, `frase: 'Cuéntame tu idea.'`,
`estado: 'Disponible para proyectos'`, cero errores.

- [x] **Paso 5: comprueba que no quedan restos del DOM viejo**

```bash
grep -rn "contacto-mail\|contacto-status\|contacto-corner\|contacto-phone\|contacto-github" src/
```

Esperado: solo aparecen en `themes.css` (los limpia la Tarea 4) y en
`vice.choreography.ts` (los limpia la Tarea 5). **Cero apariciones en `src/sections/`.**

- [x] **Paso 6: commit**

```bash
git add src/data/content.ts src/sections/contacto.ts src/style.css
git commit -m "feat(contacto): carta de ajuste — cuatro vias desde content.ts"
```

---

## Tarea 4: la piel de Vice

**Ficheros:**
- Modificar: `src/themes/themes.css` (sustituye el bloque "fundido de cierre", líneas ~1676-1850)
- Modificar: `src/style.css` (retira el estilo base del DOM viejo — ver Paso 1b)

**Interfaces:**
- Consume: las clases de la Tarea 3.
- Produce: la escena con la geometría que miden las Tareas 7 y 8.

- [x] **Paso 1: borra el bloque viejo**

En `src/themes/themes.css`, elimina las reglas de `.contacto-mail`, `.contacto-status`,
`.contacto-corner` y `.contacto .hero-surface`. Son la piel de un DOM que ya no existe.

- [x] **Paso 1b: y el estilo base huérfano de `src/style.css`**

Añadido el 2026-07-31: lo levantó el implementador de la Tarea 3 al correr el grep del Paso 5.
La Tarea 3 se llevó por delante el DOM que producía `.contacto-mail`, `.contacto-github`,
`.contacto-phone` y `.contacto-corner`, pero **ninguna tarea tenía asignada la retirada de su
estilo base**: la 4 solo hablaba de `themes.css` y la 5 solo de la coreografía. Es CSS muerto e
inofensivo — selectores que ya no casan con nada — pero se retira aquí, junto a su gemelo de
`themes.css`, en vez de dejarlo para que confunda a quien lea el fichero dentro de seis meses.

**No es un borrado a ciegas, y aquí está la trampa:** cinco de esas reglas están *agrupadas* con
`.hero-mail` / `.hero-corner`, que **siguen vivos** (`src/sections/hero.ts:26,29`). Son las que
dan al hero su `transition`, su `:hover`, su `:focus-visible`, su `:active` y su degradación bajo
`prefers-reduced-motion`. Borrar los bloques enteros dejaría al hero **sin foco visible sobre el
vídeo**, que es justo el defecto de accesibilidad que esas reglas se escribieron para tapar (lo
dicen sus propios comentarios). Retira **solo las líneas de selector `.contacto-*`** y deja el
resto del bloque intacto.

- Reglas de las que se quitan selectores, conservando `.hero-mail`: la de `transition`
  (~línea 259), `:hover` (~269), `:focus-visible` (~277), `:active` (~287) y las dos del bloque
  `@media (prefers-reduced-motion: reduce)` (~308 y ~319).
- Reglas que se eliminan **enteras**, porque no las comparte nadie: `.contacto-mail` (~218,
  con su comentario), el bloque `.contacto-github, .contacto-phone, .contacto-corner a`
  (~241-247, con su comentario sobre el azul del UA stylesheet) y `.contacto-corner` (~337,
  con su comentario del scrim).
- Los comentarios de otras reglas que citan `.contacto-mail` como ejemplo (~27, ~203, ~257,
  ~469) documentan un fallo de contraste real y su remedio: **no los borres**, reescribe la
  referencia para que apunte a `.hero-kick`, que sigue existiendo y ejemplifica lo mismo.

Comprobación del paso: `npm run build` verde, y una captura del hero con foco en el enlace de
correo (`page.focus(".hero-mail")`) que enseñe el outline. Si el outline no está, has borrado de
más.

- [x] **Paso 2: escribe la piel nueva**

```css
/*
 * Fundido de cierre — carta de ajuste. Termino la emision: cuatro barras a
 * sangre con como localizar a quien emite.
 *
 * Las barras son GELATINAS de iluminacion, no color opaco: filtros
 * translucidos delante del foco. El fondo generativo sigue vivo debajo y se
 * tine al pasar. Con barras opacas el shader quedaria tapado en el 56% de la
 * pantalla final, que es tirar lo que mas caracteriza al sitio.
 */
:root[data-theme="vice"] .contacto {
  justify-content: flex-start;
  padding: 0;
}

:root[data-theme="vice"] .contacto-band {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 39vh;
  padding: 0 3rem 2.2rem;
}

:root[data-theme="vice"] .contacto-title {
  font-size: clamp(var(--t-7), 9vw, var(--t-9));
  line-height: 0.84;
  margin-top: 0.9rem;
}

:root[data-theme="vice"] .contacto-lead {
  font-size: var(--t-3);
  font-weight: 300;
  line-height: 1.42;
  max-width: 46ch;
  color: rgb(255 244 232 / 0.85);
}

:root[data-theme="vice"] .contacto-estado {
  width: max-content;
  margin-top: 2.1rem;
  gap: 0;
  cursor: default;
}

:root[data-theme="vice"] .contacto-estado-label {
  font-size: var(--t-1);
  font-weight: 700;
  color: rgb(255 244 232 / 0.5);
  transition: color 340ms ease-out;
}

:root[data-theme="vice"] .contacto-estado-sep {
  margin: 0 0.95rem;
  font-size: var(--t-2);
  color: rgb(255 244 232 / 0.34);
  transition: color 340ms ease-out;
}

:root[data-theme="vice"] .contacto-estado-value {
  position: relative;
  padding: 0.56rem 0.82rem;
  margin: -0.56rem -0.82rem;
  font-size: var(--t-2);
  font-weight: 600;
  color: var(--accent-amber, #ffd166);
}

/*
 * Al pasar por encima, el encuadre se cierra sobre el dato: las mismas marcas
 * de esquina que enmarcan el hero, aqui alrededor de una sola linea. Se
 * descarto la pastilla redondeada con punto latiendo — es el componente mas
 * repetido de la web y no pertenece a este sitio.
 */
:root[data-theme="vice"] .contacto-estado-value::before,
:root[data-theme="vice"] .contacto-estado-value::after {
  content: "";
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid var(--accent-amber, #ffd166);
  opacity: 0;
  transition:
    opacity 260ms ease-out,
    top 480ms cubic-bezier(0.22, 1, 0.36, 1),
    left 480ms cubic-bezier(0.22, 1, 0.36, 1),
    right 480ms cubic-bezier(0.22, 1, 0.36, 1),
    bottom 480ms cubic-bezier(0.22, 1, 0.36, 1);
}

:root[data-theme="vice"] .contacto-estado-value::before {
  top: -7px;
  left: -7px;
  border-right: 0;
  border-bottom: 0;
}

:root[data-theme="vice"] .contacto-estado-value::after {
  bottom: -7px;
  right: -7px;
  border-left: 0;
  border-top: 0;
}

:root[data-theme="vice"] .contacto-estado:hover .contacto-estado-value::before {
  opacity: 1;
  top: 0;
  left: 0;
}

:root[data-theme="vice"] .contacto-estado:hover .contacto-estado-value::after {
  opacity: 1;
  bottom: 0;
  right: 0;
}

:root[data-theme="vice"] .contacto-estado:hover .contacto-estado-label,
:root[data-theme="vice"] .contacto-estado:hover .contacto-estado-sep {
  color: var(--accent-amber, #ffd166);
}

/* --- las barras --- */
:root[data-theme="vice"] .contacto-bars {
  flex: 1;
  flex-direction: row;
}

:root[data-theme="vice"] .contacto-bar {
  position: relative;
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  overflow: hidden;
  padding: 0 0 1.9rem;
  box-shadow: inset 1px 0 0 rgb(255 244 232 / 0.16);
  backdrop-filter: saturate(1.25);
  transition: flex-grow 520ms cubic-bezier(0.22, 1, 0.36, 1);
}

:root[data-theme="vice"] .contacto-bar:hover,
:root[data-theme="vice"] .contacto-bar:focus-visible {
  flex-grow: 2.6;
}

:root[data-theme="vice"] .contacto-bar--correo { background: rgb(255 46 136 / 0.3); }
:root[data-theme="vice"] .contacto-bar--linkedin { background: rgb(255 209 102 / 0.26); }
:root[data-theme="vice"] .contacto-bar--telefono { background: rgb(255 244 232 / 0.15); }
:root[data-theme="vice"] .contacto-bar--github { background: rgb(11 5 19 / 0.55); }

/*
 * La tinta bajo el valor NO es adorno: sobre un fondo generativo la luminancia
 * se mueve, y sin ella el contraste del dato deja de estar garantizado. Es lo
 * que hace que el criterio 4 del spec sea medible en vez de depender del
 * fotograma que toque.
 */
:root[data-theme="vice"] .contacto-bar::after {
  content: "";
  position: absolute;
  inset: auto 0 0 0;
  height: 190px;
  z-index: -1;
  background: linear-gradient(to top, rgb(11 5 19 / 0.82) 0%, rgb(11 5 19 / 0) 100%);
}

:root[data-theme="vice"] .contacto-bar-label {
  position: absolute;
  top: 2.1rem;
  left: 1.75rem;
  writing-mode: vertical-rl;
  /* var(--t-5), no 34px: 34 no es un paso de la escala y la Tarea 1 acaba de
     cerrarla. El valor de la maqueta se sube al paso mas cercano hacia arriba. */
  font-size: var(--t-5);
  font-weight: 700;
  letter-spacing: 0.34em;
  color: rgb(255 244 232 / 0.34);
  opacity: 1;
  transition: color 420ms ease-out;
}

:root[data-theme="vice"] .contacto-bar:hover .contacto-bar-label {
  color: rgb(255 244 232 / 0.55);
}

:root[data-theme="vice"] .contacto-bar-value {
  margin: 0 1.75rem;
  font-size: var(--t-4);
  font-weight: 600;
  white-space: nowrap;
  color: rgb(255 244 232 / 1);
  transform-origin: left bottom;
  transition: transform 520ms cubic-bezier(0.22, 1, 0.36, 1);
}

:root[data-theme="vice"] .contacto-bar:hover .contacto-bar-value {
  transform: scale(1.14);
}

:root[data-theme="vice"] .contacto-bar-mark {
  margin: 0 1.75rem 1rem;
  width: 28px;
  height: 2px;
  background: var(--accent-amber, #ffd166);
  opacity: 0.8;
  transition:
    width 520ms cubic-bezier(0.22, 1, 0.36, 1),
    opacity 420ms ease-out;
}

:root[data-theme="vice"] .contacto-bar:hover .contacto-bar-mark {
  width: 120px;
  opacity: 1;
}

:root[data-theme="vice"] .contacto-bar:focus-visible {
  outline: 3px solid var(--accent-amber, #ffd166);
  outline-offset: -6px;
}

/* En vertical las barras no caben en fila: se apilan y el rotulo vuelve a
   horizontal, que en 390px de ancho es lo unico legible. */
@media (max-width: 900px) {
  :root[data-theme="vice"] .contacto-bars {
    flex-direction: column;
  }

  :root[data-theme="vice"] .contacto-bar {
    flex: 1 1 auto;
    min-height: 5.5rem;
    justify-content: center;
    padding: 1rem 1.5rem;
  }

  :root[data-theme="vice"] .contacto-bar-label {
    position: static;
    writing-mode: horizontal-tb;
    font-size: var(--t-1);
    letter-spacing: 0.2em;
  }

  :root[data-theme="vice"] .contacto-bar-value {
    margin: 0.4rem 0 0;
    font-size: var(--t-3);
  }

  :root[data-theme="vice"] .contacto-bar-mark {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="vice"] .contacto-bar,
  :root[data-theme="vice"] .contacto-bar-value,
  :root[data-theme="vice"] .contacto-bar-mark,
  :root[data-theme="vice"] .contacto-estado-value::before,
  :root[data-theme="vice"] .contacto-estado-value::after {
    transition: none;
  }

  :root[data-theme="vice"] .contacto-bar:hover,
  :root[data-theme="vice"] .contacto-bar:focus-visible {
    flex-grow: 1;
  }

  :root[data-theme="vice"] .contacto-bar:hover .contacto-bar-value {
    transform: none;
  }

  :root[data-theme="vice"] .contacto-estado:hover .contacto-estado-value::before {
    top: -7px;
    left: -7px;
  }

  :root[data-theme="vice"] .contacto-estado:hover .contacto-estado-value::after {
    bottom: -7px;
    right: -7px;
  }
}
```

- [x] **Paso 3: mira la escena de verdad**

```bash
npm run build && (npm run preview &) && sleep 3
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for w,h,n in [(1440,900,'escritorio'),(390,844,'movil')]:
        pg = b.new_page(viewport={'width':w,'height':h})
        pg.goto('http://localhost:4173/?theme=vice', wait_until='domcontentloaded', timeout=30000)
        pg.wait_for_timeout(9000)
        pg.evaluate('''() => document.querySelector('[data-scene=\"contacto\"]').scrollIntoView()''')
        pg.wait_for_timeout(3500)
        pg.screenshot(path=f'/tmp/contacto-{n}.png')
        pg.close()
    b.close()
"
```

Ábrelas. Un `tsc` verde no garantiza que el encuadre esté bien.

- [x] **Paso 4: commit**

```bash
git add src/themes/themes.css src/style.css
git commit -m "feat(vice): piel de la carta de ajuste con barras-gelatina"
```

---

## Tarea 5: la coreografía, sin `gsap.from`

**Ficheros:**
- Modificar: `src/themes/vice.choreography.ts` (`CONTACT_TRIGGER_IDS` y `scene5Contact`, ~1218-1310)

**Interfaces:**
- Consume: las clases de la Tarea 3.
- Produce: `scene5Contact` sin un solo `gsap.from`.

- [x] **Paso 1: comprueba la deuda antes de tocar nada**

```bash
grep -n "gsap.from(" src/themes/vice.choreography.ts
```

Esperado ahora mismo: tres apariciones dentro de `scene5Contact` (kick, status, mail).

- [x] **Paso 2: reescribe la escena**

Sustituye el cuerpo de `scene5Contact` por:

```ts
function scene5Contact(gsap: Gsap, ScrollTrigger: ScrollTriggerApi, root: HTMLElement): void {
  const contacto = root.querySelector<HTMLElement>('[data-scene="contacto"]');
  if (!contacto) return;

  for (const id of CONTACT_TRIGGER_IDS) ScrollTrigger.getById(id)?.kill();

  const base = { trigger: contacto, start: "top 68%", toggleActions: "play none none reverse" } as const;
  const kick = contacto.querySelector<HTMLElement>(".hero-kick");
  const title = contacto.querySelector<HTMLElement>(".contacto-title");
  const lead = contacto.querySelector<HTMLElement>(".contacto-lead");
  const estado = contacto.querySelector<HTMLElement>(".contacto-estado");
  const bars = contacto.querySelectorAll<HTMLElement>(".contacto-bar");

  /*
   * `fromTo` con los dos extremos escritos a mano, nunca `from`: `from` deduce
   * el extremo final leyendo el DOM y ya dejo los tres enlaces del pie
   * invisibles para siempre en esta misma escena. Y ahora hay un camino de
   * ejecucion nuevo — llegar desde la navegacion con el trigger ya pasado —
   * donde ese error seria permanente.
   */
  if (kick) {
    gsap.fromTo(
      kick,
      { opacity: 0, y: 14 },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power2.out",
        scrollTrigger: { ...base, id: CONTACT_TRIGGER_IDS[0] },
      },
    );
  }
  if (title) {
    // "Hablemos" se monta letra a letra: cierra la pieza con el mismo gesto
    // con el que se abrio el nombre.
    composeTitle(gsap, title, base, CONTACT_TRIGGER_IDS[1], 0.08);
  }
  if (lead) {
    gsap.fromTo(
      lead,
      { opacity: 0, y: 14 },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power2.out",
        delay: 0.22,
        scrollTrigger: { ...base, id: CONTACT_TRIGGER_IDS[2] },
      },
    );
  }
  if (estado) {
    gsap.fromTo(
      estado,
      { opacity: 0, y: 12 },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        ease: "power2.out",
        delay: 0.3,
        scrollTrigger: { ...base, id: CONTACT_TRIGGER_IDS[3] },
      },
    );
  }
  if (bars.length) {
    /*
     * Las barras suben desde el suelo, escalonadas. Se anima `yPercent` y no
     * `flex-grow`: el hover ya usa `flex-grow`, y animar la misma propiedad
     * desde dos sitios deja la barra encallada a mitad de camino.
     */
    gsap.fromTo(
      Array.from(bars),
      { opacity: 0, yPercent: 12 },
      {
        opacity: 1,
        yPercent: 0,
        duration: 0.62,
        ease: "power3.out",
        stagger: 0.07,
        delay: 0.38,
        scrollTrigger: { ...base, id: CONTACT_TRIGGER_IDS[4] },
      },
    );
  }
}
```

- [x] **Paso 3: comprueba que la deuda está saldada**

```bash
grep -c "gsap.from(" src/themes/vice.choreography.ts
```

Esperado: `0`.

- [x] **Paso 4: comprueba que la escena se compone y que llegar por navegación no la deja invisible**

```bash
npm run build && (npm run preview &) && sleep 3
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=vice', wait_until='domcontentloaded', timeout=30000)
    pg.wait_for_timeout(9000)
    # salto seco al final, como hara la navegacion: el trigger queda ya pasado
    pg.evaluate('window.scrollTo({top: document.body.scrollHeight, behavior: \"instant\"})')
    pg.wait_for_timeout(3500)
    print(pg.evaluate('''() => {
      const q = s => getComputedStyle(document.querySelector(s)).opacity;
      return {
        kick: q('[data-scene=\"contacto\"] .hero-kick'),
        lead: q('.contacto-lead'),
        estado: q('.contacto-estado'),
        barras: [...document.querySelectorAll('.contacto-bar')].map(b => getComputedStyle(b).opacity),
      };
    }'''))
    b.close()
"
```

Esperado: **todas las opacidades a 1**. Una sola en `0` significa que quien llega por el menú se
encuentra la escena vacía, que es exactamente el fallo que los `gsap.from` hacían posible.

- [x] **Paso 5: commit**

```bash
git add src/themes/vice.choreography.ts
git commit -m "fix(vice): scene5Contact sin gsap.from y adaptada a la carta de ajuste"
```

---

## Tarea 6: la navegación de corte seco

**Ficheros:**
- Crear: `src/components/sceneNav.ts`
- Modificar: `src/main.ts`
- Modificar: `src/themes/themes.css` (piel de la navegación)
- Crear: `scripts/measure-nav.py`

**Interfaces:**
- Produce: `mountSceneNav(root: HTMLElement): { destroy: () => void }`.
- Produce: ids de escena `#hero`, `#quien-es`, `#obra`, `#creditos`, `#contacto`.

- [ ] **Paso 1: escribe el arnés que falla**

Crea `scripts/measure-nav.py`:

```python
"""Precision de aterrizaje de cada ancla, en las cinco escenas y los tres temas.

Umbral: |y_reposo - y_destino| <= 8 px, medido tras 3,5 s de asentamiento de
Lenis. Lenis sigue desplazando la pagina despues de un scrollTo: medir antes de
que asiente da falsos positivos.
"""
import sys
from playwright.sync_api import sync_playwright

TOLERANCIA = 8
ANCLAS = ["hero", "quien-es", "obra", "creditos", "contacto"]
TEMAS = ["vice", "hyprland", "caelestia"]


def main() -> int:
    fallos = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        for tema in TEMAS:
            for ancla in ANCLAS:
                pg = b.new_page(viewport={"width": 1440, "height": 900})
                pg.goto(f"http://localhost:4173/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
                pg.wait_for_timeout(9000)  # leader de apertura + GSAP + shader
                enlace = pg.query_selector(f'.scene-nav a[href="#{ancla}"]')
                if enlace is None:
                    fallos.append(f"{tema} #{ancla}: no hay enlace")
                    pg.close()
                    continue
                destino = pg.evaluate("() => window.__navDestino__?.('%s')" % ancla)
                enlace.click()
                pg.wait_for_timeout(3500)  # asentamiento de Lenis
                reposo = pg.evaluate("window.scrollY")
                if destino is None:
                    fallos.append(f"{tema} #{ancla}: sin destino calculado")
                elif abs(reposo - destino) > TOLERANCIA:
                    fallos.append(f"{tema} #{ancla}: reposo {reposo:.0f} vs destino {destino:.0f}")
                else:
                    print(f"OK {tema} #{ancla}: {reposo:.0f} (destino {destino:.0f})")
                pg.close()
        b.close()

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} anclas fuera de tolerancia")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Paso 2: córrelo y comprueba que falla**

```bash
python3 scripts/measure-nav.py
```

Esperado: FALLA con `no hay enlace` en las quince combinaciones. Hoy `nav a` es 0 en todo el
documento.

- [ ] **Paso 3: pon ids a las escenas**

En `src/main.ts`, tras componer `main` y antes de `app.append(...)`:

```ts
/*
 * Ids de escena para las anclas de la navegacion. Se ponen aqui y no en cada
 * factoria porque el carril de obra no es una escena sino un envoltorio de
 * cinco, y su ancla tiene que apuntar al carril.
 */
const ANCHOR_IDS: Record<string, string> = {
  hero: "hero",
  about: "quien-es",
  credits: "creditos",
  contacto: "contacto",
};
for (const [scene, id] of Object.entries(ANCHOR_IDS)) {
  main.querySelector<HTMLElement>(`[data-scene="${scene}"]`)?.setAttribute("id", id);
}
obraRail.id = "obra";
```

- [ ] **Paso 4: escribe el componente**

Crea `src/components/sceneNav.ts`:

```ts
/**
 * Navegacion de escenas. Corte seco, decidido sobre la alternativa de un
 * desplazamiento de un segundo: la continuidad ya la da el scroll normal, y
 * quien usa el menu lo usa justamente porque no quiere recorrer el camino.
 *
 * Vive FUERA de `.cinema-chrome`: ese contenedor es `aria-hidden="true"` y una
 * navegacion escondida del arbol de accesibilidad no es una navegacion. Ademas
 * los tres temas la necesitan y el cromo de cine solo corre en Vice.
 */
interface NavTarget {
  id: string;
  label: string;
}

const TARGETS: NavTarget[] = [
  { id: "hero", label: "Título" },
  { id: "quien-es", label: "Quién es" },
  { id: "obra", label: "Obra" },
  { id: "creditos", label: "Créditos" },
  { id: "contacto", label: "Fundido" },
];

/*
 * El carril de obra se recorre en horizontal dentro de un pin. Su borde de
 * inicio deja la primera cartela a medio montar: el fotograma asentado esta en
 * u ~ 0,42 de los 6,25 que dura la timeline maestra. Se lee EN EL MOMENTO del
 * clic y nunca se cachea: el presupuesto del pin cambia con cada refresh de
 * ScrollTrigger.
 */
const OBRA_SETTLED_U = 0.42;
const OBRA_TOTAL_U = 6.25;

function destinationFor(id: string): number | null {
  const target = document.getElementById(id);
  if (!target) return null;

  const top = target.getBoundingClientRect().top + window.scrollY;

  if (id === "obra") {
    // La altura del envoltorio menos una pantalla es el recorrido que el pin
    // reserva. Si el carril no esta fijado (Hyprland, Caelestia, movil) el
    // termino sale <= 0 y el destino es el borde, que es lo correcto ahi.
    const budget = Math.max(0, target.offsetHeight - window.innerHeight);
    return top + (OBRA_SETTLED_U / OBRA_TOTAL_U) * budget;
  }

  return top;
}

export function mountSceneNav(root: HTMLElement): { destroy: () => void } {
  const nav = document.createElement("nav");
  nav.className = "scene-nav";
  nav.setAttribute("aria-label", "Secciones");

  const list = document.createElement("ul");
  for (const target of TARGETS) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    // Ancla real en el href: sin JavaScript sigue navegando, y el navegador
    // la muestra al pasar por encima.
    link.href = `#${target.id}`;
    link.textContent = target.label;
    item.append(link);
    list.append(item);
  }
  nav.append(list);

  /*
   * UN solo punto de ejecucion del desplazamiento, delegado en el `ul`. Y
   * nunca se escribe `location.hash`: eso dispara el salto nativo del
   * navegador y competiria con este.
   */
  const onClick = (event: MouseEvent): void => {
    const link = (event.target as HTMLElement).closest<HTMLAnchorElement>("a[href^='#']");
    if (!link) return;
    const id = link.hash.slice(1);
    const destination = destinationFor(id);
    if (destination === null) return;

    event.preventDefault();
    /*
     * `behavior: "instant"` explicito. `html { scroll-behavior: smooth }` hace
     * que "auto" acabe resolviendo a suave, incluso con prefers-reduced-motion
     * puesto — que es justo el camino donde Lenis no existe para corregirlo.
     */
    window.scrollTo({ top: destination, behavior: "instant" });
    history.replaceState(null, "", `#${id}`);
  };

  list.addEventListener("click", onClick);
  root.append(nav);

  // Sonda para scripts/measure-nav.py. No afecta al render.
  (window as unknown as { __navDestino__?: (id: string) => number | null }).__navDestino__ =
    destinationFor;

  return {
    destroy: () => {
      list.removeEventListener("click", onClick);
      nav.remove();
      delete (window as unknown as { __navDestino__?: unknown }).__navDestino__;
    },
  };
}
```

- [ ] **Paso 5: móntala y desmóntala en `main.ts`**

Junto al resto de handles, antes del `pagehide`:

```ts
const sceneNavHandle = mountSceneNav(app);
```

Con su import arriba (`import { mountSceneNav } from "./components/sceneNav";`) y dentro del
`pagehide` que ya existe:

```ts
    sceneNavHandle.destroy();
```

- [ ] **Paso 6: dale piel**

En `src/themes/themes.css`:

```css
/*
 * Navegacion: fija abajo a la derecha, fuera del cromo de cine. Diana de
 * 44x44 px, holgada sobre los 24x24 que exige WCAG 2.2 AA SC 2.5.8 — el pie
 * anterior media 14,4 px de alto y lo incumplia.
 */
.scene-nav {
  position: fixed;
  right: 1.5rem;
  bottom: 1.5rem;
  z-index: 40;
}

.scene-nav ul {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.15rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.scene-nav a {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 44px;
  min-height: 44px;
  padding: 0 0.9rem;
  font-size: var(--t-1, 0.75rem);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  text-decoration: none;
  color: currentColor;
  opacity: 0.55;
  transition: opacity 260ms ease-out;
}

.scene-nav a:hover,
.scene-nav a:focus-visible {
  opacity: 1;
}

:root[data-theme="vice"] .scene-nav a:hover,
:root[data-theme="vice"] .scene-nav a:focus-visible {
  color: var(--accent-amber, #ffd166);
}

@media (prefers-reduced-motion: reduce) {
  .scene-nav a {
    transition: none;
  }
}
```

- [ ] **Paso 7: córrelo y comprueba que pasa**

```bash
npm run build && (npm run preview &) && sleep 3
python3 scripts/measure-nav.py
```

Esperado: `0 anclas fuera de tolerancia`, quince combinaciones en verde.

Si falla solo `#obra`, el sospechoso es el presupuesto del pin: **comprueba que no estás
midiendo la ventana del pin contra `distance`**. El pin reserva 5.040 px y el recorrido lateral
es de 5.760: son cosas distintas y confundirlas ya costó una sesión.

- [ ] **Paso 8: comprueba el camino sin ratón y el de movimiento reducido**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900}, reduced_motion='reduce')
    pg.goto('http://localhost:4173/?theme=vice', wait_until='domcontentloaded', timeout=30000)
    pg.wait_for_timeout(4000)
    pg.focus('.scene-nav a[href=\"#contacto\"]')
    pg.keyboard.press('Enter')
    pg.wait_for_timeout(3500)
    print('hash', pg.evaluate('location.hash'),
          '| entradas de historial anadidas:', pg.evaluate('history.length'))
    print('escena en cuadro:', pg.evaluate('''() => document
      .elementFromPoint(innerWidth/2, innerHeight/2)?.closest('[data-scene]')?.dataset.scene'''))
    b.close()
"
```

Esperado: `hash #contacto` y la escena en cuadro es `contacto`. Comprueba con
`document.elementFromPoint`, no con un selector: Lenis sigue moviendo la página después de un
`scrollTo` y anclar la comprobación a un selector da falsos positivos.

- [ ] **Paso 9: commit**

```bash
git add src/components/sceneNav.ts src/main.ts src/themes/themes.css scripts/measure-nav.py
git commit -m "feat(nav): navegacion de escenas con corte seco y arnes de aterrizaje"
```

---

## Tarea 7: el arnés de la escena y el contraste con el shader real

**Ficheros:**
- Crear: `scripts/measure-contacto.py`

**Interfaces:**
- Consume: la escena terminada (Tareas 3-5).
- Produce: los criterios 1, 2, 3, 4, 5 y 7 del spec, medidos.

- [ ] **Paso 1: escribe el arnés**

Crea `scripts/measure-contacto.py`:

```python
"""Arnes de la escena de contacto: geometria, dianas, contraste y reduced motion.

Criterios 1, 2, 3, 4, 5 y 7 del spec
docs/superpowers/specs/2026-07-30-contacto-carta-de-ajuste-design.md

El contraste se muestrea sobre el pixel RENDERIZADO, con el shader corriendo, en
tres fotogramas separados 2 s: el fondo es generativo y su luminancia se mueve.
Un solo fotograma no mide nada.
"""
import io
import sys
from PIL import Image
from playwright.sync_api import sync_playwright

DIANA_MIN = 24        # px CSS, WCAG 2.2 AA SC 2.5.8
HUECO_MAX = 120       # px sobre la primera letra
OCUPACION_MIN = 0.35  # fraccion del encuadre
CONTRASTE_MIN = 4.5
FOTOGRAMAS = 3


def luminancia(c):
    def canal(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * canal(c[0]) + 0.7152 * canal(c[1]) + 0.0722 * canal(c[2])


def ratio(a, b):
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def main() -> int:
    fallos = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto("http://localhost:4173/?theme=vice", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(9000)
        pg.evaluate("""() => {
            const s = document.querySelector('[data-scene="contacto"]');
            window.scrollTo({top: s.getBoundingClientRect().top + scrollY, behavior: 'instant'});
        }""")
        pg.wait_for_timeout(3500)

        geo = pg.evaluate("""() => {
            const vw = innerWidth, vh = innerHeight;
            const escena = document.querySelector('[data-scene="contacto"]');
            const titulo = document.querySelector('.contacto-title');
            const banda = document.querySelector('.contacto-band');
            const barras = [...document.querySelectorAll('.contacto-bar')];
            const tinta = [banda, ...barras].reduce((acc, n) => {
                const r = n.getBoundingClientRect();
                return acc + Math.max(0, r.width) * Math.max(0, r.height);
            }, 0);
            return {
                hueco_superior: titulo.getBoundingClientRect().top - escena.getBoundingClientRect().top,
                ocupacion: tinta / (vw * vh),
                dianas: barras.map(n => {
                    const r = n.getBoundingClientRect();
                    return [Math.round(r.width), Math.round(r.height)];
                }),
                valores: [...document.querySelectorAll('.contacto-bar-value')].map(n => {
                    const r = n.getBoundingClientRect();
                    return {x: r.left - 6, y: r.top + r.height / 2, color: getComputedStyle(n).color};
                }),
                estado: (() => {
                    const n = document.querySelector('.contacto-estado-value');
                    const r = n.getBoundingClientRect();
                    return {x: r.left + r.width * 0.3, y: r.top + r.height * 0.22,
                            color: getComputedStyle(n).color};
                })(),
            };
        }""")

        if geo["hueco_superior"] > HUECO_MAX:
            fallos.append(f"hueco_superior {geo['hueco_superior']:.0f} px > {HUECO_MAX}")
        if geo["ocupacion"] < OCUPACION_MIN:
            fallos.append(f"ocupacion {geo['ocupacion']:.1%} < {OCUPACION_MIN:.0%}")
        for i, (w, h) in enumerate(geo["dianas"]):
            if w < DIANA_MIN or h < DIANA_MIN:
                fallos.append(f"diana de la barra {i}: {w}x{h} px")

        # Contraste sobre el pixel renderizado, tres fotogramas separados 2 s.
        puntos = [(v["x"], v["y"], v["color"], f"valor {i}") for i, v in enumerate(geo["valores"])]
        puntos.append((geo["estado"]["x"], geo["estado"]["y"], geo["estado"]["color"], "estado"))
        for n in range(FOTOGRAMAS):
            im = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
            for x, y, color, nombre in puntos:
                fondo = im.getpixel((int(x), int(y)))
                fg = tuple(int(v) for v in color.replace("rgb(", "").replace(")", "").split(",")[:3])
                r = ratio(fg, fondo)
                if r < CONTRASTE_MIN:
                    fallos.append(f"fotograma {n}: {nombre} {r:.1f}:1 < {CONTRASTE_MIN}")
                else:
                    print(f"OK fotograma {n} {nombre}: {r:.1f}:1")
            pg.wait_for_timeout(2000)
        pg.close()

        # Movimiento reducido: el hover no mueve nada.
        pg = b.new_page(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        pg.goto("http://localhost:4173/?theme=vice", wait_until="networkidle", timeout=30000)
        pg.wait_for_timeout(3000)
        antes = pg.evaluate("""() => document.querySelector('.contacto-bar')
            .getBoundingClientRect().width""")
        pg.hover(".contacto-bar")
        pg.wait_for_timeout(900)
        despues = pg.evaluate("""() => document.querySelector('.contacto-bar')
            .getBoundingClientRect().width""")
        if abs(antes - despues) > 1:
            fallos.append(f"reduced motion: la barra se movio {antes:.0f} -> {despues:.0f}")
        else:
            print(f"OK reduced motion: la barra no se mueve ({antes:.0f} px)")
        pg.close()
        b.close()

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} criterios incumplidos")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Paso 2: córrelo**

```bash
npm run build && (npm run preview &) && sleep 3
python3 scripts/measure-contacto.py
```

Esperado: `0 criterios incumplidos`.

- [ ] **Paso 3: si el contraste falla en algún fotograma**

La corrección es **subir el relleno de la gelatina a un valor opaco**, no oscurecer el ámbar:
perder el ámbar es perder el tema. En `themes.css`, sube la alfa de la barra que falle y vuelve
a correr el arnés.

Si el fondo de esta escena todavía no está decidido en `main`, **para aquí y dilo**: los
criterios 4 y 5 se miden con el shader real o no se miden. Deja la casilla en `[!]` con el
motivo en línea y sigue con la Tarea 8.

- [ ] **Paso 4: commit**

```bash
git add scripts/measure-contacto.py
git commit -m "test(contacto): arnes de geometria, dianas, contraste y reduced motion"
```

---

## Tarea 8: el gate

**Ficheros:** ninguno nuevo. Aquí solo se verifica.

- [ ] **Paso 1: el arnés general**

```bash
npm run build && npm run lint
(npm run preview &) && sleep 3
python3 scripts/verify.py
```

Esperado: código de salida 0. Si aparece un fallo que no estaba en
`scripts/verify-baseline.json`, arréglalo. Si **arreglaste** uno que sí estaba, quítalo de la
base con `python3 scripts/verify.py --update-baseline` y revisa el diff antes de commitear.

- [ ] **Paso 2: los cuatro arneses de este encargo, seguidos**

```bash
python3 scripts/measure-type-scale.py && \
python3 scripts/measure-contacto.py && \
python3 scripts/measure-nav.py && \
python3 scripts/measure-obra-rail.py
```

Los cuatro en verde. **Córrelos de uno en uno y sin editar nada mientras corren**: `verify.py`
cae con "Execution context was destroyed" si tocas el árbol, porque el HMR de Vite se lleva el
contexto de la página por delante.

- [ ] **Paso 3: capturas reales**

Escritorio 1440x900 y móvil 390x844, con `?theme=vice`, de la escena de contacto y de una
navegación completa. Míralas.

- [ ] **Paso 4: anti-mock**

```bash
grep -rE "mockData|fakeData|hardcoded|TODO.*real|// fake|demo_data|placeholder|lorem ipsum|Lorem" \
  src/ --include="*.ts"
```

Esperado: sin resultados en las secciones publicadas.

- [ ] **Paso 5: los dos críticos**

Lanza `lidia-naive-tester` y `vera-art-director`. **Los dos leen su `memory.md` antes de actuar.**
Vera lleva dos versiones con la escala tipográfica abierta: dile explícitamente que esta entrega
la cierra, para que compruebe eso y no lo vuelva a levantar.

- [ ] **Paso 6: merge**

Solo con los dos críticos conformes y los cinco arneses en verde. La implementación va en
worktree aparte (`git worktree add`, nunca `git stash`); el merge a `main` se pide, no se hace.

---

## Autorrevisión

Repasado contra el spec:

- Criterio 1 (dianas) → Tarea 7, paso 1. Además la piel base y la de Vice dan
  `min-height` holgado, y la navegación 44x44.
- Criterio 2 (hueco superior) → Tarea 7. La causa (el `padding-top` de 202,5 px heredado de
  `[data-scene]`) la corrige la Tarea 4 con `padding: 0` en `.contacto`.
- Criterio 3 (ocupación) → Tarea 7.
- Criterios 4 y 5 (contraste) → Tarea 7, con los tres fotogramas y la vía de escape declarada.
- Criterio 6 (escala) → Tarea 1.
- Criterio 7 (movimiento reducido) → Tarea 7, y los bloques `@media` de la Tarea 4.
- Criterio 8 (navegación) → Tarea 6.
- Criterio 9 (cero `gsap.from`) → Tarea 5, pasos 1 y 3.
- Criterio 10 (arnés y build) → Tarea 8.
- Tabla del carril re-medida después de la escala → Tarea 2.
- Copy en `content.ts` → Tarea 3.
- No se toca Hyprland ni Caelestia salvo comprobar → Tareas 1, 3 y 6.

Nombres cruzados entre tareas: `contactChannels` y `ContactChannel` (T3) los consume solo T3;
`mountSceneNav` y `__navDestino__` (T6) los consume `measure-nav.py` (T6); las clases
`.contacto-*` las produce T3 y las consumen T4, T5 y T7 con la misma ortografía.
