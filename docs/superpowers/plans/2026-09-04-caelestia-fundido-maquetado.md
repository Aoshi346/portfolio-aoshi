# Caelestia B5 — Fundido: plan de maquetado

> **Esto NO es un plan de implementación.** Es la agenda de diseño de la fase B5: qué maquetas hay
> que construir en el companion, en qué orden y contra qué medirlas, para poder escribir después el
> spec y el plan. B5 **no tiene spec todavía**, y por eso no puede tener plan de implementación:
> planificar trabajo sin diseñar es lo que dejó en este repo planes con 86 y 57 casillas sin marcar.

Fecha: 2026-09-04
Fase: **B5**, la última de las seis y la que cierra el rediseño de Caelestia. Las anteriores:
A (shell), B1 Título, B2 Quién soy, B3 Obra (fusionada, `en ejecucion` a la espera de las capturas),
B4 Créditos (en implementación en `design/caelestia-creditos-b4`).

---

## El diagnóstico, medido

Medido el 2026-09-04 sobre un **build de producción en un worktree aislado de `HEAD`** (`2d93a50`),
servido con `vite preview`, tema `?theme=caelestia`, workspace 5 activo. Se midió en worktree
aparte **a propósito**: la sesión de B4 tiene sus propios `vite preview` vivos sobre el mismo repo y
su `dist` lleva Créditos a medias. No sobre `npm run dev`: el HMR corrompe estas medidas.

| Medida | Valor |
|---|---|
| Ventana del workspace | 1412 × 748 |
| `scrollHeight` vs `clientHeight` | 748 vs 748 — **sin scroll interno** |
| Extremo derecho del texto (medido con `Range`) | **x = 320** |
| **Ancho muerto al canto derecho** | **1106px — el 78% de la ventana** |
| Alto muerto abajo | 126px |
| `.hero-kick` («Contacto») | 11px |
| **`.contacto-title` («Hablemos»)** | **16px** |
| `.contacto-lead` («Cuéntame tu idea.») | 20px |
| `.contacto-bar-value` (el correo, el teléfono…) | 20px |
| Canales de contacto | 4, los cuatro enlaces reales y visibles |
| Errores de consola | 0 |

### El hallazgo que manda

**La jerarquía está invertida, y no de opinión: de medida.** El titular de cierre del portfolio
—«Hablemos», la llamada a la acción de toda la página— se pinta a **16px**, más pequeño que su
propio subtítulo (20px) y que los valores de contacto (20px). Es el segundo texto más pequeño de la
escena, solo por encima de los rótulos de 11-12px.

La causa está localizada: `.contacto-title` lleva la clase `display-xl`, y en `src/themes/themes.css`
**`display-xl` solo tiene reglas para `:root[data-theme="hyprland"]`**. Bajo Caelestia no lo
dimensiona nadie y cae al tamaño base heredado. No es una decisión de diseño que revisar: es un token
que nunca llegó a esta escena.

**Ojo con cómo se mide esto.** El primer intento dio «ancho muerto 0», porque midió cajas de bloque y
la sección es a sangre. El número real —1106px, el 78%— sale de recorrer los nodos de texto con
`document.createRange()` + `selectNodeContents()`. Es la misma trampa que ya se pagó en B1 y B2: **un
`<span>` de bloque devuelve el ancho del contenedor, no el del texto.**

### Los otros tres

2. **1106px muertos, el 78% de la ventana.** Todo el contenido vive en una columna de 320px pegada al
   canto izquierdo. Es, con diferencia, la peor ocupación de las cinco escenas: Créditos deja 424px
   (30%) y eso ya se consideró un defecto en B4.
3. **La escena no tiene entrada.** `caelestia.choreography.ts` monta Título (B1) y la Ficha (B2); para
   `contacto` **no monta nada**. Es la única de las cinco sin gesto propio al activarse su workspace.
4. **Las cuatro barras son una lista plana rótulo/valor** — el mismo Material plano que se está
   corrigiendo en B4. Aquí pesa más, porque son solo cuatro filas en 748px de alto.

### Lo que ya funciona y no se toca

- **Los cuatro canales son enlaces reales y accionables**: `mailto:`, `tel:` con el número limpio de
  espacios (el marcador del móvil no los tolera), y los externos con `target="_blank"` **y
  `rel="noopener noreferrer"`**. Eso es requisito de seguridad del repo: se conserva tal cual.
- **El dato se lee siempre, sin hover.** Está escrito en `contacto.ts` como decisión explícita: en
  táctil no hay hover y el correo no puede depender de él. **No lo escondas detrás de una
  interacción.**
- **Sin scroll interno.** Ya cumple la ley de la fase A. No lo rompas.
- **El DOM lo comparten los tres temas** (`src/sections/contacto.ts`, 51 líneas) y la piel la decide
  el CSS colgado de `[data-theme]`, nunca una rama en el TS. Respeta ese contrato.

---

## Lo que NO puede ser

1. **No la carta de ajuste de Vice.** El contacto de Vice ya es *la carta de ajuste*
   (`2026-07-30-contacto-carta-de-ajuste-design.md`): cuatro barras a sangre como gelatinas
   translúcidas. **Vice está cerrado y no se toca.**
2. **No la cinta de Hyprland.** El contacto de Hyprland ya tiene su dispositivo
   (`2026-08-13-hyprland-contacto-cinta-design.md`). Léelo **para no repetirlo**, igual que B3 leyó el
   cartel y B4 el catastro. Esta es la tercera vez que la misma sección se resuelve en un tema
   distinto: el listón de originalidad es más alto aquí, no más bajo.
3. **No una terminal tecleada.** B1 teclea `whoami`, B2 es `neofetch` entero. Sería la tercera.
4. **No esconder el dato tras un hover** (ver arriba), **ni introducir scroll interno.**

---

## La metáfora de partida

Cada escena es una aplicación: Título el escritorio desnudo, Quién soy la ficha del sistema, Obra el
gestor de archivos, Créditos el gestor de paquetes, y **Fundido el redactor de mensajes** — la
ventana de composición que queda abierta cuando el escritorio termina de presentarse.

Encaja con los cuatro hallazgos: un redactor **tiene un campo grande que domina la ventana** (los
1106px muertos y el titular de 16px), **tiene cabecera con destinatarios** (los cuatro canales), y
**tiene un gesto de apertura** natural (la ventana que se abre, hallazgo 3).

**Pero la metáfora no es la maqueta.** Un redactor de correo de verdad es un formulario gris, que es
justo el Material plano del hallazgo 4 — y **este sitio no tiene backend**, así que un formulario que
finge enviar sería mentir. La desviación es lo que hace propia la escena, como el nombre en Fraunces
fue la de B2. Decídela en M2 y déjala escrita en el spec como su tesis.

### La tensión del nombre, para resolver en el spec

La escena se llama **«Fundido»** —el cierre de una película— pero su `blurb` en `content.ts` es
**«Contacto»**, y ese campo existe, literalmente, porque *«Fundido» no comunica «contacto» a quien
llega de fuera*. La escena arrastra las dos identidades a la vez. **Di en el spec cuál manda en
Caelestia** y por qué; no lo dejes implícito, que es como lleva desde julio.

---

## Las maquetas

Todas con `/frontend-design:frontend-design`, todas en el companion, ninguna como artifact.

- **M1 — El diagnóstico.** Reproduce las medidas de arriba y enséñale a Aoshi el punto de partida:
  el titular de 16px contra su lead de 20, los 1106px muertos marcados, la escena sin entrada.
  **Antes de proponer nada.**
- **M2 — Tres composiciones**, las tres con los 1412×748 llenos de verdad. Recomienda una: con los
  números delante, Aoshi quiere criterio, no menú.
- **M3 — La escala tipográfica del cierre.** Cuánto mide «Hablemos» y con qué eje de Fraunces.
  Recuerda los dos tokens de B1: `--cae-display-axes-cartel` (`opsz 144`) para lo grande,
  `--cae-display-axes` (`opsz 9`) para 15-30px. **Nunca se reutiliza uno por el otro.** Y la escala se
  escalona en pasos discretos: una función continua sobre tokens es deuda que ya recurre en el repo.
- **M4 — Los cuatro canales.** Que dejen de ser una lista plana sin esconder el dato ni perder
  `mailto:`/`tel:`/`rel`.
- **M5 — El gesto de cierre.** Es la última escena del sitio: qué pasa cuando el visitante llega.
  Vivo, con **Repetir** y deslizador de **velocidad**.
- **M6 — La entrada de escena**, que hoy no existe. Sin terminal (veto 3), y con su degradación bajo
  `prefers-reduced-motion`.
- **M7 — Las 24 horas.** La escena a las 09:00 y a las 03:00 con el deslizador de hora, y el contraste
  de los cuatro enlaces en los dos esquemas.
- **M8 — Móvil.** A 390px. B1, B2 y B3 lo dejaron fuera de alcance a propósito. **B5 es la escena del
  contacto**: si hay una donde el móvil importa de verdad es esta, porque `tel:` y `mailto:` son
  gestos de teléfono. **Decídelo explícitamente en el spec**, no por omisión.

---

## Los gates de `scripts/measure-caelestia-fundido.py`

Ocho familias. **Ninguna se acepta sin haberla visto dar rojo contra el fallo exacto que dice cazar**
— en la fase A ocho veces el fallo estuvo en el instrumento, y en B2 se cazaron seis gates tautológicos.

1. **La jerarquía no está invertida**: el titular mide estrictamente más que su lead y que los valores
   de contacto. Es el fallo medido hoy (16 < 20).
2. **La ocupación**: extremo derecho del texto **medido con `Range`**, no con cajas de bloque — con
   cajas, hoy da «0px muertos» y el gate pasaría en falso sobre un 78% vacío. Fija el umbral tras M2.
3. **Sin scroll interno**: `scrollHeight === clientHeight`. Hoy cumple; el gate existe para que siga.
4. **Los cuatro canales siguen accionables**: `mailto:` bien formado, `tel:` sin espacios ni guiones,
   y los externos con `rel="noopener noreferrer"`. Requisito de seguridad, no de diseño.
5. **El dato se lee sin hover**: comprobar el valor visible **sin** disparar `:hover`. Cuidado: un
   `MouseEvent` sintético **no dispara `:hover`** — trampa ya pagada en B2.
6. **Contraste AA en los dos esquemas** barriendo las 24 horas, midiendo **lo que se pinta de verdad**
   (texto sobre el fondo real del panel, no los roles `on-X`/`X`: vigilar solo esos dejó al reloj bajo
   AA cuatro horas al día con el arnés en verde).
7. **`prefers-reduced-motion` salta la entrada** y deja la escena aterrizada. El selector universal
   `*` **no alcanza a los pseudo-elementos**: si algún `::before` anima, necesita su propia regla.
8. **Vice y Hyprland no se alteran**: su escena `contacto` sigue igual. `contacto.ts` es compartido.

---

## Entregables

1. Las ocho maquetas en el companion, aprobadas por Aoshi.
2. `docs/superpowers/specs/2026-09-04-caelestia-fundido-design.md`, con la tesis de la escena, la
   resolución de la tensión «Fundido»/«Contacto» y el registro de qué rompía cada gate antes de
   aceptarlo.
3. `docs/superpowers/plans/2026-09-04-caelestia-fundido.md` con `superpowers:writing-plans`.
4. `scripts/measure-caelestia-fundido.py` y su fila en la tabla de `.claude/rules/verification.md`.
5. **Rescatar al repo lo aprobado que viva en el companion**: `.superpowers/` está en `.gitignore`
   (línea 47) y lo que se quede ahí se pierde.

## Estado al escribir esto

- B5 **no está bloqueada por nada**: el dato de `contactChannels` está completo y no necesita material
  de Aoshi. Es la fase que cierra Caelestia.
- **B4 está en implementación en paralelo** (`design/caelestia-creditos-b4`). B5 no toca sus ficheros,
  pero **las dos escriben en el bloque `:root[data-theme="caelestia"]` de `themes.css`**: cuenta con
  resolver conflictos ahí y no midas contra el `dist` de esa sesión.
- Los dos `CLAUDE.md` todavía no mencionan B3 ni B4; el texto verificado de B3 está en `.ai/memory.md`
  para pegarlo al principio de una sesión, no a media.
