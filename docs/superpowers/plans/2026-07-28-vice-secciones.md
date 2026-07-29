# Remodelación de cuatro secciones de Vice City — Plan de implementación

> **Tracking: historico.** Las casillas de este plan nunca se marcaron durante la
> ejecucion, y no se marcan ahora en bloque: ticar 57 pasos que nadie siguio uno a
> uno seria falsificar el registro, no completarlo. El trabajo esta hecho y vive en
> `main` — la prueba es el codigo y los commits, no este fichero.
>
> Esta marca existe para que `scripts/verify.py::check_spec_plan_consistency` sepa
> distinguir "no se siguio" de "esta a medias". En los planes nuevos se marca al
> completar cada paso, como pide `.claude/rules/speckit-progress-tracking.md`.


> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corregir los cuatro defectos visuales que el usuario detectó en el tema Vice City (cuadro borroso del hero, salida de golpe al scrollear, "Quién es" a medio llenar, obra y créditos con medio lienzo vacío) y actualizar el contenido desfasado, sin romper Hyprland ni Caelestia.

**Architecture:** Un solo DOM semántico sirve a los tres temas; la presentación la decide el CSS bajo `[data-theme]`. Ninguna tarea ramifica el marcado por tema desde TypeScript. Las coreografías propias de Vice viven en `src/themes/vice.choreography.ts`; los otros dos temas siguen con las recetas genéricas de `src/utils/reveal.ts`.

**Tech Stack:** Vite 8 · TypeScript ~6 (strict) · Tailwind 4 · GSAP + ScrollTrigger · Lenis · Playwright (arnés en `scripts/verify.py`)

Spec: `docs/superpowers/specs/2026-07-28-vice-secciones-design.md`
Bitácora del rediseño anterior: `docs/superpowers/notes/2026-07-28-vice-city-bitacora.md`

## Global Constraints

- **Node 22 obligatorio.** `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"` antes de cualquier comando npm. Con Node 18 el build de Vite 8 falla.
- **Cero `any`.** `strict` está activo. Usar `unknown` + type guards.
- **Cero emojis** en código, documentación y mensajes de commit.
- **Cero colores escritos a mano en CSS.** Siempre `var(--color-*)` o `color-mix()` sobre un token. Esta regla ya rompió el contraste de `.hero-corner` una vez (1.09:1 en Caelestia).
- **Nunca ramificar el marcado por tema desde TypeScript.** Un solo DOM; el CSS bajo `[data-theme]` decide.
- **Limpieza GSAP obligatoria.** Cada gesto mata sus ScrollTrigger por id (`ScrollTrigger.getById(ID)?.kill()`) al principio de la función; las timelines sin `scrollTrigger` se guardan a nivel de módulo y se matan a mano.
- **Guards de `prefers-reduced-motion` intactos.** No añadir animación sin degradación.
- **Los gates de fixtures y de galería siguen fallando por defecto.** Durante el desarrollo el arnés se corre con `--allow-fixture-assets --allow-gallery-placeholder`. **Nunca** editar `FIXTURE_HASHES` ni `GALLERY_PLACEHOLDER_HASHES` ni silenciar esos gates de otra forma.
- **Toda aserción nueva se demuestra en ROJO por su causa real** antes de darla por buena. Comprobar un valor inventado no vale: ya costó dos intentos en el rediseño anterior. En este plan cada aserción se escribe antes que su implementación, y el paso "verificar que falla" es obligatorio.
- **Un arnés verde no significa que el sitio esté bien.** Hubo 14 aserciones en verde mientras el nombre del autor era invisible. Cada tarea se cierra mirando capturas reales de los tres temas.
- **Textos literales.** Los del spec están aprobados palabra por palabra por el usuario. No reescribirlos, no "mejorarlos".

### Comandos de referencia

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run dev          # servidor en http://127.0.0.1:5173
npm run build        # tsc && vite build
npm run lint

python3 scripts/verify.py --theme vice      --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme hyprland  --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme caelestia --allow-fixture-assets --allow-gallery-placeholder
```

### Script de capturas (se usa al cierre de cada tarea)

Guardar como `scripts/shots.py` en la Tarea 1 y reutilizarlo en todas las demás.

```python
"""Capturas de una escena en los tres temas, escritorio y movil.

Uso: python3 scripts/shots.py <escena> <etiqueta>
  <escena>   valor de data-scene: hero | about | obra | credits | contacto
  <etiqueta> prefijo del archivo, p.ej. "t2-vinieta"

Escribe en /tmp/shots/<etiqueta>-<tema>-<viewport>.png
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME = "/usr/bin/google-chrome"
ARGS = ["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"]
VIEWPORTS = {"desktop": {"width": 1440, "height": 900}, "mobile": {"width": 390, "height": 844}}
THEMES = ["vice", "hyprland", "caelestia"]
OUT = Path("/tmp/shots")


def main() -> int:
    scene, label = sys.argv[1], sys.argv[2]
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME, args=ARGS)
        for theme in THEMES:
            for name, viewport in VIEWPORTS.items():
                page = browser.new_page(viewport=viewport)
                page.goto(f"http://127.0.0.1:5173/?theme={theme}",
                          wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(5000)
                page.evaluate(
                    "(s) => document.querySelector(`[data-scene='${s}']`)"
                    "?.scrollIntoView({block: 'start'})", scene)
                page.wait_for_timeout(2000)
                page.screenshot(path=str(OUT / f"{label}-{theme}-{name}.png"))
                page.close()
        browser.close()
    print(f"capturas en {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

## File Structure

| Archivo | Responsabilidad | Tareas |
|---|---|---|
| `src/data/content.ts` | Única fuente de verdad del contenido. Gana el campo `currentStatus` y el grupo "Automatización e IA". | 1 |
| `src/utils/icons.ts` | Registro de SVG de `simple-icons`. Lanza si falta un slug. Gana cuatro entradas. | 1 |
| `src/sections/about.ts` | Marcado de "Quién es". El campo "Ahora" deja de derivarse de `experience[0]`. | 1, 4 |
| `src/sections/hero.ts` | Marcado del hero. Los tres bloques que se desvanecen pasan a identificarse por valor. | 3 |
| `src/components/credits.ts` | Marcado compartido del stack. Gana la pieza de detalle en la fila. | 7 |
| `src/themes/themes.css` | Skins por tema. Viñeta del hero, rejilla de obra en Vice, bloque de cartel. | 2, 5, 7 |
| `src/style.css` | Estilos compartidos. Ficha, línea de tiempo, cartela de rodaje, hover. | 4, 5, 6, 7 |
| `src/themes/vice.choreography.ts` | Coreografías propias de Vice. Salida del hero, gesto de ficha, motion de obra. | 3, 4, 6 |
| `scripts/verify.py` | Arnés. Cada tarea añade sus aserciones. | 1–7 |
| `scripts/shots.py` | Capturas en los tres temas. Se crea en la Tarea 1. | 1 |

### Dónde van las aserciones dentro de `scripts/verify.py`

`run()` tiene un bloque `if theme == "vice":` (hoy en la línea 931) para lo que solo existe en Vice, y comprobaciones fuera de él para lo que es común a los tres temas. Cada tarea dice explícitamente dónde va cada aserción. Todas usan el helper `check(condition, label)` (línea 155), que imprime `OK`/`FAIL` y acumula en `failures`.

---

## Task 1: Contenido, datos e iconos

Actualiza `content.ts` con los textos y cifras aprobados, registra los cuatro iconos nuevos y desacopla el campo "Ahora" de la pasantía terminada. Es la base de todo lo demás: las tareas 4 y 7 maquetan datos que esta tarea tiene que haber puesto ya.

**Files:**
- Modify: `src/data/content.ts`
- Modify: `src/utils/icons.ts`
- Modify: `src/sections/about.ts:20-21`
- Modify: `scripts/verify.py`
- Create: `scripts/shots.py`

**Interfaces:**
- Consumes: nada (primera tarea).
- Produces:
  - `identity.currentStatus: string` — nuevo campo obligatorio de la interfaz `Identity`.
  - `skillGroups` con 4 grupos y 16 entradas totales sumando `secondarySkills`.
  - `focusAreas` con 3 entradas.
  - `getIconMarkup(slug)` resuelve además `"gsap" | "n8n" | "claude" | "googlegemini"`.

- [ ] **Step 1: Escribir las aserciones que fallan**

En `scripts/verify.py`, dentro del bloque `if theme == "vice":`, junto al resto de comprobaciones de contenido:

```python
                # Task 1: contenido y datos actualizados. Se leen del DOM
                # renderizado, no de content.ts: lo que importa es que lleguen
                # a la pantalla, no que existan en el modulo.
                datos = page.evaluate("""(() => {
                  const scene = document.querySelector('[data-scene="about"]');
                  if (!scene) return null;
                  const stats = [...scene.querySelectorAll('[data-stats] b')].map(b => b.textContent.trim());
                  const dds = [...scene.querySelectorAll('.about-facts dd')].map(d => d.textContent.trim());
                  const dts = [...scene.querySelectorAll('.about-facts dt')].map(d => d.textContent.trim());
                  const ahora = dts.indexOf('Ahora');
                  return {
                    stats,
                    ahora: ahora >= 0 ? dds[ahora] : null,
                    focos: scene.querySelectorAll('[data-track] > div:last-child .about-item').length,
                    titulo: scene.querySelector('[data-line] .lead')?.textContent.trim() ?? '',
                  };
                })()""")
                check(datos is not None and "10.º" in datos["stats"],
                      f"la cifra de semestre dice 10.º (stats={datos['stats'] if datos else None})")
                check(datos is not None and "5" in datos["stats"],
                      f"la cifra de proyectos dice 5 (stats={datos['stats'] if datos else None})")
                check(datos is not None and datos["ahora"] == "Freelancer",
                      f"el campo Ahora de la ficha dice Freelancer (ahora={datos['ahora'] if datos else None})")
                check(datos is not None and datos["focos"] == 3,
                      f"En que me enfoco tiene tres entradas (n={datos['focos'] if datos else None})")
                check(
                    datos is not None
                    and datos["titulo"] == "Estudio Ingeniería de Sistemas y llevo cinco años construyendo software.",
                    f"el titulo de Quien es es el aprobado (titulo={datos['titulo'][:60] if datos else None!r})",
                )

                # El stack pasa de 12 a 16 entradas y gana un cuarto grupo.
                # `getIconMarkup` lanza si un slug no esta registrado, asi que
                # que las 16 filas existan en el DOM ya prueba que los cuatro
                # iconos nuevos resuelven: si faltara uno, createCredits
                # habria lanzado y la escena no se habria montado.
                stack = page.evaluate("""(() => {
                  const rows = [...document.querySelectorAll('[data-credit]')];
                  return {
                    total: rows.length,
                    grupos: [...new Set(rows.map(r => r.querySelector('.credit-role')?.textContent.trim()))],
                    nombres: rows.map(r => r.querySelector('.credit-name')?.textContent.trim()),
                    svgs: rows.filter(r => r.querySelector('svg')).length,
                  };
                })()""")
                check(stack["total"] == 16, f"el stack tiene 16 entradas (n={stack['total']})")
                check("Automatización e IA" in stack["grupos"],
                      f"existe el grupo Automatizacion e IA (grupos={stack['grupos']})")
                for esperado in ("GSAP", "n8n", "Claude Code", "Gemini"):
                    check(esperado in stack["nombres"],
                          f"el stack incluye {esperado}")
```

Fuera del bloque de Vice — la marca es del contenido, no del tema, y `getIconMarkup` corre en los tres:

```python
                # El panel de detalle pinta el icono de la entrada activa. Que
                # haya SVG prueba que el slug resolvio en `getIconMarkup`.
                panel_icon = page.evaluate(
                    "() => !!document.querySelector('[data-credit-panel] .credits-svg svg')"
                )
                check(panel_icon, "el panel de creditos pinta el icono de la entrada activa")
```

- [ ] **Step 2: Verificar que fallan**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run dev &
sleep 5
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `FAIL` en las aserciones de semestre (dice `9.º`), proyectos (dice `4`), Ahora (dice `Telefónica Venezuela`), focos (`n=2`), título (el texto viejo), total del stack (`n=12`), grupo de automatización y las cuatro tecnologías nuevas. La causa real es que el contenido todavía no existe: eso es exactamente lo que estas aserciones vigilan.

- [ ] **Step 3: Registrar los cuatro iconos**

En `src/utils/icons.ts`, añadir los imports junto a los existentes y las cuatro claves al objeto `icons`:

```ts
import gsap from "simple-icons/icons/gsap.svg?raw";
import n8n from "simple-icons/icons/n8n.svg?raw";
import claude from "simple-icons/icons/claude.svg?raw";
import googlegemini from "simple-icons/icons/googlegemini.svg?raw";
```

```ts
const icons: Record<string, string> = {
  react,
  typescript,
  tailwindcss,
  vite,
  gsap,
  python,
  django,
  mysql,
  javascript,
  html5,
  css,
  c,
  cplusplus,
  n8n,
  claude,
  googlegemini,
};
```

- [ ] **Step 4: Actualizar el contenido**

En `src/data/content.ts`:

```ts
export interface Identity {
  name: string;
  role: string;
  headline: string;
  subheadline: string;
  location: string;
  email: string;
  phone: string;
  github: string;
  /** Perfil de LinkedIn: para mucha gente de seleccion es la via de contacto
   *  por defecto, antes que el correo. */
  linkedin: string;
  githubAvatar: string;
  /** Estado visible en la ficha: la senal mas util para quien recluta. */
  availability: string;
  /**
   * Lo que hace AHORA. Campo explicito y no derivado: la ficha lo sacaba de
   * `experience[0].organization`, asi que al cerrarse la pasantia en mayo de
   * 2026 el sitio habria seguido diciendo "Telefonica Venezuela" para
   * siempre. Un dato que cambia solo con el tiempo no puede depender de la
   * entrada mas reciente de otra lista.
   */
  currentStatus: string;
  since: string;
}
```

```ts
export const identity: Identity = {
  name: "Aoshi Blanco Sanz",
  role: "Desarrollador Full Stack",
  headline: "Construyo sistemas que aguantan producción, no demos.",
  subheadline: "De la base de datos a la pantalla.",
  location: "Caracas, Venezuela",
  email: "a.blanco1501@gmail.com",
  phone: "+58 424 228 1033",
  github: "https://github.com/Aoshi346",
  linkedin: "https://www.linkedin.com/in/aoshi-blanco-sanz-14119b2b7",
  githubAvatar: "https://avatars.githubusercontent.com/u/137179835?v=4",
  availability: "Abierto a oportunidades",
  currentStatus: "Freelancer",
  since: "2021",
};
```

```ts
/** Lectura instantanea antes de leer una sola frase. */
export const stats: Stat[] = [
  { value: "2021", label: "Desde" },
  { value: "10.º", label: "Semestre" },
  { value: "5", label: "Proyectos" },
  { value: "1", label: "En producción" },
];

export const aboutCopy: string[] = [
  "Estudio Ingeniería de Sistemas y llevo cinco años construyendo software.",
  "Pienso mejor cuando el problema es real: un flujo de aprobaciones que nadie sigue, unas cuentas en tres monedas que no cuadran. Eso es lo que hay debajo.",
];
```

El periodo de la pasantía, que ya terminó:

```ts
export const experience: Experience[] = [
  {
    role: "Pasante B2C Conocimiento al Cliente",
    organization: "Telefónica Venezuela",
    period: "Ago 2025 — May 2026",
    description:
      "Desarrollo herramientas internas para el equipo de conocimiento al cliente, con foco en datos de campañas a gran escala.",
  },
];
```

Los tres focos:

```ts
/** Pares titulo/detalle de "En que me enfoco", especificos de Aoshi. */
export const focusAreas: FocusArea[] = [
  {
    title: "Que aguante el volumen",
    detail: "Una consulta sobre miles de filas tiene que seguir tardando lo mismo",
  },
  {
    title: "Que no se rompa",
    detail: "El estado complejo es donde fallan las interfaces, y donde más cuidado pongo",
  },
  {
    title: "Que no haya que repetirlo",
    detail: "Si un proceso se hace igual cada semana, lo automatizo",
  },
];
```

GSAP en Frontend, detrás de Vite, dentro de `skillGroups`:

```ts
      {
        name: "GSAP",
        slug: "gsap",
        detail: "Las animaciones de scroll y las transiciones que hacen que la interfaz se sienta viva.",
      },
```

Y el grupo nuevo, como tercer elemento de `skillGroups`, después de "Backend":

```ts
  {
    label: "Automatización e IA",
    items: [
      {
        name: "n8n",
        slug: "n8n",
        detail: "Encadeno procesos que si no habría que repetir a mano cada semana.",
      },
      {
        name: "Claude Code",
        slug: "claude",
        detail: "Lo uso a diario para revisar y refactorizar sin perder el control del código.",
      },
      {
        name: "Gemini",
        slug: "googlegemini",
        detail: "Para contrastar enfoques cuando estoy decidiendo cómo montar algo.",
      },
    ],
  },
```

El periodo de EchoPlan, en `caseStudies`:

```ts
    period: "Ago 2025 — May 2026",
```

- [ ] **Step 5: Desacoplar el campo "Ahora"**

En `src/sections/about.ts`, dentro de `createCard()`, sustituir la línea que deriva la organización:

```ts
  const facts = el("dl", "about-facts", [
    el("dt", "", ["Rol"]),
    el("dd", "", [identity.role]),
    el("dt", "", ["Base"]),
    el("dd", "", [identity.location]),
    el("dt", "", ["Ahora"]),
    // Dato explicito, no `experience[0].organization`: la pasantia termino en
    // mayo de 2026 y derivarlo de la experiencia mas reciente dejaba la ficha
    // afirmando un empleo que ya no existe.
    el("dd", "", [identity.currentStatus]),
    el("dt", "", ["Estudia"]),
    el("dd", "", [education[0]?.institution ?? ""]),
  ]);
```

- [ ] **Step 6: Verificar que pasan**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: las trece aserciones nuevas en `OK`. El resto del arnés sigue como estaba.

- [ ] **Step 7: Crear `scripts/shots.py`**

Copiar el script completo de la sección "Comandos de referencia" de este plan a `scripts/shots.py`.

- [ ] **Step 8: Comprobar los tres temas y mirar las capturas**

```bash
python3 scripts/verify.py --theme hyprland  --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme caelestia --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/shots.py about t1-contenido
python3 scripts/shots.py credits t1-contenido
```

Abrir las doce capturas de `/tmp/shots/` y confirmar con los ojos: las cifras nuevas se leen, "Freelancer" aparece en la ficha, los tres focos caben, y las cuatro filas nuevas del stack pintan su icono en los tres temas. Con 16 filas la lista es más alta que antes: anotar si desborda en móvil, la Tarea 7 lo resuelve.

- [ ] **Step 9: Build y lint**

```bash
npm run build
npm run lint
```

- [ ] **Step 10: Commit**

```bash
git add src/data/content.ts src/utils/icons.ts src/sections/about.ts scripts/verify.py scripts/shots.py
git commit -m "feat(contenido): datos actualizados, tres focos y grupo de automatizacion

El campo Ahora deja de derivarse de experience[0]: la pasantia cerro en mayo
de 2026 y la ficha habria seguido afirmando un empleo terminado."
```

---

## Task 2: Hero — la viñeta

Sustituye el panel rectangular por una mancha elíptica que se disuelve en la imagen. La aserción nueva mide el borde: es lo único que distingue "viñeta" de "caja con opacidad más baja".

**Files:**
- Modify: `src/themes/themes.css:72-105`
- Modify: `scripts/verify.py`

**Interfaces:**
- Consumes: nada de la Tarea 1.
- Produces: `.hero-surface` en Vice deja de tener borde recto perceptible. Ninguna tarea posterior depende de su geometría.

**Contexto que el implementador necesita.** El 88% de opacidad y el `blur(10px)` actuales no son un capricho: el gate `check_contrast_wcag` (línea 315) excluye del pass/fail cualquier texto cuyo fondo muestreado no sea uniforme (desviación típica > `MAX_BG_STDDEV`), y `verify.py:453` **falla si una escena no logra medir ni un elemento**. Contra el fixture de barras SMPTE que sirve hoy `public/media/vice-hero.*` — franjas de color primario puro lado a lado — hizo falta el 88% para que el muestreo bajo el nombre saliera plano. Aflojar el scrim sin más deja el hero sin cobertura y el arnés falla, correctamente.

La salida es cambiar la **forma**, no solo bajar la opacidad: núcleo sólido bajo el texto, disolución hacia los bordes.

- [ ] **Step 1: Escribir la aserción que falla**

En `scripts/verify.py`, añadir esta función al nivel de módulo, junto a las demás comprobaciones:

```python
def check_hero_scrim_edge(page, screenshot_bytes: bytes) -> None:
    """El scrim del hero en Vice no debe leerse como una caja.

    Que mide: la diferencia de luminancia entre una franja de pixeles JUSTO
    DENTRO del borde izquierdo de `.hero-surface` y otra JUSTO FUERA. Un panel
    con fondo uniforme produce un salto grande en esos pocos pixeles — es
    literalmente lo que hace visible el rectangulo. Una vinieta que se disuelve
    produce un salto pequeno.

    Por que el borde y no la opacidad declarada: leer `background` del CSS
    diria "hay un color-mix al 88%" tanto si la caja se ve como si esta
    enmascarada hasta desaparecer. El defecto que el usuario reporto es
    visual — un borde recto perceptible — asi que se mide sobre el pixel
    renderizado, igual que hace `check_contrast_wcag`.
    """
    rect = page.evaluate("""(() => {
      const el = document.querySelector('.hero-surface');
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return {x: r.x, y: r.y, width: r.width, height: r.height};
    })()""")
    if not rect or rect["width"] < 40:
        check(False, "hero: existe .hero-surface con geometria medible")
        return

    img = Image.open(BytesIO(screenshot_bytes)).convert("RGB")
    mid_y = rect["y"] + rect["height"] / 2
    left = rect["x"]

    # Franjas de 6px de ancho a cada lado del borde, saltando 2px del propio
    # borde para no muestrear el pixel de transicion.
    dentro = _sample_strip(img, left + 2, mid_y - 30, left + 8, mid_y + 30)
    fuera = _sample_strip(img, left - 8, mid_y - 30, left - 2, mid_y + 30)
    if not dentro or not fuera:
        check(False, "hero: el borde de .hero-surface cae dentro del encuadre")
        return

    def luminancia(muestras: list[tuple[int, int, int]]) -> float:
        return sum(_relative_luminance(s) for s in muestras) / len(muestras)

    salto = abs(luminancia(dentro) - luminancia(fuera))
    # Umbral 0.02 en luminancia relativa (escala 0-1). Medido: el panel actual
    # al 88% da un salto muy por encima; una vinieta disuelta se queda por
    # debajo. Si el fixture de video cambia, re-medir antes de tocar el numero.
    check(
        salto < 0.02,
        f"hero: el scrim no dibuja un borde recto (salto de luminancia en el "
        f"borde izquierdo = {salto:.4f}, maximo 0.02)",
    )
```

Y llamarla en `run()` justo después de la línea 875, donde ya se toma la captura para el gate de contraste del hero (`screenshot_bytes = page.screenshot(full_page=False)` en la 867):

```python
            if theme == "vice":
                check_hero_scrim_edge(page, screenshot_bytes)
```

La captura se reutiliza a propósito: tomar otra costaría un segundo de render y mediría un frame distinto del vídeo, que es justo lo que hace ruidosa una medición de píxel.

- [ ] **Step 2: Verificar que falla**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `FAIL hero: el scrim no dibuja un borde recto (salto de luminancia ... )` con un valor claramente por encima de 0.02. **Anotar el valor medido**: es la prueba de que la aserción cazaba el defecto real, no un umbral inventado.

- [ ] **Step 3: Sustituir el panel por la viñeta**

En `src/themes/themes.css`, reemplazar el bloque `:root[data-theme="vice"] .hero-surface` completo (hoy líneas 72-105, incluido su comentario) por:

```css
/*
 * VINIETA, NO PANEL. El tratamiento anterior era un rectangulo de
 * `--color-ink` al 88% con blur y una mascara de degradado en los cuatro
 * lados. Cumplia su funcion (dar al gate de contraste un fondo plano que
 * muestrear) pero se leia como una caja borrosa alrededor del nombre — el
 * defecto que reporto el usuario.
 *
 * La forma cambia; la funcion no. El nucleo sigue siendo lo bastante solido
 * bajo el texto para que `check_contrast_wcag` mida (la desviacion tipica del
 * muestreo tiene que quedar bajo MAX_BG_STDDEV, y `verify.py` FALLA si la
 * escena no consigue medir ni un elemento), pero la opacidad cae a cero antes
 * de llegar a ningun borde: no hay linea recta que ver. `check_hero_scrim_edge`
 * vigila justo eso, midiendo el salto de luminancia en el borde.
 *
 * El 88% sigue en el centro por la misma razon de siempre: el fixture SMPTE
 * que sirve hoy `public/media/vice-hero.*` pone franjas de color primario puro
 * lado a lado, el caso mas hostil posible. Con el video real (Task 11 del plan
 * anterior) sobrara margen.
 */
:root[data-theme="vice"] .hero-surface {
  position: relative;
  background: none;
  border: none;
  box-shadow: none;
  padding: clamp(2.5rem, 7vw, 5rem) clamp(2rem, 8vw, 7rem);
  isolation: isolate;
}

:root[data-theme="vice"] .hero-surface::before {
  content: "";
  position: absolute;
  inset: -12% -8%;
  z-index: -1;
  pointer-events: none;
  background: radial-gradient(
    ellipse 54% 48% at 50% 50%,
    color-mix(in srgb, var(--color-ink) 88%, transparent) 0%,
    color-mix(in srgb, var(--color-ink) 84%, transparent) 38%,
    color-mix(in srgb, var(--color-ink) 58%, transparent) 62%,
    color-mix(in srgb, var(--color-ink) 26%, transparent) 80%,
    transparent 100%
  );
  filter: blur(18px);
}
```

- [ ] **Step 4: Verificar que pasa**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `OK hero: el scrim no dibuja un borde recto`, y — igual de importante — `OK cobertura de contraste — vice: al menos un elemento medible` con `evaluados >= 1`. Si la cobertura cae a cero, la viñeta quedó demasiado suave: subir el porcentaje del centro (no bajar el umbral de la aserción) y volver a medir.

- [ ] **Step 5: Comprobar los otros dos temas**

```bash
python3 scripts/verify.py --theme hyprland  --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme caelestia --allow-fixture-assets --allow-gallery-placeholder
```

`.hero-surface` es el envoltorio compartido por los tres temas: Caelestia lo viste como tarjeta Material You y `check_theme_identity` (línea 679) exige que tenga fondo tonal sólido, `backdrop-filter` con blur real y sombra. Esta regla es de Vice y no debería tocarlo — el arnés lo confirma. Si Caelestia falla, la regla nueva se está aplicando fuera de su tema.

- [ ] **Step 6: Mirar las capturas**

```bash
python3 scripts/shots.py hero t2-vinieta
```

Confirmar: en Vice no hay ningún borde recto alrededor del nombre y el nombre se lee; en Caelestia sigue habiendo tarjeta; en Hyprland nada cambió. Mirar también móvil 390x844: con el padding nuevo el nombre no puede desbordar.

- [ ] **Step 7: Build, lint y commit**

```bash
npm run build && npm run lint
git add src/themes/themes.css scripts/verify.py
git commit -m "fix(hero): vinieta en vez de panel rectangular

El scrim mantiene el nucleo solido que el gate de contraste necesita para
medir, pero cae a cero antes de dibujar ningun borde. La asercion nueva mide
el salto de luminancia en el borde, no la opacidad declarada."
```

---

## Task 3: Hero — la salida escalonada y el zoom

Los tres bloques de acompañamiento salen en orden, y el zoom del nombre arranca cuando ya se han ido.

**Files:**
- Modify: `src/sections/hero.ts:10-25`
- Modify: `src/themes/vice.choreography.ts:57-103`
- Modify: `scripts/verify.py`

**Interfaces:**
- Consumes: nada de las tareas 1-2.
- Produces: los tres bloques del hero se identifican por valor — `[data-hero-fade="kick"]`, `[data-hero-fade="lead"]`, `[data-hero-fade="corner"]`. La Tarea 4 no los usa; la aserción de esta tarea sí.

**Contexto.** Hoy los tres salen a la vez (`exit.to(fading, {...duration: 0.28}, 0)`) y el zoom entra en `0.12`, casi solapado. El selector `[data-hero-fade]` no distingue cuál es cuál, así que ninguna aserción puede comprobar el orden. Por eso el primer paso de implementación es darles valor.

Las dos capas anti-carrera documentadas en la bitácora **se mantienen**: el estado inicial se fija de forma síncrona antes de cablear el zoom, y el tween usa `fromTo` con el valor de partida escrito en el código. Si se rompen, el nombre vuelve a quedar invisible en cada carga.

- [ ] **Step 1: Escribir la aserción que falla**

En `scripts/verify.py`, al nivel de módulo:

```python
def check_hero_exit_stagger(browser, url: str) -> None:
    """El acompanamiento del hero sale ESCALONADO, no de golpe.

    Que mide: la opacidad de los tres bloques en un punto temprano del
    recorrido de pin. Si salen escalonados, en ese punto las esquinas ya se
    han ido bastante mas que el rotulo. Si salen a la vez —el defecto que
    reporto el usuario— las tres opacidades son practicamente iguales.

    Se comprueba la DIFERENCIA entre bloques, no que acaben en cero: acabar en
    cero lo cumplen tanto la version rota como la buena.

    Corre en su propia pagina porque necesita scroll controlado sin que
    interfieran los barridos de otras comprobaciones.
    """
    page = browser.new_page(viewport=DESKTOP)
    try:
        page.goto(f"{url}/?theme=vice", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)

        # Un 12% de la altura del viewport dentro del recorrido de pin: lo
        # bastante pronto para que el escalonado todavia no haya terminado.
        page.mouse.wheel(0, int(DESKTOP["height"] * 0.12))
        page.wait_for_timeout(1500)

        op = page.evaluate("""(() => {
          const get = (v) => {
            const el = document.querySelector(`[data-hero-fade="${v}"]`);
            return el ? parseFloat(getComputedStyle(el).opacity) : null;
          };
          return {kick: get('kick'), lead: get('lead'), corner: get('corner')};
        })()""")

        check(
            all(v is not None for v in op.values()),
            f"hero: los tres bloques de acompanamiento estan marcados por valor ({op})",
        )
        if any(v is None for v in op.values()):
            return
        check(
            op["corner"] < op["kick"] - 0.15,
            f"hero: las esquinas salen antes que el rotulo "
            f"(corner={op['corner']:.2f}, kick={op['kick']:.2f}, minimo 0.15 de diferencia)",
        )
        check(
            op["lead"] < op["kick"],
            f"hero: la frase sale antes que el rotulo "
            f"(lead={op['lead']:.2f}, kick={op['kick']:.2f})",
        )
    finally:
        page.close()
```

Llamarla dentro del bloque `if theme == "vice":`, junto a `check_gallery_progress_bar` y las demás que abren su propia página:

```python
                check_hero_exit_stagger(browser, url)
```

- [ ] **Step 2: Verificar que falla**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `FAIL hero: los tres bloques de acompanamiento estan marcados por valor ({'kick': None, ...})`, porque hoy el atributo no lleva valor. Tras el Step 3 esa primera aserción pasa y quedan en rojo las dos del orden, que es la causa real: salen a la vez.

- [ ] **Step 3: Marcar los tres bloques por valor**

En `src/sections/hero.ts`:

```ts
export function createHero(): HTMLElement {
  const eyebrow = el("p", "hero-kick", [identity.role]);
  // Valor, no atributo vacio: la coreografia los saca en orden y el arnes
  // comprueba ese orden. Sin distinguirlos no hay forma de medirlo.
  eyebrow.setAttribute("data-hero-fade", "kick");

  const name = el("h1", "display-xl mt-4 text-[clamp(2.8rem,11vw,9.5rem)]", [identity.name]);
  name.setAttribute("data-hero-name", "");

  const lead = el("p", "lead mx-auto mt-5 max-w-[32ch] text-paper/85", [identity.subheadline]);
  lead.setAttribute("data-hero-fade", "lead");

  const location = el("span", "", [identity.location]);

  const email = el("a", "hero-mail", [identity.email]);
  email.href = `mailto:${identity.email}`;

  const corner = el("div", "hero-corner", [location, email]);
  corner.setAttribute("data-hero-fade", "corner");
```

El resto de la función no cambia.

- [ ] **Step 4: Escalonar la salida y retrasar el zoom**

En `src/themes/vice.choreography.ts`, dentro de `scene1Title`, sustituir la construcción de `fading` y la timeline `exit`:

```ts
  const chars = splitChars(name);
  // Orden de salida: primero lo periferico, al final el rotulo pegado al
  // nombre. `querySelectorAll` devuelve orden de documento, que aqui seria
  // kick, lead, corner — justo el contrario del que se quiere.
  const fadeOrder = ["corner", "lead", "kick"] as const;
  const fading = fadeOrder
    .map((key) => root.querySelector<HTMLElement>(`[data-hero-fade="${key}"]`))
    .filter((element): element is HTMLElement => element !== null);
```

La timeline de entrada sigue igual salvo que ahora `fading` está en otro orden, lo cual es correcto: entra por el mismo camino por el que sale.

```ts
  const exit = gsap.timeline({
    scrollTrigger: {
      id: HERO_ZOOM_TRIGGER_ID,
      trigger: hero,
      start: "top top",
      // +=220% en vez de +=150%: con el recorrido corto, escalonar la salida y
      // meter el zoom despues obligaba a solaparlos. Alargar el pin es lo que
      // deja sitio a las dos fases sin atropellarlas.
      end: "+=220%",
      pin: true,
      scrub: 1,
    },
  });
  // Fase 1 — el acompanamiento se va POR ORDEN. Antes los tres salian a la vez
  // en el primer 28% del recorrido, y eso se leia como "desaparecieron", no
  // como una salida. El desfase de 0.1 es lo que hace visible el escalonado; la
  // asercion `check_hero_exit_stagger` lo mide.
  exit.to(
    fading,
    { opacity: 0, y: -30, filter: "blur(6px)", ease: "none", duration: 0.3, stagger: 0.1 },
    0,
  );
  // Fase 2 — el zoom arranca cuando el acompanamiento YA se fue (0.3 de salida
  // + 0.2 de desfase acumulado del stagger = 0.5). Solaparlos era el defecto.
  // fromTo, no to(): el valor de partida va escrito a mano, nunca leido del
  // DOM. Leerlo fue la causa de la regresion que dejo el nombre invisible.
  exit.fromTo(
    name,
    { scale: 1, opacity: 1 },
    { scale: 9, opacity: 0, ease: "power2.in", duration: 1 },
    0.5,
  );
  // El fondo acompana con un empuje minimo: si solo se mueve el texto, el
  // gesto se lee como "el titulo crece", no como "la camara entra". 1.06 es
  // deliberadamente poco — mas que eso y el video se nota reencuadrado.
  const backdrop = document.querySelector<HTMLElement>(".bg-theme");
  if (backdrop) {
    exit.fromTo(backdrop, { scale: 1 }, { scale: 1.06, ease: "power2.in", duration: 1 }, 0.5);
  }
```

`.bg-theme` es el host del fondo que monta `main.ts`; se busca en `document` y no en `root` porque vive fuera del `<main>` que recibe la coreografía.

- [ ] **Step 5: Verificar que pasa**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: las tres aserciones de esta tarea en `OK`, y **sin regresión** en `[data-hero-name] visible a scroll 0`, que es la que vigila la carrera del nombre invisible.

- [ ] **Step 6: Verificar la degradación accesible**

```bash
python3 scripts/verify.py --theme vice --reduced --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `OK el nombre es legible con reduced-motion`. La coreografía no corre con `reduced-motion`, así que los tres bloques se quedan en reposo — correcto.

- [ ] **Step 7: Mirar el gesto, no solo el arnés**

```bash
python3 scripts/shots.py hero t3-salida
```

Y además, a mano: abrir `http://127.0.0.1:5173/?theme=vice` en un navegador real y scrollear despacio por el hero. Confirmar que las esquinas se van primero, luego la frase, luego el rótulo, y que el nombre empieza a crecer cuando la pantalla ya está limpia. Esto **no lo puede juzgar una captura**: es lo único de esta tarea que exige mirarlo en movimiento.

- [ ] **Step 8: Build, lint y commit**

```bash
npm run build && npm run lint
git add src/sections/hero.ts src/themes/vice.choreography.ts scripts/verify.py
git commit -m "fix(hero): salida escalonada y zoom sin solape

Los tres bloques de acompanamiento salen por orden (esquinas, frase, rotulo)
y el zoom arranca despues. El pin pasa de 150% a 220% para dar sitio a las dos
fases. Se conservan las dos capas anti-carrera del nombre."
```

---

## Task 4: Quién es — composición y motion

La sección llena la pantalla, la ficha crece, y trayectoria y foco pasan a línea de tiempo con hitos.

**Files:**
- Modify: `src/sections/about.ts`
- Modify: `src/style.css:483-680`
- Modify: `src/themes/vice.choreography.ts:109-160`
- Modify: `scripts/verify.py`

**Interfaces:**
- Consumes de la Tarea 1: `identity.currentStatus`, `focusAreas` con 3 entradas, `stats` con las cifras nuevas.
- Produces: `.about-item` gana el modificador `.is-done` para el hito cerrado. Ninguna tarea posterior lo consume.

- [ ] **Step 1: Escribir la aserción que falla**

Dentro del bloque `if theme == "vice":`:

```python
                # Task 4: la seccion llena la pantalla. El defecto reportado
                # era que el contenido moria a ~620px de 900 y dejaba el tercio
                # inferior vacio. Se mide la caja real del contenido contra la
                # altura del viewport, no la altura de la seccion (que ya era
                # min-h-screen y por eso no delataba nada).
                relleno = page.evaluate("""(() => {
                  const scene = document.querySelector('[data-scene="about"]');
                  if (!scene) return null;
                  const grid = scene.querySelector('.about-grid');
                  if (!grid) return null;
                  return {
                    contenido: grid.getBoundingClientRect().height,
                    viewport: window.innerHeight,
                  };
                })()""")
                ratio = (relleno["contenido"] / relleno["viewport"]) if relleno else 0
                check(
                    ratio > 0.72,
                    f"Quien es: el contenido ocupa la pantalla "
                    f"(alto del contenido / viewport = {ratio:.2f}, minimo 0.72)",
                )

                # La linea de tiempo distingue lo cerrado de lo que sigue en
                # curso. Es informacion (la pasantia termino, los estudios no),
                # asi que se comprueba que existen las dos clases, no solo que
                # hay puntos.
                hitos = page.evaluate("""(() => {
                  const scene = document.querySelector('[data-scene="about"]');
                  if (!scene) return null;
                  const items = [...scene.querySelectorAll('[data-track] .about-item')];
                  return {
                    total: items.length,
                    cerrados: items.filter(i => i.classList.contains('is-done')).length,
                  };
                })()""")
                check(hitos is not None and hitos["total"] >= 5,
                      f"Quien es: hay hitos en la linea de tiempo (n={hitos['total'] if hitos else None})")
                check(hitos is not None and hitos["cerrados"] >= 1,
                      f"Quien es: al menos un hito esta marcado como cerrado "
                      f"(n={hitos['cerrados'] if hitos else None})")
```

- [ ] **Step 2: Verificar que falla**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `FAIL Quien es: el contenido ocupa la pantalla` con un ratio en torno a 0.6-0.7 (el defecto real medido) y `FAIL ... al menos un hito esta marcado como cerrado` con `n=0`.

- [ ] **Step 3: Marcar los hitos cerrados en el marcado**

En `src/sections/about.ts`, dentro de `createTrack()`:

```ts
function createTrack(): HTMLElement {
  // `scene-surface` en las dos columnas: en Caelestia gana la superficie
  // Material You (necesaria ademas para que el titulo, sobre fondo claro sin
  // tarjeta, no caiga por debajo de 4.5:1 — medido con el arnes de contraste).
  const path = el("div", "about-track-col scene-surface", [
    el("h3", "about-h", ["Trayectoria"]),
    ...experience.map((item) => {
      // Punto relleno = etapa cerrada. La pasantia termino en mayo de 2026;
      // los estudios siguen. Es informacion, no adorno: quien lee la ficha
      // distingue de un vistazo lo que esta en marcha de lo que no.
      const entry = el("div", "about-item is-done", [
        el("b", "", [`${item.role} · ${item.organization}`]),
        el("span", "", [item.period]),
      ]);
      return entry;
    }),
    ...education.map((item) =>
      el("div", "about-item", [
        el("b", "", [item.degree]),
        el("span", "", [`${item.institution} · ${item.period}`]),
      ]),
    ),
  ]);

  const focus = el("div", "about-track-col scene-surface", [
    el("h3", "about-h", ["En qué me enfoco"]),
    ...focusAreas.map((area) =>
      el("div", "about-item is-done", [el("b", "", [area.title]), el("span", "", [area.detail])]),
    ),
  ]);

  const track = el("div", "about-track", [path, focus]);
  track.setAttribute("data-track", "");
  return track;
}
```

- [ ] **Step 4: Agrandar la composición y montar la línea de tiempo**

En `src/style.css`, sustituir los valores indicados dentro del bloque de "Quién es":

```css
.about-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: clamp(1.4rem, 4vw, 3.4rem);
  align-items: start;
  margin-top: 1rem;
}

@media (min-width: 860px) {
  .about-grid {
    /* La ficha crece: 235px la dejaba pequena contra el aire de la derecha,
       que era la mitad de por que la seccion se veia a medio llenar. */
    grid-template-columns: minmax(250px, 320px) 1fr;
  }
}

.about-card {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-card);
  padding: clamp(1.2rem, 3vw, 1.8rem) clamp(1.1rem, 2.5vw, 1.6rem);
  background: color-mix(in srgb, var(--color-ink) 38%, transparent);
  backdrop-filter: blur(6px);
}

.about-avatar {
  width: 74px;
  height: 74px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--color-line);
}
```

La disponibilidad pasa a píldora. Sustituir el bloque `.about-status`:

```css
/*
 * Pildora, no linea de texto suelta: la disponibilidad es la senal mas util
 * para quien recluta y necesita leerse como un estado, no como una frase mas
 * de la ficha. El color sale de `--color-accent-legible` por el mismo motivo
 * que `.about-facts dt`: el accent puro se queda sin margen en algun tema.
 */
.about-status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.9rem;
  padding: 0.35rem 0.7rem;
  border: 1px solid color-mix(in srgb, var(--color-accent) 45%, transparent);
  border-radius: 99px;
  font-weight: 700;
  font-size: 0.58rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-accent-legible);
}
```

Las cifras crecen:

```css
.about-stats b {
  display: block;
  font-family: var(--font-display);
  font-weight: var(--display-weight);
  font-size: clamp(1.8rem, 4vw, 2.9rem);
  line-height: 1;
  color: var(--color-accent);
  font-variant-numeric: tabular-nums;
}
```

Y `.about-item` pasa de filete lateral a línea de tiempo con hitos. Sustituir el bloque `.about-item` por:

```css
/*
 * Linea de tiempo con hitos. El filete lateral plano no distinguia una etapa
 * cerrada de una en curso, y esa distincion es informacion real: la pasantia
 * termino en mayo de 2026 y los estudios siguen. Punto relleno = cerrado o en
 * marcha (`.is-done`); punto hueco = en curso.
 */
.about-track-col .about-item {
  position: relative;
  border-left: 0;
  padding-left: 1.4rem;
  margin-bottom: 1rem;
}

.about-track-col .about-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.42rem;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: 1px solid var(--color-accent);
  background: var(--color-ink);
  z-index: 1;
}

.about-track-col .about-item.is-done::before {
  background: var(--color-accent);
}

/* El hilo que une los hitos: se detiene en el ultimo para no colgar en vacio. */
.about-track-col .about-item:not(:last-child)::after {
  content: "";
  position: absolute;
  left: 3px;
  top: 1.1rem;
  bottom: -1rem;
  width: 1px;
  background: color-mix(in srgb, var(--color-accent) 32%, transparent);
}
```

- [ ] **Step 5: Verificar que pasa**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: las tres aserciones de esta tarea en `OK`, y el ratio de relleno impreso por encima de 0.72. Si se queda corto, subir el tamaño de las cifras o el `gap` de `.about-track` — nunca bajar el umbral.

- [ ] **Step 6: Dar a la ficha su propio gesto**

En `src/themes/vice.choreography.ts`, dentro de `scene2Card`, sustituir el tween de la ficha:

```ts
  if (card) {
    // Revelado por mascara vertical, no un desplazamiento lateral: la ficha se
    // descubre como un plano que entra, en linea con el resto del lenguaje de
    // la seccion. `clipPath` se anima en compositor, asi que no cuesta layout.
    gsap.from(card, {
      clipPath: "inset(0 0 100% 0)",
      opacity: 0,
      duration: 1,
      ease: "power3.out",
      scrollTrigger: { ...base, id: ABOUT_TRIGGER_IDS[0] },
    });
  }
```

Y encadenar los hitos de la línea de tiempo, que hoy entran como un bloque único. Sustituir el tween de `track`:

```ts
  if (track) {
    // Los hitos entran uno a uno, no la columna entera de golpe: la linea de
    // tiempo se dibuja sola de arriba abajo.
    const milestones = Array.from(track.querySelectorAll<HTMLElement>(".about-item"));
    gsap.from(milestones, {
      x: -14,
      opacity: 0,
      duration: 0.6,
      ease: "power2.out",
      stagger: 0.08,
      delay: 0.5,
      scrollTrigger: { ...base, id: ABOUT_TRIGGER_IDS[3] },
    });
  }
```

- [ ] **Step 7: Comprobar los tres temas y mirar**

```bash
python3 scripts/verify.py --theme hyprland  --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme caelestia --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/shots.py about t4-quien-es
```

**Atención al riesgo principal de esta tarea.** `.about-item` es compartido por los tres temas. La regla nueva se acota con `.about-track-col .about-item` para no alcanzar otros usos, pero Caelestia viste `.about-track-col` como tarjeta Material You: confirmar en la captura que el hito y el hilo no se salen de la tarjeta ni pisan su padding. En Caelestia, que es claro, comprobar además que el punto hueco (relleno `--color-ink`, que ahí es casi blanco) sigue distinguiéndose del relleno.

- [ ] **Step 8: Build, lint y commit**

```bash
npm run build && npm run lint
git add src/sections/about.ts src/style.css src/themes/vice.choreography.ts scripts/verify.py
git commit -m "feat(about): la seccion llena la pantalla y la trayectoria es una linea de tiempo

Ficha mas grande, disponibilidad como pildora, cifras mayores y hitos que
distinguen lo cerrado de lo que sigue en curso. La ficha se revela por mascara
y los hitos encadenan."
```

---

## Task 5: Obra — galería a la derecha y cartela de rodaje

El lado derecho deja de estar vacío y la cartela deja de parecer una ventana de navegador.

**Files:**
- Modify: `src/themes/themes.css`
- Modify: `src/style.css`
- Modify: `scripts/verify.py`

**Interfaces:**
- Consumes: nada de tareas anteriores.
- Produces: `.gallery-item` gana el pseudo-contenido de cartela. La Tarea 6 anima estas mismas piezas.

**Contexto que cambia el enfoque, leer antes de empezar.** La galería **no se reconstruye**. `src/components/gallery.ts` ya monta un carril horizontal arrastrable con Pointer Events, navegación por teclado, barra de progreso y un `ResizeObserver`; y el arnés vigila tres cosas sobre ese DOM: que haya al menos dos carriles (`data-gallery-track`), que **todos los carriles con 2+ piezas sean desplazables en horizontal en móvil**, y `check_gallery_progress_bar`. Sustituir el componente por una rejilla rompería las tres y tiraría a la basura la accesibilidad ya construida.

Lo que se hace es **re-maquetar el mismo DOM desde CSS, solo en Vice y solo en escritorio**: el carril pasa a rejilla con la primera pieza grande a la derecha y el resto como miniaturas. **En móvil sigue siendo el carril horizontal de siempre**, así que la aserción de desplazamiento sigue en verde. Es el mismo principio de "un DOM, presentación por tema" que ya rige el resto del sitio.

Ojo con el número de piezas: EchoPlan declara dos capturas, no tres. La rejilla tiene que funcionar con `n` piezas — primera grande, resto en fila — no asumir tres.

- [ ] **Step 1: Escribir la aserción que falla**

Dentro del bloque `if theme == "vice":`:

```python
                # Task 5: en escritorio la galeria ocupa la mitad derecha de la
                # escena. El defecto reportado era que ese 35% quedaba vacio
                # con solo la marca de agua del ordinal. Se mide donde cae la
                # galeria respecto al ancho de la escena.
                reparto = page.evaluate("""(() => {
                  const scene = document.querySelector('[data-scene="obra"]');
                  if (!scene) return null;
                  const gal = scene.querySelector('[data-gallery]');
                  if (!gal) return null;
                  const s = scene.getBoundingClientRect();
                  const g = gal.getBoundingClientRect();
                  return {centroGaleria: (g.x + g.width / 2 - s.x) / s.width};
                })()""")
                centro = reparto["centroGaleria"] if reparto else None
                check(
                    centro is not None and centro > 0.55,
                    f"obra: la galeria vive en la mitad derecha en escritorio "
                    f"(centro relativo = {centro}, minimo 0.55)",
                )

                # La cartela es de rodaje, no cromo de navegador: tira superior
                # con toma y timecode. Se comprueba el contenido generado, que
                # es donde vive.
                cartela = page.evaluate("""(() => {
                  const item = document.querySelector('.gallery-item');
                  if (!item) return null;
                  const antes = getComputedStyle(item, '::before').content;
                  return {slate: antes};
                })()""")
                check(
                    cartela is not None and "Toma" in (cartela["slate"] or ""),
                    f"obra: la cartela lleva tira de rodaje (::before = {cartela['slate'] if cartela else None})",
                )
```

- [ ] **Step 2: Verificar que falla**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `FAIL obra: la galeria vive en la mitad derecha` con un centro relativo en torno a 0.3 (hoy vive abajo a la izquierda) y `FAIL obra: la cartela lleva tira de rodaje` con `content: none`.

- [ ] **Step 3: Re-maquetar la escena de obra en Vice**

En `src/themes/themes.css`, en el bloque de Vice, después de la regla de `[data-scene]`:

```css
/*
 * OBRA A DOS COLUMNAS (solo Vice, solo escritorio). El lado derecho estaba
 * vacio salvo por la marca de agua del ordinal, y la galeria vivia pequena
 * abajo a la izquierda.
 *
 * El DOM NO cambia: sigue siendo el carril arrastrable de
 * `components/gallery.ts`, con sus Pointer Events, su navegacion por teclado y
 * su barra de progreso. Aqui solo se le cambia el reparto en pantalla. En
 * movil (por debajo de 1024px) no aplica nada de esto y el carril sigue siendo
 * horizontal, que es lo que exige la asercion de desplazamiento del arnes.
 */
@media (min-width: 1024px) {
  :root[data-theme="vice"] [data-scene="obra"] .scene-surface {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(2rem, 4vw, 3.5rem);
    align-items: center;
  }

  /* La galeria salta a la columna derecha y ocupa su alto. El resto de piezas
     (rotulo, titulo, frase, metadatos, columnas, pie) se quedan en la
     izquierda por orden de documento. */
  :root[data-theme="vice"] [data-scene="obra"] [data-gallery] {
    grid-column: 2;
    grid-row: 1 / -1;
    align-self: center;
    margin-top: 0;
  }

  /* El carril deja de ser una fila y pasa a rejilla: la primera pieza grande,
     el resto como miniaturas debajo. Se escribe con `grid-column: 1 / -1` en
     la primera y auto en las demas para que funcione con CUALQUIER numero de
     piezas: EchoPlan declara dos, no tres. */
  :root[data-theme="vice"] [data-scene="obra"] .gallery-track {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.9rem;
    overflow: visible;
  }

  :root[data-theme="vice"] [data-scene="obra"] .gallery-item:first-child {
    grid-column: 1 / -1;
  }

  /* La barra de progreso no tiene sentido sin carril desplazable. */
  :root[data-theme="vice"] [data-scene="obra"] .gallery-bar {
    display: none;
  }
}
```

- [ ] **Step 4: Vestir la cartela de rodaje**

En `src/style.css`, junto al resto de estilos de galería, añadir:

```css
/*
 * CARTELA DE RODAJE. El cromo anterior (tres puntos tipo semaforo) leia la
 * captura como una ventana de navegador — generico y ajeno al lenguaje de
 * cine del tema. Ahora la pieza se lee como un fotograma: tira superior con
 * toma y timecode, perforacion de pelicula por los costados y marcas de
 * encuadre en las esquinas.
 *
 * Va en el CSS compartido pero solo se activa en Vice (regla de tema mas
 * abajo): Hyprland y Caelestia conservan su presentacion.
 */
:root[data-theme="vice"] .gallery-item {
  position: relative;
  border-radius: var(--radius-card);
  overflow: hidden;
}

/* Tira de claqueta. El numero de toma sale del indice de la pieza en el
   carril (`counter`), asi que no hay que tocar el marcado ni inventar datos. */
:root[data-theme="vice"] .gallery-track {
  counter-reset: toma;
}

:root[data-theme="vice"] .gallery-item {
  counter-increment: toma;
}

:root[data-theme="vice"] .gallery-item::before {
  content: "Toma " counter(toma, decimal-leading-zero);
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2;
  padding: 0.42rem 1.1rem;
  font-weight: 700;
  font-size: 0.5rem;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--color-accent-legible);
  background: color-mix(in srgb, var(--color-ink) 55%, transparent);
  border-bottom: 1px solid var(--color-line);
}

/* Perforacion de pelicula por los dos costados. */
:root[data-theme="vice"] .gallery-item::after {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background:
    repeating-linear-gradient(
      180deg,
      color-mix(in srgb, var(--color-paper) 16%, transparent) 0 6px,
      transparent 6px 16px
    ) left / 9px 100% no-repeat,
    repeating-linear-gradient(
      180deg,
      color-mix(in srgb, var(--color-paper) 16%, transparent) 0 6px,
      transparent 6px 16px
    ) right / 9px 100% no-repeat;
}
```

- [ ] **Step 5: Verificar que pasa**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: las dos aserciones nuevas en `OK` y — crítico — **sin regresión** en `todas las galerias con 2+ piezas son desplazables en horizontal en movil` ni en `check_gallery_progress_bar`. Si alguna cae, la regla de rejilla se está aplicando por debajo de 1024px.

- [ ] **Step 6: Mover el ordinal**

En `src/sections/obra/projectScene.ts`, la clase del ordinal lo ancla arriba a la derecha, que es justo donde ahora va la captura grande. Sustituir:

```ts
  const ordinal = el(
    "span",
    // Sangra por el borde izquierdo, detras del titulo: arriba a la derecha
    // queda tapado por la galeria desde la Task 5. Se probo abajo a la
    // izquierda y cruzaba el texto de "Problema", que se leia sucio.
    "pointer-events-none absolute -left-8 top-[14%] select-none font-display text-[clamp(7rem,26vw,22rem)] font-black leading-none text-paper/[0.06]",
    [String(index + 1).padStart(2, "0")],
  );
```

- [ ] **Step 7: Comprobar los tres temas y mirar**

```bash
python3 scripts/verify.py --theme hyprland  --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme caelestia --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/shots.py obra t5-obra
```

Confirmar en las capturas: en Vice escritorio la captura grande ocupa la derecha y las secundarias van debajo; en Vice móvil el carril sigue siendo horizontal; en Hyprland y Caelestia **nada ha cambiado** — es la comprobación más importante de esta tarea, porque `.scene-surface` y `.gallery-track` son compartidos.

- [ ] **Step 8: Build, lint y commit**

```bash
npm run build && npm run lint
git add src/themes/themes.css src/style.css src/sections/obra/projectScene.ts scripts/verify.py
git commit -m "feat(obra): galeria a la derecha y cartela de rodaje

Mismo DOM del carril arrastrable: solo cambia el reparto en pantalla, y solo
en Vice escritorio. En movil sigue siendo carril horizontal. La cartela pasa
de cromo de navegador a fotograma con toma, perforacion y marcas de encuadre."
```

---

## Task 6: Obra — hover y motion

La sección deja de ser estática bajo el cursor.

**Files:**
- Modify: `src/style.css`
- Modify: `src/themes/vice.choreography.ts:175-256`
- Modify: `scripts/verify.py`

**Interfaces:**
- Consumes de la Tarea 5: `.gallery-item` con su cartela.
- Produces: nada que consuman tareas posteriores.

- [ ] **Step 1: Escribir la aserción que falla**

Al nivel de módulo en `scripts/verify.py`:

```python
def check_obra_hover(browser, url: str) -> None:
    """Las cartelas de la obra responden al cursor.

    Que mide: el color del borde de una pieza antes y despues de poner el
    raton encima. Si no hay hover —el defecto reportado— los dos valores son
    identicos.

    Se comprueba el cambio, no un color concreto: acoplar la asercion al valor
    exacto del acento la rompe cada vez que se ajuste el token.
    """
    page = browser.new_page(viewport=DESKTOP)
    try:
        page.goto(f"{url}/?theme=vice", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)
        page.evaluate(
            "() => document.querySelector('[data-scene=\"obra\"]')"
            "?.scrollIntoView({block: 'start'})"
        )
        page.wait_for_timeout(1500)

        item = page.locator(".gallery-item").first
        antes = item.evaluate("el => getComputedStyle(el).borderColor")
        item.hover()
        page.wait_for_timeout(600)
        despues = item.evaluate("el => getComputedStyle(el).borderColor")

        check(
            antes != despues,
            f"obra: la cartela reacciona al cursor (borde antes={antes}, despues={despues})",
        )
    finally:
        page.close()
```

Llamarla dentro del bloque `if theme == "vice":`:

```python
                check_obra_hover(browser, url)
```

- [ ] **Step 2: Verificar que falla**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `FAIL obra: la cartela reacciona al cursor` con los dos colores idénticos. Es la causa real: hoy no hay regla de hover.

- [ ] **Step 3: Añadir el hover**

En `src/style.css`, después de las reglas de cartela de la Tarea 5:

```css
/*
 * Afordancia de escritorio. En movil no hay hover y la pieza ya se entiende
 * por el carril arrastrable; aqui el cursor tiene que delatar que la captura
 * es una pieza, no una imagen pegada al fondo.
 *
 * `@media (hover: hover)`: sin este guard, un navegador tactil deja la regla
 * pegada tras el primer toque, y la pieza se queda elevada para siempre.
 */
@media (hover: hover) {
  :root[data-theme="vice"] .gallery-item {
    transition:
      transform 260ms ease,
      border-color 260ms ease,
      box-shadow 260ms ease;
  }

  :root[data-theme="vice"] .gallery-item:hover {
    transform: translateY(-6px);
    border-color: var(--color-accent);
    box-shadow: 0 18px 44px -18px color-mix(in srgb, var(--color-ink) 90%, transparent);
  }
}

/* Sin transicion para quien pidio menos movimiento; el cambio de borde se
   mantiene, porque es la senal de afordancia, no decoracion. */
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="vice"] .gallery-item {
    transition: none;
  }

  :root[data-theme="vice"] .gallery-item:hover {
    transform: none;
  }
}

/*
 * Barrido de subrayado en la fila de metadatos. `background-size` en el eje X
 * se anima en compositor; animar `width` de un pseudo forzaria layout en cada
 * frame.
 */
@media (hover: hover) {
  :root[data-theme="vice"] .obra-meta > div {
    background-image: linear-gradient(var(--color-accent), var(--color-accent));
    background-repeat: no-repeat;
    background-position: 0 100%;
    background-size: 0% 1px;
    transition: background-size 320ms ease;
  }

  :root[data-theme="vice"] .obra-meta > div:hover {
    background-size: 100% 1px;
  }
}
```

- [ ] **Step 4: Verificar que pasa**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: `OK obra: la cartela reacciona al cursor`.

- [ ] **Step 5: Dar paralaje al ordinal**

En `src/themes/vice.choreography.ts`, dentro de `scene3Slate`, después del tween del ordinal existente, añadir un segundo trigger con scrub. Requiere una entrada más en la lista de ids:

```ts
/** Ids fijos del gesto 3, parametrizados por indice: puede haber varias escenas de obra. */
function obraTriggerIds(index: number): string[] {
  return [
    `vice-obra-ord-${index}`,
    `vice-obra-title-${index}`,
    `vice-obra-lead-${index}`,
    `vice-obra-meta-${index}`,
    `vice-obra-mask-${index}`,
    `vice-obra-gallery-${index}`,
    `vice-obra-parallax-${index}`,
  ];
}
```

```ts
    if (ordinal) {
      gsap.from(ordinal, {
        y: -70,
        scale: 1.35,
        opacity: 0,
        duration: 0.7,
        ease: "expo.out",
        scrollTrigger: { ...trigger, id: ids[0] },
      });
      // Paralaje: la marca de agua se mueve mas despacio que la escena, asi
      // que la cartela gana profundidad sin que nada compita con el texto.
      gsap.to(ordinal, {
        yPercent: -14,
        ease: "none",
        scrollTrigger: {
          id: ids[6],
          trigger: scene,
          start: "top bottom",
          end: "bottom top",
          scrub: 1,
        },
      });
    }
```

- [ ] **Step 6: Verificar la degradación y los tres temas**

```bash
python3 scripts/verify.py --theme vice --reduced --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme hyprland  --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme caelestia --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/shots.py obra t6-hover
```

Con `--reduced` la coreografía no corre, así que el paralaje no se aplica: correcto. Confirmar que `la galeria sigue disponible` sigue en `OK`.

- [ ] **Step 7: Build, lint y commit**

```bash
npm run build && npm run lint
git add src/style.css src/themes/vice.choreography.ts scripts/verify.py
git commit -m "feat(obra): hover en cartelas y metadatos, paralaje del ordinal

Elevacion y borde en acento al pasar el cursor, barrido de subrayado en la
fila de metadatos y marca de agua con scrub. Todo bajo (hover: hover) para que
no se quede pegado en tactil."
```

---

## Task 7: Con qué construyo — bloque de cartel

El detalle sale del panel y entra en la fila; los cuatro departamentos ordenan las dieciséis entradas.

**Files:**
- Modify: `src/components/credits.ts`
- Modify: `src/style.css:843-1073`
- Modify: `src/themes/themes.css:216-275`
- Modify: `scripts/verify.py`

**Interfaces:**
- Consumes de la Tarea 1: `skillGroups` con 4 grupos, 16 entradas totales.
- Produces: cada `[data-credit]` contiene `.credit-detail`; las filas van agrupadas bajo `.credit-dept`.

**Contexto.** `createCredits()` monta un DOM único para los tres temas: lista a la izquierda, panel de detalle a la derecha. En Vice pasa a bloque de cartel con el detalle en la propia fila; Hyprland y Caelestia **conservan su presentación de píldoras con panel**. La regla no negociable: `credits.ts` sigue montando lista, detalle y panel **siempre**, y el CSS bajo `[data-theme]` decide qué se ve. No ramificar por tema en TypeScript.

Se conserva toda la accesibilidad ya construida: `<button>` real por fila, `aria-pressed`, `aria-controls`, panel `aria-live="polite"`, primera entrada seleccionada al montar.

- [ ] **Step 1: Escribir la aserción que falla**

Al nivel de módulo en `scripts/verify.py`:

```python
def check_credits_presentation(page, theme: str) -> None:
    """Un DOM, tres presentaciones.

    En Vice el detalle se lee en la fila y el panel se oculta; en Hyprland y
    Caelestia el detalle se oculta y manda el panel. Se comprueba que el DOM
    trae SIEMPRE las dos piezas (que es lo que prueba que `credits.ts` no
    ramifica por tema) y que la visibilidad es la que toca en cada uno.
    """
    estado = page.evaluate("""(() => {
      const row = document.querySelector('[data-credit]');
      const detail = row ? row.querySelector('.credit-detail') : null;
      const panel = document.querySelector('[data-credit-panel]');
      const visible = (el) => {
        if (!el) return null;
        const s = getComputedStyle(el);
        return s.display !== 'none' && s.visibility !== 'hidden';
      };
      return {
        detailEnDom: !!detail,
        panelEnDom: !!panel,
        detailVisible: visible(detail),
        panelVisible: visible(panel),
        departamentos: document.querySelectorAll('.credit-dept').length,
      };
    })()""")

    # El DOM es el mismo en los tres temas: eso es lo que se esta protegiendo.
    check(estado["detailEnDom"], f"{theme}: la fila de creditos trae su detalle en el DOM")
    check(estado["panelEnDom"], f"{theme}: el panel de creditos sigue en el DOM")

    if theme == "vice":
        check(estado["detailVisible"] is True,
              f"vice: el detalle se lee en la fila (visible={estado['detailVisible']})")
        check(estado["panelVisible"] is False,
              f"vice: el panel lateral esta oculto (visible={estado['panelVisible']})")
        check(estado["departamentos"] == 4,
              f"vice: hay cuatro departamentos (n={estado['departamentos']})")
    else:
        check(estado["detailVisible"] is False,
              f"{theme}: el detalle de la fila esta oculto (visible={estado['detailVisible']})")
        check(estado["panelVisible"] is True,
              f"{theme}: manda el panel lateral (visible={estado['panelVisible']})")
```

Llamarla **fuera** del bloque de Vice, para que corra en los tres temas:

```python
            check_credits_presentation(page, theme)
```

- [ ] **Step 2: Verificar que falla**

```bash
python3 scripts/verify.py --theme vice --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme hyprland --allow-fixture-assets --allow-gallery-placeholder
```

Esperado en Vice: `FAIL ... la fila de creditos trae su detalle en el DOM` (no existe todavía), `FAIL vice: hay cuatro departamentos (n=0)`. En Hyprland: `FAIL ... el detalle de la fila esta oculto (visible=None)` por la misma razón.

- [ ] **Step 3: Añadir detalle y departamentos al marcado**

En `src/components/credits.ts`, sustituir la construcción de filas y lista. El resto de la función (panel, `select()`, accesibilidad) **no cambia**:

```ts
  const rows: HTMLButtonElement[] = [];
  const listChildren: HTMLElement[] = [];
  let index = 0;

  // Se recorre por grupo, no la lista aplanada: el departamento es la unidad
  // que ordena la seccion en Vice. `flatten()` sigue existiendo para el panel,
  // que necesita el indice global.
  const groups: SkillGroup[] = [
    ...skillGroups,
    { label: "Otras herramientas", items: secondarySkills },
  ];

  for (const group of groups) {
    const dept = el("p", "credit-dept", [el("span", "", [group.label])]);
    dept.setAttribute("aria-hidden", "true");
    listChildren.push(dept);

    for (const item of group.items) {
      const entry: CreditEntry = {
        role: group.label,
        name: item.name,
        slug: item.slug,
        detail: item.detail,
      };
      const row = createRow(entry, index);
      rows.push(row);
      listChildren.push(row);
      index += 1;
    }
  }
```

La cabecera de departamento lleva `aria-hidden` porque el rol ya viaja dentro de cada fila (`.credit-role`), que es lo que anuncia el lector de pantalla: sin esto, cada grupo se leería dos veces.

`createRow` es la extracción del `map` actual, con la pieza de detalle añadida:

```ts
  function createRow(entry: CreditEntry, position: number): HTMLButtonElement {
    const row = el("button", "credit", [
      el("span", "credit-role", [entry.role]),
      el("span", "credit-name", [entry.name]),
      // Tercera pieza del DOM compartido: en Vice se lee aqui mismo, en
      // Hyprland y Caelestia el CSS la oculta y manda el panel lateral. El
      // marcado es el mismo en los tres — la presentacion la decide el tema.
      el("span", "credit-detail", [entry.detail]),
    ]) as HTMLButtonElement;
    row.type = "button";
    row.setAttribute("data-credit", "");
    row.dataset.index = String(position);
    row.setAttribute("aria-controls", PANEL_ID);
    row.setAttribute("aria-pressed", "false");

    const select = () => {
      rows.forEach((other) => {
        other.classList.remove("is-active");
        other.setAttribute("aria-pressed", "false");
      });
      row.classList.add("is-active");
      row.setAttribute("aria-pressed", "true");
      icon.replaceChildren(elFromMarkup("credits-svg", getIconMarkup(entry.slug)));
      name.textContent = entry.name;
      role.textContent = entry.role;
      detail.textContent = entry.detail;
    };

    row.addEventListener("mouseenter", select);
    row.addEventListener("focus", select);
    row.addEventListener("click", select);
    return row;
  }
```

Y la lista se monta con los hijos nuevos:

```ts
  const list = el("div", "credits-list", listChildren);
  list.setAttribute("data-credit-roll", "");
```

El disparo inicial no cambia:

```ts
  rows[0]?.dispatchEvent(new MouseEvent("mouseenter"));
```

`flatten()` deja de usarse en el cuerpo principal. Borrarla **solo si** ninguna otra cosa la importa (`grep -rn "flatten" src/`); si queda huérfana, retirarla en este mismo commit.

- [ ] **Step 4: Vestir el bloque de cartel en Vice**

En `src/style.css`, dentro del bloque de créditos, añadir la presentación base compartida y el detalle oculto por defecto:

```css
/* Tercera pieza de la fila. Oculta por defecto: solo Vice la muestra. */
.credit-detail {
  display: none;
  font-size: 0.76rem;
  line-height: 1.45;
  color: color-mix(in srgb, var(--color-paper) 60%, transparent);
}

.credit-dept {
  display: none;
}
```

En `src/themes/themes.css`, en el bloque de Vice:

```css
/*
 * BLOQUE DE CARTEL. La referencia es el billing block del pie de un poster:
 * el departamento centrado entre dos filetes y las filas apretadas, con una
 * barra vertical fina separando el nombre de su linea.
 *
 * Por que este y no un rodillo con perforacion: se maquetaron los tres
 * tratamientos y se miraron montados. El de hoja de rodaje partia las
 * descripciones largas en dos lineas y dejaba las guias de puntos a alturas
 * distintas; el de bobina era el mas cargado. Este es el unico donde ningun
 * elemento se descoloca.
 *
 * Con 16 entradas, la columna repetia el nombre del departamento catorce
 * veces sin aportar nada: por eso `.credit-role` se oculta y el grupo pasa a
 * cabecera propia.
 */
:root[data-theme="vice"] .credits-grid {
  grid-template-columns: 1fr;
  max-width: none;
}

:root[data-theme="vice"] .credits-list {
  display: flex;
  flex-direction: column;
  padding: 0;
  background: none;
  backdrop-filter: none;
}

/* El panel lateral sobra: su contenido vive ahora en la propia fila. Sigue en
   el DOM (lo exige `check_credits_presentation`) porque Hyprland y Caelestia
   lo usan; aqui solo se oculta. */
:root[data-theme="vice"] .credits-panel {
  display: none;
}

:root[data-theme="vice"] .credit-dept {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  margin: 1.05rem 0 0.4rem;
}

:root[data-theme="vice"] .credit-dept:first-child {
  margin-top: 0.2rem;
}

:root[data-theme="vice"] .credit-dept::before,
:root[data-theme="vice"] .credit-dept::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--color-line);
}

:root[data-theme="vice"] .credit-dept span {
  flex: none;
  font-weight: 700;
  font-size: 0.56rem;
  letter-spacing: 0.34em;
  text-transform: uppercase;
  color: var(--color-accent-legible);
}

:root[data-theme="vice"] .credit {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  width: 100%;
  padding: 0.24rem 0.5rem;
  border: 0;
  border-left: 1px solid transparent;
}

/* El rol ya lo dice la cabecera del departamento. */
:root[data-theme="vice"] .credit-role {
  display: none;
}

:root[data-theme="vice"] .credit-name {
  flex: none;
  min-width: 190px;
  font-size: 1.28rem;
}

/* La barra vertical que separa nombre de descripcion: hace el trabajo de una
   guia de puntos sin su ruido. */
:root[data-theme="vice"] .credit-detail {
  display: block;
  position: relative;
  padding-left: 0.85rem;
}

:root[data-theme="vice"] .credit-detail::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 1px;
  height: 15px;
  background: color-mix(in srgb, var(--color-accent) 42%, transparent);
  transition: height 200ms ease, background-color 200ms ease;
}

:root[data-theme="vice"] .credit:hover .credit-detail,
:root[data-theme="vice"] .credit:focus-visible .credit-detail,
:root[data-theme="vice"] .credit.is-active .credit-detail {
  color: color-mix(in srgb, var(--color-paper) 92%, transparent);
}

:root[data-theme="vice"] .credit.is-active .credit-detail::before {
  height: 19px;
  background: var(--color-accent);
}

/* El signo de mas era la afordancia tactil de la version en lista; con el
   detalle a la vista en la propia fila ya no hay nada oculto que anunciar. */
:root[data-theme="vice"] .credit::after {
  content: none;
}

/* n8n se escribe en minuscula. `--display-transform` es `uppercase` en Vice y
   lo convertiria en "N8N", que no es la marca. */
:root[data-theme="vice"] .credit[data-lowercase] .credit-name {
  text-transform: none;
}
```

Para que esa última regla tenga a qué agarrarse, marcar la fila en `createRow`:

```ts
    // Marcas propias que no se escriben en mayusculas (n8n). El tema aplica
    // `text-transform: uppercase` a `.credit-name`; sin exencion, la marca se
    // renderiza mal.
    if (entry.name !== entry.name.toUpperCase() && entry.name === entry.name.toLowerCase()) {
      row.setAttribute("data-lowercase", "");
    }
```

- [ ] **Step 5: Verificar que pasa en los tres temas**

```bash
python3 scripts/verify.py --theme vice      --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme hyprland  --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme caelestia --allow-fixture-assets --allow-gallery-placeholder
```

Esperado: en Vice, detalle visible, panel oculto y cuatro departamentos. En Hyprland y Caelestia, detalle oculto y panel visible — la presentación de píldoras intacta. En los tres, las dos piezas presentes en el DOM.

- [ ] **Step 6: Comprobar la accesibilidad a mano**

Con el navegador abierto en `?theme=vice`, recorrer los créditos con `Tab` y confirmar que:
- cada fila recibe foco visible,
- la fila enfocada se marca activa (`aria-pressed="true"`),
- las cabeceras de departamento **no** reciben foco ni se anuncian dos veces.

Repetir en `?theme=hyprland` y confirmar que el panel lateral sigue cambiando al tabular.

- [ ] **Step 7: Mirar las capturas y decidir la altura**

```bash
python3 scripts/shots.py credits t7-cartel
```

El bloque de cartel es compacto: en escritorio sobrará aire abajo. Mirar la captura y decidir una de dos, dejando constancia en el commit:
- subir el tamaño de `.credit-name` y el `gap` entre departamentos hasta llenar, o
- aceptar que esta sección no es de altura completa.

En móvil 390x844, con 16 filas y 4 cabeceras, comprobar que la sección no desborda de forma incómoda; si lo hace, reducir `min-width` de `.credit-name` y dejar que el detalle caiga a la línea siguiente.

- [ ] **Step 8: Build, lint y commit**

```bash
npm run build && npm run lint
git add src/components/credits.ts src/style.css src/themes/themes.css scripts/verify.py
git commit -m "feat(creditos): bloque de cartel por departamentos en Vice

El detalle entra en la fila y el panel se oculta, solo en Vice: Hyprland y
Caelestia conservan sus pildoras con panel desde el mismo DOM. Cuatro
cabeceras de departamento sustituyen a la columna que repetia el grupo catorce
veces."
```

---

## Cierre

Con las siete tareas commiteadas:

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
python3 scripts/verify.py --theme vice      --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme hyprland  --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme caelestia --allow-fixture-assets --allow-gallery-placeholder
python3 scripts/verify.py --theme vice --reduced --allow-fixture-assets --allow-gallery-placeholder
grep -rE "lorem|placeholder|mockData" src/ --include="*.ts"
```

Los dos flags siguen siendo obligatorios: el vídeo de barras y las capturas de relleno siguen ahí y **son bloqueo de merge a producción**, no de este plan.

Recordatorio final, que es la lección más cara del rediseño anterior: **un arnés verde no significa que el sitio esté bien**. Antes de dar el trabajo por cerrado, abrir el sitio en un navegador real, en los tres temas, y recorrerlo entero.
