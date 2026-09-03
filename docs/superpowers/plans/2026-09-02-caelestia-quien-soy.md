# Caelestia B2 — «Quién soy» como salida de `neofetch`: plan de implementación

> **Para quien ejecute con agentes:** SUB-SKILL OBLIGATORIA: usa
> `superpowers:subagent-driven-development` (recomendado) o
> `superpowers:executing-plans` para implementar este plan tarea a tarea. Los pasos
> llevan casillas (`- [ ]`) para poder marcarlos.

**Objetivo:** que la escena `#about` del tema Caelestia deje de ser una ficha apretada y pase a ser
la salida de `neofetch` — el comando que un escritorio de Linux ejecuta para decir qué máquina es
esta.

**Arquitectura:** un bloque aditivo nuevo en `src/sections/about.ts`, oculto por defecto y visible
solo bajo `:root[data-theme="caelestia"]` — la tercera instancia del patrón que ya usan las parejas
de Vice y la placa de Hyprland. El CSS vive en `themes.css`; la entrada, el filete medido y el
rótulo de la tira viven en un módulo nuevo, `src/themes/caelestia.ficha.ts`, que la coreografía
invoca cuando el workspace se activa.

**Stack:** Vite 8 + TypeScript estricto (vanilla, sin framework) + Tailwind 4 + GSAP 3. Sin tests
unitarios en el repo: **la verificación es un arnés de Playwright**, igual que el resto de
dispositivos del proyecto.

**Spec:** `docs/superpowers/specs/2026-09-02-caelestia-quien-soy-design.md`

## Restricciones globales

Copiadas del spec y de `CLAUDE.md`. Valen para **todas** las tareas.

- **Nunca `gsap.from`.** Siempre `fromTo` con los dos extremos escritos a mano. Ya provocó tres
  regresiones reales.
- **Toda coreografía destructura `gsap` del contexto que recibe.** Un `gsap` suelto compila, pasa el
  linter y revienta en el navegador — le pasó a Hyprland y su coreografía no corrió durante semanas.
- **Cero `any`.** `strict` está activo; usa `unknown` + guardas.
- **`prefers-reduced-motion` obligatorio:** escena montada, sin recorrido.
- **Anti-mock:** si no está en `src/data/content.ts`, no se pinta.
- **Vice no se toca.** Hyprland no se toca. `shaderBackground.ts` no se toca. La fase A (barra, dock,
  carril, motor de color) no se toca. **El fondo es de B1**, no de esta fase.
- **Un `transform` en línea de GSAP gana siempre a una regla CSS**: si un nodo recibe entrada con
  GSAP, su hover se anima en un hijo o en el envoltorio, nunca en el mismo nodo.
- **DONE exige:** `npm run build` verde, `npm run lint` limpio, **captura de los tres temas** (no
  solo Caelestia) y consola sin errores. Un `tsc` verde no garantiza que el canvas pinte.
- **Node 22 obligatorio:** `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`. Con Node 18,
  `vite build` revienta dentro de rolldown con un error sobre `styleText` que no menciona la versión.
- **El tema se sortea por visita:** toda URL de verificación lleva `?theme=caelestia`.
- **Verificar contra el build servido**, nunca contra `npm run dev`: el HMR corrompe las medidas.

### Dependencia de B1, y qué hacer si aún no ha aterrizado

Esta fase usa `--cae-display-axes-cartel` (`"opsz" 144, "wght" 900, "SOFT" 0, "WONK" 1`), que
**introduce B1**. B1 se está implementando en paralelo.

**Antes de la Tarea 2**, comprueba si ya existe:

```bash
grep -n "cae-display-axes-cartel" src/themes/themes.css
```

- Si **sale**: no lo declares otra vez, úsalo.
- Si **no sale**: decláralo tú en la Tarea 2, junto a `--cae-display-axes`, con el valor exacto de
  arriba. Si luego B1 lo trae también, el conflicto de merge es de una línea idéntica y se resuelve
  quedándose con una.

---

## Estructura de ficheros

| fichero | responsabilidad |
|---|---|
| `src/sections/about.ts` (modificar) | añade `createFicha()`: solo construye DOM, cero estilo, cero animación. Se cuelga en `createAbout()` junto a `createPlaca()` |
| `src/themes/themes.css` (modificar) | la regla base que oculta la ficha en los tres temas, el bloque `:root[data-theme="caelestia"]` con toda su piel, y la regla gemela que oculta los bloques viejos bajo Caelestia |
| `src/themes/caelestia.ficha.ts` (crear) | lo único que no puede hacer el CSS: medir el filete con `Range`, la línea de tiempo de la entrada y el rótulo de la tira. Devuelve un handle con `destroy()` |
| `src/themes/caelestia.choreography.ts` (modificar) | invoca el módulo cuando el workspace «Quién soy» se activa |
| `scripts/measure-caelestia-quien-soy.py` (crear) | los ocho gates del spec |

Las figuras (`polygon()` de 240 puntos) se generan con el script ya rescatado al repo,
`docs/superpowers/specs/2026-09-02-caelestia-quien-soy-figuras.py`, y se pegan como literales en el
CSS: no hay generación en tiempo de ejecución.

---

### Tarea 1: El bloque aditivo en el DOM

**Ficheros:**
- Modificar: `src/sections/about.ts` (añadir `createFicha()`; colgarla en `createAbout()`)
- Modificar: `src/themes/themes.css` (una sola regla, la que la oculta por defecto)

**Interfaces:**
- Consume: `identity`, `aboutCopy`, `education`, `experience`, `focusAreas`, `stats` de
  `../data/content`; los helpers `el()` de `../utils/dom` y `statValue()` que ya existe en el propio
  `about.ts`.
- Produce: `createFicha(): HTMLElement`, y estos ganchos que las tareas 2, 3 y 4 seleccionan:
  `[data-ficha="neofetch"]` (raíz), `[data-ficha-cmd]`, `[data-ficha-cursor]`,
  `[data-ficha-retrato]`, `[data-ficha-nombre]`, `[data-ficha-host]`, `[data-ficha-regla]`,
  `[data-ficha-frase]`, `[data-ficha-fila]`, `[data-ficha-tira]`, `[data-ficha-prompt]`,
  `[data-ficha-grupo]` (los nodos que la entrada escalona).

- [x] **Paso 1: escribir la aserción que falla**

En `scripts/measure-caelestia-quien-soy.py`, crea el arnés con **solo este gate** por ahora:

```python
"""Arnes de la escena «Quien soy» de Caelestia (fase B2).

Se lanza a mano contra el build de produccion servido, NUNCA contra `npm run
dev`: el HMR corrompe las medidas.

    npm run build && npx vite preview --port 4173 &
    python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4173
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

FALLOS: list[str] = []


def comprobar(condicion: bool, etiqueta: str) -> None:
    print(("  OK   " if condicion else "  FALLO") + f"  {etiqueta}")
    if not condicion:
        FALLOS.append(etiqueta)


def escena_activa(pagina):
    """Lleva el carril a «Quien soy» y devuelve (escena, ventana).

    La ventana es la que CONTIENE la escena, no «la que esta en x=14»: durante
    la transicion del carril esa posicion todavia la ocupa el hero, y medir
    contra el da los numeros de otra escena.
    """
    pagina.click('[data-cae-ws="quien-es"]')
    pagina.wait_for_timeout(1400)
    return pagina.evaluate("""() => {
        const sc = document.querySelector('[data-scene="about"]');
        const v = sc && sc.closest('main[data-cae-track] > *');
        return { hayEscena: !!sc, hayVentana: !!v };
    }""")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:4173")
    args = ap.parse_args()

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
        errores: list[str] = []
        pagina.on("pageerror", lambda e: errores.append(str(e)))
        pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)

        pagina.goto(f"{args.base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        pagina.wait_for_timeout(3000)
        escena_activa(pagina)

        print("\n[1] La ficha existe y esta en el DOM")
        hay = pagina.evaluate("() => !!document.querySelector('[data-ficha=\\"neofetch\\"]')")
        comprobar(hay, "la ficha [data-ficha=neofetch] existe en el DOM")

        comprobar(not errores, f"consola sin errores ({len(errores)})")
        navegador.close()

    print(f"\n{'TODO VERDE' if not FALLOS else f'{len(FALLOS)} FALLO(S)'}")
    for f in FALLOS:
        print(f"  - {f}")
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [x] **Paso 2: verla dar rojo**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npx vite preview --port 4173 &
sleep 2
python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4173
```

Esperado: `FALLO  la ficha [data-ficha=neofetch] existe en el DOM`, salida 1.

- [x] **Paso 3: escribir `createFicha()`**

En `src/sections/about.ts`, justo antes de `export function createAbout()`:

```ts
/** Una fila clave/valor de la salida, con su detalle opcional debajo. */
function fichaFila(clave: string, valor: string, detalle?: string): HTMLElement {
  const dd = el("dd", "ficha-v", [valor]);
  if (detalle) dd.append(el("small", "ficha-s", [detalle]));
  const fila = el("div", "ficha-fila", [el("dt", "ficha-k", [clave]), dd]);
  fila.setAttribute("data-ficha-fila", "");
  return el("div", "", [fila]);
}

/**
 * La escena «Quien soy» de Caelestia: la salida de `neofetch`.
 *
 * Se anade al DOM de los tres temas y se envia oculta (`display: none` en la
 * regla base de themes.css, visible solo bajo `:root[data-theme="caelestia"]`).
 * Patron aditivo estricto, el mismo que `createPlaca()` y `createPairs()`: el
 * tema se sortea por visita y se cambia sin recargar, asi que el DOM no puede
 * construirse segun `data-theme`.
 *
 * Cero datos nuevos. La cabecera del comando es `identity.email` — no un
 * `usuario@host` inventado — y ademas es la unica parada de tabulador de la
 * escena: el resto no navega a ninguna parte y esta entero a la vista.
 */
function createFicha(): HTMLElement {
  const foto = el("img", "ficha-foto");
  foto.src = identity.githubAvatar;
  foto.alt = identity.name;
  foto.width = 288;
  foto.height = 288;
  foto.loading = "lazy";
  foto.decoding = "async";
  /*
   * El anillo del roce es un ENVOLTORIO con el mismo `clip-path`, no un
   * `outline`: un contorno no sigue un recorte, se dibujaria rectangular.
   */
  const anillo = el("span", "ficha-anillo", [foto]);
  anillo.setAttribute("data-ficha-retrato", "");
  const retrato = el("div", "ficha-arte", [anillo]);
  retrato.setAttribute("data-ficha-grupo", "");

  const cursor = el("i", "ficha-cursor", ["▌"]);
  cursor.setAttribute("data-ficha-cursor", "");
  const comando = el("b", "ficha-cmd", []);
  comando.setAttribute("data-ficha-cmd", "");
  const linea = el("p", "ficha-cmd-linea", [el("span", "ficha-prompt", ["~ $"]), " ", comando, cursor]);

  const nombre = el("p", "ficha-nombre", [identity.name]);
  nombre.setAttribute("data-ficha-nombre", "");
  const grupoNombre = el("div", "", [nombre]);
  grupoNombre.setAttribute("data-ficha-grupo", "");

  const host = el("a", "ficha-host", [identity.email]);
  host.href = `mailto:${identity.email}`;
  host.setAttribute("data-ficha-host", "");

  const punto = el("i", "ficha-punto", []);
  const estado = el("span", "ficha-estado", [punto, identity.availability]);

  const identidad = el("div", "ficha-id", [host, estado]);
  identidad.setAttribute("data-ficha-grupo", "");

  const regla = el("div", "ficha-regla", []);
  regla.setAttribute("data-ficha-regla", "");

  const frase = el("p", "ficha-frase", [aboutCopy[0] ?? ""]);
  frase.setAttribute("data-ficha-frase", "");
  const grupoFrase = el("div", "", [frase]);
  grupoFrase.setAttribute("data-ficha-grupo", "");

  /*
   * `Desde` se lee por su ROTULO, no por su indice: `stats` es un literal de
   * este mismo repo y atarlo a `stats[0]` deja una rotura silenciosa la
   * proxima vez que alguien lo reordene. Misma precaucion que `statValue()`.
   */
  const desde = statValue("Desde");
  const titulos = focusAreas.map((area) => area.title).join("  ·  ");
  const primerEnfoque = focusAreas[0];
  const segundoEnfoque = focusAreas[1];
  const filaEnfoque = fichaFila("Enfoque", titulos, primerEnfoque?.detail ?? "");
  if (segundoEnfoque) {
    filaEnfoque.querySelector(".ficha-v")?.append(el("small", "ficha-s", [segundoEnfoque.detail]));
  }

  const trabajo = experience[0];
  const carrera = education[0];
  const filas = el("dl", "ficha-filas", [
    fichaFila("Rol", identity.role),
    fichaFila("Base", identity.location),
    fichaFila("Ahora", identity.now, desde ? `Desde ${desde}` : undefined),
    filaEnfoque,
    fichaFila(
      "Último puesto",
      `${trabajo?.role ?? ""} · ${trabajo?.organization ?? ""}`,
      trabajo?.period ?? "",
    ),
    fichaFila(
      "Estudia",
      carrera?.degree ?? "",
      `${carrera?.institution ?? ""} · ${carrera?.period ?? ""}`,
    ),
  ]);

  // La tira de color con la que `neofetch` cierra siempre. Los nueve tonos son
  // los tokens de la hora: el color lo pone el CSS, no este modulo.
  const tira = el(
    "div",
    "ficha-tira",
    [
      "--cae-surface",
      "--cae-surface-container",
      "--cae-surface-container-high",
      "--cae-primary",
      "--cae-primary-container",
      "--cae-anchor",
      "--cae-wall-1",
      "--cae-wall-2",
      "--cae-wall-3",
    ].map((token) => {
      const tono = el("i", "ficha-tono", []);
      tono.setAttribute("data-ficha-tono", token);
      return tono;
    }),
  );
  tira.append(el("span", "ficha-rotulo", []));
  tira.setAttribute("data-ficha-tira", "");
  const grupoTira = el("div", "", [tira]);
  grupoTira.setAttribute("data-ficha-grupo", "");

  const cursorFinal = el("i", "ficha-cursor", ["▌"]);
  cursorFinal.setAttribute("data-ficha-prompt", "");
  const promptFinal = el("p", "ficha-cmd-linea ficha-cmd-fin", [
    el("span", "ficha-prompt", ["~ $"]),
    " ",
    cursorFinal,
  ]);

  const columna = el("div", "ficha-col", [
    grupoNombre,
    identidad,
    regla,
    grupoFrase,
    filas,
    grupoTira,
  ]);
  const cuerpo = el("div", "ficha-cuerpo", [retrato, columna]);
  const ficha = el("div", "ficha", [linea, cuerpo, promptFinal]);
  ficha.setAttribute("data-ficha", "neofetch");
  return ficha;
}
```

Y en `createAbout()`, añade `createFicha()` al array de `body`, después de `createPlaca()`:

```ts
  const body = el("div", "about-body", [
    createLine("lead", "lead text-paper/90", aboutCopy[0] ?? ""),
    createPairs(),
    createLine("note", "block mt-3 text-sm leading-relaxed text-paper/85", aboutCopy[1] ?? ""),
    createStats(),
    createTrack(),
    createPlaca(),
    createFicha(),
  ]);
```

- [x] **Paso 4: ocultarla por defecto**

En `src/themes/themes.css`, junto a la regla base que ya oculta la placa de Hyprland:

```css
/* La ficha de Caelestia viaja en los tres temas y se envia oculta: solo la
   pinta `:root[data-theme="caelestia"]`. Patron aditivo estricto. */
[data-ficha="neofetch"] {
  display: none;
}
```

- [x] **Paso 5: verla dar verde**

```bash
npm run build && npx vite preview --port 4173 &
sleep 2
python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4173
```
Esperado: `OK   la ficha [data-ficha=neofetch] existe en el DOM`, salida 0.

- [x] **Paso 6: comprobar que Vice e Hyprland no cambian**

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for tema in ("vice", "hyprland"):
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://localhost:4173/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
        pg.wait_for_timeout(6000)
        visible = pg.evaluate("""() => {
            const f = document.querySelector('[data-ficha="neofetch"]');
            return f ? getComputedStyle(f).display : 'sin ficha';
        }""")
        assert visible == "none", (tema, visible)
        assert not errs, (tema, errs)
        pg.screenshot(path=f"/tmp/b2-t1-{tema}.png", full_page=True)
        print(tema, "OK · ficha display:", visible)
    b.close()
EOF
```
Mira las dos capturas antes de seguir. Un selector mal cerrado no lo caza ni `tsc` ni `eslint`.

- [x] **Paso 7: commit**

```bash
git add src/sections/about.ts src/themes/themes.css scripts/measure-caelestia-quien-soy.py
git commit -m "feat(caelestia): el DOM de la ficha de Quien soy, oculta por defecto"
```

---

### Tarea 2: La piel — el bloque CSS de Caelestia

**Ficheros:**
- Modificar: `src/themes/themes.css` (bloque nuevo bajo `:root[data-theme="caelestia"]`, en el hueco
  entre las reglas de escena y las del shell — justo antes de `.cae-bar`)
- Modificar: `scripts/measure-caelestia-quien-soy.py` (gates 1 y 2 del spec)

**Interfaces:**
- Consume: los ganchos `data-ficha-*` de la Tarea 1; los tokens `--cae-*` de la fase A;
  `--cae-display-axes-cartel` (ver «Dependencia de B1» arriba).
- Produce: la escena maquetada. Alto esperado ≈638 px, aire ≈55/56, nombre en 1 línea.

- [x] **Paso 1: escribir los dos gates que fallan**

Sustituye el bloque `print("\n[1] ...")` del arnés por:

```python
        print("\n[1] Cabe en la ventana, y el aire esta repartido")
        medida = pagina.evaluate("""() => {
            const sc = document.querySelector('[data-scene="about"]');
            const ventana = sc.closest('main[data-cae-track] > *');
            const wr = ventana.getBoundingClientRect();
            let top = Infinity, bot = -Infinity;
            // Solo las HOJAS: un contenedor a toda la altura devolveria el alto
            // de la ventana y dejaria el aire en 0/0, que no dice nada.
            const visitar = (el) => {
                for (const h of el.children) {
                    if (h.children.length === 0) {
                        const r = h.getBoundingClientRect();
                        if (r.width > 0 && r.height > 0) {
                            top = Math.min(top, r.top); bot = Math.max(bot, r.bottom);
                        }
                    } else visitar(h);
                }
            };
            visitar(sc);
            return {
                alto: Math.round(bot - top),
                arriba: Math.round(top - wr.top),
                abajo: Math.round(wr.bottom - bot),
                desborde: ventana.scrollHeight - ventana.clientHeight,
                ventana: Math.round(wr.height),
            };
        }""")
        print(f"       alto {medida['alto']} · aire {medida['arriba']}/{medida['abajo']} "
              f"· ventana {medida['ventana']}")
        comprobar(medida["ventana"] == 748, f"la ventana mide 748 px ({medida['ventana']})")
        comprobar(medida["abajo"] >= 0, f"aire bajo el pie >= 0 ({medida['abajo']})")
        comprobar(medida["desborde"] <= 1, f"la ventana no desborda ({medida['desborde']} px)")

        print("\n[2] El nombre no parte")
        lineas = pagina.evaluate("""() => {
            const n = document.querySelector('[data-ficha-nombre]');
            const lh = parseFloat(getComputedStyle(n).lineHeight);
            return Math.max(1, Math.round(n.getBoundingClientRect().height / lh));
        }""")
        comprobar(lineas == 1, f"el nombre cabe en 1 linea ({lineas})")
```

- [x] **Paso 2: verlos dar rojo**

Corre el arnés. Esperado: **el gate 2 falla** — con la ficha aún sin estilo, el nombre hereda el
cuerpo y parte. Anota el número de líneas que sale: **es el defecto que esta fase viene a arreglar y
tienes que haberlo visto**.

- [x] **Paso 3: escribir el bloque CSS**

En `src/themes/themes.css`, antes de `:root[data-theme="caelestia"] .cae-bar`:

```css
/*
  LA FICHA DEL SISTEMA — el dispositivo de «Quien soy» en Caelestia.

  La escena es la salida de `neofetch`: el comando que un escritorio ejecuta
  para decir que maquina es esta. B1 abre con `whoami`, que pregunta quien
  eres; este pregunta que maquina eres.

  La desviacion deliberada: el NOMBRE ocupa el sitio donde neofetch imprime el
  titulo de la distribucion y es lo unico que NO va en monoespaciada. Sin el,
  la convencion de terminal deja todas las lineas pesando igual y la escena no
  tiene un primero.
*/
:root[data-theme="caelestia"] [data-ficha="neofetch"] {
  display: flex;
  flex-direction: column;
  justify-content: center;
  height: 100%;
  padding: 3.25rem 3.5rem;
  font-family: "Martian Mono", ui-monospace, monospace;
  color: var(--cae-on-surface);
}

/* La escena vieja se retira entera bajo Caelestia: la ficha dice todo esto y
   mejor. No se borran del DOM — Vice e Hyprland las siguen usando. */
:root[data-theme="caelestia"] .about-card,
:root[data-theme="caelestia"] .about-stats,
:root[data-theme="caelestia"] .about-track,
:root[data-theme="caelestia"] .about-pairs,
:root[data-theme="caelestia"] .about-body > [data-line],
:root[data-theme="caelestia"] [data-scene="about"] .hero-kick {
  display: none;
}

/* La seccion trae `px-6 py-24` y `min-h-screen` del marcado compartido. Sin
   neutralizarlo, el aire que se mide no es el de la ficha: es el de la
   maquetacion que esta fase viene a sustituir (medido: 96 px de relleno). */
:root[data-theme="caelestia"] [data-scene="about"] {
  padding: 0;
  min-height: 0;
  height: 100%;
  display: block;
}

:root[data-theme="caelestia"] [data-scene="about"] .about-grid,
:root[data-theme="caelestia"] [data-scene="about"] .about-body {
  display: contents;
}

/* La linea de comando se queda: la terminal no desaparece cuando imprime. */
:root[data-theme="caelestia"] .ficha-cmd-linea {
  margin: 0 0 2.1rem;
  width: 100%;
  max-width: 1180px;
  margin-inline: auto;
  font-size: 0.95rem;
  letter-spacing: 0.01em;
  color: var(--cae-on-surface-variant);
}

:root[data-theme="caelestia"] .ficha-cmd-fin {
  margin: 2.1rem 0 0;
}

:root[data-theme="caelestia"] .ficha-prompt {
  color: var(--cae-primary);
}

:root[data-theme="caelestia"] .ficha-cmd {
  font-weight: 400;
}

:root[data-theme="caelestia"] .ficha-cursor {
  font-style: normal;
}

:root[data-theme="caelestia"] .ficha-cuerpo {
  display: grid;
  grid-template-columns: 312px 1fr;
  gap: 4.25rem;
  align-items: center;
  width: 100%;
  max-width: 1180px;
  margin-inline: auto;
}

:root[data-theme="caelestia"] .ficha-arte {
  display: flex;
  justify-content: center;
}

/* El nombre, a `opsz 144`. `opsz` en Fraunces NO es estilo: la fuente trae
   dibujos distintos segun el tamano al que se lea, y `opsz 9` — el del shell —
   ampliado sale romo. Es la leccion de B1. */
:root[data-theme="caelestia"] .ficha-nombre {
  margin: 0 0 0.5rem;
  font-family: "Fraunces", Georgia, serif;
  font-variation-settings: var(--cae-display-axes-cartel);
  font-size: 3.35rem;
  line-height: 0.95;
  letter-spacing: -0.018em;
  white-space: nowrap;
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .ficha-id {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  flex-wrap: wrap;
}

/* La cabecera del comando es el correo, y es pulsable: la via de contacto
   principal y la unica parada de tabulador legitima de la escena. */
:root[data-theme="caelestia"] .ficha-host {
  font-size: 0.95rem;
  letter-spacing: 0.02em;
  color: var(--cae-primary);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.18s ease;
}

:root[data-theme="caelestia"] .ficha-host:hover {
  border-bottom-color: var(--cae-primary);
}

:root[data-theme="caelestia"] .ficha-host:focus-visible {
  outline: 2px solid var(--cae-anchor);
  outline-offset: 3px;
  border-radius: 2px;
}

/* La disponibilidad se dice como la dice el sistema: punto de azufre y texto,
   igual que `.cae-avail` / `.cae-dot` en la barra. Una pastilla rellena es un
   dialecto distinto para la misma frase, y le pelea el primer plano al nombre.
   Lo que la hace segunda parada de lectura es el SITIO, no el color. */
:root[data-theme="caelestia"] .ficha-estado {
  display: inline-flex;
  align-items: center;
  gap: 0.42rem;
  padding-left: 0.9rem;
  margin-left: 0.15rem;
  border-left: 1px solid var(--cae-outline);
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  white-space: nowrap;
  color: var(--cae-on-surface-variant);
  transition: color 0.2s ease;
}

:root[data-theme="caelestia"] .ficha-estado:hover {
  color: var(--cae-on-surface);
}

/* El ancla no gira con la hora: una senal de estado tiene que decir lo mismo a
   las 09:00 y a las 03:00. */
:root[data-theme="caelestia"] .ficha-punto {
  display: block;
  flex: none;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: var(--cae-anchor);
  animation: ficha-latir 2.4s ease-in-out infinite;
}

@keyframes ficha-latir {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

/* El ancho lo pone `caelestia.ficha.ts` midiendo el texto del correo con
   `Range`: neofetch imprime el filete del largo EXACTO de usuario@host. */
:root[data-theme="caelestia"] .ficha-regla {
  width: 0;
  height: 1px;
  margin: 0.7rem 0 1.2rem;
  background: var(--cae-outline);
}

/* La unica frase humana del contenido, y lo unico en la fuente de texto: entre
   el nombre en Fraunces y los campos en monoespaciada, marca que esto lo dice
   una persona y no el sistema. */
:root[data-theme="caelestia"] .ficha-frase {
  margin: 0 0 1.45rem;
  max-width: 44rem;
  font-family: "Hanken Grotesk", system-ui, sans-serif;
  font-size: 1.06rem;
  line-height: 1.5;
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .ficha-filas {
  display: grid;
  gap: 0.62rem;
  margin: 0;
}

:root[data-theme="caelestia"] .ficha-fila {
  display: grid;
  grid-template-columns: 148px 1fr;
  gap: 1.1rem;
  padding: 0.2rem 0.55rem;
  margin-left: -0.55rem;
  border-radius: 0.4rem;
  font-size: 0.92rem;
  line-height: 1.45;
  transition: background 0.18s ease;
}

:root[data-theme="caelestia"] .ficha-k {
  position: relative;
  font-weight: 600;
  color: var(--cae-on-surface-variant);
  transition: color 0.16s ease;
}

/* El prompt marca la linea que miras, y ENTRA DESLIZANDO: aparecer de golpe se
   lee como un fallo de pintado. */
:root[data-theme="caelestia"] .ficha-k::before {
  content: ">";
  position: absolute;
  left: -0.9ch;
  opacity: 0;
  transform: translateX(-5px);
  color: var(--cae-anchor);
  transition: opacity 0.14s ease, transform 0.18s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .ficha-fila:hover {
  background: var(--cae-surface);
}

:root[data-theme="caelestia"] .ficha-fila:hover .ficha-k {
  color: var(--cae-anchor);
}

:root[data-theme="caelestia"] .ficha-fila:hover .ficha-k::before {
  opacity: 1;
  transform: translateX(0);
}

/* El valor NO se mueve al roce: lo que responde es la pregunta, no el dato. */
:root[data-theme="caelestia"] .ficha-v {
  margin: 0;
  color: var(--cae-on-surface);
}

:root[data-theme="caelestia"] .ficha-s {
  display: block;
  margin-top: 0.16rem;
  font-size: 0.92em;
  color: var(--cae-on-surface-variant);
}

:root[data-theme="caelestia"] .ficha-s + .ficha-s {
  margin-top: 0.05rem;
}

/* La tira con la que neofetch cierra siempre. Aqui son los tokens de la hora,
   asi que el color lo pone `var()` y se actualiza solo con el reloj. */
:root[data-theme="caelestia"] .ficha-tira {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 1.5rem;
}

:root[data-theme="caelestia"] .ficha-tono {
  display: block;
  width: 38px;
  height: 18px;
  border-radius: 0.3rem;
  border: 1px solid rgb(0 0 0 / 0.09);
  transform-origin: center bottom;
  transition: transform 0.18s cubic-bezier(0.2, 0, 0, 1);
}

:root[data-theme="caelestia"] .ficha-tono:hover {
  transform: scaleY(1.7);
}

:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-surface"] { background: var(--cae-surface); }
:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-surface-container"] { background: var(--cae-surface-container); }
:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-surface-container-high"] { background: var(--cae-surface-container-high); }
:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-primary"] { background: var(--cae-primary); }
:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-primary-container"] { background: var(--cae-primary-container); }
:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-anchor"] { background: var(--cae-anchor); }
:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-wall-1"] { background: var(--cae-wall-1); }
:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-wall-2"] { background: var(--cae-wall-2); }
:root[data-theme="caelestia"] .ficha-tono[data-ficha-tono="--cae-wall-3"] { background: var(--cae-wall-3); }

/* La tira no se explica en reposo: solo habla cuando la rozas. */
:root[data-theme="caelestia"] .ficha-rotulo {
  margin-left: 0.7rem;
  font-size: 0.72rem;
  opacity: 0;
  color: var(--cae-on-surface-variant);
  transition: opacity 0.15s ease;
}

:root[data-theme="caelestia"] .ficha-tira:hover .ficha-rotulo {
  opacity: 1;
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] [data-ficha="neofetch"],
  :root[data-theme="caelestia"] [data-ficha="neofetch"] * {
    transition: none;
  }

  :root[data-theme="caelestia"] .ficha-punto {
    animation: none;
  }
}
```

Si `--cae-display-axes-cartel` no existía (ver «Dependencia de B1»), añádelo junto a
`--cae-display-axes`:

```css
  --cae-display-axes-cartel: "opsz" 144, "wght" 900, "SOFT" 0, "WONK" 1;
```

- [x] **Paso 4: verlos dar verde**

Corre el arnés. Esperado: los cuatro `OK`, y el nombre en **1 línea**. Si el alto se dispara por
encima de 748 o el aire de abajo sale negativo, el culpable suele ser `.ficha-cuerpo` sin
`max-width`: compruébalo antes de tocar tamaños de fuente.

- [x] **Paso 5: mirar la captura**

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://localhost:4173/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    pg.wait_for_timeout(3000)
    pg.click('[data-cae-ws="quien-es"]')
    pg.wait_for_timeout(2000)
    r = pg.evaluate("""() => {
        const v = document.querySelector('[data-scene="about"]').closest('main[data-cae-track] > *');
        const b = v.getBoundingClientRect();
        return {x: b.x, y: b.y, width: b.width, height: b.height};
    }""")
    pg.screenshot(path="/tmp/b2-t2.png", clip=r)
    b.close()
EOF
```
Ábrela. Compárala con `docs/superpowers/specs/2026-09-02-caelestia-quien-soy-final.png`.

- [x] **Paso 6: commit**

```bash
git add src/themes/themes.css scripts/measure-caelestia-quien-soy.py
git commit -m "feat(caelestia): la piel de la ficha de Quien soy"
```

---

### Tarea 3: El retrato y su morfado

**Ficheros:**
- Modificar: `src/themes/themes.css` (las dos figuras y el roce del retrato)
- Modificar: `scripts/measure-caelestia-quien-soy.py` (gate 4 del spec)

**Interfaces:**
- Consume: `[data-ficha-retrato]` (el `<span class="ficha-anillo">`) y su `<img class="ficha-foto">`.
- Produce: nada que otras tareas consuman.

- [x] **Paso 1: generar los dos polígonos**

El generador rescatado (`…-figuras.py`) escribe la maqueta entera; para sacar solo los dos
literales que necesita el CSS, usa sus mismas funciones:

```bash
python3 - <<'EOF'
import math
N = 240
def superelipse(pot):
    p = []
    for i in range(N):
        t = i * 2 * math.pi / N
        ct, st = math.cos(t), math.sin(t)
        x = math.copysign(abs(ct) ** (2 / pot), ct)
        y = math.copysign(abs(st) ** (2 / pot), st)
        p.append(f"{50 + 50 * x:.2f}% {50 + 50 * y:.2f}%")
    return "polygon(" + ", ".join(p) + ")"
def armonica(n, a, s):
    rmax = max(1 + a * math.cos(n * t) + s * math.cos(2 * n * t)
               for t in [i * 2 * math.pi / 2000 for i in range(2000)])
    p = []
    for i in range(N):
        t = i * 2 * math.pi / N
        r = (1 + a * math.cos(n * t) + s * math.cos(2 * n * t)) / rmax
        p.append(f"{50 + 50 * r * math.cos(t):.2f}% {50 + 50 * r * math.sin(t):.2f}%")
    return "polygon(" + ", ".join(p) + ")"
print("SQUIRCLE:\n", superelipse(4.0), "\n")
print("COOKIE:\n", armonica(12, -0.058, 0.012))
EOF
```

**Los dos tienen que salir con 240 puntos.** Un `polygon()` solo interpola con otro si cuentan
igual; con distinto número el navegador **no morfa, corta**.

- [x] **Paso 2: escribir el gate que falla**

Añade al arnés:

```python
        print("\n[4] El retrato morfa, no corta")
        pagina.evaluate("""() => {
            window.__morf = [];
            const img = document.querySelector('[data-ficha-retrato] img');
            const tic = () => {
                window.__morf.push(getComputedStyle(img).clipPath);
                if (window.__morf.length < 90) requestAnimationFrame(tic);
            };
            requestAnimationFrame(tic);
        }""")
        # Hover REAL: un MouseEvent sintetico no dispara `:hover`.
        pagina.hover("[data-ficha-retrato]")
        pagina.wait_for_timeout(1400)
        estados = len(set(pagina.evaluate("window.__morf")))
        # Umbral 4 y no 9: un umbral pegado a la medida mide la carga de la
        # maquina, no el diseno. Sin transicion salen exactamente 2.
        comprobar(estados >= 4, f"el clip-path recorre estados intermedios ({estados})")
```

- [x] **Paso 3: verlo dar rojo**

Corre el arnés. Esperado: **2 estados** (solo los extremos), porque aún no hay morfado. Ese 2 es la
prueba de que el gate distingue un corte de un recorrido: anótalo.

- [x] **Paso 4: escribir el CSS del retrato**

Pega los dos polígonos donde dice `POLIGONO_*`:

```css
/*
  EL RETRATO ES EL LOGOTIPO DE LA DISTRIBUCION: ocupa el sitio donde neofetch
  pone el logo de la distro.

  El anillo del roce es un ENVOLTORIO con el mismo recorte, 6 px mayor: un
  `outline` no obedece a un `clip-path` y saldria rectangular.

  Y morfa. Caelestia se define a si misma como «a fluid, morphing shell» y su
  configuracion expone un `deformScale`: morfar es su identidad, asi que al
  rozar el retrato la figura se convierte en OTRA figura con nombre de Material
  3 — squircle -> «12-sided cookie» — en vez de limitarse a encenderse.

  Las dos figuras van a 240 puntos EXACTOS. Con distinto numero de puntos el
  navegador no interpola: corta de golpe. Se generan con
  `docs/superpowers/specs/2026-09-02-caelestia-quien-soy-figuras.py`.
*/
:root[data-theme="caelestia"] .ficha-anillo {
  display: block;
  padding: 6px;
  line-height: 0;
  background: transparent;
  clip-path: POLIGONO_SQUIRCLE;
  transition:
    background 0.5s cubic-bezier(0.2, 0, 0, 1),
    clip-path 0.62s cubic-bezier(0.34, 0.02, 0.16, 1);
}

:root[data-theme="caelestia"] .ficha-foto {
  display: block;
  width: 288px;
  height: 288px;
  object-fit: cover;
  clip-path: POLIGONO_SQUIRCLE;
  transition: clip-path 0.62s cubic-bezier(0.34, 0.02, 0.16, 1);
}

:root[data-theme="caelestia"] .ficha-arte:hover .ficha-anillo {
  background: var(--cae-anchor);
  clip-path: POLIGONO_COOKIE;
}

:root[data-theme="caelestia"] .ficha-arte:hover .ficha-foto {
  clip-path: POLIGONO_COOKIE;
}

@media (prefers-reduced-motion: reduce) {
  :root[data-theme="caelestia"] .ficha-anillo,
  :root[data-theme="caelestia"] .ficha-foto {
    transition: none;
  }
}
```

- [x] **Paso 5: verlo dar verde**

Corre el arnés. Esperado: **≥ 4 estados** (medido en la maqueta: 9).

- [x] **Paso 6: volver a verlo en rojo, a propósito**

Comenta las dos líneas `transition:` del retrato, corre el arnés, confirma que vuelve a **2**, y
descoméntalas. **Un gate que no has visto fallar no vale.**

- [x] **Paso 7: commit**

```bash
git add src/themes/themes.css scripts/measure-caelestia-quien-soy.py
git commit -m "feat(caelestia): el retrato de la ficha morfa entre figuras de Material 3"
```

---

### Tarea 4: El módulo — filete medido, entrada y rótulo de la tira

**Ficheros:**
- Crear: `src/themes/caelestia.ficha.ts`
- Modificar: `src/themes/caelestia.choreography.ts` (invocarlo al activar el workspace)
- Modificar: `scripts/measure-caelestia-quien-soy.py` (gates 3 y 6 del spec)

**Interfaces:**
- Consume: `[data-ficha="neofetch"]` y sus ganchos; el `gsap` del contexto de la coreografía.
- Produce: `export function montarFicha(gsap: Gsap, escena: HTMLElement): FichaHandle | null`
  (devuelve `null` si la ficha no esta en el DOM, que es el caso en Vice y en Hyprland), con
  `interface FichaHandle { destroy: () => void; reproducir: () => void }`.

- [x] **Paso 1: escribir los dos gates que fallan**

```python
        print("\n[3] El filete mide el largo del correo")
        filete = pagina.evaluate("""() => {
            const host = document.querySelector('[data-ficha-host]');
            const regla = document.querySelector('[data-ficha-regla]');
            const rg = document.createRange();
            rg.selectNodeContents(host);
            return {
                texto: Math.round(rg.getBoundingClientRect().width),
                regla: Math.round(regla.getBoundingClientRect().width),
            };
        }""")
        print(f"       texto {filete['texto']} px · filete {filete['regla']} px")
        comprobar(abs(filete["texto"] - filete["regla"]) <= 2,
                  f"el filete mide el largo del texto ({filete['regla']} vs {filete['texto']})")

        print("\n[6] Movimiento reducido: escena montada, sin recorrido")
        contexto = navegador.new_context(viewport={"width": 1440, "height": 900},
                                         reduced_motion="reduce")
        pg2 = contexto.new_page()
        pg2.goto(f"{args.base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        pg2.wait_for_timeout(3000)
        pg2.click('[data-cae-ws="quien-es"]')
        pg2.wait_for_timeout(2000)
        reducido = pg2.evaluate("""() => {
            const cmd = document.querySelector('[data-ficha-cmd]');
            const regla = document.querySelector('[data-ficha-regla]');
            const punto = document.querySelector('.ficha-punto');
            const nombre = document.querySelector('[data-ficha-nombre]');
            return {
                comando: cmd.textContent,
                regla: Math.round(regla.getBoundingClientRect().width),
                latido: getComputedStyle(punto).animationName,
                recorte: getComputedStyle(nombre).clipPath,
            };
        }""")
        comprobar(reducido["comando"] == "neofetch",
                  f"el comando ya esta escrito ({reducido['comando']!r})")
        comprobar(reducido["regla"] > 0, f"el filete ya esta a su ancho ({reducido['regla']})")
        comprobar(reducido["latido"] == "none", f"el punto no late ({reducido['latido']})")
        contexto.close()
```

- [x] **Paso 2: verlos dar rojo**

Corre el arnés. Esperado: el filete mide **0** (el CSS lo deja a cero y nadie lo ha medido todavía) y
el comando sale **vacío**.

- [x] **Paso 3: escribir el módulo**

Crea `src/themes/caelestia.ficha.ts`:

```ts
import type { Gsap } from "./choreography";

/**
 * Lo unico de la ficha de «Quien soy» que el CSS no puede hacer: medir el
 * filete, escribir el comando y ponerle rotulo a la tira de color.
 *
 * Vive aparte de `caelestia.choreography.ts` a proposito: la coreografia
 * gobierna el carril de workspaces y no tiene por que saber que hay dentro de
 * cada ventana. Aqui no se toca el carril.
 *
 * El `gsap` llega SIEMPRE por parametro, desde el contexto de la coreografia.
 * Un `import gsap from "gsap"` suelto compila, pasa el linter y revienta en el
 * navegador: le paso a Hyprland y su coreografia no corrio durante semanas.
 */

export interface FichaHandle {
  destroy: () => void;
  reproducir: () => void;
}

const COMANDO = "neofetch";

export function montarFicha(gsap: Gsap, escena: HTMLElement): FichaHandle | null {
  const ficha = escena.querySelector<HTMLElement>('[data-ficha="neofetch"]');
  if (!ficha) return null;

  const comando = ficha.querySelector<HTMLElement>("[data-ficha-cmd]");
  const cursor = ficha.querySelector<HTMLElement>("[data-ficha-cursor]");
  const cursorFinal = ficha.querySelector<HTMLElement>("[data-ficha-prompt]");
  const host = ficha.querySelector<HTMLElement>("[data-ficha-host]");
  const regla = ficha.querySelector<HTMLElement>("[data-ficha-regla]");
  const nombre = ficha.querySelector<HTMLElement>("[data-ficha-nombre]");
  const rotulo = ficha.querySelector<HTMLElement>(".ficha-rotulo");
  const grupos = Array.from(ficha.querySelectorAll<HTMLElement>("[data-ficha-grupo]"));
  const filas = Array.from(ficha.querySelectorAll<HTMLElement>("[data-ficha-fila]"));
  const tonos = Array.from(ficha.querySelectorAll<HTMLElement>("[data-ficha-tono]"));

  if (!comando || !cursor || !cursorFinal || !host || !regla || !nombre) return null;

  const limpiadores: (() => void)[] = [];
  // Los tipos salen del propio `gsap` que llega por parametro: escribir
  // `gsap.core.Timeline` aqui referencia el ESPACIO DE NOMBRES global y choca
  // con el parametro, que es un valor con el mismo nombre.
  let linea: ReturnType<Gsap["timeline"]> | null = null;
  let latido: ReturnType<Gsap["fromTo"]> | null = null;

  /*
   * El filete del largo EXACTO del correo, como hace neofetch con
   * `usuario@host`. Se mide con Range: la caja del <a> devolveria el ancho del
   * contenedor, no el del texto. Es la trampa que B1 ya pago con su
   * justificacion.
   */
  const anchoDelTexto = (): number => {
    const rango = document.createRange();
    rango.selectNodeContents(host);
    return rango.getBoundingClientRect().width;
  };

  // La tira dice que token es y cuanto vale a esta hora. Solo al rozarla.
  for (const tono of tonos) {
    const alEntrar = (): void => {
      if (!rotulo) return;
      const token = tono.dataset.fichaTono ?? "";
      const valor = getComputedStyle(document.documentElement).getPropertyValue(token).trim();
      rotulo.textContent = `${token}  ${valor}`;
    };
    tono.addEventListener("mouseenter", alEntrar);
    limpiadores.push(() => tono.removeEventListener("mouseenter", alEntrar));
  }

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const reproducir = (): void => {
    if (linea) linea.kill();
    if (latido) latido.kill();
    const ancho = anchoDelTexto();

    if (reduce) {
      // Escena montada, sin recorrido. La regla del repo.
      gsap.set(grupos, { opacity: 1, x: 0, scale: 1, clearProps: "transform" });
      gsap.set([...filas, ...tonos], { opacity: 1, x: 0, scaleX: 1, clearProps: "transform" });
      gsap.set(nombre, { clipPath: "inset(0 0% 0 0)" });
      comando.textContent = COMANDO;
      cursor.style.opacity = "0";
      regla.style.width = `${ancho}px`;
      return;
    }

    const cuenta = { i: 0 };
    // fromTo con los dos extremos escritos a mano: `gsap.from` esta prohibido.
    const tl = gsap.timeline({
      onComplete: () => {
        latido = gsap.fromTo(
          cursorFinal,
          { opacity: 1 },
          { opacity: 0, duration: 0.55, repeat: -1, yoyo: true, ease: "none" },
        );
      },
    });
    gsap.set(nombre, { clipPath: "inset(0 100% 0 0)" });
    gsap.set(grupos, { opacity: 0 });
    gsap.set(filas, { opacity: 0, x: -6 });
    gsap.set(tonos, { opacity: 0, scaleX: 0.2 });
    regla.style.width = "0px";
    comando.textContent = "";

    tl.fromTo(cursor, { opacity: 1 },
      { opacity: 0, duration: 0.085, repeat: 3, yoyo: true, ease: "none" }, 0);
    tl.to(cuenta, {
      i: COMANDO.length, duration: 0.44, ease: "none",
      onUpdate: () => { comando.textContent = COMANDO.slice(0, Math.round(cuenta.i)); },
    }, 0.34);
    tl.fromTo(cursor, { opacity: 1 },
      { opacity: 0.2, duration: 0.04, yoyo: true, repeat: 1, ease: "power1.inOut" }, 0.78);
    tl.fromTo(grupos[0] ?? ficha, { opacity: 0, scale: 1.06 },
      { opacity: 1, scale: 1, duration: 0.55, ease: "power2.out" }, 0.86);
    tl.set(grupos[1] ?? ficha, { opacity: 1 }, 1.05);
    // El barrido de tinta: el mismo gesto que el titular de B1. Es lo que ata
    // las dos escenas.
    tl.fromTo(nombre, { clipPath: "inset(0 100% 0 0)" },
      { clipPath: "inset(0 0% 0 0)", duration: 0.72, ease: "power2.inOut" }, 1.05);
    tl.to(cursor, { opacity: 0, duration: 0.2 }, 1.05);
    tl.fromTo(grupos[2] ?? ficha, { opacity: 0, x: -6 },
      { opacity: 1, x: 0, duration: 0.28, ease: "power2.out" }, 1.45);
    tl.fromTo(regla, { width: 0 },
      { width: ancho, duration: 0.42, ease: "power2.inOut" }, 1.6);
    tl.fromTo(grupos.slice(3), { opacity: 0 },
      { opacity: 1, duration: 0.22, ease: "power2.out" }, 1.85);
    tl.fromTo(filas, { opacity: 0, x: -6 },
      { opacity: 1, x: 0, duration: 0.22, ease: "power2.out", stagger: 0.07 }, 1.85);
    tl.to(tonos, { opacity: 1, scaleX: 1, duration: 0.18, ease: "power2.out", stagger: 0.035 }, 2.45);

    linea = tl;
  };

  /*
   * El filete se remide al redimensionar: el ancho del texto cambia con el
   * tamano de fuente, y un filete congelado en el ancho de otra ventana miente
   * justo sobre lo que viene a decir.
   */
  const alRedimensionar = (): void => {
    if (!linea || !linea.isActive()) regla.style.width = `${anchoDelTexto()}px`;
  };
  window.addEventListener("resize", alRedimensionar);
  limpiadores.push(() => window.removeEventListener("resize", alRedimensionar));

  return {
    reproducir,
    destroy: () => {
      if (linea) linea.kill();
      if (latido) latido.kill();
      for (const limpiar of limpiadores) limpiar();
    },
  };
}
```

- [x] **Paso 4: engancharlo a la coreografía**

En `src/themes/caelestia.choreography.ts`, importa el módulo y llama a `reproducir()` cuando la
escena que contiene la ficha se activa. Dentro de `caelestiaChoreography`, después de
`aislarInactivos(0)`:

```ts
  /*
   * La ficha de «Quien soy» se lanza cuando SU workspace se activa, no al
   * cargar: es una aplicacion arrancando, y arranca cuando la abres. Se monta
   * una sola vez; `reproducir()` es lo que se repite.
   */
  const escenaFicha = escenas.find((escena) => escena.querySelector('[data-ficha="neofetch"]'));
  const ficha = escenaFicha ? montarFicha(gsap, escenaFicha) : null;
  const indiceFicha = escenaFicha ? escenas.indexOf(escenaFicha) : -1;
```

Y dentro de `irA`, justo después de `aislarInactivos(destino)`:

```ts
    if (ficha && destino === indiceFicha) ficha.reproducir();
```

Con el import arriba:

```ts
import { montarFicha } from "./caelestia.ficha";
```

- [x] **Paso 5: verlos dar verde**

```bash
npm run build && npm run lint
npx vite preview --port 4173 &
sleep 2
python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4173
```
Esperado: gates 3 y 6 en verde. **Ábrelo también en un navegador de verdad**: el `gsap` mal
destructurado compila, pasa el linter y solo revienta en la consola del navegador.

- [x] **Paso 6: commit**

```bash
git add src/themes/caelestia.ficha.ts src/themes/caelestia.choreography.ts scripts/measure-caelestia-quien-soy.py
git commit -m "feat(caelestia): la entrada de la ficha y el filete medido con Range"
```

---

### Tarea 5: Los gates que faltan — anti-mock, contraste y ejes del shell

**Ficheros:**
- Modificar: `scripts/measure-caelestia-quien-soy.py` (gates 5, 7 y 8)

**Interfaces:**
- Consume: la escena ya montada de las tareas 1–4.
- Produce: el arnés completo, con los ocho gates del spec.

- [x] **Paso 1: escribir los tres gates**

```python
        print("\n[7] Anti-mock: todo texto visible existe en content.ts")
        import pathlib
        fuente = pathlib.Path("src/data/content.ts").read_text(encoding="utf-8")
        textos = pagina.evaluate("""() => {
            const ficha = document.querySelector('[data-ficha="neofetch"]');
            const nodos = ficha.querySelectorAll(
                '[data-ficha-nombre], [data-ficha-host], .ficha-estado, [data-ficha-frase], .ficha-v, .ficha-s');
            return Array.from(nodos)
                .map((n) => (n.firstChild && n.firstChild.nodeType === 3
                    ? n.firstChild.textContent : n.textContent).trim())
                .filter((t) => t.length > 0);
        }""")
        # Los valores compuestos («rol · organizacion») se parten por el separador:
        # cada mitad tiene que existir literal en content.ts. El separador se
        # parte con expresion regular y NO con la cadena " · ": la fila de
        # enfoque une sus dos titulos con dos espacios a cada lado, asi que un
        # split por la cadena exacta la dejaria entera y daria un fallo falso.
        import re
        piezas: list[str] = []
        for texto in textos:
            piezas.extend(p.strip() for p in re.split(r"\s+·\s+", texto) if p.strip())
        huerfanos = [p for p in piezas if p not in fuente and not p.startswith("Desde ")]
        comprobar(not huerfanos, f"todo texto sale de content.ts (huerfanos: {huerfanos})")

        print("\n[8] Los ejes del shell no se han movido")
        ejes = pagina.evaluate("""() => ({
            marca: getComputedStyle(document.querySelector('.cae-mark')).fontVariationSettings,
            nombre: getComputedStyle(document.querySelector('[data-ficha-nombre]')).fontVariationSettings,
        })""")
        comprobar('"opsz" 9' in ejes["marca"], f"la marca de la barra sigue en opsz 9 ({ejes['marca']})")
        comprobar('"opsz" 144' in ejes["nombre"], f"el nombre usa opsz 144 ({ejes['nombre']})")

        print("\n[5] Contraste de los pares que se pintan, en los dos esquemas")
        # NO se inventa una API para forzar la hora. El motor de color lee el
        # reloj del sistema, asi que el esquema se cambia con la ZONA HORARIA
        # del contexto de Playwright, que es real y no toca el codigo.
        #
        # Dos muestras bastan, y no es un atajo: la fase A dejo demostrado que
        # la claridad de cada rol NO se mueve con el matiz, asi que dentro de un
        # esquema el contraste es invariante a la hora. Lo que cambia el
        # contraste es el ESQUEMA, y esquemas hay dos.
        PARES = [
            ("[data-ficha-nombre]", "el nombre"),
            ("[data-ficha-host]", "el correo"),
            (".ficha-estado", "la disponibilidad"),
            ("[data-ficha-frase]", "la frase"),
            (".ficha-k", "las claves"),
            (".ficha-v", "los valores"),
            (".ficha-s", "los detalles"),
        ]
        CONTRASTE_JS = """(sel) => {
            const el = document.querySelector(sel);
            if (!el) return null;
            const lum = (c) => {
                const [r, g, b] = c.match(/[\\d.]+/g).slice(0, 3).map(Number);
                const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
                return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
            };
            // El fondo REAL: se sube por los ancestros hasta el primero que
            // pinte algo. Comparar contra el rol teorico es como se colo que el
            // reloj de la barra estuviera bajo AA cuatro horas al dia.
            let nodo = el, fondo = null;
            while (nodo && fondo === null) {
                const bg = getComputedStyle(nodo).backgroundColor;
                if (bg && bg !== "rgba(0, 0, 0, 0)") fondo = bg;
                nodo = nodo.parentElement;
            }
            const a = lum(getComputedStyle(el).color);
            const b = lum(fondo || "rgb(255,255,255)");
            return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
        }"""

        peor, peor_etiqueta = 21.0, ""
        # Kiritimati (UTC+14) y Honolulu (UTC-10) caen en extremos opuestos del
        # dia a la vez: pase lo que pase, uno de los dos esta fuera de 07:00-20:00.
        for zona in ("Pacific/Kiritimati", "Pacific/Honolulu"):
            ctx = navegador.new_context(viewport={"width": 1440, "height": 900}, timezone_id=zona)
            pg3 = ctx.new_page()
            pg3.goto(f"{args.base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
            pg3.wait_for_timeout(3000)
            pg3.click('[data-cae-ws="quien-es"]')
            pg3.wait_for_timeout(2000)
            esquema = pg3.evaluate("() => document.documentElement.dataset.caeEsquema")
            for selector, etiqueta in PARES:
                ratio = pg3.evaluate(CONTRASTE_JS, selector)
                if ratio is not None and ratio < peor:
                    peor, peor_etiqueta = ratio, f"{etiqueta} en esquema {esquema}"
            print(f"       {zona}: esquema {esquema}")
            ctx.close()
        print(f"       peor par: {peor:.2f}:1 ({peor_etiqueta})")
        comprobar(peor >= 4.5, f"contraste >= 4.5:1 en los dos esquemas ({peor:.2f}:1, {peor_etiqueta})")
```

> **Comprueba que has visto los dos esquemas.** Si las dos zonas horarias imprimen el mismo
> `esquema`, el gate está midiendo dos veces lo mismo y no vale: cambia una zona hasta que salgan
> `dia` y `noche`. Un barrido que no cruza el umbral es exactamente el fallo que la fase A pagó con
> un reloj congelado.


- [x] **Paso 2: correrlos y arreglar lo que salga**

Si el gate 7 saca huérfanos, **la respuesta no es relajar el gate**: es quitar de la ficha el texto
que no está en `content.ts`.

- [x] **Paso 3: verlo dar rojo a propósito**

Cambia en `about.ts` un texto de la ficha por una cadena inventada («Repositorios públicos · 2», que
es el fallo real que cometió B1), corre el arnés, confirma que el gate 7 lo caza, y deshaz el cambio.

- [x] **Paso 4: commit**

```bash
git add scripts/measure-caelestia-quien-soy.py
git commit -m "test(caelestia): los ocho gates de la ficha de Quien soy"
```

---

### Tarea 6: Cierre — los tres temas, el arnés general y el estado del spec

**Ficheros:**
- Modificar: `docs/superpowers/specs/2026-09-02-caelestia-quien-soy-design.md` (`Estado:`)
- Modificar: `.claude/CLAUDE.md` y `CLAUDE.md` (estado de los temas)

- [x] **Paso 1: build y linter**

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run build && npm run lint
```

- [x] **Paso 2: el arnés completo, en verde**

```bash
npx vite preview --port 4173 &
sleep 2
python3 scripts/measure-caelestia-quien-soy.py --base http://localhost:4173
```
Los ocho gates en verde y salida 0.

- [x] **Paso 3: el arnés del shell, sin regresiones**

```bash
python3 scripts/measure-caelestia-hora.py --base http://localhost:4173
```
Sus 16 aserciones siguen verdes: esta fase no debe haber tocado el shell.

- [x] **Paso 4: la línea base general**

```bash
python3 scripts/verify.py
```
Sale 0 si coincide con `scripts/verify-baseline.json`. Si arreglaste algo que estaba en la base,
`python3 scripts/verify.py --update-baseline` y **revisa el diff antes de commitear**.

- [x] **Paso 5: capturas de los tres temas, y mirarlas**

```bash
python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
    for tema in ("vice", "hyprland", "caelestia"):
        for ancho, alto, nombre in ((1440, 900, "desktop"), (390, 844, "movil")):
            pg = b.new_page(viewport={"width": ancho, "height": alto})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.goto(f"http://localhost:4173/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(8000)
            pg.screenshot(path=f"/tmp/b2-cierre-{tema}-{nombre}.png", full_page=True)
            print(tema, nombre, "errores:", errs)
            assert not errs, (tema, nombre, errs)
            pg.close()
    b.close()
EOF
```
**Ábrelas las seis.** Vice e Hyprland tienen que estar exactamente como antes.

- [x] **Paso 6: cerrar el estado**

En el spec, `Estado: pendiente de plan` → `Estado: implementado`. Y en los dos `CLAUDE.md`, añade B2
al estado de los temas, con el mismo tono que las entradas de Vice y del shell: qué es, qué lo
vigila, y la trampa que no hay que repetir (las figuras a 240 puntos y el filete medido con `Range`).

- [x] **Paso 7: commit**

```bash
git add -A
git commit -m "docs(caelestia): B2 implementada — Quien soy es la salida de neofetch"
```

---

## Traspaso

**Modelo y esfuerzo recomendados por tarea:**

| tarea | modelo | por qué |
|---|---|---|
| 1 · DOM | **Sonnet** | mecánica: construir nodos siguiendo un patrón que ya existe dos veces en el fichero |
| 2 · CSS | **Sonnet** | el bloque está escrito entero en el plan; el juicio ya está tomado |
| 3 · retrato | **Sonnet** | pegar dos polígonos generados y cuatro reglas |
| 4 · módulo | **modelo top** | es donde se rompen las cosas: `gsap` del contexto, orden de la línea de tiempo, ciclo de vida del handle, y el enganche con el carril |
| 5 · gates | **modelo top** | escribir un gate es fácil; escribir uno que no mienta, no. Aquí está la nota del barrido de contraste, que exige criterio |
| 6 · cierre | **Sonnet** | correr, mirar y anotar |

**Antes de empezar:** confirma si B1 ya aterrizó (`git log --oneline -- src/sections/hero.ts`). Las
dos fases solo comparten `--cae-display-axes-cartel`; `about.ts` y `hero.ts` son ficheros distintos y
no se estorban.

**El worktree de diseño de esta fase** es `/home/aoshi/proyectos/portfolio-aoshi-b2`, rama
`design/caelestia-quien-soy`, y ahí están el spec y la maqueta viva. La implementación puede correr
en ese mismo worktree o en uno nuevo desde `main`.
