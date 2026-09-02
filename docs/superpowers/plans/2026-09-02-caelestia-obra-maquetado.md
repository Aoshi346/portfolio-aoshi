# Caelestia B3 — Obra: plan de maquetado

> **Esto NO es un plan de implementación.** Es la agenda de diseño de la fase B3: qué maquetas hay
> que construir en el companion, en qué orden y contra qué medirlas, para poder escribir después el
> spec y el plan. B3 **no tiene spec todavía**, y por eso no puede tener plan de implementación:
> planificar trabajo sin diseñar es lo que dejó en este repo planes con 86 y 57 casillas sin marcar.

Fecha: 2026-09-02
Fase: **B3** de seis. Las dos anteriores:
**B1 (Título)** implementada y fusionada — `docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md`;
**B2 (Quién soy)** especificada, planificada y en ejecución en el worktree
`/home/aoshi/proyectos/portfolio-aoshi-b2` (rama `design/caelestia-quien-soy`) —
`docs/superpowers/specs/2026-09-02-caelestia-quien-soy-design.md`.

---

## Qué es B3 y por qué es la peor de las cinco

La escena `#obra` es **la más rota**, no la más incompleta. Medido sobre el build de producción con
Node 22, `vite preview`, `?theme=caelestia` y movimiento reducido, en la ventana de 1412 × 748 que
impone el carril de workspaces:

| | valor |
|---|---|
| ventana del workspace | 1412 × 748 (barra 44 px en y=12, dock 60 px en y=826) |
| alto del contenido del carril de obra | **4964 px** |
| `overflow` del carril (`div#obra.obra-rail`) | **`auto`** → `scrollHeight` 4964 contra `clientHeight` 748: **scroll interno de 6,6 pantallas** |
| proyectos en pantalla | **1 de 5.** Los otros cuatro caen entre y=1051 e y=5032 dentro de esa caja |
| desbordamiento del primero | superficie de y=165 a y=955 contra un borde de ventana en y=816 → **139 px cortados**, y el dock los pisa desde y=826 |
| ancho muerto | la superficie mide 1316 y el texto se corta en `max-w-4xl` → **~300 px vacíos a la derecha** |
| alto de cada escena de proyecto | 983 / 990 / 1009 / 990 / 990 px |

Dos defectos, y el primero es estructural, no de acabado:

1. **Cuatro de los cinco proyectos no existen en Caelestia.** No están apretados: están fuera de la
   caja y no hay forma de llegar a ellos.
2. **El carril tiene scroll interno**, que es exactamente lo que la ley de la fase A prohíbe: *un
   espacio de trabajo no se desplaza, se cambia*. Hoy Obra la incumple por dentro.

Y lo que la captura enseñó y ningún número decía: **las nueve capturas son marcadores «CAPTURA
PENDIENTE» pintados con la paleta de Vice** —morado `#150726` y ámbar— dentro de un esquema oscuro
OkLCH. Chillan como cuerpo extraño, y en la captura actual además quedan cortadas por la mitad en el
borde inferior de la ventana.

---

## El bloqueo, y cómo se trabaja con él

Las nueve piezas de `public/media/obra/*.webp` son marcadores de 1600 × 1000 (relación 16:10). De
las cinco escenas, Obra es **la más sensible a la calidad de esas imágenes**, porque su pieza
central es una previsualización. El riesgo real es aprobar una maqueta que se caiga cuando entren
las capturas de verdad.

No bloquea el maquetado, con tres condiciones que esta agenda impone:

1. **Las maquetas dibujan el hueco de captura como caja neutra** con la relación real 16:10 y una
   retícula de marcador propia. **Nunca los `.webp` actuales**: su paleta de Vice envenena cualquier
   juicio de color de la escena.
2. **Las nueve capturas reales entran antes de implementar.** Es tarea de Aoshi, y es lo que puede
   tardar. El gate visual de B3 no se da por bueno con marcadores.
3. La maqueta decide una **regla de tratamiento** para las capturas —mate, filete, saturación en
   reposo frente a seleccionada—, porque los colores de una aplicación ajena nunca van a estar en la
   rueda OkLCH de la hora. Sin esa regla, una captura real desafina igual que un marcador.

Si Aoshi prefiere invertir el orden mientras reúne las capturas, **B4 (Créditos) no depende de
nada** y puede adelantarse.

---

## Lo que ya está decidido y NO se vuelve a abrir

- **Cada escena es una aplicación.** Obra es **el gestor de archivos**. Es la dirección aprobada en
  la fase A; lo que falta es la ejecución.
- **La ventana es 1412 × 748 y no se desplaza.** Ley de la sección: *lo que quede bajo el pliegue es
  ampliación, nunca lo que hacía falta para entender la escena.* En B3 esto tiene consecuencia
  directa: **el scroll interno del carril desaparece**, no se disimula.
- **El motor de color** (`caelestia.color.ts`): matiz por la hora, claridad fija, esquema sin
  interpolar. No se toca.
- **La tipografía**: Fraunces display, Hanken Grotesk cuerpo, Martian Mono utilidad. Y la lección de
  B1: **`opsz` se elige por el tamaño al que se lee** — `--cae-display-axes-cartel` para lo grande,
  `--cae-display-axes` para 15–30 px.
- **El fondo** lo estrenó B1 y B3 lo hereda sin tocarlo. Aquí la aplicación llena la ventana, así
  que apenas asoma.
- **Anti-mock:** todo dato visible sale de `content.ts` literal.

---

## Contenido real disponible

De `src/data/content.ts`, `caseStudies` — cinco entradas, y nada más:

| campo | contenido |
|---|---|
| `title` / `tag` / `lead` | EchoPlan · Gestión de campañas · «Todas las campañas, un solo tablero.» |
| `role` / `period` / `status` | period **no siempre existe** (TesisFar no lo tiene) |
| `problem` / `solution` | dos párrafos largos: ~250 y ~300 caracteres. Son el bulto real de la escena |
| `stack` | de 2 (C · GTK4) a 5 nombres (Python · Django · TypeScript · React · Vite) |
| `gallery` | **2 capturas en cuatro proyectos, 1 en «Editor de texto»**. Ninguna composición puede asumir dos |
| `link` **o** `privateProject` | tres llevan enlace a repositorio; dos son privados y solo pintan la nota |

**`tooling` no se pinta aquí.** Existe solo para el cruce «Aparece en» de Créditos, y el comentario
de `content.ts` dice que eso es la decisión, no un olvido. Las cifras de `stats` tampoco: son de
Título.

---

## El enfoque de partida

El gestor de archivos ya resuelve solo el problema de los cinco en 748 px: **un gestor de archivos
no apila documentos, los lista y los previsualiza**. Es el patrón *list-detail* de Material 3 y es
cómo funcionan Nautilus y Finder de verdad.

```
┌ 1412 ─────────────────────────────────────────────────────────┐
│ ~/obra   ▸ 5 elementos                     [lista] [galería]  │  barra de ruta
├──────────────┬────────────────────────────────────────────────┤
│ ▸ EchoPlan   │  EchoPlan             Gestión de campañas      │
│   TesisFar   │  Todas las campañas, un solo tablero.          │
│   HyprFinance│  ┌────────────────┐  Rol     Desarrollo full…  │
│   WatchDog   │  │    captura     │  Periodo Ago 2025 — May…   │
│   Editor…    │  │     (16:10)    │  Stack   Python · Django…  │
│              │  └────────────────┘  Estado  Sistema interno   │
│              │  Problema         │  Solución                  │
└──────────────┴────────────────────────────────────────────────┘
```

Tres cosas que compra, y que hay que verificar en la maqueta antes de darlas por buenas:

- **Los cinco siempre en pantalla.** Cinco filas de ~64 px son 320 px: sobra sitio en 748. Ninguna
  decisión de «qué se pierde bajo el pliegue» que tomar.
- **Los metadatos ya son un panel de propiedades.** `role`, `period`, `stack`, `status` son lo que un
  gestor de archivos enseña como tipo, fecha y tamaño. No hay que inventarles forma: ya la tienen.
- **El ancho muerto desaparece sin estirar el texto.** Los ~300 px sobrantes los ocupa la captura,
  que es el único activo visual real del proyecto.

Es el punto de partida a discutir, no la respuesta. **M2 lo pone a competir con otras dos.**

---

## Lo que NO puede ser

- **La captura no viaja con Flip hasta un visor grande.** Ese gesto es el cartel de Obra de
  Hyprland (`2026-08-10-hyprland-obra-cartel`), y repetirlo convierte dos temas en el mismo tema con
  otra paleta. Aquí la selección se resuelve con el **eje compartido de Material 3** —el detalle
  entra por X porque la lista está a la izquierda—, que además es el vocabulario del sistema que
  Caelestia imita.
- **La entrada de escena no es una tercera terminal.** B1 teclea `whoami`; **B2 es entera la salida
  de `neofetch`**, con el prompt devuelto al final. A la tercera es un tic, no un idioma. El gesto
  natural aquí es el del propio gestor: el directorio poblándose —las cinco filas entrando
  escalonadas y la primera auto-seleccionándose— y como mucho la ruta `~/obra` apareciendo en la
  barra.
- **El ordinal gigante de Vice no sobrevive.** `text-paper/[0.06]` es un token de Vice; en un gestor
  de archivos el número de orden, si existe, es el índice de la fila.

---

## La agenda de maquetas

Cada punto es una pantalla del companion, construida con `/frontend-design:frontend-design`, con la
piel real de Caelestia y **capturada y mirada antes de enseñarla**.

- [ ] **M1 · Diagnóstico.** La escena actual dentro de la ventana, con las medidas encima: los 4964
      px de contenido en 748, el scroll interno, los 139 px que el dock se come del primer proyecto,
      los cuatro proyectos inalcanzables y los ~300 px muertos a la derecha. Enseñar también el
      marcador de captura con la paleta de Vice: es parte del diagnóstico.

- [ ] **M2 · Tres composiciones del gestor.** No tres tallas de la misma: tres repartos distintos.
      Punto de partida sugerido:
      - **lista-detalle** (el de arriba): columna de cinco a la izquierda, detalle a la derecha;
      - **vista galería** tipo Finder: captura grande arriba a sangre, tira de cinco miniaturas
        debajo y columna de propiedades a la derecha;
      - **rejilla de carpetas**: los cinco como iconos grandes en una cuadrícula, y el detalle abre
        como panel lateral sobre ella.
      Las tres medidas en la ventana real, con el número de alto sobrante a la vista.

- [ ] **M3 · La ficha de un proyecto en detalle.** El bulto real: `problem` y `solution` suman ~550
      caracteres. Cuántas líneas ocupan a la medida elegida, y si caben junto a la captura sin
      recortar ninguno de los dos. **El proyecto de prueba es EchoPlan** (el más largo) y
      **«Editor de texto»** (una sola captura, dos tecnologías, sin `period`): si la composición
      aguanta los dos extremos, aguanta.

- [ ] **M4 · El tratamiento de la captura.** Caja neutra 16:10. Mate, filete, sombra, radio de
      Material 3, y la regla de saturación en reposo frente a seleccionada. Aquí se decide cómo
      convive una imagen de colores ajenos con la rueda OkLCH de la hora. **Enseñarla a las 09:00 y
      a las 03:00**, que es cuando se rompe.

- [ ] **M5 · La selección.** El gesto de pasar de un proyecto a otro: eje compartido de Material 3,
      con la lista quieta y el detalle entrando por X. Vivo, con **Repetir** y deslizador de
      velocidad —a ×0,4 es donde se juzga—. Y qué pasa al pasar el ratón por una fila sin pulsarla.

- [ ] **M6 · La entrada de escena.** El directorio poblándose. Tres variantes de ritmo, **ninguna
      con terminal**, todas con el shell ya montado antes de que pase nada.

- [ ] **M7 · Los dos estados de pie:** el enlace «Ver repositorio» y la nota de proyecto privado.
      Son dos cosas distintas que ocupan el mismo sitio y hoy se resuelven con la tipografía de
      Vice.

- [ ] **M8 · Movimiento reducido** de lo que se elija, y la escena a las 03:00 en esquema oscuro.
      La lección de B1: **el croma no es el mismo en los dos esquemas** — croma alto con claridad
      baja da barro en OkLCH.

---

## Contra qué se mide

El arnés de B3 (`scripts/measure-caelestia-obra.py`, aún sin escribir) hereda de B1 y B2:

1. **Cabe, y sin scroll interno.** `scrollHeight === clientHeight` en el contenedor de la escena, y
   aire bajo el pie ≥ 0. **Esta aserción es la razón de ser de la fase**: hoy daría 4964 contra 748.
2. **Los cinco proyectos son alcanzables** con teclado y con ratón, y **ninguno queda fuera de la
   ventana**. Medido por caja, no por presencia en el DOM: hoy los cinco están en el DOM.
3. **Ninguna captura queda cortada** por el borde de la ventana ni por el dock.
4. **Anti-mock**: todo texto visible existe en `content.ts`, y `tooling` **no** aparece.
5. **Aguanta los dos extremos de contenido**: EchoPlan (texto más largo, dos capturas) y Editor de
   texto (una captura, sin `period`).
6. **Contraste** contra el fondo real, barriendo las 24 horas, ≥ 4,5:1 — incluidos los rótulos sobre
   la propia captura, si alguno acaba encima.
7. **Movimiento reducido**: escena montada, primer proyecto seleccionado, sin recorrido.
8. **Los ejes del shell no se han movido**, y **Vice y Hyprland siguen intactos** — `projectScene.ts`
   es compartido por los tres temas, así que cualquier cambio ahí se verifica en los tres.

**Ningún gate se da por bueno sin haberlo visto dar rojo contra el fallo que dice cazar.**

---

## Entregables de la fase

En este orden, que es el que ya funcionó en la fase A, en B1 y en B2:

1. Las maquetas M1–M8 en el companion, con aprobación de Aoshi por pieza.
2. `docs/superpowers/specs/2026-09-0X-caelestia-obra-design.md`, con `Estado: pendiente de plan`.
   **Reutilizar el spec de B2 como plantilla** — es el más cercano en estructura.
3. Rescatar al repo cualquier artefacto aprobado que viva en el companion. **`.superpowers/` está en
   `.gitignore` (línea 47)**: lo que se quede ahí se pierde. Precedente:
   `2026-08-26-caelestia-titulo-prototipo.glsl`, `2026-08-26-caelestia-firma-paths.json`,
   `2026-09-02-caelestia-quien-soy-maqueta.html`.
4. `docs/superpowers/plans/2026-09-0X-caelestia-obra.md` con `superpowers:writing-plans`.
5. El traspaso, con modelo y esfuerzo recomendados.

---

## Estado al escribir esto

- **B1 (Título):** implementada y fusionada en `main` (`ad6affd`, `1fa9891`).
- **B2 (Quién soy):** en ejecución en el worktree `/home/aoshi/proyectos/portfolio-aoshi-b2`, rama
  `design/caelestia-quien-soy`. Su spec, su plan y su arnés (`measure-caelestia-quien-soy.py`) viven
  ahí y **todavía no están en `main`**. B3 no toca `about.ts`, así que no se estorban.
- **B3 (Obra):** esta agenda. **Bloqueada para implementar** por las nueve capturas; **no bloqueada
  para maquetar**, con las tres condiciones de arriba.
- **B4 (Créditos) y B5 (Fundido):** con encargo pendiente de la fase A — Créditos necesita un
  resumen que se sostenga solo en vez de 23 nombres que empiezan y siguen; Fundido llega corto y
  deja media ventana vacía en la escena de cierre. **B4 no depende de nada y puede adelantarse** si
  las capturas tardan.
