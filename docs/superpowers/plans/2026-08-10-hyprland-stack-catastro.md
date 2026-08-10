# El catastro — "Con qué construyo" en Hyprland · plan de implementación

> **Para quien ejecute esto:** SUB-SKILL OBLIGATORIA: usar
> `superpowers:subagent-driven-development` (recomendada) o
> `superpowers:executing-plans` para implementar tarea a tarea. Los pasos usan
> casillas (`- [ ]`) y hay que marcarlas **al completar cada paso**, no al final
> (`.claude/rules/speckit-progress-tracking.md`).

**Objetivo:** convertir `[data-scene="credits"]` en el tema Hyprland en un catastro de cuatro
parcelas cuyo ancho es proporcional a cuántas tecnologías contiene cada una, con su propia
franja de detalle al pie, sin tocar el contenido ni los otros dos temas.

**Arquitectura:** patrón aditivo estricto. Los nodos nuevos se construyen en
`src/components/credits.ts` para los tres temas y nacen **ocultos** desde la regla base de
`src/style.css`; solo `:root[data-theme="hyprland"]` los enciende. **La lista sigue siendo
plana** — `scene4Credits` de Vice anima los hijos directos de `[data-credit-roll]` y un
envoltorio por grupo reduciría su escalonado de 27 a 4 —, así que la columnización se hace con
propiedades personalizadas inline (`--skill-col`, `--skill-row`) sobre `display: contents`. La
composición vive en CSS; la coreografía reparte clases y decide *cuándo*, nunca *cuánto* dura.

**Stack:** Vite + TypeScript estricto + CSS propio en `src/themes/themes.css` + GSAP/ScrollTrigger
ya presentes. Sin dependencias nuevas.

**Spec:** `docs/superpowers/specs/2026-08-10-hyprland-stack-catastro-design.md`
**Prototipo aprobado:** `.superpowers/brainstorm/2892129-1786377307/content/catastro-v2.html`

## Restricciones globales

- **Solo Hyprland.** Vice está cerrado desde el 2026-08-05 y no se toca. Caelestia no se toca:
  se comprueba que sigue idéntico.
- **`src/data/content.ts` no cambia.** Ni una cadena nueva. Si algo hace falta y no está, se
  para y se pregunta.
- **La lista NO se envuelve por grupo.** Ni ahora ni como "refactor de limpieza".
- **Todo nodo nuevo lleva `display: none` en la regla base compartida** de `src/style.css`. Se
  ha pagado cuatro veces; la última ensanchó el disparador de Vice de 168 a 411px.
- **El acento no marca rango entre elementos comparables.** Los 23 nombres son comparables
  entre sí: su nivel va en `--text`/`--haze` y solo el apuntado recibe `--l3`. El recuento de
  cada parcela sí va en `--l1` en las cuatro cabeceras — hay uno por territorio, no es
  seleccionable y no cambia de estado, así que no compite con el naranja del apuntado.
- **Nunca `gsap.from`.** `fromTo` con los dos extremos escritos a mano. `Array.from(...)` para
  colecciones vivas.
- **Nada de `clamp()` sobre tokens de escala.** Escalones discretos por `@container`/`@media`.
- **Dos regímenes de tiempo y ningún tercero:** corte 420ms `--hard`
  (`cubic-bezier(0.7,0,0.2,1)`), atmósfera 900ms `--slow` (`cubic-bezier(0.16,0.84,0.28,1)`).
  Escalonado entre territorios 90ms.
- **Prohibido animar** `filter`, `backdrop-filter` y `box-shadow` con blur sobre los 23 nodos, y
  `width`/`height` (usar `transform: scale()`). Hay un shader WebGL a pantalla completa en rAF
  continuo detrás.
- **Las 23 lámparas se quedan en CSS; GSAP no toca más de 13 nodos** (4 carriles, 4 rótulos, 4
  chispas, 1 tween compartido sobre las 4 franjas). **No hay techo numérico de animaciones
  concurrentes** — se probó y se descartó (ronda de arreglo 1 de la tarea 8): el diseño exige 23
  lámparas de `color` (barato, no dispara layout) y por construcción casi todas se solapan
  — medido, muestreo cada 16ms separando "en efecto" de "produciendo valores de verdad"
  (`effect.getComputedTiming().progress !== null`): las dos cuentas COINCIDEN siempre
  (`1/1 1/1 1/1 14/14 23/23 22/22 21/21 20/20 18/18 15/15 13/13 10/10`), así que ni filtrar por
  fase activa evita el pico de 23. Una cuenta cruda de `document.getAnimations()` no distingue
  eso de 23 tweens de GSAP caros — lo que vigila el arnés es el mecanismo: cada `.credit`
  visible mantiene `animationName === 'hypr-lampara'` (si alguien las pasa a GSAP, ese nombre
  desaparece) y la timeline de `window.__hyprSkills` no toca más de 13 targets que sean
  Elementos reales.
- **`prefers-reduced-motion` nunca deja nada invisible.**
- **Cero `console.log`. Cero `any`.**
- **Node 22 obligatorio.** El del sistema es v18.19.1 y `rolldown-vite` necesita `styleText` de
  `node:util` (Node ≥20). Sin prefijo de entorno (el harness lo rechaza), invocar el binario
  entero:
  - `tsc`: `/root/.nvm/versions/node/v22.22.3/bin/node node_modules/typescript/bin/tsc`
  - `build`: `/root/.nvm/versions/node/v22.22.3/bin/node node_modules/vite/bin/vite.js build`
  - `preview`: `/root/.nvm/versions/node/v22.22.3/bin/node node_modules/vite/bin/vite.js preview`
- **Playwright:** `p.chromium.launch(headless=True, args=["--no-sandbox","--use-gl=swiftshader"])`.
  Sin `executable_path`: `/usr/bin/chromium-browser` no existe en esta máquina.
- **Medir contra el build de producción** (`vite preview`, puerto 4173), no contra `npm run dev`:
  el HMR corrompe las medidas de ScrollTrigger y miente en los dos sentidos.
- **`verify.py` cae con "Execution context was destroyed" si se toca el árbol mientras corre.**
  Correrlo solo y sin editar nada.
- **Para comparar contra `HEAD` usar `git worktree add`, NUNCA `git stash`.**

## Estructura de ficheros

| Fichero | Responsabilidad |
|---|---|
| `src/components/credits.ts` | Construye los nodos nuevos y **calcula** la colocación en rejilla y el nivel de cada tecnología. Solo estructura y datos; ni una clase de tema, ni un estilo. |
| `src/style.css` (regla base) | `display: none` de los nodos nuevos, para los tres temas. |
| `src/themes/themes.css` (bloque Hyprland) | El catastro: rejilla, parcelas, cabeceras, mojones, nombres, franjas, apuntado y móvil. Sustituye al bloque "el reparto". |
| `src/themes/themes.css` (bloque Vice) | Una sola regla de neutralización de las filas de friso. |
| `src/themes/hypr.choreography.ts` | Gesto 0c (reparto de clases y retardos) y gesto 4 (la corriente y el apuntado). Nada de duraciones propias salvo las dos curvas del tema. |
| `scripts/measure-catastro.py` | Arnés propio: visibilidad, cotas de los pies, acento en reposo, desbordes, alto y calles en móvil, diana táctil, y que los otros dos temas no se movieron. |
| `scripts/verify.py` | Actualizar la rama Hyprland del marcador 2, que queda obsoleta. |

## Vocabulario de ganchos (nombres definitivos, usados por todas las tareas)

| Gancho | Dónde | Qué es |
|---|---|---|
| `[data-credit-parcela]` | 4 nodos, hermanos en `.credits-grid` | Caja decorativa de columna. Dibuja el lindero y aloja la luz y la chispa. `aria-hidden`, `data-decorative`. |
| `[data-credit-strip]` | 4 nodos, hermanos en `.credits-grid` | La franja de detalle de cada parcela. `role="status"`, `aria-live="polite"`, id `credits-strip-<i>`. |
| `[data-credit-marks-row]` | 4 nodos, dentro de `.credits-marks` | Una fila de friso por parcela. Contiene los `.credits-mark` de ese grupo. Hyprland disuelve `.credits-marks` con `display: contents` para que las filas sean items de la rejilla; Vice disuelve las filas para conservar su friso de 23. |
| `--skill-col` / `--skill-row` | inline en labels y `.credit` | Colocación en la rejilla de escritorio. |
| `--skill-col-m` / `--skill-row-m` | inline en labels y `.credit` | Colocación en la rejilla de móvil. |
| `--skill-d` | inline en cada `.credit` | Retardo de su lámpara. **Es** la posición de la chispa. |
| `--parcela-cols` | inline en `.credits-grid` | `grid-template-columns` derivado del dato, p. ej. `8fr 5fr 5fr 5fr`. |
| `data-credit-tier` | en cada `.credit` | `alto` / `medio` / `bajo`. |
| `.is-caught` | en cada `.credit` | La lámpara ya prendió. La pone la coreografía. |

---

## Tarea 1 · El arnés, antes que nada

Se escribe primero y **hay que verlo rojo contra defectos reales**. La primera aserción no es
ceremonia: sin ella el arnés sale verde con el catastro apagado, porque los nodos existen en el
DOM de los tres temas desde que se añaden y una caja con `display: none` no desborda, no tiene
pies descuadrados y no lleva acento. Es el fallo exacto que ya se midió en la placa.

**Ficheros:**
- Crear: `scripts/measure-catastro.py`

**Interfaces:**
- Consume: nada.
- Produce: `python3 scripts/measure-catastro.py --url http://localhost:4173`, salida 0 sin
  fallos y 1 con ellos, imprimiendo una línea por fallo.

- [ ] **Paso 1: escribir el arnés**

```python
"""Arnes del catastro de "Con que construyo" en Hyprland.

Ocho aserciones, y todas nacieron de un fallo real o de una trampa ya pagada:

  1. El catastro se VE en Hyprland. Sin esto el arnes sale verde con todo
     apagado: los nodos existen en el DOM de los tres temas desde que se
     anaden, y una caja con `display: none` no desborda ni descuadra. Las
     otras siete aserciones se autoanulan si esta falta.
  2. Los cuatro pies cierran a la misma cota en escritorio. Con altura
     minima en vez de fija, la parcela cuyo cruce ocupa mas lineas sube su
     pie y el rectangulo deja de cerrar.
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
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

VIEWPORTS = [("escritorio", 1440, 900), ("movil", 390, 844)]
ACENTOS = {"rgb(255, 90, 52)", "rgb(255, 160, 60)"}  # --l1, --l3
CALLE_MOVIL = 26
DIANA_MINIMA = 44
ALTO_MAXIMO_MOVIL = 1100


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

            # 3. acento en reposo
            encendidos = pg.evaluate(
                "(acentos) => Array.from(document.querySelectorAll('[data-credit]'))"
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
                if len(set(cotas)) != 1:
                    fallos.append(f"[escritorio] los pies no cierran a la misma cota: {cotas}")
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
```

- [ ] **Paso 2: servir el build de producción y verlo ROJO**

```bash
/root/.nvm/versions/node/v22.22.3/bin/node node_modules/vite/bin/vite.js build
/root/.nvm/versions/node/v22.22.3/bin/node node_modules/vite/bin/vite.js preview --port 4173 &
python3 scripts/measure-catastro.py --url http://localhost:4173
```

Esperado: **falla** con `el catastro no se ve: 4 parcelas con caja` en los dos viewports, y
`0 fallos` en la parte de Vice/Caelestia. Si sale verde, el arnés está roto: no continúes.

- [ ] **Paso 3: commit**

```bash
git add scripts/measure-catastro.py
git commit -m "test(skills): arnes del catastro de Con que construyo"
```

---

## Tarea 2 · Los nodos nuevos, apagados en los tres temas

**Ficheros:**
- Modificar: `src/components/credits.ts`
- Modificar: `src/style.css` (regla base)
- Modificar: `src/themes/themes.css` (una regla de neutralización en Vice)

**Interfaces:**
- Produce: los ganchos de la tabla de vocabulario. `createCredits()` sigue devolviendo un
  `HTMLElement` con la clase `credits-grid`.

- [ ] **Paso 1: construir las 4 parcelas, las 4 franjas y las 4 filas de friso**

En `credits.ts`, **fuera** del bucle que llena `listChildren` y **fuera** de `.credits-list`.
Las franjas son hermanas de la lista por el mismo motivo escrito en el fichero para
`.credits-marks`: `scene4Credits` anima los hijos directos de `[data-credit-roll]` y meter 12
nodos ahí ahogaría el escalonado del cartel de Vice.

```ts
const parcelas: HTMLElement[] = [];
const strips: HTMLElement[] = [];
const markRows: HTMLElement[] = [];

groups.forEach((group, gi) => {
  /*
   * Caja decorativa de columna. NO es un envoltorio: la lista sigue plana y
   * esta caja es una hermana que ocupa la columna entera de la rejilla. Es
   * lo que permite tener un lindero continuo de arriba abajo y un sitio
   * donde vive la luz, sin agrupar los `.credit` bajo un padre.
   */
  const parcela = el("div", "credits-parcela", [
    el("span", "credits-rail", []),
    el("span", "credits-glow", []),
    el("span", "credits-spark", []),
  ]);
  parcela.setAttribute("data-credit-parcela", "");
  parcela.dataset.parcela = String(gi);
  parcela.setAttribute("aria-hidden", "true");
  parcela.setAttribute("data-decorative", "");
  parcelas.push(parcela);

  const strip = el("div", "credits-strip", [el("div", "credits-strip-in", [])]);
  strip.setAttribute("data-credit-strip", "");
  strip.dataset.parcela = String(gi);
  strip.id = `credits-strip-${gi}`;
  strip.setAttribute("role", "status");
  strip.setAttribute("aria-live", "polite");
  strips.push(strip);

  const row = el("div", "credits-marks-row", []);
  row.setAttribute("data-credit-marks-row", "");
  row.dataset.parcela = String(gi);
  row.setAttribute("aria-hidden", "true");
  row.setAttribute("data-decorative", "");
  markRows.push(row);
});
```

Dentro del bucle de items, cada `mark` deja de ir a `markNodes` y va a
`markRows[gi].appendChild(mark)`. El friso de Vice (`.credits-marks`) sigue existiendo y ahora
contiene las cuatro filas:

```ts
const frieze = el("div", "credits-marks", markRows);
```

Y el retorno:

```ts
return el("div", "credits-grid", [list, panel, frieze, ...parcelas, ...strips]);
```

- [ ] **Paso 2: apagar todo lo nuevo en la regla base**

En `src/style.css`, junto a `.credits-marks { display: none }` (línea 1300):

```css
/* Nodos del catastro de Hyprland. Nacen apagados para los tres temas y solo
   `:root[data-theme="hyprland"]` los enciende. El patron aditivo se ha roto
   cuatro veces por saltarse esto. */
.credits-parcela,
.credits-strip {
  display: none;
}
```

- [ ] **Paso 3: neutralizar las filas de friso en Vice**

En `src/themes/themes.css`, dentro del bloque de Vice, junto a `.credits-marks`:

```css
/* El friso pasa a tener cuatro filas (una por parcela) para Hyprland. Vice
   las disuelve para conservar su `flex-wrap` de 23 marcas en una sola caja:
   sin esto, su friso pasaria de 23 items a 4 y perderia el ajuste de linea. */
:root[data-theme="vice"] .credits-marks-row {
  display: contents;
}
```

- [ ] **Paso 4: comprobar que Vice y Caelestia no se han movido**

```bash
/root/.nvm/versions/node/v22.22.3/bin/node node_modules/typescript/bin/tsc
/root/.nvm/versions/node/v22.22.3/bin/node node_modules/vite/bin/vite.js build
python3 scripts/measure-catastro.py --url http://localhost:4173
```

Esperado: sigue fallando por visibilidad (correcto, aún no hay CSS de Hyprland), y **ni un
fallo nuevo** de Vice ni de Caelestia. Además, diff de píxeles del friso de Vice contra un
worktree del commit anterior — nunca `git stash`.

- [ ] **Paso 5: commit**

```bash
git add src/components/credits.ts src/style.css src/themes/themes.css
git commit -m "feat(skills): nodos del catastro, ocultos en los tres temas"
```

---

## Tarea 3 · La jerarquía y la colocación, calculadas desde el dato

Ni una cadena nueva en `content.ts`: todo sale de cruzar lo que ya hay.

**Ficheros:**
- Modificar: `src/components/credits.ts`

**Interfaces:**
- Produce: `data-credit-tier` (`alto`|`medio`|`bajo`) en cada `.credit`; `--skill-col`,
  `--skill-row`, `--skill-col-m`, `--skill-row-m`, `--skill-d` inline; `--parcela-cols` en
  `.credits-grid`.

- [ ] **Paso 0: la contabilidad que usan las tareas 3, 6, 8 y 9**

Antes de calcular nada hace falta poder encontrar las cosas por grupo. Se declara junto a
`parcelas`/`strips`/`markRows` de la tarea 2, y se rellena en el bucle:

```ts
const labels: HTMLElement[] = [];                       // un rotulo por grupo
const filasPorGrupo: HTMLButtonElement[][] = [];        // los botones de cada grupo
const marcasPorGrupo: Map<string, HTMLElement>[] = [];  // slug -> marca, O(1) por grupo
```

Y los atributos que hacen encontrable cada nodo desde la coreografía. `data-credit-group` hoy
es booleano: pasa a llevar el índice.

```ts
groupLabel.setAttribute("data-credit-group", String(gi));
row.dataset.parcela = String(gi);
parcela.style.setProperty("--parcela-i", String(gi));
strip.style.setProperty("--skill-col-strip", String(gi + 1));
strip.style.setProperty("--skill-span-m", String(3 + Math.ceil(group.items.length / 2)));
```

`marcasPorGrupo` sustituye al `Map` global `marks`: el mismo O(1) que ya había, pero por
parcela, porque el encendido de marca ahora es por territorio y no global.

- [ ] **Paso 1: el nivel, medido POR PARCELA**

```ts
/*
 * El nivel sale del dato: en cuantas obras aparece la tecnologia, cruzando
 * `stack` Y `tooling` — el mismo cruce que ya hace `toEntry`.
 *
 * Se normaliza contra el maximo de SU PROPIA parcela, no contra un maximo
 * global. Con vara global las cinco herramientas caen a cero y un cuarto del
 * catastro queda apagado, cuando `tooling` existe precisamente porque Git,
 * GitHub y las dos CLI estan en TODOS los proyectos: medirlas contra `stack`
 * las declara vacias siendo lo contrario. Y comparar entre territorios nunca
 * fue el mensaje de esta escena.
 */
type Tier = "alto" | "medio" | "bajo";

function tiersDeGrupo(group: SkillGroup): Map<string, Tier> {
  const cuenta = new Map<string, number>();
  for (const item of group.items) {
    cuenta.set(item.slug, toEntry(group.label, item).usedIn.length);
  }
  const max = Math.max(...cuenta.values());
  const tiers = new Map<string, Tier>();
  for (const [slug, n] of cuenta) {
    tiers.set(slug, n === 0 ? "bajo" : n === max ? "alto" : "medio");
  }
  return tiers;
}
```

En el bucle de items: `row.dataset.creditTier = tiers.get(item.slug) ?? "bajo";`

- [ ] **Paso 2: la colocación en la rejilla de escritorio**

```ts
const MAX_ITEMS = Math.max(...groups.map((g) => g.items.length)); // 8 hoy
const FILA_NOMBRES = 3; // 1 cabecera, 2 mojones, 3..(2+MAX) nombres, luego franja

/*
 * Los nombres se REPARTEN por el alto de la parcela, no se amontonan arriba:
 * las tres parcelas de 5 dejaban un agujero visible al pie y el recuento se
 * decia dos veces (ancho Y alto). Repartidos, la segunda senal pasa a ser
 * densidad. Las 5 filas de una parcela corta se estiran sobre las 8 ranuras
 * de la mas larga, asi que las cuatro parcelas miden lo mismo y las cuatro
 * chispas llegan abajo a la vez.
 */
function filaDe(i: number, n: number): number {
  if (n <= 1) return FILA_NOMBRES;
  return Math.round((i * (MAX_ITEMS - 1)) / (n - 1)) + FILA_NOMBRES;
}
```

En el bucle, sobre cada `row` y sobre cada `groupLabel`:

```ts
groupLabel.style.setProperty("--skill-col", String(gi + 1));
groupLabel.style.setProperty("--skill-row", "1");
// ...
row.style.setProperty("--skill-col", String(gi + 1));
row.style.setProperty("--skill-row", String(filaDe(i, group.items.length)));
// El retardo de la lampara ES la posicion de la chispa: si cambia la altura
// de fila y no cambia esto, el gesto miente. Los dos numeros van juntos.
row.style.setProperty("--skill-d", `${Math.round((i / Math.max(1, group.items.length - 1)) * 620)}ms`);
```

- [ ] **Paso 3: la colocación de móvil, acumulada**

```ts
/*
 * Movil: rejilla de DOS columnas por parcela, apiladas. Se calcula aqui y no
 * se deja a la colocacion automatica porque las franjas y los frisos
 * inactivos van en `display: none` y desaparecen del flujo, lo que
 * descuadraria una rejilla automatica.
 *
 * Por parcela: fila base = cabecera, +1 = mojones, +2.. = nombres de dos en
 * dos, y la franja al final.
 */
let filaM = 1;
groups.forEach((group, gi) => {
  const base = filaM;
  const filasNombres = Math.ceil(group.items.length / 2);
  labels[gi].style.setProperty("--skill-row-m", String(base));
  markRows[gi].style.setProperty("--skill-row-m", String(base + 1));
  group.items.forEach((_, i) => {
    const row = filasPorGrupo[gi][i];
    row.style.setProperty("--skill-col-m", String((i % 2) + 1));
    row.style.setProperty("--skill-row-m", String(base + 2 + Math.floor(i / 2)));
  });
  strips[gi].style.setProperty("--skill-row-m", String(base + 2 + filasNombres));
  filaM = base + 3 + filasNombres;
});
```

- [ ] **Paso 4: el ancho de cada parcela, derivado del dato**

```ts
const grid = el("div", "credits-grid", [list, panel, frieze, ...parcelas, ...strips]);
/*
 * El ancho de cada parcela es proporcional a cuantas tecnologias contiene:
 * el area en pantalla ES el dato. Sale de `content.ts`, no de una lista a
 * mano: si manana cambian los grupos, la proporcion se actualiza sola.
 */
grid.style.setProperty("--parcela-cols", groups.map((g) => `${g.items.length}fr`).join(" "));
```

- [ ] **Paso 5: comprobar el reparto de niveles**

```bash
/root/.nvm/versions/node/v22.22.3/bin/node node_modules/typescript/bin/tsc
/root/.nvm/versions/node/v22.22.3/bin/node node_modules/vite/bin/vite.js build
```

Y en el navegador, sobre el build servido:

```js
// Esperado exactamente esto:
//   alto:  Git, GitHub, TypeScript, Python, JavaScript, C
//   bajo:  7 nombres repartidos 1/2/3/1 entre las cuatro parcelas
Object.fromEntries(['alto','medio','bajo'].map(t => [t,
  Array.from(document.querySelectorAll(`[data-credit-tier="${t}"]`)).map(n => n.textContent.trim())]))
```

- [ ] **Paso 6: commit**

```bash
git add src/components/credits.ts
git commit -m "feat(skills): nivel por parcela y colocacion en rejilla del catastro"
```

---

## Tarea 4 · El catastro en escritorio

Sustituye entero al bloque `Hyprland: el reparto` de `src/themes/themes.css` (~líneas
4348-4409). Ese bloque **muere**: la prosa con barras es el defecto 5 del diagnóstico.

**Ficheros:**
- Modificar: `src/themes/themes.css`

- [ ] **Paso 1: la rejilla y las parcelas**

```css
/* ------------------------------------------------ Hyprland: el catastro */
/*
  EL CATASTRO — cuatro parcelas contiguas que se reparten el encuadre entero,
  con el ancho proporcional a cuantas tecnologias contiene cada una. El area
  en pantalla ES el dato. Radio 0, filetes de 1px, perimetro cerrado: la
  oposicion deliberada a las bandas del contacto, que van a sangre.

  La lista sigue PLANA (`display: contents`) porque `scene4Credits` de Vice
  anima los hijos directos de `[data-credit-roll]`. La columnizacion la
  hacen `--skill-col`/`--skill-row`, que credits.ts escribe inline y que Vice
  y Caelestia no leen.
*/
:root[data-theme="hyprland"] .credits-grid {
  display: grid;
  grid-template-columns: var(--parcela-cols);
  grid-template-rows: auto auto repeat(8, 1fr) auto;
  max-width: none;
  width: 100%;
  border: 1px solid var(--rule);
  /* Scrim propio: sin superficie, `--haze` a 15px cae por debajo de AA sobre
     la fase clara del fondo. El precedente es `.about-pairs` al 78%. */
  background: color-mix(in srgb, var(--void) 78%, transparent);
}

:root[data-theme="hyprland"] .credits-list {
  display: contents;
}

:root[data-theme="hyprland"] .credits-parcela {
  display: block;
  position: relative;
  grid-column: calc(var(--parcela-i) + 1);
  grid-row: 1 / -1;
  pointer-events: none;
}
:root[data-theme="hyprland"] .credits-parcela + .credits-parcela {
  border-left: 1px solid var(--rule);
}
```

`--parcela-i` lo escribe `credits.ts`: `parcela.style.setProperty("--parcela-i", String(gi))`.

- [ ] **Paso 2: cabecera, mojones, nombres y franja**

```css
:root[data-theme="hyprland"] .credit-group-label {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.6rem;
  grid-column: var(--skill-col);
  grid-row: var(--skill-row);
  margin: 0;
  padding: 0.95rem 1rem;
  border-bottom: 1px solid var(--rule);
  font-family: var(--font-body);
  font-size: var(--t-1);
  font-weight: 600;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--haze);
}

/*
 * Las cuatro filas de friso viven DENTRO de `.credits-marks`, que la regla
 * base apaga y solo Vice enciende. Sin disolver ese contenedor, las filas no
 * son items de la rejilla del catastro y su `grid-column` no aplica a nada:
 * el `display: contents` de aqui es lo que las sube un nivel. Es la imagen
 * simetrica de lo que Vice hace con las filas para conservar su friso de 23.
 */
:root[data-theme="hyprland"] .credits-marks {
  display: contents;
}

:root[data-theme="hyprland"] .credits-marks-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.62rem;
  grid-column: var(--skill-col);
  grid-row: 2;
  padding: 0.62rem 1rem;
  border-bottom: 1px solid var(--rule);
}
:root[data-theme="hyprland"] .credits-mark {
  width: 14px;
  height: 14px;
  color: var(--haze);
}

:root[data-theme="hyprland"] .credit {
  appearance: none;
  grid-column: var(--skill-col);
  grid-row: var(--skill-row);
  align-self: center;
  justify-self: start;
  width: auto;
  padding: 0.2rem 1rem;
  border: 0;
  background: none;
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: -0.014em;
  line-height: 1.2;
  color: var(--color-paper);
}
/* El nivel se dice SOLO con tipografia. El acento es estado. */
:root[data-theme="hyprland"] .credit[data-credit-tier="alto"]  { font-size: var(--t-4); }
:root[data-theme="hyprland"] .credit[data-credit-tier="medio"] { font-size: var(--t-3); }
:root[data-theme="hyprland"] .credit[data-credit-tier="bajo"]  {
  font-size: var(--t-2);
  color: var(--haze);
}
/* El rol se muestra una vez como cabecera de grupo, no por fila. Sigue en el
   DOM: es un gate del arnes, no deuda tecnica. */
:root[data-theme="hyprland"] .credit-role { display: none; }
/* La prosa con barras muere aqui. */
:root[data-theme="hyprland"] .credit:not(:last-child)::after { content: none; }

/* La franja: altura FIJA, no minima. Con minima, la parcela cuyo cruce ocupa
   mas lineas sube su pie y el rectangulo deja de cerrar. Medido: los cuatro
   pies a la misma cota. */
:root[data-theme="hyprland"] .credits-strip {
  display: block;
  grid-column: var(--skill-col-strip);
  grid-row: -2 / -1;
  height: 126px;
  padding: 0;
  border-top: 1px solid var(--rule);
  overflow: hidden;
  position: relative;
}
/* Los DOS nodos del rodillo van siempre en absoluto: cambiar de absoluto a
   estatico a mitad de gesto desplaza el contenido (un absoluto se posiciona
   contra la caja de padding) y pega un tiron al terminar. */
:root[data-theme="hyprland"] .credits-strip-in {
  position: absolute;
  inset: 0;
  padding: 0.75rem 1rem 0.875rem;
}

/* El panel compartido no se usa aqui: cada parcela tiene su propia franja.
   `display: none` lo saca tambien del arbol de accesibilidad, que es lo que
   evita dos regiones vivas anunciando a la vez. */
:root[data-theme="hyprland"] .credits-panel { display: none; }
```

`--skill-col-strip` lo escribe `credits.ts` igual que `--skill-col`.

- [ ] **Paso 3: verificar**

Build, `preview`, y `python3 scripts/measure-catastro.py`. Esperado: pasan las aserciones 1, 2
y 5 en escritorio. Siguen fallando las de móvil.

- [ ] **Paso 4: commit**

```bash
git add src/themes/themes.css
git commit -m "feat(skills): el catastro en escritorio, en lugar del reparto"
```

---

## Tarea 5 · La franja: contenido, cruce y siembra

**Ficheros:**
- Modificar: `src/components/credits.ts`

- [ ] **Paso 1: pintar una franja**

```ts
/*
 * Con 4 o 5 obras no se listan los proyectos: "Los cinco proyectos" dice mas
 * y ocupa menos. Listar los cinco no distingue nada y descuadraba el pie, que
 * tiene altura fija.
 */
function textoCruce(usedIn: string[]): string {
  if (usedIn.length === 5) return "Los cinco proyectos";
  if (usedIn.length === 4) return "Cuatro de los cinco proyectos";
  return "";
}

function pintarFranja(strip: HTMLElement, entry: CreditEntry): HTMLElement {
  const dentro = el("div", "credits-strip-in", []);
  const marca = elFromMarkup("credits-strip-mark", getIconMarkup(entry.slug));
  marca.setAttribute("aria-hidden", "true");
  marca.setAttribute("data-decorative", "");

  const hijos: HTMLElement[] = [
    el("div", "credits-strip-top", [marca, el("span", "credits-strip-name", [entry.name])]),
    el("p", "credits-strip-detail", [entry.detail]),
  ];

  if (entry.usedIn.length === 0) {
    const vacio = el("p", "credits-strip-none", ["Sin obra publicada"]);
    hijos.push(vacio);
  } else {
    const resumen = textoCruce(entry.usedIn);
    const items = resumen
      ? [el("span", "credits-used-item", [resumen])]
      : entry.usedIn.map((t) => el("span", "credits-used-item", [t]));
    hijos.push(el("div", "credits-used", [el("p", "credits-used-label", ["Aparece en"]), ...items]));
  }

  dentro.replaceChildren(...hijos);
  return dentro;
}
```

- [ ] **Paso 2: sembrar sin encender**

```ts
/*
 * La franja arranca LLENA para no dejar un hueco esperando interaccion, pero
 * llenar no es encender: en reposo todavia no ha pasado nada, asi que ningun
 * nombre lleva acento ni desplazamiento. Sembrar marcando el primero como
 * seleccionado producia un falso hover en movil.
 */
groups.forEach((group, gi) => {
  const primera = toEntry(group.label, group.items[0]);
  strips[gi].replaceChildren(pintarFranja(strips[gi], primera));
});
```

- [ ] **Paso 3: verificar las aserciones 3 y 4 del arnés**

Build, `preview`, arnés. Esperado: `acento en reposo: []` y cero franjas vacías, en los dos
viewports.

- [ ] **Paso 4: commit**

```bash
git add src/components/credits.ts src/themes/themes.css
git commit -m "feat(skills): contenido de la franja y siembra sin encender"
```

---

## Tarea 6 · Selección por parcela y accesibilidad

Hoy `select()` es global: una sola selección para las 23. Pasa a ser **una por parcela**.

**Ficheros:**
- Modificar: `src/components/credits.ts`

- [ ] **Paso 1: el `select()` por grupo**

```ts
/*
 * Una seleccion por parcela, no una global: cuatro franjas, cuatro
 * seleccionados a la vez. Es lo que pone la causa y el efecto en la misma
 * columna — de "otro bloque de la pagina" a 40-350px sin cruzar un lindero.
 */
const seleccionar = (gi: number, i: number): void => {
  const group = groups[gi];
  const entry = toEntry(group.label, group.items[i]);
  const filas = filasPorGrupo[gi];

  filas.forEach((otra, k) => {
    otra.classList.toggle("is-active", k === i);
    otra.setAttribute("aria-pressed", String(k === i));
  });
  for (const [slug, node] of marcasPorGrupo[gi]) {
    node.classList.toggle("is-active", slug === entry.slug);
  }
  strips[gi].replaceChildren(pintarFranja(strips[gi], entry));
};
```

Cada botón queda enganchado a `mouseenter`, `focus` y `click` con su `(gi, i)`, y apunta a su
propia franja: `row.setAttribute("aria-controls", `credits-strip-${gi}`)`.

- [ ] **Paso 2: comprobar el árbol de accesibilidad**

```python
# Exactamente 4 regiones live, y el panel compartido no aparece.
snap = pg.accessibility.snapshot()
```

Esperado: 4 nodos con `live: "polite"`, ninguno correspondiente a `.credits-panel`.

- [ ] **Paso 3: commit**

```bash
git add src/components/credits.ts
git commit -m "feat(skills): seleccion por parcela y region viva propia por franja"
```

---

## Tarea 7 · El catastro en móvil

**Ficheros:**
- Modificar: `src/themes/themes.css`

- [ ] **Paso 1: apilar, dos columnas, calles fijas**

```css
@media (max-width: 820px) {
  /*
   * Calle FIJA de 26px, no derivada del 5vw del tema: a 390px ese 5vw deja 20
   * y un rectangulo de borde duro queda casi a sangre.
   */
  :root[data-theme="hyprland"] .credits-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: none;
    grid-auto-rows: min-content;
    margin: 0 26px;
    width: auto;
  }
  /* La parcela decorativa no sobrevive al apilado: el lindero pasa al canto
     izquierdo de la rejilla y la luz se posiciona sobre la fila. */
  :root[data-theme="hyprland"] .credits-parcela {
    grid-column: 1 / -1;
    grid-row: var(--skill-row-m) / span var(--skill-span-m);
    border-left: 0;
  }
  :root[data-theme="hyprland"] .credit-group-label,
  :root[data-theme="hyprland"] .credits-marks-row,
  :root[data-theme="hyprland"] .credits-strip {
    grid-column: 1 / -1;
    grid-row: var(--skill-row-m);
  }
  :root[data-theme="hyprland"] .credit {
    grid-column: var(--skill-col-m);
    grid-row: var(--skill-row-m);
    min-height: 44px;
    display: flex;
    align-items: center;
    padding: 0.3rem 1.1rem;
  }
  /*
   * El friso solo en el territorio activo: con los cuatro a la vez son 23
   * iconos de 14px compitiendo con 23 nombres en 390px de ancho.
   */
  :root[data-theme="hyprland"] .credits-marks-row { display: none; }
  :root[data-theme="hyprland"] .credits-marks-row.is-open { display: flex; }
  /* Una sola franja abierta: la que se abre y la que se cierra lo hacen a la
     vez y con la misma duracion, asi que la altura total no cambia. */
  :root[data-theme="hyprland"] .credits-strip { display: none; height: 128px; }
  :root[data-theme="hyprland"] .credits-strip.is-open { display: block; }
}
```

La clase `is-open` la pone `seleccionar()` sobre la parcela, la fila de friso y la franja del
grupo tocado, y la quita de las otras tres. `--skill-span-m` lo escribe `credits.ts` como
`3 + filasNombres`.

- [ ] **Paso 2: verificar las aserciones de móvil**

Arnés. Esperado: alto < 1100, calles `[26, 26]`, diana ≥ 44, cero desbordes.

- [ ] **Paso 3: commit**

```bash
git add src/themes/themes.css src/components/credits.ts
git commit -m "feat(skills): el catastro en movil, rejilla de dos columnas"
```

---

## Tarea 8 · La entrada: "la corriente"

**Ficheros:**
- Modificar: `src/themes/hypr.choreography.ts`
- Modificar: `src/themes/themes.css` (las 23 lámparas, en CSS)

**Interfaces:**
- Consume: `[data-credit-parcela]`, `.credit`, `--skill-d`.
- Produce: la clase `.is-caught` en cada `.credit` y `--rail`/`--spark` en cada parcela.

- [ ] **Paso 1: las lámparas, en CSS**

Son 23 nodos: como animaciones CSS lo lleva el motor de estilo; como 23 tweens de GSAP
escribiendo estilo inline por fotograma, con un shader detrás, no.

```css
/*
 * El fotograma 100% es IDENTICO al valor de reposo y el relleno es
 * `backwards`, no `forwards`: una `animation` con `forwards` gana a una
 * `transition` en la cascada y dejaria el apuntado sin color. Es el primo
 * hermano del "transform inline de GSAP gana a la regla CSS".
 */
@keyframes hypr-lampara {
  0%   { opacity: 0.28; color: var(--haze); }
  35%  { opacity: 1; color: var(--catch); }
  100% { }
}
:root[data-theme="hyprland"] .credit.is-caught {
  animation: hypr-lampara 0.4s var(--hard) backwards;
  animation-delay: var(--skill-d);
}
```

- [ ] **Paso 2: el gesto, en la coreografía**

```ts
// Gesto 4 — la corriente. El orden ES el orden del argumento: primero el
// limite (el carril), luego el nombre del sitio (el rotulo), luego lo que hay
// dentro (los nombres), y al final donde se comprueba (las franjas). Si los
// nombres entraran antes que los rotulos, la escena diria "23 tecnologias
// agrupadas de alguna manera", que es lo que decia antes.
const parcelas = Array.from(root.querySelectorAll<HTMLElement>("[data-credit-parcela]"));
if (parcelas.length > 0) {
  const R = 0.09; // entre territorios, no los 70ms del paso interno del tema
  const tl = gsap.timeline({
    scrollTrigger: { id: `${ID}-skills`, trigger: parcelas[0], start: "top 82%", once: true },
  });

  parcelas.forEach((parcela, c) => {
    const at = c * R;
    const rail = parcela.querySelector<HTMLElement>(".credits-rail");
    const spark = parcela.querySelector<HTMLElement>(".credits-spark");
    const gi = parcela.dataset.parcela ?? "0";
    const label = root.querySelector<HTMLElement>(`[data-credit-group="${gi}"]`);
    const nombres = Array.from(
      root.querySelectorAll<HTMLElement>(`[data-credit][data-parcela="${gi}"]`),
    );

    if (rail) {
      tl.fromTo(
        rail,
        { scaleY: 0, transformOrigin: "0 0" },
        { scaleY: 1, duration: 0.5, ease: HARD, immediateRender: false },
        at,
      );
    }
    if (label) {
      tl.fromTo(
        label,
        { clipPath: "inset(0 100% 0 0)" },
        { clipPath: "inset(0 0% 0 0)", duration: 0.42, ease: HARD, immediateRender: false },
        at + 0.14,
      );
    }
    if (spark) {
      // Velocidad constante y misma duracion en las cuatro: como las parcelas
      // miden lo mismo, las cuatro chispas llegan abajo A LA VEZ.
      tl.fromTo(
        spark,
        { yPercent: 0, opacity: 1 },
        { yPercent: 100 * (parcela.offsetHeight / spark.offsetHeight), opacity: 0,
          duration: 0.62, ease: "none", immediateRender: false },
        at + 0.26,
      );
    }
    tl.call(() => { for (const n of nombres) n.classList.add("is-caught"); }, [], at + 0.26);
  });

  const strips = Array.from(root.querySelectorAll<HTMLElement>("[data-credit-strip]"));
  tl.fromTo(
    strips,
    { opacity: 0, y: 14 },
    { opacity: 1, y: 0, duration: 0.62, ease: SLOW, immediateRender: false },
    0.9,
  );

  // Sonda del arnes: el ritmo se mide con tl.progress() desde dentro de la
  // pagina; page.screenshot() en headless perturba GSAP.
  (window as unknown as { __hyprSkills?: gsap.core.Timeline }).__hyprSkills = tl;
}
```

`immediateRender: false` en todos los `fromTo` por el motivo ya documentado en `buildSlateRail`:
un `refresh()` puede renderizar la timeline para medir y dejar la escena montada antes de tiempo.

- [ ] **Paso 3: medir el ritmo desde dentro de la página**

```js
// 1. duracion declarada
window.__hyprSkills.duration()            // <= 1.6
// 2. el mensaje cierra a los 830ms
window.__hyprSkills.pause(); window.__hyprSkills.progress(0.546);
// los 4 rotulos con clip-path: inset(0px)
// 3. el orden, por lo que NO ha pasado
window.__hyprSkills.progress(0.33);       // ningun nombre de las columnas 2-4 en reposo
// 4. mecanismo, no cuenta cruda (ver "Restricciones globales" — un techo
// numerico de document.getAnimations() se probo y se descarto: el diseno
// exige 23 lamparas de CSS solapadas, asi que el numero por si solo no
// distingue eso de 23 tweens de GSAP caros)
Array.from(document.querySelectorAll('[data-credit]'))
  .filter(n => getComputedStyle(n).display !== 'none')
  .every(n => getComputedStyle(n).animationName === 'hypr-lampara')   // true
window.__hyprSkills.getChildren(false, true, false)
  .filter(t => t.targets().length > 0 && t.targets().every(x => x instanceof Element))
  .length                                                              // <= 13
```

- [ ] **Paso 4: commit**

```bash
git add src/themes/hypr.choreography.ts src/themes/themes.css
git commit -m "feat(skills): la corriente como entrada del catastro"
```

---

## Tarea 9 · El apuntado: la luz que viaja

**Ficheros:**
- Modificar: `src/themes/hypr.choreography.ts`
- Modificar: `src/themes/themes.css`

- [ ] **Paso 1: la luz con peso**

```ts
/*
 * La luz del lindero no salta a la fila: la lleva un `quickTo`, asi que al
 * recorrer nombres VIAJA por el carril y un salto de Git a Gemini CLI se ve
 * recorrer. Es la misma idea de la entrada — corriente por un cable —
 * sostenida dentro del apuntado en vez de abandonada al acabar, y es lo que
 * quita la sensacion de estatico: hay un objeto fisico moviendose, no
 * estados relevandose.
 */
const glow = parcela.querySelector<HTMLElement>(".credits-glow");
const mover = gsap.quickTo(glow, "y", { duration: 0.42, ease: "power4.out" });
```

Al seleccionar: `mover(boton.offsetTop + boton.offsetHeight / 2 - 19)` y
`gsap.to(glow, { opacity: 1, duration: 0.42 })`. Al salir de la parcela,
`gsap.to(glow, { opacity: 0, duration: 0.9 })`.

- [ ] **Paso 2: el rodillo de la franja**

```ts
/*
 * Lo viejo sale por arriba mientras lo nuevo entra por abajo. Antes solo
 * entraba lo nuevo, que es un fundido disfrazado.
 *
 * Barrido antes de montar: recorriendo nombres rapido llegan varias
 * selecciones dentro de los 420ms del rodillo y los nodos se apilaban sin
 * limite. Verificado con 6 selecciones en 600ms: debe quedar 1.
 */
const previos = Array.from(strip.querySelectorAll<HTMLElement>(".credits-strip-in"));
const viejo = previos.pop() ?? null;
for (const n of previos) { gsap.killTweensOf(n); n.remove(); }
strip.appendChild(nuevo);
gsap.fromTo(nuevo, { yPercent: 100, opacity: 0 },
  { yPercent: 0, opacity: 1, duration: 0.42, ease: "power4.out" });
if (viejo) {
  gsap.to(viejo, { yPercent: -100, opacity: 0, duration: 0.3, ease: "power2.in",
    onComplete: () => viejo.remove() });
}
```

- [ ] **Paso 3: el friso que se aparta, y el rótulo que calienta despacio**

```ts
// Se realza QUITANDO, no anadiendo: nada de `filter` ni `box-shadow`, que es
// la linea roja con un shader a pantalla completa detras.
gsap.to(marcas, { opacity: 0.42, scale: 1, duration: 0.42, ease: "power3.out" });
gsap.to(marcaActiva, { opacity: 1, scale: 1.28, duration: 0.42, ease: "power3.out" });
// El rotulo del area va lento A PROPOSITO, y es el unico elemento que rompe
// el ritmo: apuntar Django no solo enciende Django, calienta despacio
// "Backend y datos". Lo rapido es la accion, lo lento es el contexto.
gsap.to(label, { color: "var(--l3)", duration: 0.9, ease: "power3.out" });
```

En CSS, el nombre apuntado y su desplazamiento — **en el hijo, nunca en el `<button>`**:

```css
:root[data-theme="hyprland"] .credit .credit-name {
  display: inline-block;
  transition: transform 0.9s var(--slow), color 0.9s var(--slow);
}
:root[data-theme="hyprland"] .credit:hover .credit-name,
:root[data-theme="hyprland"] .credit:focus-visible .credit-name,
:root[data-theme="hyprland"] .credit.is-active .credit-name {
  color: var(--l3);
  transform: translateX(6px);
  transition: transform 0.42s var(--hard), color 0.42s var(--hard);
}
:root[data-theme="hyprland"] .credit:focus-visible {
  outline: 2px solid var(--l3);
  outline-offset: 3px;
}
```

- [ ] **Paso 4: el ambiente, sin un solo bucle nuevo**

```css
/*
 * Los carriles leen la posicion de la luz que el gesto 3 YA escribe en :root
 * en cada onUpdate del scroll. Cero rAF nuevos, cero timers, cero nodos: es
 * un background-image que se repinta cuando la variable cambia, y la
 * variable ya cambia. A cambio, la escena respira al desplazarte y la luz de
 * la pagina cruza el catastro en vez de ignorarlo.
 *
 * Descartada la deriva perpetua de la chispa: es barata de ejecutar y cara
 * semanticamente. Si la chispa se mueve siempre, el recorrido de la entrada
 * deja de ser un acontecimiento y el apuntado compite contra un fondo en
 * movimiento. Vale porque pasa UNA vez — el mismo argumento por el que los
 * creditos de Vice ruedan y se detienen.
 */
:root[data-theme="hyprland"] .credits-rail {
  background-image: linear-gradient(
    to bottom,
    var(--rule) 0%,
    color-mix(in oklab, var(--l1) 22%, var(--rule)) var(--by, 50%),
    var(--rule) 100%
  );
}
```

- [ ] **Paso 5: verificar el barrido rápido**

```js
// 6 selecciones en 600ms sobre la misma parcela
document.querySelectorAll('[data-credit-strip]')[0].querySelectorAll('.credits-strip-in').length // 1
```

Y `PerformanceObserver` de `layout-shift` durante 20 apuntados: suma 0.

- [ ] **Paso 6: commit**

```bash
git add src/themes/hypr.choreography.ts src/themes/themes.css
git commit -m "feat(skills): el apuntado del catastro, la luz que viaja"
```

---

## Tarea 10 · Movimiento reducido y limpieza

**Ficheros:**
- Modificar: `src/themes/hypr.choreography.ts`

- [ ] **Paso 1: la rama `reduce`**

```ts
/*
 * La escena completa se lee sin haber interactuado. El estado de REPOSO es el
 * que tiene que pasar AA; el `--haze` al 28% previo al destello no pasa, y es
 * aceptable solo porque dura <400ms, no existe aqui, y ningun nodo reposa ahi.
 */
mm.add("(prefers-reduced-motion: reduce)", () => {
  for (const n of Array.from(root.querySelectorAll<HTMLElement>("[data-credit]"))) {
    n.classList.add("is-caught");
  }
  for (const p of parcelas) {
    gsap.set(p.querySelector(".credits-rail"), { scaleY: 1 });
    gsap.set(p.querySelector(".credits-spark"), { opacity: 0 });
  }
  return () => {
    for (const n of Array.from(root.querySelectorAll<HTMLElement>("[data-credit]"))) {
      n.classList.remove("is-caught");
    }
  };
});
```

Y en CSS, apagar la animación de la lámpara bajo `reduce` dejando el color de reposo:

```css
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .credit.is-caught { animation: none; }
  :root[data-theme="hyprland"] .credit .credit-name { transition: none; }
}
```

- [ ] **Paso 2: montar / destruir / montar**

La coreografía ya mata sus ScrollTriggers por prefijo al entrar. Añadir a esa limpieza el
borrado de `.is-caught` y de la sonda:

```ts
for (const n of Array.from(root.querySelectorAll<HTMLElement>("[data-credit].is-caught"))) {
  n.classList.remove("is-caught");
}
delete (window as unknown as { __hyprSkills?: unknown }).__hyprSkills;
```

Esperado tras un remonte: la entrada vuelve a correr entera, cero ScrollTriggers duplicados
con el prefijo `hypr-skills`.

- [ ] **Paso 3: commit**

```bash
git add src/themes/hypr.choreography.ts src/themes/themes.css
git commit -m "fix(skills): movimiento reducido y limpieza del catastro"
```

---

## Tarea 11 · `verify.py`: el marcador 2 queda obsoleto

**Ficheros:**
- Modificar: `scripts/verify.py` (líneas 1159-1174, rama Hyprland)

- [ ] **Paso 1: actualizar la aserción**

La rama de Hyprland comprueba hoy `.credits-list` en `flex-direction: row` con `.credit-role`
oculto. La lista pasa a `display: contents` con los `.credit` como ítems de rejilla. Se
**actualiza** esa rama, no se relaja ni se borra:

```python
# Hyprland: el catastro. La lista se disuelve (`display: contents`) y cada
# `.credit` es un item de la rejilla con su columna asignada. `.credit-role`
# sigue oculto, como en el reparto anterior.
```

Comprobar: `getComputedStyle('.credits-list').display === 'contents'`,
`getComputedStyle('.credit').gridColumnStart !== 'auto'`, `.credit-role` en `display: none`.

- [ ] **Paso 2: correr el arnés general, solo y sin editar nada**

```bash
python3 scripts/verify.py --theme hyprland
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
```

Esperado: salida 0 en los tres, contra `scripts/verify-baseline.json`. Si se arregla un fallo
que está en la base, actualizarla con `--update-baseline` y revisar el diff antes de commitear.

- [ ] **Paso 3: commit**

```bash
git add scripts/verify.py
git commit -m "test(skills): el marcador 2 de Hyprland pasa del reparto al catastro"
```

---

## Tarea 12 · Verificación final y gates

- [ ] **Paso 1: build y lint**

```bash
/root/.nvm/versions/node/v22.22.3/bin/node node_modules/typescript/bin/tsc
/root/.nvm/versions/node/v22.22.3/bin/node node_modules/vite/bin/vite.js build
npm run lint
```

- [ ] **Paso 2: el arnés propio y el general, sobre el build**

```bash
python3 scripts/measure-catastro.py --url http://localhost:4173   # 0 fallos
python3 scripts/verify.py --theme hyprland
python3 scripts/verify.py --theme vice
python3 scripts/verify.py --theme caelestia
```

- [ ] **Paso 3: contraste, con el fondo real**

`check_contrast_wcag` con recorte **ajustado al glifo** y el shader **activo**, en producción.
El `--haze` del nivel bajo es el más ajustado. Criterio: ≥ 4,5:1. Si no llega, se sube el scrim
del catastro; **nunca se toca el token**.

- [ ] **Paso 4: capturas y anti-mock**

Capturas 1440×900 y 390×844 con `?theme=hyprland`, y las de Vice y Caelestia para el diff
contra un worktree del commit previo.

```bash
grep -rE "mockData|fakeData|placeholder|lorem ipsum|Lorem" src/ --include="*.ts"
```

- [ ] **Paso 5: los dos críticos**

- `lidia-naive-tester`, pregunta abierta: *"¿qué te cuenta esta sección?"*. Verde si responde en
  términos de áreas ("hace interfaces, y también backend, y sabe lenguajes de bajo nivel").
  Rojo si responde "una lista de logos".
- `vera-art-director`, con las capturas de `about` y `credits` a 1440 lado a lado y **sin
  decirle qué buscamos**. Verde si describe dos dispositivos distintos por iniciativa propia.
  Si dice "la misma rejilla dos veces", la salida es darle al catastro el perímetro cerrado a
  doble filete, no tocar la placa.

- [ ] **Paso 6: cerrar el registro**

Actualizar `PROGRESS.json`, poner el spec en `Estado: implementado` y añadirle la línea
`Plan: docs/superpowers/plans/2026-08-10-hyprland-stack-catastro.md`, con una sección de
"Registro de implementación" y las divergencias respecto a este plan si las hubo.

```bash
git add docs/superpowers/specs/2026-08-10-hyprland-stack-catastro-design.md PROGRESS.json
git commit -m "docs(skills): el catastro queda implementado"
```
