# La brasa — el cursor de Hyprland deja de encerrar lo pulsable en una caja

Estado: pendiente de plan
Fecha: 2026-09-10
Alcance: **solo el tema Hyprland**, y dentro de el **solo el dispositivo del cursor**.
`src/components/hyprCursor.ts` y el arnes `scripts/measure-cursor-luz.py`.
**No se toca `src/themes/themes.css`** (el anillo de foco de teclado se queda como esta, ver
`## Lo que NO cambia`), no se toca `src/backgrounds/shaderBackground.ts`, no se toca ninguna
escena, y **Vice y Caelestia no se rozan**: su cursor es otro modulo.

Revoca dos decisiones del spec `2026-08-19-hyprland-cursor-luz-design.md`, que sigue siendo el
documento de referencia del dispositivo: el canto como filete de la caja completa, y el charco
recortado a canto vivo. Todo lo demas de aquel spec sigue en pie.

Maqueta aprobada por Aoshi el 2026-09-10, opcion B, vista viva y medida:
`.superpowers/brainstorm/4110132-1789056931/content/canto-opciones-v2.html`.

---

## El encargo

Aoshi, dictando el tercero de cuatro fallos del repaso de Hyprland:

> La animacion de hover del cursor sobre items que se pueden clickear hace que tenga un recuadro
> naranja, hace que se vea mal.

Preguntado por que le chirria exactamente, contesto dos cosas, no una: **la caja, sea del color que
sea**, y **que sea la caja COMPLETA**. No es cuestion de tono. Y despues de ver las maquetas
anadio que **el recorte del charco entra tambien**.

## Por que no es una reparacion

El canto no es un descuido. `2026-08-19-hyprland-cursor-luz-design.md` lo declara como el
delimitador del dispositivo — *"el charco ... mas el canto del elemento a 1px en `--l1`"* — y el
tema tiene el cursor por TERMINADO. Esto es una decision cerrada que Aoshi revoca, asi que va por
diseno y no por depuracion.

Y hay una segunda razon, medida: **el canto carga hoy con la senal entera**. Con el canto tapado,
la luminancia media dentro de la diana entre rozado y no rozado se mueve:

| diana | geometria a 1440x900 | delta de luminancia sin el canto |
|---|---|---|
| `.hero-mail` | 211 x 22 | **+0,0032** |
| `.obra-abrir` | 1440 x 108 | +0,0325 |

Sobre el enlace del hero eso es cero: si se borra el canto y no se pone nada, apuntar deja de
producir ningun cambio visible. **El canto no se puede quitar, se tiene que sustituir.**

## Por que se ve como se ve

Tres cosas se suman, y conviene tenerlas separadas porque solo dos entran en el alcance:

1. **Es un rectangulo alrededor de texto.** Sobre `.hero-mail` (211 x 22, monoespaciada) se lee
   como un campo de formulario.
2. **Sobre dianas anchas cruza la pantalla.** `.obra-abrir` mide 1440 px de ancho: el canto es una
   caja naranja de canto a canto del viewport.
3. **Es indistinguible del anillo de foco del navegador**, y no por casualidad:
   `.obra-abrir:focus-visible` es `outline: 2px solid var(--l1); outline-offset: -2px`
   (`src/themes/themes.css`). El raton y el teclado pintan hoy **la misma forma en el mismo color**.

## Lo que se descarto, y con que evidencia

Se maquetaron tres direcciones vivas con la piel real del tema. Las dos descartadas no cayeron por
gusto:

**C — borrar el canto y subir el charco hasta que se baste solo.** Para que se note hay que subirlo
a 4x. A esa potencia el charco —que va recortado a la caja— deja de leerse como luz y se convierte
en un rectangulo oscuro macizo de cantos duros; sobre `.obra-abrir` es un manchon que cruza la
pantalla. **C devuelve la caja que el encargo rechaza, solo que rellena en vez de perfilada.**

**A — encender solo el borde inferior, de canto a canto.** Correcta sobre dianas pequenas: se lee
como el subrayado de un enlace, la convencion mas vieja de la web, y no necesita manual. Pero sobre
`.obra-abrir` sigue siendo una linea de 1440 px — mas discreta que la caja y con la misma cualidad
que el encargo rechaza: una senal que cruza la pantalla entera porque la diana es ancha.

## El dispositivo

### La brasa

Sustituye al `strokeRect`. Un tramo de la **arista inferior** de la diana, encendido en `--l1`,
que sigue a la mano.

| | |
|---|---|
| **Grosor** | 2 px |
| **Color** | `rgb(255 90 52 / 0.85 · pot)` — el mismo `--l1` y la misma potencia que el canto de hoy |
| **Posicion** | centrado en la x del puntero, sobre `rect.bottom` |
| **Ancho** | `radio · 0.75`, donde `radio` es el que ya calcula el charco (`max(alto · 2.4, 120)`) |
| **Extremos** | difuminados a cero con un degradado lineal — **sin cantos duros**: no es una barra recortada |
| **Acotado** | nunca sobresale de `rect.left`/`rect.right` |
| **Suavizado** | la POTENCIA se suaviza (`POT_SMOOTHING`); la POSICION no, como el punto de la mano |

**El ancho sale de la ley que ya existe, no de un numero nuevo.** El radio del charco lo dicta la
altura del elemento y no la seccion, y la brasa hereda esa misma ley: ~90 px sobre un nombre de
Stack (105 x 34), ~194 sobre una fila de obra (1440 x 108).

**Acotarlo hace que B contenga a A gratis.** Si la diana es mas estrecha que el tramo, la brasa
cubre la arista entera y el comportamiento es exactamente el de A, sin que nadie programe el caso.

**2 px en `--l1` no es una eleccion libre:** es la linea de brasa que los cimientos acaban de
estrenar como suelo de la escena Stack (fusionada el 2026-09-10). La senal del cursor pasa a hablar
la gramatica que el tema ya tiene, en vez de anadir una forma propia.

**Que resuelve, punto por punto:** no encierra (una sola arista, y parcial); no cruza la pantalla
(sobre 1440 px solo hay luz cerca de la mano); y no se confunde con el foco de teclado, que sigue
siendo un anillo inscrito de 2 px en las cuatro aristas.

### La pluma del charco

El charco sigue recortado a la caja de la diana. **El recorte no se quita: se empluma.**

Es importante entender que se conserva. El spec del cursor declara que el charco existe *"SOLO
dentro de lo que se puede pulsar, recortado a canto vivo"*, y eso **no es un descuido: es lo unico
que dice hasta donde llega la zona pulsable**. Difuminarlo del todo deja al dispositivo sin ninguna
senal de extension.

La pluma es de **14 px hacia dentro desde cada arista**. Desaparece el corte duro y con el la
lectura de caja; la extension sigue siendo legible porque el charco sigue muriendo dentro de la
diana y nunca fuera. Se difumina el filo, no se quita el limite.

### Ruling: la pluma es solo para el lienzo

El charco tiene dos mecanismos (`2026-08-19`, Task 9): el lienzo de `z-index: -4` para dianas sin
nada opaco encima, y un `background-image` en linea para las que si lo tienen.

**El segundo mecanismo hoy no pinta en ningun sitio.** Su unica diana era `.credit`, que se retiro
con el catastro de creditos, y darle una nueva es un encargo que ya estaba abierto y anotado en
`2026-09-09-hyprland-stack-cimientos-design.md`. `measure-cursor-luz.py` sale por eso con **1 fallo
esperado**, escrito en su propio docstring.

Decision: **la pluma se implementa solo en el lienzo.** El mecanismo de `background-image` conserva
su corte duro y gana un comentario que ata la pluma a ese encargo abierto. Escribir codigo que
ningun gate puede ver en rojo es exactamente el modo de fallo que este proyecto lleva trece
instrumentos rotos pagando; cuando esa familia tenga diana, la pluma entra con ella y se mide
entonces.

## Lo que NO cambia

- **El charco**: rampas (`HUECO_CENTRO`/`HUECO_MEDIO`, `LUZ_CENTRO`/`LUZ_MEDIO`), umbral
  `LUM_OSCURA`, el signo adaptativo y el radio. Toda esa calibracion se queda intacta: este spec no
  toca ni un numero de contraste.
- **El punto de la mano** y su anillo oscuro.
- **El reparto de senales**: `NATIVE_ZONE`, `PRESSABLE`, el I-beam sobre texto corrido, el
  `grab` de la galeria y los enlaces externos con puntero nativo.
- **El anillo de foco de teclado.** `.obra-abrir:focus-visible` sigue siendo
  `outline: 2px solid var(--l1)` inscrito. Quitarlo seria un fallo de accesibilidad, y ahora que el
  raton pinta otra forma **las dos senales por fin se distinguen entre si**, que es parte de lo que
  arregla este spec.
- **Movimiento reducido y tactil**: el modulo no se monta, igual que hoy. Este dispositivo es de
  escritorio por construccion, asi que **no hay maqueta de 390 px** en este spec: no seria una
  version, seria un caso inventado.
- **La limpieza de `destroy()`**, incluido `restaurarImagen()`.

## Los gates

`measure-cursor-luz.py` vigila el charco por familias (oscurecer tiene que mejorar el contraste,
iluminar tiene que aguantar AAA y notarse) y **nunca ha mirado el canto**. Que un rectangulo naranja
rodeara cada pulsable durante semanas con el arnes en verde es un fallo del instrumento tanto como
del diseno, asi que las aserciones que faltan son parte del arreglo.

Entran tres familias. **Las tres se veran dar rojo contra `main` antes de aceptarse**, y aqui no
hace falta sabotear nada: el comportamiento actual ES el fallo que dicen cazar.

1. **La senal no encierra la diana.** Sobre una diana ancha y con el charco encendido: ni la arista
   superior ni las dos laterales tienen linea encendida, y lo encendido en la inferior ocupa
   claramente menos que el ancho del elemento. Roja hoy: hoy las cuatro aristas estan encendidas.
2. **La brasa sigue la mano.** Dos posiciones distintas del puntero sobre la misma diana mueven el
   centro de masa de lo encendido en la arista inferior, y lo mueven en el mismo sentido. Roja hoy:
   hoy el filete es identico se ponga el raton donde se ponga.
3. **El charco no tiene canto duro.** Cruzando la arista de la diana pixel a pixel con el charco
   encendido, no hay escalon de luminancia por encima del umbral. Roja hoy: hoy hay corte a canto
   vivo.

Reglas de instrumento que este repo ya pago y que estos gates heredan: `hover()` real y nunca un
`MouseEvent` sintetico (no dispara `:hover`); anclaje al ESTADO y no al cronometro (bajo
`--use-gl=swiftshader` el rAF llega cada 200-400 ms); oyente de consola en todas las paginas; y
`page.screenshot()` provoca su propio aviso de `ReadPixels`, que no es un error de la pagina.

## Riesgos anotados

- **La brasa sobre una diana muy baja.** Sobre `.hero-mail` (22 px de alto) el tramo cae a 2 px por
  debajo de una linea de texto de 22: hay que comprobar en captura que no se lee como subrayado del
  texto de la linea siguiente.
- **Dianas contiguas.** Los 23 nombres de los cimientos estan pegados; la brasa de uno no puede
  invadir la caja del vecino. El acotado a `rect.left`/`rect.right` lo cubre por construccion, pero
  se mira en captura.
- **La pluma y el contraste.** Emplumar reduce el area donde el charco oscurece, y el charco que
  oscurece es el que SUBE el contraste. El gate de contraste por familia tiene que volver a salir
  con sus numeros de hoy o mejores; si baja, la pluma se recorta antes que la calibracion.
