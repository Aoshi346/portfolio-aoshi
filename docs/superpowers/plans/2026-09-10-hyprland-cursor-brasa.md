# La brasa — plan de implementacion

> **Para agentes:** SUB-SKILL OBLIGATORIA: usa `superpowers:subagent-driven-development` para
> ejecutar este plan tarea a tarea. Los pasos van con casillas (`- [ ]`) para poder marcarlos.

**Objetivo:** que el cursor de Hyprland deje de encerrar cada pulsable en un rectangulo naranja,
sustituyendo el canto por un tramo corto de la arista inferior que sigue a la mano, y emplumando el
recorte a canto vivo del charco.

**Arquitectura:** todo el cambio vive en la funcion `tick()` de `src/components/hyprCursor.ts`, que
ya pinta en dos lienzos: `hueco` (`z-index: -4`, debajo del contenido) lleva el charco y `canvas`
(`z-index: 70`, encima) lleva la mano y la senal. La brasa sustituye al `strokeRect` en el lienzo de
arriba; la pluma se anade al charco en el de abajo, borrando hacia dentro con
`globalCompositeOperation = "destination-out"`. No entra ningun modulo nuevo, ninguna dependencia y
ninguna regla de CSS.

**Stack:** TypeScript estricto, Canvas 2D crudo (sin GSAP en este modulo), Playwright + Pillow para
el arnes.

**Spec:** `docs/superpowers/specs/2026-09-10-hyprland-cursor-brasa-design.md` — leelo entero antes
de empezar. Este plan argumenta desde el, y las dos revocaciones que hace sobre
`2026-08-19-hyprland-cursor-luz-design.md` estan justificadas alli, no aqui.

## Restricciones globales

Copiadas del spec y de `CLAUDE.md`. Valen para TODAS las tareas:

- **Ficheros que puedes tocar:** `src/components/hyprCursor.ts`,
  `scripts/measure-cursor-luz.py`, y en la tarea 4 tambien
  `docs/superpowers/specs/2026-09-10-hyprland-cursor-brasa-design.md`,
  `docs/superpowers/plans/2026-09-10-hyprland-cursor-brasa.md` y
  `/home/aoshi/proyectos/portfolio-aoshi/.claude/rules/verification.md`.
- **Ficheros PROHIBIDOS**, sin excepcion: `src/backgrounds/shaderBackground.ts`,
  `src/themes/themes.css`, `src/themes/*.choreography.ts`, cualquier cosa bajo `src/sections/`,
  `src/data/content.ts` y `scripts/verify.py`. Si crees que necesitas tocar uno, PARA y dilo en tu
  informe en vez de tocarlo.
- **Nunca `any`** (`strict` esta activo; usa `unknown` + guardas).
- **Nunca `gsap.from`** — este modulo no usa GSAP en absoluto; no lo introduzcas.
- **Nunca `console.log`** en codigo de produccion.
- **Cero emojis** en codigo, comentarios, commits e informes.
- **Las guardias de `prefers-reduced-motion` y la limpieza de `destroy()` quedan intactas.**
- **Node 22 en cada shell:** `export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"`.
- **Se verifica contra el build de produccion servido, NUNCA `npm run dev`** (el HMR corrompe las
  medidas y miente en los dos sentidos). Hay un preview del worktree en
  `http://127.0.0.1:4214`; si no responde, levanta uno con `npx vite preview --port 4214` y
  **matalo por PID**, nunca con `pkill -f "vite preview"` (el patron casa con la linea de comando
  del propio bucle que espera).
- **El tema se sortea por visita:** toda URL de verificacion lleva `?theme=hyprland`.
- **Oyente de consola enganchado ANTES de navegar** en cualquier pagina que abras. El aviso
  `GPU stall due to ReadPixels` lo provoca `page.screenshot()` y no es un error de la pagina.
- **Ningun gate se da por bueno sin haberlo visto dar rojo** contra el fallo que dice cazar. En este
  plan no hace falta sabotear nada: el codigo actual ES el fallo, asi que el rojo se toma contra
  `main` antes de implementar.
- **No termines tu turno con un proceso tuyo corriendo en segundo plano.** Espera por PID. Y no
  uses `timeout 170`/`280` con estos arneses: los corta a media corrida y el resultado parece un
  fallo del instrumento.

---

## Estructura de ficheros

| Fichero | Responsabilidad | Tareas |
|---|---|---|
| `src/components/hyprCursor.ts` | El dispositivo. Constantes nuevas arriba, brasa y pluma dentro de `tick()`. | 1, 2 |
| `scripts/measure-cursor-luz.py` | Las tres familias nuevas + el docstring que declara el rojo esperado. | 1, 2, 3, 4 |
| El spec y este plan | Registro de implementacion y estado. | 4 |

---

## Tarea 1: La brasa

**Ficheros:**
- Modificar: `src/components/hyprCursor.ts` (constantes junto a `PUNTO_REPOSO`, y el bloque del
  canto, hoy lineas 426-431)
- Modificar: `scripts/measure-cursor-luz.py` (dos familias nuevas)

**Interfaces:**
- Consume: `pointerX`, `rect`, `pot`, `radio` y `ctx`, todos ya existentes dentro de `tick()`.
- Produce: las constantes `BRASA_ANCHO_FACTOR` y `BRASA_GROSOR`, y en el arnes las funciones
  `_pixeles_encendidos(pg, caja, selector, punto=None)`, `gate_brasa(pg, fallos)` y
  `gate_brasa_sigue(pg, fallos)`. La tarea 2 reutiliza `_pixeles_encendidos`.

- [x] **Paso 1: leer el terreno**

Lee `src/components/hyprCursor.ts` entero (511 lineas) antes de tocar nada. Fijate en la cabecera
del modulo: prohibe dibujar ni un caracter ni un numero fuera de la diana, y explica por que hay dos
lienzos. Lee tambien las lineas 245-380 de `scripts/measure-cursor-luz.py`: ahi estan los ayudantes
`abrir()`, `apuntar()`, `esperar_pot_asentada()`, `_lin()` y `_lum()`, que vas a reutilizar en vez
de reescribir.

- [x] **Paso 2: escribir las dos familias nuevas del arnes**

Anadelas a `scripts/measure-cursor-luz.py`. La diana es `.obra-abrir` (1440x108 a 1440x900): es la
unica lo bastante ancha para que "encierra" y "no encierra" se distingan, y el arnes ya la usa en
la asercion 3, asi que su forma de alcanzarla esta resuelta.

La medida es PAREADA, como el gate de contraste que ya existe: se captura la caja de la diana con el
puntero encima y con el puntero lejos, y se compara pixel a pixel. Sin parear, el fondo generativo
—que se mueve solo— decide el resultado.

```python
# --- Familias 8 y 9: la senal del pulsable no encierra la diana -------------
#
# Nacen de un fallo real: hasta el 2026-09-10 el cursor pintaba
# `ctx.strokeRect` sobre la caja ENTERA de cada pulsable, y este arnes estuvo
# semanas en verde con un rectangulo naranja rodeando cada enlace de la
# pagina. Vigilaba el charco por familias y NUNCA miro la senal. Un gate que
# no mira la pieza que el visitante ve no vigila nada.

# Un pixel esta "encendido" si la diferencia contra la captura sin puntero es
# a la vez FUERTE y NARANJA. Solo por magnitud no vale: el fondo generativo se
# mueve entre las dos capturas y produce diferencias de varias unidades en
# todo el encuadre.
ENCENDIDO_DELTA_R = 30
ENCENDIDO_SESGO = 15


def _pixeles_encendidos(pg, caja: dict, selector: str, punto=None):
    """Devuelve (ancho, alto, set de (x, y) encendidos) dentro de la caja.

    Captura con el puntero sobre `selector` y con el puntero lejos, y se queda
    con los pixeles cuya diferencia es fuerte y naranja (`--l1` es 255 90 52:
    sube mucho el rojo y casi nada el azul). La mano no cuenta como encendida:
    es `--catch` (255 217 204), que sube el azul tanto como el rojo.
    """
    from PIL import Image
    import io

    clip = {"x": caja["x"], "y": caja["y"], "width": caja["width"], "height": caja["height"]}

    pg.mouse.move(4, 4)
    pg.wait_for_timeout(900)
    apagado = Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")

    apuntar(pg, selector, punto)
    esperar_pot_asentada(pg)
    encendido = Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB")

    w, h = encendido.size
    a, e = apagado.load(), encendido.load()
    vivos = set()
    for y in range(h):
        for x in range(w):
            dr = e[x, y][0] - a[x, y][0]
            db = e[x, y][2] - a[x, y][2]
            if dr >= ENCENDIDO_DELTA_R and (dr - db) >= ENCENDIDO_SESGO:
                vivos.add((x, y))
    return w, h, vivos


def gate_brasa(pg, fallos: list) -> None:
    """Familia 8: la senal no encierra la diana."""
    caja = pg.locator(PULSABLE_SCROLL).first.bounding_box()
    w, h, vivos = _pixeles_encendidos(pg, caja, PULSABLE_SCROLL)

    banda = 3  # px de tolerancia por arista: el antialias del trazo
    for nombre, conjunto in (
        ("SUPERIOR", {p for p in vivos if p[1] < banda}),
        ("IZQUIERDA", {p for p in vivos if p[0] < banda}),
        ("DERECHA", {p for p in vivos if p[0] >= w - banda}),
    ):
        if conjunto:
            fallos.append(
                f"la senal enciende la arista {nombre} de {PULSABLE_SCROLL}: "
                f"{len(conjunto)} px encendidos, esperado 0"
            )

    abajo = {p for p in vivos if p[1] >= h - banda}
    if not abajo:
        fallos.append(f"la senal no enciende nada en la arista INFERIOR de {PULSABLE_SCROLL}")
        return

    xs = sorted({p[0] for p in abajo})
    tramo = xs[-1] - xs[0] + 1
    if tramo >= w * 0.6:
        fallos.append(
            f"el tramo encendido de {PULSABLE_SCROLL} ocupa {tramo} px sobre {w} "
            f"({tramo / w:.0%}), esperado por debajo del 60%"
        )


def gate_brasa_sigue(pg, fallos: list) -> None:
    """Familia 9: el tramo encendido se mueve con la mano y en su mismo sentido."""
    caja = pg.locator(PULSABLE_SCROLL).first.bounding_box()
    centros = []
    for frac in (0.25, 0.75):
        punto = (caja["x"] + caja["width"] * frac, caja["y"] + caja["height"] / 2)
        _, h, vivos = _pixeles_encendidos(pg, caja, PULSABLE_SCROLL, punto)
        abajo = [p[0] for p in vivos if p[1] >= h - 3]
        if not abajo:
            fallos.append(
                f"no hay tramo encendido con la mano al {int(frac * 100)}% de {PULSABLE_SCROLL}"
            )
            return
        centros.append(sum(abajo) / len(abajo))

    desplazamiento = centros[1] - centros[0]
    minimo = caja["width"] * 0.2
    if desplazamiento <= minimo:
        fallos.append(
            f"el tramo no sigue a la mano en {PULSABLE_SCROLL}: su centro se mueve "
            f"{desplazamiento:.0f} px al pasar el raton del 25% al 75% del ancho "
            f"(minimo exigido {minimo:.0f} px)"
        )
```

Engancha las dos familias en `main()`, junto a las que ya existen, sobre la misma pagina de
Hyprland a 1440x900 que usa la asercion 3, pasandoles la lista `fallos` que `main()` ya mantiene:
**este arnes no tiene ningun `check()`**, acumula cadenas en `fallos` y al final las imprime con
prefijo `FALLO:`. Sigue ese patron y no introduzcas otro.

`PULSABLE_SCROLL` ya vale `".obra-abrir"` en el arnes y su docstring explica por que `apuntar()`
necesita punto explicito con esa diana: es `position: absolute; inset: 0` sobre la fila entera.

- [x] **Paso 3: verlas dar ROJO contra el codigo actual**

Sin tocar todavia `hyprCursor.ts`:

```bash
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
cd /home/aoshi/proyectos/portfolio-aoshi-hypr
npm run build && python3 scripts/measure-cursor-luz.py --base http://127.0.0.1:4214
```

Esperado: la familia 8 falla en las tres aristas (arriba, izquierda y derecha estan encendidas
porque hoy hay un rectangulo completo) Y en el tramo (hoy ocupa el 100% del ancho). La familia 9
falla porque el centro no se mueve: el filete es identico se ponga el raton donde se ponga. Ademas
sigue el fallo esperado de siempre, el de la diana ocluida.

**Pega la salida literal de esos fallos en tu informe.** Un gate que no has visto en rojo no vale.

- [x] **Paso 4: implementar la brasa**

Anade las constantes junto a las de la mano (`PUNTO_REPOSO` / `PUNTO_PULSADO`):

```ts
/*
 * La brasa que sustituye al canto (spec 2026-09-10). El ancho NO es un numero
 * suelto: sale del mismo `radio` que ya calcula el charco, que a su vez lo
 * dicta la altura del elemento y no la seccion. Asi una fila de obra de 108px
 * y un nombre de Stack de 34 reciben la misma ley.
 *
 * Va acotado a la caja de la diana, y esa cota tiene consecuencia de diseno:
 * en una diana mas estrecha que el tramo la brasa cubre la arista entera, que
 * es exactamente la opcion A que se descarto por si sola. B contiene a A sin
 * que nadie programe el caso.
 */
const BRASA_ANCHO_FACTOR = 0.75;
// 2px en `--l1`: es la linea de brasa que los cimientos estrenaron como suelo
// de la escena Stack. La senal del cursor habla la gramatica que el tema ya
// tiene en vez de anadir una forma propia.
const BRASA_GROSOR = 2;
```

Y sustituye el bloque del canto (hoy lineas 426-431, el comentario incluido) por:

```ts
      // La brasa: un tramo de la arista inferior, centrado en la mano y
      // acotado a la caja. Sustituye al filete de la caja ENTERA, que se leia
      // como campo de formulario sobre texto y, sobre una diana de 1440px de
      // ancho, como una caja que cruza la pantalla — y que ademas era
      // indistinguible del anillo de foco de teclado, que es un `outline` de
      // 2px en el mismo `--l1`. Se queda en el lienzo de ARRIBA: es senal, no
      // relleno, y necesita ir por encima del contenido.
      const anchoBrasa = Math.min(radio * BRASA_ANCHO_FACTOR, rect.width);
      const centroBrasa = Math.min(
        Math.max(pointerX, rect.left + anchoBrasa / 2),
        rect.right - anchoBrasa / 2,
      );
      const brasaX = centroBrasa - anchoBrasa / 2;
      // Extremos difuminados a cero: sin esto es una barra recortada, que es
      // otra vez una forma con cantos duros.
      const brasa = ctx.createLinearGradient(brasaX, 0, brasaX + anchoBrasa, 0);
      const brasaAlfa = (0.85 * pot).toFixed(3);
      brasa.addColorStop(0, "rgb(255 90 52 / 0)");
      brasa.addColorStop(0.5, `rgb(255 90 52 / ${brasaAlfa})`);
      brasa.addColorStop(1, "rgb(255 90 52 / 0)");
      ctx.fillStyle = brasa;
      ctx.fillRect(brasaX, rect.bottom - BRASA_GROSOR, anchoBrasa, BRASA_GROSOR);
```

- [x] **Paso 5: verlas en VERDE**

```bash
npm run build && npm run lint
python3 scripts/measure-cursor-luz.py --base http://127.0.0.1:4214
```

Esperado: las familias 8 y 9 pasan. El recuento total de fallos vuelve a ser **exactamente 1** (el
de la diana ocluida). Cualquier otro numero es un fallo nuevo.

- [x] **Paso 6: mirar una captura de verdad**

Con el build servido y un oyente de consola puesto antes de navegar, captura la brasa sobre las tres
dianas a 1440x900: `.hero-mail`, `[data-cimientos] .cim-nombre` y `.obra-abrir`. Deja las capturas
en `/tmp/brasa-t1/` y **miralas tu**. Comprueba: no hay linea en las otras tres aristas; sobre
`.obra-abrir` la luz esta cerca de la mano y no cruza la pantalla; sobre `.cim-nombre` la brasa no
invade la caja del nombre vecino.

- [x] **Paso 7: commit**

```bash
git add src/components/hyprCursor.ts scripts/measure-cursor-luz.py
git commit -m "feat(cursor): la brasa sustituye al canto de la caja entera"
```

---

## Tarea 2: La pluma del charco

**Ficheros:**
- Modificar: `src/components/hyprCursor.ts` (constante nueva, y el bloque del lienzo dentro de
  `tick()`, hoy lineas 407-423)
- Modificar: `scripts/measure-cursor-luz.py` (una familia nueva)

**Interfaces:**
- Consume: `huecoCtx`, `rect`, `pot`, `iluminar`, `radio`, todos ya existentes.
- Produce: la constante `PLUMA`, el umbral `PLUMA_MARGEN` y la funcion `gate_pluma(pg, fallos)`.

- [x] **Paso 1: escribir la familia nueva**

```python
# --- Familia 10: el charco no tiene canto duro ------------------------------
#
# El charco va recortado a la caja de la diana, y eso NO se quita: es lo unico
# que dice hasta donde llega la zona pulsable. Lo que se quita es el CORTE, que
# es lo que se leia como caja. El gate cruza la arista pixel a pixel y exige
# que no haya escalon.
#
# El umbral no es un numero suelto: se calibra contra la MISMA franja con el
# charco apagado. El fondo es generativo y tiene sus propios gradientes, asi
# que un umbral absoluto mediria el shader, no el recorte.
PLUMA_MARGEN = 1.5


def gate_pluma(pg, fallos: list) -> None:
    """Familia 10: el charco muere hacia dentro, sin escalon en la arista."""
    from PIL import Image
    import io

    caja = pg.locator(PULSABLE_SCROLL).first.bounding_box()
    # Franja horizontal que cruza la arista IZQUIERDA: 20px fuera, 20px dentro,
    # a media altura de la diana. Se promedian 8 filas para que el ruido del
    # shader no decida.
    clip = {
        "x": caja["x"] - 20,
        "y": caja["y"] + caja["height"] / 2 - 4,
        "width": 40,
        "height": 8,
    }

    def escalon_maximo(img) -> float:
        px = img.load()
        w, h = img.size
        perfil = [sum(_lum(px[x, y]) for y in range(h)) / h for x in range(w)]
        return max(abs(perfil[i + 1] - perfil[i]) for i in range(len(perfil) - 1))

    pg.mouse.move(4, 4)
    pg.wait_for_timeout(900)
    base = escalon_maximo(Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB"))

    apuntar(pg, PULSABLE_SCROLL)
    esperar_pot_asentada(pg)
    con = escalon_maximo(Image.open(io.BytesIO(pg.screenshot(clip=clip))).convert("RGB"))

    tope = base * PLUMA_MARGEN + 0.002
    if con > tope:
        fallos.append(
            f"el charco corta a canto vivo en la arista de {PULSABLE_SCROLL}: escalon maximo "
            f"de luminancia {con:.4f} con charco contra {base:.4f} sin el (tope {tope:.4f})"
        )
```

Engancha `gate_pluma(pg, fallos)` en `main()` junto a las otras, con el mismo patron de lista.

- [x] **Paso 2: verla dar ROJO**

Corre el arnes sin tocar todavia el charco. Esperado: la familia 10 falla, porque hoy hay corte a
canto vivo en la arista. **Pega la salida literal en tu informe.** Si sale verde, el gate no sirve:
para y dilo — no lo ajustes hasta que pase.

- [x] **Paso 3: implementar la pluma**

Constante, junto a `LUZ_MEDIO`:

```ts
/*
 * La pluma del recorte. El charco SIGUE recortado a la caja de la diana —eso
 * es lo unico que dice hasta donde llega la zona pulsable— pero el filo se
 * difumina 14px hacia dentro, que es lo que se leia como caja. Se difumina el
 * filo, no se quita el limite: el charco sigue muriendo dentro de la diana y
 * nunca fuera.
 */
const PLUMA = 14;
```

Dentro de `tick()`, en la rama del lienzo, justo despues del
`huecoCtx.fillRect(rect.left, rect.top, rect.width, rect.height);` que ya existe y ANTES del
`huecoCtx.restore();`:

```ts
        // Se borra hacia dentro desde cada arista con `destination-out`. La
        // pluma se acota a la mitad del lado para que en una diana estrecha no
        // se coma el charco entero. Las esquinas se borran dos veces, lo que
        // las deja mas blandas todavia: es lo que se quiere.
        huecoCtx.globalCompositeOperation = "destination-out";
        const plumaX = Math.min(PLUMA, rect.width / 2);
        const plumaY = Math.min(PLUMA, rect.height / 2);
        const aristas: Array<[number, number, number, number, number, number, number, number]> = [
          [rect.left, 0, rect.left + plumaX, 0, rect.left, rect.top, plumaX, rect.height],
          [rect.right, 0, rect.right - plumaX, 0, rect.right - plumaX, rect.top, plumaX, rect.height],
          [0, rect.top, 0, rect.top + plumaY, rect.left, rect.top, rect.width, plumaY],
          [0, rect.bottom, 0, rect.bottom - plumaY, rect.left, rect.bottom - plumaY, rect.width, plumaY],
        ];
        for (const [gx0, gy0, gx1, gy1, bx, by, bw, bh] of aristas) {
          const borrado = huecoCtx.createLinearGradient(gx0, gy0, gx1, gy1);
          borrado.addColorStop(0, "rgb(0 0 0 / 1)");
          borrado.addColorStop(1, "rgb(0 0 0 / 0)");
          huecoCtx.fillStyle = borrado;
          huecoCtx.fillRect(bx, by, bw, bh);
        }
```

El `huecoCtx.restore()` que ya esta debajo devuelve `globalCompositeOperation` a su valor por
defecto: no lo restaures a mano.

**No toques la rama de `imagenDiana`** (el `background-image` en linea). Anade encima de ella este
comentario y nada mas:

```ts
        // La pluma del recorte (spec 2026-09-10) NO se aplica aqui a
        // proposito. Este mecanismo hoy no pinta en ningun sitio: su unica
        // diana era `.credit` y se fue con el catastro de creditos, asi que
        // ningun gate podria verlo en rojo. Cuando esta familia tenga diana
        // ocluida nueva —encargo abierto, ver el docstring del arnes— la pluma
        // entra con ella y se mide entonces, no antes.
```

- [x] **Paso 4: verde, build y lint**

```bash
npm run build && npm run lint
python3 scripts/measure-cursor-luz.py --base http://127.0.0.1:4214
```

Esperado: familia 10 en verde, total de fallos **exactamente 1**.

- [x] **Paso 5: captura y mirada**

Captura `.obra-abrir` y `[data-cimientos] .cim-nombre` con el charco encendido, en `/tmp/pluma-t2/`,
y miralas: el charco tiene que morir hacia dentro sin canto visible, y el texto de la diana tiene
que leerse igual de bien que con el charco apagado.

- [x] **Paso 6: commit**

```bash
git add src/components/hyprCursor.ts scripts/measure-cursor-luz.py
git commit -m "feat(cursor): el recorte del charco se empluma 14px hacia dentro"
```

---

## Tarea 3: Los tres riesgos anotados y la verificacion completa

**Ficheros:**
- Modificar (solo si algun riesgo se confirma): `src/components/hyprCursor.ts`
- Modificar: `scripts/measure-cursor-luz.py` (solo si hace falta una asercion mas)

**Interfaces:**
- Consume: todo lo de las tareas 1 y 2.
- Produce: los numeros de antes/despues que van al commit del fallo y al registro del spec.

- [x] **Paso 1: riesgo A — la brasa bajo una diana muy baja**

`.hero-mail` mide 211x22. La brasa cae a 2px por debajo de una linea de texto de 22px de alto.
Captura y **mira**: comprueba que no se lee como subrayado del texto de la linea siguiente. Si lo
hace, PARA y dilo en el informe con la captura: es una decision de diseno, no la resuelvas tu.

- [x] **Paso 2: riesgo B — dianas contiguas**

Los 23 nombres de los cimientos estan pegados. Roza uno del medio de una columna y captura: la brasa
no puede invadir la caja del vecino. El acotado a `rect.left`/`rect.right` deberia cubrirlo por
construccion; confirmalo con la captura, no por lectura del codigo.

- [x] **Paso 3: riesgo C — la pluma y el contraste**

Emplumar reduce el area donde el charco oscurece, y el charco que oscurece es el que SUBE el
contraste. Corre el arnes **entero**, con la familia de contraste incluida, y compara sus numeros
contra los de antes de esta rama:

```bash
nohup python3 scripts/measure-cursor-luz.py --base http://127.0.0.1:4214 > /tmp/cursor-t3.log 2>&1 &
PID=$!; until ! kill -0 $PID 2>/dev/null; do sleep 5; done; tail -40 /tmp/cursor-t3.log
```

Esperado: los pisos por familia siguen cumpliendose. Si el contraste baja, **la pluma se recorta
antes que la calibracion**: baja `PLUMA` de 14 hasta que vuelva a cumplir y deja escrito el numero
final. No toques `HUECO_CENTRO`, `HUECO_MEDIO`, `LUZ_CENTRO`, `LUZ_MEDIO` ni `LUM_OSCURA`.

- [x] **Paso 4: que nada mas se ha movido**

```bash
npm run build && npm run lint
python3 scripts/verify.py --base http://127.0.0.1:4214
python3 scripts/measure-cimientos.py --url http://127.0.0.1:4214
python3 scripts/measure-placa.py --base http://127.0.0.1:4214
```

Esperado: `verify.py` sale 0 ("12 fallos conocidos, 0 nuevos"), los otros dos en verde. Vice y
Caelestia no se han tocado: confirmalo abriendo `?theme=vice` y `?theme=caelestia` con oyente de
consola y capturando.

- [x] **Paso 5: commit**

```bash
git add -A src/components/hyprCursor.ts scripts/measure-cursor-luz.py
git commit -m "test(cursor): los tres riesgos del spec, medidos"
```

Si ningun fichero cambio en esta tarea, no hay commit: dilo en el informe y pasa.

---

## Tarea 4: El registro

**Ficheros:**
- Modificar: `scripts/measure-cursor-luz.py` (docstring de cabecera)
- Modificar: `docs/superpowers/specs/2026-09-10-hyprland-cursor-brasa-design.md`
- Modificar: `docs/superpowers/plans/2026-09-10-hyprland-cursor-brasa.md`
- Modificar: `/home/aoshi/proyectos/portfolio-aoshi/.claude/rules/verification.md`

- [x] **Paso 1: el docstring del arnes**

En la cabecera de `scripts/measure-cursor-luz.py`, junto al aviso del fallo esperado que ya existe,
anade las tres familias nuevas a la lista numerada de "cada asercion nace de un fallo real ya pagado
en este repo", diciendo cual: que el cursor rodeo cada pulsable con un rectangulo naranja durante
semanas con este mismo arnes en verde, porque vigilaba el charco y nunca miro la senal.

- [x] **Paso 2: el registro de implementacion del spec**

Anade al spec una seccion `## Registro de implementacion` con: los numeros de antes y despues, el
valor final de `PLUMA` (14 o el que haya quedado), lo que dijeron las capturas de los tres riesgos,
y cualquier decision que hayas tenido que tomar por tu cuenta. Cambia `Estado:` de
`pendiente de plan` a `implementado` **solo si todas las casillas de este plan estan marcadas**;
si queda alguna, dejalo en `en ejecucion`. `scripts/verify.py` cruza las dos cosas y falla si se
contradicen.

Anade tambien la linea `Plan: \`docs/superpowers/plans/2026-09-10-hyprland-cursor-brasa.md\`` en la
cabecera del spec, debajo de `Estado:`.

- [x] **Paso 3: la tabla de arneses**

`/home/aoshi/proyectos/portfolio-aoshi/.claude/rules/verification.md` tiene una tabla con un renglon
por arnes. **Ojo: `.claude/` esta en `.gitignore`, asi que ese fichero NO existe en este worktree**
— editalo en la ruta absoluta del repo principal que se da arriba, y no lo anadas a ningun commit.
Actualiza el renglon de `measure-cursor-luz.py` para que mencione las tres familias nuevas y siga
diciendo que el arnes sale con 1 fallo esperado.

- [x] **Paso 4: commit**

```bash
git add scripts/measure-cursor-luz.py docs/superpowers/specs/2026-09-10-hyprland-cursor-brasa-design.md docs/superpowers/plans/2026-09-10-hyprland-cursor-brasa.md
git commit -m "docs(cursor): registro de implementacion de la brasa"
```

---

## Paso 5: la revision de Aoshi en el sitio real

- [x] Aoshi ve la brasa en el sitio servido y da su visto bueno.

Revisado el 2026-09-10 sobre el build de la rama servido por tailnet
(`http://100.77.228.13:4216/?theme=hyprland`). Veredicto de Aoshi: "Esta excelente".

Esta casilla la marca el orquestador, no un implementador. Hasta entonces el spec no puede decir
`implementado`.
