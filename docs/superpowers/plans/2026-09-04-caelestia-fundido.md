# Caelestia B5 — Fundido: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convertir la escena `#contacto` de Caelestia en la contraportada del escritorio — campo de
color invertido, titular de cierre a `--t-10`, colofón jerarquizado, troquel de Material 3 con el
dino de Chrome, fundido de entrada y adaptación a 390 px — sin tocar Vice ni Hyprland.

**Architecture:** Todo el diseño vive en CSS colgado de `:root[data-theme="caelestia"]` más **un
módulo de escena propio** (`src/themes/caelestia.fundido.ts`) que hace lo que el CSS no puede:
partir el titular en líneas, inyectar el sprite, y correr el fundido y la entrada. El módulo se
monta desde `caelestia.choreography.ts` con el mismo contrato que `montarFicha` (B2): recibe `gsap`
por parámetro, nunca lo importa. `src/sections/contacto.ts` solo gana **ganchos**, no contenido.

**Tech Stack:** Vite + TypeScript (strict) + Tailwind + GSAP. Sin framework, sin Three.js.
Verificación con Playwright desde Python.

**Spec:** `docs/superpowers/specs/2026-09-04-caelestia-fundido-design.md`

## Global Constraints

Copiadas del spec y de los dos `CLAUDE.md`. **Los requisitos de cada tarea las incluyen.**

- **No `any`.** `strict` está activo; usar `unknown` con guardas.
- **No `gsap.from`.** Solo `fromTo` con los dos extremos escritos a mano. Ha causado tres
  regresiones reales.
- **`gsap` llega SIEMPRE por parámetro**, desestructurado del contexto de la coreografía. Un
  `import gsap from "gsap"` compila, pasa el linter y revienta en el navegador.
- **No `console.log` en producción.**
- **`rel="noopener noreferrer"` en los enlaces externos** y `tel:` sin espacios ni guiones: es
  requisito de seguridad, no de diseño.
- **El dato se lee sin hover.** Escrito como decisión explícita en `contacto.ts`.
- **Sin scroll interno en la escena**, a 1440 y a 390. Ley de la fase A.
- **La escala tipográfica se escalona en pasos discretos.** Prohibido `clamp()` o `vw` sobre tokens
  de escala.
- **`prefers-reduced-motion` deja la escena aterrizada**, no una versión corta. El selector `*` en
  la guarda de CSS **no alcanza a los pseudo-elementos**.
- **Vice está cerrado y no se toca.** Hyprland tampoco. `contacto.ts` es compartido por los tres.
- **No declarar DONE sin build + captura real en navegador.**
- **`npm` se ejecuta con Node 22, no con el del PATH.** El `node` por defecto de esta maquina es
  v18.19.1 y `npm run build` revienta con `does not provide an export named 'styleText'`. Cada
  bloque de comandos empieza por:
  `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`
- **El puerto es 4193 y NO se arranca ningun servidor.** El `vite preview` de este worktree ya corre
  ahi y sirve `dist/` desde disco. **En 4173 corre otra sesion sirviendo otro repositorio**: medir
  ahi da verde contra codigo ajeno. Cada bloque comprueba la huella del bundle antes de medir.
- Comandos: `npm run build`, `npm run lint`.

---

## Estructura de ficheros

| Fichero | Responsabilidad |
|---|---|
| `src/sections/contacto.ts` (modificar) | **Solo atributos.** Marcar cada canal como acto o destino y poner el gancho del titular. Ni una cadena nueva, ni un elemento nuevo, ni un cambio de orden. |
| `src/themes/caelestia.fundido.ts` (crear) | Lo que el CSS no puede: partir el titular en líneas, montar el troquel, correr el fundido y la entrada. Devuelve un handle. |
| `src/themes/caelestia.dino.ts` (crear) | **El sprite, aislado.** Mapas de bits del dino, la nube y el horizonte, y su conversión a SVG. Quitar el bicho = borrar este fichero y una llamada. |
| `src/themes/caelestia.choreography.ts` (modificar) | Montar el módulo y dispararlo al entrar en el workspace, con la regla de B2. |
| `src/themes/themes.css` (modificar) | Todo el aspecto de la escena, en un bloque nuevo tras el de B2. |
| `scripts/measure-caelestia-fundido.py` (crear) | Los doce gates del spec. |
| `docs/superpowers/maquetas/2026-09-04-caelestia-fundido-*.html` (crear) | Rescate de las maquetas aprobadas, que hoy viven en `.superpowers/` (ignorado). |

---

## Task 1: Rescatar las maquetas aprobadas del directorio ignorado

`.superpowers/` está en `.gitignore` (línea 47). Las ocho maquetas aprobadas por Aoshi viven ahí y
**se pierden en cuanto se limpie el worktree**. Va primero porque es lo único irrecuperable.

**Files:**
- Create: `docs/superpowers/maquetas/2026-09-04-caelestia-fundido-composicion.html`
- Create: `docs/superpowers/maquetas/2026-09-04-caelestia-fundido-escala.html`
- Create: `docs/superpowers/maquetas/2026-09-04-caelestia-fundido-canales.html`
- Create: `docs/superpowers/maquetas/2026-09-04-caelestia-fundido-movimiento.html`
- Create: `docs/superpowers/maquetas/2026-09-04-caelestia-fundido-entrada.html`
- Create: `docs/superpowers/maquetas/2026-09-04-caelestia-fundido-movil.html`
- Create: `docs/superpowers/maquetas/README.md`

- [ ] **Step 1: Localizar el directorio del companion**

```bash
ls .superpowers/brainstorm/*/content/*.html
```

Esperado: al menos `10-dino-chrome.html`, `12-escala.html`, `13-canales.html`, `14-fundido.html`,
`15-entrada.html`, `16-movil.html`.

- [ ] **Step 2: Copiar las seis maquetas que documentan decisiones aprobadas**

```bash
mkdir -p docs/superpowers/maquetas
D=$(ls -d .superpowers/brainstorm/*/content | head -1)
cp "$D/10-dino-chrome.html" docs/superpowers/maquetas/2026-09-04-caelestia-fundido-composicion.html
cp "$D/12-escala.html"      docs/superpowers/maquetas/2026-09-04-caelestia-fundido-escala.html
cp "$D/13-canales.html"     docs/superpowers/maquetas/2026-09-04-caelestia-fundido-canales.html
cp "$D/14-fundido.html"     docs/superpowers/maquetas/2026-09-04-caelestia-fundido-movimiento.html
cp "$D/15-entrada.html"     docs/superpowers/maquetas/2026-09-04-caelestia-fundido-entrada.html
cp "$D/16-movil.html"       docs/superpowers/maquetas/2026-09-04-caelestia-fundido-movil.html
```

- [ ] **Step 3: Arreglar la única dependencia externa**

Las maquetas de movimiento y entrada cargan `<script src="/files/gsap.min.js">`, que solo existe
mientras corre el servidor del companion. Se apunta al CDN para que sigan abriéndose sueltas.

```bash
sed -i 's#<script src="/files/gsap.min.js"></script>#<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>#' \
  docs/superpowers/maquetas/2026-09-04-caelestia-fundido-movimiento.html \
  docs/superpowers/maquetas/2026-09-04-caelestia-fundido-entrada.html
grep -c 'files/gsap' docs/superpowers/maquetas/*.html
```

Esperado: `0` en todos.

- [ ] **Step 4: Escribir el README que dice qué es cada una**

```markdown
# Maquetas de la fase B5 — Fundido

Rescatadas del companion de brainstorming el 2026-09-04, porque `.superpowers/` está en
`.gitignore` (línea 47) y lo que se queda ahí se pierde.

Son **fragmentos de pantalla**, no páginas: se escribieron para incrustarse en el companion, así
que abiertas sueltas no traen `<html>` ni `<head>`. El navegador las muestra igual.

| fichero | qué decidió |
|---|---|
| `…-composicion.html` | K · la contraportada, y las micro-interacciones del bicho |
| `…-escala.html` | `--t-10` para el cierre, y los cuatro tokens de ejes |
| `…-canales.html` | B · el pie de imprenta: dos actos y dos destinos |
| `…-movimiento.html` | el fundido: 7 gestos, 1900 ms, con partitura viva |
| `…-entrada.html` | la entrada de 440 ms, y la regla de «suena una vez» |
| `…-movil.html` | 390 px, el sello entero y la figura de ocho lóbulos |

Las de movimiento y entrada cargan GSAP del CDN; en el companion venía de `/files/`.
```

- [ ] **Step 5: Comprobar que se abren sin el servidor del companion**

```bash
python3 -c "
import pathlib
for f in sorted(pathlib.Path('docs/superpowers/maquetas').glob('*.html')):
    s = f.read_text()
    assert 'localhost' not in s, f'{f.name} apunta a localhost'
    assert '/files/' not in s, f'{f.name} apunta a /files/'
    print(f'{f.name}: {len(s)} B, OK')
"
```

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/maquetas
git commit -m "docs(fundido): rescata al repo las seis maquetas aprobadas de B5

.superpowers/ esta en .gitignore y lo que se queda ahi se pierde."
```

---

## Task 2: Los ganchos en el DOM compartido

`contacto.ts` lo comparten los tres temas. Esta tarea le añade **solo atributos**: ni una cadena
nueva, ni un elemento nuevo, ni un cambio en el orden de los hijos.

**Por qué no hay envoltorios.** La versión anterior de esta tarea agrupaba los cuatro canales en un
`<div>` de actos y otro de destinos. Eso **reordena el DOM** —de correo·LinkedIn·teléfono·GitHub a
correo·teléfono·LinkedIn·GitHub— y con él el orden visible de las cuatro barras **en Vice, que es un
diseño cerrado que no se toca**, y en Hyprland. El agrupamiento visual de Caelestia lo hace su CSS
con `order` (Task 4), que no le cambia el DOM a nadie.

**Files:**
- Modify: `src/sections/contacto.ts`
- Test: `scripts/measure-caelestia-fundido.py` (creado en la Task 8; aquí se verifica a mano)

**Interfaces:**
- Produces: en el DOM, `[data-canal="acto"]` y `[data-canal="destino"]` sobre cada
  `a.contacto-bar`, y `[data-fundido-lead]` sobre el `<p>` del titular de cierre. **El orden de los
  hijos de `.contacto-bars` no cambia**: sigue siendo el de `contactChannels` — correo, LinkedIn,
  teléfono, GitHub. Las Tasks 4, 5 y 6 dependen de estos nombres y de ese orden.

- [ ] **Step 1: Verificar el punto de partida en el navegador**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
    pg.wait_for_timeout(3000)
    print(pg.evaluate("""() => ({
        canales: document.querySelectorAll('[data-canal]').length,
        lead: !!document.querySelector('[data-fundido-lead]'),
    })"""))
    b.close()
PY
```

Esperado: `{'canales': 0, 'lead': False}` — los ganchos no existen todavía.

- [ ] **Step 2: Añadir el tipo de canal, derivado del `href`**

En `src/sections/contacto.ts`, dentro de `createBar`, justo antes del `return bar;`:

```ts
  /*
   * Acto o destino. NO es una etiqueta nueva en `content.ts`: se deriva del
   * esquema del `href` que ya existe. `mailto:` y `tel:` disparan una
   * aplicacion del aparato y siguen sirviendo sin red; los externos abren una
   * pestana y la necesitan. Caelestia dimensiona cada grupo distinto con esto
   * (fase B5); Vice y Hyprland lo ignoran.
   */
  const esquema = channel.href.split(":")[0];
  bar.dataset.canal = esquema === "mailto" || esquema === "tel" ? "acto" : "destino";
```

- [ ] **Step 3: Dejar `.contacto-bars` exactamente como está**

No hay nada que hacer aquí, y es deliberado. La línea

```ts
  const bars = el("div", "contacto-bars", contactChannels.map(createBar));
```

**se queda tal cual**. Los cuatro canales siguen siendo hijos directos y en el orden de
`contactChannels`. Añadir envoltorios reordenaría el DOM y con él el orden visible de las barras en
Vice y en Hyprland; el agrupamiento visual de Caelestia lo hace su CSS con `order` en la Task 4.

- [ ] **Step 4: Poner el gancho del titular de cierre**

En `createContacto`, sustituir:

```ts
    el("p", "contacto-lead", [identity.invitation]),
```

por:

```ts
    lead,
```

y declararlo antes de `const band`:

```ts
  // El titular de cierre de Caelestia (B5) se parte en lineas para trazarlas
  // una a una, y eso lo hace `caelestia.fundido.ts` en el navegador. Aqui solo
  // queda el gancho: el texto sigue siendo el mismo literal de `content.ts`.
  const lead = el("p", "contacto-lead", [identity.invitation]);
  lead.setAttribute("data-fundido-lead", "");
```

- [ ] **Step 5: Construir y comprobar que los ganchos existen y no rompen nada**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run lint && npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
FALLOS = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for tema in ("caelestia", "vice", "hyprland"):
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://localhost:4193/?theme={tema}", wait_until="domcontentloaded")
        pg.wait_for_timeout(3000)
        d = pg.evaluate("""() => {
            const bars = [...document.querySelectorAll('a.contacto-bar')];
            return {
              n: bars.length,
              tipos: bars.map(a => a.dataset.canal),
              orden: bars.map(a => a.getAttribute('href').split(':')[0]),
              lead: !!document.querySelector('[data-fundido-lead]'),
              rel: bars.filter(a => a.target === '_blank')
                       .every(a => (a.rel || '').includes('noopener') && (a.rel || '').includes('noreferrer')),
              tel: bars.filter(a => a.getAttribute('href').startsWith('tel:'))
                       .every(a => /^tel:\\+?\\d+$/.test(a.getAttribute('href'))),
            };
        }""")
        print(tema, d, "errores:", errs or "ninguno")
        if d["n"] != 4: FALLOS.append(f"{tema}: {d['n']} canales, esperados 4")
        if d["tipos"] != ["acto", "destino", "acto", "destino"]:
            FALLOS.append(f"{tema}: tipos {d['tipos']}")
        if not d["rel"] or not d["tel"]: FALLOS.append(f"{tema}: rel/tel rotos")
        if errs: FALLOS.append(f"{tema}: {errs}")
        pg.close()
    b.close()
print("FALLOS:", FALLOS or "ninguno")
assert not FALLOS
PY
```

Esperado: los tres temas con 4 canales, tipos `acto, destino, acto, destino` (el orden de
`contactChannels` es correo, linkedin, telefono, github), `rel`/`tel` intactos, cero errores.

- [ ] **Step 6: Ver que el orden visible no ha cambiado en Vice ni en Hyprland**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for tema in ("vice", "hyprland"):
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(f"http://localhost:4193/?theme={tema}#contacto", wait_until="domcontentloaded")
        pg.wait_for_timeout(3500)
        pg.eval_on_selector('[data-scene="contacto"]', "e => e.scrollIntoView()")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=f"/tmp/b5-t2-{tema}.png")
        print(tema, pg.evaluate("""() => [...document.querySelectorAll('a.contacto-bar')]
            .map(a => Math.round(a.getBoundingClientRect().top))"""))
        pg.close()
    b.close()
PY
```

Mirar `/tmp/b5-t2-vice.png` y `/tmp/b5-t2-hyprland.png`: **las cuatro barras tienen que seguir
apiladas, en el mismo orden y con la misma pinta.** Esta tarea solo añade atributos, así que la
única forma de romperlas sería que algún selector de esos temas usara `a.contacto-bar:not([data-*])`
o similar — improbable, pero la captura es barata y el diseño de Vice está cerrado.

- [ ] **Step 7: Commit**

```bash
git add src/sections/contacto.ts
git commit -m "feat(contacto): ganchos de canal y de titular para la fase B5

Acto o destino se deriva del esquema del href, sin campo nuevo en content.ts y
sin tocar el orden de los hijos: envolverlos habria reordenado las barras en
Vice, que esta cerrado."
```

---

## Task 3: Los tokens de ejes de Fraunces

Renombrado puro más un token nuevo. **No mueve un píxel** de B1 ni de B2, y hay que demostrarlo con
capturas antes y después.

**Files:**
- Modify: `src/themes/themes.css:3533` (declaración de tokens) y las tres reglas con el literal
  (`:3949`, `:3991`, `:4104` — los números pueden haberse movido; buscar por contenido)

**Interfaces:**
- Produces: `--cae-display-axes-texto` y `--cae-display-axes-cierre`. La Task 4 usa el segundo.

- [ ] **Step 1: Capturar B1 y B2 antes de tocar nada**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
    pg.wait_for_timeout(3500)
    pg.screenshot(path="/tmp/b5-t3-antes-hero.png")
    pg.click('[data-cae-ws="quien-es"]'); pg.wait_for_timeout(2500)
    pg.screenshot(path="/tmp/b5-t3-antes-about.png")
    b.close()
PY
```

- [ ] **Step 2: Declarar los dos tokens nuevos**

En `src/themes/themes.css`, justo después de la declaración de `--cae-display-axes-cartel`:

```css
  /*
   * La voz de TEXTO. Es el literal que B1 y B2 ya escribian a mano en tres
   * reglas — la firma, el widget «Ahora mismo» y la frase de la ficha — y que
   * NO coincide con `--cae-display-axes`, que dice 900. Ponerle nombre no
   * cambia un pixel: es el mismo valor, escrito una vez.
   */
  --cae-display-axes-texto: "opsz" 9, "wght" 700, "SOFT" 0, "WONK" 1;

  /*
   * La voz de CIERRE, y solo se usa en un sitio de todo el sitio: la frase de
   * «Fundido» (B5). `SOFT` a 100 redondea los angulos de los remates — la
   * misma familia hablando bajo. Si se usara en dos sitios deja de significar
   * «esto se acaba».
   */
  --cae-display-axes-cierre: "opsz" 144, "wght" 300, "SOFT" 100, "WONK" 1;
```

- [ ] **Step 3: Sustituir los tres literales por el token**

```bash
grep -n '"opsz" 9, "wght" 700, "SOFT" 0, "WONK" 1' src/themes/themes.css
```

Esperado: tres coincidencias, todas como valor de `font-variation-settings`. Sustituir cada una por
`var(--cae-display-axes-texto)`. **No tocar** la línea de la declaración del token nuevo.

- [ ] **Step 4: Comprobar que no queda ningún literal y que el token se usa tres veces**

```bash
grep -c 'var(--cae-display-axes-texto)' src/themes/themes.css   # esperado: 3
grep -c '"opsz" 9, "wght" 700' src/themes/themes.css            # esperado: 1 (la declaracion)
```

- [ ] **Step 5: Capturar después y comparar píxel a píxel**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run lint && npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
    pg.wait_for_timeout(3500)
    pg.screenshot(path="/tmp/b5-t3-despues-hero.png")
    pg.click('[data-cae-ws="quien-es"]'); pg.wait_for_timeout(2500)
    pg.screenshot(path="/tmp/b5-t3-despues-about.png")
    b.close()
PY
python3 - <<'PY'
from PIL import Image, ImageChops
for n in ("hero", "about"):
    a = Image.open(f"/tmp/b5-t3-antes-{n}.png").convert("RGB")
    d = Image.open(f"/tmp/b5-t3-despues-{n}.png").convert("RGB")
    caja = ImageChops.difference(a, d).getbbox()
    print(n, "diferencia:", caja or "NINGUNA")
PY
```

Esperado: `NINGUNA` en las dos. **El color de Caelestia sigue el reloj**, así que las dos capturas
tienen que tomarse con pocos minutos de diferencia; si el matiz se ha movido, la comparación dará
diferencia por el fondo y no por la tipografía — repetir seguidas.

- [ ] **Step 6: Commit**

```bash
git add src/themes/themes.css
git commit -m "refactor(caelestia): nombra la voz de texto y anade la de cierre

--cae-display-axes-texto renombra el literal que B1 y B2 escribian tres veces,
y que no coincidia con --cae-display-axes (900 declarado, 700 usado).
--cae-display-axes-cierre es nuevo y solo lo usa la frase de B5.
Capturas antes/despues de hero y about: sin diferencia."
```

---

## Task 4: La composición — el campo de color y la escala del cierre

Sin animación todavía y sin troquel: solo que la escena deje de estar rota.

**Files:**
- Modify: `src/themes/themes.css` — bloque nuevo inmediatamente antes del comentario
  `/*\n * La barra del shell: marca, pastillas de workspace y bandeja de estado.` (≈ línea 4554)

**Interfaces:**
- Consumes: `[data-canal]` y `[data-fundido-lead]` (Task 2), con los cuatro canales como hijos
  directos de `.contacto-bars` y en el orden de `contactChannels`; `--cae-display-axes-cierre`
  (Task 3).
- Produces: `--fundido-dim` sobre `[data-scene="contacto"]`. La Task 5 lo hereda.

- [ ] **Step 1: Escribir el bloque de la escena**

```css
/*
 * ===================================================================
 * FUNDIDO (fase B5) — la contraportada del escritorio
 *
 * Es la UNICA de las cinco escenas que invierte a un campo de color: las
 * otras cuatro son ventanas de aplicacion sobre el escritorio, esta es una
 * superficie `--cae-primary` a sangre. Eso es lo que la hace legible como
 * final sin que nadie lo explique.
 *
 * La excepcion al panel opaco generico de la fase A es deliberada, igual que
 * la de `[data-scene="hero"]`, y esta acotada a esta escena.
 * ===================================================================
 */
:root[data-theme="caelestia"] main[data-cae-track] > [data-scene="contacto"] {
  background: var(--cae-primary);
  color: var(--cae-on-primary);
}

/*
 * El atenuado del cierre. UN NUMERO CALIBRADO CONTRA UNA SUPERFICIE, no un
 * porcentaje suelto: 0,82 sobre `--cae-primary` da 4,80:1 en el peor de los
 * 288 pasos del dia. A 0,72 caia a 4,08:1 y no llegaba a AA; el suelo exacto
 * esta en 0,78 (4,50:1, sin margen).
 *
 * SI ESTO SE REUTILIZA SOBRE OTRA SUPERFICIE, HAY QUE VOLVER A MEDIRLO. Una
 * opacidad es un porcentaje de un fondo concreto: llevarse el numero es no
 * llevarse nada. Misma regla que `--nav-dim`.
 */
:root[data-theme="caelestia"] [data-scene="contacto"] {
  --fundido-dim: 0.82;
  display: flex;
  flex-direction: column;
  padding: 2.125rem 3.25rem 1.875rem;
  min-height: 0;
}

/* El antetitulo y el estado se apagan: en la contraportada el rotulo de
   seccion lo lleva la esquina, y el estado baja al pie. */
:root[data-theme="caelestia"] [data-scene="contacto"] .hero-kick,
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-estado-label,
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-estado-sep {
  display: none;
}

/*
 * EL TITULAR DE CIERRE. `--t-10` no sale a ojo: la linea larga mide 530 px
 * sobre un hueco libre de 858, asi que el techo no lo pone el troquel — lo
 * decide la ocupacion. A `--t-8` la frase flota en el campo de color.
 *
 * Un PASO de la escala, nunca un `clamp()` ni un `vw`: una funcion continua
 * devuelve cualquier real entre sus topes y se esconde justo en 390 y 1440,
 * que es donde se mira.
 */
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-lead {
  font-family: var(--font-display);
  font-style: italic;
  font-variation-settings: var(--cae-display-axes-cierre);
  font-size: var(--t-10);
  line-height: 0.88;
  letter-spacing: -0.028em;
  margin: 0;
  max-width: 48.75rem;
}

/* «Hablemos» desaparece: el titular de la escena es la invitacion, y dos
   titulares seguidos se estorban. El `h2` sigue en el arbol para los lectores
   de pantalla — se oculta visualmente, no semanticamente. */
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-title {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

/*
 * `position: relative` NO es decorativo: el troquel de la Task 5 es absoluto y
 * necesita un ancestro posicionado. Sin esto se colocaria contra la seccion,
 * que lleva la clase `relative` de Tailwind desde `contacto.ts` — funcionaria
 * por accidente y se romperia el dia que alguien quitase esa clase.
 */
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-band {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  min-height: 0;
}

/* ---------- el pie de imprenta ---------- */

/*
 * LOS CUATRO CANALES SE AGRUPAN CON `order`, NO CON ENVOLTORIOS. En el DOM
 * siguen en el orden de `contactChannels` — correo, LinkedIn, telefono,
 * GitHub — porque envolverlos reordenaria las barras tambien en Vice, que
 * esta cerrado. Aqui los dos actos se van delante y los dos destinos detras
 * sin que el arbol cambie: el orden de lectura de un lector de pantalla sigue
 * siendo el del DOM, que es el orden en el que estan escritos los datos.
 */
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-bars {
  display: flex;
  align-items: flex-end;
  gap: 3.5rem;
  border-top: 1px solid currentColor;
  padding-top: 1.125rem;
}

:root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="acto"] {
  order: 1;
}

:root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="destino"] {
  order: 2;
}

/*
 * El primer destino empuja la pareja al canto derecho. Es `:nth-child(2)`
 * porque LinkedIn es el segundo canal de `contactChannels`; si algun dia se
 * anade un canal antes que el, esta regla deja de ser cierta y el colofon se
 * queda pegado a los actos — visible al instante, no silencioso.
 */
:root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="destino"]:nth-child(2) {
  margin-left: auto;
}

/* Entre los dos destinos el aire es menor que entre los actos: son una pareja,
   no dos columnas. El `gap` general los separaria igual que a los grandes. */
:root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="destino"] + [data-canal="destino"] {
  margin-left: -1.75rem;
}

:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-bar {
  text-decoration: none;
  color: inherit;
  border-radius: 0.5rem;
}

/*
 * EL ACTO VALE EL DOBLE QUE EL DESTINO, y se puede medir: 85 px de alto contra
 * 42. `mailto:` y `tel:` disparan una aplicacion del aparato y siguen
 * sirviendo sin red; los externos abren una pestana y la necesitan. Cuatro
 * columnas iguales dirian que los cuatro son intercambiables, que es falso.
 *
 * El relleno con margen negativo agranda el blanco SIN mover el texto.
 */
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-bar[data-canal="acto"] {
  display: block;
  padding: 0.625rem 0.875rem 0.75rem;
  margin: -0.625rem -0.875rem -0.75rem;
}

:root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="acto"] .contacto-bar-value {
  display: block;
  font-size: var(--t-4);
  margin-top: 0.4375rem;
  letter-spacing: -0.005em;
}

:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-bar[data-canal="destino"] {
  display: flex;
  align-items: baseline;
  gap: 0.5625rem;
  padding: 0.5625rem 0.75rem;
  margin: -0.5625rem -0.75rem;
}

:root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="destino"] .contacto-bar-value {
  font-size: var(--t-2);
  letter-spacing: -0.005em;
}

:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-bar-label {
  font-family: var(--font-mono);
  font-size: 0.5625rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  opacity: var(--fundido-dim);
}

:root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="acto"] .contacto-bar-label {
  display: block;
}

/* La marca de la barra es de la carta de ajuste de Vice; aqui no pinta nada. */
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-bar-mark {
  display: none;
}

/*
 * EL ESTADO VA BAJO EL COLOFON, y en el DOM compartido vive DENTRO de
 * `.contacto-band`, encima de las barras. Quien lo mueve es
 * `caelestia.fundido.ts` al montar (Task 5), no `contacto.ts`: moverlo en el
 * marcado cambiaria el orden de lectura en los tres temas.
 *
 * Hasta que la Task 5 exista, este bloque lo pinta donde este. Es correcto que
 * en la captura de la Task 4 aparezca todavia bajo el titular.
 */
:root[data-theme="caelestia"] [data-scene="contacto"] .contacto-estado {
  margin: 1rem 0 0;
  display: flex;
  align-items: center;
  gap: 0.5625rem;
  font-family: var(--font-mono);
  font-size: 0.59375rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  opacity: var(--fundido-dim);
}

/* ---------- 390 px ----------
 * Un PASO distinto, no una funcion. El techo lo pone el ancho y esta medido:
 * `--t-9` deja «Cuentame» en 398 px sobre una medida util de 322 y se sale;
 * `--t-8` la deja en 299. La jerarquia de M4 se conserva; lo que cambia es que
 * en vertical los actos son FILAS ENTERAS — a 390 el ancho es el recurso
 * escaso, y un acto que ocupa todo el ancho es el blanco mas facil que hay.
 */
@media (max-width: 40rem) {
  :root[data-theme="caelestia"] [data-scene="contacto"] {
    padding: 1.25rem 1.25rem 1.125rem;
  }

  :root[data-theme="caelestia"] [data-scene="contacto"] .contacto-lead {
    font-size: var(--t-8);
  }

  /* En vertical los actos son FILAS ENTERAS y los destinos se reparten la
     ultima a mitades. `wrap` con los actos al 100% fuerza el corte de linea
     sin necesitar ningun envoltorio. */
  :root[data-theme="caelestia"] [data-scene="contacto"] .contacto-bars {
    flex-wrap: wrap;
    gap: 0.25rem 0.625rem;
  }

  :root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="acto"] {
    flex: 0 0 100%;
  }

  :root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="acto"] .contacto-bar-value {
    font-size: var(--t-3);
  }

  :root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="destino"] {
    flex: 1;
    margin-left: 0;
  }

  :root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="destino"]:nth-child(2) {
    margin-left: 0;
    margin-top: 0.625rem;
  }

  :root[data-theme="caelestia"] [data-scene="contacto"] [data-canal="destino"] + [data-canal="destino"] {
    margin-left: 0;
    margin-top: 0.625rem;
  }
}
```

- [ ] **Step 2: Construir y medir la jerarquía**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run lint && npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
FALLOS = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for w, h, tit in ((1440, 900, 159.66), (390, 844, 89.85)):
        pg = b.new_page(viewport={"width": w, "height": h}, is_mobile=(w == 390), has_touch=(w == 390))
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
        pg.wait_for_timeout(3000)
        pg.click('[data-cae-ws="contacto"]'); pg.wait_for_timeout(1400)
        d = pg.evaluate("""() => {
            const sc = document.querySelector('[data-scene="contacto"]');
            const f = s => parseFloat(getComputedStyle(sc.querySelector(s)).fontSize);
            const cajas = [...sc.querySelectorAll('a.contacto-bar')].map(a => {
                const r = a.getBoundingClientRect();
                return [a.dataset.canal, Math.round(r.width), Math.round(r.height)];
            });
            let der = 0;
            const paseo = document.createTreeWalker(sc, NodeFilter.SHOW_TEXT);
            for (let n = paseo.nextNode(); n; n = paseo.nextNode()) {
                if (!n.textContent.trim()) continue;
                const r = document.createRange(); r.selectNode(n);
                const c = r.getBoundingClientRect();
                if (c.width > 0) der = Math.max(der, c.right);
            }
            return { lead: f('.contacto-lead'), valor: f('[data-canal="acto"] .contacto-bar-value'),
                     cajas, der: Math.round(der),
                     scroll: [sc.scrollHeight, sc.clientHeight],
                     ancho: Math.round(sc.getBoundingClientRect().width) };
        }""")
        print(w, d, "errores:", errs or "ninguno")
        if abs(d["lead"] - tit) > 0.01: FALLOS.append(f"{w}: titular {d['lead']}, esperado {tit}")
        if d["lead"] <= d["valor"]: FALLOS.append(f"{w}: jerarquia invertida")
        if d["scroll"][0] != d["scroll"][1]: FALLOS.append(f"{w}: scroll interno {d['scroll']}")
        if any(c[1] < 24 or c[2] < 24 for c in d["cajas"]): FALLOS.append(f"{w}: blanco < 24 {d['cajas']}")
        if errs: FALLOS.append(f"{w}: {errs}")
        pg.screenshot(path=f"/tmp/b5-t4-{w}.png")
        pg.close()
    b.close()
print("FALLOS:", FALLOS or "ninguno")
assert not FALLOS
PY
```

Esperado: titular **159,66** a 1440 y **89,85** a 390, mayor que el valor del acto en los dos, sin
scroll interno, cero errores.

- [ ] **Step 3: Mirar las dos capturas**

Abrir `/tmp/b5-t4-1440.png` y `/tmp/b5-t4-390.png`. Los números pueden estar verdes con el
resultado roto: **hay que ver el campo de color, el titular grande y el colofón en dos grupos.**
Si a 390 la frase desborda por la derecha, el paso elegido no cabe — volver al spec, no bajar el
tamaño a ojo.

- [ ] **Step 4: Comprobar que Vice y Hyprland siguen intactos**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for tema in ("vice", "hyprland"):
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(f"http://localhost:4193/?theme={tema}#contacto", wait_until="domcontentloaded")
        pg.wait_for_timeout(3500)
        pg.eval_on_selector('[data-scene="contacto"]', "e => e.scrollIntoView()")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=f"/tmp/b5-t4-{tema}.png")
        print(tema, pg.evaluate("""() => {
            const sc = document.querySelector('[data-scene="contacto"]');
            return { titular: getComputedStyle(sc.querySelector('.contacto-title')).fontSize,
                     visible: getComputedStyle(sc.querySelector('.contacto-title')).position };
        }"""))
        pg.close()
    b.close()
PY
```

El titular de Vice y Hyprland **no puede estar en `position: absolute`**: la regla que lo oculta
lleva `[data-theme="caelestia"]` delante y solo debe aplicar ahí.

- [ ] **Step 5: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(fundido): el campo de color, la escala del cierre y el pie de imprenta

El titular pasa de 16 px a --t-10 (159,66) y deja de usar opsz 9. Los cuatro
canales dejan de ser una lista plana: dos actos grandes y dos destinos al
canto. --fundido-dim 0,82, calibrado contra --cae-primary (4,80:1 en el peor
de 288 pasos del dia)."
```

---

## Task 5: El troquel y el sprite, aislados

**Files:**
- Create: `src/themes/caelestia.dino.ts`
- Create: `src/themes/caelestia.fundido.ts`
- Modify: `src/themes/themes.css`

**Interfaces:**
- Consumes: `[data-scene="contacto"]` con el CSS de la Task 4.
- Produces:
  - `caelestia.dino.ts`: `export function svgDino(): string`, `export function svgNube(): string`,
    `export function svgHorizonte(tramo?: number): string`, `export const OJO_DINO: readonly [number, number, number, number]`.
  - `caelestia.fundido.ts`: `export interface FundidoHandle { destroy: () => void; reproducir: () => void; entrar: (desde: number) => void }`
    y `export function montarFundido(gsap: Gsap, escena: HTMLElement): FundidoHandle | null`.
    La Task 6 llama a `reproducir` y `entrar`; la Task 7 no toca esta interfaz.

- [ ] **Step 1: Escribir `caelestia.dino.ts` con los mapas y su cabecera legal**

Los mapas de bits salen de las maquetas rescatadas en la Task 1. **Ojo con de cuál**:

| constante | fichero |
|---|---|
| `QUIETO`, `NUBE`, `HORIZONTE` | `…-fundido-movimiento.html` (también están en `…-composicion.html`) |
| `CARRERA_1`, `CARRERA_2` | **solo** en `…-fundido-movimiento.html` |

Copiarlos verbatim de ahí — **no volver a extraerlos del PNG**. La extracción tiene dos pasos no
obvios (tapar el hueco del ojo solo en el fotograma de pie, y pegar los tres al mismo lienzo abajo
y a la derecha) y rehacerla es rehacer las dos trampas.

```ts
/**
 * El dino de Chrome, aislado en su propio fichero A PROPOSITO: quitarlo tiene
 * que ser borrar este fichero y una llamada, no una cirugia.
 *
 * PROCEDENCIA. Las piezas salen del sprite de la pagina de error de red de
 * Chromium:
 *   components/neterror/resources/images/default_100_percent/offline/
 *   100-offline-sprite.png   (1233 x 100)
 * Piezas usadas: dino de pie x=848, zancada 1 x=936, zancada 2 x=980,
 * nube x=86 (46x14), horizonte x=2 y=54 (600x12).
 *
 * LICENCIA Y MARCA. El codigo de Chromium es BSD-3-Clause. La MARCA no: el
 * dino es un activo identificable de un producto de Google, y usarlo en un
 * portfolio personal es un riesgo de marca, no de licencia. Es una decision
 * de Aoshi, tomada despues de que se le advirtiera dos veces durante el
 * maquetado de B5. Queda escrito aqui para que quien lo lea dentro de un ano
 * sepa que fue una eleccion y no un descuido.
 *
 * DOS TRAMPAS, YA PAGADAS:
 *   1. El hueco del ojo esta TAPADO en el fotograma de pie. Encima va un
 *      `rect` movible (el bicho te mira) y si se dejara el hueco original, el
 *      hueco y el rect se suman y el ojo se ve DOBLE en cuanto se mueve. En
 *      los de zancada NO se tapa: ahi no hay rect y el hueco ES el ojo.
 *   2. Los tres fotogramas van en el MISMO lienzo de 40x43, pegados abajo y a
 *      la derecha. Sus cajas no miden igual (las piernas se mueven) y sin
 *      igualarlas la cabeza pega un tiron lateral en cada zancada.
 */

/** El lienzo comun de los tres fotogramas. */
export const ANCHO_DINO = 40;
export const ALTO_DINO = 43;

/** El ojo del fotograma de pie: x, y, ancho, alto, en el lienzo comun. */
export const OJO_DINO = [24, 3, 2, 2] as const;

const QUIETO: readonly string[] = [
  // ... copiar las 43 filas de la maqueta, tal cual
];

const CARRERA_1: readonly string[] = [
  // ... 43 filas
];

const CARRERA_2: readonly string[] = [
  // ... 43 filas
];

const NUBE: readonly string[] = [
  // ... 13 filas de 46
];

const HORIZONTE: readonly string[] = [
  // ... 8 filas de 600
];

/** Una tira por corrida de pixeles encendidos: menos `rect` y bordes limpios. */
function tiras(mapa: readonly string[]): string {
  const ancho = mapa[0].length;
  let salida = "";
  for (let y = 0; y < mapa.length; y += 1) {
    let x = 0;
    while (x < ancho) {
      if (mapa[y][x] === "#") {
        let n = 1;
        while (x + n < ancho && mapa[y][x + n] === "#") n += 1;
        salida += `<rect x="${x}" y="${y}" width="${n}" height="1"/>`;
        x += n;
      } else {
        x += 1;
      }
    }
  }
  return salida;
}

export type Fotograma = "quieto" | "carrera1" | "carrera2";

const MAPAS: Record<Fotograma, readonly string[]> = {
  quieto: QUIETO,
  carrera1: CARRERA_1,
  carrera2: CARRERA_2,
};

/** Las tres corridas, calculadas una vez: la zancada cambia 12 veces al entrar. */
const DIBUJOS: Record<Fotograma, string> = {
  quieto: tiras(QUIETO),
  carrera1: tiras(CARRERA_1),
  carrera2: tiras(CARRERA_2),
};

export function dibujoDino(fotograma: Fotograma): string {
  return DIBUJOS[fotograma];
}

export function svgDino(): string {
  return (
    `<svg viewBox="0 0 ${ANCHO_DINO} ${ALTO_DINO}" shape-rendering="crispEdges" aria-hidden="true">` +
    `<g class="cae-dino-cuerpo" data-dino-cuerpo>${DIBUJOS.quieto}</g>` +
    `<rect class="cae-dino-ojo" data-dino-ojo x="${OJO_DINO[0]}" y="${OJO_DINO[1]}" ` +
    `width="${OJO_DINO[2]}" height="${OJO_DINO[3]}"/></svg>`
  );
}

export function svgNube(): string {
  return (
    `<svg viewBox="0 0 ${NUBE[0].length} ${NUBE.length}" shape-rendering="crispEdges" ` +
    `aria-hidden="true">${tiras(NUBE)}</svg>`
  );
}

/**
 * El horizonte, opcionalmente RECORTADO a un tramo central.
 *
 * El sprite mide 600 px de ancho. Metido entero en los 172 px del sello de
 * movil queda a escala 0,29 y la linea solida del suelo mide MENOS DE UN PIXEL
 * y no se pinta — el bicho parece flotar. Se ensena un tramo, que es casi
 * escala 1:1 y conserva el tamano de los guijarros. Estirarlo con
 * `preserveAspectRatio` los deformaria.
 */
export function svgHorizonte(tramo = HORIZONTE[0].length): string {
  const ancho = Math.min(tramo, HORIZONTE[0].length);
  const desde = Math.floor((HORIZONTE[0].length - ancho) / 2);
  return (
    `<svg viewBox="${desde} 0 ${ancho} ${HORIZONTE.length}" shape-rendering="crispEdges" ` +
    `aria-hidden="true">${tiras(HORIZONTE)}</svg>`
  );
}

/** Las lineas por fotograma, para que las pruebas puedan comprobarlas. */
export function alturaMapa(fotograma: Fotograma): number {
  return MAPAS[fotograma].length;
}
```

- [ ] **Step 2: Comprobar los invariantes del sprite sobre el propio fichero**

Antes de que nada lo pinte. Si un mapa está torcido, el bicho flota o se deforma, y en una captura
reducida no se ve.

```bash
npm run lint && npm run build
python3 - <<'FIN'
import re, sys, pathlib
src = pathlib.Path("src/themes/caelestia.dino.ts").read_text()
FALLOS = []

def mapa(nombre):
    m = re.search(rf"const {nombre}: readonly string\[\] = \[(.*?)\];", src, re.S)
    if not m:
        FALLOS.append(f"{nombre}: no encontrado")
        return []
    return re.findall(r'"([.#]*)"', m.group(1))

quieto, c1, c2 = mapa("QUIETO"), mapa("CARRERA_1"), mapa("CARRERA_2")
nube, horizonte = mapa("NUBE"), mapa("HORIZONTE")

for nombre, m in (("QUIETO", quieto), ("CARRERA_1", c1), ("CARRERA_2", c2)):
    if len(m) != 43:
        FALLOS.append(f"{nombre}: {len(m)} filas, esperadas 43")
    if {len(f) for f in m} != {40}:
        FALLOS.append(f"{nombre}: anchos {{len(f) for f in m}}, esperado 40")
    # Sin esto el bicho flota por encima del horizonte.
    if m and "#" not in m[-1]:
        FALLOS.append(f"{nombre}: la ultima fila esta vacia")

# El hueco del ojo se tapa SOLO en el de pie: encima va el rect movible.
if quieto and quieto[3][24] != "#":
    FALLOS.append("QUIETO: el hueco del ojo no esta tapado -- se veria doble al moverse")
if c1 and c1[3][24] != ".":
    FALLOS.append("CARRERA_1: el ojo esta tapado y ahi el hueco ES el ojo")
if c2 and c2[3][24] != ".":
    FALLOS.append("CARRERA_2: el ojo esta tapado y ahi el hueco ES el ojo")
if c1 and c2 and c1 == c2:
    FALLOS.append("los dos fotogramas de carrera son identicos")

# La cabeza tiene que estar en el mismo sitio en los tres, o cada zancada es
# un tiron lateral.
bordes = {n: len(m[3].rstrip(".")) for n, m in (("quieto", quieto), ("c1", c1), ("c2", c2)) if m}
if len(set(bordes.values())) != 1:
    FALLOS.append(f"la cabeza se mueve entre fotogramas: {bordes}")

if len(nube) != 13 or {len(f) for f in nube} != {46}:
    FALLOS.append(f"NUBE: {len(nube)} filas de {{len(f) for f in nube}}, esperadas 13 de 46")
if len(horizonte) != 8 or {len(f) for f in horizonte} != {600}:
    FALLOS.append(f"HORIZONTE: {len(horizonte)} filas, esperadas 8 de 600")

print("FALLOS:", FALLOS or "ninguno")
sys.exit(1 if FALLOS else 0)
FIN
```

Esperado: `ninguno`. **Si alguno falla, los mapas se copiaron mal** — volver a la maqueta, no
retocarlos a mano.

- [ ] **Step 3: Escribir `caelestia.fundido.ts` — el montaje, sin animación todavía**

```ts
import type { Gsap } from "./choreography";
import { OJO_DINO, svgDino, svgHorizonte, svgNube } from "./caelestia.dino";

/**
 * Lo unico de «Fundido» que el CSS no puede hacer: partir el titular en
 * lineas, montar el troquel con su bicho, y correr el fundido y la entrada.
 *
 * Vive aparte de `caelestia.choreography.ts` a proposito, igual que la ficha
 * de B2: la coreografia gobierna el carril y no tiene por que saber que hay
 * dentro de cada ventana. Aqui no se toca el carril.
 *
 * `gsap` llega SIEMPRE por parametro. Un `import gsap from "gsap"` compila,
 * pasa el linter y revienta en el navegador — le paso a Hyprland y su
 * coreografia no corrio durante semanas.
 */

/** El tramo de horizonte que se ensena dentro del sello de movil. */
const TRAMO_MOVIL = 200;
/** Por debajo de este ancho de ventana, el troquel es un sello entero. */
const ANCHO_SELLO = 640;

export interface FundidoHandle {
  destroy: () => void;
  /** El fundido completo. Suena UNA vez, la primera visita al workspace. */
  reproducir: () => void;
  /** La entrada corta. Suena en cada llegada. `desde` es el workspace de origen. */
  entrar: (desde: number) => void;
}

/** Parte el titular en una linea por renglon natural, para poder trazarlas. */
function partirEnLineas(lead: HTMLElement): HTMLElement[] {
  const texto = lead.textContent ?? "";
  if (!texto.trim()) return [];
  /*
   * Se parte por PALABRAS y se deja que el navegador decida los renglones: el
   * texto sale de `identity.invitation` y no se puede trocear a mano sin
   * inventar contenido. Cada palabra va en un `<span>` en linea; despues se
   * agrupan por su `offsetTop`, que es donde el navegador las ha puesto de
   * verdad.
   */
  lead.textContent = "";
  const palabras = texto.split(/\s+/).filter(Boolean);
  const marcas = palabras.map((palabra, i) => {
    const span = document.createElement("span");
    span.className = "cae-fundido-palabra";
    span.textContent = i === palabras.length - 1 ? palabra : `${palabra} `;
    lead.append(span);
    return span;
  });

  const porFila = new Map<number, HTMLElement[]>();
  for (const marca of marcas) {
    const fila = Math.round(marca.offsetTop);
    const lista = porFila.get(fila);
    if (lista) lista.push(marca);
    else porFila.set(fila, [marca]);
  }

  const lineas: HTMLElement[] = [];
  for (const [, grupo] of [...porFila.entries()].sort((a, b) => a[0] - b[0])) {
    const linea = document.createElement("span");
    linea.className = "cae-fundido-linea";
    linea.setAttribute("data-fundido-linea", "");
    grupo[0].before(linea);
    linea.append(...grupo);
    lineas.push(linea);
  }
  return lineas;
}

export function montarFundido(
  gsap: Gsap,
  escena: HTMLElement,
  // Lo usa `entrar` en la Task 6, para saber de que lado vienes. Se recibe
  // desde ya: cambiar la firma entre tareas es como se rompen los planes.
  indiceEscena: number,
): FundidoHandle | null {
  const lead = escena.querySelector<HTMLElement>("[data-fundido-lead]");
  const banda = escena.querySelector<HTMLElement>(".contacto-band");
  const barras = escena.querySelector<HTMLElement>(".contacto-bars");
  if (!lead || !banda || !barras) return null;

  // El troquel: una figura de Material 3 recortando el escritorio sobre el
  // campo de color. El `clip-path` lo pone el CSS; aqui solo va el contenido.
  const troquel = document.createElement("span");
  troquel.className = "cae-fundido-troquel";
  troquel.setAttribute("data-fundido-troquel", "");
  troquel.setAttribute("aria-hidden", "true");

  const nube = document.createElement("span");
  nube.className = "cae-fundido-nube";
  nube.innerHTML = svgNube();

  const suelo = document.createElement("span");
  suelo.className = "cae-fundido-suelo";
  suelo.setAttribute("data-fundido-suelo", "");

  const bicho = document.createElement("span");
  bicho.className = "cae-fundido-bicho";
  bicho.setAttribute("data-fundido-bicho", "");
  bicho.innerHTML = svgDino();

  troquel.append(nube, suelo, bicho);
  banda.append(troquel);

  /*
   * El estado baja bajo el colofon. En el DOM compartido vive dentro de
   * `.contacto-band` —encima de las barras— y la contraportada lo quiere
   * abajo, con el pie de imprenta. Se mueve AQUI y no en `contacto.ts`
   * porque moverlo en el marcado le cambiaria el orden de lectura a Vice y a
   * Hyprland, y Vice esta cerrado.
   */
  const estadoDom = escena.querySelector<HTMLElement>(".contacto-estado");
  if (estadoDom) barras.after(estadoDom);

  const lineas = partirEnLineas(lead);
  const actos = Array.from(escena.querySelectorAll<HTMLElement>('[data-canal="acto"]'));
  const destinos = Array.from(escena.querySelectorAll<HTMLElement>('[data-canal="destino"]'));
  const estado = estadoDom;
  const ojo = bicho.querySelector<SVGRectElement>("[data-dino-ojo]");
  const svgBicho = bicho.querySelector<SVGSVGElement>("svg");

  /** El horizonte se re-dibuja al cambiar de ancho: ver `svgHorizonte`. */
  const pintarSuelo = (): void => {
    suelo.innerHTML = svgHorizonte(window.innerWidth <= ANCHO_SELLO ? TRAMO_MOVIL : undefined);
  };
  pintarSuelo();
  window.addEventListener("resize", pintarSuelo);

  const aterrizado = (): void => {
    gsap.set([lead, ...lineas, ...actos, ...destinos, barras], { clearProps: "all" });
    if (estado) gsap.set(estado, { clearProps: "all" });
    if (svgBicho) gsap.set(svgBicho, { clearProps: "all" });
    if (ojo) ojo.setAttribute("x", String(OJO_DINO[0]));
  };
  aterrizado();

  return {
    destroy: () => window.removeEventListener("resize", pintarSuelo),
    // Las dos se implementan en la Task 6; aqui dejan la escena puesta para
    // que la composicion se pueda revisar sin movimiento.
    reproducir: aterrizado,
    entrar: () => aterrizado(),
  };
}
```

- [ ] **Step 4: Añadir el CSS del troquel**

En el bloque de `[data-scene="contacto"]` de la Task 4:

```css
/*
 * EL TROQUEL. Una figura de Material 3 recortando el escritorio sobre el campo
 * de color, como el hueco de una contraportada por el que se ve la guarda.
 *
 * La caja es CUADRADA obligatoriamente: un `polygon()` en % en una caja alta
 * no es una figura, es una mancha. Lo aprendio B2 con el retrato.
 */
:root[data-theme="caelestia"] .cae-fundido-troquel {
  position: absolute;
  right: -0.625rem;
  top: 50%;
  transform: translateY(-50%);
  width: 28.75rem;
  height: 28.75rem;
  z-index: 2;
  overflow: hidden;
  background: var(--cae-surface);
  /* La galleta: 12 lobulos, 24,9 px de relieve a 460. */
  clip-path: polygon(/* generado en la Task 6 desde armonica(12, -0.058, 0.012) */);
}

:root[data-theme="caelestia"] .cae-fundido-troquel::before {
  content: "";
  position: absolute;
  width: 150%;
  height: 150%;
  left: -25%;
  top: -30%;
  background:
    radial-gradient(circle at 40% 45%, var(--cae-wall-1) 0%, transparent 62%),
    radial-gradient(circle at 78% 76%, var(--cae-wall-2) 0%, transparent 58%);
}

:root[data-theme="caelestia"] .cae-fundido-nube,
:root[data-theme="caelestia"] .cae-fundido-suelo,
:root[data-theme="caelestia"] .cae-fundido-bicho {
  position: absolute;
  display: block;
}

:root[data-theme="caelestia"] .cae-fundido-nube {
  left: 17%;
  top: 18%;
  width: 7.75rem;
}

:root[data-theme="caelestia"] .cae-fundido-nube svg { width: 100%; height: auto; display: block; fill: var(--cae-outline); }
:root[data-theme="caelestia"] .cae-fundido-suelo { left: 6%; right: 6%; bottom: 30%; transform-origin: 0 50%; }
:root[data-theme="caelestia"] .cae-fundido-suelo svg { width: 100%; height: auto; display: block; fill: var(--cae-on-surface-variant); }
:root[data-theme="caelestia"] .cae-fundido-bicho { left: 50%; bottom: 30%; width: 13.125rem; margin-left: -6.5625rem; }
:root[data-theme="caelestia"] .cae-fundido-bicho svg { width: 100%; height: auto; display: block; }
:root[data-theme="caelestia"] .cae-dino-cuerpo { fill: var(--cae-on-surface); }
:root[data-theme="caelestia"] .cae-dino-ojo { fill: var(--cae-surface); transition: fill 0.3s; }

/* El titular partido en lineas: cada una es una caja propia para poder
   trazarla. `partirEnLineas` las crea leyendo donde las ha puesto el navegador,
   no partiendo el texto a mano. */
:root[data-theme="caelestia"] .cae-fundido-linea { display: block; }

/* ---------- 390 px: el sello ----------
 * Deja de sangrar y va ENTERO. Sangrar 208 px en una ventana de 362 se come
 * mas de la mitad y lo que queda no deja completar la figura: se lee como una
 * mancha, no como una forma recortada.
 *
 * Y la figura pierde lobulos al encoger. Una figura no se lee por su nombre:
 * se lee por la PROFUNDIDAD de su lobulo en pixeles. La galleta cae de 24,9 px
 * a 460 hasta 10,6 a 196. Aqui va el sol (8 lobulos): 20,6 px.
 */
@media (max-width: 40rem) {
  :root[data-theme="caelestia"] .cae-fundido-troquel {
    position: relative;
    right: auto;
    top: auto;
    transform: none;
    align-self: flex-end;
    width: 12.25rem;
    height: 12.25rem;
    clip-path: polygon(/* generado en la Task 6 desde armonica(8, 0.115, -0.02) */);
  }

  :root[data-theme="caelestia"] [data-scene="contacto"] .contacto-band {
    flex-direction: column;
    justify-content: center;
    gap: 1.75rem;
    align-items: stretch;
  }

  :root[data-theme="caelestia"] .cae-fundido-nube { left: 13%; top: 15%; width: 3.625rem; }
  :root[data-theme="caelestia"] .cae-fundido-suelo { left: 6%; right: 6%; bottom: 26%; }
  :root[data-theme="caelestia"] .cae-fundido-bicho { left: 50%; bottom: 26%; width: 5.75rem; margin-left: -2.875rem; }
}
```

- [ ] **Step 5: Montarlo temporalmente para poder verlo, y medir**

En `caelestia.choreography.ts`, junto a `montarFicha`, añadir de forma provisional (la Task 6 lo
deja definitivo):

```ts
  const indiceFundido = escenas.findIndex((escena) => escena.dataset.scene === "contacto");
  const fundido =
    indiceFundido >= 0 ? montarFundido(gsap, escenas[indiceFundido], indiceFundido) : null;
```

con su `import { montarFundido } from "./caelestia.fundido";`.

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run lint && npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
FALLOS = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for w, h, lado, lobulos in ((1440, 900, 460, 12), (390, 844, 196, 8)):
        pg = b.new_page(viewport={"width": w, "height": h}, is_mobile=(w == 390), has_touch=(w == 390))
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
        pg.wait_for_timeout(3000)
        pg.click('[data-cae-ws="contacto"]'); pg.wait_for_timeout(1400)
        d = pg.evaluate("""() => {
            const t = document.querySelector('[data-fundido-troquel]');
            const c = t.getBoundingClientRect();
            const clip = getComputedStyle(t).clipPath;
            const puntos = [...clip.matchAll(/([\\d.]+)%\\s+([\\d.]+)%/g)].map(m => [+m[1], +m[2]]);
            const rr = puntos.map(([x, y]) => Math.hypot(x - 50, y - 50));
            return {
              lado: [Math.round(c.width), Math.round(c.height)],
              puntos: puntos.length,
              hondo: puntos.length ? Math.round((Math.max(...rr) - Math.min(...rr)) / 50 * (c.width / 2) * 10) / 10 : 0,
              lineas: document.querySelectorAll('[data-fundido-linea]').length,
              bicho: !!document.querySelector('[data-fundido-bicho] svg'),
              suelo: document.querySelector('[data-fundido-suelo] svg').getAttribute('viewBox'),
              texto: document.querySelector('[data-fundido-lead]').textContent.trim(),
            };
        }""")
        print(w, d, "errores:", errs or "ninguno")
        if d["lado"][0] != d["lado"][1]: FALLOS.append(f"{w}: el troquel no es cuadrado {d['lado']}")
        if abs(d["lado"][0] - lado) > 2: FALLOS.append(f"{w}: lado {d['lado'][0]}, esperado {lado}")
        if d["puntos"] != 240: FALLOS.append(f"{w}: {d['puntos']} puntos, esperados 240")
        if d["hondo"] < 12: FALLOS.append(f"{w}: lobulo de {d['hondo']} px — por debajo de 12 es ruido")
        if d["lineas"] < 2: FALLOS.append(f"{w}: el titular no se partio ({d['lineas']} lineas)")
        if not d["bicho"]: FALLOS.append(f"{w}: no hay bicho")
        if d["texto"] != "Cuéntame tu idea.": FALLOS.append(f"{w}: el titular cambio: {d['texto']!r}")
        if errs: FALLOS.append(f"{w}: {errs}")
        pg.screenshot(path=f"/tmp/b5-t5-{w}.png")
        pg.close()
    b.close()
print("FALLOS:", FALLOS or "ninguno")
assert not FALLOS
PY
```

Esperado: troquel cuadrado de 460 (escritorio) y 196 (móvil), **240 puntos** en el `clip-path`,
lóbulo de 24,9 y 20,6 px, el titular partido en 2 líneas y **con el mismo texto de `content.ts`**,
el horizonte con `viewBox` recortado solo a 390.

- [ ] **Step 6: Mirar las capturas**

`/tmp/b5-t5-1440.png` y `/tmp/b5-t5-390.png`. El bicho tiene que **apoyarse en el horizonte**, no
flotar; el ojo tiene que verse **una vez**, no dos.

- [ ] **Step 7: Commit**

```bash
git add src/themes/caelestia.dino.ts src/themes/caelestia.fundido.ts \
        src/themes/caelestia.choreography.ts src/themes/themes.css
git commit -m "feat(fundido): el troquel de Material 3 con el dino de Chromium

El sprite va aislado en caelestia.dino.ts con su procedencia, su licencia y la
nota de marca: quitarlo es borrar un fichero y una llamada. El horizonte se
recorta a un tramo en movil -- entero, su linea medía menos de un pixel."
```

---

## Task 6: El fundido y la entrada

**Files:**
- Modify: `src/themes/caelestia.fundido.ts`
- Modify: `src/themes/caelestia.choreography.ts`
- Modify: `src/themes/themes.css` (los dos `clip-path`, generados aquí)

**Interfaces:**
- Consumes: `FundidoHandle` (Task 5).
- Produces: nada nuevo; completa `reproducir` y `entrar`.

- [ ] **Step 1: Generar los dos `clip-path` y pegarlos en el CSS**

```bash
python3 - <<'PY'
import math
N = 240
def armonica(n, a, s):
    rmax = max(1 + a*math.cos(n*t) + s*math.cos(2*n*t)
               for t in (i*2*math.pi/2000 for i in range(2000)))
    pts = []
    for i in range(N):
        t = i*2*math.pi/N
        r = (1 + a*math.cos(n*t) + s*math.cos(2*n*t)) / rmax
        pts.append((50 + 50*r*math.cos(t), 50 + 50*r*math.sin(t)))
    return pts
for nombre, pts in (("galleta n=12 (escritorio)", armonica(12, -0.058, 0.012)),
                    ("sol n=8 (movil)",           armonica(8, 0.115, -0.02))):
    rr = [math.hypot(x-50, y-50) for x, y in pts]
    print(f"/* {nombre} — {len(pts)} puntos, relieve {(max(rr)-min(rr))/50:.4f} del radio */")
    print("clip-path: polygon(" + ", ".join(f"{x:.2f}% {y:.2f}%" for x, y in pts) + ");\n")
PY
```

Pegar cada salida en el `clip-path` correspondiente de la Task 5, sustituyendo el comentario
marcador. **Los 240 puntos son obligatorios en los dos**: dos `polygon()` solo interpolan si tienen
el mismo número de vértices, y con recuentos distintos el navegador hace un corte seco sin avisar.

- [ ] **Step 2: Escribir el fundido**

En `caelestia.fundido.ts`, sustituir el `return` del final:

```ts
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /*
   * Cuanto tiene que crecer el campo para tapar la ventana. NO es un numero a
   * ojo: es la distancia del centro de la figura a la esquina mas lejana,
   * dividida entre el radio MINIMO de la figura — los VALLES, no las crestas —
   * con un 4% de margen. Con el radio maximo se queda corto y el escritorio
   * asoma por una esquina.
   */
  const factorCrecimiento = (): number => {
    const v = escena.getBoundingClientRect();
    const c = troquel.getBoundingClientRect();
    const cx = c.left + c.width / 2 - v.left;
    const cy = c.top + c.height / 2 - v.top;
    const lejos = Math.max(
      Math.hypot(cx, cy),
      Math.hypot(v.width - cx, cy),
      Math.hypot(cx, v.height - cy),
      Math.hypot(v.width - cx, v.height - cy),
    );
    const clip = window.getComputedStyle(troquel).clipPath;
    const puntos = [...clip.matchAll(/([\d.]+)%\s+([\d.]+)%/g)];
    if (puntos.length === 0) return 1;
    const radios = puntos.map((m) => Math.hypot(Number(m[1]) - 50, Number(m[2]) - 50));
    const rMin = (Math.min(...radios) / 50) * (c.width / 2);
    return rMin > 0 ? (lejos / rMin) * 1.04 : 1;
  };

  // El campo de color: la MISMA figura que el troquel, en la misma posicion,
  // pintada en `--cae-primary`. Un solo mecanismo en dos direcciones — es un
  // iris de cine, no dos efectos sueltos.
  const campo = document.createElement("span");
  campo.className = "cae-fundido-campo";
  campo.setAttribute("aria-hidden", "true");
  banda.append(campo);

  const linea = (): ReturnType<Gsap["timeline"]> => {
    const crece = factorCrecimiento();
    const tl = gsap.timeline();
    tl.fromTo(campo, { scale: 1 }, { scale: crece, duration: 0.48, ease: "power2.inOut" }, 0);
    tl.fromTo(troquel, { scale: 0 }, { scale: 1, duration: 0.52, ease: "power3.out" }, 0.38);
    // Todo lo que aparece se traza de izquierda a derecha: un gesto repetido,
    // no tres maneras distintas de aparecer.
    tl.fromTo(
      lineas,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.62, ease: "power2.inOut", stagger: 0.12 },
      0.52,
    );
    // La frase se ABLANDA al llegar: entra con la voz de cabecera y aterriza en
    // la de cierre. `opsz` no se toca: se lee a 159,66 px de principio a fin.
    const ejes = { wght: 900, soft: 0 };
    tl.fromTo(
      ejes,
      { wght: 900, soft: 0 },
      {
        wght: 300,
        soft: 100,
        duration: 0.78,
        ease: "power2.out",
        onUpdate: () => {
          lead.style.fontVariationSettings =
            `"opsz" 144, "wght" ${Math.round(ejes.wght)}, "SOFT" ${Math.round(ejes.soft)}, "WONK" 1`;
        },
        onComplete: () => {
          // Se QUITA el valor en linea en vez de repetir el numero: un numero
          // repetido es un numero que se desincroniza del token.
          lead.style.fontVariationSettings = "";
        },
      },
      0.52,
    );
    tl.fromTo(suelo, { scaleX: 0 }, { scaleX: 1, duration: 0.34, ease: "power2.inOut" }, 0.74);
    if (svgBicho) {
      // Entra CORRIENDO: el idioma del propio bicho. La zancada es finita, solo
      // mientras entra, asi que no infringe la prohibicion de animacion
      // infinita en la escena de cierre.
      tl.fromTo(
        bicho,
        { x: -280 },
        {
          x: 0,
          duration: 0.66,
          ease: "power2.out",
          onStart: () => arrancarZancada(),
          onComplete: () => pararZancada(),
        },
        0.8,
      );
      tl.to(svgBicho, { scaleY: 0.9, scaleX: 1.07, duration: 0.07, transformOrigin: "50% 100%" }, 1.46);
      tl.to(svgBicho, { scaleY: 1, scaleX: 1, duration: 0.16, ease: "power2.out" }, 1.53);
    }
    tl.fromTo(nube, { opacity: 0, x: 26 }, { opacity: 1, x: 0, duration: 0.28, ease: "power2.out" }, 1.55);
    tl.fromTo(
      barras,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.42, ease: "power2.inOut" },
      0.82,
    );
    // La escalonada DICE algo: los actos antes que los destinos, que es la
    // jerarquia de la escena. Si se cambia esa jerarquia, esto se cae con ella.
    tl.fromTo(
      actos,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.46, ease: "power2.inOut", stagger: 0.1 },
      0.9,
    );
    tl.fromTo(
      destinos,
      { clipPath: "inset(-12% 100% -12% -2%)" },
      { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.42, ease: "power2.inOut", stagger: 0.09 },
      1.16,
    );
    if (estado) {
      tl.fromTo(
        estado,
        { clipPath: "inset(-12% 100% -12% -2%)" },
        { clipPath: "inset(-12% -6% -12% -2%)", duration: 0.34, ease: "power2.inOut" },
        1.3,
      );
    }
    return tl;
  };
```

Y la zancada, sobre el ticker de GSAP, encima del `return`:

```ts
  /*
   * La zancada la lleva un reloj propio y no la linea de tiempo: son doce
   * cambios de fotograma y meterlos como tweens ensuciaria la partitura sin
   * aportar nada. Se enciende y se apaga desde el tween del desplazamiento,
   * asi que sigue atado a el.
   */
  const ZANCADA = 0.085;
  let corriendo = false;
  let paso = 0;
  let ultimo = 0;

  const ponFotograma = (cual: Fotograma): void => {
    const cuerpo = bicho.querySelector<SVGGElement>("[data-dino-cuerpo]");
    if (cuerpo) cuerpo.innerHTML = dibujoDino(cual);
    // El ojo movible SOLO existe de pie: en los de zancada el ojo es el hueco
    // del propio sprite, y con el rect encima se veria doble.
    if (ojo) ojo.style.opacity = cual === "quieto" ? "1" : "0";
  };

  const tic = (): void => {
    if (!corriendo) return;
    const ahora = performance.now() / 1000;
    if (ahora - ultimo < ZANCADA) return;
    ultimo = ahora;
    paso ^= 1;
    ponFotograma(paso ? "carrera1" : "carrera2");
  };
  gsap.ticker.add(tic);

  const arrancarZancada = (): void => {
    paso = 0;
    ultimo = 0;
    corriendo = true;
  };
  const pararZancada = (): void => {
    corriendo = false;
    ponFotograma("quieto");
  };
```

Ampliar el `import` de `caelestia.dino` con `dibujoDino` y el tipo `Fotograma`, y el `destroy` con
`gsap.ticker.remove(tic)`.

- [ ] **Step 3: Escribir la entrada**

```ts
  /*
   * LA ENTRADA. El carril de la fase A ya desliza 520 ms; esto son 440 y cabe
   * dentro, asi que no anade espera: la rellena. No es un fundido acortado —
   * un final que suena cada vez no es un final.
   */
  const ENTRADA_MS = 440;
  let tlEntrada: ReturnType<Gsap["timeline"]> | null = null;

  const entrar = (desde: number): void => {
    if (tlEntrada) tlEntrada.kill();
    aterrizado();
    if (reduce) return;
    // Vienes de un workspace menor => el contenido se queda atras hacia la
    // derecha y alcanza; y el bicho mira hacia donde estabas.
    const sentido = desde < indiceEscena ? 1 : -1;
    tlEntrada = gsap.timeline();
    tlEntrada.fromTo(escena, { x: 28 * sentido }, { x: 0, duration: 0.38, ease: "power2.out" }, 0);
    tlEntrada.fromTo(troquel, { scale: 0.965 }, { scale: 1, duration: 0.26, ease: "power2.out" }, 0.12);
    if (ojo) {
      tlEntrada.call(() => ojo.setAttribute("x", String(OJO_DINO[0] - sentido)), undefined, 0.22);
      tlEntrada.call(() => ojo.setAttribute("x", String(OJO_DINO[0])), undefined, 0.36);
      // El parpadeo: el ojo es un hueco TAPADO, asi que apagar el rect no lo
      // borra — lo cierra, porque debajo queda el cuerpo.
      tlEntrada.to(ojo, { opacity: 0, duration: 0.001 }, 0.3);
      tlEntrada.to(ojo, { opacity: 1, duration: 0.001 }, 0.41);
    }
  };
```

`indiceEscena` ya llega como tercer parámetro desde la Task 5.

Y el `reproducir` definitivo:

```ts
    reproducir: () => {
      aterrizado();
      if (reduce) return;      // No es una version corta: es ninguna version.
      linea().play(0);
    },
```

- [ ] **Step 4: Cablearlo en la coreografía con la regla de B2**

En `caelestia.choreography.ts`, dentro de `irA`, junto a la línea de la ficha:

```ts
    /*
     * EL FUNDIDO SUENA UNA VEZ; LA ENTRADA, TODAS. Es la misma regla que ya
     * gobierna la ficha de B2 dos lineas mas arriba: no vuelves a abrir la
     * aplicacion en la que ya estas. Un final de 1,9 s reproducido en la
     * quinta visita deja de ser un final y pasa a ser un peaje.
     */
    if (fundido && destino === indiceFundido && destino !== origen) {
      if (fundidoVisto) fundido.entrar(origen);
      else {
        fundido.reproducir();
        fundidoVisto = true;
      }
    }
```

con `let fundidoVisto = false;` junto a `let actual = 0;`.

- [ ] **Step 5: Medir la línea de tiempo parándola en instantes exactos**

Una captura no distingue una animación que corre de una que ya aterrizó.

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run lint && npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
FALLOS = []
LEE = """() => {
  const sc = document.querySelector('[data-scene="contacto"]');
  const cs = s => getComputedStyle(sc.querySelector(s));
  const esc = s => {
    const t = cs(s).transform;
    if (t === 'none') return 1;
    return Math.round(parseFloat(t.match(/matrix\\(([^,]+)/)[1]) * 1000) / 1000;
  };
  const oculto = s => {
    const c = cs(s).clipPath;
    const n = c && c.match(/inset\\(([^)]*)\\)/);
    if (!n) return 0;
    const p = n[1].trim().split(/\\s+/).map(v => parseFloat(v) || 0);
    return Math.max(0, ...p.map(v => v / 100));
  };
  return { campo: esc('.cae-fundido-campo'), troquel: esc('[data-fundido-troquel]'),
           frase: oculto('[data-fundido-linea]'), acto: oculto('[data-canal="acto"]'),
           destino: oculto('[data-canal="destino"]'),
           ejes: cs('[data-fundido-lead]').fontVariationSettings };
}"""
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
    pg.wait_for_timeout(3000)
    pg.click('[data-cae-ws="contacto"]')
    pg.wait_for_timeout(120)
    pronto = pg.evaluate(LEE)
    pg.wait_for_timeout(3000)
    fin = pg.evaluate(LEE)
    print("pronto:", pronto); print("fin:", fin)
    if pronto["troquel"] > 0.2: FALLOS.append(f"al arrancar el troquel ya esta abierto: {pronto['troquel']}")
    if pronto["frase"] < 0.5: FALLOS.append(f"al arrancar la frase ya se ve: {pronto['frase']}")
    if abs(fin["troquel"] - 1) > 0.02: FALLOS.append(f"el troquel no aterriza: {fin['troquel']}")
    if fin["frase"] > 0.02 or fin["acto"] > 0.02 or fin["destino"] > 0.02:
        FALLOS.append(f"el texto no aterriza: {fin}")
    if "300" not in fin["ejes"] or "100" not in fin["ejes"]:
        FALLOS.append(f"los ejes no aterrizan en la voz de cierre: {fin['ejes']}")
    # La segunda visita NO repite el fundido.
    pg.click('[data-cae-ws="creditos"]'); pg.wait_for_timeout(1200)
    pg.click('[data-cae-ws="contacto"]'); pg.wait_for_timeout(150)
    segunda = pg.evaluate(LEE)
    if segunda["frase"] > 0.5:
        FALLOS.append(f"la segunda visita repite el fundido: frase oculta {segunda['frase']}")
    if errs: FALLOS.append(str(errs))
    b.close()
print("FALLOS:", FALLOS or "ninguno")
assert not FALLOS
PY
```

- [ ] **Step 6: Ver el gate del crecimiento dar rojo antes de aceptarlo**

Cambiar temporalmente el `* 1.04` de `factorCrecimiento` por `* 0.80`, reconstruir, y comprobar que
al terminar el fundido **el escritorio asoma por una esquina de la escena**:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
    pg.wait_for_timeout(3000)
    pg.click('[data-cae-ws="contacto"]'); pg.wait_for_timeout(3000)
    print(pg.evaluate("""() => {
      const sc = document.querySelector('[data-scene="contacto"]');
      const c = sc.getBoundingClientRect(); const d = 26;
      return [[c.left+d,c.top+d],[c.right-d,c.top+d],[c.left+d,c.bottom-d],[c.right-d,c.bottom-d]]
        .map(([x,y]) => { const e = document.elementFromPoint(x,y);
          return e ? (e.className.baseVal ?? e.className ?? e.tagName).toString().slice(0,30) : 'nada'; });
    }"""))
    b.close()
PY
```

Con `0.80` alguna esquina **no** puede ser `cae-fundido-campo`. Restaurar `1.04` y volver a
ejecutar: las cuatro tienen que serlo. **Si con 0,80 sale verde, el gate no vale.**

- [ ] **Step 7: Commit**

```bash
git add src/themes/caelestia.fundido.ts src/themes/caelestia.choreography.ts src/themes/themes.css
git commit -m "feat(fundido): el fundido de 1900 ms y la entrada de 440

Un solo mecanismo en dos direcciones: la misma figura inunda la ventana y
despues nace dentro de si misma. El fundido suena una vez -- la regla que B2
ya dejo escrita; la entrada, todas, y cabe dentro de los 520 del carril.
Visto en rojo con el factor de crecimiento a 0,80."
```

---

## Task 7: Movimiento reducido

**Files:**
- Modify: `src/themes/themes.css`
- Modify: `src/themes/caelestia.fundido.ts` (ya lo contempla; aquí se verifica)

- [ ] **Step 1: Añadir la guarda de CSS, con sus pseudo-elementos nombrados**

```css
/*
 * Bajo `prefers-reduced-motion` la escena queda ATERRIZADA, no en una version
 * corta: es ninguna version. El JS ya no monta ninguna linea de tiempo; esto
 * solo apaga lo que anima el CSS.
 *
 * EL SELECTOR UNIVERSAL `*` NO ALCANZA A LOS PSEUDO-ELEMENTOS. Se pago en B2
 * con `.ficha-k::before`, que siguio animando bajo la guarda generica. Cada
 * pseudo-elemento que anime va nombrado aqui, uno por uno.
 */
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] .cae-dino-ojo {
    transition: none;
  }

  :root[data-theme="caelestia"] .cae-fundido-troquel::before {
    transition: none;
    animation: none;
  }
}
```

- [ ] **Step 2: Comprobar que la escena queda puesta y en 0 ms**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
FALLOS = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    pg = ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
    pg.wait_for_timeout(3000)
    pg.click('[data-cae-ws="contacto"]')
    pg.wait_for_timeout(200)   # 200 ms: si algo anima, aqui esta a medias
    d = pg.evaluate("""() => {
      const sc = document.querySelector('[data-scene="contacto"]');
      const cs = s => getComputedStyle(sc.querySelector(s));
      const oculto = s => { const c = cs(s).clipPath;
        const n = c && c.match(/inset\\(([^)]*)\\)/);
        if (!n) return 0;
        return Math.max(0, ...n[1].trim().split(/\\s+/).map(v => (parseFloat(v)||0)/100)); };
      const esc = s => { const t = cs(s).transform;
        return t === 'none' ? 1 : Math.round(parseFloat(t.match(/matrix\\(([^,]+)/)[1])*1000)/1000; };
      return { frase: oculto('[data-fundido-linea]'), acto: oculto('[data-canal="acto"]'),
               troquel: esc('[data-fundido-troquel]'),
               ojo: cs('[data-dino-ojo]').transitionDuration };
    }""")
    print(d, "errores:", errs or "ninguno")
    if d["frase"] > 0.02 or d["acto"] > 0.02: FALLOS.append(f"no esta aterrizado: {d}")
    if abs(d["troquel"] - 1) > 0.02: FALLOS.append(f"el troquel no esta puesto: {d['troquel']}")
    if d["ojo"] not in ("0s", "0"): FALLOS.append(f"el ojo sigue con transicion: {d['ojo']}")
    pg.screenshot(path="/tmp/b5-t7-reduce.png")
    b.close()
print("FALLOS:", FALLOS or "ninguno")
assert not FALLOS
PY
```

- [ ] **Step 3: Ver el gate dar rojo**

Comentar temporalmente el `if (reduce) return;` de `reproducir`, reconstruir y volver a ejecutar el
paso 2. **Tiene que fallar** con `no esta aterrizado`. Restaurar y volver a verde.

- [ ] **Step 4: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(fundido): guarda de prefers-reduced-motion con sus pseudo-elementos

El selector universal * no alcanza a ::before -- se pago en B2 con
.ficha-k::before. Aqui van nombrados uno por uno. Visto en rojo quitando el
return temprano de reproducir()."
```

---

## Task 8: El arnés

**Files:**
- Create: `scripts/measure-caelestia-fundido.py`
- Modify: `CLAUDE.md` (raíz del proyecto)

- [ ] **Step 1: Escribir el arnés con los doce gates del spec**

Sigue el patrón de `scripts/measure-caelestia-quien-soy.py`: `argparse` con `--base`, la función
`comprobar(condicion, etiqueta)`, un bloque `print` por familia y `sys.exit(main())`. Los doce gates
están enumerados en el spec, sección `## Los gates`; cada uno con el numérico exacto que aparece
allí. Reutilizar los fragmentos de medición ya escritos en las Tasks 4, 5, 6 y 7 — **no volver a
inventarlos**.

Los dos que hay que escribir con cuidado, porque son los que pueden pasar en falso:

```python
    # Gate 7 · contraste: SOLO LOS PARES QUE SE PINTAN DE VERDAD.
    #
    # Vigilar los roles `on-X` contra `X` en abstracto es lo que dejo al reloj
    # de la fase A bajo AA cuatro horas al dia con el arnes en verde. Y dos
    # pares que NO se miden, a proposito:
    #   · las nubes (2,19:1) son decorado, y WCAG exime el decorado;
    #   · el ojo de dia NO EXISTE — de dia el ojo es el hueco, en
    #     `--cae-surface`, no en `--cae-anchor`. Medirlo es medir un par que
    #     nunca se pinta.
    PARES = [
        ("la frase", ".contacto-lead", '[data-scene="contacto"]'),
        ("valor del acto", '[data-canal="acto"] .contacto-bar-value', '[data-scene="contacto"]'),
        ("rotulo del acto", '[data-canal="acto"] .contacto-bar-label', '[data-scene="contacto"]'),
        ("el estado", ".contacto-estado", '[data-scene="contacto"]'),
    ]
```

```python
    # Gate 6 · el dato se lee SIN hover.
    #
    # No se simula nada: un MouseEvent sintetico NO dispara `:hover`, asi que
    # una prueba que lo simule mide su propia simulacion. Se lee y ya.
    visibles = pagina.evaluate("""() => [...document.querySelectorAll(
        '[data-scene="contacto"] .contacto-bar-value')].filter(v => {
            const cs = getComputedStyle(v);
            return v.textContent.trim().length > 0 && cs.visibility !== 'hidden'
                && cs.display !== 'none' && parseFloat(cs.opacity) > 0.05;
        }).length""")
    comprobar(visibles == 4, f"los cuatro datos se leen sin hover ({visibles}/4)")
```

- [ ] **Step 2: Ejecutarlo contra el build**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 scripts/measure-caelestia-fundido.py --base http://localhost:4193
```

Esperado: `TODO VERDE`.

- [ ] **Step 3: Comprobar que los arneses de las fases anteriores siguen verdes**

```bash
python3 scripts/measure-caelestia-hora.py --base http://localhost:4193
python3 scripts/measure-caelestia-titulo.py --base http://localhost:4193
python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4193
python3 scripts/measure-caelestia-obra.py --base http://localhost:4193
```

Los cuatro tienen que seguir verdes. **Si alguno cae, B5 ha roto una fase cerrada** — arreglarlo
antes de seguir, no anotarlo como deuda.

- [ ] **Step 4: Ver rojo cada gate nuevo**

Para cada uno de los doce, introducir el fallo exacto que dice cazar, ejecutar el arnés y anotar el
mensaje rojo en una tabla. Los cuatro sabotajes ya ejecutados durante el maquetado están en el spec
(`## Ninguno se acepta sin haberlo visto dar rojo`) y valen como referencia; **los otros ocho hay que
hacerlos aquí**. Ejemplos:

| gate | sabotaje |
|---|---|
| 1 · jerarquía | poner `font-size: var(--t-2)` en `.contacto-lead` |
| 2 · ejes | cambiar `--cae-display-axes-cierre` por `--cae-display-axes` |
| 3 · ocupación | poner `max-width: 20rem` en `.contacto-lead` |
| 4 · sin scroll | poner `height: 200%` en `.contacto-bars` |
| 5 · `tel:`/`rel` | quitar el `rel` de un externo en `contacto.ts` |
| 6 · sin hover | poner `opacity: 0` en `.contacto-bar-value` y `1` en `:hover` |
| 11 · 390 | poner `font-size: var(--t-10)` también en el `@media` |
| 12 · Vice/Hyprland | quitar el `[data-theme="caelestia"]` de la regla del campo de color |

- [ ] **Step 5: Actualizar `CLAUDE.md`**

Añadir el párrafo de B5 a la sección `## Theme Status`, con los números del spec, y actualizar el
estado general de Caelestia. **Ojo:** ese fichero todavía no menciona B3 ni B4 — anotarlo como
pendiente, no inventar su texto.

- [ ] **Step 6: Commit**

```bash
git add scripts/measure-caelestia-fundido.py CLAUDE.md
git commit -m "test(fundido): el arnes de B5, doce gates vistos en rojo

Dos pares NO se miden a proposito: las nubes son decorado (WCAG las exime) y
el ojo de dia es un par que nunca se pinta. Los cuatro arneses de las fases
anteriores siguen verdes."
```

---

## Task 9: Cierre — build, capturas y gates de crítica

- [ ] **Step 1: Build limpio y lint**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run lint && npm run build
```

- [ ] **Step 2: Capturas reales, las cinco escenas y los tres temas**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
# El `vite preview` de ESTE worktree ya corre en 4193 y sirve `dist/` desde
# disco, asi que recoge el build nuevo sin reiniciar nada. NO uses 4173: ahi
# corre otra sesion sirviendo OTRO repositorio, y medir contra ella da verde
# contra codigo que no es tuyo. La huella del bundle lo comprueba.
ASSET=$(grep -o 'assets/index-[A-Za-z0-9_-]*\.js' dist/index.html | head -1)
curl -s http://localhost:4193/ | grep -q "$ASSET" \
  || { echo "PELIGRO: el puerto 4193 no sirve este worktree (espero $ASSET)"; exit 1; }
python3 - <<'PY'
from playwright.sync_api import sync_playwright
ESCENAS = ["hero", "quien-es", "obra", "creditos", "contacto"]
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for w, h in ((1440, 900), (390, 844)):
        pg = b.new_page(viewport={"width": w, "height": h}, is_mobile=(w == 390), has_touch=(w == 390))
        pg.goto("http://localhost:4193/?theme=caelestia", wait_until="domcontentloaded")
        pg.wait_for_timeout(3000)
        for e in ESCENAS:
            pg.click(f'[data-cae-ws="{e}"]'); pg.wait_for_timeout(2600)
            pg.screenshot(path=f"/tmp/b5-final-{w}-{e}.png")
        pg.close()
    for tema in ("vice", "hyprland"):
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(f"http://localhost:4193/?theme={tema}#contacto", wait_until="domcontentloaded")
        pg.wait_for_timeout(3500)
        pg.eval_on_selector('[data-scene="contacto"]', "e => e.scrollIntoView()")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=f"/tmp/b5-final-{tema}.png")
        pg.close()
    b.close()
PY
```

**Mirar las doce capturas.** Los números pueden estar verdes con el resultado roto: es la lección
que este repo ha pagado más veces.

- [ ] **Step 3: Gates de crítica**

Lanzar `lidia-naive-tester` y `vera-art-director` sobre la escena, **con `model: sonnet` pinado** y
prohibiéndoles explícitamente editar producción. Registrar sus veredictos en el spec, en una sección
`## Gates de critica`, igual que hicieron B1 y la fase A — incluido un BLOCK aceptado, si lo hay,
con el motivo de la aceptación.

- [ ] **Step 4: Actualizar el estado del spec**

Cambiar `Estado: disenado, sin implementar` por `Estado: hecho`, y rellenar el `Registro de
implementación` con lo que rompió cada gate y con lo que se descubrió al implementar.

- [ ] **Step 5: Commit final**

```bash
git add docs/superpowers/specs/2026-09-04-caelestia-fundido-design.md
git commit -m "docs(fundido): registro de implementacion y gates de critica de B5"
```

---

## Autorrevisión de este plan

**Cobertura del spec.** Cada sección tiene tarea: `Por que` → Tasks 2 y 4; la tesis y la composición
→ Task 4; la escala y los tokens → Tasks 3 y 4; los cuatro canales → Tasks 2 y 4; el troquel y el
sprite → Task 5; el fundido → Task 6; la entrada → Task 6; color y contraste → Task 8 (gate 7) con
`--fundido-dim` puesto en la Task 4; móvil → Tasks 4 y 5 con su gate en la 8; movimiento reducido →
Task 7; los doce gates → Task 8; el rescate de las maquetas → Task 1.

**Lo que este plan NO hace, y el spec deja abierto.** Las cinco preguntas abiertas del spec:

1. **`.claude/rules/verification.md` no existe.** Este plan **no lo crea**: registra el arnés en
   `CLAUDE.md` (Task 8, paso 5), que es donde están registrados los demás. Si Aoshi quiere la tabla,
   es una tarea aparte.
2. **Conflictos en `themes.css` con B4.** No se resuelven aquí: B5 escribe en un bloque nuevo al
   final del suyo, y la fusión se hace cuando B4 aterrice.
3. **`display-xl` bajo Caelestia.** Resuelto por la vía limpia: la Task 4 oculta `.contacto-title`
   solo bajo Caelestia y no toca la clase en `contacto.ts`.
4. **Dónde vive el sprite.** Resuelto: `src/themes/caelestia.dino.ts`, como SVG generado.
5. **`--cae-display-axes-texto`.** Entra en B5, en su propia tarea, con comparación de capturas.

**Nombres, comprobados entre tareas.** `[data-canal="acto"|"destino"]` y `[data-fundido-lead]`
(Task 2) los consumen las Tasks 4, 5 y 6; **no hay envoltorios**, el agrupamiento es CSS.
`[data-fundido-troquel]`, `[data-fundido-suelo]`, `[data-fundido-bicho]`, `[data-fundido-linea]`,
`[data-dino-ojo]`, `[data-dino-cuerpo]`, `.cae-fundido-campo` (Task 5) los consumen las Tasks 6, 7 y
8. `montarFundido(gsap, escena, indice)` y `FundidoHandle { destroy, reproducir, entrar }` (Task 5)
los consume la Task 6. `svgDino`, `svgNube`, `svgHorizonte`, `dibujoDino`, `OJO_DINO`, `Fotograma`
(Task 5, `caelestia.dino.ts`) los consumen `caelestia.fundido.ts` en las Tasks 5 y 6.

**Un hueco conocido, dicho en voz alta.** La Task 5, paso 1, dice «copiar los mapas verbatim de la
maqueta» en vez de traer las 43 × 3 + 13 + 8 filas aquí. Es deliberado: son 150 líneas de arte de
bits que ya están en el repo tras la Task 1, y copiarlas a mano en el plan **añade una oportunidad
de equivocarse sin añadir información**. El fichero de origen y las constantes están nombrados
exactamente, y los invariantes (40 × 43, ojo tapado en (24,3), los tres fotogramas del mismo tamaño)
se comprueban en el paso 5.
