# Spec de Caelestia — Fundido: la contraportada del escritorio

Estado: disenado, sin implementar
Fecha: 2026-09-04
Agenda de maquetado: `docs/superpowers/plans/2026-09-04-caelestia-fundido-maquetado.md`
Plan de implementacion: pendiente — `docs/superpowers/plans/2026-09-04-caelestia-fundido.md`
Alcance: la **fase B5**, ultima de las seis del rediseno de Caelestia y la que lo cierra. La escena
`#contacto` dentro del workspace 5. Toca el bloque `:root[data-theme="caelestia"]` de
`src/themes/themes.css`, anade un modulo de coreografia propio para la escena y **no toca
`src/sections/contacto.ts`** salvo para las envolturas minimas que el maquetado necesite — ese DOM
lo comparten los tres temas y la piel la decide el CSS colgado de `[data-theme]`, nunca una rama en
el TS.

**Vice no se toca** (cerrado el 2026-08-05): su contacto ya es la carta de ajuste
(`2026-07-30-contacto-carta-de-ajuste-design.md`). **Hyprland no se toca**: su contacto ya tiene su
dispositivo (`2026-08-13-hyprland-contacto-cinta-design.md`), leido aqui **para no repetirlo**. La
fase A (shell), B1 (Titulo) y B2 (Quien soy) estan cerradas y no se tocan; B3 (Obra) esta en
ejecucion y B4 (Creditos) en implementacion en otra rama — **las dos escriben en el mismo bloque de
`themes.css` que B5**, asi que hay que contar con conflictos ahi.

Maquetas vivas, en el companion, pendientes de rescatar al repo: `01-diagnostico` … `16-movil`.
**`.superpowers/` esta en `.gitignore` (linea 47): lo que se quede ahi se pierde.**

---

## Por que

Medido el 2026-09-04 sobre un **build de produccion** (`npm run build && npx vite preview`,
`?theme=caelestia`, workspace 5 activo), en la ventana de **1412 × 748** que impone el carril de
workspaces, y a **390 × 844** con viewport tactil de verdad:

| | 1440 × 900 | 390 × 844 |
|---|---|---|
| ventana del workspace | 1412 × 748 | 362 × 692 |
| `scrollHeight` vs `clientHeight` | 748 = 748 — sin scroll | 692 = 692 — sin scroll |
| extremo derecho del texto, medido con `Range` | x = 320 | x = 320 |
| **ancho muerto al canto derecho** | **1106 px — el 78 %** | 56 px — el 15 % |
| `.hero-kick` («Contacto») | 10,56 px | 10,56 px |
| **`.contacto-title` («Hablemos»)** | **16 px** | **16 px** |
| `.contacto-lead` («Cuentame tu idea.») | 20 px | 20 px |
| `.contacto-bar-value` | 20 px | 20 px |
| area accionable por canal | 1412 × 98 | 362 × 98 |
| errores de consola | 0 | 0 |

### El hallazgo que manda

**La jerarquia esta invertida, y no de opinion: de medida.** El titular de cierre del portfolio —la
llamada a la accion de toda la pagina— se pinta a **16 px**, mas pequeno que su propio subtitulo
(20 px) y que los valores de contacto (20 px). Es el segundo texto mas pequeno de la escena.

La causa esta localizada: `.contacto-title` lleva la clase `display-xl`, y en `themes.css`
**`display-xl` solo tiene reglas para `:root[data-theme="hyprland"]`**. Bajo Caelestia no lo
dimensiona nadie y cae al tamano base heredado. No es una decision de diseno que revisar: es un
token que nunca llego a esta escena.

Y el defecto es **doble**. Ademas del tamano, «Hablemos» se pinta con `--cae-display-axes`, que es
`opsz 9`: el dibujo de TEXTO de Fraunces, ampliado. En Fraunces `opsz` no es estilo — la fuente trae
dibujos distintos segun el tamano al que se vaya a leer. `opsz 9` engorda las finas para que
sobrevivan a 15 px; ampliado sale romo y sin contraste de trazo.

### Los otros cuatro

2. **1106 px muertos, el 78 % de la ventana**, en escritorio. Todo el contenido vive en una columna
   de 320 px pegada al canto izquierdo. Es la peor ocupacion de las cinco escenas.
3. **La escena no tiene entrada.** `caelestia.choreography.ts` monta Titulo y la Ficha; para
   `contacto` **no monta nada**. Es la unica de las cinco sin gesto propio al activarse su workspace.
4. **Las cuatro barras son una lista plana rotulo/valor** — el mismo Material plano que se esta
   corrigiendo en B4.
5. **La escena no tiene tipografia adaptable**: ni un solo tamano cambia entre 390 y 1440. La
   jerarquia invertida es identica en el telefono.

### Caelestia no tiene una escala tipografica: 14 de sus 16 tamanos no salen de ella

Medido recorriendo **cada nodo que pinta texto** en las cuatro escenas y leyendo su `fontSize`
calculado — no los tokens declarados. El repo declara diez pasos (`--t-1` … `--t-10`, razon 1,333).
Caelestia pinta **16 tamanos distintos** y **solo 2 caen en un paso** (16 y 12). De los otros 14:
**10 son literales sueltos en px** (30, 26, 24, 20, 16,96, 15,2, 14,72, 13, 12,8, 10,56) y **4 los
calcula JS** al justificar el titular de B1, asi que no son elegibles por token.

Hallazgo derivado: **el token declarado y el que se usa de verdad no son el mismo.**
`--cae-display-axes` dice `wght 900`, pero B1 y B2 escriben `"opsz" 9, "wght" 700, "SOFT" 0,
"WONK" 1` a mano en tres reglas (`themes.css` 3949, 3991, 4104). Nadie usa el token.

### Lo que ya funciona y no se toca

- **Los cuatro canales son enlaces reales y accionables**: `mailto:`, `tel:` con el numero limpio de
  espacios, y los externos con `target="_blank"` **y `rel="noopener noreferrer"`**. Requisito de
  seguridad del repo.
- **El dato se lee siempre, sin hover.** Decision explicita escrita en `contacto.ts`: en tactil no
  hay hover y el correo no puede depender de el.
- **Sin scroll interno**, en los dos anchos. Ya cumple la ley de la fase A.
- **Las areas accionables de 98 px de alto.** Son lo mejor que tiene el diseno actual y es en el
  telefono donde se justifican. El rediseno no las tira.

---

## La tesis: la contraportada

Cada escena es una aplicacion —Titulo el escritorio desnudo, Quien soy la ficha del sistema, Obra el
gestor de archivos, Creditos el gestor de paquetes— y **Fundido es la contraportada del libro**: la
ultima pagina, donde el color se invierte y solo quedan la frase y el pie de imprenta.

La agenda proponia «el redactor de mensajes». Se descarto tras cuatro rondas de maquetas: un
redactor de correo de verdad es un formulario gris, que es justo el Material plano del hallazgo 4,
y **este sitio no tiene backend**, asi que un formulario que finge enviar seria mentir.

**Fundido es la unica de las cinco escenas que invierte a un campo de color.** Las otras cuatro son
ventanas de aplicacion sobre el escritorio; esta es una superficie `--cae-primary` a sangre con el
texto en `--cae-on-primary`. Eso es lo que la hace legible como final sin necesitar que nadie lo
explique.

Y dentro de ese campo hay **un troquel**: una figura de Material 3 recortada sobre el fondo
generativo del escritorio, como el hueco de una contraportada por el que se ve la guarda.

### La tension del nombre, resuelta

La escena se llama **«Fundido»** en `sceneIndex` y su `blurb` es **«Contacto»**; el campo existe
literalmente porque «Fundido» no comunica «contacto» a quien llega de fuera.

**En Caelestia manda «Fundido», y el gesto lo justifica.** El fundido es una transicion de cine y la
escena hace una: el campo de color inunda la ventana desde el troquel. El nombre deja de ser una
etiqueta poetica y pasa a describir lo que se ve.

**«Contacto» no desaparece**: sigue siendo el `blurb`, sigue siendo lo que lee un lector de
pantalla en el indice de escenas, y los rotulos del colofon son verbos explicitos —«Escribeme»,
«Llamame»— que no dependen del nombre de la escena para decir que hacen.

**Lo que el spec fija:** el rotulo visible de la pastilla del workspace sigue siendo «Fundido»; el
`blurb` sigue siendo «Contacto»; **ninguno de los dos se renombra en B5.** Lo que cambia es que el
nombre pasa a estar ganado.

---

## Composicion

Elegida en M2d como **K · La contraportada**, tras descartar tres rondas anteriores (A/B/C
disposiciones de la misma idea, D/E/F/G dispositivos, H/I/J familia). Las descartadas eran
disposiciones de informacion, no composiciones: sin cursiva, sin figura, sin solape.

```
┌──────────────────────────────────────────────────────────────┐  ventana 1412 × 748
│ FUNDIDO                          AOSHI BLANCO SANZ · CARACAS │  corn, 10 px, filete
│ ──────────────────────────────────────────────────────────── │
│                                                              │
│   Cuéntame                                    ╭─────────╮    │  frase --t-10 (159,66)
│   tu idea.                                    │ troquel │    │  italic, SOFT 100
│                                               ╰─────────╯    │  460 px, sangra al canto
│ ──────────────────────────────────────────────────────────── │
│ ESCRÍBEME              LLÁMAME        LINKEDIN ·  GITHUB     │  el pie de imprenta
│ a.blanco1501@…         +58 424 …      Aoshi B.S.  Aoshi346   │
│ ● DISPONIBLE PARA PROYECTOS                                  │
└──────────────────────────────────────────────────────────────┘
```

### La escala del cierre (M3)

| rol | token | valor | ejes |
|---|---|---|---|
| la frase | `--t-10` | 159,66 px | **`--cae-display-axes-cierre`** (nuevo) |
| valor del acto | `--t-4` | 28,43 px | Hanken Grotesk |
| valor del destino | `--t-2` | 16 px | Hanken Grotesk |
| rotulos, corn, pie | — | 9–10 px | Martian Mono |

**`--t-10` no sale a ojo.** La linea larga mide 530 px sobre un hueco libre de 858 (derivado del
relleno real, no copiado), asi que el techo no lo pone el troquel. Lo decide la ocupacion: a
`--t-8` la frase flota en el campo de color y el hallazgo 2 sigue medio sin contestar; a `--t-10`
el texto y el troquel se equilibran, 530 contra 460. Razon contra el colofon: **9,98×**.

**Nada de `clamp()` ni de `vw` en la escala.** Regla dura del repo: una funcion continua sobre
tokens devuelve cualquier real entre sus topes y se esconde justo en 390 y 1440. El salto a movil
es un paso discreto en un `@media`, lo que permite que el arnes exija un valor exacto en vez de un
rango.

**Y nada de justificar por JS como B1.** Alli las tres lineas tenian que medir lo mismo; aqui son
dos lineas que no se justifican. Traer el ajustador seria traer sus tres trampas sin necesitar
ninguna.

### Los cuatro tokens de ejes

| token | ejes | quien |
|---|---|---|
| `--cae-display-axes` | `opsz 9 · wght 900` | **se queda como esta**, es de la fase A. El spec deja escrito que **hoy no lo usa nadie**. |
| `--cae-display-axes-cartel` | `opsz 144 · wght 900` | B1 y B2. **Fundido no lo usa**: su cierre no es otra cabecera. |
| **`--cae-display-axes-texto`** | `opsz 9 · wght 700` | **Nuevo, y no inventa nada**: pone nombre al literal ya escrito tres veces. Es la deuda que el spec de B1 anoto. Renombrar no cambia un pixel — verificable comparando capturas antes y despues. |
| **`--cae-display-axes-cierre`** | `italic · opsz 144 · wght 300 · SOFT 100 · WONK 1` | **Nuevo, y es la tesis tipografica de B5.** Cuarta voz, en **un solo sitio de todo el sitio**: la frase de cierre. Si se usara en dos, deja de significar «esto se acaba». |

### Los cuatro canales (M4)

**Disposicion B · el pie de imprenta.** Los cuatro canales no son intercambiables y el propio diseno
ya lo contradecia: cuando cae la red, LinkedIn y GitHub se tachan y el correo y el telefono siguen
sirviendo. **Dos son actos** (`mailto:` y `tel:` disparan una aplicacion del aparato) y **dos son
destinos** (abren pestana, necesitan internet).

- Los dos actos, grandes, a la izquierda: **85 px de alto**.
- Los dos destinos, pequenos, al canto derecho: **42 px**.
- El tamano del blanco va con la importancia del canal, en vez de repartirse a partes iguales.

**No se recomienda por el suelo de WCAG 2.5.8**: las tres disposiciones probadas lo pasan (la de
cuatro columnas tiene incluso las areas mas grandes, 307×43 las cuatro) y aun asi es la peor,
porque reparte el mismo peso a lo que no pesa lo mismo.

Descartado **C · el renglon** (el colofon escrito como una frase): compite con el titular —dos
frases seguidas en la misma pantalla— y tiene un defecto que solo aparece al medir: el enlace de
LinkedIn **parte en dos renglones**, asi que su area accionable esta partida y su rect miente
(declara 1067 × 83 px cubriendo un hueco que no es pulsable) y el anillo de foco sale igual de
partido.

---

## El troquel y lo que hay dentro

El troquel es una **figura de Material 3** generada con las mismas formulas de B2 (`armonica(n,a,s)`
y `superelipse(pot)`, **240 puntos**), recortando el fondo generativo del escritorio sobre el campo
de color.

Dentro va **el dino de Chrome**, quieto, con su horizonte y dos nubes.

### Procedencia del sprite — leer antes de implementar

- **Origen**: `components/neterror/resources/images/default_100_percent/offline/100-offline-sprite.png`
  del arbol de Chromium. Hoja de 1233 × 100. Piezas usadas: dino de pie `x=848`, zancada 1 `x=936`,
  zancada 2 `x=980`, nube `x=86` (46 × 14), horizonte `x=2 y=54` (600 × 12).
- **Licencia**: el codigo de Chromium es BSD-3-Clause. **La marca no**: el dino es un activo
  identificable de un producto de Google. Usarlo en un portfolio personal es un riesgo de marca, no
  de licencia.
- **Decision**: es de Aoshi, tomada **despues de advertirlo dos veces** en la sesion de maquetado.
  Queda registrada aqui a proposito, para que quien lo lea dentro de un ano sepa que fue una
  eleccion y no un descuido. La atribucion tiene que aparecer en el codigo (comentario en el modulo
  que inyecta el sprite) y **la implementacion debe dejar el bicho detras de un unico modulo**, para
  que quitarlo sea borrar un fichero y una regla, no una cirugia.

### Dos trampas del sprite, ya pagadas

1. **El hueco del ojo se tapa al extraer el fotograma de pie.** Ahi va encima un `rect` movible —el
   bicho te mira— y si se deja el hueco original, el hueco y el `rect` se suman y **el ojo se ve
   doble** en cuanto se mueve. En los fotogramas de zancada **no** se tapa: ahi no hay `rect`, y el
   hueco del sprite ES el ojo.
2. **Los tres fotogramas van en el mismo lienzo**, pegados abajo y a la derecha. Sus cajas no miden
   igual (las piernas se mueven) y sin igualarlas **la cabeza pega un tiron lateral en cada
   zancada**. El lienzo comun medido es 40 × 43 y el ojo cae en (24, 3).

### La nube y el horizonte

Quietos al aterrizar. **El spec de Hyprland prohibe la animacion infinita en la escena de cierre**
con todas las letras («no descansa nunca y no informa de nada»); entrar es un gesto, desplazarse
seria animacion infinita. Tampoco hay cactus: un cactus promete el juego, y el juego pide teclado,
colisiones y puntuacion.

---

## El fundido (M5): suena una vez

Caelestia no tiene scroll: las cinco escenas son escritorios que se conmutan. Eso parte el gesto en
dos, y **la regla ya estaba escrita en `caelestia.choreography.ts`**: la ficha de «Quien soy» se
reproduce solo al ENTRAR en su workspace y solo si vienes de otro — *«no vuelves a abrir la
aplicacion en la que ya estas»*. B5 la hereda tal cual.

> **El fundido suena la primera vez que se llega al workspace 5. La entrada suena todas.**

Un final de 1,9 s reproducido en la quinta visita deja de ser un final y pasa a ser un peaje.

### La partitura — 7 gestos, 1900 ms

Los tiempos salen de la propia linea de tiempo (ver `## Trampas`, punto 1), no de una tabla escrita
a mano:

| | ms | gesto |
|---|---|---|
| 1 | 0–480 | el campo de color inunda la ventana **desde el troquel** |
| 2 | 380–900 | el troquel se abre **dentro de si mismo** |
| 3 | 520–1300 | la frase se traza linea a linea, y **sus ejes se ablandan** |
| 4 | 740–1900 | dentro: el suelo se traza, el bicho entra corriendo y frena, salen las nubes |
| 5 | 820–1290 | los dos filetes se trazan |
| 6 | 900–1460 | los dos actos se trazan |
| 7 | 1160–1670 | los dos destinos, despues |

**Un solo mecanismo en dos direcciones.** Los gestos 1 y 2 son la misma figura escalando: una hacia
fuera hasta inundar, otra naciendo dentro. Es un iris de cine, no dos efectos sueltos.

**El factor de crecimiento no es un numero a ojo.** Sale de la distancia del centro de la figura a
la esquina mas lejana de la ventana, dividida entre el **radio minimo** de la figura (los valles,
no las crestas), con un 4 % de margen: **6,34**. Con menos, el lienzo asoma por una esquina.

**Todo lo que aparece se traza de izquierda a derecha** — filetes, suelo del troquel, frase y los
cuatro canales. Un gesto repetido, en vez de tres maneras distintas de aparecer.

**La frase se ablanda al llegar**: entra con la voz de cabecera (`wght 900`, `SOFT 0` — los ejes del
cartel de B1) y aterriza en la voz de cierre (`wght 300`, `SOFT 100`). Medido en la propia linea:
900 → 354 → 300, con `SOFT` 0 → 91 → 100. `opsz` **no se toca**: se lee a 159,66 px de principio a
fin, y `opsz` no es estilo.

**El bicho entra corriendo** — el idioma del propio dino. Dos fotogramas de zancada alternando cada
85 ms, frenando hasta pararse de pie con el mismo aplaste que ya hace al pulsarlo. **El ojo movible
se apaga durante la carrera** y vuelve al pararse.

**La escalonada dice algo**: los dos actos entran antes que los dos destinos, que es exactamente la
jerarquia de M4. Si algun dia se cambia esa jerarquia, esto se cae con ella — y asi debe ser.

**Nada de `gsap.from`**: regla dura del repo, tres regresiones reales. Todo con `fromTo` y los dos
extremos escritos a mano.

### Lo descartado del fundido

- **Un fundido a negro.** Es lo que la palabra pide de primeras y es lo peor: taparia el correo y el
  telefono. El fundido va **al color**, no a negro.
- **Tapar la barra y el dock.** El escritorio es la tesis del tema; hacerlo desaparecer un segundo
  se lee como un fallo, no como cine. El fundido pasa **dentro de la ventana**.
- **Tipografia animada letra a letra.** Con la frase a 159,66 px son dos lineas enormes, y B1 ya
  tiene el trazado de glifos como su gesto.
- **Una tercera terminal tecleada.** Veto de la agenda: B1 teclea `whoami`, B2 es un `neofetch`.

---

## La entrada (M6): suena cada vez

El carril de la fase A ya desliza los escritorios: **520 ms con `power3.inOut`**, y bajo
`prefers-reduced-motion` el mismo `fromTo` con duracion 0. **Eso no lo toca B5.**

Lo que anade B5 son **tres gestos, 440 ms**, que caben dentro de los 520 del deslizamiento: la
entrada termina antes de que el carril pare, asi que **no anade espera, la rellena**.

1. **El contenido se asienta.** El carril mueve el panel; el contenido va 28 px por detras y lo
   alcanza. Un solo tween sobre el envoltorio, no uno por elemento.
2. **El troquel respira**, de 0,965 a 1.
3. **El bicho mira de donde vienes, y parpadea una vez.** La direccion la decide **de que workspace
   llegas** — algo que solo puede tener un carril de escritorios. El parpadeo funciona porque el ojo
   es un hueco *tapado*: apagar el `rect` no lo borra, lo cierra.

**Pulsar la pastilla del workspace activo no dispara nada**, ni cuenta visita. Y `inert` sigue en
todo workspace que no sea el activo, en las dos direcciones.

Descartado: repetir el fundido aunque sea acortado; que el bicho vuelva a entrar corriendo (la
carrera es la llegada, y solo se llega una vez); escalonar los cuatro canales otra vez.

---

## Color y contraste (M7)

Barrido de **288 muestras** (cada 5 min de las 24 h) del motor de `caelestia.color.ts`, midiendo
**los pares tal como estan puestos en la maqueta, opacidades incluidas** — no los roles `on-X`
contra `X` en abstracto, que es la trampa que en la fase A dejo al reloj bajo AA cuatro horas al dia
con el arnes en verde. Instrumento con tres pares de control: 21,00 / 1,00 / 4,54.

| par | peor caso | veredicto |
|---|---|---|
| la frase · `on-primary`/`primary` | **6,30:1** a las 08:45 | AA |
| valor del colofon | 6,30:1 | AA |
| el dino · `on-surface`/`surface` | 14,92:1 | AAA |
| el suelo · `on-surface-variant`/`surface` | 6,36:1 | AA |
| el ojo de noche · `anchor`/`surface` | 14,05:1 | AAA |

**La inversion de noche es segura.** El campo de color no es un problema de accesibilidad: si se
cambia, sera por gusto.

### `--fundido-dim: 0.82` — un numero calibrado contra una superficie

El barrido cazo **dos defectos propios**, de la misma familia que el del diagnostico: rotulos del
colofon a `opacity: .68` daban **3,81:1** y ladillo y pie a `.72` daban **4,08:1**. El suelo esta en
**0,78 → 4,50:1 justo**, sin margen, asi que se sube a **0,82 → 4,80:1**.

Va como token con nombre, **`--fundido-dim`**, y el comentario dice **contra que superficie se
calibro**. Es el patron que el repo exige desde `--nav-dim`, y existe precisamente para que nadie
reutilice el numero sobre otra superficie: una opacidad es un porcentaje de un fondo concreto, y
llevarse el numero es no llevarse nada.

### Dos falsas alarmas que el arnes tiene que saber distinguir

- **Las nubes a 2,19:1.** No son texto ni transmiten informacion: son decorado, y WCAG las exime.
- **El ojo a 1,46:1 de dia.** Ese par **no existe**: de dia el ojo es el hueco, que se pinta en
  `--cae-surface`, no en `--cae-anchor`. El instrumento midio un par que nunca se pinta. Es el mismo
  error que la fase A documenta con los `PARES` que vigilaban roles que nadie pintaba.

Si el arnes final no las distingue, dara rojo para siempre y acabara desactivandose.

---

## Movil: 390 px ENTRA en el alcance (M8)

B1, B2 y B3 dejaron el movil **fuera de alcance a proposito**, y esta escrito en sus specs.

> **B5 no hereda esa exencion. 390 px entra en el alcance de la fase y el arnes lo mide.**

La razon no es de gusto: esta es la escena del contacto, `tel:` abre el marcador y `mailto:` abre el
correo — **son gestos de telefono**. Una escena de contacto que solo funciona en escritorio
contradice lo unico que la escena existe para hacer. Se deja escrito con estas palabras porque **si
se deja implicito, el que venga detras asume la exencion**, que es lo que ha pasado tres veces.

| | escritorio | 390 |
|---|---|---|
| titular | `--t-10` · 159,66 | `--t-8` · 89,85 |
| valor del acto | `--t-4` · 28,43 | `--t-3` · 21,33 |
| valor del destino | `--t-2` · 16 | `--t-2` · 16 |
| los cuatro canales | 2 actos + 2 destinos al canto | 2 actos en fila entera + 2 destinos a mitades |
| el troquel | 460 px, sangrando | **196 px, sello entero** |
| figura del troquel | galleta · 12 lobulos | **sol · 8 lobulos** |
| profundidad del lobulo | 24,9 px | 20,6 px |

**`--t-8` es el paso mas grande que cabe**, no un tamano elegido a ojo: `--t-9` deja «Cuentame» en
398 px sobre una medida util de 322 y se sale; `--t-8` la deja en 299.

**El troquel deja de sangrar.** Sangrar 208 px en una ventana de 362 se come mas de la mitad y lo
que queda no deja completar la figura: se lee como una mancha, no como una forma recortada.

**La figura pierde lobulos al encoger.** Una figura no se lee por su nombre: se lee por la
**profundidad de su lobulo en pixeles**. La galleta cae de 24,9 px a 460 hasta **10,6 px a 196**,
repartidos en doce lobulos de 51 px de arco — a ese tamano no es una figura, es un borde sucio. El
sello de movil usa el mismo generador y la misma malla de 240 puntos con **ocho** lobulos: 20,6 px.
Es como funcionan las figuras de Material 3, y **es una regla nueva del proyecto**: *la complejidad
de la figura baja con el tamano; por debajo de ~12 px de relieve, un lobulo es ruido*.

**El horizonte se recorta, no se escala.** El sprite mide 600 px de ancho; metido entero en los
172 px del sello queda a escala 0,29 y **la linea del suelo mide menos de un pixel y no se pinta**
— el bicho parece flotar. Se ensena un tramo de 200 columnas, casi a escala 1:1. Estirarlo con
`preserveAspectRatio` deformaria los guijarros.

Y **la segunda nube se quita**: a ese tamano era un pixel gris.

Sigue sin haber scroll interno, y el blanco mas pequeno mide **160 × 53** — por encima del suelo de
**48 de Material**, que es el que manda en tactil, no el de 24 de WCAG.

---

## Movimiento reducido

`prefers-reduced-motion` **salta el fundido y la entrada y deja la escena aterrizada**, en 0 ms.
No es una version corta: es ninguna version.

**Trampa a no repetir:** el selector universal `*` en la guarda de CSS **no alcanza a los
pseudo-elementos** — pagada en B2 con `.ficha-k::before`, que siguio animando bajo la guarda
generica. En B5 la guarda es JS y decide la duracion, que si llega a todo; si la implementacion
anade algun `::before` animado por CSS, **necesita su propia regla explicita**.

---

## Los gates

El arnes nuevo, `scripts/measure-caelestia-fundido.py`, tiene que comprobar al menos:

1. **La jerarquia no esta invertida.** El titular mide estrictamente mas que su lead y que los
   valores del colofon, y su valor es **exacto** (`--t-10` = 159,66 px), no un rango.
2. **Los ejes son los que tocan.** La frase usa `--cae-display-axes-cierre` (`opsz 144`), no
   `--cae-display-axes`. Es la mitad del defecto del diagnostico y no la caza ningun gate de tamano.
3. **La ocupacion**, con el extremo derecho del texto medido con `Range` — con cajas de bloque hoy
   da «0 px muertos» y el gate pasaria en falso sobre un 78 % vacio.
4. **Sin scroll interno**: `scrollHeight === clientHeight`, en 1440 y en 390.
5. **Los cuatro canales siguen accionables**: `mailto:` bien formado, `tel:` sin espacios ni
   guiones, externos con las dos palabras de `rel`.
6. **El dato se lee sin hover.** Cuidado: un `MouseEvent` sintetico **no dispara `:hover`** — trampa
   ya pagada en B2. Se comprueba leyendo, no simulando.
7. **Contraste AA en los dos esquemas**, barriendo las 24 h, midiendo **lo que se pinta de verdad**,
   con pares de control, y **sin vigilar pares que no existen** (el ojo de dia) ni decorado (las
   nubes).
8. **El fundido suena una vez y la entrada todas**: pulsar la pastilla del workspace activo no
   dispara nada; volver desde el 4 dispara solo la entrada.
9. **La entrada cabe dentro del deslizamiento del carril** (440 < 520).
10. **`prefers-reduced-motion` deja la escena aterrizada** en 0 ms, con el bicho de pie, el suelo
    trazado y las nubes puestas.
11. **390 px**: titular en su paso exacto, la linea mas larga cabe en la medida util, ningun blanco
    baja de 48 × 48, el sello es **cuadrado** y no sangra.
12. **Vice y Hyprland no se alteran**: `contacto.ts` es compartido.

### Ninguno se acepta sin haberlo visto dar rojo

En la fase A, ocho veces el fallo estuvo en el instrumento; en B2 se cazaron seis gates
tautologicos. Estos son los sabotajes que ya se ejecutaron durante el maquetado, con su resultado:

| gate | sabotaje | rojo obtenido |
|---|---|---|
| el lienzo no asoma | factor de crecimiento 6,34 → 5,07 | `['lienzo','campo','lienzo','campo']` |
| el fundido no suena dos veces | quitar la guarda `destino === origen` | `pulsar el workspace activo dispara la entrada` + `cuenta una visita` |
| el bicho mira de donde vienes | sentido fijado a constante | `el ojo no mira hacia el 4: x=24, esperado 23` |
| la profundidad del lobulo | comparar el mando contra el `clip-path` pintado | verde solo si coinciden a 0,3 px |

---

## Trampas de medicion pagadas en esta sesion — que no se repitan

1. **La partitura copiada a mano se desincroniza.** La tabla de tiempos del fundido estaba escrita
   aparte de la linea de tiempo; al tocar un `stagger` el dibujo mentia sin dar ningun error. **Se
   deriva de la propia linea de tiempo**, etiquetando cada tween con su numero de gesto, y avisa por
   consola si algun tween se queda sin etiquetar.
2. **Una copia congelada de un valor.** `window.__mf.TOTAL` se capturo antes de construir la linea
   de tiempo y devolvia 1000 ms para siempre. Los asideros de prueba tienen que ser **funciones**.
3. **Medir la propiedad equivocada.** El arnes leia la **opacidad** del pie cuando el pie habia
   pasado a esconderse con **recorte**: daba 1 todo el rato y la asercion pasaba sin mirar nada.
   Ahora mide *cuanto esta oculto* sumando opacidad y recorte, venga del borde que venga.
4. **Un verde que no comprobaba nada.** La comprobacion de esquinas devolvia `nada` porque el punto
   caia fuera de pantalla. **`nada` es ahora un fallo explicito.**
5. **Un control que no era el control.** La disposicion «cuatro columnas iguales» tenia en realidad
   tres celdas —un `<span>` agrupaba dos canales— y los actos se estiraban a 109 px. Comparar contra
   eso no comparaba nada.
6. **Descartar la version mala de una opcion no es descartar la opcion.** El renglon escondia de que
   red era cada valor; hubo que arreglarlo antes de poder rechazarlo con honestidad.
7. **Recomendar antes de mirar los numeros.** Dos veces: `--t-9` «porque rozaria el troquel» (la
   linea mide 530 y el hueco 858) y B «porque las otras no llegan al suelo de 24×24» (las tres lo
   pasan). Los dos argumentos eran falsos y la propia maqueta los desmintio.
8. **Un rotulo que se sale del lienzo no da error, desaparece.** En el grafico de la escala, el
   tamano mayor —el que hay que ver— se perdia entero. Ahora hay una asercion que grita.
9. **Un fichero suelto servido como descarga.** El companion manda `/files/*.htm` como descarga, y
   ademas trocea la pantalla por sus etiquetas: el fragmento de movil va incrustado con `srcdoc` y
   con **todos los `<` neutralizados como `\u003c`**. Escapar solo `</script>` no bastaba.
10. **El ancla `#NN-nombre` del companion no selecciona pantalla**: siempre se ve la ULTIMA
    escrita. Todas las medidas de esta sesion salieron bien porque cada maqueta se midio justo
    despues de escribirla, pero una medida tomada «de la pantalla 5» con la 8 delante habria medido
    la 8 y dado verde. Si hay que volver a medir una maqueta vieja, hay que reescribirla primero.
11. **Un `div` de 390 px no cambia el viewport.** Las media queries y los `vw` leen el viewport, no
    la caja del padre. El movil se mide en un viewport de verdad o dentro de un `iframe`.

---

## Lo que NO es

1. **No la carta de ajuste de Vice.** Cerrada y no se toca.
2. **No la cinta de Hyprland.** Es la tercera vez que la misma seccion se resuelve en un tema
   distinto: el liston de originalidad es mas alto aqui, no mas bajo.
3. **No una terminal tecleada.** Seria la tercera.
4. **No esconder el dato tras un hover**, ni introducir scroll interno.
5. **No un formulario.** No hay backend; fingir que envia seria mentir.
6. **No un QR.** Seria un quinto dispositivo en una escena que ya tiene troquel y campo de color.
7. **No iconos en vez de rotulos.** El dock de la barra ya lleva los cuatro; un icono solo esconde
   el dato.

---

## Preguntas abiertas para el plan

1. **`.claude/rules/verification.md` no existe.** La agenda daba por hecho que hay que anadir una
   fila a esa tabla y en el repo no hay tal fichero. El plan tiene que decidir: crearlo, registrar
   el arnes donde se registren los demas, o quitar ese entregable.
2. **Conflictos en `themes.css`.** B4 esta escribiendo en el mismo bloque `:root[data-theme=
   "caelestia"]` desde otra rama. Hay que decidir el orden de fusion.
3. **`display-xl` bajo Caelestia.** B5 puede darle regla propia o dejar de usar la clase en esta
   escena. Lo segundo es mas limpio pero toca `contacto.ts`, que es compartido — hay que comprobar
   que no afecta a Vice ni a Hyprland.
4. **Donde vive el sprite.** Un modulo propio bajo `src/components/` o `src/themes/`, y si se
   inyecta como SVG generado (lo maquetado) o como fichero.
5. **`--cae-display-axes-texto`** es un renombrado puro de tres literales. Confirmar con capturas
   antes/despues que no mueve un pixel, y decidir si entra en B5 o se deja como tarea aparte.

---

## Lo que queda abierto en Caelestia despues de B5

B5 cierra el **diseno** de las seis fases, no el tema:

- **B3 (Obra) sigue `en ejecucion`**, a la espera de las **nueve capturas reales** de los proyectos;
  hoy lleva huecos neutros.
- **Los dos `CLAUDE.md` no mencionan B3 ni B4.** Hay texto verificado de B3 en `.ai/memory.md` para
  pegarlo al principio de una sesion.
- **Las maquetas viven en `.superpowers/`, que esta en `.gitignore`.** Hay que rescatar al repo lo
  aprobado antes de cerrar la fase.
- **La deuda de escala tipografica** queda documentada aqui con numero por primera vez (16 tamanos,
  2 en la escala). B5 arregla su escena; **el resto del tema sigue con diez literales sueltos.**
