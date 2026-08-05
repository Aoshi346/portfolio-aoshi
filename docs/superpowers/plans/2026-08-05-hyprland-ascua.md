# Ascua — plan de implementación del tema Hyprland

> **Para quien ejecute esto:** SUB-SKILL OBLIGATORIA: `superpowers:subagent-driven-development`
> (recomendada) o `superpowers:executing-plans`, tarea a tarea. Los pasos usan casillas
> (`- [ ]`) y se marcan **en el momento**, no en bloque al final
> (`.claude/rules/speckit-progress-tracking.md`).

**Objetivo:** convertir el tema Hyprland, hoy un esqueleto de 12 tokens sin coreografía, en un
tema propio con la dirección "Ascua": luz emisiva de canto duro sobre negro con sesgo rojo,
organizada con los mismos dispositivos editoriales que Vice pero en material opuesto.

**Arquitectura:** un solo DOM para los tres temas, como ya hace el proyecto. Hyprland no
ramifica en TypeScript salvo en las puertas de `main.ts`; todo su aspecto vive en
`:root[data-theme="hyprland"] …` dentro de `themes.css`. Se le añade un módulo de coreografía
propio cargado en diferido y un fondo propio, ambos con el contrato `destroy()` que ya usan
todos los módulos de tema.

**Stack:** Vite 8 · TypeScript ~6 estricto · Tailwind 4 · GSAP 3 · Lenis · WebGL crudo. Sin
Three.js, sin framework.

**Prototipo de referencia:** `.superpowers/brainstorm/689488-1785939513/content/hyprland-v5-canto.html`,
tonalidad `ascua`. **Está aprobado y medido** — los números de contraste y las curvas de
easing salen de ahí, no se reinventan.

**Spec:** `docs/superpowers/specs/2026-08-05-hyprland-ascua-design.md`

## Restricciones globales

Aplican a **todas** las tareas:

- **Vice no se toca.** Ni sus bloques en `themes.css`, ni `vice.choreography.ts`, ni
  `viceCursor.ts`, ni `scrollRail.ts`, ni `introLeader.ts`, ni `cinemaChrome.ts`. Está cerrado
  en `0aee0af`.
- **Caelestia debe renderizar idéntico** antes y después. Lo único que se le hace es sacarlo de
  un selector compartido, copiando sus reglas tal cual a un bloque propio.
- **`src/backgrounds/shaderBackground.ts` no se modifica.** Lo comparte Vice.
- **Nunca `gsap.from`.** `fromTo` con los dos extremos escritos a mano, y `Array.from(...)`
  para colecciones vivas.
- **Nada de `any`.** `unknown` + guards. `strict` está activo.
- **Sin `console.log`.** Sólo `console.error` justificado.
- **Sin monoespaciada en el tema.** Es la señal de "herramienta de desarrollador" que se está
  evitando. `--font-mono` se sobrescribe a la cara de texto, como hace Vice.
- **Radio 0 en todo el tema salvo la navegación.**
- **Todo gesto degrada con `prefers-reduced-motion`.**
- **Un commit por tarea**, en la rama `design/hyprland-ascua`.
- **Verificar siempre con `?theme=hyprland`** — el tema se sortea por visita.
- **Playwright:** el chromium propio **no está descargado en esta máquina**. Lanzar con
  `executable_path="/usr/bin/google-chrome"`. `chromium-browser` no existe.

### Curvas y tiempos (valores exactos del prototipo)

```
--slow: cubic-bezier(.16,.84,.28,1)    /* atmosférico, 900ms */
--hard: cubic-bezier(.7,0,.2,1)        /* cortes, 400-500ms, sin rebote */
```

### Paleta Ascua (valores exactos)

```
--void #0b0404   --l1 #ff5a34   --l2 #e01d3c   --l3 #ffa03c
--text #ffeae6   --haze #b18c86  --rule #3d1c1c  --catch #ffd9cc
```

---

## Ficheros

| Fichero | Responsabilidad |
|---|---|
| `src/themes/themes.css` | Bloque `:root[data-theme="hyprland"]`: tokens, escala, dispositivos. Bloques de Vice y Caelestia intactos. |
| `src/themes/hyprland.ts` | Descriptor: `fontHref`, `themeColor`, `motion`, `choreography`, `mountBackground`. |
| `index.html` | Entrada `hyprland` del mapa `fontHrefs`. Cambia junto a `hyprland.ts`. |
| `src/backgrounds/hyprEmber.ts` | **Nuevo.** El campo y el haz. Sustituye a `hyprGradient.ts`. |
| `src/backgrounds/hyprGradient.ts` | **Se borra** al final de la tarea 3. |
| `src/themes/hypr.choreography.ts` | **Nuevo.** Gestos propios. Sin código compartido con Vice. |
| `src/main.ts` | Puerta `theme.id === "hyprland"` para el encendido, y su `destroy()` en `pagehide`. |
| `src/components/hyprIgnition.ts` | **Nuevo.** El encendido (equivalente a la cortinilla). |
| `scripts/verify.py` | Partir el marcador 2 de `check_theme_identity`; añadir marcadores propios de Hyprland. |

---

### Tarea 1: Tokens, tipografía y escala

**Ficheros:**
- Modificar: `src/themes/themes.css:1084-1107` (bloque de tokens de Hyprland)
- Modificar: `src/themes/hyprland.ts`
- Modificar: `index.html` (mapa `fontHrefs`, entrada `hyprland`)

**Interfaces:**
- Produce: los custom properties `--color-ink`, `--color-paper`, `--color-accent`,
  `--color-accent-2`, `--color-line`, `--l1`, `--l2`, `--l3`, `--catch`, `--rule`, `--haze`,
  `--slow`, `--hard`, `--t-1`…`--t-10`, `--font-display`, `--font-body`, `--font-said`,
  `--font-mono`, `--display-weight`, `--display-tracking`, `--display-leading`, `--radius-card`,
  `--nav-dim`, `--nav-dim-soft`, `--bg-fallback`. Todas las tareas siguientes los consumen.

- [x] **Paso 1: Sustituir el bloque de tokens**

Reemplazar íntegro `:root[data-theme="hyprland"] { … }` en `src/themes/themes.css:1084-1107` por:

```css
/* ----------------------------------------------------------------- Hyprland */
/*
  Ascua. El tema es luz EMISIVA sobre negro con sesgo rojo, de canto duro.
  Se eligio frente a Sodio (ambar) porque Vice ya es ambar miel #ffd166 sobre
  tinta purpura #150726 y el rojo no le roza por ningun lado.
  Detalle y descartes: docs/superpowers/specs/2026-08-05-hyprland-ascua-design.md
*/
:root[data-theme="hyprland"] {
  --color-ink: #0b0404;
  --color-paper: #ffeae6;
  --color-accent: #ff5a34;
  --color-accent-2: #e01d3c;
  --color-line: #3d1c1c;

  /* las tres luces y el tono que recoge el blanco del display */
  --l1: #ff5a34;
  --l2: #e01d3c;
  --l3: #ffa03c;
  --catch: #ffd9cc;
  --rule: #3d1c1c;
  --haze: #b18c86;

  /* Medir contra ESTE fondo antes de cerrar la tarea 8. Heredar el 55% de
     Vice fue el error del tema anterior: una opacidad se calibra contra un
     scrim concreto. */
  --nav-dim: 58%;
  --nav-dim-soft: 52%;

  /* Escala cerrada: los MISMOS diez pasos que Vice (base 16, razon 1,333).
     Espejar el sistema numerico es parte de organizarse como Vice. */
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

  --slow: cubic-bezier(0.16, 0.84, 0.28, 1);
  --hard: cubic-bezier(0.7, 0, 0.2, 1);

  --font-display: "Bricolage Grotesque", system-ui, sans-serif;
  --font-body: "Instrument Sans", system-ui, sans-serif;
  /* Reservada a UN solo trabajo: lo hablado, las frases en primera persona.
     Es el equivalente de Pathway Gothic One en Vice, que solo aparece en lo
     acreditado. */
  --font-said: "Instrument Serif", Georgia, serif;
  /* Red de seguridad, igual que en Vice: sin esto las utilidades `font-mono`
     de Tailwind filtran `ui-monospace`, y la monoespaciada es justo el tic que
     hacia que el tema se leyera como una herramienta de desarrollador. */
  --font-mono: "Instrument Sans", system-ui, sans-serif;

  --radius-card: 0px;
  --display-tracking: -0.032em;
  --display-weight: 600;
  --display-transform: none;
  --display-leading: 0.94;
  --bg-fallback: radial-gradient(120% 90% at 52% 26%, #3a1008 0%, #150605 46%, #0b0404 100%);
}
```

- [x] **Paso 2: Actualizar el descriptor del tema**

En `src/themes/hyprland.ts`, sustituir el objeto entero por:

```ts
import type { Theme } from "./types";

/** Ascua: luz emisiva de canto duro sobre negro con sesgo rojo. */
export const hyprlandTheme: Theme = {
  id: "hyprland",
  label: "Hyprland",
  themeColor: "#0b0404",
  fontHref:
    "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Instrument+Sans:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap",
  motion: { style: "snap", ease: "power3.out", duration: 0.9, stagger: 0.07 },
  async mountBackground(container) {
    const { mountHyprEmber } = await import("../backgrounds/hyprEmber");
    return mountHyprEmber(container);
  },
};
```

> `mountHyprEmber` no existe todavía: lo crea la tarea 3. Hasta entonces `npm run build` falla
> a propósito. Si prefieres commits verdes uno a uno, deja el import apuntando a
> `hyprGradient` en esta tarea y cámbialo en la tarea 3, paso 4.

- [x] **Paso 3: Sincronizar el mapa de fuentes de `index.html`**

En el `<script>` del `<head>`, sustituir la entrada `hyprland` de `fontHrefs` por la **misma
cadena literal** del paso 2. El fichero avisa de que la duplicación es deliberada: una
desincronización degrada a la vía lenta en silencio, sin error.

Y actualizar `<meta name="theme-color" content="#05070a" />` **no** — ese valor lo reescribe
`applyTheme()` en tiempo de ejecución desde `theme.themeColor`. Dejarlo como está.

- [x] **Paso 4: Comprobar que las tres fuentes existen antes de seguir**

```bash
for f in "Bricolage+Grotesque:opsz,wght@12..96,400..800" "Instrument+Sans:wght@400;500;600" "Instrument+Serif:ital@0;1"; do
  echo "$(curl -s -o /dev/null -w '%{http_code}' -A 'Mozilla/5.0' "https://fonts.googleapis.com/css2?family=$f&display=swap")  $f"
done
```

Esperado: `200` en las tres.

- [x] **Paso 5: Verificar que Vice y Caelestia no se han movido**

```bash
git diff --stat src/themes/themes.css
```

Esperado: sólo el rango del bloque de Hyprland. Si aparece cualquier línea de los bloques
`vice` o `caelestia`, revertir y rehacer.

- [x] **Paso 6: Commit**

```bash
git add src/themes/themes.css src/themes/hyprland.ts index.html
git commit -m "feat(hyprland): tokens, tipografia y escala de Ascua"
```

---

### Tarea 2: Escenas a sangre, display, lo hablado y el bloque de afirmación/prueba

**Ficheros:**
- Modificar: `src/themes/themes.css` (añadir bloque de dispositivos de Hyprland tras sus tokens)

**Interfaces:**
- Consume: los tokens de la tarea 1.
- Produce: las clases de tema `.hypr-cut`, `.hypr-up`, `.hypr-rule`, y el tratamiento de
  `.hero`, `.hero-kick`, `.display-xl`, `.display-lg`, `.lead`, `.hero-corner`. La tarea 7
  anima exactamente esos tres nombres de clase.

- [x] **Paso 1: Escribir las reglas de escena y tipografía**

Añadir en `src/themes/themes.css`, después del bloque de tokens de Hyprland:

```css
/* Escenas a sangre: el padding lateral es del tema, no de la maqueta comun. */
:root[data-theme="hyprland"] [data-scene] {
  padding-top: 15vh;
  padding-bottom: 17vh;
  padding-left: 7vw;
  padding-right: 7vw;
}

:root[data-theme="hyprland"] .hero {
  align-items: flex-start;
  text-align: left;
}

:root[data-theme="hyprland"] .hero-kick {
  font-family: var(--font-body);
  font-size: var(--t-1);
  font-weight: 600;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--haze);
}

/*
  LA FIRMA: el display es blanco que RECOGE color, no texto en degradado.
  La saturacion se mantiene baja a proposito — un arcoiris en el titular es
  el tic que hacia que el tema se leyera como generado.
  El degradado va anclado a la pantalla (`fixed`) para que al desplazarte la
  luz pase POR DENTRO de las palabras en vez de viajar con ellas.
  Medido en el prototipo: 14,4:1 sobre el campo.
*/
:root[data-theme="hyprland"] .display-xl,
:root[data-theme="hyprland"] .display-lg,
:root[data-theme="hyprland"] .contacto-title,
:root[data-theme="hyprland"] .about-name {
  font-family: var(--font-display);
  font-weight: var(--display-weight);
  letter-spacing: var(--display-tracking);
  line-height: var(--display-leading);
  text-transform: none;
  background: radial-gradient(
      64vw 64vw at var(--bx, 52%) var(--by, 30%),
      #ffffff 0%,
      var(--catch) 44%,
      color-mix(in oklab, var(--catch) 70%, var(--l2)) 100%
    )
    fixed;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

:root[data-theme="hyprland"] .display-xl,
:root[data-theme="hyprland"] .contacto-title {
  font-size: clamp(var(--t-6), 8.2vw, var(--t-9));
}
:root[data-theme="hyprland"] .display-lg,
:root[data-theme="hyprland"] .about-name {
  font-size: clamp(var(--t-5), 5.2vw, var(--t-7));
}

/* Lo hablado. Unico gesto de calidez conseguido por FORMA, no por color. */
:root[data-theme="hyprland"] .lead,
:root[data-theme="hyprland"] .contacto-lead {
  font-family: var(--font-said);
  font-style: italic;
  font-size: clamp(var(--t-3), 2.2vw, var(--t-4));
  line-height: 1.3;
  font-weight: 400;
  color: color-mix(in oklab, var(--color-paper) 84%, transparent);
}

/* El pie del hero: filete, no caja. */
:root[data-theme="hyprland"] .hero-corner {
  border-top: 1px solid var(--rule);
  padding-top: 1rem;
  font-size: var(--t-1);
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--haze);
}
:root[data-theme="hyprland"] .hero-mail {
  color: var(--haze);
  transition: color 0.3s var(--slow);
}
:root[data-theme="hyprland"] .hero-mail:hover,
:root[data-theme="hyprland"] .hero-mail:focus-visible {
  color: var(--l1);
}

/*
  Gramatica de revelado. Tres gestos, no uno repetido: el defecto de las
  propuestas descartadas era que TODO iba lento y suave, que es un ajuste
  global y no una coreografia. Los cortes son rapidos y sin rebote.
*/
:root[data-theme="hyprland"] .hypr-cut {
  clip-path: inset(0 100% 0 0);
  transition: clip-path 0.42s var(--hard);
  transition-delay: var(--hypr-d, 0ms);
}
:root[data-theme="hyprland"] .is-lit .hypr-cut,
:root[data-theme="hyprland"] .hypr-cut.is-lit {
  clip-path: inset(0 0 0 0);
}
:root[data-theme="hyprland"] .hypr-up {
  opacity: 0;
  transform: translateY(14px);
  transition:
    opacity 0.9s var(--slow),
    transform 0.9s var(--slow);
  transition-delay: var(--hypr-d, 0ms);
}
:root[data-theme="hyprland"] .is-lit .hypr-up,
:root[data-theme="hyprland"] .hypr-up.is-lit {
  opacity: 1;
  transform: none;
}
:root[data-theme="hyprland"] .hypr-rule {
  transform: scaleY(0);
  transform-origin: top;
  transition: transform 0.4s var(--hard);
  transition-delay: var(--hypr-d, 0ms);
}
:root[data-theme="hyprland"] .is-lit .hypr-rule {
  transform: scaleY(1);
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .hypr-cut,
  :root[data-theme="hyprland"] .hypr-up,
  :root[data-theme="hyprland"] .hypr-rule {
    clip-path: none;
    opacity: 1;
    transform: none;
    transition: none;
  }
}

/*
  "QUIEN ES" — el bloque de afirmacion y prueba, en filas con filete.
  El DOM ya existe (`src/sections/about.ts`): `.about-pair` > `.about-claim` >
  `.about-claim-in`, y `.about-proof` > `.about-proof-in`. Vice lo maqueta como
  cartel de cine; aqui es una tabla editorial de dos columnas.

  El filete que se pinta al apuntar es el equivalente de las marcas de esquina
  de Vice: el dato que recibe atencion se marca, y se marca con un canto.
*/
:root[data-theme="hyprland"] .about-grid {
  grid-template-columns: 1fr;
}
:root[data-theme="hyprland"] .about-pairs {
  border-top: 1px solid var(--rule);
  margin-top: 6vh;
}
:root[data-theme="hyprland"] .about-pair {
  position: relative;
  display: grid;
  gap: 0.25rem 1.2rem;
  padding: 1.15rem 0;
  border-bottom: 1px solid var(--rule);
}
@media (min-width: 760px) {
  :root[data-theme="hyprland"] .about-pair {
    grid-template-columns: 0.9fr 1.1fr;
    align-items: baseline;
  }
}
:root[data-theme="hyprland"] .about-pair::before {
  content: "";
  position: absolute;
  left: 0;
  bottom: -1px;
  height: 1px;
  width: 0;
  background: var(--l1);
  transition: width 0.5s var(--hard);
}
:root[data-theme="hyprland"] .about-pair:hover::before,
:root[data-theme="hyprland"] .about-pair:focus-within::before {
  width: 100%;
}
:root[data-theme="hyprland"] .about-claim-in {
  font-family: var(--font-display);
  font-size: var(--t-3);
  font-weight: 500;
  letter-spacing: -0.015em;
  text-transform: none;
  color: var(--color-paper);
}
:root[data-theme="hyprland"] .about-proof-in {
  font-family: var(--font-body);
  font-size: var(--t-2);
  color: var(--haze);
}
:root[data-theme="hyprland"] .about-portrait {
  border-radius: 0;
}
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .about-pair::before {
    transition: none;
  }
}
```

- [x] **Paso 2: Levantar el dev server y mirar el hero**

```bash
npm run dev
```

Abrir `http://localhost:5173/?theme=hyprland`. Esperado: titular en caja baja ancha con relleno
claro, frase en itálica de serif, pie con filete. **Si el titular sale transparente e
invisible**, el `background-clip: text` no está aplicando — comprobar que no hay un `color`
posterior ganando la cascada.

- [x] **Paso 3: Captura de comprobación**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",
                          args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:5173/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(6000)
    pg.screenshot(path="/tmp/hypr-t2.png", full_page=False)
    print(pg.evaluate("""({
      display: getComputedStyle(document.querySelector('.display-xl')).fontFamily,
      lead: getComputedStyle(document.querySelector('.lead')).fontFamily,
      radius: getComputedStyle(document.querySelector('.hero-surface')).borderRadius
    })"""))
    b.close()
PY
```

Esperado: `display` contiene `Bricolage Grotesque`, `lead` contiene `Instrument Serif`,
`radius` es `0px`.

- [x] **Paso 4: Mirar también la escena "quién es"**

En el navegador, ir a la sección de about y comprobar: las filas de afirmación/prueba están en
dos columnas con filete entre ellas, y al pasar el ratón por una fila el filete inferior se
pinta de izquierda a derecha con corte duro. El retrato es cuadrado, sin redondear.

- [x] **Paso 5: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(hyprland): escenas a sangre, display de luz y bloque de afirmacion"
```

---

### Tarea 3: El campo y el haz

**Ficheros:**
- Crear: `src/backgrounds/hyprEmber.ts`
- Borrar: `src/backgrounds/hyprGradient.ts`
- Modificar: `src/themes/hyprland.ts` (si en la tarea 1 se dejó apuntando a `hyprGradient`)

**Interfaces:**
- Consume: `mountShaderBackground(container, fragmentShader, dynamicUniforms?)` y el tipo
  `BackgroundHandle` de `src/backgrounds/shaderBackground.ts`.
- Produce: `export function mountHyprEmber(container: HTMLElement): BackgroundHandle`.

- [x] **Paso 1: Leer el contrato antes de escribir nada**

```bash
sed -n '1,60p' src/backgrounds/shaderBackground.ts
```

Anotar: qué uniforms inyecta siempre (`uTime`, `uResolution`), qué chunk de ruido prepende, y
la forma exacta del handle. **No modificar el fichero**: lo comparte Vice.

- [x] **Paso 2: Escribir el fondo**

Crear `src/backgrounds/hyprEmber.ts`:

```ts
import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * Ascua: el campo de brasa y el haz.
 *
 * Dos piezas, y la segunda es la que importa. El campo es emision suave
 * (halo anisotropo, elipse rotada, no un circulo). El HAZ es una cuna de
 * bordes NITIDOS que cruza en diagonal: es el gesto que rompe con lo blando,
 * y lo blando era justo lo que hacia que el tema se leyera como generado.
 *
 * El grano no es decorativo: sin el, un degradado de este tamano hace bandas
 * visibles sobre un campo casi negro.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  varying vec2 vUv;

  /* distancia con signo a una banda diagonal: el canto duro del haz */
  float beam(vec2 p, float ang, float halfWidth) {
    vec2 dir = vec2(cos(ang), sin(ang));
    vec2 n = vec2(-dir.y, dir.x);
    return halfWidth - abs(dot(p, n));
  }

  void main() {
    vec2 uv = vUv;
    float aspect = uResolution.x / max(uResolution.y, 1.0);
    vec2 p = (uv * 2.0 - 1.0) * vec2(aspect, 1.0);
    float t = uTime * 0.04;

    vec3 base  = vec3(0.043, 0.016, 0.016);   /* #0b0404 */
    vec3 ember = vec3(1.000, 0.353, 0.204);   /* #ff5a34 */
    vec3 crim  = vec3(0.878, 0.114, 0.235);   /* #e01d3c */
    vec3 amber = vec3(1.000, 0.627, 0.235);   /* #ffa03c */

    /* campo: halo anisotropo que respira, no una mancha centrada */
    vec2 c = vec2(-0.18 + sin(t * 0.7) * 0.12, 0.22 + cos(t * 0.5) * 0.08);
    vec2 q = (p - c) * vec2(0.62, 1.15);
    float glow = exp(-dot(q, q) * 1.25);
    vec3 col = base + mix(crim, ember, 0.5 + 0.5 * sin(t)) * glow * 0.85;

    /* segundo foco, mas frio y bajo, para que el campo no sea simetrico */
    vec2 q2 = (p - vec2(0.55, -0.42)) * vec2(0.9, 1.3);
    col += crim * exp(-dot(q2, q2) * 2.4) * 0.3;

    /* EL HAZ: canto duro. El smoothstep es de ~1,5 pixeles, no un degradado. */
    float px = 2.0 / uResolution.y;
    float ang = 1.28 + sin(t * 0.35) * 0.05;
    float d = beam(p - vec2(-0.45, 0.0), ang, 0.30);
    float edge = smoothstep(0.0, px * 1.5, d);
    float falloff = smoothstep(1.25, -0.35, p.y);
    col += mix(ember, amber, 0.5 + 0.5 * p.y) * edge * falloff * 0.20;

    /* vinetado y grano */
    col *= smoothstep(2.05, 0.30, length(p));
    col += (hash(uv * uResolution + t) - 0.5) * 0.030;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountHyprEmber(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
```

- [x] **Paso 3: Borrar el fondo viejo**

```bash
git rm src/backgrounds/hyprGradient.ts
grep -rn "hyprGradient" src/ scripts/ || echo "sin referencias colgando"
```

Esperado: `sin referencias colgando`. Si aparece alguna en `scripts/verify.py` o en un
comentario de `shaderBackground.ts`, actualizar **sólo el texto del comentario**.

- [x] **Paso 4: Confirmar el import en el descriptor**

`src/themes/hyprland.ts` debe importar `../backgrounds/hyprEmber` y llamar a `mountHyprEmber`.

- [x] **Paso 5: Verificar que Vice sigue pintando**

Esto es el punto de fallo real de esta tarea: `shaderBackground.ts` es compartido.

```bash
npm run build && npm run preview &
sleep 4
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",
                          args=["--no-sandbox", "--use-gl=swiftshader"])
    for tema in ("vice", "hyprland", "caelestia"):
        pg = b.new_page(viewport={"width": 1200, "height": 800})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://localhost:4173/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(8000)
        negro = pg.evaluate("""(() => {
          const c = document.querySelector('.bg-theme canvas');
          if (!c) return 'sin canvas';
          const g = c.getContext('webgl') || c.getContext('webgl2');
          return g ? 'canvas con contexto' : 'canvas sin contexto';
        })()""")
        print(tema, '->', negro, '| errores:', errs or 'ninguno')
        pg.screenshot(path=f"/tmp/bg-{tema}.png")
        pg.close()
    b.close()
PY
```

Esperado: los tres con `canvas con contexto` y sin errores. **Mirar las tres capturas**: Vice
tiene que seguir siendo su serigrafía de tinta.

- [x] **Paso 6: Commit**

```bash
git add src/backgrounds/hyprEmber.ts src/themes/hyprland.ts
git rm --cached src/backgrounds/hyprGradient.ts 2>/dev/null || true
git commit -m "feat(hyprland): fondo de brasa con haz de canto duro"
```

---

### Tarea 4: La tira de exposición (obra)

**Ficheros:**
- Modificar: `src/themes/themes.css` (bloque de Hyprland)

**Interfaces:**
- Consume: el DOM que ya produce `src/sections/obra/projectScene.ts` — `section.scene[data-scene="obra"]`
  con `span[data-ord]`, `div.scene-surface`, `p.hero-kick`, `h2.display-lg`, `p.lead`,
  `dl.obra-meta`.
- Produce: la clase de estado `.is-open` sobre `[data-scene="obra"]`, que la tarea 7 conmuta.

- [x] **Paso 1: Escribir la tira**

Añadir al bloque de Hyprland en `src/themes/themes.css`:

```css
/*
  LA TIRA DE EXPOSICION — el dispositivo de la obra.
  Equivale al carril horizontal de Vice (la bobina), pero aqui no hay
  tarjetas: es una banda a sangre partida en escalones de la misma luz, sin
  radio, con filete de 1px entre ellos y exposicion creciente. El apuntado se
  abre y los demas se comprimen.

  NADA de scroll-snap. Medido con A/B en el prototipo: con snap, fijar
  `scrollLeft = 400` aterriza en 477 porque los anclajes caen cada ~477px, asi
  que cada incremento de rueda volvia al origen; el carril se quedaba clavado
  en 34 de 954 y ademas bloqueaba la pagina.
*/
@media (min-width: 821px) {
  /* `.obra-rail` > `.obra-track` los crea `src/main.ts:98-103` para los TRES
     temas, no la coreografia de Vice: el contenedor existe siempre y el padre
     directo de las escenas es `.obra-track`. */
  :root[data-theme="hyprland"] .obra-rail {
    overflow: hidden;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
  }
  :root[data-theme="hyprland"] .obra-track {
    display: flex;
    width: 100%;
    transform: none;
  }

  :root[data-theme="hyprland"] .obra-track > [data-scene="obra"] {
    position: relative;
    flex: 1 1 0;
    min-width: 0;
    min-height: 56vh;
    padding: 1.7rem 1.5rem;
    border-right: 1px solid var(--rule);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: linear-gradient(180deg, rgba(26, 10, 10, 0.2), rgba(26, 10, 10, 0.65));
    transition:
      flex-grow 0.5s var(--hard),
      background 0.5s var(--slow);
  }
  :root[data-theme="hyprland"] [data-scene="obra"]:last-child {
    border-right: 0;
  }

  /* el escalon: cada uno recibe mas luz que el anterior */
  :root[data-theme="hyprland"] [data-scene="obra"]::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background: linear-gradient(
      180deg,
      color-mix(in oklab, var(--l1) calc(var(--hypr-e, 16) * 1%), transparent),
      transparent 62%
    );
  }

  :root[data-theme="hyprland"] [data-scene="obra"].is-open {
    flex-grow: 3.1;
    background: linear-gradient(180deg, rgba(26, 10, 10, 0.35), rgba(26, 10, 10, 0.8));
  }
  :root[data-theme="hyprland"] [data-scene="obra"].is-open::after {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--l1);
    box-shadow: 0 0 22px var(--l1);
  }

  /* el pliegue: solo el abierto muestra su contenido. En un panel comprimido
     el texto se cortaba a media palabra. */
  :root[data-theme="hyprland"] [data-scene="obra"] .lead,
  :root[data-theme="hyprland"] [data-scene="obra"] .obra-meta,
  :root[data-theme="hyprland"] [data-scene="obra"] [data-gallery] {
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.38s var(--slow) 0.1s;
  }
  :root[data-theme="hyprland"] [data-scene="obra"].is-open .lead,
  :root[data-theme="hyprland"] [data-scene="obra"].is-open .obra-meta,
  :root[data-theme="hyprland"] [data-scene="obra"].is-open [data-gallery] {
    opacity: 1;
    pointer-events: auto;
  }

  /* el ordinal, grande y al fondo: el eco del de Vice */
  :root[data-theme="hyprland"] [data-scene="obra"] [data-ord] {
    position: absolute;
    right: 1rem;
    bottom: 0.2rem;
    font-family: var(--font-display);
    font-size: var(--t-8);
    font-weight: 700;
    line-height: 1;
    color: color-mix(in oklab, var(--color-paper) 7%, transparent);
  }
}

/* Bajo 821px o con movimiento reducido: pila vertical, como el resto de temas.
   Mismo contrato de breakpoint que usa la coreografia (tarea 7). */
@media (max-width: 820px), (prefers-reduced-motion: reduce) {
  :root[data-theme="hyprland"] .obra-rail {
    display: block;
  }
  :root[data-theme="hyprland"] [data-scene="obra"] {
    border-bottom: 1px solid var(--rule);
  }
  :root[data-theme="hyprland"] [data-scene="obra"] .lead,
  :root[data-theme="hyprland"] [data-scene="obra"] .obra-meta,
  :root[data-theme="hyprland"] [data-scene="obra"] [data-gallery] {
    opacity: 1;
    pointer-events: auto;
  }
}
```

- [x] **Paso 2: Confirmar que no se ha tocado el bloque de Vice**

```bash
git diff src/themes/themes.css | grep -c 'data-theme="vice"'
```

Esperado: `0`. Vice tiene sus propias reglas de `.obra-track` en `themes.css:1741-1752` y son
las que mueven su bobina; si aparecen en el diff, se ha editado su bloque por error.

- [x] **Paso 3: Verificar en el navegador que no se corta texto**

Con `npm run dev` y `?theme=hyprland`, comprobar en la sección de obra:
- los cinco paneles caben sin barra de scroll horizontal en 1440px;
- el panel abierto muestra lead y meta, los cerrados no;
- ningún texto queda cortado a media palabra.

- [x] **Paso 4: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(hyprland): la tira de exposicion sustituye al carril de tarjetas"
```

---

### Tarea 5: El reparto y las bandas de contacto

**Ficheros:**
- Modificar: `src/themes/themes.css:2403-2445` (partir el bloque compartido con Caelestia)
- Modificar: `src/themes/themes.css` (bloque de Hyprland: reparto y bandas)

**Interfaces:**
- Consume: el DOM de `src/components/credits.ts` (`.credits-grid`, `.credits-list`,
  `.credit`, `.credit-role`, `.credit-name`, `.credit-group-label`) y el de
  `src/sections/contacto.ts` (`.contacto-band`, `.contacto-bars`, `.contacto-bar-label`,
  `.contacto-bar-mark`, `.contacto-bar-value`, `.contacto-estado`).

- [x] **Paso 1: Guardar la referencia de Caelestia ANTES de tocar nada**

```bash
npm run build && npm run preview &
sleep 4
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",
                          args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4173/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(7000)
    pg.evaluate("document.querySelector('[data-scene=\"credits\"]').scrollIntoView()")
    pg.wait_for_timeout(2500)
    pg.screenshot(path="/tmp/caelestia-creditos-ANTES.png")
    b.close()
PY
```

- [x] **Paso 2: Partir el bloque compartido**

En `src/themes/themes.css:2403-2445`, cada regla tiene hoy dos selectores
(`:root[data-theme="hyprland"] .x, :root[data-theme="caelestia"] .x`). **Borrar de cada una el
selector de `hyprland`**, dejando el de `caelestia` intacto. No reescribir sus declaraciones:
copiar el bloque tal cual y quitar selectores es lo único que garantiza render idéntico.

- [x] **Paso 3: Escribir el reparto y las bandas de Hyprland**

Añadir al bloque de Hyprland:

```css
/*
  EL REPARTO — equivale al cartel de reparto de Vice: el rol aparece UNA vez
  como rotulo y los nombres fluyen como prosa atribuida, no como rejilla de
  fichas. Aqui el rol va a la izquierda en su columna y los nombres a la
  derecha, separados por filete.
*/
:root[data-theme="hyprland"] .credits-grid {
  grid-template-columns: 1fr;
  max-width: 1000px;
}
:root[data-theme="hyprland"] .credits-list {
  display: block;
}
:root[data-theme="hyprland"] .credit-group-label {
  font-family: var(--font-body);
  font-size: var(--t-1);
  font-weight: 600;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: var(--haze);
}
:root[data-theme="hyprland"] .credit {
  display: inline;
  width: auto;
  padding: 0;
  border: 0;
  background: none;
  font-family: var(--font-display);
  font-size: clamp(var(--t-3), 2.2vw, var(--t-4));
  font-weight: 500;
  letter-spacing: -0.014em;
  line-height: 1.3;
  color: var(--color-paper);
  transition: color 0.3s var(--slow);
}
:root[data-theme="hyprland"] .credit:hover,
:root[data-theme="hyprland"] .credit:focus-visible,
:root[data-theme="hyprland"] .credit.is-active {
  color: var(--l1);
  background: none;
  border: 0;
}
:root[data-theme="hyprland"] .credit:not(:last-child)::after {
  content: "  /  ";
  color: var(--rule);
}
/* El rol se muestra una vez como cabecera de grupo, no por fila. */
:root[data-theme="hyprland"] .credit-role {
  display: none;
}

/*
  LAS BANDAS — equivale a la carta de ajuste de Vice: el cierre. Alli eran
  geles de color; aqui son bandas a sangre con filete, rotulo a la izquierda y
  valor grande a la derecha. Al apuntar, la luz inunda la banda de izquierda a
  derecha con un corte duro.
*/
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
  padding: 1.4rem 7vw;
  border-bottom: 1px solid var(--rule);
  background: none;
  overflow: hidden;
}
:root[data-theme="hyprland"] [class*="contacto-bar--"]::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, color-mix(in oklab, var(--l1) 20%, transparent), transparent 70%);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.45s var(--hard);
}
:root[data-theme="hyprland"] [class*="contacto-bar--"]:hover::before,
:root[data-theme="hyprland"] [class*="contacto-bar--"]:focus-visible::before {
  transform: scaleX(1);
}
:root[data-theme="hyprland"] .contacto-bar-label {
  writing-mode: horizontal-tb;
  transform: none;
  width: 9rem;
  flex: 0 0 auto;
  font-size: var(--t-1);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--haze);
  position: relative;
  z-index: 1;
}
:root[data-theme="hyprland"] .contacto-bar-value {
  font-family: var(--font-display);
  font-weight: 500;
  font-size: clamp(var(--t-3), 2.4vw, var(--t-4));
  letter-spacing: -0.02em;
  position: relative;
  z-index: 1;
}
:root[data-theme="hyprland"] .contacto-bar-mark {
  margin-left: auto;
  position: relative;
  z-index: 1;
  background: var(--l1);
}
```

- [x] **Paso 4: Comprobar que Caelestia no se ha movido ni un píxel**

Repetir el script del paso 1 guardando en `/tmp/caelestia-creditos-DESPUES.png` y comparar:

```bash
python3 - <<'PY'
from PIL import Image, ImageChops
a = Image.open("/tmp/caelestia-creditos-ANTES.png").convert("RGB")
b = Image.open("/tmp/caelestia-creditos-DESPUES.png").convert("RGB")
if a.size != b.size:
    print("FALLO: tamanos distintos", a.size, b.size)
else:
    diff = ImageChops.difference(a, b)
    caja = diff.getbbox()
    print("identico" if caja is None else f"FALLO: difieren en {caja}")
PY
```

Esperado: `identico`. Si difiere, se ha tocado una declaración de Caelestia y hay que revertir
el paso 2 y rehacerlo quitando **sólo** selectores.

> El fondo de Caelestia es generativo y anima, así que una diferencia en la zona del canvas es
> esperable. Si `getbbox()` no es `None`, comprobar que la caja cae **fuera** del bloque de
> créditos antes de darlo por bueno.

- [x] **Paso 5: Commit**

```bash
git add src/themes/themes.css
git commit -m "feat(hyprland): reparto y bandas de contacto propias, Caelestia sale del bloque compartido"
```

---

### Tarea 6: El encendido

**Ficheros:**
- Crear: `src/components/hyprIgnition.ts`
- Modificar: `src/main.ts`

**Interfaces:**
- Produce: `export function mountHyprIgnition(host: HTMLElement): { destroy: () => void }`.
- Consume: `el()` de `src/utils/dom.ts`.

- [x] **Paso 1: Leer el helper de DOM que ya existe**

```bash
sed -n '1,40p' src/utils/dom.ts
```

Usar `el()` — no reescribir creación de nodos a mano (`.claude/rules/code-style.md`).

- [x] **Paso 2: Escribir el módulo**

Crear `src/components/hyprIgnition.ts`:

```ts
import { el } from "../utils/dom";

/**
 * El encendido: equivale a la cortinilla de academia de Vice, en el material
 * de este tema. La pagina arranca a oscuras y la luz prende una vez.
 *
 * No hay cuenta atras ni iris: eso es de Vice. Aqui es un unico corte de
 * 1,1s con la curva dura del tema, y el velo se autodestruye al terminar
 * para no dejar un nodo a pantalla completa capturando eventos.
 */
export interface IgnitionHandle {
  destroy: () => void;
}

export function mountHyprIgnition(host: HTMLElement): IgnitionHandle {
  const veil = el("div", { class: "hypr-ignition", "aria-hidden": "true" });
  host.appendChild(veil);

  let done = false;
  const finish = (): void => {
    if (done) return;
    done = true;
    veil.remove();
  };

  veil.addEventListener("animationend", finish, { once: true });
  // Red: si la animacion no llega a disparar (pestana en segundo plano al
  // cargar, por ejemplo), el velo se retira igualmente.
  const fallback = window.setTimeout(finish, 2000);

  return {
    destroy(): void {
      window.clearTimeout(fallback);
      finish();
    },
  };
}
```

- [x] **Paso 3: Añadir su CSS al bloque de Hyprland**

En `src/themes/themes.css`:

```css
:root[data-theme="hyprland"] .hypr-ignition {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: var(--color-ink);
  pointer-events: none;
  animation: hypr-ignite 1.1s var(--hard) forwards;
}
@keyframes hypr-ignite {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
    visibility: hidden;
  }
}
```

- [x] **Paso 4: Engancharlo en `main.ts`**

Junto a la puerta que ya existe para el leader de Vice (`src/main.ts:51`), añadir la de
Hyprland, siguiendo el mismo patrón de import diferido:

```ts
let ignitionHandle: { destroy: () => void } | null = null;
if (!prefersReducedMotion && theme.id === "hyprland") {
  void import("./components/hyprIgnition").then(({ mountHyprIgnition }) => {
    ignitionHandle = mountHyprIgnition(app);
  });
}
```

Y en el listener de `pagehide` (`src/main.ts:197`), junto a `backgroundHandle?.destroy()`,
añadir `ignitionHandle?.destroy();`.

- [x] **Paso 5: Comprobar que no queda un velo capturando clics**

Con `npm run dev` y `?theme=hyprland`, esperar 3s y ejecutar en la consola del navegador:

```js
document.querySelectorAll(".hypr-ignition").length;
```

Esperado: `0`. Y comprobar que los enlaces del pie del hero se pueden pulsar.

- [x] **Paso 6: Commit**

```bash
git add src/components/hyprIgnition.ts src/main.ts src/themes/themes.css
git commit -m "feat(hyprland): el encendido, con velo que se autodestruye"
```

---

### Tarea 7: Coreografía propia

**Ficheros:**
- Crear: `src/themes/hypr.choreography.ts`
- Modificar: `src/themes/hyprland.ts` (añadir la clave `choreography`)

**Interfaces:**
- Consume: el tipo `Choreography` de `src/themes/choreography.ts`, y las clases
  `.hypr-cut`, `.hypr-up`, `.hypr-rule`, `.is-lit`, `.is-open` de las tareas 2 y 4.
- Produce: `export const hyprChoreography: Choreography`.

- [x] **Paso 1: Leer el contrato de coreografía y el de Vice como referencia de forma**

```bash
cat src/themes/choreography.ts
grep -n "export const viceChoreography" -A 12 src/themes/vice.choreography.ts
```

**No copiar código de Vice.** Sólo se mira la forma del export y cómo mata sus triggers.

- [x] **Paso 2: Escribir la coreografía**

Crear `src/themes/hypr.choreography.ts`:

```ts
import type { Choreography } from "./choreography";

const ID = "hypr";

/**
 * Ascua: tres gestos, no uno repetido a distintas escalas.
 *
 * El defecto de las propuestas descartadas era que TODO iba lento y suave —
 * eso es un ajuste global, no una coreografia. Aqui lo atmosferico va a 900ms
 * con curva blanda y los cortes a 400ms con `--hard`, sin rebote. La
 * diferencia de tiempos es lo que hace que el movimiento parezca decidido.
 *
 * El revelado NO se fia solo del observador de interseccion: con scroll
 * rapido se pierden callbacks y el contenido se queda invisible para siempre.
 * Va con red por posicion, que es justo lo que hace ScrollTrigger.
 */
export const hyprChoreography: Choreography = ({ gsap, ScrollTrigger, root }) => {
  ScrollTrigger.getAll()
    .filter((t) => typeof t.vars.id === "string" && t.vars.id.startsWith(ID))
    .forEach((t) => t.kill());

  const scenes = Array.from(root.querySelectorAll<HTMLElement>("[data-scene]"));

  // Gesto 0 — repartir la gramatica.
  // El DOM lo construyen las secciones, que son COMPARTIDAS por los tres
  // temas y no pueden llevar clases de uno solo. Asi que las reparte aqui el
  // tema, junto con su escalonado: sin este paso, `.hypr-cut` y compania
  // existirian en la hoja sin aplicarse a nada, y `--hypr-d` se quedaria a 0
  // dejando todas las entradas simultaneas.
  const RECETA: ReadonlyArray<readonly [string, string]> = [
    [".hero-kick", "hypr-cut"],
    [".display-xl, .display-lg, .contacto-title, .about-name", "hypr-up"],
    [".lead, .contacto-lead", "hypr-up"],
    [".about-pair", "hypr-up"],
    [".contacto-estado", "hypr-up"],
    ['[class*="contacto-bar--"]', "hypr-up"],
  ];

  scenes.forEach((scene) => {
    let n = 0;
    RECETA.forEach(([selector, clase]) => {
      Array.from(scene.querySelectorAll<HTMLElement>(selector)).forEach((node) => {
        if (node.classList.contains(clase)) return;
        node.classList.add(clase);
        // 70ms por pieza: el mismo escalonado que el prototipo aprobado.
        node.style.setProperty("--hypr-d", `${n * 70}ms`);
        n += 1;
      });
    });
  });

  // Gesto 1 — la escena se enciende. Las clases hacen el trabajo; GSAP solo
  // decide CUANDO, para que el CSS siga siendo la fuente de los tiempos.
  scenes.forEach((scene, i) => {
    ScrollTrigger.create({
      id: `${ID}-lit-${i}`,
      trigger: scene,
      start: "top 90%",
      once: true,
      onEnter: () => scene.classList.add("is-lit"),
    });
  });

  // Red: cualquier escena ya dentro del cuadro se enciende sin esperar a un
  // callback. Sin esto, un scroll rapido deja secciones en blanco.
  const net = (): void => {
    scenes.forEach((scene) => {
      const r = scene.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.9 && r.bottom > 0) scene.classList.add("is-lit");
    });
  };
  net();
  window.addEventListener("scroll", net, { passive: true });

  // Gesto 2 — la tira de exposicion. Solo en escritorio y sin movimiento
  // reducido: el mismo contrato de breakpoint que el CSS de la tarea 4.
  const mm = gsap.matchMedia();
  mm.add("(min-width: 821px) and (prefers-reduced-motion: no-preference)", () => {
    const obras = Array.from(root.querySelectorAll<HTMLElement>('[data-scene="obra"]'));
    if (obras.length === 0) return;

    obras.forEach((obra, i) => {
      obra.style.setProperty("--hypr-e", String(16 + i * 13));
      const open = (): void => {
        obras.forEach((o) => o.classList.toggle("is-open", o === obra));
      };
      obra.addEventListener("pointerenter", open);
      obra.addEventListener("focusin", open);
    });
    obras[0].classList.add("is-open");

    return () => {
      obras.forEach((o) => o.classList.remove("is-open"));
    };
  });

  // Gesto 3 — el titular lee la posicion de la luz, para que al desplazarte
  // la luz pase POR DENTRO de las palabras en vez de viajar con ellas.
  ScrollTrigger.create({
    id: `${ID}-light`,
    trigger: root,
    start: "top top",
    end: "bottom bottom",
    onUpdate: (self) => {
      const p = self.progress;
      root.style.setProperty("--bx", `${52 + Math.sin(p * Math.PI * 1.4) * 15}%`);
      root.style.setProperty("--by", `${26 + p * 32}%`);
    },
  });
};

export default hyprChoreography;
```

> Si `Choreography` no expone `root` como `HTMLElement` con esa forma, ajustar la firma a lo que
> declare `src/themes/choreography.ts` — ese fichero manda.

- [x] **Paso 3: Registrarla en el descriptor**

En `src/themes/hyprland.ts`, añadir dentro del objeto:

```ts
  async choreography() {
    const { hyprChoreography } = await import("./hypr.choreography");
    return hyprChoreography;
  },
```

- [x] **Paso 4: Verificar que no queda nada sin revelar tras un recorrido con rueda**

```bash
npm run build && npm run preview &
sleep 4
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",
                          args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4173/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(8000)
    pg.mouse.move(300, 450)
    # rueda de verdad, no scrollTo: con `scroll-behavior:smooth` los scrollTo
    # encadenados se interrumpen y la pagina nunca pinta las escenas de en medio.
    for _ in range(60):
        pg.mouse.wheel(0, 200)
        pg.wait_for_timeout(45)
    pg.wait_for_timeout(2500)
    print("sin encender:", pg.evaluate(
        "[...document.querySelectorAll('[data-scene]')].filter(s=>!s.classList.contains('is-lit')).map(s=>s.dataset.scene)"))
    print("scroll:", pg.evaluate("Math.round(scrollY)+'/'+(document.body.scrollHeight-innerHeight)"))
    b.close()
PY
```

Esperado: `sin encender: []` y el scroll llegando al final. Si el scroll se queda corto, la
tira está secuestrando la rueda: tiene que consumir su recorrido y **soltar**.

Y comprobar que el gesto 0 repartió de verdad la gramática — si esto sale a 0, las clases
están en la hoja sin aplicarse a nada y no se anima nada:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",
                          args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4173/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(9000)
    print(pg.evaluate("""({
      conGramatica: document.querySelectorAll('.hypr-cut,.hypr-up,.hypr-rule').length,
      conRetardo: [...document.querySelectorAll('.hypr-up')]
        .filter(e => e.style.getPropertyValue('--hypr-d') !== '').length
    })"""))
    b.close()
PY
```

Esperado: `conGramatica` bien por encima de 10, y `conRetardo` igual al número de `.hypr-up`.

- [x] **Paso 5: Verificar con movimiento reducido**

Repetir el script anterior añadiendo `reduced_motion="reduce"` al `new_page(...)`. Esperado:
todo visible desde el primer fotograma, la obra en pila vertical, sin `is-open`.

- [x] **Paso 6: Commit**

```bash
git add src/themes/hypr.choreography.ts src/themes/hyprland.ts
git commit -m "feat(hyprland): coreografia propia con contraste de tiempos"
```

---

### Tarea 8: El gate de identidad

**Ficheros:**
- Modificar: `scripts/verify.py:1159-1174` (marcador 2 de `check_theme_identity`)
- Modificar: `scripts/verify.py` (añadir marcadores propios de Hyprland)

**Interfaces:**
- Consume: la función `check(cond, etiqueta)` que ya existe en el arnés.

- [x] **Paso 1: Leer la función entera antes de tocarla**

```bash
sed -n '1066,1180p' scripts/verify.py
```

El docstring explica por qué existe cada marcador. **Ampliarlo, no vaciarlo**: el modo de fallo
que protege —una tarea que reescribe una sección compartida y rompe la identidad de otro tema—
ya ha ocurrido tres veces en este proyecto.

- [x] **Paso 2: Partir el marcador 2 en dos, uno por tema**

El bloque actual `if theme in ("hyprland", "caelestia"):` afirma píldoras horizontales con el
rol oculto. Ascua ya no es píldoras: es rol como cabecera y nombres fluyendo. Sustituirlo por:

```python
    if theme == "caelestia":
        credits_layout = page.evaluate("""(() => {
          const list = document.querySelector('.credits-list');
          const role = document.querySelector('.credit-role');
          if (!list) return null;
          const s = getComputedStyle(list);
          return {
            flexDirection: s.flexDirection,
            roleDisplay: role ? getComputedStyle(role).display : null,
          };
        })()""")
        check(
            credits_layout is not None and credits_layout["flexDirection"] == "row",
            f"{theme}: .credits-list se re-skinea en pildoras horizontales "
            f"(flexDirection={credits_layout['flexDirection'] if credits_layout else None})",
        )

    if theme == "hyprland":
        # Ascua NO son pildoras: el rol va una vez como cabecera de grupo y los
        # nombres fluyen como prosa atribuida, igual que el cartel de reparto de
        # Vice pero en su propio material. Si alguien reintroduce el bloque
        # compartido con Caelestia, esto salta.
        reparto = page.evaluate("""(() => {
          const credit = document.querySelector('.credit');
          const label = document.querySelector('.credit-group-label');
          if (!credit) return null;
          const s = getComputedStyle(credit);
          return {
            display: s.display,
            borderWidth: s.borderTopWidth,
            radius: s.borderTopLeftRadius,
            tieneRotulo: Boolean(label),
          };
        })()""")
        check(
            reparto is not None and reparto["display"] == "inline",
            f"hyprland: .credit fluye como prosa, no como pildora "
            f"(display={reparto['display'] if reparto else None})",
        )
        check(
            reparto is not None and reparto["borderWidth"] == "0px",
            f"hyprland: .credit no lleva caja "
            f"(borderWidth={reparto['borderWidth'] if reparto else None})",
        )
        check(
            reparto is not None and reparto["tieneRotulo"],
            "hyprland: el rol aparece una vez como .credit-group-label",
        )
```

- [x] **Paso 3: Añadir el marcador de canto duro**

Dentro del mismo `if theme == "hyprland":`, añadir:

```python
        # Radio 0 es la decision estructural del tema: Ascua es luz con CANTO.
        # Caelestia lleva radio y sombra; si Hyprland empieza a redondear,
        # los dos temas convergen y se pierde la identidad.
        canto = page.evaluate("""(() => {
          const s = document.querySelector('.scene-surface') || document.querySelector('.hero-surface');
          if (!s) return null;
          const cs = getComputedStyle(s);
          return { radius: cs.borderTopLeftRadius, shadow: cs.boxShadow };
        })()""")
        check(
            canto is not None and canto["radius"] == "0px",
            f"hyprland: las superficies no redondean (radius={canto['radius'] if canto else None})",
        )
```

- [x] **Paso 4: Correr el gate en los tres temas**

```bash
npm run build && npm run preview &
sleep 4
for t in vice hyprland caelestia; do
  echo "=== $t ==="
  python3 scripts/verify.py --theme "$t" --url http://localhost:4173 2>&1 | tail -20
done
```

Esperado: los tres salen con código 0 contra la línea base. Vice y Caelestia **no pueden**
haber cambiado su recuento de fallos.

- [x] **Paso 5: Commit**

```bash
git add scripts/verify.py
git commit -m "test(hyprland): el gate de identidad protege el reparto y el canto de Ascua"
```

---

### Tarea 9: Gates finales

**Ficheros:**
- Modificar: `docs/superpowers/specs/2026-08-05-hyprland-ascua-design.md` (estado y registro)
- Modificar: `PROGRESS.json`

- [x] **Paso 1: Build y lint**

```bash
npm run build && npm run lint
```

Esperado: cero errores de TypeScript, cero de ESLint.

- [x] **Paso 2: Anti-mock**

```bash
grep -rE "mockData|fakeData|hardcoded|TODO.*real|// fake|demo_data|placeholder|lorem ipsum|Lorem" \
  src/ --include="*.ts" --include="*.tsx"
```

Esperado: sin resultados en secciones publicadas.

- [x] **Paso 3: El arnés en los tres temas, más la pasada de movimiento reducido**

```bash
npm run build && npm run preview &
sleep 4
for t in vice hyprland caelestia; do
  python3 scripts/verify.py --theme "$t" --url http://localhost:4173 || echo "FALLO en $t"
done
python3 scripts/verify.py --theme hyprland --reduced --url http://localhost:4173 || echo "FALLO en reduced"
```

Correrlo **solo y sin editar nada**: el arnés cae con "Execution context was destroyed" si se
toca el árbol mientras corre, y no admite dos instancias contra el mismo servidor.

- [x] **Paso 4: Contraste medido, con recorte ajustado al glifo**

Trampa ya pagada: medir la caja de un bloque ancho y casi vacío devuelve la variación del
fondo, no la del texto — dio 1,5:1 sobre un texto que estaba realmente en 7,9:1. Y el
estadístico tiene que ser **bipolar**, porque hay elementos con texto oscuro sobre fondo claro.

```bash
python3 - <<'PY'
import io, statistics
from PIL import Image
from playwright.sync_api import sync_playwright

def lum(c):
    f = lambda x: (x/255)/12.92 if x/255 <= .04045 else (((x/255)+.055)/1.055)**2.4
    return .2126*f(c[0]) + .7152*f(c[1]) + .0722*f(c[2])

def ratio(png):
    im = Image.open(io.BytesIO(png)).convert("RGB")
    px = list(im.getdata()); n = len(px)
    s = sorted(px, key=lum); k = max(1, int(n*.05))
    m = lambda g: tuple(int(statistics.median(c[i] for c in g)) for i in range(3))
    d, l = m(s[:k]), m(s[-k:])
    r = sorted([lum(d), lum(l)], reverse=True)
    return round((r[0]+.05)/(r[1]+.05), 2)

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome",
                          args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=3)
    pg.goto("http://localhost:4173/?theme=hyprland", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(9000)
    for sel in (".display-xl", ".lead", ".hero-kick", ".hero-corner", ".credit"):
        box = pg.evaluate("""(s => {
          const el = document.querySelector(s);
          if (!el) return null;
          const r = document.createRange(); r.selectNodeContents(el);
          const b = r.getBoundingClientRect();
          return {x: b.left-2, y: b.top-2, width: Math.max(8, b.width+4), height: Math.max(8, b.height+4)};
        })""", sel)
        if not box:
            print(f"  {sel:16} no encontrado"); continue
        v = ratio(pg.screenshot(clip=box))
        print(f"  {sel:16} {v}:1  {'AA ok' if v >= 4.5 else 'REVISAR'}")
    b.close()
PY
```

Esperado: todo ≥ 4,5:1. Referencia del prototipo aprobado: display 14,4 · hablada 11,6 ·
rótulo 6,03.

- [x] **Paso 5: Capturas reales, escritorio y móvil**

1440×900 y 390×844 con `?theme=hyprland`, `--use-gl=swiftshader`, esperando a que el shader
pinte. **Mirar las capturas**, no sólo guardarlas. Confirmar canvas no negro, cero errores de
consola, cero avisos de context lost.

- [x] **Paso 6: Recalibrar `--nav-dim` contra el fondo nuevo**

El valor puesto en la tarea 1 (58% / 52%) es una estimación. Medir el contraste real del
telón de navegación sobre el fondo de Ascua y ajustar hasta que pase AA, anotando en el
comentario del token **contra qué scrim se midió**. Heredar un porcentaje sin medirlo es
exactamente el error que traía el tema.

- [x] **Paso 7: Actualizar `PROGRESS.json` y el estado del spec**

Marcar los items del checklist, poner `"status": "completed"` y `completedAt`. En el spec,
cambiar `Estado: pendiente de plan` por `Estado: implementado` y añadir al final una sección
`## Registro de implementación` con los números finales medidos y cualquier divergencia
respecto a este plan.

- [ ] **Paso 8: → PEDIR REVISIÓN A AOSHI**

Sobre el **sitio real haciendo scroll**, no sobre capturas. Es la lección que costó una tarde
en Vice.

- [ ] **Paso 9: Gates de crítica**

Lanzar `lidia-naive-tester` (flujo y primera impresión) y `vera-art-director` (ejecución
visual, umbral 7,5/10). Los dos leen el mismo build estático, así que **se pueden lanzar a la
vez** — en la sesión de la cortinilla eso ahorró veinte minutos.

- [ ] **Paso 10: Commit final**

```bash
git add PROGRESS.json docs/superpowers/specs/2026-08-05-hyprland-ascua-design.md
git commit -m "docs(hyprland): cerrar Ascua con el registro de implementacion"
```
