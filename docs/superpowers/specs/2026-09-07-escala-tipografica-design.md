# La escala tipográfica de Caelestia

Estado: en diseno
Fecha: 2026-09-07
Rama de trabajo: `design/escala-tipografica`, desde `main` (`a73fa11`)
Origen: `vera-art-director` marca «ausencia de escala tipográfica» por **séptima vez** en el
proyecto (fase A del shell, B1, la tarjeta «Ahora mismo», B4 y B6). Cada vez se aceptó como deuda
conocida. Aoshi la reabre para cerrarla.

---

## Qué se arregla y por qué

**La escala existe. Lo que no existe es la obligación de usarla.**

Está declarada en `src/themes/themes.css`, una cuarta justa de razón 1,333, diez escalones de 12 a
159,66 px. Y está declarada **tres veces**, una dentro de cada bloque de tema
(`:root[data-theme="vice"]` L77, `hyprland` L1185, `caelestia` L3549), con valores idénticos. Nunca
en `:root` a secas.

Medido sobre `themes.css`: **176 declaraciones de `font-size`, 108 con token y 68 con un literal**,
con 39 valores distintos. El reparto no está repartido: **56 de esos literales son de Caelestia**,
3 de Vice —dos de ellos texto dentro de comentarios, así que el número real es 1— y el resto
genéricos. Esta es una deuda de Caelestia, no del proyecto.

De los 56, **23 caen por debajo de 12 px**, el primer escalón: siete valores distintos (8,48 · 9 ·
9,5 · 10 · 10,5 · 11 · 11,5) para un solo trabajo, que es rotular. Rótulos, versalitas y la
monoespaciada del shell. Ahí no hay decisión de diseño detrás de cada número: hay siete tanteos.

**Y hay una segunda escala escondida.** `src/style.css`, que es común a los tres temas, consume los
tokens con respaldo:

```css
font-size: var(--t-1, 0.53rem);   /*  8,48px */
font-size: var(--t-1, 0.66rem);   /* 10,56px */
font-size: var(--t-1, 0.75rem);   /* 12px    */
```

Nueve respaldos distintos para tres tokens. Mientras haya un tema puesto no se pintan nunca, pero
son el número que se pintaría si el token faltara, y el registro fósil de las tallas anteriores a
los tokens. **Un `--t-1` que puede valer 8,48 o 12 según dónde se escriba no es un token, es una
sugerencia.**

## La escala nueva

Tres cambios, ninguno de ellos cosmético:

| token | px | razón respecto al anterior |
|---|---|---|
| `--t-00` | 9,5 | — |
| `--t-0` | 10,67 | 1,125 |
| `--t-1` | 12 | 1,125 |
| `--t-2` | 16 | 1,333 |
| `--t-3` | 21,33 | 1,333 |
| `--t-4` | 28,43 | 1,333 |
| `--t-5` | 37,9 | 1,333 |
| `--t-6` | 50,52 | 1,333 |
| `--t-7` | 67,4 | 1,333 |
| `--t-8` | 89,85 | 1,333 |
| `--t-9` | 119,77 | 1,333 |
| `--t-10` | 159,66 | 1,333 |

1. **Dos escalones nuevos por abajo, con razón 1,125 y no 1,333.** El cambio de razón es
   deliberado: a 10 px el ojo distingue un escalón de 1 px y a 120 px no distingue quince. Una
   razón única en todo el rango deja o sin tallas abajo (1,333 bajo 12 solo da 9, y luego 6,75) o
   con quince tallas arriba que nadie usa. Los 23 literales pequeños caen en `--t-00`, `--t-0` y
   `--t-1`, con un desplazamiento máximo de 1,02 px.
2. **La escala se declara UNA vez, en `:root` a secas.** Los tres bloques de tema dejan de
   repetirla. No es tocar el diseño de Vice: son exactamente los mismos números que su bloque ya
   declara, y su bloque deja de declararlos.
3. **Desaparecen los nueve respaldos de `style.css`.** `var(--t-1)` sin coma. Un token que necesita
   respaldo es un token que no está garantizado; con la declaración en `:root` lo está.

## La migración

Los **56 literales de Caelestia pasan al escalón más cercano de la escala nueva, sin excepciones.**
Mediana del desplazamiento: **0,50 px**. Máximo: **3,90 px**. Seis se mueven más de 2 px y son los
únicos que pueden pedir trabajo de verdad:

| hoy | pasa a | Δ | dónde |
|---|---|---|---|
| 34 px | 37,9 | +3,90 | `.cae-obra-drawer-title h3` — titular del cajón de Obra |
| 32 px | 28,43 | −3,57 | `.cae-cred-nombre` — nombre de pieza en Stack |
| 53,6 px | 50,52 | −3,08 | `.ficha-nombre` — el nombre en Quién soy |
| 26 px | 28,43 | +2,43 | `.ficha-nombre` en móvil |
| 26 px | 28,43 | +2,43 | `.cae-v2` |
| 26 px | 28,43 | +2,43 | `.cae-cred-cruce-lista li` |

**Si una de esas seis rompe su caja, se arregla la CAJA, no se devuelve el número.** Es la única
regla que impide que esto termine en una lista de excepciones, que es exactamente como se llegó a
los 39 valores. Dos de ellas son titulares que Aoshi ya aprobó, así que las seis se miran en
captura, a 1440x900 y a 390x844, antes de aceptarse.

Aviso medido para `.cae-cred-nombre`: la cabecera de Stack tiene **altura fija de 254 px en el
teléfono** desde `e4beed5`, calibrada al peor caso de las 23 piezas porque si cambia de alto al
elegir, la tira se mueve bajo el dedo y tocas una pieza y se elige otra. Bajar el nombre de 32 a
28,43 cambia esa altura: **hay que volver a medir el peor caso de las 23 y actualizar el valor**,
no dejarlo como está.

### La única excepción, y es nombrada

El titular de B1 se justifica midiendo el texto y estirándolo hasta la medida
(`src/themes/caelestia.titulo.ts:48-52`):

```ts
linea.style.fontSize = "100px";
if (ancho > 0) linea.style.fontSize = `${(objetivo / ancho) * 100}px`;
```

Su tamaño lo decide el ancho de la caja, no una talla elegida, así que **no puede estar en la
escala por construcción**. La alternativa sería renunciar a la justificación, que es la firma de la
escena. Se exceptúa en el gate **por selector concreto** (`#hero .cae-ln`), nunca por categoría: si
mañana aparece un segundo elemento con tamaño en línea, el gate se pone rojo. Una excepción que se
nombra se ve; una que se describe se llena.

Fuera de alcance por no pintar en Caelestia: las 6 clases `text-*` de Tailwind
(`projectScene.ts`, `about.ts`, `credits.ts` — DOM genérico que `themes.css` oculta entero) y el
`fontSize` en línea de `sceneNav.siluetas.ts`, con `sceneNav` en `display: none`.

## El orden

Por escenas y de menor a mayor riesgo, un commit por escena, cada una firmada por su arnés de
siempre:

1. **La escala y el shell.** Tokens nuevos, declaración única en `:root`, respaldos fuera, y los 23
   literales pequeños. Desplazamiento máximo 1,02 px. Firma: `measure-caelestia-hora.py`.
2. **Obra.** Incluye el titular del cajón (+3,90). Firma: `measure-caelestia-obra.py`.
3. **Stack.** Incluye el nombre de pieza (−3,57) y volver a medir la altura fija de la cabecera.
   Firma: `measure-caelestia-creditos.py` y `measure-caelestia-movil.py`.
4. **Quién soy.** Incluye el nombre (−3,08 en escritorio, +2,43 en móvil).
   Firma: `measure-caelestia-quien-soy.py`.
5. **Título y Contacto.** Lo que quede. Firma: `measure-caelestia-titulo.py` y
   `measure-caelestia-fundido.py`.

`measure-caelestia-movil.py` entero al cerrar, porque cruza las cinco escenas.

## Los gates (`scripts/measure-escala-tipografica.py`)

Dos familias que se vigilan entre sí. Cada una se ve en rojo contra el fallo que dice cazar antes
de aceptarse.

**1. Estática, sobre el fuente.** No necesita navegador.
   - Cero `font-size` con literal bajo `[data-theme="caelestia"]` en `themes.css`.
   - Cero `var(--t-N, respaldo)` en todo `src/`: el token se usa sin coma.
   - La escala se declara **exactamente una vez** en el repo, y en `:root` a secas.
   - Los doce tokens existen y sus valores son los de la tabla.
   Sabotaje: devolver un literal al CSS y un respaldo a `style.css`.

**2. Viva, sobre el build de producción servido.** Es la que manda.
   - Recorre las cinco escenas de Caelestia en los dos esquemas (13:00 y 23:00), con `is_mobile` y
     sin él, y lee el `font-size` **computado** de cada nodo que pinta texto propio.
   - Cada valor tiene que caer en la escala con tolerancia de 0,01 px.
   - Excepción única y por selector: `#hero .cae-ln`.
   Sabotaje: poner un `font-size` en línea desde la consola sobre un nodo que la familia estática
   no puede ver.

La familia viva existe porque la estática se burla sin querer: Tailwind, estilos en línea desde TS,
`style.css` y cualquier regla futura quedan fuera de una regex sobre `themes.css`. **Lo que vale es
lo que se pinta** — trece instrumentos rotos en este proyecto lo llevan demostrando, y el último,
en B6, salía verde contra el fallo real por medir `scrollWidth` en vez de lo pintado.

## Lo que este trabajo NO es

- **No es tocar Vice.** Su bloque pierde la declaración duplicada de la escala y nada más. Sus
  tallas no cambian: son las mismas.
- **No es Hyprland.** Sus literales quedan como están; el gate acota a Caelestia. Cuando Hyprland
  cierre su rediseño pendiente, se le amplía.
- **No es rediseñar la jerarquía.** Ninguna pieza cambia de papel: la que era rótulo sigue siendo
  rótulo. Lo único que cambia es que su talla pasa a ser una de doce y no una de treinta y nueve.

## Gates de crítica

Al cerrar, `vera-art-director` sobre las cinco escenas, que es quien lleva siete rondas
señalándolo. La pregunta concreta que tiene que responder no es «¿está la escala?» sino **«¿se nota
que las tallas ahora son doce?»** — si la jerarquía no se lee mejor, el trabajo ha sido contable y
no de diseño.
