# Escala tipográfica de Caelestia — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que ninguna talla tipográfica de Caelestia se elija a ojo: las 56 declaraciones con
literal pasan a los doce escalones de la escala, y un gate impide que vuelva a colarse una.

**Architecture:** Tres movimientos sobre `src/themes/themes.css` y `src/style.css`: dos escalones
nuevos por abajo (`--t-00` 9,5px y `--t-0` 10,67px, razón 1,125), la escala declarada una sola vez
en `:root` en lugar de tres veces —una por tema—, y los nueve respaldos de `style.css` fuera. Luego
la migración escena por escena, cada una firmada por el arnés que ya la vigila. El gate nuevo tiene
dos familias: una estática sobre el fuente y una viva sobre el build servido que lee el `font-size`
computado de todo lo que pinta texto.

**Tech Stack:** Vite 8, TypeScript estricto, Tailwind 4, CSS puro en `src/themes/themes.css`,
Playwright (Python) para los arneses.

**Spec:** `docs/superpowers/specs/2026-09-07-escala-tipografica-design.md`

## Global Constraints

- **Rama:** `design/escala-tipografica`, ya creada desde `main` (`a73fa11`). Sin push.
- **Node 22:** `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"` antes de cualquier `npm`.
- **Los arneses se lanzan contra el build de producción servido**, nunca contra `npm run dev`.
  Levantar una vez: `npm run build && npx vite preview --port 4173 &`. Tras CADA cambio de CSS hay
  que volver a `npm run build`: `vite preview` sirve `dist/`, no el fuente.
- **Un arnés a la vez.** Dos en paralelo producen rojos falsos y ya han matado la máquina por OOM.
  Lanzar con `nohup`, esperar POR PID dentro del MISMO comando de Bash, nunca terminar el turno
  esperando. **Jamás `pkill -f`**: el patrón casa con la línea de comando del propio bucle que
  espera, y ya mató el arnés de otra sesión.
- **Ningún gate se acepta sin haberlo visto dar ROJO** contra el fallo exacto que dice cazar.
- **Verificar el CSS construido, no el fuente**, cuando se dude de si una regla se aplicó:
  `grep -o '<regla>' dist/assets/*.css`. El mismo texto de regla existe en varias bandas de
  `@media` y un reemplazo puede aterrizar en la equivocada.
- **Vice no se toca** más allá de quitarle la declaración duplicada de la escala, que son los mismos
  números. Hyprland queda fuera de alcance.
- **Si una talla nueva rompe su caja, se arregla la CAJA, no se devuelve el número.**
- Cero emojis en código, commits y documentación.

---

## Estructura de ficheros

| Fichero | Responsabilidad | Acción |
|---|---|---|
| `src/themes/themes.css` | Tokens y las 56 declaraciones a migrar | Modificar |
| `src/style.css` | Consumo de tokens con respaldo (9 sitios) | Modificar |
| `scripts/measure-escala-tipografica.py` | El gate, dos familias | Crear |
| `.claude/rules/verification.md` | Fila del arnés nuevo | Modificar (al cerrar) |
| `docs/superpowers/specs/2026-09-07-escala-tipografica-design.md` | Estado y registro | Modificar (al cerrar) |
| `CLAUDE.md` y `.claude/CLAUDE.md` | Bloque de estado | Modificar (al cerrar) |

---

## Task 0: El gate, visto en rojo contra el estado actual

**Files:**
- Create: `scripts/measure-escala-tipografica.py`

**Interfaces:**
- Produces: `familia_estatica(raiz: Path) -> list[str]` y
  `familia_viva(navegador, base: str) -> list[str]`, las dos devolviendo la lista de fallos;
  `comprobar(condicion: bool, etiqueta: str) -> None`, que imprime `OK`/`FALLO` y acumula en la
  global `FALLOS`. Es el mismo contrato que `scripts/measure-caelestia-movil.py`, para que quien
  lea uno lea el otro.
- Consumes: nada de tareas anteriores.

- [ ] **Step 1: Escribir el arnés entero**

Crear `scripts/measure-escala-tipografica.py` con este contenido:

```python
#!/usr/bin/env python3
"""La escala tipografica de Caelestia (spec 2026-09-07-escala-tipografica).

Dos familias que se vigilan entre si:
  1. ESTATICA, sobre el fuente. Cero `font-size` con literal bajo
     `[data-theme="caelestia"]`, cero `var(--t-N, respaldo)` en todo `src/`,
     y la escala declarada EXACTAMENTE UNA VEZ y en `:root` a secas.
  2. VIVA, sobre el build de produccion servido. El `font-size` COMPUTADO de
     cada nodo que pinta texto propio cae en la escala.

La viva existe porque la estatica se burla sin querer: Tailwind, estilos en
linea desde TS, `style.css` y cualquier regla futura quedan fuera de una
regex sobre `themes.css`. Lo que vale es lo que se pinta.

  npm run build && npx vite preview --port 4173 &
  python3 scripts/measure-escala-tipografica.py --base http://127.0.0.1:4173
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

FALLOS: list[str] = []

# La escala, en px. Es la tabla del spec y la fuente de verdad del arnes.
ESCALA = {
    "--t-00": 9.5,
    "--t-0": 10.67,
    "--t-1": 12.0,
    "--t-2": 16.0,
    "--t-3": 21.33,
    "--t-4": 28.43,
    "--t-5": 37.9,
    "--t-6": 50.52,
    "--t-7": 67.4,
    "--t-8": 89.85,
    "--t-9": 119.77,
    "--t-10": 159.66,
}
VALORES = sorted(ESCALA.values())

# La UNICA excepcion, y es por selector concreto, nunca por categoria: el
# titular de B1 se justifica midiendo el texto y estirandolo hasta la medida
# (`caelestia.titulo.ts:48-52`), asi que su tamano lo decide el ancho de la
# caja y no puede estar en la escala por construccion. Si aparece un segundo
# elemento con tamano en linea, este gate se pone rojo, que es el objetivo.
EXCEPCIONES = ["#hero .cae-ln"]

ESCENAS = ["hero", "quien-es", "obra", "creditos", "contacto"]


def comprobar(condicion: bool, etiqueta: str) -> None:
    print(("  OK   " if condicion else "  FALLO") + f"  {etiqueta}")
    if not condicion:
        FALLOS.append(etiqueta)


def _sin_comentarios(css: str) -> str:
    """Quita los comentarios /* */ antes de buscar reglas: `themes.css` cita
    valores de `font-size` dentro de sus propios comentarios, y contarlos daba
    tres literales fantasma en Vice."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def familia_estatica(raiz: pathlib.Path) -> list[str]:
    print("\n[1] Estatica: el fuente no elige tallas a ojo")
    themes = _sin_comentarios((raiz / "src/themes/themes.css").read_text(encoding="utf-8"))

    # 1a. Ni un `font-size` con literal bajo [data-theme="caelestia"].
    sel = ""
    literales: list[str] = []
    for n, linea in enumerate(themes.split("\n"), 1):
        st = linea.strip()
        if st.endswith("{"):
            sel = st[:-1].strip()
        m = re.search(r"font-size:\s*([0-9.]+)(px|rem)\s*;", linea)
        if m and "caelestia" in sel:
            literales.append(f"L{n} {sel.split('] ')[-1][:40]} = {m.group(0).strip()}")
    comprobar(not literales, f"cero font-size literal en Caelestia ({len(literales)}: {literales[:3]})")

    # 1b. Ni un token con respaldo, en todo src/. Un token que necesita
    # respaldo no esta garantizado: son una segunda escala escondida.
    con_respaldo: list[str] = []
    for f in sorted(raiz.glob("src/**/*.css")) + sorted(raiz.glob("src/**/*.ts")):
        for n, linea in enumerate(_sin_comentarios(f.read_text(encoding="utf-8")).split("\n"), 1):
            if re.search(r"var\(--t-\d+\s*,", linea):
                con_respaldo.append(f"{f.relative_to(raiz)}:{n}")
    comprobar(not con_respaldo, f"cero var(--t-N, respaldo) en src/ ({len(con_respaldo)}: {con_respaldo[:3]})")

    # 1c. La escala se declara UNA vez, y en `:root` a secas.
    decls = [n for n, linea in enumerate(themes.split("\n"), 1) if re.match(r"\s*--t-1:\s", linea)]
    comprobar(len(decls) == 1, f"la escala se declara una sola vez (lineas {decls})")
    if decls:
        prof, dueno = 0, "?"
        lineas = themes.split("\n")
        for i in range(decls[0] - 2, -1, -1):
            prof += lineas[i].count("}") - lineas[i].count("{")
            if prof < 0:
                dueno = lineas[i].strip()
                break
        comprobar(dueno.startswith(":root {"), f"la escala cuelga de :root a secas (cuelga de «{dueno[:40]}»)")

    # 1d. Los doce tokens existen con el valor de la tabla.
    for token, px in ESCALA.items():
        m = re.search(rf"{re.escape(token)}:\s*([0-9.]+)px", themes)
        comprobar(m is not None and abs(float(m.group(1)) - px) < 0.005,
                  f"{token} vale {px}px (declarado: {m.group(1) + 'px' if m else 'no existe'})")
    return []


def familia_viva(navegador, base: str) -> list[str]:
    print("\n[2] Viva: lo que se PINTA cae en la escala")
    errores: list[str] = []
    for ancho, alto, movil in ((1440, 900, False), (390, 844, True)):
        for hora, etiqueta in ((13 * 60, "13:00"), (23 * 60, "23:00")):
            kwargs = {"viewport": {"width": ancho, "height": alto}}
            if movil:
                kwargs |= {"device_scale_factor": 2, "is_mobile": True, "has_touch": True}
            ctx = navegador.new_context(**kwargs)
            pg = ctx.new_page()
            pg.on("pageerror", lambda e: errores.append(str(e)))
            pg.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            try:
                pg.wait_for_function(
                    "document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000
                )
            except Exception:
                pg.wait_for_timeout(3000)
            pg.evaluate("(m) => window.__CAE_SET_MINUTOS__(m)", hora)
            pg.wait_for_timeout(600)
            for escena in ESCENAS:
                pg.click(f'[data-cae-ws="{escena}"]')
                pg.wait_for_timeout(1600)
                fuera = pg.evaluate(
                    """([valores, excepciones]) => {
                        const ws = [...document.querySelectorAll('main[data-cae-track] > *')].find(e => !e.inert);
                        if (!ws) return null;
                        const raiz = [ws, document.querySelector('.cae-bar'), document.querySelector('.cae-dock')];
                        const malos = [];
                        for (const r of raiz) {
                            if (!r) continue;
                            for (const e of [r, ...r.querySelectorAll('*')]) {
                                if (e.getClientRects().length === 0) continue;
                                if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue;
                                if (excepciones.some(s => e.matches(s))) continue;
                                const px = parseFloat(getComputedStyle(e).fontSize);
                                if (!valores.some(v => Math.abs(v - px) < 0.01)) {
                                    malos.push(e.tagName + '.' + String(e.className).slice(0, 30) + ' = ' + px.toFixed(2) + 'px');
                                }
                            }
                        }
                        return malos;
                    }""",
                    [VALORES, EXCEPCIONES],
                )
                comprobar(
                    fuera is not None and not fuera,
                    f"{ancho}x{alto} {etiqueta} {escena}: todo lo pintado esta en la escala "
                    f"({len(fuera or [])} fuera, p.ej. {(fuera or [])[:3]})",
                )
            ctx.close()
    return errores


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:4173")
    ap.add_argument("--solo", default="", help="familias a correr: 1, 2")
    args = ap.parse_args()
    solo = {x.strip() for x in args.solo.split(",") if x.strip()}
    raiz = pathlib.Path(__file__).resolve().parent.parent
    errores: list[str] = []
    if not solo or "1" in solo:
        errores += familia_estatica(raiz)
    if not solo or "2" in solo:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
            errores += familia_viva(navegador, args.base)
            navegador.close()
    print(f"\n[3] Consola sin errores")
    comprobar(not errores, f"cero errores de consola ({errores[:2]})")
    print(f"\n{len(FALLOS)} fallo(s)")
    for f in FALLOS:
        print(f"  - {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Correr la familia estática y verla en ROJO**

```bash
python3 scripts/measure-escala-tipografica.py --solo 1
```

Esperado: **FALLA** con al menos cuatro fallos — 56 literales en Caelestia, 9 tokens con respaldo,
la escala declarada 3 veces, y `--t-00`/`--t-0` que no existen. Este rojo no es un sabotaje
montado: es el estado real del repo, que es lo que este trabajo viene a arreglar.

- [ ] **Step 3: Levantar el preview y correr la familia viva, también en ROJO**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && nohup npx vite preview --port 4173 --strictPort > /tmp/preview.log 2>&1 &
sleep 3
nohup python3 scripts/measure-escala-tipografica.py --solo 2 --base http://127.0.0.1:4173 > /tmp/escala.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -30 /tmp/escala.log
```

Esperado: **FALLA**, con nodos fuera de la escala en las cinco escenas.

- [ ] **Step 4: Commit del arnés en rojo**

```bash
git add scripts/measure-escala-tipografica.py
git commit -m "test(escala): arnes de la escala tipografica, en rojo contra el estado actual

Dos familias: estatica sobre el fuente (cero literales en Caelestia, cero
tokens con respaldo, escala declarada una vez y en :root) y viva sobre el
build servido (el font-size COMPUTADO de todo lo que pinta texto cae en la
escala). La viva existe porque la estatica se burla sin querer: Tailwind,
estilos en linea y style.css quedan fuera de una regex sobre themes.css.

Las dos salen rojas contra el repo tal cual esta, que es el fallo que
vienen a cazar."
```

---

## Task 1: La escala nueva, declarada una vez

**Files:**
- Modify: `src/themes/themes.css` (L77-86, L1185-1194, L3549-3558)
- Modify: `src/style.css` (9 declaraciones con respaldo)

**Interfaces:**
- Produces: los doce tokens `--t-00` … `--t-10` disponibles en `:root` para todo el sitio, sin
  necesidad de respaldo. Las tareas 2 a 6 los consumen.

- [ ] **Step 1: Quitar las tres declaraciones por tema y poner una en `:root`**

Las tres son idénticas. Localizarlas y borrarlas:

```bash
grep -n -- '--t-1: 12px;' src/themes/themes.css   # tres lineas: 78, 1186, 3550 (aprox)
```

Con este script, que borra los diez tokens de cada bloque de tema y escribe el bloque nuevo al
principio del fichero:

```python
import pathlib, re
p = pathlib.Path("src/themes/themes.css")
s = p.read_text(encoding="utf-8")
# Los diez tokens seguidos, tal como aparecen en los tres bloques.
viejo = re.compile(
    r"\n  --t-1: 12px;\n  --t-2: 16px;\n  --t-3: 21\.33px;\n  --t-4: 28\.43px;\n"
    r"  --t-5: 37\.9px;\n  --t-6: 50\.52px;\n  --t-7: 67\.4px;\n  --t-8: 89\.85px;\n"
    r"  --t-9: 119\.77px;\n  --t-10: 159\.66px;\n"
)
s, n = viejo.subn("\n", s)
assert n == 3, f"esperaba 3 bloques y he encontrado {n}"
nuevo = """/*
 * La escala tipografica del sitio entero. UNA sola declaracion y en `:root` a
 * secas: hasta el 2026-09-07 vivia repetida dentro de los tres bloques de tema
 * con valores identicos, y `style.css` -- que es comun a los tres -- la
 * consumia con respaldo (`var(--t-1, 0.53rem)`, nueve respaldos distintos para
 * tres tokens). Un token que puede valer 8,48 o 12 segun donde se escriba no es
 * un token, es una sugerencia. Con la declaracion aqui, el respaldo sobra.
 *
 * Razon 1,333 (cuarta justa) de --t-1 hacia arriba, y 1,125 de --t-1 hacia
 * abajo. El cambio de razon es deliberado: a 10px el ojo distingue un escalon
 * de 1px y a 120px no distingue quince, asi que una razon unica en todo el
 * rango deja o sin tallas abajo (1,333 bajo 12 solo da 9, y luego 6,75) o con
 * quince arriba que nadie usa. Los dos escalones de abajo salen de los siete
 * valores a ojo que hacian un unico trabajo: rotular.
 */
:root {
  --t-00: 9.5px;
  --t-0: 10.67px;
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
}

"""
p.write_text(nuevo + s, encoding="utf-8")
```

- [ ] **Step 2: Quitar los nueve respaldos de `style.css`**

```python
import pathlib, re
p = pathlib.Path("src/style.css")
s = p.read_text(encoding="utf-8")
s, n = re.subn(r"var\((--t-\d+),\s*[0-9.]+rem\)", r"var(\1)", s)
print(f"{n} respaldos quitados")   # esperado: 9
p.write_text(s, encoding="utf-8")
```

- [ ] **Step 3: Build y familia estática, comprobando qué queda rojo**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
python3 scripts/measure-escala-tipografica.py --solo 1
```

Esperado: los checks 1b, 1c y 1d **en VERDE** (sin respaldos, una sola declaración, doce tokens con
su valor). El 1a sigue **ROJO** con 56 literales: eso lo cierran las tareas 2 a 6.

- [ ] **Step 4: Comprobar que Vice y Hyprland siguen intactos**

Los tokens son los mismos números, así que ninguna talla puede haber cambiado. Confirmarlo, no
asumirlo:

```bash
nohup python3 scripts/measure-obra-rail.py --base http://127.0.0.1:4173 > /tmp/vice.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -5 /tmp/vice.log
nohup python3 scripts/measure-cartel.py --base http://127.0.0.1:4173 > /tmp/hypr.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -5 /tmp/hypr.log
```

Esperado: los dos como estaban antes de tocar nada. Si alguno cambia, la causa es la cascada (la
declaración en `:root` tiene MENOS especificidad que la de tema, así que cualquier regla que
redefiniera un token dentro de un tema ahora gana): revisar `grep -n -- '--t-' src/themes/themes.css`
antes de seguir.

- [ ] **Step 5: Commit**

```bash
git add src/themes/themes.css src/style.css
git commit -m "refactor(escala): dos escalones nuevos y una sola declaracion en :root

--t-00 (9,5px) y --t-0 (10,67px) por debajo del primer escalon, con razon
1,125 en vez de 1,333: a 10px el ojo distingue un escalon de 1px y a 120
no distingue quince.

La escala deja de estar declarada tres veces, una por tema con valores
identicos, y pasa a :root a secas. Con eso los nueve respaldos de
style.css sobran: var(--t-1, 0.53rem) era una segunda escala escondida,
el numero que se pintaria si el token faltara.

Vice y Hyprland sin cambios: son exactamente los mismos numeros."
```

---

## Task 2: El shell (13 declaraciones)

**Files:**
- Modify: `src/themes/themes.css` — líneas L4190, L4216, L4225, L4440, L6154, L6167, L6195, L6217,
  L6253, L6421, L6529, L6535, L6706 (los números se desplazan al aplicar la Task 1: localizar por
  selector, no por línea)

**Interfaces:**
- Consumes: los doce tokens de la Task 1.
- Produces: nada que otras tareas usen.

- [ ] **Step 1: Sustituir las trece**

| selector | hoy | pasa a | Δ |
|---|---|---|---|
| `.cae-meta` | 10px | `var(--t-00)` | +0,50 |
| `.cae-v2` | 26px | `var(--t-4)` | −2,43 |
| `.cae-k` | 9px | `var(--t-00)` | −0,50 |
| `.cae-wsub` | 13px | `var(--t-1)` | +1,00 |
| `.cae-mark` | 0.6875rem | `var(--t-0)` | +0,33 |
| `.cae-ws` | 0.75rem | `var(--t-1)` | 0 |
| `.cae-ws-n` | 0.625rem | `var(--t-00)` | +0,50 |
| `.cae-clock` | 0.8125rem | `var(--t-1)` | +1,00 |
| `.cae-ws-n` (banda ≤640) | 0.75rem | `var(--t-1)` | 0 |
| `.cae-dock-item::after` | 0.65625rem | `var(--t-0)` | −0,17 |
| `.cae-toast-t` | 0.71875rem | `var(--t-1)` | −0,50 |
| `.cae-toast-s` | 0.65625rem | `var(--t-0)` | −0,17 |
| `.cae-meta` (banda ≤900) | 0.5625rem | `var(--t-00)` | −0,50 |

**`.cae-ws-n` y `.cae-meta` aparecen dos veces cada uno, en bandas de `@media` distintas.** Un
reemplazo por texto aterriza en la equivocada. Sustituir por número de línea, releyendo el fichero
tras cada cambio, o comprobar después con `grep -o` sobre el CSS **construido**.

- [ ] **Step 2: Build y comprobar el CSS construido**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
grep -o 'cae-clock{[^}]*}' dist/assets/*.css | head -1
```

Esperado: el bloque de `.cae-clock` cita `var(--t-1)`, no `0.8125rem`.

- [ ] **Step 3: Arnés del shell**

```bash
nohup python3 scripts/measure-caelestia-hora.py --base http://127.0.0.1:4173 > /tmp/hora.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -20 /tmp/hora.log
```

Esperado: 0 fallos. Vigila el contraste del reloj y de la marca sobre el fondo real de la barra, que
es justo lo que estas dos tallas mueven.

- [ ] **Step 4: Captura y mirarla**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox","--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width":1440,"height":900})
    pg.goto("http://127.0.0.1:4173/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_function("document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000)
    pg.wait_for_timeout(2000)
    pg.screenshot(path="/tmp/shell.png")
    b.close()
PY
```

Abrir `/tmp/shell.png` y mirarla de verdad: la barra con las cinco pastillas y el reloj, y el dock.
Lo que se busca es que el reloj no haya crecido de más contra la marca (pasa de 13 a 12) y que las
pastillas sigan alineadas.

- [ ] **Step 5: Commit**

```bash
git add src/themes/themes.css
git commit -m "refactor(escala): las trece tallas del shell pasan a la escala

Barra, reloj, marca, dock, notificacion y las dos metas. Desplazamiento
maximo 2,43px (.cae-v2), mediana 0,50. Arnes de hora en verde."
```

---

## Task 3: Obra (14 declaraciones)

**Files:**
- Modify: `src/themes/themes.css` — bloque de `#obra` y la banda móvil de Obra

**Interfaces:**
- Consumes: los tokens de la Task 1.

- [ ] **Step 1: Sustituir las catorce**

| selector | hoy | pasa a | Δ |
|---|---|---|---|
| `.cae-obra-caption` | 14px | `var(--t-1)` | +2,00 |
| `.cae-obra-tag` | 9px | `var(--t-00)` | −0,50 |
| `.cae-obra-drawer-kick` | 10.5px | `var(--t-0)` | −0,17 |
| **`.cae-obra-drawer-title h3`** | **34px** | **`var(--t-5)`** | **+3,90** |
| `.cae-obra-drawer-lead` | 14px | `var(--t-1)` | +2,00 |
| `.cae-obra-drawer-meta dt` | 9.5px | `var(--t-00)` | 0 |
| `.cae-obra-drawer-meta dd` | 13px | `var(--t-1)` | +1,00 |
| `.cae-obra-stack-text` | 10.5px | `var(--t-0)` | −0,17 |
| `.cae-obra-prose h4` | 10px | `var(--t-00)` | +0,50 |
| `.cae-obra-prose p` | 14px | `var(--t-1)` | +2,00 |
| `.cae-obra-prose p` (segunda regla) | 13.5px | `var(--t-1)` | +1,50 |
| `.cae-obra-foot a` | 12.5px | `var(--t-1)` | +0,50 |
| `.cae-obra-foot-private` | 13px | `var(--t-1)` | +1,00 |
| `.cae-obra-caption` (banda móvil) | 12px | `var(--t-1)` | 0 |

`.cae-obra-caption` y `.cae-obra-prose p` aparecen dos veces cada uno: mismo aviso que en la Task 2.

- [ ] **Step 2: Build y arnés de Obra**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
nohup python3 scripts/measure-caelestia-obra.py --base http://127.0.0.1:4173 > /tmp/obra.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -20 /tmp/obra.log
```

Esperado: **los mismos tres fallos de contraste de siempre y ninguno más.** Ese arnés falla con tres
hallazgos (`bg=rgba(0, 0, 0, 0)`) desde antes de fusionar B5, y es su propio instrumento, que no
resuelve el fondo pintado. Si aparece un cuarto, es de este cambio.

- [ ] **Step 3: Captura del cajón abierto, con el titular que se mueve 3,9px**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox","--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width":1440,"height":900})
    pg.goto("http://127.0.0.1:4173/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_function("document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000)
    pg.click('[data-cae-ws="obra"]'); pg.wait_for_timeout(2600)
    pg.screenshot(path="/tmp/obra-cajon.png")
    print(pg.evaluate("""() => { const h = document.querySelector('.cae-obra-drawer-title h3');
        const r = h.getBoundingClientRect(); const ws = document.querySelector('#obra').getBoundingClientRect();
        return { alto: Math.round(r.height), lineas: Math.round(r.height / parseFloat(getComputedStyle(h).lineHeight)),
                 cabe: r.bottom <= ws.bottom + 1 }; }"""))
    b.close()
PY
```

Mirar la captura y el número: **si el titular pasa a dos líneas o se sale del cajón, se arregla la
CAJA** (el ancho del cajón, su relleno o el `line-height` del titular), nunca devolviendo los 34px.

- [ ] **Step 4: Commit**

```bash
git add src/themes/themes.css
git commit -m "refactor(escala): las catorce tallas de Obra pasan a la escala

Incluye el titular del cajon, que sube de 34 a 37,9px (+3,90, el mayor
desplazamiento de toda la migracion). Comprobado en captura que sigue en
una linea y dentro del cajon. El arnes de Obra sigue con sus tres fallos
de contraste conocidos y ninguno mas."
```

---

## Task 4: Stack (11 declaraciones) y la altura de la cabecera

**Files:**
- Modify: `src/themes/themes.css` — bloque de `#credits`, la banda ≤900 y la banda ≤640

**Interfaces:**
- Consumes: los tokens de la Task 1.
- Produces: el valor nuevo de `min-height` de `.cae-cred-cab` en la banda ≤640, que sustituye a los
  `15.875rem` (254px) actuales.

- [ ] **Step 1: Sustituir las once**

| selector | hoy | pasa a | Δ |
|---|---|---|---|
| `.cae-cred-rot h4` | 16px | `var(--t-2)` | 0 |
| `.cae-cred-nom` | 10px | `var(--t-00)` | +0,50 |
| **`.cae-cred-nombre`** | **32px** | **`var(--t-4)`** | **−3,57** |
| `.cae-cred-detalle` | 17px | `var(--t-2)` | +1,00 |
| `.cae-cred-cab .cae-cred-terr` | 10px | `var(--t-00)` | +0,50 |
| `.cae-cred-cruce > span` | 9.5px | `var(--t-00)` | 0 |
| `.cae-cred-cruce-lista li` | 26px | `var(--t-4)` | −2,43 |
| `.cae-cred-cruce-lista li.is-vacia` | 21px | `var(--t-3)` | −0,33 |
| `.cae-cred-cruce-lista li` (banda ≤640) | 1.0625rem | `var(--t-2)` | +1,00 |
| `.cae-cred-nom` (banda ≤900) | 0.53rem | `var(--t-00)` | −1,02 |
| `.credit-name` | 0.8rem | `var(--t-1)` | +0,80 |

- [ ] **Step 2: Volver a medir la altura de la cabecera en el teléfono**

`.cae-cred-cab` tiene `min-height: 15.875rem` (254px) en la banda ≤640, y ese número **no es
decorativo**: se fijó al peor caso de las 23 piezas porque si la cabecera cambia de alto al elegir,
la tira baja bajo el dedo entre el `pointerdown` y el `click` y tocas una pieza pero se elige otra.
Al bajar el nombre de 32 a 28,43 el peor caso cambia. Medirlo:

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox","--use-gl=swiftshader"])
    for w in (360, 390, 430):
        ctx = b.new_context(viewport={"width": w, "height": 800}, device_scale_factor=2,
                            is_mobile=True, has_touch=True)
        pg = ctx.new_page()
        pg.goto("http://127.0.0.1:4173/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_function("document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000)
        pg.click('[data-cae-ws="creditos"]'); pg.wait_for_timeout(2600)
        print(w, pg.evaluate("""async () => {
          const ws = document.querySelector('[data-scene="credits"]');
          const cab = ws.querySelector('.cae-cred-cab');
          cab.style.minHeight = '0px';           // medir el contenido, no la reserva
          const altos = [];
          for (const btn of ws.querySelectorAll('.cae-cred-pieza')) {
            btn.click(); await new Promise(r => setTimeout(r, 40));
            altos.push([btn.dataset.pieza, Math.round(cab.getBoundingClientRect().height)]);
          }
          cab.style.minHeight = '';
          altos.sort((a, b) => b[1] - a[1]);
          return { peor: altos[0], mejor: altos[altos.length - 1] };
        }"""))
        ctx.close()
    b.close()
PY
```

Tomar el mayor de los tres anchos, redondear hacia arriba al cuarto de píxel y escribirlo en
`rem` (dividir entre 16). Ejemplo: si el peor caso sale 248px, `min-height: 15.5rem`. Dejar el
comentario que ya está encima explicando por qué existe, actualizando el número medido.

- [ ] **Step 3: Arneses de Stack, uno detrás de otro**

```bash
nohup python3 scripts/measure-caelestia-creditos.py --base http://127.0.0.1:4173 > /tmp/cred.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -20 /tmp/cred.log
nohup python3 scripts/measure-caelestia-movil.py --base http://127.0.0.1:4173 > /tmp/movil.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -20 /tmp/movil.log
```

Esperado en Créditos: sus fallos conocidos y ninguno más — arrastra un `hover` que expira
(«element is outside of the viewport»), reproducido igual antes de B6, que sale como excepción y no
como aserción roja. Esperado en móvil: **0 fallos**, incluida la familia 5b, que comprueba que la
cabecera mide siempre lo mismo elijas la pieza que elijas. Si 5b sale roja, el `min-height` del
Step 2 está mal medido.

- [ ] **Step 4: Commit**

```bash
git add src/themes/themes.css
git commit -m "refactor(escala): las once tallas de Stack, y la cabecera vuelve a medirse

El nombre de pieza baja de 32 a 28,43px (-3,57), asi que el peor caso de
las 23 cabeceras cambia y con el la altura fija que las iguala. Sin
volver a medirla, la tira se mueve bajo el dedo al elegir y tocas una
pieza pero se elige otra (el fallo de e4beed5).

Arnes de movil en verde, familia 5b incluida."
```

---

## Task 5: Quién soy (8 declaraciones)

**Files:**
- Modify: `src/themes/themes.css` — bloque de `[data-ficha="neofetch"]` y la banda ≤900

**Interfaces:**
- Consumes: los tokens de la Task 1.

- [ ] **Step 1: Sustituir las ocho**

| selector | hoy | pasa a | Δ |
|---|---|---|---|
| `.ficha-cmd-linea` | 0.95rem | `var(--t-2)` | −0,80 |
| **`.ficha-nombre`** | **3.35rem** | **`var(--t-6)`** | **−3,08** |
| `.ficha-host` | 0.95rem | `var(--t-2)` | −0,80 |
| `.ficha-estado` | 0.78rem | `var(--t-1)` | +0,48 |
| `.ficha-frase` | 1.06rem | `var(--t-2)` | +0,96 |
| `.ficha-fila` | 0.92rem | `var(--t-2)` | −1,28 |
| `.ficha-rotulo` | 0.72rem | `var(--t-1)` | −0,48 |
| **`.ficha-nombre`** (banda ≤900) | **1.625rem** | **`var(--t-4)`** | **+2,43** |

- [ ] **Step 2: Build y arnés de Quién soy**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
nohup python3 scripts/measure-caelestia-quien-soy.py --base http://127.0.0.1:4173 > /tmp/quien.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -20 /tmp/quien.log
```

Esperado: 0 fallos. Ese arnés comprueba explícitamente que **el nombre no se parte en tres líneas** y
que el filete medido con `Range` guarda su relación con el retrato: son las dos cosas que un cambio
de 3px en el nombre puede romper.

- [ ] **Step 3: Captura en los dos anchos y mirarlas**

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox","--use-gl=swiftshader"])
    for nombre, w, h, movil in (("escritorio", 1440, 900, False), ("movil", 390, 844, True)):
        kw = {"viewport": {"width": w, "height": h}}
        if movil: kw |= {"device_scale_factor": 2, "is_mobile": True, "has_touch": True}
        ctx = b.new_context(**kw); pg = ctx.new_page()
        pg.goto("http://127.0.0.1:4173/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_function("document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000)
        pg.click('[data-cae-ws="quien-es"]'); pg.wait_for_timeout(2600)
        pg.screenshot(path=f"/tmp/quien-{nombre}.png"); ctx.close()
    b.close()
PY
```

Mirar las dos. El nombre es el ancla de identidad de la escena: si a 50,52px pierde presencia contra
el retrato, **se ajusta el retrato o la medida de la columna**, no se devuelven los 53,6px.

- [ ] **Step 4: Commit**

```bash
git add src/themes/themes.css
git commit -m "refactor(escala): las ocho tallas de Quien soy pasan a la escala

El nombre baja de 53,6 a 50,52 en escritorio y sube de 26 a 28,43 en
movil. El arnes comprueba que sigue sin partirse en tres lineas y que el
filete medido con Range guarda su relacion con el retrato."
```

---

## Task 6: Título (10 declaraciones)

**Files:**
- Modify: `src/themes/themes.css` — bloque de `#hero`, la tarjeta «Ahora mismo» y la banda ≤900

**Interfaces:**
- Consumes: los tokens de la Task 1.

- [ ] **Step 1: Sustituir las diez**

| selector | hoy | pasa a | Δ |
|---|---|---|---|
| `.cae-firma` | 30px | `var(--t-4)` | +1,57 |
| `.cae-term-line` | 20px | `var(--t-3)` | −1,33 |
| `.cae-whd` | 9.5px | `var(--t-00)` | 0 |
| `.cae-wnow` | 27px | `var(--t-4)` | −1,43 |
| `.cae-wfecha` | 9.5px | `var(--t-00)` | 0 |
| `.cae-wnombre` | 12.5px | `var(--t-1)` | +0,50 |
| `.cae-pilla` | 10.5px | `var(--t-0)` | −0,17 |
| `.cae-mv-prosa` | 0.8125rem | `var(--t-1)` | +1,00 |
| `.cae-mv-cifras` | 0.625rem | `var(--t-00)` | +0,50 |
| `.cae-mv-cifra b` | 0.9375rem | `var(--t-2)` | −1,00 |

**No tocar `#hero .cae-ln`**: el titular se justifica desde TS (`caelestia.titulo.ts:48-52`) y su
tamaño lo decide el ancho de la medida. Es la única excepción del gate, por selector.

**Contacto no tiene ninguna declaración que migrar**, y no es un olvido: B5 se construyó entera
sobre los tokens, incluida su cuarta voz tipográfica a `--t-10`. Es la prueba de que la escala se
podía respetar desde el principio.

- [ ] **Step 2: Build y arnés de Título**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build
nohup python3 scripts/measure-caelestia-titulo.py --base http://127.0.0.1:4173 > /tmp/titulo.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -20 /tmp/titulo.log
```

Esperado: 0 fallos. Vigila que la tarjeta «Ahora mismo» no pise la columna de cifras a 1366x768
(`tarjeta_portatil`), que es lo que puede mover `.cae-wnow` al bajar 1,43px, y que las tres líneas
del titular siguen midiendo lo mismo.

- [ ] **Step 3: Commit**

```bash
git add src/themes/themes.css
git commit -m "refactor(escala): las diez tallas de Titulo pasan a la escala

Firma, terminal, tarjeta Ahora mismo y el bloque movil de B6. El titular
justificado queda fuera a proposito: su tamano lo decide el ancho de la
medida desde TS, asi que no puede estar en la escala por construccion.
Es la unica excepcion del gate, y va por selector."
```

---

## Task 7: Cierre

**Files:**
- Modify: `docs/superpowers/specs/2026-09-07-escala-tipografica-design.md`
- Modify: `.claude/rules/verification.md`
- Modify: `CLAUDE.md` y `.claude/CLAUDE.md`

- [ ] **Step 1: El gate entero, las dos familias en verde**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
nohup python3 scripts/measure-escala-tipografica.py --base http://127.0.0.1:4173 > /tmp/escala.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -30 /tmp/escala.log
```

Esperado: **0 fallos**. Si la familia viva encuentra algo fuera de la escala, es una talla que llega
por un camino que la estática no ve (Tailwind, `style.css`, estilo en línea): perseguirla hasta el
origen, no añadirla a `EXCEPCIONES`.

- [ ] **Step 2: Ver la familia VIVA en rojo contra un fallo que la estática no puede ver**

Este es el sabotaje que da valor a la segunda familia. Con el build ya migrado y verde:

```bash
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox","--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width":1440,"height":900})
    pg.goto("http://127.0.0.1:4173/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_function("document.documentElement.dataset.caeShell === 'workspaces'", timeout=12000)
    pg.wait_for_timeout(1500)
    # Un tamano en linea, invisible para cualquier regex sobre el CSS.
    pg.evaluate("() => { document.querySelector('.cae-clock').style.fontSize = '13.7px'; }")
    print(pg.evaluate("""() => { const e = document.querySelector('.cae-clock');
        return getComputedStyle(e).fontSize; }"""))
    b.close()
PY
```

Comprobar a mano que 13,7px no está en `VALORES` y que la familia viva lo marcaría: la aserción es
`valores.some(v => Math.abs(v - px) < 0.01)`. Para verlo rojo de verdad, añadir temporalmente al
arnés un `pg.evaluate` que ponga ese estilo antes de medir, correr `--solo 2`, ver el FALLO, y
quitarlo. Dejar constancia del número en el commit.

- [ ] **Step 3: Los siete arneses de Caelestia, uno detrás de otro, y `verify.py`**

```bash
for a in hora titulo quien-soy obra creditos fundido cursor movil; do
  nohup python3 scripts/measure-caelestia-$a.py --base http://127.0.0.1:4173 > /tmp/$a.log 2>&1 &
  PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done
  echo "$a: $(grep -cE '^  FALLO' /tmp/$a.log) fallos"
done
python3 scripts/verify.py --url http://127.0.0.1:4173
```

Esperado: cero fallos nuevos. Los conocidos que siguen valiendo: los tres de contraste de Obra y el
`hover` que expira en Créditos. `verify.py` con código 0 (12 conocidos, 0 nuevos).

- [ ] **Step 4: Vera sobre las cinco escenas**

Lanzar `vera-art-director` con `model: sonnet`, sobre `http://127.0.0.1:4173/?theme=caelestia`, a
1440x900 y 390x844. La pregunta concreta no es «¿está la escala?» sino **«¿se nota que las tallas
ahora son doce?»**: si la jerarquía no se lee mejor, el trabajo ha sido contable y no de diseño.
En el brief: que no edite nada de `src/`, que no use `pkill` y que espere por PID dentro del mismo
comando.

- [ ] **Step 5: Documentación y cierre**

- Spec a `Estado: implementado` y añadir `## Registro de implementación` con: el desplazamiento real
  de las seis que se movían más de 2px, qué cajas hubo que tocar, el valor nuevo del `min-height` de
  la cabecera de Stack, y el veredicto de Vera.
- Fila de `measure-escala-tipografica.py` en la tabla de `.claude/rules/verification.md`.
- Bloque de estado en `CLAUDE.md` y `.claude/CLAUDE.md`, con lo que hay que saber para no
  deshacerlo: la escala se declara **una vez y en `:root`**, no se usa token con respaldo, y la
  única excepción es el titular justificado de B1.
- Marcar las casillas de este plan conforme se van cerrando, no en bloque al final.

- [ ] **Step 6: Commit del cierre**

```bash
git add -A
git commit -m "docs(escala): registro de implementacion y cierre de la escala tipografica"
```

---

## Verificación final

- [ ] `npm run build` y `npm run lint` limpios
- [ ] `measure-escala-tipografica.py` con 0 fallos, y su familia viva vista en rojo contra un
      `font-size` en línea
- [ ] Los ocho arneses de Caelestia sin fallos nuevos
- [ ] `verify.py` con código 0
- [ ] Capturas miradas de las seis tallas que se mueven más de 2px
- [ ] Vera pasada, con su veredicto anotado en el spec
- [ ] Spec en `implementado` y este plan con todas las casillas marcadas
