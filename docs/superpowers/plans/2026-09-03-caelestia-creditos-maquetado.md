# Caelestia B4 — Créditos: plan de maquetado

> **Esto NO es un plan de implementación.** Es la agenda de diseño de la fase B4: qué maquetas hay
> que construir en el companion, en qué orden y contra qué medirlas, para poder escribir después el
> spec y el plan. B4 **no tiene spec todavía**, y por eso no puede tener plan de implementación:
> planificar trabajo sin diseñar es lo que dejó en este repo planes con 86 y 57 casillas sin marcar.

Fecha: 2026-09-03
Fase: **B4** de seis. Las tres anteriores dentro de la ventana:
`2026-08-26-caelestia-titulo` (B1, fusionada), `2026-09-02-caelestia-quien-soy` (B2, fusionada),
`2026-09-03-caelestia-obra` (B3, fusionada, `en ejecucion` a la espera de las capturas reales).

---

## El diagnóstico, medido

Medido el 2026-09-03 sobre el **build de producción** servido con `vite preview`, tema
`?theme=caelestia`, workspace 4 activo. No sobre `npm run dev`: el HMR corrompe estas medidas.

| Medida | Valor |
|---|---|
| Ventana del workspace | 1412 × 748 (barra 44px arriba, dock abajo, borde inferior en y816) |
| `#creditos` `scrollHeight` vs `clientHeight` | **758 vs 748** — 10px de scroll interno |
| `overflow-y` computado | `auto` |
| Ancho de los dos paneles pintados | 62 → 1002 = **940px** |
| **Ancho muerto al canto derecho** | **424px, el 30% de la ventana** |
| Rótulos de grupo en el DOM (`.credit-group-label`) | 4 |
| **Rótulos de grupo visibles bajo Caelestia** | **0** |
| Tecnologías pintadas | 23, en **una sola parrilla plana** |
| Alto del panel de detalle | 371px para ~4 líneas de contenido (caso React) |
| Errores de consola | 0 |

**Esto NO es lo que era B3.** Obra estaba estructuralmente rota (4964px en una ventana de 748,
cuatro de cinco proyectos inalcanzables). Créditos **funciona**: se ve entero, no tiene errores, el
cruce "Aparece en" resuelve. Los problemas son de composición y de jerarquía, no de que la escena
no quepa. Dimensiona el trabajo a eso y no reescribas lo que ya sirve.

### Los tres hallazgos que mandan

1. **La escena tira la estructura que el dato sí tiene.** `content.ts` agrupa las 23 tecnologías en
   cuatro bloques con rótulo — *Interfaz* (8), *Backend y datos* (5), *Lenguajes base* (5),
   *Herramientas* (5) — y `credits.ts` **emite los cuatro rótulos**. Medido: **ninguno se pinta bajo
   Caelestia**. El visitante ve 23 pastillas indiferenciadas donde el dato dice que hay cuatro
   territorios. No hay que inventar el agrupamiento: hay que dejar de tirarlo.

2. **424px muertos al canto derecho.** El mismo mal que tenía Obra. Los dos paneles se quedan en
   940px dentro de una ventana de 1412 y el tercio derecho está vacío. Aquí hay sitio de sobra para
   que el detalle conviva con la lista en vez de colgar debajo.

3. **La parrilla de pastillas es exactamente el Material plano que Aoshi ya rechazó una vez.**
   Consta: prefiere estilo editorial —Fraunces itálica, tarjetas tipo revista— sobre listas y
   parrillas grises. Este es el sitio del proyecto donde más se nota, porque es la única escena que
   sigue siendo una lista de etiquetas.

### Lo que ya funciona y no se toca

- **El cruce "Aparece en".** Cada tecnología sabe en qué proyectos aparece, cruzando `stack` y
  `tooling` de `caseStudies`. Es el mejor activo de la escena: **ata Créditos con Obra**, y es un
  dato derivado real, no un adorno. Sea cual sea la composición nueva, esto sobrevive.
- **El DOM compartido.** `src/components/credits.ts` (619 líneas) lo usan los tres temas y la
  presentación la decide el CSS colgado de `[data-theme]`, nunca una rama en el TS. **Respeta ese
  contrato.** Si crees que hay que tocar `credits.ts`, dilo explícitamente en el spec y verifica
  Vice —que está **cerrado**— y Hyprland antes de proponerlo.
- **El recuento por grupo es derivado** (`group.items.length`), no un campo nuevo. No lo conviertas
  en dato.

---

## Lo que NO puede ser

Tres vetos duros. Se anotan aquí para no gastar una maqueta en descubrirlos.

1. **No el catastro de Hyprland.** «Con qué construyo» en Hyprland ya es *el catastro*: un reparto de
   territorio (`2026-08-10-hyprland-stack-catastro-design.md`, `Estado: implementado`, en la rama
   `worktree-hyprland-stack-catastro`, **sin fusionar a `main`**). Léelo **para no repetirlo**, igual
   que B3 leyó el cartel de obra para vetarlo. Dos temas no pueden resolver la misma sección con el
   mismo dispositivo.
2. **No una tercera terminal tecleada.** B1 teclea `whoami`. B2 es `neofetch` entero, con el prompt
   devuelto. Un gestor de paquetes pide a gritos un `pacman -Q` tecleado y **por eso mismo está
   vetado**: sería el tercer comando escrito en pantalla en cuatro escenas y el recurso dejaría de
   significar nada. El vocabulario de terminal puede seguir presente; **la entrada de la escena tiene
   que ser otro gesto.**
3. **No un scroll interno, ni de 10px.** La ley de la fase A: un espacio de trabajo no se desplaza,
   se cambia. Los 10px de hoy son un defecto, no una tolerancia.

---

## La metáfora de partida

La decisión que gobierna las cinco escenas: **cada una es una aplicación.** Título es el escritorio
desnudo, Quién soy la ficha del sistema, Obra el gestor de archivos, y **Créditos el gestor de
paquetes** — la aplicación que dice qué hay instalado en esta máquina, agrupado por origen, con lo
que depende de cada cosa.

Encaja sola con los tres hallazgos: un gestor de paquetes **agrupa por repositorio** (los cuatro
rótulos que hoy se tiran), **enseña detalle al lado de la lista** (los 424px muertos), y **"Aparece
en" es literalmente la lista de dependencias inversas** — qué tiene instalado esto por dentro. No
hay que forzar nada.

**Pero la metáfora no es la maqueta.** Un gestor de paquetes de verdad es una tabla gris, que es el
Material plano del hallazgo 3. **La desviación es lo que hace propia la escena**, igual que en B2 el
nombre era lo único fuera de la monoespaciada. Decide en M2 cuál es la desviación aquí y déjala
escrita en el spec como su tesis.

---

## Las maquetas

Todas con `/frontend-design:frontend-design`, todas en el companion, ninguna como artifact.

- **M1 — El diagnóstico.** Reproduce las medidas de arriba sobre el build de producción y enséñale a
  Aoshi el punto de partida: los 424px muertos marcados, los cuatro rótulos que existen y no se ven,
  los 10px de scroll. **Antes de proponer nada.**
- **M2 — Tres composiciones.** Maestro-detalle a dos columnas (lista agrupada a la izquierda, ficha
  fija a la derecha, que come los 424px); cuatro columnas, una por territorio; y una tercera que
  propongas tú. Cada una con los 23 nombres reales y los cuatro rótulos. Recomienda una: con los
  números delante, Aoshi quiere criterio, no menú.
- **M3 — La desviación editorial.** La composición ganadora, resuelta dos veces: una fiel al gestor
  de paquetes y otra con el giro editorial (Fraunces itálica, jerarquía de revista). Es **la decisión
  central de la fase** y la que contesta el hallazgo 3.
- **M4 — El detalle y el cruce.** La ficha de una tecnología con su `detail` y su "Aparece en".
  Pruébala contra los dos extremos reales: **React** (2 proyectos) y una que **no aparezca en
  ninguno** — el panel no puede quedar vacío ni mentir.
- **M5 — El gesto de selección.** Vivo, con ratón, botón de Repetir y deslizador de velocidad. Cómo
  se pasa de una tecnología a otra sin que la ficha salte.
- **M6 — La entrada de escena.** Sin terminal tecleada (veto 2). Qué hace la escena al activarse su
  workspace, y cómo se degrada con `prefers-reduced-motion`.
- **M7 — Las 24 horas.** La escena a las 09:00 y a las 03:00 con el deslizador de hora. Los 23 chips
  llevan **iconos de marca con color propio** (`slug` de simple-icons): son colores ajenos a la rueda
  OkLCH, el mismo problema que las capturas en B3. Decide la regla de tratamiento.
- **M8 — Móvil.** A 390px. B1 y B2 lo dejaron fuera de alcance a propósito; **di explícitamente en el
  spec si B4 hace lo mismo o no**, no lo dejes implícito.

---

## Los gates de `scripts/measure-caelestia-creditos.py`

Ocho familias. **Ninguna se acepta sin haberla visto dar rojo contra el fallo exacto que dice cazar**
— en la fase A ocho veces el fallo estuvo en el instrumento, no en el diseño, y en B2 se cazaron seis
gates tautológicos.

1. **Sin scroll interno**: `scrollHeight === clientHeight` en la escena. Es el fallo medido hoy.
2. **Los cuatro rótulos de grupo se pintan**: contar los visibles con `getClientRects().length > 0`,
   no los del DOM — hoy hay 4 en el DOM y 0 visibles, y un gate que contara nodos pasaría en falso.
3. **El ancho muerto baja del 30%**: medir el canto derecho del bloque pintado contra el de la
   ventana. Fija el umbral **después** de M2, contra la composición elegida.
4. **Las 23 tecnologías están, y son literales de `content.ts`**: ni una inventada, ni un `detail`
   reescrito. Regla anti-mock del repo.
5. **"Aparece en" cruza de verdad**: para una tecnología con proyectos, los que salen son los que
   dice `caseStudies`; para una sin ninguno, el panel dice algo honesto y no queda vacío.
6. **Contraste AA en los dos esquemas**, barriendo las 24 horas, **midiendo lo que se pinta de
   verdad** (texto sobre el fondo real del panel, no los roles `on-X`/`X` — vigilar solo esos dejó al
   reloj bajo AA cuatro horas al día con el arnés en verde).
7. **`prefers-reduced-motion` salta la entrada** y deja la escena en su estado aterrizado. Ojo: el
   selector universal `*` **no alcanza a los pseudo-elementos** — si algún `::before` anima, necesita
   su propia regla, que es la trampa que se pagó en B2.
8. **Vice y Hyprland no se alteran**: la escena `credits` de los otros dos temas sigue como estaba.
   `credits.ts` es compartido.

---

## Entregables

1. Las ocho maquetas en el companion, aprobadas por Aoshi.
2. `docs/superpowers/specs/2026-09-03-caelestia-creditos-design.md`, con la tesis de la escena, la
   desviación de M3 y el registro de qué rompía cada gate antes de aceptarlo.
3. `docs/superpowers/plans/2026-09-03-caelestia-creditos.md` con `superpowers:writing-plans`.
4. `scripts/measure-caelestia-creditos.py` y su fila en la tabla de `.claude/rules/verification.md`.
5. **Rescatar al repo lo aprobado que viva en el companion**: `.superpowers/` está en `.gitignore`
   (línea 47) y lo que se quede ahí se pierde.

## Estado al escribir esto

- B4 **no está bloqueada por nada**. A diferencia de B3, no depende de las nueve capturas de Aoshi:
  los 23 iconos de marca ya existen y el dato está completo en `content.ts`.
- `npm run build`, `npm run lint` y `scripts/verify.py` están en verde a 2026-09-03.
- Los dos `CLAUDE.md` **todavía no mencionan B3**; el texto verificado está en `.ai/memory.md` para
  pegarlo al principio de una sesión, no a media.
