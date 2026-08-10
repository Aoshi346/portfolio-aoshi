# La placa — "Quién soy" en Hyprland deja de ser una pila de bloques y pasa a ser una ficha técnica

Estado: pendiente de plan
Plan: `docs/superpowers/plans/2026-08-10-hyprland-quien-soy-placa.md`
Fecha: 2026-08-10
Alcance: **solo el tema Hyprland**. `[data-scene="about"]` (`src/sections/about.ts`,
`src/themes/themes.css`, `src/themes/hypr.choreography.ts`). **Vice no se toca** (cerrado el
2026-08-05). **Caelestia no se toca**: se comprueba que sigue idéntico.
Contenido: **`src/data/content.ts` no cambia**. Es un rediseño de estructura y diseño; toda
cadena que aparece en la placa sale literal de ese fichero.

Prototipo aprobado por Aoshi, medido y con los números de este documento:
`.superpowers/brainstorm/1961497-1786322787/content/ficha-b.html`.

---

## Diagnóstico — por qué la composición actual no funciona

Medido contra el build de producción con `?theme=hyprland`, no deducido.

1. **La sección mide 1353 px de alto en un viewport de 900** (1705 px en móvil 390). Es pantalla y
   media de scroll para una sección de presentación.
2. **Siete bloques apilados en vertical** sin razón visible para el orden: ficha, lead, tres filas
   de afirmación|prueba, nota, franja de cuatro cifras, y un track de dos columnas.
3. **Duplicación literal.** Las tres afirmaciones de `.about-pairs` son `focusAreas[*].title` más
   `identity.role` (`about.ts:249-269`), y la columna "En qué me enfoco" del track vuelve a
   imprimir esos mismos títulos con su detalle (`about.ts:170-175`). Vice oculta esa columna
   justo por esto; Hyprland deja las dos.
4. **Aire muerto horizontal.** A 1440, a la derecha de las afirmaciones queda media página vacía.
5. **Una sola micro-interacción** en toda la sección: un filete de 1 px que crece en
   `.about-pair::before` al apuntar.
6. **Tres cifras de `stats` se desperdician.** "Desde 2021" y "Semestre 10" no se leen en ningún
   sitio útil, y el mismo periodo aparece escrito tres veces en el encuadre.
7. **Contenido de `content.ts` sin usar**: `identity.headline`, `identity.subheadline` y
   `aboutCopy[0]` no aparecen en la sección de ningún tema.

### Defecto vivo, independiente de este rediseño

`about.ts:259` llama `stackOf("Frontend", 4)`, pero ese grupo se llama **"Interfaz"** en
`content.ts:142`. La función devuelve cadena vacía y **la segunda pareja se queda sin su prueba en
los tres temas**, incluido Vice — se ve en captura: bajo "5 proyectos · 1 en producción" no hay
nada. Es exactamente el texto que el comentario de `about.ts:22-32` defiende como imprescindible.
**No se arregla en este spec** porque toca a Vice, que está cerrado. Queda anotado para que Aoshi
decida.

---

## Direcciones descartadas, y por qué

Se registran porque el coste de volver a proponerlas es alto y el motivo de descarte no es opinión.

| Dirección | Motivo |
|---|---|
| Pestañas numeradas / carrusel con iris | Resultado por defecto. El carácter estaba en la transición, no en el dispositivo. |
| Mosaico que redimensiona | Repite el carril de obra: `themes.css:2079`, `flex: 1 1 0` → `flex-grow: 3.1`. Y ese carril **abandona** el patrón bajo 821 px (`themes.css:2126`), que es lo que el encargo prohíbe. |
| Revelado por opacidad | Repite la hoja de contactos: comentario literal en `themes.css:2421`, *"La exposición hace de navegación: la escena en curso es la única revelada"*. |
| Temperatura = recencia (eje horizontal) | **Construida y descartada al mirarla.** Con las fechas reales, entre 2021 y agosto de 2025 solo existe la carrera: el 82 % del eje es una banda vacía y se lee como barra de progreso. |
| Temperatura = recencia (estratos verticales) | **Miente.** Un testigo de sondeo exige estratos sucesivos y las trayectorias son concurrentes: apilar duraciones cuenta 2021—2026 dos veces. |
| La carga, el lecho de brasas, la fragua, la frase, el filamento, el canto, el contraluz | Descartadas por Aoshi tras verlas vivas a tamaño real. |
| A sangre, el margen, el cruce | Ídem. El margen además tenía colisión real: el nombre vertical se partía en dos columnas y "SANZ" caía encima de la banda inferior. |

---

## Dirección elegida — la placa

La sección deja de ser una pila de bloques y pasa a ser **una placa de características**: la chapa
atornillada que lleva toda máquina que aguanta producción, con su rótulo diminuto arriba y su dato
grabado abajo. El vocabulario es del sujeto, no traído de fuera: `identity.headline` dice
literalmente *"Construyo sistemas que aguantan producción, no demos."*

La placa ocupa el encuadre entero, de borde a borde del área de contenido. Nada de tarjetas
flotando en el centro.

### Elemento firma

**El corte de tinta.** Al apuntar una celda, una cuña de brasa entra en diagonal por su borde
izquierdo y la cubre en 420 ms. La superficie cambia; el contenido no se mueve ni un píxel. Es lo
único audaz de la sección: todo lo demás se calla.

---

## Composición

Rejilla de **6 columnas × 3 filas**, `gap: 1px` sobre `--rule`, con celdas de distinto ancho.
Una rejilla uniforme es una tabla; anchos desiguales son una placa, y ordenan por importancia sin
cambiar el tamaño de la letra.

Filas: `1.02fr 0.98fr 1.05fr`.

| Celda | `grid-area` | Contenido (todo de `content.ts`) |
|---|---|---|
| Quién | `1 / 1 / 2 / 4` | `identity.name` · `identity.role` + `identity.location` + `identity.headline` · pie: `identity.subheadline` |
| Retrato | `1 / 4 / 2 / 5` | `identity.githubAvatar` |
| Estado *(caliente)* | `1 / 5 / 3 / 7` | `identity.availability` · `aboutCopy[0]` · pie: `identity.now` |
| Hace | `2 / 1 / 3 / 4` | `focusAreas[0]` y `focusAreas[1]`, título y detalle |
| Obra | `2 / 4 / 3 / 5` | `stats` "Proyectos" y "En producción" |
| Último puesto | `3 / 1 / 4 / 4` | `experience[0]`: organización, rol, descripción · pie: periodo |
| Estudia | `3 / 4 / 4 / 7` | `education[0]` + `aboutCopy[1]` · pie: periodo |

**Siete celdas, no catorce.** Se unificó solo lo que era la misma cosa partida en dos: Quién y Rol
son identidad; las dos áreas de enfoque llevaban el mismo rótulo repetido; las dos cifras de obra
cuentan cuánto hay y cuánto vive; y "Desde 2021" y "Semestre 10" **eran el mismo periodo que ya
dice la celda de Estudia** — unirlas cierra una duplicación, no solo reduce ruido.

### Reglas de la celda

- El rótulo y el dato van **pegados al borde superior**. La versión con `justify-content:
  space-between` dejaba un hueco muerto en el centro de cada celda: ese era el motivo real de que
  la placa se viera vacía, no la falta de contenido.
- La línea de periodo se ancla al **pie** de la celda con `margin-top: auto`. Ojo con la
  especificidad: `.placa dd { margin: 0 }` (0-1-1) gana a una clase suelta (0-1-0) y anula el `auto`.
- El retrato va con **`background-size: contain`**, no `cover`. Con `cover` se recortaba la cara.
  Duotono de brasa con el filtro **solo en la capa de imagen**: puesto en el elemento, el
  `grayscale` agrisa también la capa de brasa antes de mezclarla y el duotono desaparece.
- **Solo la celda de Estado se enciende**, con marca de esquina de 14 px. Así "Disponible para
  proyectos" es lo primero que se lee sin necesidad de ser lo más grande.

---

## Tipografía

Escalones **discretos** por `@container`, nunca `clamp()` sobre tokens de escala: un
`clamp(var(--t-4), 4.4cqi, var(--t-7))` devolvía 54,5 px a 1440, que no es ninguno de los diez
pasos del tema. Es la regla que `CLAUDE.md` marca como "Never Do".

| Elemento | < 820 | ≥ 820 | ≥ 1200 |
|---|---|---|---|
| Nombre de cabecera | `--t-5` | `--t-6` | `--t-7` |
| Dato de celda (`.placa-v`) | `--t-3` | `--t-3` | `--t-3` |
| Dato de celda grande | `--t-4` | `--t-4` | `--t-5` |
| Cifra (`.placa-num`) | `--t-5` | `--t-5` | `--t-6` |
| Rótulo | 10 px, tracking `0.26em` | | |
| Detalle | `--t-1` | | |

Contorno de texto, si se usa, en `em` (`0.028em`) y no en píxeles: un trazo fijo pesa el 4,9 % del
cuerpo a 28 px y el 2,1 % a 67 px.

---

## Color y contraste

Medido con la fórmula WCAG 2.1 sobre los tokens de Hyprland.

| Combinación | Ratio | Veredicto |
|---|---|---|
| `--haze` #b18c86 sobre tinta #070302 | 6,81:1 | AA |
| `--haze` sobre lo más claro del fondo real #3a1008 | 5,54:1 | AA, margen estrecho |
| `--l1` #ff5a34 sobre tinta | 6,61:1 | AA |
| Extremo apagado #6b4a44 de un degradado radial | **2,63:1** | **Falla**, incluso como texto grande |

Dos consecuencias, y las dos son obligatorias:

1. **Ningún degradado de texto puede cerrar por debajo de `--haze`.** El descartado cerraba en
   #6b4a44 y el estado de reposo era justo el que fallaba.
2. **El fondo real no es un plano.** La página lleva el shader más `--bg-fallback`, que sube hasta
   #3a1008. Hay precedente medido en el repo: `.about-pairs` necesitó un scrim al 78 % porque el
   texto secundario caía a **3,20:1** sin superficie (`themes.css:1877-1886`). La placa lleva su
   propio scrim, y el contraste **se mide contra el fondo real, no contra un negro plano**.

---

## Movimiento

Los dos regímenes del tema, sin inventar un tercero: **corte** a 420 ms con `--hard`
(`cubic-bezier(0.7,0,0.2,1)`) y **atmósfera** a 900 ms con `--slow`
(`cubic-bezier(0.16,0.84,0.28,1)`), escalonado de 70 ms.

### Entrada — "el montaje"

Las celdas no aparecen: **llegan**. Cada una entra desde el borde de la placa que le queda más
cerca —las de la columna 1 desde la izquierda, la fila 1 desde arriba— y encaja en su hueco.

- Recorrido: 22 px en horizontal, 18 px en vertical. Dirección derivada del `grid-area`, no escrita
  a mano.
- `transform: translate(...)` → `none` en **420 ms `--hard`**, con retardo diagonal
  `((fila-1) + (columna-1)) * 70 ms`: la llegada cruza la placa en vez de recorrer una lista.
- La **opacidad entra más tarde que el desplazamiento**: `0.24s linear` con `+200 ms` de retardo
  sobre el mismo escalonado. Sin esto, el texto se veía **cortado a media llegada** contra el
  `overflow: hidden` de su celda, y leía como fallo en vez de como pieza encajando. Es el defecto
  que se detectó mirando el fotograma intermedio, no razonando.

### Apuntado — "el corte de tinta"

`clip-path: polygon(...)` de una cuña que entra por el borde izquierdo, **420 ms `--hard`** al
encender y **900 ms `--slow`** al apagar. La asimetría es deliberada: encender es un corte, apagar
es enfriarse. Se declara en reglas separadas porque la transición la dicta el estado de destino.
Compositor puro: ni maquetación ni repintado del árbol.

### Ambiente

El nombre de cabecera recoge un foco radial cuya posición deriva despacio (`--lx/--ly`, 22 s). Es
el mismo aparejo que ya usa el titular del hero. **`--lx` y `--ly` van registradas con
`@property`**: sin registrar son cadenas para el navegador y ninguna transición sobre ellas
interpola — el foco salta en vez de moverse.

### `prefers-reduced-motion`

Ni `transition: none` a secas ni nada invisible: las celdas resuelven a `opacity: 1; transform:
none`, el apuntado cambia de estado sin transición, y la deriva del foco se detiene. La placa
completa se lee sin haber interactuado.

---

## Accesibilidad

- Cada celda es focalizable (`tabindex="0"`) y responde igual al foco de teclado que al puntero:
  todas las reglas de apuntado llevan `:focus-within` junto a `:hover`.
- Anillo de foco propio del tema (`--l3`), no el del sistema, que sobre esta tinta casi no separa.
- El orden de lectura es el del DOM, no el de la rejilla: `grid-area` coloca, no reordena el foco.
- Objetivo táctil: la celda entera, muy por encima de 44 px.

---

## Verificación

- `npm run build`, `npm run lint`, `python3 scripts/verify.py` en los tres temas más la pasada
  `--reduced`.
- Capturas del **build de producción** a 1440×900 y 390×844, nunca de `npm run dev`.
- **Arnés propio, y que se le vea fallar antes de darlo por bueno**: ninguna celda con
  `scrollHeight > clientHeight` (el fallo de "las letras se montan" que se cazó dos veces en el
  prototipo, y que en la placa se detecta así y no a ojo), y ningún tamaño de fuente fuera de los
  diez pasos de la escala.
- Contraste medido **contra el fondo real con el shader activo**, no contra un plano.
- Comprobar que Vice y Caelestia siguen idénticos: la sección comparte DOM con los tres temas, así
  que **todo nodo nuevo necesita su `display: none` de base** en la lista compartida de
  `themes.css`. Se ha pagado cuatro veces; la última ensanchó el disparador de Vice de 168 a 411 px.
- Gates: `lidia-naive-tester` con una métrica cronometrable, y `vera-art-director` con umbral 7,5.

## Pendiente de decisión

1. El defecto de `stackOf("Frontend")`, que toca a Vice y por eso no se arregla aquí.
2. El tamaño del retrato. Se probó a media escena (demasiado), a una columna de dos filas
   (demasiado) y en la celda actual de una columna, que es la aprobada. Queda escrito porque el
   equilibrio entre "muestra a alguien" y "no domina la placa" es fino y puede querer revisarse al
   verlo en el sitio real y no en el prototipo.
