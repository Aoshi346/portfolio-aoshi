# Caelestia B4 — Créditos: la bandeja de paquetes · Plan de implementación

> **Para ejecutores agénticos:** SUB-SKILL OBLIGATORIA: usa
> `superpowers:subagent-driven-development` (recomendada) o
> `superpowers:executing-plans` para ejecutar este plan tarea a tarea. Los pasos
> llevan casilla (`- [ ]`) para marcarlos **en el momento**, no al final.

**Objetivo:** que la escena `#credits` de Caelestia deje de tener scroll interno y rótulos que no
se pintan, y pase a ser una bandeja de gestor de paquetes con las 23 tecnologías siempre en
pantalla y una ficha que se releva al rozar.

**Arquitectura:** un componente nuevo (`src/components/caelestiaCreditosBandeja.ts`) construye su
propio árbol leyendo `skillGroups` y `caseStudies` de `src/data/content.ts`, igual que hizo B3 con
la Editorial. **`src/components/credits.ts` no se toca y no se bifurca por tema**: su DOM genérico
se oculta entero desde `themes.css` bajo `[data-theme="caelestia"]`, que es el patrón que B3 ya
dejó probado. Las 23 figuras se reconstruyen en runtime desde una tabla de 23 filas, no se embeben
como literales.

**Stack:** Vite 8 · TypeScript ~6 `strict` · Tailwind 4 · GSAP 3. Sin framework, sin backend.
Los gates son arneses Playwright en Python contra el **build de producción servido** — no hay
runner de tests JS en el repo y no se añade ninguno.

**Spec:** `docs/superpowers/specs/2026-09-03-caelestia-creditos-design.md` — se lee entero antes de
empezar. El plan argumenta desde ahí.

## Restricciones globales

- **Cero `any`.** `strict` está activo; usa `unknown` + guardas.
- **Nunca `gsap.from`** — `fromTo` con los dos extremos escritos a mano. `Array.from(...)` para
  colecciones vivas.
- **Un `transform` inline de GSAP le gana siempre a una regla CSS**: si un elemento recibe entrada
  con GSAP, su hover se anima en un hijo o en el envoltorio.
- **Todo módulo de tema devuelve un handle con `destroy()`** y se llama en `pagehide`.
- **`prefers-reduced-motion` siempre**, y recuerda que **el selector universal `*` NO alcanza a los
  pseudo-elementos**: cada `::before`/`::after` animado necesita su propia regla.
- **Sin `console.log`** en producción.
- **Cero emojis** en código, docs y commits.
- **La escena no puede tener scroll interno**, ni 10 px. Es la ley de la fase A.
- **Ningún dato inventado.** Todo sale de `src/data/content.ts`. Hay regla anti-mock.
- **Ningún gate se acepta sin haberlo visto dar rojo** contra el fallo exacto que dice cazar.
- **Móvil (390 px) queda FUERA DE ALCANCE**, igual que en B1 y B2 — ver `## Movil (M8)` del spec.
  No lo arregles aquí ni lo empeores; no se añade ninguna regla `@media` nueva para 390.
- Verifica **siempre** contra el build servido (`npm run build && npx vite preview --port 4173`),
  **nunca** contra `npm run dev`: el HMR corrompe las medidas.
- Antes de medir, comprueba de quién es el puerto: `ss -ltnp | grep 4173` y
  `readlink /proc/<pid>/cwd`. Ya hubo 16 `vite preview` huérfanos sirviendo `dist` de worktrees
  borrados, y una medida salió verde contra uno de ellos. **Mata por PID**: `pkill -f "vite
  preview"` se mata a sí mismo desde el harness de Bash, porque el patrón casa con su propia línea
  de comando.
- El tema se sortea por visita: **toda URL lleva `?theme=caelestia`**.
- `npm` necesita Node 22: `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`.
- Cada tarea acaba en commit. `npm run build` y `npm run lint` verdes antes de cada uno.

---

## Estructura de ficheros

| fichero | responsabilidad |
|---|---|
| `src/utils/figurasM3.ts` **(nuevo)** | las 23 figuras: tabla de 23 filas `(slug, tipo, n, a)` y la reconstrucción del `polygon()` a 240 vértices. Nada de DOM. |
| `src/components/caelestiaCreditosBandeja.ts` **(nuevo)** | el árbol de la bandeja, la ficha, la selección y la entrada. Devuelve un handle con `destroy()`. |
| `src/themes/themes.css` *(modificar)* | dentro del bloque `:root[data-theme="caelestia"]`: ocultar el DOM genérico de créditos y estilar la bandeja. |
| `src/main.ts` *(modificar)* | montaje diferido tras la puerta `theme.id === "caelestia"` y `destroy()` en `pagehide`. |
| `scripts/measure-caelestia-creditos.py` **(nuevo)** | el arnés: ocho familias de aserciones. |
| `.claude/rules/verification.md` *(modificar)* | su fila en la tabla de arneses. |
| `CLAUDE.md` y `.claude/CLAUDE.md` *(modificar)* | el bloque de estado de la fase B4. |

**Referencias vivas rescatadas al repo** (ábrelas, no las reinventes):
`docs/superpowers/specs/2026-09-03-caelestia-creditos-maqueta.html` (la bandeja),
`…-extremos.html` (M4), `…-figuras.py` (el generador con sus seis gates).

---

## Task 1: El arnés, con los dos gates que ya dan rojo hoy

No se toca `src/` en esta tarea. Se escribe primero el instrumento y se comprueba que **acusa el
estado actual**; un gate que nace verde no sirve para nada.

**Files:**
- Create: `scripts/measure-caelestia-creditos.py`

**Interfaces:**
- Produce: el script acepta `--base http://localhost:4173`, sale con código 0 si todo pasa y 1 si
  algo falla, e imprime una línea `OK`/`FAIL` por aserción. Mismo contrato que
  `scripts/measure-caelestia-obra.py`.

- [ ] **Paso 1: levantar el build servido y comprobar de quién es el puerto**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
cd /home/aoshi/proyectos/portfolio-aoshi
npm run build
npx vite preview --port 4173 &
sleep 3
ss -ltnp | grep ':4173'                      # anota el pid
readlink /proc/<pid>/cwd                     # tiene que ser este repo, no un worktree borrado
```

- [ ] **Paso 2: escribir el arnés con los gates 1 y 3**

Crea `scripts/measure-caelestia-creditos.py`:

```python
"""Arnes de la escena Creditos de Caelestia (fase B4, la bandeja de paquetes).

Cada familia de aserciones nacio de un fallo real, documentado en su propio
docstring. Ninguna se acepta sin haberla visto dar rojo contra ese fallo.

Se corre SIEMPRE contra el build de produccion servido (`npm run build &&
npx vite preview --port 4173`), nunca contra `npm run dev`: el HMR corrompe
las medidas de layout y de ScrollTrigger, y miente en los dos sentidos.
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

FALLOS: list[str] = []


def check(ok: bool, etiqueta: str) -> None:
    print(("  OK   " if ok else "  FAIL ") + etiqueta)
    if not ok:
        FALLOS.append(etiqueta)


def abre(pagina, base: str) -> None:
    """Abre Creditos y espera a que el workspace asiente.

    Se cambia de workspace pulsando la pastilla del shell, no tocando el hash:
    el hash lo cambia el shell, y forzarlo desde fuera deja el carril a medio
    camino."""
    pagina.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=45000)
    pagina.wait_for_timeout(6000)
    pagina.eval_on_selector_all(
        ".cae-ws",
        "bs=>{const b=bs.find(x=>/Cr..?ditos/.test(x.textContent)); if(b) b.click();}",
    )
    pagina.wait_for_timeout(2500)


def gate_sin_scroll(pagina) -> None:
    """La escena NO puede desplazarse por dentro. Es la ley de la fase A: un
    espacio de trabajo no se desplaza, se cambia.

    Visto rojo con: el estado de partida, 758 / 748 — diez pixeles."""
    print("[1] la escena no tiene scroll interno")
    m = pagina.evaluate(
        """() => {
             const e = document.querySelector('[data-scene="credits"]');
             return {alto: e.scrollHeight, caja: e.clientHeight,
                     ancho: e.scrollWidth, cajaX: e.clientWidth};
           }"""
    )
    check(m["alto"] <= m["caja"], f"sin scroll vertical ({m['alto']} / {m['caja']})")
    check(m["ancho"] <= m["cajaX"], f"sin scroll horizontal ({m['ancho']} / {m['cajaX']})")


def gate_rotulos(pagina) -> None:
    """Los cuatro rotulos de territorio tienen que PINTARSE.

    Visto rojo con: el estado de partida, donde los cuatro existian en el DOM y
    no se pintaba ninguno. Contar nodos no es contar lo que se ve — es el modo
    de fallo central de esta fase, asi que se filtra por getClientRects()."""
    print("[3] los cuatro rotulos de territorio se pintan")
    n = pagina.evaluate(
        """() => [...document.querySelectorAll('[data-scene="credits"] .cae-cred-rot')]
                   .filter(e => e.getClientRects().length > 0).length"""
    )
    check(n == 4, f"cuatro rotulos pintados ({n} de 4)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    with sync_playwright() as p:
        navegador = p.chromium.launch(
            headless=True, args=["--no-sandbox", "--use-gl=swiftshader"]
        )
        pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
        errores: list[str] = []
        pagina.on("pageerror", lambda e: errores.append(str(e)))
        pagina.on(
            "console",
            lambda m: errores.append(m.text) if m.type == "error" else None,
        )

        abre(pagina, args.base)
        gate_sin_scroll(pagina)
        gate_rotulos(pagina)

        print("[0] consola")
        check(not errores, f"cero errores de consola ({errores[:3]})")
        navegador.close()

    print(f"\n{'TODO OK' if not FALLOS else str(len(FALLOS)) + ' FALLOS'}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Paso 3: correrlo y ver que da ROJO**

```bash
python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173
```

Esperado: **FAIL** en `sin scroll vertical (758 / 748)` y en `cuatro rotulos pintados (0 de 4)`.
Salida con código 1.

Si el gate 1 sale verde, algo va mal: o no estás en la escena de créditos, o estás midiendo un
`vite preview` huérfano. Vuelve al paso 1.

- [ ] **Paso 4: commit**

```bash
git add scripts/measure-caelestia-creditos.py
git commit -m "test(creditos): arnes de la fase B4 con los dos gates que acusan el estado actual"
```

---

## Task 2: Las 23 figuras, reconstruidas en runtime

**Files:**
- Create: `src/utils/figurasM3.ts`

**Interfaces:**
- Produce:
  - `export type SlugFigura = string`
  - `export function figuraDe(slug: string): string` — devuelve un `polygon(...)` de 240 vértices.
  - `export function figuraSuaveDe(slug: string): string` — la misma, con el relieve al 42 %.
  - `export const FIGURA_CIRCULO: string` — el círculo de 240 vértices de la entrada.
  - `export function radioInscritoDe(slug: string): number` — para acotar el icono.

**Por qué runtime y no literales:** el generador de referencia emite 167 KB de coordenadas. Medido:
dividir por `rmax` **es redundante** si después se encaja normalizando el vano de cada eje — la
desviación punto a punto entre hacerlo y no hacerlo es de `4.4e-16`, error de coma flotante. Así
que al runtime le bastan `(tipo, n, a)` por figura: 23 filas, menos de 1 KB en el bundle.

- [ ] **Paso 1: comprobar que la tabla del Paso 2 es la que sale del generador**

La tabla ya está escrita abajo. Este paso no la produce: la **verifica**, porque una tabla copiada
a mano se desincroniza en silencio. El despeje por bisección vive en el generador del repo:

```bash
cd /home/aoshi/proyectos/portfolio-aoshi
python3 - <<'PY'
import runpy, math, json
# Se reutiliza el generador de referencia tal cual: sus seis gates son la
# garantia de que la tabla que sale de aqui es la buena.
g = runpy.run_path("docs/superpowers/specs/2026-09-03-caelestia-creditos-figuras.py")
tabla = []
for sl, nom, tipo, n in g["DEF"]:
    a = g["despeja"](g["familia"](tipo, n), nom)
    tabla.append({"slug": sl, "tipo": tipo, "n": n, "a": round(a, 6)})
print(json.dumps(tabla, indent=0))
PY
```

Compara la salida con `AMPLITUDES` del Paso 2: tienen que coincidir en las 23 filas. Si el
generador aborta en un `assert`, uno de sus seis gates ha saltado y **no sigas**: la tabla escrita
abajo dejo de ser valida. Salida esperada del generador antes del JSON:

```
OK · 23 figuras · encajan exactas en su caja (dos ejes) · area dispersion 0.00% · relieve minimo 9.2% · deformacion peor x1.126 · radio inscrito 0.68..0.91
```

- [ ] **Paso 2: escribir `src/utils/figurasM3.ts`**

```ts
/**
 * Las 23 figuras de Material 3 Expressive de la bandeja de Creditos (B4).
 *
 * Todas son la misma curva armonica polar:
 *
 *     r(t) = 1 + a·cos(n·t) + s·cos(2n·t)
 *
 * `n` son los lobulos —lo que distingue una figura de otra— y el signo de `a`
 * decide si son concavos (galleta) o convexos (trebol). UNA sola familia para
 * las 23: con familias de canto recto mezcladas no existe un area comun
 * alcanzable (un hexagono no baja de 3.00 y un cuadrado no baja de 3.147), y el
 * despeje las aplanaba a circulos.
 *
 * Las amplitudes de `AMPLITUDES` salen despejadas por biseccion en
 * `docs/superpowers/specs/2026-09-03-caelestia-creditos-figuras.py`, que ademas
 * lleva los seis gates (23 figuras, 23 unicas, 240 vertices, dispersion de area
 * < 0,5 %, relieve >= 6 %, anisotropia < 1,25). Aqui solo se reconstruye.
 *
 * Se reconstruye en vez de embeber porque el generador emite 167 KB de
 * coordenadas y no hacen falta: medido, dividir por `rmax` es redundante
 * cuando despues se encaja normalizando el VANO de cada eje (desviacion punto
 * a punto 4.4e-16, error de coma flotante).
 */

/** 240 y no menos: dos `polygon()` solo interpolan si tienen el MISMO numero
 *  de puntos. Con distinto, el navegador no morfa — corta de golpe, sin error
 *  y sin aviso. Es la trampa que costo la fase B2. */
const VERTICES = 240;

interface DefFigura {
  readonly tipo: "galleta" | "trebol";
  readonly n: number;
  readonly a: number;
}

/* Pega aqui la tabla del Paso 1, con esta forma. Concavas en Interfaz y
   Herramientas, convexas en Backend y Lenguajes: el territorio ya lo dicen la
   banda y su rotulo, la figura identifica la PIEZA. Ninguna concava por debajo
   de 5 lobulos — con 3 o 4 la cintura se cierra tanto que la figura se lee
   como un aspa y el icono se sale por los brazos. */
const AMPLITUDES: Readonly<Record<string, DefFigura>> = {
  // Interfaz
  react: { tipo: "galleta", n: 5, a: 0.095138 },
  nextdotjs: { tipo: "galleta", n: 6, a: 0.09705 },
  typescript: { tipo: "galleta", n: 7, a: 0.070599 },
  tailwindcss: { tipo: "galleta", n: 8, a: 0.110285 },
  vite: { tipo: "galleta", n: 9, a: 0.059717 },
  gsap: { tipo: "galleta", n: 10, a: 0.061956 },
  electron: { tipo: "galleta", n: 11, a: 0.05384 },
  gtk: { tipo: "galleta", n: 12, a: 0.072186 },
  // Backend y datos
  python: { tipo: "trebol", n: 3, a: 0.183186 },
  django: { tipo: "trebol", n: 4, a: 0.056827 },
  nodedotjs: { tipo: "trebol", n: 5, a: 0.112974 },
  mysql: { tipo: "trebol", n: 6, a: 0.118822 },
  rxdb: { tipo: "trebol", n: 7, a: 0.089681 },
  // Lenguajes base
  javascript: { tipo: "trebol", n: 8, a: 0.056809 },
  html5: { tipo: "trebol", n: 9, a: 0.078557 },
  css: { tipo: "trebol", n: 10, a: 0.082262 },
  c: { tipo: "trebol", n: 11, a: 0.072448 },
  cplusplus: { tipo: "trebol", n: 12, a: 0.05678 },
  // Herramientas
  git: { tipo: "galleta", n: 13, a: 0.050769 },
  github: { tipo: "galleta", n: 14, a: 0.05196 },
  n8n: { tipo: "galleta", n: 15, a: 0.048537 },
  claude: { tipo: "galleta", n: 16, a: 0.058386 },
  googlegemini: { tipo: "galleta", n: 18, a: 0.048394 },
};

type Punto = readonly [number, number];

function radios({ tipo, n, a }: DefFigura, relieve: number): number[] {
  const amp = (tipo === "galleta" ? -a : a) * relieve;
  const seg = (tipo === "galleta" ? a * 0.18 : -a * 0.14) * relieve;
  const rs: number[] = [];
  for (let i = 0; i < VERTICES; i += 1) {
    const t = (i * 2 * Math.PI) / VERTICES;
    rs.push(1 + amp * Math.cos(n * t) + seg * Math.cos(2 * n * t));
  }
  return rs;
}

/**
 * Encaja el poligono en su caja normalizando el VANO de cada eje, y recentra.
 *
 * No vale dividir por `max(abs(x))`: eso es el RADIO, no la semianchura, y en
 * una figura de lobulos impares la silueta no es simetrica respecto al centro.
 * Medido con la version anterior: el trebol de 3 ocupaba 90,4 px de ancho donde
 * el de 4 ocupaba 102 — un 13,7 % menos con el mismo dato, que es exactamente
 * lo que se veia.
 */
function encaja(rs: readonly number[]): Punto[] {
  const p: Punto[] = rs.map((r, i) => {
    const t = (i * 2 * Math.PI) / VERTICES;
    return [r * Math.cos(t), r * Math.sin(t)] as const;
  });
  const xs = p.map(([x]) => x);
  const ys = p.map(([, y]) => y);
  const cx = (Math.max(...xs) + Math.min(...xs)) / 2;
  const cy = (Math.max(...ys) + Math.min(...ys)) / 2;
  const hx = (Math.max(...xs) - Math.min(...xs)) / 2;
  const hy = (Math.max(...ys) - Math.min(...ys)) / 2;
  return p.map(([x, y]) => [(x - cx) / hx, (y - cy) / hy] as const);
}

function poly(p: readonly Punto[]): string {
  return `polygon(${p
    .map(([x, y]) => `${(50 + 50 * x).toFixed(2)}% ${(50 + 50 * y).toFixed(2)}%`)
    .join(", ")})`;
}

const cache = new Map<string, string>();

function figura(slug: string, relieve: number, clave: string): string {
  const memo = cache.get(clave);
  if (memo !== undefined) return memo;
  const def = AMPLITUDES[slug];
  // defensive: un slug nuevo en content.ts sin figura no debe romper la escena;
  // cae al circulo, que es una figura valida de 240 vertices.
  const salida = def ? poly(encaja(radios(def, relieve))) : FIGURA_CIRCULO;
  cache.set(clave, salida);
  return salida;
}

export function figuraDe(slug: string): string {
  return figura(slug, 1, `f:${slug}`);
}

/** Al rozar, la figura se ablanda sin cambiar de caja: mismo numero de
 *  vertices, asi que interpola. */
export function figuraSuaveDe(slug: string): string {
  return figura(slug, 0.42, `s:${slug}`);
}

export const FIGURA_CIRCULO: string = poly(
  encaja(new Array<number>(VERTICES).fill(1)),
);

/** El icono se acota por el radio INSCRITO, no por la caja: en una figura de
 *  lobulos profundos la cintura queda por dentro del canto y el icono se salia
 *  por los brazos. */
export function radioInscritoDe(slug: string): number {
  const def = AMPLITUDES[slug];
  if (!def) return 1;
  return Math.min(...encaja(radios(def, 1)).map(([x, y]) => Math.hypot(x, y)));
}
```

- [ ] **Paso 3: comprobar que el TypeScript reproduce al generador punto a punto**

No basta con que compile: tiene que dar **las mismas coordenadas**.

```bash
cd /home/aoshi/proyectos/portfolio-aoshi
npx tsx --eval '
import { figuraDe, FIGURA_CIRCULO } from "./src/utils/figurasM3";
const salida: Record<string, string> = {};
for (const slug of ["react","nextdotjs","typescript","tailwindcss","vite","gsap","electron","gtk",
  "python","django","nodedotjs","mysql","rxdb","javascript","html5","css","c","cplusplus",
  "git","github","n8n","claude","googlegemini"]) salida[slug] = figuraDe(slug);
salida["__circulo"] = FIGURA_CIRCULO;
console.log(JSON.stringify(salida));
' > /tmp/fig-ts.json

python3 - <<'PY'
import json, runpy
g = runpy.run_path("docs/superpowers/specs/2026-09-03-caelestia-creditos-figuras.py")
ts = json.load(open("/tmp/fig-ts.json"))
peor, cual = 0.0, ""
for slug, ref in g["FIG"].items():
    a = [float(v.rstrip('%')) for v in ref.replace('polygon(','').rstrip(')').replace(',',' ').split()]
    b = [float(v.rstrip('%')) for v in ts[slug].replace('polygon(','').rstrip(')').replace(',',' ').split()]
    assert len(a) == len(b) == 480, f"{slug}: {len(a)} vs {len(b)} coordenadas"
    d = max(abs(x-y) for x, y in zip(a, b))
    if d > peor: peor, cual = d, slug
print(f"desviacion maxima: {peor:.4f}% en «{cual}»")
assert peor < 0.02, "el TypeScript NO reproduce al generador"
assert len(set(ts[s] for s in g["FIG"])) == 23, "hay figuras repetidas"
print("OK · 23 figuras · 240 vertices · identicas al generador")
PY
```

Esperado: `OK · 23 figuras · 240 vertices · identicas al generador`.

Si `npx tsx` no está disponible, instálalo como dependencia de desarrollo
(`npm i -D tsx`) — es una dependencia de proyecto y no requiere permiso.

- [ ] **Paso 4: verlo dar rojo**

Cambia a mano una amplitud de `AMPLITUDES` (por ejemplo `react.a` a `0.9`) y vuelve a correr el
paso 3. Esperado: `AssertionError: el TypeScript NO reproduce al generador`. Deshaz el cambio.

- [ ] **Paso 5: build, lint y commit**

```bash
npm run build && npm run lint
git add src/utils/figurasM3.ts
git commit -m "feat(creditos): las 23 figuras de Material 3, reconstruidas desde una tabla de 23 filas"
```

---

## Task 3: La bandeja — el árbol, el CSS y el cableado

Aquí se cierran los gates 1, 2 y 3. Es la tarea más grande del plan y es indivisible: el árbol sin
CSS no se puede medir, y el CSS sin cableado no llega a la página.

**Files:**
- Create: `src/components/caelestiaCreditosBandeja.ts`
- Modify: `src/themes/themes.css` (dentro del bloque `:root[data-theme="caelestia"]`)
- Modify: `src/main.ts:161-168` (patrón de montaje) y `src/main.ts:283-295` (`pagehide`)
- Modify: `scripts/measure-caelestia-creditos.py`

**Interfaces:**
- Consume: `figuraDe`, `figuraSuaveDe`, `FIGURA_CIRCULO`, `radioInscritoDe` de la Task 2.
- Produce:
  - `export interface CaelestiaCreditosHandle { destroy: () => void }`
  - `export async function mountCaelestiaCreditosBandeja(root: HTMLElement): Promise<CaelestiaCreditosHandle>`
  - Clases que el arnés y el CSS usan: `.cae-cred-wrap`, `.cae-cred-cab`, `.cae-cred-marca`,
    `.cae-cred-nombre`, `.cae-cred-detalle`, `.cae-cred-terr`, `.cae-cred-cruce`, `.cae-cred-grid`,
    `.cae-cred-banda`, `.cae-cred-rot`, `.cae-cred-tira`, `.cae-cred-pieza`, `.cae-cred-fig`.

- [ ] **Paso 1: añadir al arnés el gate 2 (las 23 dentro de la caja)**

Añade a `scripts/measure-caelestia-creditos.py`, y llámalo desde `main()` después de `gate_rotulos`:

```python
def gate_piezas(pagina) -> None:
    """Las 23 tecnologias tienen que estar DENTRO de la caja de la escena, sin
    desplazar. En el estado de partida cuatro de los cinco proyectos de Obra
    quedaban fuera de la ventana por el mismo motivo; aqui se comprueba antes de
    que pase.

    Se compara contra la caja de la escena, no contra el viewport: la ventana
    del workspace mide 1412 x 748 y el viewport 1440 x 900."""
    print("[2] las 23 piezas estan dentro de la caja de la escena")
    m = pagina.evaluate(
        """() => {
             const e = document.querySelector('[data-scene="credits"]');
             const c = e.getBoundingClientRect();
             const t = [...e.querySelectorAll('.cae-cred-pieza')]
                         .filter(x => x.getClientRects().length > 0);
             const fuera = t.filter(x => { const r = x.getBoundingClientRect();
               return r.left < c.left - 1 || r.right > c.right + 1
                   || r.top < c.top - 1 || r.bottom > c.bottom + 1; });
             const lados = [...new Set(t.map(x => Math.round(
               x.querySelector('.cae-cred-fig').getBoundingClientRect().width)))];
             return {n: t.length, fuera: fuera.length, lados};
           }"""
    )
    check(m["n"] == 23, f"23 piezas pintadas ({m['n']})")
    check(m["fuera"] == 0, f"ninguna fuera de la caja ({m['fuera']})")
    # El tamano no codifica nada: las dos varas posibles mienten (vara global
    # infla Herramientas porque `tooling` esta en los cinco proyectos; vara por
    # territorio hace a JavaScript —una obra— tan grande como Git —cinco—).
    check(len(m["lados"]) == 1, f"un solo lado en todo el DOM ({m['lados']})")
```

- [ ] **Paso 2: correr el arnés y ver el gate 2 en rojo**

```bash
python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173
```

Esperado: `FAIL 23 piezas pintadas (0)` — la clase todavía no existe.

- [ ] **Paso 3: escribir el componente**

Crea `src/components/caelestiaCreditosBandeja.ts`. La maqueta viva
(`docs/superpowers/specs/2026-09-03-caelestia-creditos-maqueta.html`) tiene el árbol exacto; esto es
su traducción a TypeScript tipado:

```ts
import { caseStudies, skillGroups } from "../data/content";
import { el, elFromMarkup } from "../utils/dom";
import { figuraDe, figuraSuaveDe, radioInscritoDe } from "../utils/figurasM3";
import { getIconMarkup } from "../utils/icons";

export interface CaelestiaCreditosHandle {
  destroy: () => void;
}

interface Pieza {
  readonly territorio: string;
  readonly name: string;
  readonly slug: string;
  readonly detail: string;
  readonly obras: readonly string[];
}

/** 88 y no 96: al rozar, la figura crece un 7 % (unos 3 px por lado) y con 96
 *  el canto superior llegaba a tocar el filete de la banda anterior. Medido:
 *  22,5 px de holgura en reposo, 19,2 rozando. */
const LADO = 88;

/**
 * El cruce contra las obras se hace contra `stack` Y `tooling`, que es el mismo
 * cruce que hace `credits.ts::toEntry`. Sin el segundo array, Git, GitHub y las
 * dos CLI saldrian como "sin obra publicada" siendo justo lo contrario: estan
 * en todos los proyectos, y no aparecen en `stack` porque `stack` se pinta
 * literal en la ficha de obra y ahi cuatro nombres repetidos no distinguen nada.
 */
function obrasDe(name: string): string[] {
  return caseStudies
    .filter((p) => [...p.stack, ...(p.tooling ?? [])].includes(name))
    .map((p) => p.title);
}

/** Mismo resumen que `credits.ts::textoCruce`, sin duplicar la decision: con
 *  cuatro o cinco obras no se listan los titulos porque no distinguen nada. */
function cruceTexto(obras: readonly string[]): string[] {
  if (obras.length === 5) return ["Los cinco proyectos"];
  if (obras.length === 4) return ["Cuatro de los cinco proyectos"];
  return [...obras];
}

/** El icono se acota por el radio inscrito de SU figura, no por la caja. */
function ladoIcono(slug: string): number {
  const cabe = (LADO * radioInscritoDe(slug) * 0.88) / Math.SQRT2;
  return Math.max(17, Math.round(Math.min(LADO * 0.3, cabe)));
}

function construirPieza(p: Pieza): HTMLButtonElement {
  const fig = el("span", "cae-cred-fig", [
    elFromMarkup("cae-cred-icono", getIconMarkup(p.slug)),
  ]);
  fig.style.setProperty("--fig", figuraDe(p.slug));
  fig.style.setProperty("--fig-suave", figuraSuaveDe(p.slug));
  fig.style.width = `${LADO}px`;
  fig.style.height = `${LADO}px`;
  const icono = fig.firstElementChild as HTMLElement;
  icono.style.width = `${ladoIcono(p.slug)}px`;
  icono.style.height = `${ladoIcono(p.slug)}px`;
  icono.setAttribute("aria-hidden", "true");
  icono.setAttribute("data-decorative", "");

  const boton = el("button", "cae-cred-pieza", [
    fig,
    el("figcaption", "cae-cred-nom", [p.name]),
  ]) as HTMLButtonElement;
  boton.type = "button";
  boton.dataset.pieza = p.name;
  boton.setAttribute("aria-pressed", "false");
  return boton;
}

export async function mountCaelestiaCreditosBandeja(
  root: HTMLElement,
): Promise<CaelestiaCreditosHandle> {
  const escena = root.querySelector<HTMLElement>('[data-scene="credits"]');
  if (!escena) throw new Error("La bandeja de Creditos necesita [data-scene=credits]");

  const { default: gsap } = await import("gsap");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const piezas: Pieza[] = skillGroups.flatMap((g) =>
    g.items.map((it) => ({
      territorio: g.label,
      name: it.name,
      slug: it.slug,
      detail: it.detail,
      obras: obrasDe(it.name),
    })),
  );

  // La cabecera se releva EN EL SITIO: 96 px fijos, nada mas se mueve.
  const marca = el("span", "cae-cred-marca", []);
  const nombre = el("h3", "cae-cred-nombre", []);
  const detalle = el("p", "cae-cred-detalle", []);
  const territorio = el("p", "cae-cred-terr", []);
  const cruceLista = el("ul", "cae-cred-cruce-lista", []);
  const cruce = el("div", "cae-cred-cruce", [
    el("span", "", ["Aparece en"]),
    cruceLista,
  ]);
  const cabecera = el("div", "cae-cred-cab", [
    marca,
    el("div", "", [nombre, detalle, territorio]),
    cruce,
  ]);

  const bandas = skillGroups.map((g) => {
    const tira = el(
      "div",
      "cae-cred-tira",
      g.items.map((it) =>
        construirPieza(piezas.find((p) => p.name === it.name) as Pieza),
      ),
    );
    // El filete de la banda llega solo hasta su ultima pieza, asi que su LARGO
    // es la masa del territorio. Dice el recuento sin escribir el numero, y
    // sale de `items.length`, no de un dato nuevo.
    tira.style.setProperty("--piezas", String(g.items.length));
    return el("div", "cae-cred-banda", [
      el("div", "cae-cred-rot", [el("h4", "", [g.label])]),
      tira,
    ]);
  });

  const wrap = el("div", "cae-cred-wrap", [cabecera, el("div", "cae-cred-grid", bandas)]);
  escena.append(wrap);

  function pintarFicha(p: Pieza): void {
    marca.replaceChildren(elFromMarkup("", getIconMarkup(p.slug)));
    marca.style.clipPath = figuraDe(p.slug);
    nombre.textContent = p.name;
    detalle.textContent = p.detail;
    territorio.textContent = p.territorio;
    const lineas = cruceTexto(p.obras);
    cruceLista.replaceChildren(
      ...(p.obras.length === 0
        ? [el("li", "is-vacia", ["Sin obra publicada"])]
        : lineas.map((t) => el("li", "", [t]))),
    );
  }

  pintarFicha(piezas[0]);

  return {
    destroy: () => {
      gsap.killTweensOf(escena.querySelectorAll("*"));
      wrap.remove();
    },
  };
}
```

- [ ] **Paso 4: el CSS**

Añade al final del bloque `:root[data-theme="caelestia"]` de `src/themes/themes.css`. Copia los
valores de la maqueta rescatada; esto es lo mínimo que cierran los gates 1–3:

```css
/*
 * Fase B4 — Creditos deja de ser el reparto de parcelas y pasa a ser la
 * bandeja del gestor de paquetes. El DOM generico de `credits.ts` (parcelas,
 * frisos, panel, rodillo) no sirve aqui: se oculta entero y
 * `caelestiaCreditosBandeja.ts` construye su propio arbol leyendo
 * `skillGroups` directamente, igual que hizo B3 con la Editorial. Ese fichero
 * lo comparten los tres temas y NO se bifurca.
 */
:root[data-theme="caelestia"] .credits-grid {
  display: none;
}

:root[data-theme="caelestia"] .cae-cred-wrap {
  height: 100%;
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 0;
}

:root[data-theme="caelestia"] .cae-cred-cab {
  display: grid;
  grid-template-columns: 52px 1fr auto;
  gap: 18px;
  align-items: center;
  height: 96px;
  margin-bottom: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--cae-outline);
}

/* Cuatro bandas de la MISMA altura. Con `space-between` sobre cajas de altura
   distinta el aire salia desigual y la bandeja volvia a leerse suelta. */
:root[data-theme="caelestia"] .cae-cred-grid {
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  min-height: 0;
}

:root[data-theme="caelestia"] .cae-cred-banda {
  display: grid;
  grid-template-columns: 158px 1fr;
  gap: 0 22px;
  align-items: center;
  padding-bottom: 14px;
}

/* El rotulo va al centro vertical de SU banda y a bandera derecha contra el
   canto de la calle, para que los cuatro caigan sobre el mismo eje. */
:root[data-theme="caelestia"] .cae-cred-rot {
  text-align: right;
  align-self: center;
}

:root[data-theme="caelestia"] .cae-cred-tira {
  position: relative;
  display: grid;
  grid-template-columns: repeat(8, 142px);
  align-items: end;
  justify-items: center;
  padding-top: 8px;
}

/* El filete llega solo hasta la ultima pieza de la banda. */
:root[data-theme="caelestia"] .cae-cred-banda:not(:last-child) .cae-cred-tira::after {
  content: "";
  position: absolute;
  bottom: -14px;
  left: 0;
  height: 1px;
  width: calc(var(--piezas) * 142px);
  background: var(--cae-outline);
}

:root[data-theme="caelestia"] .cae-cred-pieza {
  border: 0;
  background: none;
  font: inherit;
  color: inherit;
  cursor: pointer;
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 0;
}

:root[data-theme="caelestia"] .cae-cred-fig {
  clip-path: var(--fig);
  display: grid;
  place-items: center;
  /* Relleno en `--cae-outline`: `--cae-surface-container` es EXACTAMENTE
     `--cae-elev-1`, el fondo de la ventana, asi que rellenar con el borra la
     figura. Lo mismo vale para apagarla: se apaga la tinta, nunca el fondo. */
  background: var(--cae-outline);
}

:root[data-theme="caelestia"] .cae-cred-pieza:focus-visible {
  outline: 2px solid var(--cae-anchor);
  outline-offset: 5px;
  border-radius: 10px;
}
```

- [ ] **Paso 5: cablear en `src/main.ts`**

Junto al montaje de la Editorial (alrededor de la línea 161), con el mismo patrón:

```ts
// La bandeja de Creditos en Caelestia: cuatro bandas y 23 piezas siempre en
// pantalla. Import diferido, igual que el resto de modulos de tema.
let caeCreditosHandle: { destroy: () => void } | null = null;
if (theme.id === "caelestia") {
  void import("./components/caelestiaCreditosBandeja").then(
    async ({ mountCaelestiaCreditosBandeja }) => {
      caeCreditosHandle = await mountCaelestiaCreditosBandeja(app);
    },
  );
}
```

Y en el `pagehide`, junto a `caeObraHandle?.destroy();`:

```ts
    caeCreditosHandle?.destroy();
```

- [ ] **Paso 6: build y volver a medir — los tres gates en verde**

```bash
npm run build && npm run lint
kill <pid-del-preview>; npx vite preview --port 4173 & sleep 3
python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173
```

Esperado: OK en `sin scroll vertical (748 / 748)`, `cuatro rotulos pintados (4 de 4)`,
`23 piezas pintadas (23)`, `ninguna fuera de la caja (0)`, `un solo lado en todo el DOM (['88px'])`
y `cero errores de consola`.

- [ ] **Paso 7: captura real, no sólo números**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded', timeout=45000)
    pg.wait_for_timeout(6000)
    pg.eval_on_selector_all('.cae-ws', 'bs=>{const b=bs.find(x=>/Cr..?ditos/.test(x.textContent)); if(b) b.click();}')
    pg.wait_for_timeout(2500)
    pg.screenshot(path='/tmp/b4-bandeja.png')
    b.close()
"
```

Ábrela. Los números pueden estar verdes con el resultado roto — ya pasó en esta fase. Compárala
contra `docs/superpowers/specs/2026-09-03-caelestia-creditos-maqueta.html`.

- [ ] **Paso 8: commit**

```bash
git add src/components/caelestiaCreditosBandeja.ts src/themes/themes.css src/main.ts scripts/measure-caelestia-creditos.py
git commit -m "feat(creditos): la bandeja de paquetes sustituye al reparto de parcelas en Caelestia"
```

---

## Task 4: La ficha y el cruce — los dos defectos que cazó M4

**Files:**
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-caelestia-creditos.py`

**Interfaces:**
- Consume: `.cae-cred-cruce`, `.cae-cred-cruce-lista`, `.cae-cred-terr` de la Task 3.

- [ ] **Paso 1: añadir el gate 6 al arnés**

```python
def gate_cruce(pagina) -> None:
    """El cruce «Aparece en» tiene que caber en los 96 px de cabecera en LAS 23
    piezas, y el estado vacio tiene que leerse.

    Visto rojo con: TypeScript (tres obras) apilaba tres renglones, 111 px en
    una cabecera de 96 — se salia 15 contra el filete de la primera banda. Y
    «Sin obra publicada» iba en `--cae-outline`: 1,80:1 de noche, 2,34:1 a las
    09:00, en 7 de las 23 piezas.

    El contraste se mide PINTANDO el color en un lienzo 1x1 y leyendo el pixel.
    Leer `oklch(...)` con una regex como si fueran bytes RGB da 1.00:1 en todo
    — la trampa que ya costo la fase A."""
    print("[6] el cruce cabe en la cabecera y el estado vacio se lee")
    peor = pagina.evaluate(
        """() => {
          const px = c => { const k=document.createElement('canvas'); k.width=k.height=1;
            const x=k.getContext('2d'); x.fillStyle='#000'; x.fillRect(0,0,1,1);
            x.fillStyle=c; x.fillRect(0,0,1,1);
            const d=x.getImageData(0,0,1,1).data; return [d[0],d[1],d[2]]; };
          const lum = r => { const f=r.map(v=>{v/=255;
            return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4);});
            return 0.2126*f[0]+0.7152*f[1]+0.0722*f[2]; };
          const rat = (a,b) => { const la=lum(px(a)), lb=lum(px(b));
            const h=Math.max(la,lb), l=Math.min(la,lb); return (h+0.05)/(l+0.05); };
          // El contenedor de la escena es TRANSPARENTE: leer su backgroundColor
          // devuelve rgba(0,0,0,0) y el contraste sale contra negro (11,11:1
          // donde lo real era 8,05). Se sube hasta el primer ancestro opaco.
          const opaco = e => { let n=e; while(n && n!==document.documentElement){
            const bg=getComputedStyle(n).backgroundColor;
            if (bg && !/, *0\\)$/.test(bg) && bg!=='transparent') return bg;
            n=n.parentElement; } return '#fff'; };
          const cab = document.querySelector('.cae-cred-cab');
          const cru = document.querySelector('.cae-cred-cruce');
          const res = {sale: 0, peor: 99, cual: ''};
          for (const b of document.querySelectorAll('.cae-cred-pieza')) {
            b.dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
            const rc = cru.getBoundingClientRect(), rb = cab.getBoundingClientRect();
            res.sale = Math.max(res.sale, Math.round(rc.bottom - rb.bottom));
            const li = cru.querySelector('li');
            if (li && li.getClientRects().length) {
              const r = rat(getComputedStyle(li).color, opaco(li));
              if (r < res.peor) { res.peor = r; res.cual = b.dataset.pieza; }
            }
          }
          return res;
        }"""
    )
    check(peor["sale"] <= 0, f"el cruce no se sale de la cabecera ({peor['sale']} px)")
    check(
        peor["peor"] >= 4.5,
        f"el cruce se lee en las 23 (peor {peor['peor']:.2f}:1 en «{peor['cual']}»)",
    )
```

- [ ] **Paso 2: correrlo y verlo dar rojo**

Esperado: `FAIL el cruce se lee en las 23` — la Task 3 no puso estilo al cruce y hereda el color
del contenedor, o `FAIL el cruce no se sale de la cabecera (15 px)` si lo pusiste en pila.

- [ ] **Paso 3: el CSS del cruce y del territorio**

```css
/* HILERA, no pila. Medido: con tres obras (TypeScript: EchoPlan, TesisFar,
   HyprFinance) la pila de <li> medía 111 px dentro de una cabecera de 96 y se
   salía 15. En hilera con punto medio caben en uno: 51 px, 400 de ancho en un
   hueco de 420. Los tres títulos siguen escritos, ninguno se resume. */
:root[data-theme="caelestia"] .cae-cred-cruce {
  text-align: right;
  max-width: 420px;
}

/* Tracking corto: a .2em «APARECE EN» se leía como diez letras sueltas. Sigue
   en versalitas porque es un epígrafe, no una palabra que se lea. */
:root[data-theme="caelestia"] .cae-cred-cruce > span {
  display: block;
  font-family: "Martian Mono", ui-monospace, monospace;
  font-size: 9.5px;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--cae-on-surface-variant);
  margin-bottom: 9px;
}

:root[data-theme="caelestia"] .cae-cred-cruce-lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: baseline;
  gap: 0 2px;
}

:root[data-theme="caelestia"] .cae-cred-cruce-lista li {
  font-family: "Fraunces", Georgia, serif;
  font-style: italic;
  font-variation-settings: "opsz" 48, "wght" 500, "SOFT" 0, "WONK" 1;
  font-size: 26px;
  line-height: 1.16;
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .cae-cred-cruce-lista li + li::before {
  content: "\00B7";
  padding: 0 7px 0 5px;
  color: var(--cae-on-surface-variant);
  font-style: normal;
}

/* «Sin obra publicada» NO se apaga con tinta: en `--cae-outline` daba 1,80:1 de
   noche y 2,34:1 a las 09:00, y son 7 de las 23 piezas (el 30 %). El estado lo
   dice la PALABRA. Apagar la tinta para decir «esto pesa menos» es la misma
   opacidad recalibrada que ya fallo en B1. */
:root[data-theme="caelestia"] .cae-cred-cruce-lista li.is-vacia {
  font-size: 21px;
  color: var(--cae-on-surface-variant);
}

:root[data-theme="caelestia"] .cae-cred-nombre {
  font-family: "Fraunces", Georgia, serif;
  font-variation-settings: var(--cae-display-axes-cartel);
  font-size: 32px;
  line-height: 1;
  margin: 0 0 4px;
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .cae-cred-detalle {
  margin: 0;
  font-family: "Fraunces", Georgia, serif;
  font-style: italic;
  font-variation-settings: "opsz" 24, "wght" 400, "SOFT" 0, "WONK" 1;
  font-size: 17px;
  color: var(--cae-on-surface-variant);
}

/* Especificidad `.cae-cred-cab .cae-cred-terr` (0,2,0) y no `.cae-cred-terr`
   (0,1,0): `.cae-cred-cab p` le ganaba y el territorio se pintaba en Fraunces
   itálica pese a pedir la monoespaciada, obedeciendo solo el tracking. Y no
   basta con repetir la familia: hay que apagar tambien `font-style` y los ejes
   heredados. Sin versalitas ni tracking largo — a 10 px separaba las letras. */
:root[data-theme="caelestia"] .cae-cred-cab .cae-cred-terr {
  font-family: "Martian Mono", ui-monospace, monospace;
  font-size: 10px;
  letter-spacing: 0.01em;
  font-style: normal;
  font-variation-settings: normal;
  color: var(--cae-on-surface-variant);
  margin: 7px 0 0;
}
```

- [ ] **Paso 4: comprobar el estilo COMPUTADO del territorio, no la captura**

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded', timeout=45000)
    pg.wait_for_timeout(6000)
    pg.eval_on_selector_all('.cae-ws', 'bs=>{const b=bs.find(x=>/Cr..?ditos/.test(x.textContent)); if(b) b.click();}')
    pg.wait_for_timeout(2500)
    print(pg.eval_on_selector('.cae-cred-terr', 'e=>{const c=getComputedStyle(e); return {fam:c.fontFamily, style:c.fontStyle, ls:c.letterSpacing, tt:c.textTransform};}'))
    b.close()
"
```

Esperado: `Martian Mono` primero, `fontStyle: normal`, `textTransform: none`. Si sale `Fraunces` o
`italic`, la especificidad sigue perdiendo.

- [ ] **Paso 5: build, medir en verde y commit**

```bash
npm run build && npm run lint
kill <pid>; npx vite preview --port 4173 & sleep 3
python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173
git add src/themes/themes.css scripts/measure-caelestia-creditos.py
git commit -m "fix(creditos): el cruce en hilera y el estado vacio legible — los dos defectos de M4"
```

---

## Task 5: Rozar elige, y el teclado llega a lo mismo

**Files:**
- Modify: `src/components/caelestiaCreditosBandeja.ts`
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-caelestia-creditos.py`

**Interfaces:**
- Consume: `pintarFicha(p: Pieza)` de la Task 3.

- [ ] **Paso 1: el gate 7**

```python
def gate_seleccion(pagina) -> None:
    """Rozar ELIGE, sin pulsar, y el teclado llega a lo mismo que el raton.

    Se comprueba con `hover()` real de Playwright, NO con un MouseEvent
    sintetico: un evento fabricado no dispara `:hover`, asi que un gate escrito
    asi da verde con el hover roto. Ya paso en B2."""
    print("[7] rozar elige, y el foco hace lo mismo")
    antes = pagina.eval_on_selector(".cae-cred-nombre", "e=>e.textContent")
    pagina.hover('.cae-cred-pieza[data-pieza="Git"]')
    pagina.wait_for_timeout(700)
    tras_rozar = pagina.eval_on_selector(".cae-cred-nombre", "e=>e.textContent")
    check(tras_rozar == "Git" and antes != tras_rozar, f"rozar releva la ficha ({tras_rozar})")

    marcadas = pagina.eval_on_selector_all(
        '.cae-cred-pieza[aria-pressed="true"]', "es=>es.map(e=>e.dataset.pieza)"
    )
    check(marcadas == ["Git"], f"solo la elegida lleva aria-pressed ({marcadas})")

    pagina.eval_on_selector('.cae-cred-pieza[data-pieza="Python"]', "e=>e.focus()")
    pagina.wait_for_timeout(700)
    tras_foco = pagina.eval_on_selector(".cae-cred-nombre", "e=>e.textContent")
    check(tras_foco == "Python", f"el foco releva la ficha ({tras_foco})")
```

- [ ] **Paso 2: correrlo y verlo dar rojo**

Esperado: `FAIL rozar releva la ficha (React)` — la ficha sigue en la primera pieza.

- [ ] **Paso 3: cablear la selección**

En `mountCaelestiaCreditosBandeja`, después de `pintarFicha(piezas[0])`:

```ts
  const botones = Array.from(
    escena.querySelectorAll<HTMLButtonElement>(".cae-cred-pieza"),
  );
  const grid = escena.querySelector<HTMLElement>(".cae-cred-grid");
  let elegida = piezas[0].name;

  function elegir(nombre: string): void {
    if (elegida === nombre) return;
    const p = piezas.find((x) => x.name === nombre);
    if (!p) return;
    elegida = nombre;
    pintarFicha(p);
    for (const b of botones) {
      b.setAttribute("aria-pressed", String(b.dataset.pieza === nombre));
    }
    if (reduce) return;
    // La cabecera se releva con barridos de clip-path: nada se desvanece, todo
    // se recorta. Es la ley de seccion heredada del cartel.
    gsap.fromTo(
      [nombre, detalle, territorio, cruceLista],
      { clipPath: "inset(0px 100% 0px 0px)" },
      {
        clipPath: "inset(0px 0% 0px 0px)",
        duration: 0.22,
        stagger: 0.03,
        ease: "power2.out",
      },
    );
    gsap.fromTo(
      marca,
      { clipPath: "circle(0% at 50% 50%)" },
      { clipPath: figuraDe(p.slug), duration: 0.26, ease: "power2.out" },
    );
  }

  // Rozar elige: no hace falta pulsar. Clic y foco hacen lo mismo, para que el
  // teclado llegue adonde llega el raton.
  const escuchas: Array<() => void> = [];
  for (const b of botones) {
    const nombre = b.dataset.pieza ?? "";
    const entrar = (): void => {
      grid?.classList.add("is-tocando");
      elegir(nombre);
    };
    const salir = (): void => grid?.classList.remove("is-tocando");
    b.addEventListener("mouseenter", entrar);
    b.addEventListener("focus", entrar);
    b.addEventListener("click", entrar);
    b.addEventListener("blur", salir);
    escuchas.push(() => {
      b.removeEventListener("mouseenter", entrar);
      b.removeEventListener("focus", entrar);
      b.removeEventListener("click", entrar);
      b.removeEventListener("blur", salir);
    });
  }
```

Y en `destroy()`, antes de `wrap.remove()`:

```ts
      for (const off of escuchas) off();
```

- [ ] **Paso 4: el CSS del estado elegido**

```css
:root[data-theme="caelestia"] .cae-cred-pieza[aria-pressed="true"] .cae-cred-fig {
  clip-path: var(--fig-suave);
  background: var(--cae-primary);
  transform: scale(1.07);
}

:root[data-theme="caelestia"] .cae-cred-fig {
  transition:
    clip-path 0.22s ease,
    transform 0.22s ease,
    background 0.22s ease;
}

/* Las demas bajan su TINTA, nunca su fondo: `--cae-surface-container` es
   exactamente `--cae-elev-1`, el fondo de la ventana, asi que apagar el relleno
   borra las figuras en vez de atenuarlas. */
:root[data-theme="caelestia"] .cae-cred-grid.is-tocando
  .cae-cred-pieza:not([aria-pressed="true"]) figcaption {
  color: var(--cae-on-surface-variant);
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] .cae-cred-fig {
    transition: none;
  }
}
```

- [ ] **Paso 5: build, medir en verde y commit**

```bash
npm run build && npm run lint
kill <pid>; npx vite preview --port 4173 & sleep 3
python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173
git add src/components/caelestiaCreditosBandeja.ts src/themes/themes.css scripts/measure-caelestia-creditos.py
git commit -m "feat(creditos): rozar elige la pieza, y el foco llega a lo mismo"
```

---

## Task 6: La entrada — «la instalación»

**Files:**
- Modify: `src/components/caelestiaCreditosBandeja.ts`
- Modify: `src/themes/themes.css`
- Modify: `scripts/measure-caelestia-creditos.py`

- [ ] **Paso 1: el gate 8**

```python
def gate_entrada(pagina, base: str) -> None:
    """La entrada existe, y `prefers-reduced-motion` la salta ENTERA — al estado
    aterrizado, no a un fotograma intermedio.

    Se mide el estado aterrizado, no un fotograma de la entrada: agrupar por
    posicion mientras GSAP tiene desplazamientos por elemento da lineas fantasma
    de un solo nombre. Con `reduced_motion='reduce'` la animacion se salta y los
    numeros son los del layout."""
    print("[8] la entrada, y el movimiento reducido la salta")
    contexto = pagina.context.browser.new_context(
        viewport={"width": 1440, "height": 900}, reduced_motion="reduce"
    )
    p2 = contexto.new_page()
    abre(p2, base)
    m = p2.evaluate(
        """() => {
             const f = [...document.querySelectorAll('.cae-cred-fig')];
             return {opacos: f.filter(e => +getComputedStyle(e).opacity === 1).length,
                     total: f.length,
                     sinEscala: f.filter(e => {
                       const t = getComputedStyle(e).transform;
                       return t === 'none' || t === 'matrix(1, 0, 0, 1, 0, 0)';
                     }).length};
           }"""
    )
    check(m["opacos"] == m["total"], f"con mov. reducido las 23 estan opacas ({m['opacos']}/{m['total']})")
    check(m["sinEscala"] >= m["total"] - 1, f"y sin escala de entrada ({m['sinEscala']}/{m['total']})")
    contexto.close()
```

- [ ] **Paso 2: correrlo y verlo dar rojo**

Antes de implementar nada, sabotea: añade a mano `opacity: 0` a `.cae-cred-fig` en `themes.css`,
recompila y corre. Esperado: `FAIL con mov. reducido las 23 estan opacas (0/23)`. Deshaz.

- [ ] **Paso 3: la entrada, en CSS con GSAP decidiendo sólo el cuándo**

```css
/* «La instalacion»: las 23 llegan como CIRCULOS IDENTICOS —paquetes sin
   abrir— y cada una morfa a su figura mientras crece desde 0,66 y se endereza
   6 grados. El mecanismo es la identidad declarada del tema, no un
   desplazamiento prestado de otra escena. Sin terminal tecleada: seria la
   tercera despues de B1 y B2, y esta vetada. */
@keyframes caeCredInstala {
  from {
    clip-path: circle(50% at 50% 50%);
    transform: scale(0.66) rotate(-6deg);
    opacity: 0;
  }
  60% {
    opacity: 1;
  }
  to {
    clip-path: var(--fig);
    transform: scale(1) rotate(0deg);
    opacity: 1;
  }
}

:root[data-theme="caelestia"] [data-cred-entrando] .cae-cred-fig {
  animation: caeCredInstala 0.52s cubic-bezier(0.22, 1, 0.36, 1) both;
  animation-delay: var(--retardo, 0ms);
}

/* La guardia con `*` NO alcanza a los pseudo-elementos ni a las animaciones ya
   declaradas por nombre: hace falta esta regla explicita. */
@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] [data-cred-entrando] .cae-cred-fig {
    animation: none;
  }
}
```

- [ ] **Paso 4: dispararla, y soltar la animación al acabar**

En el componente, antes del `return`:

```ts
  // La onda va POR TERRITORIOS: cada familia arranca 190 ms detras de la
  // anterior, y dentro de cada una las piezas se escalonan 34 ms.
  if (!reduce) {
    escena.setAttribute("data-cred-entrando", "");
    let indice = 0;
    skillGroups.forEach((g, gi) => {
      g.items.forEach((_, i) => {
        const fig = botones[indice]?.querySelector<HTMLElement>(".cae-cred-fig");
        fig?.style.setProperty("--retardo", `${260 + gi * 190 + i * 34}ms`);
        indice += 1;
      });
    });
    // Cada nodo SUELTA su animacion al acabar. Con `both`, `transform` y
    // `clip-path` se quedan congelados en el ultimo fotograma y le ganan al
    // `:hover` y al estado elegido: el morfado al rozar no ocurria, sin error
    // ninguno.
    for (const b of botones) {
      const fig = b.querySelector<HTMLElement>(".cae-cred-fig");
      fig?.addEventListener(
        "animationend",
        () => {
          fig.style.animation = "none";
        },
        { once: true },
      );
    }
  }
```

- [ ] **Paso 5: comprobar a mano que el roce sigue funcionando DESPUÉS de la entrada**

Es el fallo exacto que provoca `fill: both`, y ningún gate de layout lo ve:

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:4173/?theme=caelestia', wait_until='domcontentloaded', timeout=45000)
    pg.wait_for_timeout(6000)
    pg.eval_on_selector_all('.cae-ws', 'bs=>{const b=bs.find(x=>/Cr..?ditos/.test(x.textContent)); if(b) b.click();}')
    pg.wait_for_timeout(4000)   # la entrada cierra en ~1,6 s: se espera de sobra
    pg.hover('.cae-cred-pieza[data-pieza=\"Git\"]')
    pg.wait_for_timeout(800)
    print(pg.eval_on_selector('.cae-cred-pieza[data-pieza=\"Git\"] .cae-cred-fig',
        'e=>({t:getComputedStyle(e).transform, anim:getComputedStyle(e).animationName})'))
    b.close()
"
```

Esperado: `animationName: none` y un `transform` con escala 1.07 (`matrix(1.07, 0, 0, 1.07, 0, 0)`).
Si sale `matrix(1, 0, 0, 1, 0, 0)`, la animación sigue congelando el nodo.

- [ ] **Paso 6: build, medir en verde y commit**

```bash
npm run build && npm run lint
kill <pid>; npx vite preview --port 4173 & sleep 3
python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173
git add src/components/caelestiaCreditosBandeja.ts src/themes/themes.css scripts/measure-caelestia-creditos.py
git commit -m "feat(creditos): la entrada de escena, la instalacion de paquetes"
```

---

## Task 7: El barrido de las 24 horas

**Files:**
- Modify: `scripts/measure-caelestia-creditos.py`

- [ ] **Paso 1: el gate 5**

```python
def gate_horas(pagina) -> None:
    """Contraste de TODO lo que lleva tinta, en las 24 posiciones del reloj y en
    los DOS estados de la ficha (con obra y sin ella).

    Los dos estados no son un extra: con solo uno, «Sin obra publicada» —7 de
    las 23 piezas— no se mide nunca. El sabotaje lo demostro: la sonda daba
    verde con ese par a 1,80:1, porque el nodo no existia mientras medía.

    Visto rojo con: el territorio en `--cae-outline` — rojo en las 24 horas.

    El reloj se mueve con la sonda que expone `caelestia.color`; el fondo se
    resuelve subiendo al primer ancestro OPACO, no leyendo el de la escena, que
    es transparente y daria el ratio contra negro."""
    print("[5] contraste en las 24 horas, en los dos estados de la ficha")
    peor = (99.0, "", -1)
    for hora in range(24):
        pagina.evaluate("(m)=>window.__CAE_SET_MINUTOS__ && window.__CAE_SET_MINUTOS__(m)", hora * 60)
        pagina.wait_for_timeout(220)
        for pieza in ("Git", "Tailwind CSS"):
            pagina.hover(f'.cae-cred-pieza[data-pieza="{pieza}"]')
            pagina.wait_for_timeout(260)
            m = pagina.evaluate(_JS_CONTRASTE)
            if m["peor"] < peor[0]:
                peor = (m["peor"], m["cual"], hora)
    check(peor[0] >= 4.5, f"ningun par baja de AA (peor {peor[0]:.2f}:1 en «{peor[1]}» a las {peor[2]:02d}:00)")
```

Y `_JS_CONTRASTE` a nivel de módulo, con los 55 pares — nombre, detalle, territorio, epígrafe,
cruce, los cuatro rótulos de banda, los 23 iconos **contra su propia figura** y los 23 nombres:

```python
_JS_CONTRASTE = r"""() => {
  const px = c => { const k=document.createElement('canvas'); k.width=k.height=1;
    const x=k.getContext('2d'); x.fillStyle='#000'; x.fillRect(0,0,1,1);
    x.fillStyle=c; x.fillRect(0,0,1,1);
    const d=x.getImageData(0,0,1,1).data; return [d[0],d[1],d[2]]; };
  const lum = r => { const f=r.map(v=>{v/=255;
    return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4);});
    return 0.2126*f[0]+0.7152*f[1]+0.0722*f[2]; };
  const rat = (a,b) => { const la=lum(px(a)), lb=lum(px(b));
    const h=Math.max(la,lb), l=Math.min(la,lb); return (h+0.05)/(l+0.05); };
  const opaco = e => { let n=e; while(n && n!==document.documentElement){
    const bg=getComputedStyle(n).backgroundColor;
    if (bg && !/, *0\)$/.test(bg) && bg!=='transparent') return bg;
    n=n.parentElement; } return '#fff'; };

  let peor = 99, cual = '';
  const mide = (nom, el, color) => {
    if (!el || el.getClientRects().length === 0) return;
    const r = rat(color || getComputedStyle(el).color, opaco(el));
    if (r < peor) { peor = r; cual = nom; }
  };

  mide('nombre', document.querySelector('.cae-cred-nombre'));
  mide('detalle', document.querySelector('.cae-cred-detalle'));
  mide('territorio', document.querySelector('.cae-cred-terr'));
  mide('epigrafe', document.querySelector('.cae-cred-cruce > span'));
  mide('cruce', document.querySelector('.cae-cred-cruce-lista li'));
  document.querySelectorAll('.cae-cred-rot h4')
    .forEach((h, i) => mide('rotulo ' + (i + 1), h));
  // El icono se pinta con `fill`, no con `color`, y su fondo es LA FIGURA, no
  // la escena: leer el fondo de la escena daria un numero que nadie ve.
  document.querySelectorAll('.cae-cred-pieza').forEach(t => {
    const sv = t.querySelector('svg'), fg = t.querySelector('.cae-cred-fig');
    if (!sv || !fg || sv.getClientRects().length === 0) return;
    const r = rat(getComputedStyle(sv).fill, getComputedStyle(fg).backgroundColor);
    if (r < peor) { peor = r; cual = 'icono ' + t.dataset.pieza; }
  });
  document.querySelectorAll('.cae-cred-pieza figcaption')
    .forEach(f => mide('nombre ' + f.parentElement.dataset.pieza, f));

  return { peor, cual };
}"""
```

- [ ] **Paso 2: exponer el reloj para poder barrerlo**

`src/themes/caelestia.color.ts` gobierna el color por la hora. Si no expone ya una vía para fijar
los minutos, añádele una **sonda de verificación** con el mismo patrón que `__CONTENT_SHAPE__` en
`src/main.ts:296`: una propiedad en `window` que no afecta al render. Sin eso, el barrido de 24 h
no es alcanzable y el gate sería tautológico — que es exactamente el fallo del reloj congelado de
la fase A.

- [ ] **Paso 3: verlo dar rojo**

```bash
# Sabotaje: devuelve el territorio a --cae-outline
sed -i 's|\(\.cae-cred-terr {[^}]*\)var(--cae-on-surface-variant)|\1var(--cae-outline)|' src/themes/themes.css
grep -c "cae-cred-terr" src/themes/themes.css     # asegurate de que el sed toco algo
npm run build && kill <pid> && npx vite preview --port 4173 & sleep 3
python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173
git checkout src/themes/themes.css
```

Esperado: `FAIL ningun par baja de AA (peor 1.80:1 en «territorio» a las 03:00)`.

**Un `sed` que no casa no da error: deja el fichero igual y el sabotaje no ocurre.** El `grep -c`
está para eso.

- [ ] **Paso 4: correr en verde y commit**

Esperado: `OK ningun par baja de AA (peor 5.73:1 en «nombre Git» a las 08:00)`.

```bash
git add scripts/measure-caelestia-creditos.py src/themes/caelestia.color.ts
git commit -m "test(creditos): barrido de las 24 horas sobre los dos estados de la ficha"
```

---

## Task 8: Cerrar — documentación y estado

**Files:**
- Modify: `.claude/rules/verification.md`
- Modify: `CLAUDE.md`, `.claude/CLAUDE.md`
- Modify: `docs/superpowers/specs/2026-09-03-caelestia-creditos-design.md`

- [ ] **Paso 1: la fila del arnés**

Añade a la tabla de arneses de `.claude/rules/verification.md`, después de la de
`measure-caelestia-obra.py`:

```markdown
| `measure-caelestia-creditos.py` | La escena «Créditos» de Caelestia (fase B4, la bandeja de paquetes): 7 familias de aserciones — la octava, la de las 23 figuras, no necesita navegador y vive en `docs/superpowers/specs/2026-09-03-caelestia-creditos-figuras.py`, que compara la salida de `src/utils/figurasM3.ts` contra el generador punto a punto. Que la escena **no tiene scroll interno** (era 758/748); que los **cuatro rótulos de territorio se pintan** (existían los cuatro en el DOM y no se pintaba ninguno — contar nodos no es contar lo que se ve); que las 23 piezas están dentro de la caja y **todas al mismo lado** (el tamaño no codifica: las dos varas posibles mienten); que el cruce «Aparece en» cabe en los 96 px de cabecera en las 23 (con tres obras la pila medía 111 y se salía 15); que **«Sin obra publicada» se lee** (iba en `--cae-outline`: 1,80:1 de noche, en 7 de las 23 piezas); que rozar elige sin pulsar y el foco llega a lo mismo (con `hover()` real, **no** un `MouseEvent` sintético, que no dispara `:hover`); la entrada y su salto con movimiento reducido; y el contraste de los 55 pares en las **24 horas y en los dos estados de la ficha** — con un solo estado, el vacío no se mide nunca. | `npm run build && npx vite preview --port 4173 &`<br>`python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173` |
```

- [ ] **Paso 2: el estado de la fase en los dos CLAUDE.md**

**Regla dura: no edites `CLAUDE.md` a mitad de sesión** — invalida el prompt cache. Haz este paso
**al principio de una sesión**, o anótalo en `.ai/memory.md` y déjalo para la siguiente.

Añade el bloque de B4 después del de B3 en los dos ficheros (inglés en `CLAUDE.md`, español en
`.claude/CLAUDE.md`), siguiendo la forma de los anteriores: qué es la escena ahora, qué fichero es
nuevo, qué NO se tocó (`credits.ts`, que comparten los tres temas), el arnés que la vigila, y que
**móvil queda fuera de alcance a propósito**, igual que en B1 y B2.

- [ ] **Paso 3: cerrar el estado del spec**

```bash
sed -i 's/^Estado: pendiente de plan$/Estado: implementado/' docs/superpowers/specs/2026-09-03-caelestia-creditos-design.md
grep -n "^Estado:" docs/superpowers/specs/2026-09-03-caelestia-creditos-design.md
```

Y añade en el spec la sección `Plan:` apuntando a este fichero.

`scripts/verify.py::check_spec_plan_consistency` **falla** si el spec dice `implementado` y este
plan tiene pasos sin marcar. Así que este paso va el último, con todas las casillas ya en `[x]`.

- [ ] **Paso 4: la verificación completa**

```bash
npm run build && npm run lint
python3 scripts/verify.py --url http://localhost:4173      # tiene que salir con codigo 0
python3 scripts/measure-caelestia-creditos.py --base http://localhost:4173
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173      # la fase A sigue intacta
python3 scripts/measure-caelestia-titulo.py --base http://localhost:4173    # B1 sigue intacta
python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4173 # B2 sigue intacta
python3 scripts/measure-caelestia-obra.py --base http://localhost:4173      # B3 sigue intacta
```

Los cuatro arneses de las fases anteriores tienen que seguir verdes: el CSS de B4 vive en el mismo
bloque `:root[data-theme="caelestia"]` y una regla demasiado genérica se filtra. Fue lo que pasó en
B1, donde la regla de panel de la fase A tapó el 78 % del fondo generativo del Título.

Comprueba también que **Vice y Hyprland siguen intactos**: `credits.ts` es suyo también.

```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=['--no-sandbox','--use-gl=swiftshader'])
    for tema in ('vice','hyprland'):
        pg = b.new_page(viewport={'width':1440,'height':900})
        pg.goto(f'http://localhost:4173/?theme={tema}', wait_until='domcontentloaded', timeout=45000)
        pg.wait_for_timeout(7000)
        n = pg.eval_on_selector_all('[data-credit]', 'es=>es.filter(e=>e.getClientRects().length>0).length')
        print(tema, 'filas de credito pintadas:', n)
        assert n > 0, f'{tema}: la bandeja de Caelestia se ha filtrado y ha borrado sus creditos'
        pg.close()
    b.close()
"
```

- [ ] **Paso 5: los gates de crítica**

Lanza `lidia-naive-tester` y `vera-art-director` sobre la escena, como en B1, B2 y B3.
**Prohíbeles explícitamente editar nada de `src/`** en el brief: ya han ensuciado `main` una vez.

- [ ] **Paso 6: commit final**

```bash
git add .claude/rules/verification.md CLAUDE.md .claude/CLAUDE.md docs/superpowers/
git commit -m "docs(creditos): cierra la fase B4 — arnes en la tabla, estado y registro de implementacion"
```

---

## Preguntas que este plan NO decide

1. **El hueco al pie derecho, 28,1 %.** Las tres bandas de cinco dejan tres módulos libres cada una.
   El spec recomienda **aceptarlo** como el canto irregular de un 8/5/5/5 y dejarlo escrito como
   decisión. No lo rellenes por tu cuenta: repartir las bandas de otra forma cuesta la alineación
   de columnas, que es un requisito explícito.
2. **Móvil.** Fuera de alcance, con la deuda cuantificada en el spec (154 px de scroll interno hoy
   a 390, y tres filas fuera de la ventana). La recomendación es una fase transversal después de
   B5, no un arreglo aquí.
