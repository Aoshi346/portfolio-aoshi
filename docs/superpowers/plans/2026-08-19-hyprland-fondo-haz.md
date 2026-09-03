# El haz al mando — fondo de Hyprland — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Portar el prototipo GLSL aprobado "el haz al mando" a
`src/backgrounds/hyprEmber.ts` (el fondo de producción del tema Hyprland), sustituyendo el halo
sin techo de hoy por un haz de canto duro gobernado por scroll, con techo de luminancia 46.

**Architecture:** Un único fragment shader dentro de `hyprEmber.ts` (mismo patrón que
`viceInk.ts`), montado vía `mountShaderBackground` (`shaderBackground.ts`, no se toca). El scroll
y la entrada del segundo haz llegan como `DynamicUniforms` (modelo *pull*, releídos cada
fotograma — cero listeners de resize). No hay test unitario de GLSL en este proyecto: la
verificación es empírica, con arneses Playwright/Python contra el build de producción servido
(mismo patrón que `measure-bg-luma.py`, `measure-obra-rail.py`). Cada tarea de este plan termina
en un comando ejecutable con salida verificable, no en un `pytest`.

**Tech Stack:** TypeScript strict + WebGL crudo (GLSL ES 1.00, sin Three.js) + Vite. Verificación:
Playwright (Python) contra `vite preview`.

**Spec:** `docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md` (fuente de verdad,
números de aceptación). Prototipo aprobado:
`docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-prototipo.glsl`.

## Global Constraints

- No tocar `src/backgrounds/shaderBackground.ts`, `src/backgrounds/viceInk.ts`, ni nada de Vice o
  Caelestia.
- Techo de luminancia: **46** (no 62, que es el de Vice).
- El recorte de techo va el ÚLTIMO paso del shader, después del grano.
- La entrada del segundo haz sale del `offsetTop` real de `#creditos`, nunca de un literal
  `0.735/0.765` escrito a mano.
- El grano trabaja en píxeles CSS: `gl_FragCoord.xy / uPixelRatio`.
- Responsive: ángulo, semiancho, origen del haz y derrame van todos por
  `mix(escritorio, movil, vertical)` con `vertical = smoothstep(1.0, 0.62, aspect)`. Escritorio
  debe quedar byte a byte idéntico (`vertical` vale 0 en apaisado).
- `prefers-reduced-motion` congela `uTime` (ya lo hace `shaderBackground.ts`); `uScroll` sigue
  vivo.
- `npm run build` y `npm run lint` en verde son requisito de cada task que toque código.
- Radio 0, filete de 1px — idioma visual del tema, no crear bordes redondeados nuevos.

---

## Task 1: Portar el shader a `hyprEmber.ts`

**Files:**
- Modify: `src/backgrounds/hyprEmber.ts` (fichero entero — 66 líneas hoy, se sustituye el
  contenido del `FRAGMENT_SHADER` y se reescribe `mountHyprEmber`)

**Interfaces:**
- Consumes: `mountShaderBackground(container, fragmentShader, dynamicUniforms?)` y
  `BackgroundHandle` de `src/backgrounds/shaderBackground.ts` (sin cambios en su firma).
  `dynamicUniforms` es `Record<string, () => number>` — cada función se llama una vez por
  fotograma.
- Produces: `mountHyprEmber(container: HTMLElement): BackgroundHandle` — misma firma que hoy,
  consumida por `src/themes/hyprland.ts:16-17` sin cambios.

- [x] **Step 1: Escribir el nuevo `FRAGMENT_SHADER`**

Reemplaza el contenido de `src/backgrounds/hyprEmber.ts` entero:

```ts
import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * El haz al mando: el fondo deja de ser un halo que respira y pasa a ser una
 * unica cuna de luz con canto duro, gobernada por el scroll. Dos cantos de
 * comportamiento distinto (uno duro, uno que se disuelve en el material) y un
 * derrame que sale del propio eje del haz, no de un foco con coordenadas
 * propias. Espeja la organizacion de Vice sin copiar su material: Vice es
 * tinta impresa, Hyprland es luz con canto.
 *
 * Reacciona por una sola via, `uScroll` (0..1, progreso del documento): el
 * balance de color, la posicion del origen, el angulo, el semiancho y la
 * entrada del segundo haz. Sin puntero y sin velocidad, misma razon que deja
 * escrita viceInk.ts: anadirlos aqui seria rediseñar, no portar.
 *
 * Portado literal del prototipo aprobado en el companion de brainstorming
 * (docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-prototipo.glsl), con
 * los seis uniforms de apagado de la maqueta (fAsim/fSangre/fEje/fCorte/
 * fDerrame/fMateria) colapsados a su lado "nuevo": esos uniforms solo
 * servian para comparar cada correccion con su version anterior en el
 * companion, no tienen sentido en produccion.
 *
 * Spec: docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime, uScroll, uCreditsEntry, uPixelRatio;
  uniform vec2 uResolution;
  varying vec2 vUv;

  /*
   * Techo de luminancia. Mecanismo importado de viceInk.ts (escala por
   * luminancia perceptual, no por canal: el verde aporta el 71% de la
   * luminancia percibida, asi que un tope por canal se calibra mirando un
   * tono concreto y se rompe en cuanto el fondo recorre otro), pero NO su
   * valor: 46 es el techo AA 4,5:1 de --haze (#b18c86, cuerpo de texto de
   * Hyprland), no el 62 de Vice, que esta calibrado contra su papel
   * #fff4e8.
   *
   * VA EL ULTIMO PASO, despues del grano. Medido: con el grano sumado
   * despues del recorte, su cola positiva se escapa del techo y el p99.5
   * sale a 48.1 en vez de 46.1.
   */
  vec3 techo(vec3 c) {
    float lm = 46.0 / 255.0;
    float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
    return l > lm ? c * (lm / max(l, 1e-4)) : c;
  }

  const vec3 INK = vec3(0.043, 0.016, 0.016);
  const vec3 EMBER = vec3(1.0, 0.353, 0.204);
  const vec3 CRIM = vec3(0.878, 0.114, 0.235);
  const vec3 AMBER = vec3(1.0, 0.627, 0.235);

  /*
   * Grano de carbon atado a pixeles de DISPOSITIVO, no a uv: con la rejilla
   * atada a uv el paso cambia con la resolucion y bate contra la rejilla de
   * la pantalla, y eso hormiguea al scrollear. Misma razon por la que Vice
   * ata su lineatura al fragmento.
   *
   * Se divide por uPixelRatio para trabajar en pixeles CSS. Con el paso
   * fijo en pixeles de BUFFER el grano cambia de tamano fisico entre
   * pantallas: shaderBackground.ts acota el ratio a 1 en <=820px y a 1.5 en
   * escritorio, asi que sin esta division la textura saldria ~1.5 veces mas
   * fina en retina que sin retina. Mismo hallazgo que viceInk.ts, misma
   * decision.
   */
  float carbon(vec2 frag, float ang) {
    vec2 css = frag / max(uPixelRatio, 1.0);
    float c = cos(ang), s = sin(ang);
    vec2 r = vec2(css.x * c - css.y * s, css.x * s + css.y * c);
    return mix(fbm(r / 34.0), hash(floor(r / 1.4)), 0.30);
  }

  void main() {
    vec2 uv = vUv;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    vec2 p = (uv * 2.0 - 1.0) * vec2(aspect, 1.0);
    float px = 2.0 / uResolution.y;

    /*
     * MOVIL: no basta con enderezar el angulo. Medido a 390x844: con el
     * semiancho fijo, el haz cubre TODA la pantalla y su canto duro —lo
     * unico que define esta direccion— queda fuera del encuadre. Y con el
     * origen fijo el sitio abre con el fondo casi vacio, porque en un
     * encuadre estrecho el haz aun no ha entrado. El aspecto gobierna las
     * cuatro cosas, no solo el angulo.
     */
    float vertical = smoothstep(1.0, 0.62, aspect);
    float ang = mix(1.36, 1.52, vertical) - uScroll * mix(0.30, 0.14, vertical);

    vec2 dir = vec2(cos(ang), sin(ang));
    vec2 nrm = vec2(-dir.y, dir.x);
    vec2 o = vec2(mix(-0.62, -0.30, vertical) + uScroll * mix(0.95, 0.62, vertical),
                  mix(0.0, 0.30, vertical));
    vec2 rel = p - o;

    /* distancia CON SIGNO al eje: sin abs(), que hacia salir los dos cantos
       iguales y el haz se leia como una cinta pegada encima */
    float s = dot(rel, nrm);
    float hw = (0.26 + uScroll * 0.10) * mix(1.0, 0.42, vertical);

    /* CANTO ASIMETRICO: un canto duro que define el haz, el otro lado se
       pierde en el material a lo largo de 0.42 */
    float duro = 1.0 - smoothstep(-px * 0.7, px * 0.7, s - hw);
    float suave = smoothstep(-hw - 0.42, -hw + 0.02, s);
    float dentro = duro * suave;

    /* CAIDA POR SU EJE: se mide a lo largo del haz, no como degradado
       vertical de viewport, asi que gira con el haz al girar con el
       scroll */
    float alo = dot(rel, dir);
    float caida = smoothstep(1.45, -0.15, alo) * smoothstep(-1.6, -0.9, alo);

    vec3 col = INK;

    /* DERRAME: la luz que el haz suelta sobre el material, calculada desde
       su propio eje, no un foco con coordenadas propias */
    float derrame = exp(-abs(s - hw) * 2.6) * caida;
    col += mix(CRIM, EMBER, uScroll) * derrame * mix(0.30, 0.17, vertical);

    /* MATERIA dentro del haz, multiplicativa. Aditiva subiria el suelo del
       cuadro entero. El canto se queda liso a proposito. */
    float m = carbon(gl_FragCoord.xy, ang);
    float cuerpo = 0.55 + m * 0.85;

    col += mix(EMBER, AMBER, 0.5 + 0.5 * p.y) * dentro * caida * 0.19 * cuerpo;
    col += AMBER * (1.0 - smoothstep(0.0, px * 1.15, abs(s - hw))) * caida * 0.62;

    /*
     * CORTE EN FRONTERA. El segundo haz entra en el limite Obra->Creditos
     * real (uCreditsEntry, calculado en TS desde el offsetTop de #creditos
     * — nunca un literal escrito a mano aqui), con corte seco: algo que
     * aparece de la nada dentro de una escena se lee como fallo de render.
     */
    float ent = smoothstep(uCreditsEntry - 0.015, uCreditsEntry + 0.015, uScroll);
    vec2 o2 = vec2(0.55, 0.10);
    vec2 d2dir = vec2(cos(-0.95), sin(-0.95));
    float s2 = dot(p - o2, vec2(-d2dir.y, d2dir.x));
    float alo2 = dot(p - o2, d2dir);
    float caida2 = smoothstep(1.3, -0.9, alo2);
    col += AMBER * (1.0 - smoothstep(0.0, px * 1.15, abs(abs(s2) - 0.055))) * caida2 * 0.46 * ent;

    /* SALE A SANGRE: caida leve solo en el vertice contrario al haz, en vez
       de vinetado radial que moria justo en las esquinas por donde el haz
       sale del cuadro */
    col *= mix(1.0, 0.86, smoothstep(0.6, 1.9, length(p - vec2(0.9, -0.9))));

    col += (hash(uv * uResolution + uTime) - 0.5) * 0.026;
    col = techo(col);
    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountHyprEmber(container: HTMLElement): BackgroundHandle {
  /*
   * #creditos ya existe en el DOM cuando este modulo monta: main.ts compone
   * `main` completo (con las cinco secciones) y lo anexa a #app antes de
   * invocar `applyTheme` -> `mountBackground` (ver src/main.ts, orden entre
   * `app.append(backgroundHost, noise, main, ...)` y
   * `void applyTheme(theme, backgroundHost)`). La seccion no se recrea
   * durante la visita, asi que una lectura al montar basta.
   */
  const creditos = document.getElementById("creditos");

  const readScrollable = (): number =>
    Math.max(document.documentElement.scrollHeight - window.innerHeight, 0);

  /*
   * Modelo PULL, igual que uScroll en viceInk.ts: se lee del propio
   * `window` cada fotograma, no de Lenis ni de ScrollTrigger, para no
   * depender de que la coreografia (import dinamico) haya cargado.
   */
  const readScroll = (): number => {
    const scrollable = readScrollable();
    return scrollable <= 0 ? 0 : Math.min(Math.max(window.scrollY / scrollable, 0), 1);
  };

  /*
   * Se relee cada fotograma en vez de cachear una fraccion fija: un cambio
   * de layout por resize se refleja solo en el siguiente fotograma, sin
   * necesidad de un ResizeObserver propio (mountShaderBackground ya tiene
   * el suyo para el canvas, y este calculo no depende de el).
   */
  const readCreditsEntry = (): number => {
    const scrollable = readScrollable();
    if (scrollable <= 0 || !creditos) return 0.75; // respaldo: 75% del documento
    return Math.min(Math.max(creditos.offsetTop / scrollable, 0), 1);
  };

  return mountShaderBackground(container, FRAGMENT_SHADER, {
    uScroll: readScroll,
    uCreditsEntry: readCreditsEntry,
  });
}
```

- [x] **Step 2: Compilar y lintar**

Run: `npm run build && npm run lint`
Expected: ambos en verde. Si `tsc`/`vite build` fallan por el shader (símbolo duplicado con
`NOISE_CHUNK`, uniform sin declarar, etc.), el error de Vite señala la línea del GLSL — corregir
antes de seguir.

- [x] **Step 3: Confirmar visualmente que el haz renderiza**

Run:
```bash
npm run build && npx vite preview --port 4173 &
sleep 2
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=hyprland', wait_until='domcontentloaded', timeout=30000)
    pg.wait_for_timeout(4000)
    pg.screenshot(path='/tmp/hyprland-check.png', full_page=False)
    b.close()
"
```
Expected: `/tmp/hyprland-check.png` muestra un fondo oscuro con una cuña diagonal de luz de canto
duro (no un halo difuso, no negro plano, no error de shader en consola).

- [x] **Step 4: Commit**

```bash
git add src/backgrounds/hyprEmber.ts
git commit -m "feat(hyprland): portar el haz al mando al fondo de produccion

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WiBaPiySGgkVMJTBGT2UMp"
```

---

## Task 2: Comentario de cabecera de `hyprland.ts`

**Files:**
- Modify: `src/themes/hyprland.ts:3` (solo el comentario de módulo, cero cambio funcional)

**Interfaces:**
- Consumes: `mountHyprEmber` de Task 1 (firma sin cambios).
- Produces: nada nuevo — `hyprlandTheme` sigue exportando lo mismo.

- [x] **Step 1: Actualizar el comentario**

En `src/themes/hyprland.ts`, sustituir:

```ts
/** Ascua: luz emisiva de canto duro sobre negro con sesgo rojo. */
```

por:

```ts
/** Ascua: el haz al mando — luz de canto duro sobre negro, gobernada por el scroll. */
```

- [x] **Step 2: Build**

Run: `npm run build`
Expected: verde (cambio de comentario, no debería afectar nada).

- [x] **Step 3: Commit**

```bash
git add src/themes/hyprland.ts
git commit -m "docs(hyprland): actualizar comentario del fondo tras el haz al mando

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WiBaPiySGgkVMJTBGT2UMp"
```

---

## Task 3: Arnés `scripts/measure-fondo-haz.py`

**Files:**
- Create: `scripts/measure-fondo-haz.py`

**Interfaces:**
- Consumes: build de producción servido en `--base` (default `http://localhost:4173`), página con
  `?theme=hyprland`. Mismo patrón de aislar el fondo que `scripts/measure-bg-luma.py`
  (`#app > *:not(.bg-theme):not(.bg-noise) { visibility: hidden !important; }`) y de muestreo
  desde dentro de la página que `scripts/measure-obra-rail.py` (evita que `page.screenshot()`
  contamine el timing).
- Produces: script ejecutable standalone, código de salida 0 si las 5 aserciones pasan, 1 si
  alguna falla (mismo contrato que el resto de `scripts/measure-*.py`). No se integra en
  `scripts/verify.py`.

- [x] **Step 1: Escribir el script completo**

Crear `scripts/measure-fondo-haz.py`:

```python
#!/usr/bin/env python3
"""El haz al mando — verificacion del fondo de Hyprland.

No arregla nada: mide, contra el build de produccion servido (nunca
`npm run dev`: el HMR corrompe las medidas). Cinco aserciones, las que fija
el spec en docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md,
seccion "## Verificacion":

  1. Techo de banda tipografica <= 46 (p99.5), 12 posiciones de scroll x 3
     viewports (390x844, 768x1024, 1440x900).
  2. El corte del segundo haz cae en el limite REAL de la seccion de
     creditos (su offsetTop / alto desplazable), no en un literal fijo.
  3. Sin deriva temporal: a scroll fijo, >= 160s de muestreo, recorrido de
     la mediana de luma <= 2.0.
  4. Canto duro visible: salto de luminancia >= 12 entre pixeles contiguos
     en la banda del haz, en los tres viewports.
  5. `prefers-reduced-motion`: dos capturas separadas 5s a scroll fijo,
     identicas.

Uso:
    npm run build && npx vite preview --port 4173
    python3 scripts/measure-fondo-haz.py [--base URL] [--json OUT]

Requiere `executable_path=/usr/bin/google-chrome` (el chromium propio de
Playwright no esta descargado en esta maquina) y `--use-gl=swiftshader`
para que el fondo WebGL renderice en headless.
"""

from __future__ import annotations

import argparse
import io
import json
import statistics
import sys

from playwright.sync_api import sync_playwright
from PIL import Image

CHROME = "/usr/bin/google-chrome"
DEFAULT_BASE = "http://127.0.0.1:4173"

VIEWPORTS = [
    {"width": 390, "height": 844},
    {"width": 768, "height": 1024},
    {"width": 1440, "height": 900},
]

BANDA_TOP = 0.06
BANDA_BOTTOM = 0.74
TECHO_BANDA = 46.0

N_POSICIONES = 12
DERIVA_SEGUNDOS = 160
DERIVA_PASO = 14
DERIVA_MAX_RECORRIDO = 2.0

CANTO_SALTO_MIN = 12.0

HIDE_CONTENT_CSS = (
    "#app > *:not(.bg-theme):not(.bg-noise) { visibility: hidden !important; }"
)


def luminancia(r: int, g: int, b: int) -> float:
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def percentil(valores: list[float], p: float) -> float:
    if not valores:
        return 0.0
    datos = sorted(valores)
    if len(datos) == 1:
        return datos[0]
    rango = (len(datos) - 1) * (p / 100.0)
    bajo = int(rango)
    alto = min(bajo + 1, len(datos) - 1)
    frac = rango - bajo
    return datos[bajo] + (datos[alto] - datos[bajo]) * frac


def banda_p995(png_bytes: bytes, alto_viewport: int) -> float:
    imagen = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    ancho_px, alto_px = imagen.size
    escala_y = alto_px / alto_viewport
    top_px = int(BANDA_TOP * alto_viewport * escala_y)
    bottom_px = int(BANDA_BOTTOM * alto_viewport * escala_y)

    pixeles = imagen.load()
    luminancias: list[float] = []
    for y in range(top_px, bottom_px):
        for x in range(ancho_px):
            r, g, b = pixeles[x, y]
            luminancias.append(luminancia(r, g, b))
    return percentil(luminancias, 99.5)


def fila_luma(png_bytes: bytes, frac_y: float) -> list[float]:
    """Luminancia a lo largo de una fila horizontal, para el salto de canto."""
    imagen = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    ancho_px, alto_px = imagen.size
    y = min(int(frac_y * alto_px), alto_px - 1)
    pixeles = imagen.load()
    return [luminancia(*pixeles[x, y]) for x in range(ancho_px)]


def mayor_salto(fila: list[float]) -> float:
    return max((abs(fila[i + 1] - fila[i]) for i in range(len(fila) - 1)), default=0.0)


def imagenes_iguales(a: bytes, b: bytes, margen: float = 1.0) -> bool:
    im_a = Image.open(io.BytesIO(a)).convert("RGB")
    im_b = Image.open(io.BytesIO(b)).convert("RGB")
    if im_a.size != im_b.size:
        return False
    px_a, px_b = im_a.load(), im_b.load()
    ancho, alto = im_a.size
    diffs = []
    for y in range(0, alto, 4):  # muestreo cada 4px: rapido, suficiente
        for x in range(0, ancho, 4):
            ra, ga, ba = px_a[x, y]
            rb, gb, bb = px_b[x, y]
            diffs.append(abs(luminancia(ra, ga, ba) - luminancia(rb, gb, bb)))
    return statistics.mean(diffs) <= margen


def hide_content(pg) -> None:
    pg.add_style_tag(content=HIDE_CONTENT_CSS)
    pg.wait_for_timeout(300)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    url = f"{args.base.rstrip('/')}/?theme=hyprland"
    fallos: list[str] = []
    reporte: dict[str, object] = {}

    with sync_playwright() as p:
        b = p.chromium.launch(
            executable_path=CHROME,
            headless=True,
            args=["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"],
        )

        # --- 1. Techo de banda, 3 viewports x 12 posiciones ---
        techo_reporte = []
        for viewport in VIEWPORTS:
            pg = b.new_page(viewport=viewport)
            pg.goto(url, wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(6000)
            hide_content(pg)

            alto_total = pg.evaluate("document.documentElement.scrollHeight")
            max_scroll = max(alto_total - viewport["height"], 0)
            posiciones = [round(max_scroll * i / (N_POSICIONES - 1)) for i in range(N_POSICIONES)]

            peor = 0.0
            for y in posiciones:
                pg.evaluate(f"window.scrollTo(0, {y})")
                pg.wait_for_timeout(500)
                png = pg.screenshot()
                banda = banda_p995(png, viewport["height"])
                peor = max(peor, banda)
                if banda > TECHO_BANDA:
                    fallos.append(
                        f"[1-techo] {viewport['width']}x{viewport['height']} scroll={y}: "
                        f"banda p99.5={banda:.1f} > techo {TECHO_BANDA}"
                    )
            techo_reporte.append({"viewport": viewport, "peor_banda": peor})
            print(f"[1] {viewport['width']}x{viewport['height']}: peor banda p99.5={peor:.2f}")
            pg.close()
        reporte["techo"] = techo_reporte

        # --- 2. Corte del segundo haz en el limite real ---
        pg = b.new_page(viewport=VIEWPORTS[-1])
        pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(6000)

        entrada_esperada = pg.evaluate(
            """() => {
                const creditos = document.getElementById('creditos');
                const scrollable = document.documentElement.scrollHeight - window.innerHeight;
                if (!creditos || scrollable <= 0) return null;
                return creditos.offsetTop / scrollable;
            }"""
        )
        if entrada_esperada is None:
            fallos.append("[2-corte] no se pudo calcular el offsetTop de #creditos")
        else:
            hide_content(pg)
            alto_total = pg.evaluate("document.documentElement.scrollHeight")
            max_scroll = alto_total - VIEWPORTS[-1]["height"]

            # Barre uScroll entre 0.70 y 0.80 en pasos finos y detecta el
            # salto de luminancia del segundo haz por el crecimiento del
            # maximo de la banda respecto al fotograma anterior.
            pasos = [0.70 + i * 0.002 for i in range(51)]
            anterior = None
            salto_en = None
            for frac in pasos:
                y = round(max_scroll * frac)
                pg.evaluate(f"window.scrollTo(0, {max(y, 0)})")
                pg.wait_for_timeout(150)
                png = pg.screenshot()
                banda = banda_p995(png, VIEWPORTS[-1]["height"])
                if anterior is not None and banda - anterior > 2.0 and salto_en is None:
                    salto_en = frac
                anterior = banda

            if salto_en is None:
                fallos.append(
                    "[2-corte] no se detecto salto de luminancia del segundo haz "
                    "entre uScroll 0.70 y 0.80"
                )
            elif abs(salto_en - entrada_esperada) > 0.03:
                fallos.append(
                    f"[2-corte] corte detectado en uScroll={salto_en:.3f}, "
                    f"esperado (offsetTop de #creditos)={entrada_esperada:.3f}"
                )
            print(
                f"[2] corte esperado={entrada_esperada:.3f} "
                f"detectado={salto_en if salto_en is not None else 'ninguno'}"
            )
            reporte["corte"] = {"esperado": entrada_esperada, "detectado": salto_en}
        pg.close()

        # --- 3. Sin deriva temporal, a scroll fijo ---
        pg = b.new_page(viewport=VIEWPORTS[-1])
        pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(6000)
        hide_content(pg)
        alto_total = pg.evaluate("document.documentElement.scrollHeight")
        pg.evaluate(f"window.scrollTo(0, {round((alto_total - 900) * 0.4)})")
        pg.wait_for_timeout(500)

        muestras = []
        t = 0
        while t <= DERIVA_SEGUNDOS:
            png = pg.screenshot()
            muestras.append(banda_p995(png, VIEWPORTS[-1]["height"]))
            pg.wait_for_timeout(DERIVA_PASO * 1000)
            t += DERIVA_PASO

        mediana = statistics.median(muestras)
        recorrido = max(muestras) - min(muestras)
        if recorrido > DERIVA_MAX_RECORRIDO:
            fallos.append(
                f"[3-deriva] recorrido de mediana={recorrido:.2f} > "
                f"maximo {DERIVA_MAX_RECORRIDO} (mediana={mediana:.2f}, muestras={muestras})"
            )
        print(f"[3] deriva: recorrido={recorrido:.2f} (max {DERIVA_MAX_RECORRIDO}), mediana={mediana:.2f}")
        reporte["deriva"] = {"recorrido": recorrido, "mediana": mediana, "muestras": muestras}
        pg.close()

        # --- 4. Canto duro visible, 3 viewports ---
        canto_reporte = []
        for viewport in VIEWPORTS:
            pg = b.new_page(viewport=viewport)
            pg.goto(url, wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(6000)
            hide_content(pg)
            png = pg.screenshot()
            salto = mayor_salto(fila_luma(png, 0.5))
            canto_reporte.append({"viewport": viewport, "salto": salto})
            if salto < CANTO_SALTO_MIN:
                fallos.append(
                    f"[4-canto] {viewport['width']}x{viewport['height']}: "
                    f"mayor salto={salto:.1f} < minimo {CANTO_SALTO_MIN}"
                )
            print(f"[4] {viewport['width']}x{viewport['height']}: mayor salto={salto:.1f}")
            pg.close()
        reporte["canto"] = canto_reporte

        # --- 5. prefers-reduced-motion: estatico ---
        ctx = b.new_context(viewport=VIEWPORTS[-1], reduced_motion="reduce")
        pg = ctx.new_page()
        pg.goto(url, wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(4000)
        hide_content(pg)
        primera = pg.screenshot()
        pg.wait_for_timeout(5000)
        segunda = pg.screenshot()
        if not imagenes_iguales(primera, segunda):
            fallos.append("[5-reduced-motion] dos capturas separadas 5s no son identicas")
        print(f"[5] reduced-motion: {'estatico' if imagenes_iguales(primera, segunda) else 'CAMBIA'}")
        pg.close()
        ctx.close()

        b.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"url": url, "reporte": reporte, "fallos": fallos}, f, indent=2)
        print(f"\nmedidas volcadas en {args.json}")

    print()
    for fallo in fallos:
        print("FALLO:", fallo)

    if fallos:
        print(f"\n{len(fallos)} aserciones fallidas de 5")
        return 1

    print("\nTODO OK — las 5 aserciones del haz al mando pasan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Step 2: Verificar que el script arranca (sintaxis + import)**

Run: `python3 -m py_compile scripts/measure-fondo-haz.py`
Expected: sin salida, código de salida 0.

- [x] **Step 3: Commit**

```bash
git add scripts/measure-fondo-haz.py
git commit -m "test(hyprland): arnes measure-fondo-haz.py para el haz al mando

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WiBaPiySGgkVMJTBGT2UMp"
```

---

## Task 4: Correr la verificación completa y arreglar lo que falle

**Files:**
- Modify: `src/backgrounds/hyprEmber.ts` (solo si algún número no cuadra — iterar sobre
  constantes, no sobre estructura; el shader del Task 1 es el prototipo aprobado literal, así que
  no se esperan sorpresas de diseño, solo posibles errores de transcripción)

**Interfaces:**
- Consumes: `scripts/measure-fondo-haz.py` (Task 3), `scripts/measure-bg-luma.py` (ya existe),
  `scripts/verify.py` (ya existe).
- Produces: evidencia verificable para el checklist pre-DONE del proyecto.

- [x] **Step 1: Levantar el build de producción**

```bash
npm run build
npx vite preview --port 4173 &
sleep 2
```

- [x] **Step 2: Correr el arnés nuevo**

Run: `python3 scripts/measure-fondo-haz.py --base http://localhost:4173 --json /tmp/fondo-haz.json`
Expected: código de salida 0, "TODO OK — las 5 aserciones del haz al mando pasan". Si falla,
leer qué aserción y por cuánto, ajustar la constante correspondiente en `hyprEmber.ts` (no la
estructura del shader — el prototipo ya está validado en el companion), y repetir desde Step 1.

- [x] **Step 3: Correr el arnés heredado de luminancia**

Run: `python3 scripts/measure-bg-luma.py --url "http://localhost:4173/?theme=hyprland"`
Expected: código 0 ("TODO OK"). El techo por defecto de este script es 62 (el de Vice); con el
fondo nuevo a techo 46 debe pasar con margen.

- [x] **Step 4: Correr `verify.py`**

Run: `python3 scripts/verify.py`
Expected: código 0, sin fallos nuevos fuera de la línea base conocida
(`scripts/verify-baseline.json`).

- [x] **Step 5: Capturas reales, y confirmar que Vice/Caelestia no cambiaron**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for theme, vw, name in [
        ('hyprland', {'width':390,'height':844}, 'hypr-mobile'),
        ('hyprland', {'width':1440,'height':900}, 'hypr-desktop'),
        ('vice', {'width':1440,'height':900}, 'vice-desktop'),
        ('caelestia', {'width':1440,'height':900}, 'caelestia-desktop'),
    ]:
        pg = b.new_page(viewport=vw)
        pg.goto(f'http://localhost:4173/?theme={theme}', wait_until='domcontentloaded', timeout=30000)
        pg.wait_for_timeout(6000)
        pg.screenshot(path=f'/tmp/{name}.png', full_page=False)
        pg.close()
    b.close()
"
```
Expected: `/tmp/hypr-mobile.png` y `/tmp/hypr-desktop.png` muestran el haz de canto duro correcto
en cada encuadre (canto visible dentro de la pantalla en móvil, no cubriendo todo el viewport).
`/tmp/vice-desktop.png` y `/tmp/caelestia-desktop.png` se ven igual que antes de este cambio
(comparación visual — no se tocó código de esos temas, así que es una confirmación, no se espera
diferencia).

- [x] **Step 6: Parar el preview server** <!-- verificado 2026-09-03: no queda ningun `vite preview` de esta fase vivo -->

```bash
kill %1 2>/dev/null || true
```

- [x] **Step 7: Commit (solo si Step 2 requirió ajustes en `hyprEmber.ts`)**

```bash
git add src/backgrounds/hyprEmber.ts
git commit -m "fix(hyprland): ajustar constantes del haz tras medir contra produccion

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WiBaPiySGgkVMJTBGT2UMp"
```

---

## Task 5: Gates de QA y cierre del spec

**Files:**
- Modify: `docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md` (cabecera `Estado:` +
  nueva sección `## Registro de implementación`)
- Modify: `PROGRESS.json` (raíz del proyecto)

**Interfaces:**
- Consumes: evidencia de Task 4 (capturas, salidas de arneses).
- Produces: spec cerrado, listo para PR/merge.

- [x] **Step 1: Gate `lidia-naive-tester`**

Invocar el subagente `lidia-naive-tester` sobre el sitio servido (`http://localhost:4173/?theme=hyprland`,
o `npm run dev` si el subagente lo prefiere — seguir su memoria en
`.claude/agents/lidia-naive-tester/memory.md`). Verde requerido antes de continuar.

- [x] **Step 2: Gate `vera-art-director`**

Invocar el subagente `vera-art-director` sobre el mismo sitio. Documentar el resultado (score,
BLOCK/PASS) tal como se hizo para Vice en el spec de referencia.

- [x] **Step 3: Cerrar el spec** <!-- verificado 2026-09-03: el spec dice `Estado: implementado` y lleva `## Registro de implementacion` -->

En `docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md`:
- Cambiar `Estado: pendiente de plan` a `Estado: implementado`.
- Añadir al final una sección `## Registro de implementación` con: fecha, qué se desvió del
  prototipo (si algo se desvió en Task 4), resultados de los 5 gates de `measure-fondo-haz.py`, y
  el resultado de los gates `lidia`/`vera`.

- [!] **Step 4: `PROGRESS.json` a `completed`** <!-- NO SE HIZO. Verificado 2026-09-03: no hay ni un commit de PROGRESS.json entre el 18 y el 22-ago. Ya no puede hacerse: el fichero es uno por sesion y lo han reutilizado las sesiones posteriores (hoy guarda la fase A de Caelestia); reescribirlo con esta fase corromperia el estado vigente. Se deja escrito en vez de ticado en falso. -->

Marcar todos los items del checklist como `done: true`, `status: "completed"`,
`completedAt` con timestamp ISO.

- [x] **Step 5: Commit final** <!-- verificado 2026-09-03: el cierre del spec esta commiteado en main -->

```bash
git add docs/superpowers/specs/2026-08-19-hyprland-fondo-haz-design.md PROGRESS.json
git commit -m "docs(hyprland): cerrar el spec del haz al mando como implementado

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WiBaPiySGgkVMJTBGT2UMp"
```

---

## Self-Review Notes

- **Cobertura del spec:** las 6 correcciones del haz (canto asimétrico, sale a sangre, caída por
  eje, corte en frontera, derrame, materia) están todas en el shader de Task 1, con sus
  comentarios explicativos portados del prototipo. El techo (46, al final) → Task 1. El grano en
  píxeles CSS → Task 1 (`carbon()`). Responsive por `vertical` → Task 1. `uCreditsEntry` dinámico
  → Task 1 (`mountHyprEmber`). `prefers-reduced-motion` → ya resuelto por `shaderBackground.ts`,
  verificado en Task 4/Task 3 del arnés. Los 5 números de aceptación → Task 3 (arnés) + Task 4
  (ejecución). Los dos gates de QA → Task 5.
- **Fuera de alcance respetado:** ningún task toca `--haze`, `shaderBackground.ts`, `viceInk.ts`,
  ni la mención a `hyprGradient.ts` en `CLAUDE.md` (deliberadamente fuera, va en un commit propio
  y ajeno a este plan).
- **Consistencia de tipos/nombres:** `mountHyprEmber(container: HTMLElement): BackgroundHandle` es
  la misma firma en Task 1 y en el consumidor (`src/themes/hyprland.ts`, sin cambios ahí salvo el
  comentario de Task 2). `DynamicUniforms` (`Record<string, () => number>`) es el tipo ya
  existente en `shaderBackground.ts`, no uno nuevo.
