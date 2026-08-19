# El haz al mando — el fondo de Hyprland deja de ser un degradado y pasa a ser una luz acotada

Estado: pendiente de plan
Fecha: 2026-08-19
Alcance: sólo `src/backgrounds/hyprEmber.ts` y el cableado de sus uniforms dinámicos en
`src/themes/hyprland.ts`. **Vice no se toca** (cerrado el 2026-08-05). **Caelestia no se toca.**
`shaderBackground.ts` es compartido y **no se modifica**: todo lo que hace falta ya existe en él.

## Por qué

El fondo actual no falla por gusto. Falla por cuatro cosas medidas.

**1. No tiene techo, y se pasa el 100% del tiempo.** `scripts/measure-bg-luma.py` contra el build
de producción, p99.5 de la banda tipográfica:

| scroll | banda p99.5 | fotograma p99.5 | píxel máx |
|---|---|---|---|
| 0 | 119,4 | 118,6 | 123,2 |
| 1477 | 127,9 | 127,1 | 131,7 |
| 2659 | **130,6** | 129,8 | 134,6 |

24 superaciones de techo. El techo de la banda es 62.

**2. Late en un ciclo de 150 s que nadie pidió.** A scroll fijo, muestreando cada 14 s:

```
t(s)    6    20    34    48    62    76    90   104   118   132   146   160   174
luma  116.9 126.5 130.6 127.1 117.6 105.9 96.9 95.4 102.3 114.0 125.3 132.2 131.5
```

Es el `mix(crim, ember, 0.5 + 0.5*sin(t))` con `t = uTime*0.04`: periodo teórico 157 s. Lo bastante
lento para no leerse como animación y lo bastante amplio —38 puntos de luma— para que el texto
cambie de legibilidad mientras se lee. **Ni en su punto más oscuro baja de 95.**

**3. El techo que se venía usando era el de otro tema.** El 62 es el de Vice, calibrado contra su
papel `#fff4e8`. Los de Hyprland, calculados contra sus propios tokens:

| token de texto | luma | fondo máx. AA 4,5:1 | AAA 7:1 |
|---|---|---|---|
| `--color-paper` `#ffeae6` (titular) | 238,2 | 108,6 | 79,8 |
| `--catch` `#ffd9cc` | 224,1 | 100,3 | 71,9 |
| `--haze` `#b18c86` (cuerpo) | 147,4 | **46,1** | **imposible** |

El binding es `--haze`: **46,1**, y no alcanza AAA contra ningún fondo posible. Eso es un hallazgo
de paleta, no de fondo — ver `## Decisiones que quedan fuera`.

**4. No usa el scroll.** `shaderBackground.ts` expone `DynamicUniforms`, un modelo "pull" que Vice
usa para alimentar su fondo. Hyprland no lo usa en absoluto: su única fuente de cambio es el reloj.

## La tesis

**El campo se aplana y el haz pasa a ser el asunto.** Hoy hay un halo blando con una cuña dura
pegada encima, y se nota el injerto. Aquí el haz es lo único que hay: dos cantos de comportamiento
distinto, su recorrido gobernado por el scroll, y un derrame que sale del propio haz en vez de ser
un segundo foco con coordenadas propias.

Esto **espeja la organización de Vice sin copiar su material**, que es la relación que el proyecto
ya tiene escrita entre los dos temas: Vice es tinta impresa, Hyprland es luz con canto.

## Los dos mecanismos que se importan de Vice

### 1. Techo de luminancia dentro del shader

```glsl
vec3 techo(vec3 c){
  float lm = TECHO / 255.0;
  float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
  return l > lm ? c * (lm / max(l, 1e-4)) : c;
}
```

Se importa **el mecanismo, no el valor**. La razón de que escale por luminancia y no por canal
está en `viceInk.ts` y es correcta: el verde aporta el 71% de la luminancia percibida, así que un
tope por canal se calibra mirando un tono concreto y se rompe en cuanto el fondo recorre otro.

**Valor para Hyprland: 46** (`--haze`, AA 4,5:1). No 62, que es el de Vice.

**El recorte va el ÚLTIMO, después del grano.** Medido: con el grano sumado después, su cola
positiva se escapa y el p99.5 sale a 48,1 en vez de 46,1. Un gate que se puede saltar por el
último `+=` no es un gate.

### 2. Una sola vía de reacción

Fuera el `sin(uTime)` que hacía el latido. `uScroll` (0..1, progreso del documento) gobierna:

- el balance `mix(CRIM, EMBER, uScroll)`,
- la posición del origen del haz,
- su ángulo,
- su semiancho,
- la entrada del segundo haz.

Queda una deriva de tiempo mínima para que no sea una imagen fija. **Sin puntero y sin velocidad**,
igual que Vice, y por la misma razón que él deja escrita: añadirlos sería rediseñar.

## Las seis correcciones del haz

Sobre la variante aprobada en el companion (`.superpowers/brainstorm/*/content/haz.html`).

| # | Corrección | Qué arregla |
|---|---|---|
| 1 | **Canto asimétrico** — distancia con signo al eje, sin `abs()`. Un canto duro de 1 px que define el haz; el otro lado se disuelve en el material a lo largo de 0,42. | Con `abs()` los dos cantos salen idénticos y el haz se lee como una cinta pegada encima, no como luz. |
| 2 | **Sale a sangre** — fuera el viñeteado radial; queda una caída leve sólo en el vértice contrario al haz. | El viñeteado moría justo en las esquinas, que es por donde el haz sale del cuadro: reblandecía con una línea lo mismo que el canto endurece. |
| 3 | **Caída por su eje** — `dot(rel, dir)` en vez de `smoothstep` sobre `p.y`. | La caída era un degradado vertical de viewport: al girar el haz con el scroll, no giraba con él, y la luz se apagaba por una razón ajena a la luz. |
| 4 | **Corte en frontera** — el segundo haz entra con corte seco en el límite Obra→Créditos (ver aviso abajo). | Antes entraba con una rampa de 0,45 a 0,75, a mitad de sección. Algo que aparece de la nada dentro de una escena se lee como fallo de render. |
| 5 | **Derrame del haz** — el resplandor se calcula desde el eje del haz (`exp(-abs(s - hw) * 2.6)`) en vez de ser un foco con posición propia. | El halo suelto ni se veía ni se echaba de menos, y pagaba render. |
| 6 | **Materia dentro** — grano de carbón **multiplicativo** dentro del haz. El canto se queda liso. | Sin textura el interior del haz es un plano liso. Aditivo subiría el suelo del cuadro entero. Y un canto duro con textura deja de ser un canto duro. |

### Aviso sobre la frontera del corte

En el companion la entrada está en `smoothstep(0.735, 0.765, uScroll)` porque allí las cinco
secciones miden lo mismo. **En el sitio real no lo miden**, así que 0,75 no es el límite
Obra→Créditos: es sólo el 75% del documento. El valor tiene que salir del `offsetTop` real de la
sección de créditos dividido por el alto desplazable, calculado en JS y pasado como uniform —no
escrito a mano en el shader— y recalcularse en `resize`. Si se deja el literal, el corte caerá a
mitad de una escena, que es exactamente el defecto que esta corrección viene a arreglar.

## Responsive: el aspecto gobierna cuatro parámetros, no uno

Medido a 390×844: con el semiancho fijo, **la pantalla entera queda dentro del haz** y su canto
duro —lo único que define esta dirección— cae fuera del encuadre. Y con el origen fijo en −0,62 el
sitio abre con el fondo casi vacío, porque en un encuadre estrecho el haz aún no ha entrado.

Con `vertical = smoothstep(1.0, 0.62, aspect)`:

| | escritorio (`vertical` = 0) | móvil 390 (`vertical` ≈ 1) |
|---|---|---|
| ángulo | 1,36 rad | 1,52 rad |
| semiancho | ×1,00 | **×0,42** |
| origen en x | −0,62 → +0,33 | **−0,30 → +0,32** |
| derrame | 0,30 | **0,17** |

Escritorio queda **byte a byte idéntico**: todo va por `mix(escritorio, movil, vertical)`, que en
apaisado vale 0.

## El grano va en píxeles CSS, no de buffer

`shaderBackground.ts:175` acota el ratio buffer/CSS:

```js
const ratio = Math.min(window.devicePixelRatio, window.innerWidth <= 820 ? 1 : 1.5);
```

Así que el móvil real renderiza a ratio **1** y el escritorio retina a **1,5** — nunca a 3. Con el
paso del grano fijo en píxeles de buffer, su tamaño **físico** cambia ~1,5× entre las dos, y dos
visitantes ven materiales distintos. Se divide `gl_FragCoord` por `uPixelRatio`, que el módulo
compartido ya expone y que `viceInk.ts` ya usa por este mismo motivo, documentado allí.

## Movimiento reducido

Con `prefers-reduced-motion`, `shaderBackground.ts` ya congela el tiempo en `STATIC_FRAME_TIME = 8.0`.
**`uScroll` sigue gobernando**: no es animación, es posición, y quitarla dejaría el fondo mudo para
quien pide movimiento reducido.

## Números de aceptación

p99.5 de la banda tipográfica (0,06–0,74 del alto), techo **46**:

| viewport | ratio | scroll 0 | 0,35 | 0,75 | 1,0 |
|---|---|---|---|---|---|
| 390×844 | 1,0 | 44,9 | 45,9 | 46,3 | 46,3 |
| 768×1024 | 2,0 | 43,5 | 46,0 | 46,3 | 46,3 |
| 1440×900 | 1,5 | 45,7 | 46,1 | 46,3 | 46,3 |

Referencia: el fondo de hoy marca **113–131** en la misma medida.

## Restricciones

- **`shaderBackground.ts` no se toca.** `DynamicUniforms` y `uPixelRatio` ya existen; sólo hay que
  cablearlos desde `src/themes/hyprland.ts`.
- **El haz sobrevive con su forma.** `src/components/sceneNav.siluetas.ts` dibuja una pieza `beam`
  sobre los cinco planos de la hoja de contactos. Si el haz cambiara de silueta, esas miniaturas
  dejarían de retratar el sitio. Sigue siendo una cuña diagonal reconocible, así que no hay cambio
  ahí — pero es una comprobación del plan, no una suposición.
- **Vice intacto.** Ni `viceInk.ts` ni su `LUMA_MAX`.
- Radio 0 y filete de 1 px, que es el idioma del tema.

## Verificación

Arnés nuevo, `scripts/measure-fondo-haz.py`, independiente como los demás y contra el build de
producción servido (nunca `npm run dev`: el HMR corrompe sus medidas). Comprueba:

1. p99.5 de la banda ≤ 46 en 12 posiciones de scroll × 3 viewports (390, 768, 1440).
2. Que el corte del segundo haz caiga en el límite real de la sección de créditos y no en el 75%
   del documento: se compara el `uScroll` de entrada contra el `offsetTop` medido de esa sección.
3. Que **no** haya deriva temporal: a scroll fijo, muestreo a lo largo de ≥ 160 s, recorrido de la
   mediana ≤ 2,0. Es el defecto que este spec viene a cerrar y hay que dejarlo medido, no prometido.
4. Que el canto duro esté en pantalla en los tres viewports (existe un salto de luminancia
   ≥ 12 entre píxeles contiguos en la banda del haz).
5. Con `reduced_motion="reduce"`: dos capturas separadas 5 s a scroll fijo, idénticas.

`scripts/verify.py` no lo invoca: los arneses de este proyecto se lanzan a mano, uno por gesto.

## Decisiones que quedan fuera de este spec

**`--haze` `#b18c86` es el que ahoga al fondo.** Fuerza el techo a 46 y no alcanza AAA contra
ningún fondo posible. Subirlo dos escalones daría al haz rango real sin tocar la legibilidad, pero
es un cambio de paleta que toca cuerpo de texto, rótulos y los cuatro dispositivos ya cerrados de
Hyprland. **No se toca aquí.** Queda anotado para decidir aparte.
