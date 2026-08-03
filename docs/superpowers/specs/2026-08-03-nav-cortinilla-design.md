# La cortinilla — la navegación deja de ocupar sitio y pasa a llamarse

Estado: pendiente de plan
Fecha: 2026-08-03
Alcance: la navegación de escenas en los tres temas. La escena de contacto se toca solo para
retirar lo que sostenía al rail. Hyprland y Caelestia no se rediseñan: se comprueba que no se
rompen.

## Por qué

La navegación de escenas funciona —15 de 15 anclas aterrizan a ±8 px en los tres temas— pero
cobra un peaje permanente por un servicio que se usa una vez. En escritorio es una lista fija
en el borde derecho; en pantallas estrechas, un rail numerado clavado al pie. En los dos casos
ocupa presencia el 100% del tiempo para resolver un salto ocasional.

Ese peaje no es una impresión, está pagado en incidencias. La lista lateral obligó a reservarle
150 px de carril a las barras de contacto, y ese carril produjo un corte vertical de color que
contradice la regla de sangrado de la propia escena. Al quitarlo, la píldora cayó sobre la banda
del correo —la CTA primaria— robando la pulsación en 25 de 25 puntos muestreados. El rail del pie
interceptaba el toque de las cuatro vías durante el scroll, un hallazgo que sobrevivió tres
revisiones de usuario y acabó escalado a P0 automático. Cada arreglo movió el problema en vez de
cerrarlo, porque el problema no era dónde estaba la navegación: era que estaba siempre.

Hay además una duplicación que nadie había señalado. El cromo de cine ya lleva un indicador de
posición vivo, `.rail-now`, que la coreografía actualiza escena a escena ("01 · Título" …
"05 · Fundido"). Es decir, el sitio tiene **dos sistemas diciendo lo mismo**: uno dice dónde
estás, otro dice a dónde puedes ir. Fundirlos elimina el segundo sin perder nada.

## Qué se construye

El indicador de escena del cromo se convierte en el disparador. Al pulsarlo, una **cortinilla**
cubre el área de contenido con las cinco escenas compuestas como el índice de un guion; al
elegir una, o al cerrar, desaparece. En reposo no hay navegación en pantalla: solo el rótulo que
ya estaba.

### El índice

Cada escena se compone en un renglón con cuatro piezas sobre un mismo eje:

```
01   TÍTULO      ···························   Desarrollador full stack
02   QUIÉN ES    ···························   Trayectoria y cifras
03   OBRA        ···························   Cinco proyectos
04   CRÉDITOS    ···························   Con qué construyo
05   FUNDIDO     ···························   Contacto            <- escena en curso
```

El **descriptor de la derecha no es copy nuevo**: es el rótulo que cada escena ya lleva en su
`hero-kick` ("Quién es", "Con qué construyo", "Contacto") o, en el hero, `identity.role`. El menú
solo los reúne. Esto cierra un hallazgo abierto en tres revisiones consecutivas de usuario: los
nombres de cine ("Fundido", "Créditos") no comunican su contenido a quien llega de fuera, y hasta
ahora la única salida planteada era renunciar a ellos. Con el índice, la personalidad se queda
entera y deja de costar comprensión.

La escena en curso va en ámbar, nombre y número. El resto en crema al 55%.

### Lo que se retira

Tres piezas existían únicamente para sostener una navegación permanente, y se van con ella:

- La lista vertical del borde derecho y el rail numerado del pie, con sus dos juegos de estilos.
- El `padding-bottom: 4.25rem` de la última vía de contacto, que reservaba hueco al rail.
- El mecanismo de tránsito de `sceneNav.ts` (los escuchadores de `scroll`, `touchmove` y `wheel`
  que apartaban el rail mientras la página rodaba). Sin capa fija sobre contenido en movimiento,
  no hay nada de lo que apartarse.

Se conserva intacto `destinationFor()`, incluida la corrección del carril de obra
(`OBRA_SETTLED_U / OBRA_TOTAL_U`) y su guardarraíl de acoplamiento en `scripts/measure-nav.py`.
Es lógica medida y verificada; el rediseño cambia cómo se pide el salto, no a dónde va.

### Movimiento

| momento | qué hace | cuánto |
|---|---|---|
| apertura del telón | recorte desde arriba (`clip-path: inset`) | 460 ms |
| entrada de los renglones | desde abajo, de desenfocado a nítido, escalonados cada 55 ms | 380–460 ms |
| cierre | telón y renglones a la vez, sin escalonado | 140 ms |

La curva es `cubic-bezier(0.22, 1, 0.36, 1)`, la que ya usan el hover de las gelatinas y el carril
de obra. La asimetría es deliberada: entrar puede ser una ceremonia, salir nunca. Con
`prefers-reduced-motion` la cortinilla aparece y desaparece sin transición ni escalonado, y sigue
siendo plenamente operable — se degrada el viaje, no la función.

### Teclado y foco

El disparador es un `<button>` con `aria-expanded`. Al abrir, el foco entra en la primera escena;
mientras está abierta, Tab cicla dentro de las cinco y no se escapa; Esc cierra; al cerrar, el
foco vuelve al disparador. Cada escena es un enlace real con su `href="#id"`, así que sin
JavaScript sigue navegando.

## Criterios de aceptación

Cada uno dice con qué instrumento se mide y a qué umbral.

1. **Nada de navegación en reposo.** Con la cortinilla cerrada, ningún elemento de `.scene-nav`
   intersecta el rectángulo de ninguna vía de contacto ni del hero. Instrumento:
   `getBoundingClientRect` en 390, 1029 y 1440. Umbral: 0 intersecciones.
2. **Cero robo de toque.** Barrido del scroll de la escena de contacto en 390 y 1029, muestreando
   puntos dentro de cada vía. Instrumento: `document.elementFromPoint`. Umbral: 0 puntos
   interceptados por la navegación. (El arnés ya existe y hoy da 0 sobre 654 puntos; debe seguir
   dando 0 cuando el rail ya no exista.)
3. **Las anclas no se mueven.** `scripts/measure-nav.py`, sin cambios de umbral: 15 de 15 a ±8 px
   en los tres temas, tras 3,5 s de asentamiento de Lenis.
4. **Alineación del índice.** Rótulo de sección y los cinco nombres comparten borde izquierdo;
   número, guía y descriptor comparten centro vertical. Instrumento: `getBoundingClientRect`.
   Umbral: ≤1 px de desviación en ambos ejes.
5. **Tiempos.** Apertura ≤480 ms, cierre ≤160 ms. Instrumento: `transitionend` cronometrado desde
   el clic.
6. **Foco.** Al abrir, `document.activeElement` es la primera escena; con Tab recorre las cinco y
   vuelve a la primera; Esc cierra; al cerrar, `activeElement` es el disparador. `aria-expanded`
   refleja el estado. Instrumento: Playwright con teclado real.
7. **Movimiento reducido.** Con `reduced_motion="reduce"`, el disparador es visible y pulsable
   —umbral: caja ≥44×44 px, frente a los 0×0 que mide hoy el cromo—, la cortinilla abre y cierra
   con duración 0 y el criterio 6 sigue cumpliéndose entero.
8. **Escala tipográfica.** `scripts/measure-type-scale.py`: 0 fallos nuevos sobre su línea base.
   Cualquier tamaño de la cortinilla debe ser un escalón declarado.
9. **Contraste.** Nombres y descriptores sobre el telón, muestreados sobre el píxel renderizado en
   tres fotogramas separados 2 s. Umbral: ≥4,5:1 el texto normal, ≥3,0:1 el texto ≥24 px.
10. **Los otros dos temas no se rompen.** La cortinilla abre, navega y cierra en Hyprland y
    Caelestia. Instrumento: `measure-nav.py`, que ya recorre los tres.
11. **Build y lint verdes**, y `verify.py` con 0 fallos nuevos sobre su línea base.

## El disparador no puede vivir en el cromo

Parecía natural convertir `.rail-now` en el botón, ya que está donde tiene que estar y dice lo que
tiene que decir. **Medido, no se puede**, y por dos motivos que se descubrieron al escribir este
spec:

- `.cinema-chrome` y su `.rail` llevan `aria-hidden="true"`. Una navegación escondida del árbol de
  accesibilidad no es una navegación.
- Con `prefers-reduced-motion: reduce` el cromo entero pasa a `display: none`: medido en 1440×900
  con `?theme=vice`, `.rail` queda en **0×0** y `.rail-now` con él. Un disparador ahí dentro
  dejaría **sin navegación a quien pide movimiento reducido**, que es justo quien más agradece no
  tener que recorrer la página entera. Y el cromo solo existe en Vice, mientras que la navegación
  hace falta en los tres temas.

Decisión: el disparador es un elemento propio de `sceneNav`, montado **fuera** del cromo —como ya
hace hoy la navegación, y por esta misma razón, que está anotada en su cabecera—, colocado en la
esquina superior derecha por CSS propio. Es un `<button>` real, presente en los tres temas y con
movimiento reducido.

Para no acabar con dos rótulos diciendo lo mismo en esa esquina, **`.rail-now` se retira del cromo
y su papel lo asume el disparador**: muestra la escena en curso ("05 · Fundido") y es lo que se
pulsa para saltar. Un solo elemento y una sola verdad. Eso obliga a que `sceneNav` mantenga por su
cuenta cuál es la escena actual —con un `IntersectionObserver`, no con la coreografía— para que
funcione igual en Hyprland y Caelestia, donde no hay cromo ni coreografía que lo actualice. La
línea que hoy lo actualiza en `vice.choreography.ts` desaparece con él.

## Riesgos

**El descriptor duplica un texto que vive en cada sección.** Si mañana cambia un `hero-kick` y el
menú no, el índice miente. Debe leerse del DOM en el momento de montar, no copiarse a mano — misma
familia que la trampa de `OBRA_TRANSIT`/`OBRA_REST` que ya documenta CLAUDE.md.

**Es una capa a pantalla completa sobre una página con pines de ScrollTrigger.** Hay que
comprobar que abrirla y cerrarla no dispara un `refresh` que descoloque el carril de obra.

## Fuera de alcance

El color del borde superior de la cuarta vía de contacto, la frontera del título en 1123 px, los
cinco tamaños por encuadre y el hover imperceptible entre 1080 y 1095 px siguen abiertos en la
revisión visual y no se tocan aquí. Tampoco los siete `gsap.from` heredados de `src/utils/reveal.ts`
ni las siete clases de tamaño fuera de escala de about, hero y créditos, contenidas por línea base.
