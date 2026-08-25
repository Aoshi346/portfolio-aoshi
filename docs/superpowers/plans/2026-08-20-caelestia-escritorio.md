# Caelestia · el escritorio — Plan de implementación (fase A: el shell)

> **Para agentes ejecutores:** SUB-SKILL REQUERIDA: usa `superpowers:subagent-driven-development`
> (recomendada) o `superpowers:executing-plans` para ejecutar tarea a tarea. Los pasos usan
> casillas (`- [ ]`) para el seguimiento, y **hay que marcarlas en el momento**, no al final
> (`.claude/rules/speckit-progress-tracking.md`).

**Objetivo:** convertir Caelestia de un juego de tokens en un shell de escritorio Material You 3
cuyo color y esquema los gobierna el reloj del visitante.

**Arquitectura:** un módulo puro calcula los tokens de color en OkLCH a partir de los minutos del
día y los escribe como propiedades personalizadas en `:root`. `themes.css` deja de tener colores
literales para Caelestia y pasa a consumir esas propiedades. Tres componentes nuevos (barra, dock,
notificación) y una coreografía propia montan el shell, todos con `destroy()` y todos tras la
puerta `theme.id === "caelestia"` en `main.ts`, siguiendo el patrón que ya usan Vice y Hyprland.

**Stack:** Vite 8 · TypeScript ~6 (`strict`) · Tailwind 4 · GSAP 3 · WebGL crudo. **Sin Three.js.
Sin dependencias nuevas** — `oklch()` es CSS nativo.

**Spec:** `docs/superpowers/specs/2026-08-20-caelestia-escritorio-design.md`

---

## Cómo se verifica en este repo — léelo antes de la Tarea 1

**Este proyecto no tiene runner de tests unitarios.** `package.json` expone exactamente cuatro
scripts: `dev`, `build`, `preview`, `lint`. **No instales vitest, jest ni ningún runner.** El ciclo
de prueba del repo es otro y está establecido:

1. `npm run build` (`tsc && vite build`) y `npm run lint`.
2. Arneses Playwright independientes, `scripts/measure-*.py`, lanzados **a mano contra el build de
   producción servido** — nunca contra `npm run dev`, porque el HMR corrompe sus medidas.
3. `python3 scripts/verify.py` contra `scripts/verify-baseline.json`.
4. Captura en navegador.

En este plan, **el "test que falla" de cada tarea es una aserción nueva en
`scripts/measure-caelestia-hora.py`**, que se crea en la Tarea 1 y va creciendo. Ese arnés es el
banco de pruebas de todo lo demás.

Levantar el banco (una vez por tarea, en otra terminal):

```bash
npm run build && npx vite preview --port 4173
```

Y en la principal:

```bash
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
```

---

## Restricciones globales

Se aplican a **todas** las tareas. Copiadas del spec y de `CLAUDE.md`.

- **Vice no se toca.** Ni fondo, ni disparador, ni coreografía, ni tipografía. Cerrado el
  2026-08-05.
- **Hyprland no se toca.**
- **`src/backgrounds/shaderBackground.ts` no se modifica.** Es compartido.
- **No se cambia el orden ni la estructura de las secciones** en el DOM compartido.
- **Nunca `any`.** `strict` está activo; usa `unknown` + guards.
- **Nunca `gsap.from`.** Usa `fromTo` con los dos extremos escritos a mano, y `Array.from(...)`
  para colecciones vivas.
- **Nunca un `transform` CSS de hover sobre un elemento animado por GSAP.** El transform inline
  gana siempre; anima un hijo o el envoltorio.
- **Nunca `data-scene` en algo que no sea una escena.**
- **Todo módulo devuelve un handle con `destroy()`** que se llama en `pagehide`. WebGL: borrar
  programa y buffers; GSAP: matar timelines; RAF: `cancelAnimationFrame`.
- **`prefers-reduced-motion: reduce` siempre tiene fallback.**
- **Cero `console.log`** en código de producción.
- **Cero emojis** en código, docs y commits.
- **El esquema no se interpola jamás.** Ni por `transition` de CSS. Ver Tarea 1.
- **El azufre solo marca lo accionable**: botón de contacto, marca de disponibilidad y anillo de
  foco. Ningún otro uso.
- Commits: `tipo(scope): descripción`. Scope de este plan: `caelestia`.
- **Ninguna dependencia nueva en `package.json`.**

### Constantes del motor, verbatim del spec

```
H(min)      = (min / 1440 * 360 + 60) mod 360          // origen "mediodía frío"
croma(H)    = 1                             si d <= 70  // d = dist. angular a 240°
              max(0.32, 1 - (d - 70) / 115) si d > 70
oscuro(min) = min < 420 || min >= 1200                  // claro de 07:00 a 20:00
azufre      = oklch(0.855 0.152 96)   claro
              oklch(0.905 0.152 96)   oscuro
sobreAzufre = oklch(0.215 0.050 96)
```

---

## Estructura de archivos

| Archivo | Responsabilidad |
|---|---|
| `src/themes/caelestia.color.ts` | **crear** — motor puro: minutos → tokens OkLCH. Sin DOM salvo la función que los aplica |
| `src/themes/caelestia.choreography.ts` | **crear** — coreografía del tema y cambio de workspace |
| `src/components/caelestiaShell.ts` | **crear** — barra, dock y notificación; un solo handle |
| `src/themes/caelestia.ts` | **modificar** — `fontHref`, `choreography`, arranque del motor |
| `src/themes/themes.css` | **modificar** — el bloque `:root[data-theme="caelestia"]` (líneas 3503-3600) |
| `src/backgrounds/caelestiaBlobs.ts` | **modificar** — el shader recibe el matiz; deja de traer color propio |
| `src/main.ts` | **modificar** — rama `theme.id === "caelestia"` para montar el shell |
| `index.html` | **modificar** — `fontHrefs.caelestia` del script inline |
| `scripts/measure-caelestia-hora.py` | **crear** — el arnés |

Los tres componentes del shell van en **un solo archivo** (`caelestiaShell.ts`) y no en tres:
comparten estado (la hora, la escena activa) y cambian juntos. Separarlos obligaría a exportar ese
estado, que es justo el acoplamiento que se quiere evitar.

---

## Tarea 1 · El motor de color y el arnés

**Archivos:**
- Crear: `src/themes/caelestia.color.ts`
- Crear: `scripts/measure-caelestia-hora.py`
- Modificar: `src/themes/caelestia.ts`

**Interfaces:**
- Consume: nada.
- Produce:
  - `export interface CaelestiaColorHandle { destroy: () => void }`
  - `export function hueAt(minutes: number): number`
  - `export function chromaScaleAt(hue: number): number`
  - `export function isDarkAt(minutes: number): boolean`
  - `export function caelestiaTokens(minutes: number): Record<string, string>`
  - `export function mountCaelestiaColor(root: HTMLElement): CaelestiaColorHandle`
  - Las tareas siguientes consumen los tokens **solo por CSS**, nunca importando el módulo.

**Nombres de los tokens (contrato para las tareas 2-9, no los renombres):**

```
--cae-surface        --cae-surface-container   --cae-surface-container-high
--cae-on-surface     --cae-on-surface-variant  --cae-outline
--cae-primary        --cae-on-primary
--cae-primary-container --cae-on-primary-container
--cae-anchor         --cae-on-anchor
--cae-wall-1  --cae-wall-2  --cae-wall-3
--cae-hue            (número sin unidad, para el shader)
```

- [x] **Paso 1: escribir el arnés que falla**

Crear `scripts/measure-caelestia-hora.py`:

```python
#!/usr/bin/env python3
"""
Arnes del motor de color de Caelestia.

Nacio de un fallo real detectado a mano el 2026-08-19 a las 19:43: con una
banda de transicion de 45 min entre esquemas, superficie y texto intercambian
el orden de claridad y se cruzan. En el cruce el contraste es 1:1. Ninguna
curva lo evita — hay que cortar en seco.

Se lanza contra el BUILD DE PRODUCCION servido, nunca contra `npm run dev`:
el HMR de Vite corrompe las medidas.

    npm run build && npx vite preview --port 4173 &
    python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

TOKENS = [
    "--cae-surface", "--cae-surface-container", "--cae-surface-container-high",
    "--cae-on-surface", "--cae-on-surface-variant", "--cae-outline",
    "--cae-primary", "--cae-on-primary",
    "--cae-primary-container", "--cae-on-primary-container",
    "--cae-anchor", "--cae-on-anchor",
]

# Pares que tienen que cumplir AA en TODAS las horas.
PARES = [
    ("--cae-on-surface", "--cae-surface"),
    ("--cae-on-surface-variant", "--cae-surface-container"),
    ("--cae-on-primary", "--cae-primary"),
    ("--cae-on-primary-container", "--cae-primary-container"),
    ("--cae-on-anchor", "--cae-anchor"),
]

# Se inyecta antes de que cargue nada: el motor lee la hora una sola vez, al
# arrancar, asi que parchear Date despues no serviria de nada.
RELOJ = """(minutos) => {
  const Real = Date;
  const base = new Real(2026, 0, 1, Math.floor(minutos / 60), minutos %% 60, 0);
  class Fija extends Real {
    constructor(...args) { super(...(args.length ? args : [base.getTime()])); }
    static now() { return base.getTime(); }
  }
  window.Date = Fija;
}"""


def rel_luminance(rgb):
    def canal(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (canal(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = rel_luminance(a), rel_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def leer(page, minutos):
    """Devuelve {token: (r,g,b)} resolviendo oklch() a sRGB en el navegador."""
    return page.evaluate(
        """(tokens) => {
            const cs = getComputedStyle(document.documentElement);
            const probe = document.createElement('span');
            document.body.appendChild(probe);
            const out = {};
            for (const t of tokens) {
              probe.style.color = cs.getPropertyValue(t).trim();
              const m = getComputedStyle(probe).color.match(/[\\d.]+/g);
              out[t] = m ? m.slice(0, 3).map(Number) : null;
            }
            probe.remove();
            out.__hue = parseFloat(cs.getPropertyValue('--cae-hue'));
            return out;
        }""",
        TOKENS,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    fallos = []
    with sync_playwright() as p:
        nav = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])

        # ---- 1. barrido de las 24 horas, cada 20 minutos
        for minutos in range(0, 1440, 20):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            ctx.add_init_script("(%s)(%d)" % (RELOJ, minutos))
            page = ctx.new_page()
            page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1200)
            vals = leer(page, minutos)

            for t in TOKENS:
                if vals.get(t) is None:
                    fallos.append("%02d:%02d token ausente %s" % (minutos // 60, minutos %% 60, t))

            for fg, bg in PARES:
                if vals.get(fg) and vals.get(bg):
                    r = ratio(vals[fg], vals[bg])
                    if r < 4.5:
                        fallos.append(
                            "%02d:%02d %s sobre %s = %.2f:1 (< 4.5)"
                            % (minutos // 60, minutos %% 60, fg, bg, r)
                        )

            # ---- 2. el matiz a las 11:00 es 225 +/- 1
            if minutos == 660:
                hue = vals.get("__hue")
                if hue is None or abs(hue - 225.0) > 1.0:
                    fallos.append("matiz a las 11:00 = %s (esperado 225 +/- 1)" % hue)

            ctx.close()

        # ---- 3. el umbral no tiene estados intermedios
        for antes, despues in ((1199, 1200), (419, 420)):
            claves = []
            for minutos in (antes, despues):
                ctx = nav.new_context(viewport={"width": 1440, "height": 900})
                ctx.add_init_script("(%s)(%d)" % (RELOJ, minutos))
                page = ctx.new_page()
                page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(1200)
                v = leer(page, minutos)
                claves.append(ratio(v["--cae-on-surface"], v["--cae-surface"]))
                ctx.close()
            for r in claves:
                if r < 4.5:
                    fallos.append("umbral %d/%d: contraste %.2f:1 (< 4.5)" % (antes, despues, r))

        nav.close()

    if fallos:
        print("FALLOS (%d):" % len(fallos))
        for f in fallos:
            print("  -", f)
        sys.exit(1)
    print("OK — motor de color de Caelestia en verde")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

- [x] **Paso 2: correrlo y comprobar que falla**

```bash
npm run build && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
```

Esperado: `FALLOS`, con `token ausente --cae-surface` repetido para las 72 horas muestreadas.
Si sale otra cosa, para y averigua por qué antes de seguir.

- [x] **Paso 3: escribir el motor**

Crear `src/themes/caelestia.color.ts`:

```ts
/**
 * El motor de color de Caelestia: la hora del visitante decide el matiz y el
 * esquema. Puro salvo `mountCaelestiaColor`, que es lo unico que toca el DOM.
 *
 * Por que OkLCH y no HSL: en OkLCH la claridad es perceptual e independiente
 * del matiz. Con L y C fijas por rol, el contraste es INVARIANTE al matiz por
 * construccion — se mide una vez y vale para las 1.440 posiciones del reloj.
 * En HSL eso es falso y este gesto seria temerario.
 */

/** L y C por rol. El matiz es lo unico que se mueve. */
type Rol = readonly [l: number, c: number];

const CLARO: Record<string, Rol> = {
  "surface": [0.98, 0.012],
  "surface-container": [0.955, 0.02],
  "surface-container-high": [0.925, 0.026],
  "on-surface": [0.245, 0.035],
  "on-surface-variant": [0.47, 0.032],
  "outline": [0.7, 0.022],
  "primary": [0.505, 0.13],
  "on-primary": [0.99, 0.01],
  "primary-container": [0.895, 0.062],
  "on-primary-container": [0.31, 0.1],
};

const OSCURO: Record<string, Rol> = {
  "surface": [0.185, 0.016],
  "surface-container": [0.235, 0.022],
  "surface-container-high": [0.285, 0.026],
  "on-surface": [0.925, 0.016],
  "on-surface-variant": [0.795, 0.024],
  "outline": [0.42, 0.02],
  "primary": [0.815, 0.115],
  "on-primary": [0.27, 0.095],
  "primary-container": [0.395, 0.105],
  "on-primary-container": [0.9, 0.062],
};

/** Origen de la rueda: "mediodia frio". Ver el spec para por que no es 270. */
const ORIGEN = 60;

/** El ancla no gira nunca: es lo unico constante del tema. */
const AZUFRE = { l: 0.855, lOscuro: 0.905, c: 0.152, h: 96 } as const;

const MINUTOS_DIA = 1440;
const AMANECE = 7 * 60;
const ANOCHECE = 20 * 60;

function ok(l: number, c: number, h: number): string {
  return `oklch(${l.toFixed(3)} ${c.toFixed(3)} ${h.toFixed(1)})`;
}

/** Los 360 grados de la rueda repartidos sobre 24 horas. */
export function hueAt(minutes: number): number {
  return (((minutes / MINUTOS_DIA) * 360 + ORIGEN) % 360 + 360) % 360;
}

/**
 * Marea de croma: pleno en la mitad fria, a un tercio en el naranja y el
 * magenta. No recorta el arco — baja la voz cuando pasa por el territorio de
 * Hyprland y de Vice, para que no se confundan con ellos.
 */
export function chromaScaleAt(hue: number): number {
  const d = Math.abs((((hue - 240) % 360) + 540) % 360 - 180);
  if (d <= 70) return 1;
  return Math.max(0.32, 1 - (d - 70) / 115);
}

/** Claro de 07:00 a 20:00. Sin banda de transicion: ver `mountCaelestiaColor`. */
export function isDarkAt(minutes: number): boolean {
  return minutes < AMANECE || minutes >= ANOCHECE;
}

export function caelestiaTokens(minutes: number): Record<string, string> {
  const hue = hueAt(minutes);
  const escala = chromaScaleAt(hue);
  const oscuro = isDarkAt(minutes);
  const roles = oscuro ? OSCURO : CLARO;

  const tokens: Record<string, string> = {};
  for (const [nombre, [l, c]] of Object.entries(roles)) {
    tokens[`--cae-${nombre}`] = ok(l, c * escala, hue);
  }

  tokens["--cae-anchor"] = ok(oscuro ? AZUFRE.lOscuro : AZUFRE.l, AZUFRE.c, AZUFRE.h);
  tokens["--cae-on-anchor"] = ok(0.215, 0.05, AZUFRE.h);
  tokens["--cae-wall-1"] = ok(oscuro ? 0.24 : 0.93, 0.09 * escala, hue);
  tokens["--cae-wall-2"] = ok(oscuro ? 0.21 : 0.95, 0.07 * escala, (hue + 42) % 360);
  tokens["--cae-wall-3"] = ok(oscuro ? 0.2 : 0.96, 0.06 * escala, (hue + 318) % 360);
  tokens["--cae-hue"] = hue.toFixed(1);

  return tokens;
}

export interface CaelestiaColorHandle {
  destroy: () => void;
}

/**
 * Aplica los tokens y los mantiene al dia.
 *
 * EL ESQUEMA NO SE INTERPOLA. La superficie va de L 0.980 a 0.185 y el texto
 * de 0.245 a 0.925: intercambian el orden, asi que cualquier recorrido
 * continuo entre los dos esquemas cruza por el punto en que ambos tienen la
 * misma claridad — contraste 1:1. Medido: 1.38:1 a las 19:55 con una banda de
 * 45 min. No hay easing que lo salve. Por eso el cambio de esquema apaga las
 * transiciones durante un fotograma en vez de suavizarse.
 */
export function mountCaelestiaColor(root: HTMLElement): CaelestiaColorHandle {
  let oscuroActual: boolean | null = null;
  let temporizador = 0;

  const aplicar = (): void => {
    const ahora = new Date();
    const minutos = ahora.getHours() * 60 + ahora.getMinutes();
    const oscuro = isDarkAt(minutos);

    if (oscuroActual !== null && oscuroActual !== oscuro) {
      root.classList.add("cae-corte");
      window.setTimeout(() => root.classList.remove("cae-corte"), 60);
      root.dispatchEvent(
        new CustomEvent("caelestia:esquema", { detail: { oscuro }, bubbles: true }),
      );
    }
    oscuroActual = oscuro;
    root.dataset.caeEsquema = oscuro ? "noche" : "dia";

    for (const [nombre, valor] of Object.entries(caelestiaTokens(minutos))) {
      root.style.setProperty(nombre, valor);
    }
  };

  aplicar();
  // Un minuto es la resolucion del reloj de la barra; el matiz avanza 0,25
  // grados por minuto, que es imperceptible entre pasos.
  temporizador = window.setInterval(aplicar, 60_000);

  return {
    destroy: () => {
      window.clearInterval(temporizador);
    },
  };
}
```

Y arrancarlo desde `src/themes/caelestia.ts`, dentro de `mountBackground` **no** — el color no
depende del fondo. Modificar el módulo del tema así:

```ts
import type { Theme } from "./types";

/**
 * El escritorio: un shell Material You 3 cuyo color y esquema los gobierna el
 * reloj del visitante. Ver
 * `docs/superpowers/specs/2026-08-20-caelestia-escritorio-design.md`.
 */
export const caelestiaTheme: Theme = {
  id: "caelestia",
  label: "Caelestia",
  themeColor: "#f4f0f9",
  fontHref:
    "https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@500&display=swap",
  motion: { style: "fluid", ease: "back.out(1.5)", duration: 1.2, stagger: 0.08 },
  async mountBackground(container) {
    const { mountCaelestiaBlobs } = await import("../backgrounds/caelestiaBlobs");
    return mountCaelestiaBlobs(container);
  },
};
```

> La tipografía se cambia en la Tarea 3, no aquí. Una tarea, un cambio.

El arranque del motor va en `src/main.ts`, junto a los otros módulos por tema. Añadir **después**
del bloque del cursor de Vice (sobre la línea 200) y **antes** de `applyTheme`:

```ts
// El motor de color de Caelestia: la hora decide matiz y esquema. Va antes de
// `applyTheme` para que los tokens esten puestos en el primer pintado.
let caeColorHandle: { destroy: () => void } | null = null;
if (theme.id === "caelestia") {
  void import("./themes/caelestia.color").then(({ mountCaelestiaColor }) => {
    caeColorHandle = mountCaelestiaColor(document.documentElement);
  });
}
```

Y añadirlo al `pagehide` existente (sobre la línea 217), junto a los demás:

```ts
    caeColorHandle?.destroy();
```

- [x] **Paso 4: correr el arnés y comprobar que pasa**

```bash
npm run build && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
```

Esperado: `OK — motor de color de Caelestia en verde`, código de salida 0.

Si algún par cae por debajo de 4.5:1, **no toques el umbral del arnés**: ajusta la `L` del rol en
`caelestia.color.ts` y actualiza la tabla del spec. El arnés es la referencia, no la variable.

- [x] **Paso 5: build y lint**

```bash
npm run build && npm run lint
```

Esperado: los dos en verde, cero errores de TypeScript.

- [x] **Paso 6: commit**

```bash
git add src/themes/caelestia.color.ts src/main.ts scripts/measure-caelestia-hora.py
git commit -m "feat(caelestia): motor de color en OkLCH gobernado por la hora

El esquema NO se interpola: superficie y texto intercambian el orden de
claridad, asi que todo recorrido continuo cruza por contraste 1:1 (1.38:1
medido a las 19:55). Se decide al cargar y se corta en seco.

Arnes nuevo: scripts/measure-caelestia-hora.py, 72 horas muestreadas."
```

---

## Tarea 2 · La rampa tonal en `themes.css`

**Archivos:**
- Modificar: `src/themes/themes.css:3503-3600` (el bloque `:root[data-theme="caelestia"]`)

**Interfaces:**
- Consume: los tokens `--cae-*` de la Tarea 1.
- Produce: los tokens de tema del proyecto (`--color-ink`, `--color-paper`, `--color-accent`,
  `--color-line`, `--radius-card`) alimentados desde los `--cae-*`, más
  `--cae-elev-1/2/3` para las tres alturas de superficie.

- [ ] **Paso 1: añadir la aserción de rampa al arnés**

En `scripts/measure-caelestia-hora.py`, dentro del bucle de las 24 horas, después del bloque de
`PARES`:

```python
            # ---- rampa tonal: las tres superficies tienen que ser DISTINTAS.
            # El tema viejo usaba `#ffffff 62%` para todas y por eso no habia
            # jerarquia de elevacion: todo flotaba a la misma altura.
            rampa = [
                vals.get("--cae-surface"),
                vals.get("--cae-surface-container"),
                vals.get("--cae-surface-container-high"),
            ]
            if all(rampa):
                lums = [rel_luminance(c) for c in rampa]
                pasos = [abs(lums[i + 1] - lums[i]) for i in range(2)]
                if min(pasos) < 0.008:
                    fallos.append(
                        "%02d:%02d rampa plana: pasos de luminancia %s"
                        % (minutos // 60, minutos %% 60, [round(p, 4) for p in pasos])
                    )
```

- [ ] **Paso 2: correr y comprobar que falla**

Esperado: `rampa plana` en las 72 horas — porque `themes.css` todavía no usa los tokens y las
superficies siguen siendo `color-mix(in srgb, #ffffff 62%, transparent)` para todo.

- [ ] **Paso 3: reescribir el bloque**

Sustituir **todo** el bloque `:root[data-theme="caelestia"]` de `themes.css` (desde
`/* ---- Caelestia */` hasta justo antes del comentario de `Reparto agrupado por area (solo Vice)`)
por:

```css
/* ---------------------------------------------------------------- Caelestia */

/*
 * El escritorio. Aqui ya no hay colores literales: los pone
 * `caelestia.color.ts` en `:root` a partir de la hora del visitante, y este
 * bloque solo los reparte por rol. Ver
 * `docs/superpowers/specs/2026-08-20-caelestia-escritorio-design.md`.
 */
:root[data-theme="caelestia"] {
  --color-ink: var(--cae-surface);
  --color-paper: var(--cae-on-surface);
  --color-accent: var(--cae-primary);
  --color-accent-2: var(--cae-anchor);
  --color-line: var(--cae-outline);

  /*
   * Tema de dos caras. El 70% de antes estaba calibrado contra un unico fondo
   * claro y ya no vale: ahora el rol atenuado es un token propio con su
   * claridad fija, medida por el arnes en las 24 horas.
   */
  --nav-dim: 100%;
  --nav-dim-soft: 100%;

  --font-display: "Outfit", system-ui, sans-serif;
  --font-body: "Outfit", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  --radius-card: 22px;
  --display-tracking: -0.03em;
  --display-weight: 800;
  --display-transform: none;
  --display-leading: 0.98;
  --bg-fallback: linear-gradient(160deg, #f4f0f9 0%, #e4dcf3 50%, #dbeee6 100%);

  /* Las tres alturas de la rampa. Es la pieza que faltaba. */
  --cae-elev-1: var(--cae-surface-container);
  --cae-elev-2: var(--cae-surface-container-high);
  --cae-elev-3: var(--cae-primary-container);

  background: var(--cae-surface);
  color: var(--cae-on-surface);
}

/*
 * El corte de esquema. Se pone durante un fotograma cuando el reloj cruza el
 * umbral: interpolar entre los dos esquemas atraviesa contraste 1:1 de forma
 * matematicamente inevitable, asi que no puede haber transicion aqui.
 */
:root[data-theme="caelestia"].cae-corte,
:root[data-theme="caelestia"].cae-corte * {
  transition: none !important;
}

/* Contenedores tonales con elevacion real, cada uno en su altura. */
:root[data-theme="caelestia"] .hero-surface,
:root[data-theme="caelestia"] .scene-surface {
  background: var(--cae-elev-1);
  border: 1px solid var(--cae-outline);
  border-radius: var(--radius-card);
  padding: clamp(1.75rem, 4vw, 3.25rem);
  box-shadow: none;
  transition: background 0.7s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .hero-surface {
  max-width: 68rem;
}

/*
 * Compensacion heredada: `.hero-kick` paso a ser hermano de `.hero-surface`
 * para que la rejilla de Hyprland pudiera usarlo como columna 1, y al salir de
 * la tarjeta perdio su padding y su borde. Se reponen aqui. El comentario
 * largo con las medidas esta en el historial de este archivo (buscar
 * "x:101/y:267/ancho:982"); no se repite para no duplicarlo.
 */
:root[data-theme="caelestia"] [data-scene="hero"] .hero-kick {
  position: relative;
  top: calc(clamp(1.75rem, 4vw, 3.25rem) + 1px);
  margin-left: calc(clamp(1.75rem, 4vw, 3.25rem) + 1px);
  margin-right: calc(clamp(1.75rem, 4vw, 3.25rem) + 1px);
  width: calc(min(68rem, 100%) - 2 * (clamp(1.75rem, 4vw, 3.25rem) + 1px));
}

:root[data-theme="caelestia"] .chip {
  background: var(--cae-primary-container);
  border-color: transparent;
  color: var(--cae-on-primary-container);
}

/* El grano se retira: con rampa tonal real ya hay profundidad sin ensuciar. */
:root[data-theme="caelestia"] .bg-noise {
  opacity: 0;
}

:root[data-theme="caelestia"] :focus-visible {
  outline: 2px solid var(--cae-anchor);
  outline-offset: 3px;
}
```

> **Ojo con `--nav-dim`.** El valor de 70% que había estaba calibrado contra un único fondo claro y
> con dos esquemas deja de tener sentido. Se pone a 100% y el atenuado pasa a ser
> `--cae-on-surface-variant`, que tiene su claridad fija y la mide el arnés. Si al revisar
> `sceneNav` ves que el atenuado se ha perdido, es esto: usa el token, no el porcentaje.

- [ ] **Paso 4: correr el arnés y comprobar que pasa**

Esperado: `OK`. Si sigue saliendo `rampa plana`, comprueba que `caelestia.color.ts` está
escribiendo en `document.documentElement` y no en `app`.

- [ ] **Paso 5: build, lint y captura**

```bash
npm run build && npm run lint
```

Y una captura en las dos horas, para ver la rampa con los ojos:

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for hora, nombre in ((11, 'dia'), (23, 'noche')):
        ctx = b.new_context(viewport={'width':1440,'height':900})
        ctx.add_init_script('Date.now = () => new Date(2026,0,1,%d,0,0).getTime()' % hora)
        pg = ctx.new_page()
        pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded')
        pg.wait_for_timeout(9000)
        pg.screenshot(path='/tmp/cae-rampa-%s.png' % nombre, full_page=True)
        ctx.close()
    b.close()
"
```

Míralas. Las tres superficies deben distinguirse a simple vista.

- [ ] **Paso 6: commit**

```bash
git add src/themes/themes.css scripts/measure-caelestia-hora.py
git commit -m "feat(caelestia): rampa tonal real en vez de un blanco al 62%

Las superficies dejan de ser el mismo color-mix para todo y pasan a las
tres alturas de MD3. El arnes comprueba que los pasos de luminancia entre
ellas no bajan de 0.008 en ninguna de las 24 horas."
```

---

## Tarea 3 · Tipografía

**Archivos:**
- Modificar: `src/themes/caelestia.ts` (el `fontHref`)
- Modificar: `index.html` (el `fontHrefs.caelestia` del script inline)
- Modificar: `src/themes/themes.css` (los tres tokens de familia)

**Interfaces:**
- Consume: nada.
- Produce: `--font-display`, `--font-body`, `--font-mono` y `--cae-display-axes` para Caelestia.

> **Los dos `fontHref` van SIEMPRE a la par.** El script inline de `index.html` es quien pide las
> fuentes antes del primer pintado; tocar solo uno no rompe nada visible, degrada la carga a la vía
> lenta en silencio, que es peor que un error. El mismo aviso está escrito en `src/themes/vice.ts`.

- [ ] **Paso 1: comprobar que la hoja existe antes de escribirla**

```bash
curl -s -o /dev/null -w "%{http_code}\n" -A "Mozilla/5.0" \
  "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1&family=Hanken+Grotesk:wght@100..900&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=swap"
```

Esperado: `200`. Si no, para: la fuente o el eje han cambiado en Google Fonts y hay que revisar el
spec antes de continuar.

- [ ] **Paso 2: escribir el `fontHref` en el módulo del tema**

En `src/themes/caelestia.ts`, sustituir el `fontHref` y añadir el comentario:

```ts
  /*
   * Fraunces es el display, y sus ejes van escritos a mano en `themes.css`
   * (`--cae-display-axes`): con `opsz` a 9 los remates se afilan, con SOFT a 0
   * desaparece el redondeo y WONK a 1 activa las formas alternativas torcidas.
   * Hanken Grotesk cubre el cuerpo y Martian Mono las etiquetas.
   *
   * Este href y el `fontHrefs.caelestia` del script inline de `index.html` van
   * SIEMPRE a la par: el inline es quien pide las fuentes antes del primer
   * pintado, asi que tocar solo uno degrada la carga a la via lenta en
   * silencio, que es peor que un error.
   */
  fontHref:
    "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1&family=Hanken+Grotesk:wght@100..900&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=swap",
```

- [ ] **Paso 3: espejar el href en `index.html`**

```bash
grep -n "fontHrefs" index.html
```

Sustituir el valor de `caelestia` por **exactamente la misma cadena**. Después:

```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('index.html','utf8');
const ts = fs.readFileSync('src/themes/caelestia.ts','utf8');
const re = /https:\/\/fonts\.googleapis\.com\/css2\?family=Fraunces[^\"']+/;
const a = (html.match(re)||[])[0], b = (ts.match(re)||[])[0];
if (!a || !b || a !== b) { console.error('DESINCRONIZADOS'); process.exit(1); }
console.log('href sincronizado');
"
```

Esperado: `href sincronizado`.

- [ ] **Paso 4: los tokens de familia**

En el bloque de Caelestia de `themes.css`, sustituir las tres líneas de familia:

```css
  --font-display: "Fraunces", Georgia, serif;
  --font-body: "Hanken Grotesk", system-ui, sans-serif;
  /* Red de seguridad, igual que en Vice y Hyprland: sin esto las utilidades
     `font-mono` de Tailwind filtran `ui-monospace`. */
  --font-mono: "Martian Mono", ui-monospace, monospace;

  /* Los ejes del display, escritos a mano. Fraunces por defecto no es esto. */
  --cae-display-axes: "opsz" 9, "wght" 900, "SOFT" 0, "WONK" 1;
  --display-weight: 900;
  --display-tracking: -0.03em;
```

Y aplicar los ejes donde se use el display:

```css
:root[data-theme="caelestia"] [data-display],
:root[data-theme="caelestia"] h1,
:root[data-theme="caelestia"] h2 {
  font-family: var(--font-display);
  font-variation-settings: var(--cae-display-axes);
}
```

- [ ] **Paso 5: verificar que la fuente carga de verdad**

Añadir al final de `scripts/measure-caelestia-hora.py`, antes de `nav.close()`:

```python
        # ---- 4. las tres familias cargan y el display lleva sus ejes
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2500)
        tipos = page.evaluate(
            """() => {
                const cs = getComputedStyle(document.documentElement);
                const h1 = document.querySelector('h1');
                return {
                  display: cs.getPropertyValue('--font-display').trim(),
                  cargadas: [...document.fonts].map(f => f.family),
                  ejes: h1 ? getComputedStyle(h1).fontVariationSettings : null,
                };
            }"""
        )
        for familia in ("Fraunces", "Hanken Grotesk", "Martian Mono"):
            if familia not in tipos["cargadas"]:
                fallos.append("tipografia no cargada: %s" % familia)
        if tipos["ejes"] is None or "WONK" not in str(tipos["ejes"]):
            fallos.append("el display no lleva los ejes: %s" % tipos["ejes"])
        ctx.close()
```

Correr el arnés. Esperado: `OK`.

- [ ] **Paso 6: build, lint y commit**

```bash
npm run build && npm run lint
git add src/themes/caelestia.ts index.html src/themes/themes.css scripts/measure-caelestia-hora.py
git commit -m "feat(caelestia): Fraunces con WONK sobre Hanken Grotesk y Martian Mono

Outfit hacia de display y de cuerpo a la vez, asi que la jerarquia salia
entera del tamano. Roboto descartada: en la escala oficial de MD3 tiene el
mismo sintoma. Los ejes del display van escritos a mano -- Fraunces por
defecto no es esto."
```

---

## Tarea 4 · La barra del shell

**Archivos:**
- Crear: `src/components/caelestiaShell.ts`
- Modificar: `src/main.ts`
- Modificar: `src/themes/themes.css`

**Interfaces:**
- Consume: `--cae-*` (Tareas 1-3), `el()` de `src/utils/dom.ts`, `sceneEntries` de
  `src/data/content.ts` (los cinco `{ id, label, blurb }` que ya existen).
- Produce:
  - `export interface CaelestiaShellHandle { destroy: () => void; setScene: (index: number) => void }`
  - `export function mountCaelestiaShell(root: HTMLElement): CaelestiaShellHandle`
  - Evento `caelestia:workspace` con `detail: { index: number; id: string }`, que consume la
    Tarea 7.

- [ ] **Paso 1: leer el contrato de los datos**

```bash
grep -n "sceneEntries" -B 8 src/data/content.ts | tail -20
```

Confirma los cinco ids: `hero`, `quien-es`, `obra`, `creditos`, `contacto`. **Usa esos, no los
inventes.**

- [ ] **Paso 2: aserción en el arnés**

```python
        # ---- 5. la barra: cinco pastillas, reloj y bandeja
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script("(%s)(%d)" % (RELOJ, 660))
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        barra = page.evaluate(
            """() => {
                const b = document.querySelector('[data-cae-bar]');
                if (!b) return null;
                return {
                  pastillas: b.querySelectorAll('[data-cae-ws]').length,
                  reloj: (b.querySelector('[data-cae-clock]') || {}).textContent,
                  activa: b.querySelectorAll('[data-cae-ws][aria-current="true"]').length,
                };
            }"""
        )
        if barra is None:
            fallos.append("no existe [data-cae-bar]")
        else:
            if barra["pastillas"] != 5:
                fallos.append("la barra tiene %d pastillas, esperadas 5" % barra["pastillas"])
            if barra["reloj"] != "11:00":
                fallos.append("el reloj marca %r, esperado '11:00'" % barra["reloj"])
            if barra["activa"] != 1:
                fallos.append("pastillas activas: %d, esperada 1" % barra["activa"])
        ctx.close()

        # ---- 6. los otros dos temas NO montan el shell
        for otro in ("vice", "hyprland"):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            page.goto(args.base + "/?theme=" + otro, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            if page.query_selector("[data-cae-bar]"):
                fallos.append("el shell de Caelestia se ha montado en %s" % otro)
            ctx.close()
```

Correr. Esperado: `no existe [data-cae-bar]`.

- [ ] **Paso 3: escribir la barra**

Crear `src/components/caelestiaShell.ts`:

```ts
import { sceneEntries } from "../data/content";
import { el } from "../utils/dom";

/**
 * El shell de Caelestia: barra de workspaces, dock y notificaciones.
 *
 * Los tres viven en un solo modulo a proposito — comparten estado (la hora, la
 * escena activa) y cambian juntos. Separarlos obligaria a exportar ese estado,
 * que es el acoplamiento que se quiere evitar.
 */
export interface CaelestiaShellHandle {
  destroy: () => void;
  setScene: (index: number) => void;
}

function formatoHora(fecha: Date): string {
  const hh = String(fecha.getHours()).padStart(2, "0");
  const mm = String(fecha.getMinutes()).padStart(2, "0");
  return `${hh}:${mm}`;
}

export function mountCaelestiaShell(root: HTMLElement): CaelestiaShellHandle {
  const limpiadores: (() => void)[] = [];

  // ---------------------------------------------------------------- la barra
  const pastillas = sceneEntries.map((escena, indice) => {
    const numero = el("i", "cae-ws-n", [String(indice + 1)]);
    const boton = el("button", "cae-ws", [numero, escena.label]);
    boton.type = "button";
    boton.dataset.caeWs = escena.id;
    boton.setAttribute("aria-current", indice === 0 ? "true" : "false");

    const alPulsar = (): void => {
      root.dispatchEvent(
        new CustomEvent("caelestia:workspace", {
          detail: { index: indice, id: escena.id },
          bubbles: true,
        }),
      );
    };
    boton.addEventListener("click", alPulsar);
    limpiadores.push(() => boton.removeEventListener("click", alPulsar));
    return boton;
  });

  const navegacion = el("nav", "cae-ws-list", pastillas);
  navegacion.setAttribute("aria-label", "Escenas");

  const punto = el("i", "cae-dot");
  const disponible = el("span", "cae-avail", [punto, "Disponible"]);

  const reloj = el("span", "cae-clock", [formatoHora(new Date())]);
  reloj.dataset.caeClock = "";

  const bandeja = el("span", "cae-tray", [disponible, reloj]);
  const marca = el("span", "cae-mark", ["caelestia"]);

  const barra = el("header", "cae-bar", [marca, navegacion, bandeja]);
  barra.dataset.caeBar = "";

  root.append(barra);

  // El reloj de la barra es lo que gobierna el tema: tiene que ir al minuto.
  const tic = window.setInterval(() => {
    reloj.textContent = formatoHora(new Date());
  }, 30_000);

  const setScene = (index: number): void => {
    pastillas.forEach((boton, i) => {
      boton.setAttribute("aria-current", i === index ? "true" : "false");
    });
  };

  return {
    destroy: () => {
      window.clearInterval(tic);
      for (const limpiar of limpiadores) limpiar();
      barra.remove();
    },
    setScene,
  };
}
```

- [ ] **Paso 4: montarla en `main.ts`**

Junto al resto de módulos por tema, **después** del bloque del motor de color de la Tarea 1:

```ts
// El shell de Caelestia: barra, dock y notificaciones. Misma puerta por tema
// que usan el encendido de Hyprland y el cursor de Vice.
let caeShellHandle: { destroy: () => void; setScene: (index: number) => void } | null = null;
if (theme.id === "caelestia") {
  void import("./components/caelestiaShell").then(({ mountCaelestiaShell }) => {
    caeShellHandle = mountCaelestiaShell(app);
  });
}
```

Y en el `pagehide`:

```ts
    caeShellHandle?.destroy();
```

- [ ] **Paso 5: los estilos de la barra**

Al final del bloque de Caelestia en `themes.css`:

```css
:root[data-theme="caelestia"] .cae-bar {
  position: fixed;
  top: 0.75rem;
  left: 0.875rem;
  right: 0.875rem;
  z-index: 60;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  flex-wrap: wrap;
  padding: 0.5rem 0.625rem 0.5rem 1rem;
  border-radius: 999px;
  background: var(--cae-elev-2);
  backdrop-filter: blur(18px);
  box-shadow: 0 10px 30px -18px rgb(0 0 0 / 0.5);
  transition: background 0.7s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .cae-mark {
  font-family: var(--font-mono);
  font-size: 0.6875rem;
  letter-spacing: 0.06em;
  color: var(--cae-primary);
}

:root[data-theme="caelestia"] .cae-ws-list {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

:root[data-theme="caelestia"] .cae-ws {
  font-family: var(--font-body);
  font-size: 0.75rem;
  padding: 0.3125rem 0.6875rem;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--cae-on-surface-variant);
  cursor: pointer;
  white-space: nowrap;
  transition:
    background 0.28s cubic-bezier(0.2, 0, 0, 1),
    color 0.28s,
    padding 0.28s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .cae-ws:hover {
  background: var(--cae-elev-1);
}

:root[data-theme="caelestia"] .cae-ws[aria-current="true"] {
  background: var(--cae-primary);
  color: var(--cae-on-primary);
  font-weight: 600;
  padding-inline: 0.9375rem;
}

:root[data-theme="caelestia"] .cae-ws-n {
  font-style: normal;
  font-family: var(--font-mono);
  font-size: 0.625rem;
  opacity: 0.55;
  margin-right: 0.3125rem;
}

:root[data-theme="caelestia"] .cae-tray {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.5625rem;
}

:root[data-theme="caelestia"] .cae-avail {
  display: flex;
  align-items: center;
  gap: 0.3125rem;
  font-size: 0.625rem;
  color: var(--cae-on-surface-variant);
}

:root[data-theme="caelestia"] .cae-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  background: var(--cae-anchor);
}

/* El reloj no es adorno: es lo que gobierna el tema. */
:root[data-theme="caelestia"] .cae-clock {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--cae-primary);
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] .cae-ws {
    transition: none;
  }
}
```

- [ ] **Paso 6: correr el arnés, build, lint y commit**

```bash
npm run build && npm run lint && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
```

Esperado: `OK`, incluida la aserción 6 (el shell no aparece en Vice ni en Hyprland).

```bash
git add src/components/caelestiaShell.ts src/main.ts src/themes/themes.css scripts/measure-caelestia-hora.py
git commit -m "feat(caelestia): barra de workspaces con reloj y bandeja de estado

Cinco pastillas desde sceneEntries, no una lista propia. El arnes
comprueba ademas que el shell NO se monta en Vice ni en Hyprland."
```

---

## Tarea 5 · El dock

**Archivos:**
- Modificar: `src/components/caelestiaShell.ts`
- Modificar: `src/themes/themes.css`

**Interfaces:**
- Consume: `contactChannels` de `src/data/content.ts` (los cuatro `{ id, label, ... }`) y
  `elFromMarkup()` de `src/utils/dom.ts` para los SVG.
- Produce: nada nuevo hacia fuera; el dock cuelga del mismo handle.

> **Los SVG son de confianza y van bundleados.** `elFromMarkup` usa `innerHTML`, que es aceptable
> aquí y solo aquí: son cadenas propias y estáticas, no dato externo. Nunca metas por ahí un query
> param ni una respuesta de API.

- [ ] **Paso 1: leer los canales reales**

```bash
sed -n '340,385p' src/data/content.ts
```

Confirma las etiquetas: `Correo`, `LinkedIn`, `Teléfono`, `GitHub`. **Usa `href` de los datos, no
literales.**

- [ ] **Paso 2: aserción en el arnés**

```python
        # ---- 7. el dock: cuatro accesos con etiqueta accesible y rel seguro
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        dock = page.evaluate(
            """() => {
                const d = document.querySelector('[data-cae-dock]');
                if (!d) return null;
                const enlaces = [...d.querySelectorAll('a')];
                return {
                  n: enlaces.length,
                  sinLabel: enlaces.filter(a => !a.getAttribute('aria-label')).length,
                  externosSinRel: enlaces.filter(
                    a => a.target === '_blank' && !(a.rel || '').includes('noopener')
                  ).length,
                  sinIcono: enlaces.filter(a => !a.querySelector('svg')).length,
                };
            }"""
        )
        if dock is None:
            fallos.append("no existe [data-cae-dock]")
        else:
            if dock["n"] < 4:
                fallos.append("el dock tiene %d accesos, esperados 4 o mas" % dock["n"])
            if dock["sinLabel"]:
                fallos.append("%d accesos del dock sin aria-label" % dock["sinLabel"])
            if dock["externosSinRel"]:
                fallos.append("%d enlaces externos sin rel noopener" % dock["externosSinRel"])
            if dock["sinIcono"]:
                fallos.append("%d accesos del dock sin icono" % dock["sinIcono"])
        ctx.close()
```

Correr. Esperado: `no existe [data-cae-dock]`.

- [ ] **Paso 3: los iconos**

En `caelestiaShell.ts`, arriba del módulo:

```ts
/**
 * Iconos del dock. Cadenas propias y estaticas, bundleadas — por eso pueden ir
 * por `elFromMarkup` (innerHTML). Nunca metas aqui dato externo.
 * GitHub y LinkedIn son las marcas oficiales (simple-icons, CC0).
 */
const ICONOS: Record<ContactChannel["key"], string> = {
  github:
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>',
  linkedin:
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
  correo:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="m3.5 7.5 8.5 6 8.5-6"/></svg>',
  telefono:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.24 11.4 11.4 0 0 0 3.6.58 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1 11.4 11.4 0 0 0 .58 3.6 1 1 0 0 1-.25 1z"/></svg>',
};

// El tipo se importa para que `ICONOS` no pueda desincronizarse de los canales:
// si manana aparece un quinto `key`, TypeScript exige el icono.

/*
 * No hace falta mapa de etiqueta a icono: `ContactChannel.key` ya es
 * "correo" | "linkedin" | "telefono" | "github", exactamente estas claves.
 */
```

- [ ] **Paso 4: construir el dock**

Dentro de `mountCaelestiaShell`, después de la barra:

```ts
  // ------------------------------------------------------------------ dock
  // Centrado y dimensionado a su contenido, NO estirado a todo el ancho: un
  // dock estirado se lee como pie de pagina.
  const accesos = contactChannels.map((canal) => {
    const icono = elFromMarkup("cae-dock-icon", ICONOS[canal.key]);
    const enlace = el("a", "cae-dock-item", [icono]);
    enlace.href = canal.href;
    enlace.setAttribute("aria-label", canal.label);
    // La etiqueta visible es un tooltip decorativo; la accesible es aria-label.
    enlace.dataset.caeLabel = canal.value;
    if (canal.external) {
      enlace.target = "_blank";
      enlace.rel = "noopener noreferrer";
      // Punto de "abierto": el dock marca lo que esta corriendo.
      enlace.dataset.caeLive = "";
    }
    return enlace;
  });

  const dock = el("div", "cae-dock", accesos);
  dock.dataset.caeDock = "";
  root.append(dock);
```

Añadir `dock.remove()` al `destroy()` y ajustar el import:

```ts
import { contactChannels, sceneEntries, type ContactChannel } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
```

> Verificado contra `src/data/content.ts:340-347`: `ContactChannel` es
> `{ key, label, value, href, external }`, con `key` tipado como
> `"correo" | "linkedin" | "telefono" | "github"`. Tipar `ICONOS` con
> `Record<ContactChannel["key"], string>` hace que un canal nuevo sin icono **no compile**, que es
> mejor que un `?? "correo"` silencioso.

- [ ] **Paso 5: los estilos del dock**

```css
:root[data-theme="caelestia"] .cae-dock {
  position: fixed;
  bottom: 0.875rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 60;
  display: flex;
  gap: 0.375rem;
  padding: 0.4375rem;
  border-radius: 1.375rem;
  background: var(--cae-elev-2);
  backdrop-filter: blur(16px);
  box-shadow: 0 14px 34px -22px rgb(0 0 0 / 0.55);
  transition: background 0.7s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .cae-dock-item {
  position: relative;
  width: 2.875rem;
  height: 2.875rem;
  border-radius: 0.9375rem;
  display: grid;
  place-items: center;
  background: var(--cae-elev-1);
  color: var(--cae-on-surface-variant);
  transition:
    background 0.28s cubic-bezier(0.2, 0, 0, 1),
    color 0.28s,
    transform 0.28s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .cae-dock-item:hover,
:root[data-theme="caelestia"] .cae-dock-item:focus-visible {
  transform: translateY(-0.4375rem);
  background: var(--cae-anchor);
  color: var(--cae-on-anchor);
}

:root[data-theme="caelestia"] .cae-dock-icon svg {
  width: 1.3125rem;
  height: 1.3125rem;
  display: block;
}

:root[data-theme="caelestia"] .cae-dock-item::after {
  content: attr(data-cae-label);
  position: absolute;
  bottom: calc(100% + 0.625rem);
  left: 50%;
  transform: translateX(-50%) translateY(0.25rem);
  white-space: nowrap;
  pointer-events: none;
  font-size: 0.65625rem;
  padding: 0.3125rem 0.625rem;
  border-radius: 0.5625rem;
  background: var(--cae-on-surface);
  color: var(--cae-surface);
  opacity: 0;
  transition: opacity 0.2s, transform 0.24s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .cae-dock-item:hover::after,
:root[data-theme="caelestia"] .cae-dock-item:focus-visible::after {
  opacity: 1;
  transform: translateX(-50%);
}

:root[data-theme="caelestia"] .cae-dock-item[data-cae-live]::before {
  content: "";
  position: absolute;
  bottom: 0.25rem;
  left: 50%;
  transform: translateX(-50%);
  width: 0.25rem;
  height: 0.25rem;
  border-radius: 50%;
  background: var(--cae-anchor);
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] .cae-dock-item,
  :root[data-theme="caelestia"] .cae-dock-item::after {
    transition: none;
  }
  :root[data-theme="caelestia"] .cae-dock-item:hover {
    transform: none;
  }
}
```

- [ ] **Paso 6: arnés, build, lint y commit**

```bash
npm run build && npm run lint && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
git add -A src/ scripts/
git commit -m "feat(caelestia): dock centrado con iconos, tooltip y punto de abierto

Centrado y dimensionado a su contenido: estirado a todo el ancho se lee
como pie de pagina. Los href salen de contactChannels, no de literales.
El arnes comprueba aria-label, rel noopener e icono en cada acceso."
```

---

## Tarea 6 · La notificación

**Archivos:**
- Modificar: `src/components/caelestiaShell.ts`
- Modificar: `src/themes/themes.css`

**Interfaces:**
- Consume: el evento `caelestia:esquema` que emite `mountCaelestiaColor` (Tarea 1) con
  `detail: { oscuro: boolean }`, y `identity.availability` de `src/data/content.ts`.
- Produce: nada nuevo hacia fuera.

- [ ] **Paso 1: aserción en el arnés**

```python
        # ---- 8. la notificacion de disponibilidad aparece y no roba el foco
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        aviso = page.evaluate(
            """() => {
                const t = document.querySelector('[data-cae-toast]');
                if (!t) return null;
                return {
                  visible: t.classList.contains('is-open'),
                  live: t.getAttribute('aria-live'),
                  robaFoco: document.activeElement === t || t.contains(document.activeElement),
                };
            }"""
        )
        if aviso is None:
            fallos.append("no existe [data-cae-toast]")
        else:
            if not aviso["visible"]:
                fallos.append("la notificacion de disponibilidad no llego a mostrarse")
            if aviso["live"] != "polite":
                fallos.append("la notificacion tiene aria-live=%r, esperado 'polite'" % aviso["live"])
            if aviso["robaFoco"]:
                fallos.append("la notificacion roba el foco")
        ctx.close()
```

Correr. Esperado: `no existe [data-cae-toast]`.

- [ ] **Paso 2: escribir la notificación**

En `mountCaelestiaShell`, después del dock:

```ts
  // --------------------------------------------------------- notificaciones
  const avisoTitulo = el("b", "cae-toast-t");
  const avisoDetalle = el("span", "cae-toast-s");
  const avisoPunto = el("i", "cae-dot");
  const aviso = el("aside", "cae-toast", [
    avisoPunto,
    el("span", "cae-toast-body", [avisoTitulo, avisoDetalle]),
  ]);
  aviso.dataset.caeToast = "";
  // `polite`, no `assertive`: informa, no interrumpe. Y nunca toma el foco.
  aviso.setAttribute("aria-live", "polite");
  root.append(aviso);

  let cierre = 0;
  const notificar = (titulo: string, detalle: string): void => {
    avisoTitulo.textContent = titulo;
    avisoDetalle.textContent = detalle;
    aviso.classList.add("is-open");
    window.clearTimeout(cierre);
    cierre = window.setTimeout(() => aviso.classList.remove("is-open"), 4200);
  };

  const alCambiarEsquema = (evento: Event): void => {
    if (!(evento instanceof CustomEvent)) return;
    const detalle: unknown = evento.detail;
    if (typeof detalle !== "object" || detalle === null || !("oscuro" in detalle)) return;
    const oscuro = Boolean((detalle as { oscuro: unknown }).oscuro);
    notificar(
      oscuro ? "El escritorio ha cambiado a modo noche" : "El escritorio ha vuelto a modo día",
      "El esquema se decide con tu reloj",
    );
  };
  document.documentElement.addEventListener("caelestia:esquema", alCambiarEsquema);
  limpiadores.push(() =>
    document.documentElement.removeEventListener("caelestia:esquema", alCambiarEsquema),
  );

  // Primer aviso: el estado, que es lo que un reclutador viene a saber.
  const primerAviso = window.setTimeout(() => {
    notificar(identity.availability, `${identity.now} · ${identity.location}`);
  }, 900);
```

En `destroy()`: `window.clearTimeout(primerAviso); window.clearTimeout(cierre); aviso.remove();`

Import: `import { contactChannels, identity, sceneEntries } from "../data/content";`

- [ ] **Paso 3: estilos**

```css
:root[data-theme="caelestia"] .cae-toast {
  position: fixed;
  right: 0.875rem;
  bottom: 5.5rem;
  z-index: 61;
  max-width: 17rem;
  display: flex;
  gap: 0.625rem;
  align-items: flex-start;
  padding: 0.75rem 0.875rem;
  border-radius: 1.125rem;
  background: var(--cae-elev-2);
  backdrop-filter: blur(18px);
  box-shadow: 0 18px 40px -22px rgb(0 0 0 / 0.6);
  transform: translateY(0.875rem);
  opacity: 0;
  pointer-events: none;
  transition:
    transform 0.42s cubic-bezier(0.2, 0, 0, 1),
    opacity 0.32s,
    background 0.7s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .cae-toast.is-open {
  transform: none;
  opacity: 1;
}

:root[data-theme="caelestia"] .cae-toast .cae-dot {
  margin-top: 0.25rem;
  flex-shrink: 0;
}

:root[data-theme="caelestia"] .cae-toast-t {
  display: block;
  font-size: 0.71875rem;
  margin-bottom: 0.125rem;
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .cae-toast-s {
  font-size: 0.65625rem;
  line-height: 1.4;
  color: var(--cae-on-surface-variant);
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] .cae-toast {
    transition: opacity 0.01ms;
    transform: none;
  }
}
```

- [ ] **Paso 4: arnés, build, lint y commit**

```bash
npm run build && npm run lint && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
git add -A src/ scripts/
git commit -m "feat(caelestia): notificaciones del shell -- estado y cambio de esquema

El cambio de esquema es instantaneo por construccion, asi que hace falta
que el shell lo anuncie: es lo que hace un escritorio. aria-live polite y
sin robar el foco."
```

---

## Tarea 7 · El cambio de workspace

**La tarea de más riesgo del plan.** Léela entera antes de tocar nada.

**Archivos:**
- Crear: `src/themes/caelestia.choreography.ts`
- Modificar: `src/themes/caelestia.ts` (añadir el gancho `choreography`)
- Modificar: `src/components/caelestiaShell.ts` (conectar `setScene`)
- Modificar: `src/themes/themes.css`

**Interfaces:**
- Consume: `ChoreographyContext` de `src/themes/choreography.ts`
  (`{ gsap, ScrollTrigger, root, motion }`), el evento `caelestia:workspace` de la Tarea 4, y los
  cinco ids de ancla que pone `main.ts` (`hero`, `quien-es`, `obra`, `creditos`, `contacto`).
- Produce: `export const caelestiaChoreography: Choreography`.

> **Recordatorio de la corrección del spec:** Lenis **no está montado** en Caelestia
> (`reveal.ts:253` solo lo monta para `motion.style === "cinematic"`, que es Vice). No hay nada que
> desactivar. Lo que sí hay que hacer es que las cinco escenas dejen de apilarse en vertical y
> pasen a ser un carril horizontal.

- [ ] **Paso 1: aserción en el arnés**

```python
        # ---- 9. cambio de workspace: la pagina no desplaza, el carril si
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        alturaDoc = page.evaluate("document.documentElement.scrollHeight - window.innerHeight")
        if alturaDoc > 4:
            fallos.append("la pagina sigue desplazando en Caelestia: sobran %dpx" % alturaDoc)

        page.eval_on_selector_all("[data-cae-ws]", "bs => bs[2].click()")
        page.wait_for_timeout(900)
        estado = page.evaluate(
            """() => {
                const t = document.querySelector('[data-cae-track]');
                const activa = document.querySelector('[data-cae-ws][aria-current="true"]');
                return {
                  transform: t ? getComputedStyle(t).transform : null,
                  activa: activa ? activa.dataset.caeWs : null,
                };
            }"""
        )
        if estado["activa"] != "obra":
            fallos.append("tras pulsar la tercera pastilla, la activa es %r" % estado["activa"])
        if not estado["transform"] or estado["transform"] == "none":
            fallos.append("el carril no se ha movido: transform %r" % estado["transform"])

        # Los anclas siguen resolviendo en los tres temas (sceneNav depende de ellos).
        ctx.close()
        for tema in ("vice", "hyprland", "caelestia"):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            page = ctx.new_page()
            page.goto(args.base + "/?theme=" + tema, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            faltan = page.evaluate(
                """() => ['hero','quien-es','obra','creditos','contacto']
                     .filter(id => !document.getElementById(id))"""
            )
            if faltan:
                fallos.append("%s: anclas ausentes %s" % (tema, faltan))
            ctx.close()
```

Correr. Esperado: `la pagina sigue desplazando en Caelestia`.

- [ ] **Paso 2: escribir la coreografía**

Crear `src/themes/caelestia.choreography.ts`:

```ts
import type { Choreography } from "./choreography";

/**
 * La coreografia de Caelestia: las cinco escenas dejan de apilarse en vertical
 * y pasan a ser un carril horizontal de workspaces. Un espacio de trabajo no
 * se desplaza, se cambia — es el gesto que sostiene la metafora de escritorio.
 *
 * Lenis NO interviene aqui: `reveal.ts` solo lo monta para `motion.style ===
 * "cinematic"`, que es Vice. Ver la correccion del 2026-08-20 en el spec.
 *
 * ScrollTrigger tampoco: en Caelestia no hay pins. Se recibe en el contexto
 * porque el contrato es comun a los tres temas, y se usa solo para refrescar
 * al cambiar el tamano de la ventana.
 */
const DURACION = 0.52;
const CURVA = "power3.inOut";

export const caelestiaChoreography: Choreography = ({ gsap, ScrollTrigger, root }) => {
  const main = root.querySelector<HTMLElement>("main");
  if (!main) return;

  const escenas = Array.from(main.children).filter(
    (nodo): nodo is HTMLElement => nodo instanceof HTMLElement,
  );
  if (escenas.length === 0) return;

  main.dataset.caeTrack = "";
  root.dataset.caeShell = "workspaces";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let actual = 0;

  const irA = (indice: number): void => {
    const destino = Math.max(0, Math.min(indice, escenas.length - 1));
    actual = destino;
    // fromTo con los dos extremos escritos a mano: `gsap.from` esta prohibido
    // en este proyecto y ya provoco tres regresiones reales.
    gsap.fromTo(
      main,
      { xPercent: -100 * (destino === 0 ? 0 : destino) },
      {
        xPercent: -100 * destino,
        duration: reduce ? 0 : DURACION,
        ease: CURVA,
        overwrite: "auto",
      },
    );
  };

  // Estado inicial explicito, sin leer el DOM.
  gsap.set(main, { xPercent: 0 });

  const alCambiar = (evento: Event): void => {
    if (!(evento instanceof CustomEvent)) return;
    const detalle: unknown = evento.detail;
    if (typeof detalle !== "object" || detalle === null || !("index" in detalle)) return;
    const indice = Number((detalle as { index: unknown }).index);
    if (!Number.isFinite(indice)) return;
    irA(indice);
  };
  root.addEventListener("caelestia:workspace", alCambiar);

  const alRedimensionar = (): void => {
    gsap.set(main, { xPercent: -100 * actual });
    ScrollTrigger.refresh();
  };
  window.addEventListener("resize", alRedimensionar);

  /*
   * Sin `destroy()` propio: la coreografia se invoca una vez por carga y el
   * arbol muere con la pagina. Los oyentes van sobre `root` y `window`, que
   * tienen el mismo ciclo de vida. Si esto deja de ser cierto (navegacion sin
   * recarga), hay que devolver un limpiador y llamarlo desde `pagehide`.
   */
};
```

- [ ] **Paso 3: engancharla al tema**

En `src/themes/caelestia.ts`:

```ts
  async choreography() {
    const { caelestiaChoreography } = await import("./caelestia.choreography");
    return caelestiaChoreography;
  },
```

> Esto además **saca a Caelestia de la rama genérica de `reveal.ts`**, que para el estilo `fluid`
> usa `gsap.from` — prohibido por `CLAUDE.md`. Es una mejora colateral, no un efecto secundario a
> vigilar.

- [ ] **Paso 4: sincronizar la pastilla activa**

En `main.ts`, dentro del bloque de Caelestia:

```ts
  app.addEventListener("caelestia:workspace", (evento) => {
    if (!(evento instanceof CustomEvent)) return;
    const detalle: unknown = evento.detail;
    if (typeof detalle !== "object" || detalle === null || !("index" in detalle)) return;
    const indice = Number((detalle as { index: unknown }).index);
    if (Number.isFinite(indice)) caeShellHandle?.setScene(indice);
  });
```

- [ ] **Paso 5: el carril en CSS**

```css
/*
 * El carril de workspaces. La pagina deja de desplazar en vertical: las cinco
 * escenas van en fila y lo que se mueve es el carril.
 */
:root[data-theme="caelestia"][data-cae-shell="workspaces"] {
  overflow: hidden;
}

:root[data-theme="caelestia"][data-cae-shell="workspaces"] body {
  overflow: hidden;
  height: 100dvh;
}

:root[data-theme="caelestia"] main[data-cae-track] {
  display: flex;
  flex-wrap: nowrap;
  width: 100%;
  height: 100dvh;
  /* Hueco para la barra arriba y el dock abajo. */
  padding: 4.25rem 0.875rem 5.25rem;
  will-change: transform;
}

:root[data-theme="caelestia"] main[data-cae-track] > * {
  flex: 0 0 100%;
  max-width: 100%;
  height: 100%;
  /* La ventana desplaza su contenido. Un escritorio cambia de espacio de un
     golpe, y la ventana que hay dentro tiene su barra. */
  overflow-y: auto;
  overscroll-behavior: contain;
  border-radius: 1.25rem;
  background: var(--cae-elev-1);
  transition: background 0.7s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] main[data-cae-track] > *::-webkit-scrollbar {
  width: 0.5625rem;
}

:root[data-theme="caelestia"] main[data-cae-track] > *::-webkit-scrollbar-thumb {
  background: var(--cae-outline);
  border-radius: 999px;
  border: 3px solid transparent;
  background-clip: content-box;
}
```

- [ ] **Paso 6: arnés completo, y la comprobación que protege a los otros dos temas**

```bash
npm run build && npm run lint && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
```

Esperado: `OK`, incluida la comprobación de que los cinco anclas siguen resolviendo en **los tres**
temas.

**Y además, capturas comparadas de Vice y Hyprland contra el estado anterior:**

```bash
git stash list   # comprobar que esta vacio antes de nada

# Comparar contra HEAD con worktree, NUNCA con git stash:
# un `stash --include-untracked` ya se llevo por delante una sesion entera.
git worktree add /tmp/cae-base HEAD~1
cd /tmp/cae-base && npm ci && npm run build && npx vite preview --port 4174 &
```

Con los dos servidores levantados (4173 = rama, 4174 = base):

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for tema in ('vice','hyprland'):
        for puerto, etiqueta in ((4173,'rama'), (4174,'base')):
            pg = b.new_page(viewport={'width':1440,'height':900})
            pg.goto('http://localhost:%d/?theme=%s' % (puerto, tema), wait_until='domcontentloaded')
            pg.wait_for_timeout(9000)
            pg.screenshot(path='/tmp/cmp-%s-%s.png' % (tema, etiqueta), full_page=True)
            pg.close()
    b.close()
"
```

**Míralas de verdad, las cuatro.** El fondo es generativo y no serán idénticas píxel a píxel; lo
que tiene que ser idéntico es el **layout**: posiciones, tamaños, tipografía, orden. Si algo se ha
movido en Vice o en Hyprland, para y arréglalo antes de commitear.

```bash
git worktree remove /tmp/cae-base
```

- [ ] **Paso 7: commit**

```bash
git add -A src/ scripts/
git commit -m "feat(caelestia): las cinco escenas pasan a ser un carril de workspaces

Un espacio de trabajo no se desplaza, se cambia. La pagina deja de tener
scroll vertical en Caelestia y la ventana de cada escena desplaza su
propio contenido.

Lenis no intervino: reveal.ts solo lo monta para motion.style cinematic,
que es Vice. El arnes comprueba que los cinco anclas siguen resolviendo en
los tres temas, y hay capturas comparadas de Vice y Hyprland contra HEAD~1."
```

---

## Tarea 8 · El wallpaper provisional y la retirada de los blobs

**Archivos:**
- Modificar: `src/backgrounds/caelestiaBlobs.ts`

**Interfaces:**
- Consume: `--cae-hue` (Tarea 1) y `mountShaderBackground` de `shaderBackground.ts`
  (**que no se modifica**).
- Produce: `mountCaelestiaBlobs` con la misma firma que ahora — `(container) => BackgroundHandle`.

> **El wallpaper generativo definitivo es una fase propia**, no está diseñado y no se inventa aquí.
> Lo que hace esta tarea es quitarle al shader su color propio para que deje de contradecir al
> motor: el fondo pasa a ser una versión difusa del mismo matiz que gobierna la hora, en vez de
> cuatro pasteles fijos que van por su cuenta.

- [ ] **Paso 1: aserción en el arnés**

```python
        # ---- 10. el fondo sigue el matiz de la hora, no trae color propio
        muestras = {}
        for minutos in (300, 660, 1020, 1380):
            ctx = nav.new_context(viewport={"width": 1440, "height": 900})
            ctx.add_init_script("(%s)(%d)" % (RELOJ, minutos))
            page = ctx.new_page()
            page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(6000)
            png = page.screenshot(clip={"x": 0, "y": 0, "width": 200, "height": 200})
            muestras[minutos] = len(png)   # proxy barato: el PNG cambia si cambia el color
            ctx.close()
        if len(set(muestras.values())) < 3:
            fallos.append("el fondo apenas cambia con la hora: %s" % muestras)
```

> Es un proxy, y hay que decirlo: compara el tamaño del PNG, no el color. Sirve para detectar un
> fondo **congelado**, no para validar el matiz. El matiz ya lo valida la aserción 2 sobre
> `--cae-hue`. No lo conviertas en un umbral fino: sería medir ruido.

- [ ] **Paso 2: reescribir el shader**

`src/backgrounds/caelestiaBlobs.ts`:

```ts
import { mountShaderBackground, type BackgroundHandle } from "./shaderBackground";

/**
 * El wallpaper de Caelestia.
 *
 * PROVISIONAL: el fondo generativo definitivo es una fase propia y aun no esta
 * disenado. Lo que hace esta version es dejar de traer color propio — los
 * cuatro pasteles fijos que habia contradecian al motor de la hora — y pasar a
 * ser una version difusa del mismo matiz que gobierna el tema.
 *
 * El matiz llega por `--cae-hue`, que escribe `caelestia.color.ts`.
 */
const FRAGMENT_SHADER = /* glsl */ `
  uniform float uTime;
  uniform vec2 uResolution;
  uniform float uHue;
  uniform float uDark;
  varying vec2 vUv;

  // OkLCH -> sRGB aproximado, suficiente para un fondo desenfocado.
  vec3 fromHue(float hue, float l, float c) {
    float h = radians(hue);
    float a = cos(h) * c;
    float b = sin(h) * c;
    float l_ = l + 0.3963377774 * a + 0.2158037573 * b;
    float m_ = l - 0.1055613458 * a - 0.0638541728 * b;
    float s_ = l - 0.0894841775 * a - 1.2914855480 * b;
    vec3 lms = vec3(l_ * l_ * l_, m_ * m_ * m_, s_ * s_ * s_);
    return clamp(mat3(
       4.0767416621, -1.2684380046, -0.0041960863,
      -3.3077115913,  2.6097574011, -0.7034186147,
       0.2309699292, -0.3413193965,  1.7076147010
    ) * lms, 0.0, 1.0);
  }

  void main() {
    vec2 uv = vUv;
    float t = uTime * 0.05;

    float lBase = mix(0.975, 0.175, uDark);
    float lBlob = mix(0.930, 0.245, uDark);

    vec3 col = fromHue(uHue, lBase, 0.010);

    vec2 c1 = vec2(0.22 + sin(t * 0.85) * 0.10, 0.26 + cos(t * 0.65) * 0.10);
    vec2 c2 = vec2(0.80 + cos(t * 0.55) * 0.11, 0.64 + sin(t * 0.75) * 0.10);
    vec2 c3 = vec2(0.52 + sin(t * 0.45 + 1.7) * 0.14, 0.90 + cos(t * 0.60) * 0.08);

    col = mix(col, fromHue(uHue, lBlob, 0.075), smoothstep(0.46, 0.0, length(uv - c1)) * 0.70);
    col = mix(col, fromHue(mod(uHue + 42.0, 360.0), lBlob, 0.060), smoothstep(0.42, 0.0, length(uv - c2)) * 0.60);
    col = mix(col, fromHue(mod(uHue + 318.0, 360.0), lBlob, 0.050), smoothstep(0.48, 0.0, length(uv - c3)) * 0.52);

    col += (hash(uv * uResolution + t) - 0.5) * 0.010;

    gl_FragColor = vec4(col, 1.0);
  }
`;

export function mountCaelestiaBlobs(container: HTMLElement): BackgroundHandle {
  return mountShaderBackground(container, FRAGMENT_SHADER);
}
```

> **Antes de escribir esto, lee `shaderBackground.ts`** y comprueba cómo se declaran los uniforms
> dinámicos: Hyprland ya pasa uniforms propios (ver `src/backgrounds/hyprEmber.ts` y el cableado en
> `src/themes/hyprland.ts`). **Sigue ese mecanismo exacto para `uHue` y `uDark`.** Si
> `shaderBackground.ts` no admite uniforms adicionales sin modificarlo, **para**: modificarlo está
> prohibido por el spec, y hay que resolverlo pasando el matiz por otra vía (por ejemplo, un
> `--cae-hue` leído desde el propio módulo con `getComputedStyle` en el bucle de render).

- [ ] **Paso 3: arnés, build, lint, captura y commit**

```bash
npm run build && npm run lint && npx vite preview --port 4173 &
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
git add -A src/ scripts/
git commit -m "feat(caelestia): el wallpaper deja de traer color propio

Los cuatro pasteles fijos contradecian al motor de la hora. Provisional:
el fondo generativo definitivo es una fase propia."
```

---

## Tarea 9 · Móvil, 390x844

**Archivos:**
- Modificar: `src/themes/themes.css`

**Interfaces:** ninguna nueva.

El spec lo deja como pregunta abierta. **Decisión para este plan:** a menos de 821px las pastillas
se quedan en el número (el nombre se oculta) y el dock reduce la celda a 2.375rem. Ni se colapsa el
dock ni se esconde la barra: las dos son la navegación entera del tema.

- [ ] **Paso 1: aserción en el arnés**

```python
        # ---- 11. movil: nada se sale del viewport
        ctx = nav.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        desbordes = page.evaluate(
            """() => ['[data-cae-bar]','[data-cae-dock]','[data-cae-toast]']
                 .map(sel => {
                   const n = document.querySelector(sel);
                   if (!n) return sel + ' ausente';
                   const r = n.getBoundingClientRect();
                   return (r.right > 391 || r.left < -1) ? sel + ' se sale: ' + JSON.stringify([r.left, r.right]) : null;
                 }).filter(Boolean)"""
        )
        for d in desbordes:
            fallos.append("movil 390: %s" % d)
        if page.evaluate("document.documentElement.scrollWidth > 391"):
            fallos.append("movil 390: la pagina desplaza en horizontal")
        ctx.close()
```

- [ ] **Paso 2: los estilos**

```css
@media (max-width: 820px) {
  :root[data-theme="caelestia"] .cae-bar {
    padding-inline: 0.75rem 0.5rem;
    gap: 0.375rem;
  }

  /* Solo el numero: el nombre no cabe cinco veces a 390px. */
  :root[data-theme="caelestia"] .cae-ws {
    font-size: 0;
    padding: 0.375rem 0.5rem;
  }

  :root[data-theme="caelestia"] .cae-ws-n {
    font-size: 0.75rem;
    opacity: 1;
    margin-right: 0;
  }

  :root[data-theme="caelestia"] .cae-mark,
  :root[data-theme="caelestia"] .cae-avail {
    display: none;
  }

  :root[data-theme="caelestia"] .cae-dock-item {
    width: 2.375rem;
    height: 2.375rem;
  }

  :root[data-theme="caelestia"] .cae-toast {
    left: 0.875rem;
    right: 0.875rem;
    max-width: none;
  }

  :root[data-theme="caelestia"] main[data-cae-track] {
    padding: 3.75rem 0.625rem 4.75rem;
  }
}
```

> **Ojo:** `font-size: 0` en el botón y tamaño real en el `<i>` deja el nombre fuera de la caja
> visual pero **dentro del árbol de accesibilidad**, que es lo que se quiere. No lo cambies por
> `display: none` sobre el texto: eso sí lo quitaría del lector de pantalla.

- [ ] **Paso 3: arnés, captura móvil y commit**

```bash
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':390,'height':844})
    pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded')
    pg.wait_for_timeout(9000)
    pg.screenshot(path='/tmp/cae-movil.png', full_page=True)
    b.close()
"
git add -A src/ scripts/
git commit -m "feat(caelestia): barra y dock a 390px

Las pastillas se quedan en el numero (font-size 0 en el boton, tamano real
en el numero: sale de la caja visual pero NO del arbol de accesibilidad).
El dock reduce la celda. Ninguno de los dos se esconde: son la navegacion."
```

---

## Tarea 10 · Movimiento reducido y accesibilidad

**Archivos:**
- Modificar: `src/themes/themes.css`
- Modificar: `src/themes/caelestia.choreography.ts` (ya lo contempla; verificar)

- [ ] **Paso 1: aserción en el arnés**

```python
        # ---- 12. movimiento reducido: el cambio de workspace es instantaneo
        ctx = nav.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        page.eval_on_selector_all("[data-cae-ws]", "bs => bs[4].click()")
        page.wait_for_timeout(120)   # muy por debajo de los 520 ms de la animacion
        llegado = page.evaluate(
            """() => {
                const t = document.querySelector('[data-cae-track]');
                const m = getComputedStyle(t).transform.match(/-?[\\d.]+/g);
                return m ? Math.abs(Number(m[4])) : 0;
            }"""
        )
        ancho = page.evaluate("window.innerWidth")
        if llegado < ancho * 3.5:
            fallos.append(
                "con movimiento reducido el carril no llego de golpe: %.0f de %.0f"
                % (llegado, ancho * 4)
            )
        ctx.close()

        # ---- 13. el foco es visible y usa el ancla
        ctx = nav.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(args.base + "/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2500)
        page.keyboard.press("Tab")
        page.keyboard.press("Tab")
        contorno = page.evaluate(
            "() => { const e = document.activeElement; return e ? getComputedStyle(e).outlineStyle : null }"
        )
        if contorno in (None, "none"):
            fallos.append("el elemento con foco no tiene contorno visible")
        ctx.close()
```

> **El umbral de 120 ms está elegido con margen deliberado**, no pegado a los 520 ms de la
> animación. `CLAUDE.md` lo dice: un umbral más ajustado que el ruido del instrumento mide carga de
> máquina, no la animación.

- [ ] **Paso 2: el bloque de movimiento reducido**

```css
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] main[data-cae-track],
  :root[data-theme="caelestia"] main[data-cae-track] > *,
  :root[data-theme="caelestia"] .cae-bar,
  :root[data-theme="caelestia"] .cae-dock {
    transition: none;
  }
}
```

Y confirmar que `caelestia.choreography.ts` pone `duration: 0` cuando
`prefers-reduced-motion: reduce` — ya está escrito así en la Tarea 7; **verifícalo, no lo asumas**.

- [ ] **Paso 3: arnés, build, lint y commit**

```bash
git add -A src/ scripts/
git commit -m "feat(caelestia): movimiento reducido y foco visible

El cambio de workspace es instantaneo con reduced-motion. El umbral del
arnes (120 ms contra una animacion de 520) lleva margen a proposito: uno
mas ajustado mediria carga de maquina."
```

---

## Tarea 11 · Gate final

**Archivos:** ninguno de código. Es la puerta antes de proponer merge.

- [ ] **Paso 1: la batería completa**

```bash
npm run build
npm run lint
npx vite preview --port 4173 &
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
python3 scripts/verify.py
```

Los cinco en verde. `verify.py` tiene que salir con **código 0** contra
`scripts/verify-baseline.json`. Si arreglaste algo que estaba en la base, quítalo:

```bash
python3 scripts/verify.py --update-baseline    # y revisa el diff antes de commitear
```

- [ ] **Paso 2: anti-mock**

```bash
grep -rE "mockData|fakeData|hardcoded|TODO.*real|// fake|demo_data|placeholder|lorem ipsum|Lorem" \
  src/ --include="*.ts" --include="*.tsx"
```

Esperado: sin resultados en lo que has tocado. Si aparece algo, **arréglalo, no lo documentes como
deuda**.

- [ ] **Paso 3: capturas reales, no solo headless**

Cuatro como mínimo: Caelestia de día y de noche, en 1440x900 y en 390x844. Y las de control de Vice
y Hyprland de la Tarea 7. **Míralas.** El arnés caza números; las capturas cazan lo que los números
no ven.

- [ ] **Paso 4: consola limpia**

Cero errores JS, cero avisos de contexto WebGL perdido, en los tres temas.

- [ ] **Paso 5: cerrar el estado del spec**

En `docs/superpowers/specs/2026-08-20-caelestia-escritorio-design.md`, cambiar
`Estado: en diseno` por `Estado: implementado` **solo si todas las casillas de este plan están
marcadas**. `verify.py` cruza las dos cosas y falla si el spec dice `implementado` con pasos sin
marcar.

Añadir además una sección `## Registro de implementación` con lo que se desvió del spec y por qué.
Si no se desvió nada, dilo — un registro vacío también es información.

- [ ] **Paso 6: los gates de crítica**

```
Subagente lidia-naive-tester  (flujo y primera impresión)
Subagente vera-art-director   (ejecución visual)
```

**Píname el modelo de los dos subagentes** (`model: sonnet` salvo que la subtarea exija el top):
heredan el modelo de la sesión y un fan-out sin pinear factura todo a tarifa alta.

- [ ] **Paso 7: PROGRESS.json y propuesta de merge**

Actualizar `PROGRESS.json` a `completed` con su `completedAt`, y **pedir aprobación antes de
mergear a `main`**. No mergees por tu cuenta.

---

## Lo que este plan NO hace

Dicho explícitamente para que nadie lo dé por hecho:

- **No diseña el wallpaper generativo definitivo.** La Tarea 8 solo le quita el color propio al
  shader actual. El wallpaper es una fase propia con su spec.
- **No rediseña ninguna sección.** Hero, quién soy, obra, créditos y contacto se quedan como están,
  metidos en la ventana de workspace. Son las fases B1-B5.
- **No resuelve el currículum en PDF** del dock: el fichero no existe, así que la celda no se monta.
  Cuando exista, se añade.
- **No toca Vice ni Hyprland.**

Al terminar, **espera que las secciones se vean mal dentro de la ventana**. Es lo esperado: la
Tarea 7 les cambia el contenedor y su maquetación está pensada para una página que desplaza. Eso es
exactamente el trabajo de la fase B, y este plan lo deja preparado, no resuelto.
