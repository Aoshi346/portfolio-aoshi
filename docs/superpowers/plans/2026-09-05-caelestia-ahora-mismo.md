# Caelestia — la tarjeta «Ahora mismo» — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar la tarjeta «Ahora mismo» del hero de Caelestia según el spec: superficie tonal sin borde, orden «quién, qué hace, estado», «Full Stack Developer» como único primero, figura de Material 3 viva, luz que respira, capa de estado, y una entrada que brota de la luz.

**Architecture:** La tarjeta sigue siendo DOM común construido en `src/sections/hero.ts` con literales de `content.ts`, vestida solo bajo `[data-theme="caelestia"]` en `themes.css`, y animada desde `src/themes/caelestia.titulo.ts` (`montarEntrada` para la entrada, un `montarFiguraViva` nuevo para la figura). La figura reutiliza el generador de 240 vértices de `src/utils/figurasM3.ts` mediante una función paramétrica nueva. Cada cambio entra con su gate en `scripts/measure-caelestia-titulo.py`, visto en rojo antes.

**Tech Stack:** Vite 8, TypeScript estricto, GSAP 3 (solo `fromTo`/`set`/`to`, nunca `from`), CSS con tokens `--cae-*`, Playwright (Python) para los gates.

**Spec:** `docs/superpowers/specs/2026-09-05-caelestia-ahora-mismo-design.md`

## Global Constraints

- Node 22: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"` antes de cualquier `npm`.
- Trabajo en worktree propio (regla de memoria «el trabajo de tema va en worktree»): rama `design/caelestia-ahora-mismo` desde `fix/repaso-interfaces`.
- Los gates corren contra el build servido: `npm run build && npx vite preview --port 4183 --strictPort` (nunca `npm run dev`). Si el 4183 está ocupado, comprobar de quién es (`ss -ltnp | grep 4183`, `readlink /proc/<pid>/cwd`) y matar por PID, nunca `pkill -f`.
- Nunca `any`, nunca `gsap.from`, nunca `console.log`. Cero emojis en código y commits.
- Toda animación con su rama `prefers-reduced-motion`; el selector `*` no alcanza pseudo-elementos, cada `::after` que anime lleva su regla propia.
- Una opacidad no se reutiliza entre esquemas: cada valor con comentario de contra qué superficie se midió.
- Ningún gate se acepta sin haberlo visto en rojo contra el fallo que dice cazar.
- Viewport oficial de Caelestia: página 1440×900 (el panel mide 1412×748). El arnés de Título usa `VENTANA = 1412×748` como viewport a propósito; para la tarjeta se mantiene ese arnés y su viewport.
- Commits: `tipo(scope): descripción`; scope `hero`. No se hace `git push`.

---

### Task 0: Worktree y punto de partida

**Files:** ninguno (git).

- [ ] **Step 1: Crear rama y worktree**

```bash
cd /home/aoshi/proyectos/portfolio-aoshi
git worktree add -b design/caelestia-ahora-mismo ../portfolio-aoshi-ahora-mismo fix/repaso-interfaces
cd ../portfolio-aoshi-ahora-mismo
ln -s /home/aoshi/proyectos/portfolio-aoshi/node_modules node_modules
```

- [ ] **Step 1b: El spec pasa a `en ejecucion`**

En `docs/superpowers/specs/2026-09-05-caelestia-ahora-mismo-design.md`, línea 3: `Estado: en ejecucion`. Commit: `git commit -am "docs(hero): el spec de Ahora mismo pasa a en ejecucion"`. (`scripts/verify.py` cruza el estado del spec con las casillas de este plan: un plan a medias con `en ejecucion` es legítimo; `implementado` con casillas sin marcar, no.)

- [ ] **Step 2: Build verde en el punto de partida y arnés de Título verde**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && (npx vite preview --port 4183 --strictPort > /tmp/preview-am.log 2>&1 & echo $! > /tmp/preview-am.pid)
python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183
```
Expected: `0 fallo(s)`. Si no, parar: el punto de partida está roto y hay que saberlo antes de tocar nada.

---

### Task 1: El literal «Full Stack Developer» y el gate anti-mock que lo lee

**Files:**
- Modify: `src/data/content.ts:46`
- Modify: `scripts/measure-caelestia-titulo.py` (función `widget`, ~línea 255)

**Interfaces:**
- Produces: `identity.now === "Full Stack Developer"`, leído por `hero.ts:151` y `about.ts:99,329,461` sin tocarlos.
- Produces en el arnés: `literal_now()` → `str`, que lee `content.ts` con regex.

- [ ] **Step 1: Cambiar el literal**

En `src/data/content.ts`, línea 46:
```ts
  now: "Full Stack Developer",
```

- [ ] **Step 2: Build y ver el gate `widget` en rojo**

```bash
npm run build && python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183 2>&1 | grep -A12 "\[widget\]"
```
Expected: `FALLO el widget dice 'Freelancer', literal de content.ts` (la lista `esperado` del arnés lleva el literal viejo a mano).

- [ ] **Step 3: El arnés lee el literal de `content.ts`**

En `scripts/measure-caelestia-titulo.py`, encima de `def widget`:
```python
import re
from pathlib import Path

def literal_now() -> str:
    """`identity.now` tal como esta escrito en content.ts. El arnes no puede
    importar TypeScript, asi que lo lee como texto; si no lo encuentra FALLA en
    vez de devolver un valor por defecto (un gate que adivina no vigila)."""
    fuente = (Path(__file__).resolve().parent.parent / "src" / "data" / "content.ts").read_text(encoding="utf-8")
    m = re.search(r'^\s*now:\s*"([^"]+)",', fuente, re.M)
    assert m, "no se encuentra `now: \"...\"` en content.ts"
    return m.group(1)
```
Y en `esperado`, sustituir la línea `"Freelancer",                  # identity.now` por:
```python
        literal_now(),                 # identity.now, leido de content.ts (Task 1 del plan Ahora mismo)
```

- [ ] **Step 4: Gate verde**

```bash
python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183 2>&1 | grep -A12 "\[widget\]"
```
Expected: `OK   el widget dice 'Full Stack Developer', literal de content.ts` y el resto OK.

- [ ] **Step 5: Ver «Quién soy» con el literal nuevo (no se toca, se mira)**

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://127.0.0.1:4183/?theme=caelestia', wait_until='domcontentloaded'); pg.wait_for_timeout(7000)
    pg.click('.cae-ws:nth-child(2)'); pg.wait_for_timeout(4000)
    print(pg.evaluate("() => [...document.querySelectorAll('#about *')].filter(e => e.children.length===0 && /Full Stack Developer/.test(e.textContent)).length"), 'nodos de la ficha con el literal nuevo')
    b.close()
EOF
```
Expected: al menos 1.

- [ ] **Step 6: Commit**

```bash
git add src/data/content.ts scripts/measure-caelestia-titulo.py
git commit -m "feat(hero): identity.now pasa a Full Stack Developer y el arnes lo lee de content.ts"
```

---

### Task 2: El DOM nuevo de la tarjeta (orden y columnas)

**Files:**
- Modify: `src/sections/hero.ts:139-166`
- Modify: `scripts/measure-caelestia-titulo.py` (nueva función `tarjeta_orden`, llamada desde `main`)

**Interfaces:**
- Produces (clases del DOM, las usan las Tasks 3, 4 y 5): `.cae-widget` > `.cae-wcab` (`.cae-whd` + `.cae-wfig`), `.cae-wnow`, `.cae-wsub`, `.cae-wdos` (2 × `.cae-wcol` > `small.cae-wfecha` + `b.cae-wnombre`), `.cae-wpie` > `.cae-pilla` (> `i.cae-wluz` + texto).

- [ ] **Step 1: Escribir el gate del orden y verlo en rojo**

En `scripts/measure-caelestia-titulo.py`, nueva función:
```python
def tarjeta_orden(pg, base: str) -> None:
    print("\n[tarjeta] orden quien / que hace / estado, dos columnas fechadas")
    abrir(pg, base, "13:00")
    d = pg.evaluate(
        """() => {
          const w = document.querySelector('#hero .cae-widget'); if (!w) return null;
          const clases = [...w.children].map(c => c.className.split(' ')[0]);
          const cols = [...w.querySelectorAll('.cae-wdos > .cae-wcol')];
          const colsOk = cols.length === 2 && cols.every(c => c.children.length === 2
             && c.children[0].matches('small.cae-wfecha') && c.children[1].matches('b.cae-wnombre'));
          const luz = w.querySelector('.cae-wpie .cae-pilla > i.cae-wluz');
          const fig = w.querySelector('.cae-wcab .cae-wfig');
          return { clases, colsOk, luz: !!luz, fig: !!fig,
                   gridCols: getComputedStyle(w.querySelector('.cae-wdos') || w).gridTemplateColumns };
        }"""
    )
    assert_que(d is not None, "existe #hero .cae-widget")
    if d is None:
        return
    assert_que(d["clases"] == ["cae-wcab", "cae-wnow", "cae-wsub", "cae-wdos", "cae-wpie"],
               f"los hijos directos van en orden cabecera/primero/ubicacion/columnas/pie ({d['clases']})")
    assert_que(d["colsOk"], "dos columnas, cada una con la fecha (small) antes del nombre (b)")
    assert_que(d["luz"], "la pastilla del pie lleva la luz (i.cae-wluz)")
    assert_que(d["fig"], "la cabecera lleva el hueco de la figura (.cae-wfig)")
    assert_que(len(d["gridCols"].split()) == 2, f"las columnas son dos pistas de grid ({d['gridCols']!r})")
```
Añadir `tarjeta_orden(pg, args.base)` en `main`, justo después de `widget(pg, args.base)`. Correr:
```bash
python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183 2>&1 | grep -A8 "\[tarjeta\]"
```
Expected: rojo en orden, columnas, luz y figura (el DOM actual es `cae-whd`, `cae-pilla`, `cae-wnow`, `cae-wsub`, `cae-wfila`, `cae-wfila`).

- [ ] **Step 2: Reescribir el bloque del widget en `hero.ts`**

Sustituir las líneas 150-164 (desde `const disponible = ...` hasta el cierre de `const widget = el(...)`) por:
```ts
  const luz = el("i", "cae-wluz");
  luz.setAttribute("aria-hidden", "true");
  const disponible = el("span", "cae-pilla", [luz, identity.availability]);
  const figura = el("span", "cae-wfig");
  figura.setAttribute("aria-hidden", "true");
  const wnow = el("p", "cae-wnow", [identity.now]);
  const wsub = el("p", "cae-wsub", [`${identity.location} · Desde ${identity.since}`]);

  /*
   * Dos columnas fechadas, no dos filas de tabla (spec 2026-09-05-caelestia-
   * ahora-mismo): la fecha va ENCIMA como etiqueta y el nombre debajo, asi
   * estudios y empresa se leen como dos cosas distintas (hallazgo de Lidia
   * en B1), no como dos filas iguales.
   */
  const wcol = (fecha: string, nombre: string): HTMLElement =>
    el("div", "cae-wcol", [el("small", "cae-wfecha", [fecha]), el("b", "cae-wnombre", [nombre])]);

  const widget = el("div", "cae-widget", [
    el("div", "cae-wcab", [el("p", "cae-whd", ["Ahora mismo"]), figura]),
    wnow,
    wsub,
    el("div", "cae-wdos", [
      wcol(semestre, education[0].degree),
      wcol(experience[0].period, experience[0].organization),
    ]),
    el("div", "cae-wpie", [disponible]),
  ]);
```
Comprobar que `el(tag, clase, hijos?)` admite `Node | string` en hijos (ver `src/utils/dom.ts`); si `el("i", "cae-wluz")` sin hijos no compila, pasar `[]`.

- [ ] **Step 3: Build, lint y gate**

```bash
npm run build && npm run lint && python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183 2>&1 | grep -A8 "\[tarjeta\]"
```
Expected: todo OK salvo `las columnas son dos pistas de grid` (el CSS llega en Task 3; anotarlo y seguir). El gate `[widget]` (anti-mock) sigue verde: los literales no cambian.

- [ ] **Step 4: Commit**

```bash
git add src/sections/hero.ts scripts/measure-caelestia-titulo.py
git commit -m "feat(hero): la tarjeta Ahora mismo cambia de orden: quien, que hace, estado; columnas fechadas"
```

---

### Task 3: La superficie, la tipografía y la luz (CSS)

**Files:**
- Modify: `src/themes/themes.css` (token nuevo junto a `--cae-display-axes-texto`, ~línea 3593; bloque `.cae-widget`…`.cae-wn`, ~líneas 4123-4210)
- Modify: `scripts/measure-caelestia-titulo.py` (nueva función `tarjeta_superficie`)

**Interfaces:**
- Produces: token `--cae-display-axes-ficha`; clases pintadas de Task 2; `.cae-wfig` con caja 40×40 y fondo `--cae-primary-container` (la Task 4 solo le pone `clip-path`).

- [ ] **Step 1: Gate de superficie, jerarquía y luz, en rojo**

```python
def tarjeta_superficie(pg, base: str) -> None:
    print("\n[tarjeta] sin caja, un primero en una linea, la luz respira")
    abrir(pg, base, "13:00")
    d = pg.evaluate(
        """() => {
          const w = document.querySelector('#hero .cae-widget'), bar = document.querySelector('.cae-bar'), hero = document.querySelector('#hero');
          const cs = getComputedStyle(w), now = w.querySelector('.cae-wnow');
          const r = document.createRange(); r.selectNodeContents(now);
          const tamanos = [...w.querySelectorAll('*')].filter(e => e.textContent.trim() && e.children.length === 0)
             .map(e => parseFloat(getComputedStyle(e).fontSize));
          const luz = w.querySelector('.cae-wluz');
          return {
            borde: cs.borderTopWidth, fondo: cs.backgroundColor, fondoBar: bar ? getComputedStyle(bar).backgroundColor : null,
            fondoHero: getComputedStyle(hero).backgroundColor,
            nowPx: parseFloat(getComputedStyle(now).fontSize), maxPx: Math.max(...tamanos),
            nowAncho: r.getBoundingClientRect().width, caja: w.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight),
            nowLineas: r.getClientRects().length,
            axes: getComputedStyle(now).fontVariationSettings,
            anillo: luz ? getComputedStyle(luz, '::after').animationName : 'sin-luz',
          };
        }"""
    )
    assert_que(d["borde"] == "0px", f"la tarjeta no lleva borde ({d['borde']})")
    assert_que(d["fondo"] == d["fondoBar"] and d["fondo"] != d["fondoHero"], f"la tarjeta es surface-container-high como la barra ({d['fondo']})")
    assert_que(d["nowPx"] == d["maxPx"] and d["nowPx"] >= 26, f"el primero es el texto mas grande de la tarjeta ({d['nowPx']} px)")
    assert_que(d["nowAncho"] <= d["caja"] and d["nowLineas"] == 1, f"el primero cabe en una linea ({d['nowAncho']:.0f} de {d['caja']:.0f} px, {d['nowLineas']} lineas)")
    assert_que('"opsz" 60' in d["axes"], f"el primero va a tamano optico 60 ({d['axes']})")
    assert_que(d["anillo"] not in ("none", "sin-luz"), f"la luz respira con movimiento ({d['anillo']})")

    ctx = pg.context.browser.new_context(viewport=VENTANA, reduced_motion="reduce")
    pr = ctx.new_page()
    abrir(pr, base, "13:00")
    quieta = pr.evaluate("() => { const l = document.querySelector('#hero .cae-wluz'); return l ? getComputedStyle(l, '::after').animationName : 'sin-luz'; }")
    assert_que(quieta == "none", f"con movimiento reducido la luz no respira ({quieta})")
    ctx.close()
```
Llamar a `tarjeta_superficie(pg, args.base)` tras `tarjeta_orden`. Correr y esperar rojo en borde (`1px`), fondo (`surface-container`), tamaño óptico (`opsz 9`) y anillo (`none`).

- [ ] **Step 2: El token y el CSS**

Junto a `--cae-display-axes-texto` (themes.css ~3593):
```css
  /* El primero de la tarjeta "Ahora mismo" (spec 2026-09-05): a 27 px, el
     tamano optico 9 del token de texto da remates pesados; el 60 es el que ya
     usa el titulo del cajon de Obra. Un token, no un literal repetido. */
  --cae-display-axes-ficha: "opsz" 60, "wght" 700, "SOFT" 0, "WONK" 1;
```
Sustituir el bloque desde `:root[data-theme="caelestia"] .cae-widget {` hasta el final de `.cae-wn { ... }` por:
```css
/*
 * La tarjeta "Ahora mismo" (spec 2026-09-05-caelestia-ahora-mismo): mismo
 * sitio y ancho que antes, pero superficie tonal SIN borde (el escalon de la
 * barra y el dock), un primero claro, dos columnas fechadas y la pastilla al
 * pie. Sombra por esquema: 0,22 calibrado contra surface-container-high
 * claro; 0,5 contra el oscuro (abajo).
 */
:root[data-theme="caelestia"] .cae-widget {
  display: block;
  position: absolute;
  top: 30px;
  right: 48px;
  width: 316px;
  padding: 18px 22px 18px;
  border-radius: 24px;
  background: var(--cae-surface-container-high);
  box-shadow: 0 14px 36px -20px rgb(0 0 0 / 0.22);
  color: var(--cae-on-surface);
}
:root[data-theme="caelestia"][data-cae-esquema="noche"] .cae-widget {
  box-shadow: 0 14px 36px -20px rgb(0 0 0 / 0.5);
}
/* Capa de estado M3 al rozar: 6 % del primario (M3 pide 8 %; aqui el fondo ya
   es tonal y con 8 la tarjeta viraba de tono, medido en los dos esquemas). El
   levantamiento y apartar el fondo ya los hace montarRoce: no se duplican. */
:root[data-theme="caelestia"] .cae-widget::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: var(--cae-primary);
  opacity: 0;
  transition: opacity 0.25s;
  pointer-events: none;
}
:root[data-theme="caelestia"] .cae-widget:hover::after {
  opacity: 0.06;
}
:root[data-theme="caelestia"] .cae-wcab {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 40px;
  margin-bottom: 6px;
}
:root[data-theme="caelestia"] .cae-whd {
  margin: 0;
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--cae-on-surface-variant);
}
:root[data-theme="caelestia"] .cae-wfig {
  display: block;
  width: 40px;
  height: 40px;
  background: var(--cae-primary-container);
  border-radius: 50%; /* hasta que la Task 4 le ponga su clip-path */
}
:root[data-theme="caelestia"] .cae-wnow {
  margin: 0;
  font-family: var(--font-display);
  font-variation-settings: var(--cae-display-axes-ficha);
  font-size: 27px;
  line-height: 1;
  letter-spacing: -0.01em;
  white-space: nowrap;
}
:root[data-theme="caelestia"] .cae-wsub {
  margin: 5px 0 0;
  font-size: 13px;
  color: var(--cae-on-surface-variant);
}
:root[data-theme="caelestia"] .cae-wdos {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid color-mix(in oklch, var(--cae-outline) 45%, transparent);
}
:root[data-theme="caelestia"] .cae-wfecha {
  display: block;
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.04em;
  color: var(--cae-on-surface-variant);
  margin-bottom: 3px;
  white-space: nowrap;
}
:root[data-theme="caelestia"] .cae-wnombre {
  display: block;
  font-weight: 500;
  font-size: 12.5px;
  line-height: 1.25;
}
:root[data-theme="caelestia"] .cae-wpie {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid color-mix(in oklch, var(--cae-outline) 45%, transparent);
}
:root[data-theme="caelestia"] .cae-pilla {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 28px;
  padding: 0 12px 0 10px;
  border-radius: 999px;
  background: var(--cae-anchor);
  color: var(--cae-on-anchor);
  font-family: var(--font-mono);
  font-size: 10.5px;
  letter-spacing: 0.06em;
  white-space: nowrap;
}
:root[data-theme="caelestia"] .cae-wluz {
  position: relative;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cae-on-anchor);
  display: block;
}
/* La luz respira: SOLO con movimiento. Es un ::after, asi que el `*` de la
   guardia generica de reduced-motion no lo alcanzaria; por eso vive entero
   dentro de no-preference y con reduce no existe. */
@media (prefers-reduced-motion: no-preference) {
  :root[data-theme="caelestia"] .cae-wluz::after {
    content: "";
    position: absolute;
    inset: -5px;
    border-radius: 50%;
    border: 1.5px solid var(--cae-on-anchor);
    animation: caeLuzRespira 2.4s ease-in-out infinite;
  }
  @keyframes caeLuzRespira {
    0%, 100% { transform: scale(0.6); opacity: 0; }
    50% { transform: scale(1); opacity: 0.6; }
  }
}
```
Borrar cualquier regla vieja de `.cae-wfila` y `.cae-wn` que quede.

- [ ] **Step 3: Build, lint, gates**

```bash
npm run build && npm run lint && python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183 2>&1 | grep -A10 "\[tarjeta\]"
```
Expected: `[tarjeta] orden…` todo OK (ahora sí las dos pistas de grid) y `[tarjeta] sin caja…` todo OK.

- [ ] **Step 4: Captura y mirarla**

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for hora, nombre in (("13:00","dia"),("23:00","noche")):
        pg = b.new_page(viewport={'width':1440,'height':900}, device_scale_factor=2)
        hh, mm = hora.split(":")
        pg.add_init_script(f"(() => {{ const R = Date; const i0 = R.now(); const a0 = new R(2026,7,26,{hh},{mm},0).getTime(); class F extends R {{ constructor(...a) {{ return a.length ? new R(...a) : new R(a0 + (R.now() - i0)); }} static now() {{ return a0 + (R.now() - i0); }} }} window.Date = F; }})()")
        pg.goto('http://127.0.0.1:4183/?theme=caelestia', wait_until='domcontentloaded'); pg.wait_for_timeout(9000)
        pg.locator('#hero .cae-widget').screenshot(path=f'/tmp/tarjeta-{nombre}.png'); pg.close()
    b.close()
EOF
```
Abrir las dos capturas y comparar con la maqueta `.superpowers/brainstorm/*/content/09-fullstack.html` (tamaño A). Si la tarjeta no se parece, no seguir.

- [ ] **Step 5: Commit**

```bash
git add src/themes/themes.css scripts/measure-caelestia-titulo.py
git commit -m "feat(hero): la tarjeta Ahora mismo sin caja: superficie tonal, primero a opsz 60, luz que respira"
```

---

### Task 4: La figura viva (morfa con la hora, mira al cursor)

**Files:**
- Modify: `src/utils/figurasM3.ts` (nueva `figuraParametrica`)
- Modify: `src/themes/caelestia.titulo.ts` (nueva `montarFiguraViva`)
- Modify: `src/themes/caelestia.choreography.ts:193-197` (montarla junto a `montarRoce`)
- Modify: `scripts/measure-caelestia-titulo.py` (nueva `tarjeta_figura`)

**Interfaces:**
- Produces: `figuraParametrica(n: number, a: number, relieve: number, fase: number): string` (un `polygon()` de 240 pares).
- Produces: `montarFiguraViva(gsap: Gsap, root: HTMLElement): FiguraVivaHandle` con `{ destroy(): void; relieve: { v: number }; pinta(): void }` — `relieve.v` y `pinta` los usa la Task 5 para que la figura nazca como círculo en la entrada.

- [ ] **Step 1: Gate de la figura, en rojo**

```python
def tarjeta_figura(pg, base: str) -> None:
    print("\n[tarjeta] la figura vive: 240 vertices, cambia sola, quieta con movimiento reducido")
    abrir(pg, base, "13:00")
    LEE = "() => { const f = document.querySelector('#hero .cae-wfig'); return f ? getComputedStyle(f).clipPath : 'sin-figura'; }"
    a = pg.evaluate(LEE)
    pares = a.count("%,") + 1 if a.startswith("polygon(") else 0
    assert_que(pares == 240, f"la figura es un polygon() de 240 pares ({pares})")
    # Anclado a ESTADO: se espera a que cambie, con tope; si no cambia, falla.
    cambio = False
    t0 = time.monotonic()
    while time.monotonic() - t0 < 6:
        if pg.evaluate(LEE) != a:
            cambio = True
            break
        pg.wait_for_timeout(120)
    assert_que(cambio, "la figura cambia de forma sola (morfa con el tiempo)")

    ctx = pg.context.browser.new_context(viewport=VENTANA, reduced_motion="reduce")
    pr = ctx.new_page()
    abrir(pr, base, "13:00")
    q0 = pr.evaluate(LEE)
    pr.wait_for_timeout(1500)
    q1 = pr.evaluate(LEE)
    assert_que(q0.startswith("polygon(") and q0 == q1, "con movimiento reducido la figura esta y no cambia")
    ctx.close()
```
(`time` ya está importado en el arnés.) Llamar tras `tarjeta_superficie`. Correr: rojo en «240 pares» (hoy `clip-path: none`).

- [ ] **Step 2: `figuraParametrica` en `figurasM3.ts`**

Al final del fichero:
```ts
/**
 * Figura parametrica para piezas que morfan en tiempo real (la tarjeta "Ahora
 * mismo" de Caelestia): misma cuenta de VERTICES que las de la tabla, asi
 * que un `polygon()` de esta funcion interpola con cualquiera de las otras.
 * `n` lobulos, `a` amplitud (como la tabla), `relieve` 0..1 (0 = circulo,
 * lo usa la entrada), `fase` en radianes gira los lobulos sin girar la caja.
 * Sin cache: cambia cada fotograma y la clave seria el propio resultado.
 */
export function figuraParametrica(n: number, a: number, relieve: number, fase: number): string {
  const amp = -a * relieve;
  const seg = a * 0.18 * relieve;
  const rs: number[] = [];
  for (let i = 0; i < VERTICES; i += 1) {
    const t = (i * 2 * Math.PI) / VERTICES;
    rs.push(1 + amp * Math.cos(n * (t + fase)) + seg * Math.cos(2 * n * (t + fase)));
  }
  return poly(encaja(rs));
}
```

- [ ] **Step 3: `montarFiguraViva` en `caelestia.titulo.ts`**

Importar arriba: `import { figuraParametrica } from "../utils/figurasM3";`. Añadir al final del fichero:
```ts
export interface FiguraVivaHandle {
  destroy: () => void;
  /** 0 = circulo, 1 = figura entera. La entrada lo lleva de 0 a 1. */
  relieve: { v: number };
  pinta: () => void;
}

const FIGURA_NULA: FiguraVivaHandle = { destroy: () => {}, relieve: { v: 1 }, pinta: () => {} };

/**
 * La figura de la tarjeta "Ahora mismo" (spec 2026-09-05-caelestia-ahora-
 * mismo): morfa con la hora del visitante como las figuras del fondo (los
 * lobulos avanzan de 5 a 9 a lo largo del dia, la fase gira en un bucle de
 * 24 s) y se inclina hacia el cursor dentro de la tarjeta. Con movimiento
 * reducido se pinta una vez, quieta, con los lobulos de la hora.
 */
export function montarFiguraViva(gsap: Gsap, root: HTMLElement): FiguraVivaHandle {
  const tarjeta = root.querySelector<HTMLElement>("#hero .cae-widget");
  const figura = tarjeta?.querySelector<HTMLElement>(".cae-wfig") ?? null;
  if (!tarjeta || !figura) return FIGURA_NULA;

  const estado = { fase: 0 };
  const relieve = { v: 1 };
  const lobulos = (): number => {
    const ahora = new Date();
    const minutos = ahora.getHours() * 60 + ahora.getMinutes();
    return 5 + Math.floor((minutos / 1440) * 5); // 5..9
  };
  const pinta = (): void => {
    figura.style.clipPath = figuraParametrica(lobulos(), 0.11, relieve.v, estado.fase);
  };
  pinta();

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return { destroy: () => {}, relieve, pinta };
  }

  const bucle = gsap.to(estado, { fase: Math.PI * 2, duration: 24, ease: "none", repeat: -1, onUpdate: pinta });

  const mirar = (e: PointerEvent): void => {
    const r = figura.getBoundingClientRect();
    const dx = (e.clientX - (r.left + r.width / 2)) / 40;
    const dy = (e.clientY - (r.top + r.height / 2)) / 40;
    gsap.to(figura, {
      rotateY: Math.max(-18, Math.min(18, dx)),
      rotateX: Math.max(-18, Math.min(18, -dy)),
      transformPerspective: 300,
      duration: 0.4,
      ease: "power2.out",
    });
  };
  const soltar = (): void => {
    gsap.to(figura, { rotateX: 0, rotateY: 0, duration: 0.6, ease: "power2.out" });
  };
  tarjeta.addEventListener("pointermove", mirar);
  tarjeta.addEventListener("pointerleave", soltar);

  return {
    relieve,
    pinta,
    destroy: () => {
      bucle.kill();
      gsap.killTweensOf(figura);
      tarjeta.removeEventListener("pointermove", mirar);
      tarjeta.removeEventListener("pointerleave", soltar);
    },
  };
}
```
En `caelestia.choreography.ts`, tras `montarRoce(gsap, root);`:
```ts
  // La figura viva de la tarjeta "Ahora mismo" (spec 2026-09-05). Sin
  // destroy() propio por el mismo motivo que montarRoce (ver el comentario
  // "Sin destroy() propio" al final del fichero); el handle existe para la
  // entrada (montarEntrada lo recibe) y para tests.
  const figuraViva = montarFiguraViva(gsap, root);
```
y cambiar la llamada `montarEntrada(gsap, root);` para que quede DESPUÉS y reciba el handle: `montarEntrada(gsap, root, figuraViva);` (la firma se amplía en la Task 5; en esta tarea, añadir a `montarEntrada` un tercer parámetro opcional `figura?: FiguraVivaHandle` sin usarlo todavía, para que compile). Actualizar el `import` de `./caelestia.titulo` con `montarFiguraViva`.

- [ ] **Step 4: Quitar el `border-radius: 50%` provisional de `.cae-wfig`** (Task 3, Step 2): ahora manda el `clip-path`. En themes.css sustituir esa línea por `/* la forma la pone montarFiguraViva con clip-path (240 vertices) */`.

- [ ] **Step 5: Build, lint, gate**

```bash
npm run build && npm run lint && python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183 2>&1 | grep -A6 "la figura vive"
```
Expected: 240 pares OK, cambia sola OK, quieta con reduce OK. Comprobar también en la consola del navegador (`pageerror`) que no hay error: `gsap` llega por parámetro, nunca por `import` directo en este fichero.

- [ ] **Step 6: Commit**

```bash
git add src/utils/figurasM3.ts src/themes/caelestia.titulo.ts src/themes/caelestia.choreography.ts src/themes/themes.css scripts/measure-caelestia-titulo.py
git commit -m "feat(hero): la figura viva de la tarjeta Ahora mismo morfa con la hora y mira al cursor"
```

---

### Task 5: La entrada brota de la luz

**Files:**
- Modify: `src/themes/caelestia.titulo.ts` (`montarEntrada`: estado inicial y paso 11)
- Modify: `scripts/measure-caelestia-titulo.py` (`entrada`: ampliar `LEE_ENTRADA` y aserciones)

**Interfaces:**
- Consumes: `FiguraVivaHandle.relieve.v` y `.pinta()` de la Task 4.

- [ ] **Step 1: Gate en rojo**

En `LEE_ENTRADA` (dentro de `entrada`), añadir al objeto devuelto:
```js
        tarjetaClip: (() => { const w = q('#hero .cae-widget'); return w ? (w.style.clipPath || '') : ''; })(),
        tarjetaOp: (() => { const w = q('#hero .cae-widget'); return w ? parseFloat(getComputedStyle(w).opacity) : null; })(),
```
Y tras la aserción del widget («queda puesto al final»), añadir:
```python
        brota = [m for m in muestras if m.get("tarjetaClip", "").startswith("circle(")]
        radios = []
        for m in brota:
            mm = re.search(r"circle\(([\d.]+)px", m["tarjetaClip"])
            if mm:
                radios.append(float(mm.group(1)))
        assert_que(bool(radios) and min(radios) < 20, f"la tarjeta brota de la luz: hubo un circle() de radio < 20 px ({min(radios) if radios else 'ninguno'})")
        assert_que(not muestras[-1].get("tarjetaClip"), f"al aterrizar la tarjeta no conserva clip-path inline ({muestras[-1].get('tarjetaClip')!r})")
```
(`re` ya está importado por la Task 1.) **Dos ajustes al bucle que espera a la tarjeta** (el que hoy afirma «el widget .cae-widget queda puesto al final de la entrada»), porque el brote ocurre DESPUÉS del aterrizaje de la firma, fuera del muestreo principal, y porque con la entrada nueva la opacidad de la tarjeta ya no cambia (cambia su `clip-path`):
1. En cada vuelta del bucle, leer también `style.clipPath` de la tarjeta y la opacidad de su último hijo, y guardar la lectura en `muestras` (`muestras.append({"t": time.monotonic() - t0, "firmaExiste": True, "typed": "whoami", "tarjetaClip": w["clip"], **w})`), para que `brota` las vea.
2. La condición de «puesta» pasa a ser: `w["clip"] == ""` y opacidad del último hijo `>= 0.99` y `visibility` visible. Si no llega en 25 s, FALLA (como ahora).
Correr: rojo en «brota» (hoy la tarjeta entra con un `fromTo` de opacidad, sin `circle`).

- [ ] **Step 2: La entrada en `montarEntrada`**

Firma: `export function montarEntrada(gsap: Gsap, root: HTMLElement, figura: FiguraVivaHandle = FIGURA_NULA): EntradaHandle`.

En el bloque de estados iniciales (donde está `if (widget) gsap.set(widget, { opacity: 0, y: 8 });`), sustituir por:
```ts
  if (widget) {
    // Brota de la luz: el circulo se centra en la luz de la pastilla, medida
    // AQUI (con la caja ya definitiva; medir al montar daba la caja colapsada,
    // misma trampa que el aterrizaje del trazo).
    gsap.set(widget, { opacity: 1, y: 0 });
    const luz = widget.querySelector<HTMLElement>(".cae-wluz");
    const wr = widget.getBoundingClientRect();
    const lr = luz?.getBoundingClientRect();
    const cx = lr ? lr.left + lr.width / 2 - wr.left : wr.width / 2;
    const cy = lr ? lr.top + lr.height / 2 - wr.top : wr.height / 2;
    widget.style.clipPath = `circle(0px at ${cx}px ${cy}px)`;
    gsap.set(Array.from(widget.children), { opacity: 0, y: 6 });
    figura.relieve.v = 0;
    figura.pinta();
    brote = { cx, cy };
  }
```
Declarar antes, junto a `const widget = ...`: `let brote: { cx: number; cy: number } | null = null;`.

Sustituir el paso 11 (el `fromTo` del widget) por:
```ts
  // 11. La tarjeta "Ahora mismo" brota de su luz: el circulo crece desde el
  // punto de la pastilla, la figura florece de circulo a figura y el texto se
  // posa. Al terminar se limpia el clip-path inline: una mascara viva sobre
  // la tarjeta rompe el hover y la capa de estado.
  if (widget && brote) {
    const radio = { r: 0 };
    const { cx, cy } = brote;
    tl.to(
      radio,
      {
        r: 420,
        duration: 0.85,
        ease: "power3.inOut",
        onUpdate: () => {
          widget.style.clipPath = `circle(${radio.r.toFixed(1)}px at ${cx}px ${cy}px)`;
        },
        onComplete: () => {
          widget.style.clipPath = "";
        },
      },
      "-=0.2",
    );
    tl.to(figura.relieve, { v: 1, duration: 0.8, ease: "back.out(1.4)", onUpdate: figura.pinta }, "<");
    tl.fromTo(
      Array.from(widget.children),
      { opacity: 0, y: 6 },
      { opacity: 1, y: 0, duration: 0.3, ease: "power2.out", stagger: 0.06 },
      "-=0.5",
    );
  }
```
En la rama de movimiento reducido de `montarEntrada` no hay que tocar nada: no escribe `clip-path` y `montarFiguraViva` ya pintó la figura con relieve 1.

Comprobar `destroy`: `tl.kill()` deja el `clip-path` a medias si se mata en mitad del brote. Añadir en `destroy`: `if (widget) widget.style.clipPath = "";` y `figura.relieve.v = 1; figura.pinta();` (kill NO dispara onComplete: trampa documentada del proyecto).

- [ ] **Step 3: Build, lint, arnés entero**

```bash
npm run build && npm run lint && python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183
```
Expected: `0 fallo(s)`, incluidas las dos aserciones nuevas de `[entrada]` y todas las de `[tarjeta]`.

- [ ] **Step 4: Verlo**

Con Playwright, `wait_until="commit"` y muestreo cada 40 ms del `style.clipPath` de la tarjeta hasta el aterrizaje: imprimir la serie de radios (debe ir de ~0 a 420 y luego vacío). Y una captura a mitad del brote si se pilla (anclada: primera muestra con radio entre 60 y 200).

- [ ] **Step 5: Commit**

```bash
git add src/themes/caelestia.titulo.ts scripts/measure-caelestia-titulo.py
git commit -m "feat(hero): la tarjeta Ahora mismo brota de su luz al entrar"
```

---

### Task 6: Contraste en las 24 horas con la capa de estado, verificación final y cierre

**Files:**
- Modify: `scripts/measure-caelestia-titulo.py` (nueva `tarjeta_contraste`)
- Modify: `docs/superpowers/specs/2026-09-05-caelestia-ahora-mismo-design.md` (Estado y registro)
- Modify: `.claude/rules/verification.md` (fila de `measure-caelestia-titulo.py`)

- [ ] **Step 1: Gate de contraste, y verlo en rojo con un sabotaje**

Copiar de `scripts/measure-caelestia-obra.py` las funciones `_oklab_to_srgb255`, `_parse_rgb`, `_luminancia` y `_ratio` (líneas ~334-405) al arnés de Título si no existen ya equivalentes (comprobar con `grep -n "def _ratio\|def contraste" scripts/measure-caelestia-titulo.py`; si existe `contraste(lumA, lumB)` y `luz_texto`, usarlas y solo añadir el parseo de `oklch`). Nueva función:
```python
def tarjeta_contraste(pg, base: str) -> None:
    print("\n[tarjeta] contraste AA de sus pares en las 24 horas, con la capa de estado puesta")
    PARES = [
        ("primero", "#hero .cae-wnow"),
        ("ubicacion", "#hero .cae-wsub"),
        ("fecha", "#hero .cae-wfecha"),
        ("nombre", "#hero .cae-wnombre"),
        ("pastilla", "#hero .cae-pilla"),
    ]
    peor = (99.0, "", "")
    for h in range(0, 24, 3):
        abrir(pg, base, f"{h:02d}:30")
        pg.hover("#hero .cae-widget")  # hover REAL: un MouseEvent sintetico no dispara :hover
        pg.wait_for_timeout(400)      # la capa de estado tiene transition 0.25s
        for nombre, sel in PARES:
            d = pg.evaluate(
                """(sel) => {
                  const e = document.querySelector(sel); if (!e) return null;
                  const cs = getComputedStyle(e);
                  // fondo: la pastilla pinta el suyo; el resto lee la tarjeta y le apila la capa de estado
                  const w = document.querySelector('#hero .cae-widget');
                  const capa = getComputedStyle(w, '::after');
                  return { fg: cs.color, bg: sel.includes('pilla') ? cs.backgroundColor : getComputedStyle(w).backgroundColor,
                           capa: capa.backgroundColor, capaOp: parseFloat(capa.opacity) };
                }""",
                sel,
            )
            assert_que(d is not None, f"existe {sel}")
            if d is None:
                continue
            fg = _parse_rgb(d["fg"]); bg = _parse_rgb(d["bg"]); capa = _parse_rgb(d["capa"])
            if not fg or not bg:
                assert_que(False, f"no se pudo parsear el color de {nombre} ({d['fg']} / {d['bg']})")
                continue
            if capa and d["capaOp"] > 0 and "pilla" not in sel:
                a = d["capaOp"]
                bg = tuple(bg[i] * (1 - a) + capa[i] * a for i in range(3)) + (1.0,)
            r = _ratio(fg[:3], bg[:3])
            if r < peor[0]:
                peor = (r, nombre, f"{h:02d}:30")
    assert_que(peor[0] >= 4.5, f"peor par de la tarjeta {peor[1]} a las {peor[2]}: {peor[0]:.2f}:1 (piso AA 4.5)")
```
Llamar tras `tarjeta_figura`. **Sabotaje obligatorio**: cambiar temporalmente en themes.css `.cae-wfecha { color: var(--cae-outline) }`, build, correr: debe salir rojo (la `outline` da ~1,8:1 de noche, el fallo real de B4). Deshacer el sabotaje, build, correr: verde. Anotar los dos resultados literales en el commit.

- [ ] **Step 2: Verificación completa**

```bash
npm run build && npm run lint
python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4183       # 0 fallo(s)
python3 scripts/measure-caelestia-hora.py --base http://127.0.0.1:4183         # shell intacto (nohup + PID, tarda minutos)
python3 scripts/measure-caelestia-quien-soy.py --base http://127.0.0.1:4183    # la ficha con el literal nuevo
python3 scripts/verify.py --url http://127.0.0.1:4183                          # 0 nuevos
```
Capturas 1440×900 de `?theme=caelestia` a las 13:00 y 23:00, y de `?theme=vice` y `?theme=hyprland` (no deben cambiar: `.cae-widget` sigue `display: none` fuera de Caelestia en `style.css`). Escuchar `pageerror` y `console` error en todas.

- [ ] **Step 3: Gates de crítica**

Lanzar `lidia-naive-tester` y `vera-art-director` sobre el hero de Caelestia (brief: solo la tarjeta y su entrada; prohibido editar producción). Registrar resultados en el spec (§ «Gates de crítica»). Un P0 se arregla antes de cerrar; los P1 se anotan.

- [ ] **Step 4: Cerrar el spec y la documentación**

- Spec: `Estado: implementado`, más una sección `## Registro de implementación` con: lo que rompió cada gate en rojo, medidas finales (ancho del primero con `Range`, peor contraste del barrido, radios del brote), y las desviaciones respecto al spec si las hubo.
- `.claude/rules/verification.md`, fila de `measure-caelestia-titulo.py`: añadir «la tarjeta “Ahora mismo”: orden y columnas fechadas, sin caja (surface-container-high, sin borde), primero a opsz 60 en una línea medida con `Range`, la luz respira solo con movimiento, la figura viva de 240 vértices cambia sola y queda quieta con reduce, la entrada brota de la luz (`circle()` de radio < 20 leído durante la entrada, sin `clip-path` inline al aterrizar) y el contraste de sus cinco pares en las 24 horas con la capa de estado puesta (hover real)».
- Memoria: actualizar `caelestia-carga-paso-a-paso.md` (el widget ya no está pendiente).

- [ ] **Step 5: Commit y cierre de rama**

```bash
git add scripts/measure-caelestia-titulo.py docs/superpowers/specs/2026-09-05-caelestia-ahora-mismo-design.md
git commit -m "feat(hero): contraste de la tarjeta Ahora mismo en las 24 horas y cierre del spec"
```
Después, `superpowers:finishing-a-development-branch`: fusionar `design/caelestia-ahora-mismo` en `fix/repaso-interfaces` (o en `main` si Aoshi ya fusionó el repaso), retirar el worktree, matar el preview por PID.
