# HANDOFF — la cola de la seccion de obra

> Escrito el 2026-07-30 al mergear `design/obra-rail-ritmo`. Recoge lo que los dos gates
> (`lidia-naive-tester` y `vera-art-director`) levantaron y que **no** bloqueo aquel merge, mas
> lo que ya venia diferido del encargo del ritmo.
>
> El ritmo del carril esta cerrado: spec `docs/superpowers/specs/2026-07-30-obra-rail-ritmo-design.md`,
> `Estado: implementado`, con registro de implementacion.

## Antes de tocar nada

Lee el registro de implementacion de ese spec. Documenta cinco trampas que ya se pagaron en
esta seccion, y dos de ellas son de **definicion**, no de codigo: un gate y su instrumento
midiendo cosas distintas con el mismo nombre. Volvio a pasar dos veces en el mismo encargo.

## Por que hay cola y no un merge bloqueado

Vera puntuo la seccion en 6,50/10 (su gate son 7,5) y aun asi no bloqueo. Los dos numeros no se
contradicen: el promedio es de **la seccion**, y la seccion arrastra tres cosas que el cambio de
ritmo no causo — la escala tipografica del tema, los nueve placeholders y una flotacion vertical
del CSS anterior. Descontadas, el trabajo mergeado es positivo en el eje que ataca y neutro en
el resto.

## La cola, por orden

### 1. Orientacion, indice y salida del carril — el mayor, y el mas votado

Lo levantaron el especialista de UX en el diseno **y** Lidia en el gate, por separado.

Durante 5040 px el carril esta fijado y no hay forma de saber por que obra vas ni cuantas
quedan. El unico indicador es el ordinal del fondo, **al 6% de opacidad y `aria-hidden`**. Y el
rotulo de la barra de orientacion dice `03 · CARTELA` durante las cinco obras: es el numero de
**escena**, pero se lee como "proyecto 3". Lidia estaba en la obra 5 y arriba seguia poniendo 03.

Va por su segunda ronda en el naive test. A la tercera Lidia lo escala a P0 automatico.

**Un detalle que NO es regresion y conviene no perseguir:** el rotulo cambia a `04 · CREDITOS`
con la obra 5 todavia ocupando media pantalla. Es estructural: la region de cromo del carril se
define como `{start: pin.start, end: pin.end}` (`vice.choreography.ts:1425`), pero al soltar el
pin el elemento fijado necesita **un viewport entero** mas para salir de pantalla. Medido, el
hueco vale 900 px antes y despues del cambio de ritmo. Se arregla al disenar la orientacion, no
antes.

Aqui entra tambien el hallazgo del naive test sobre el recorrido hasta el `mailto:`. Ya muy
mitigado: el email esta en el hero, a 754 px en movil, dentro de la primera pantalla. Lidia lo
llamo "lo mejor que ha pasado desde la ronda anterior" y le subio el eje de CTA de 4 a 6.

### 2. F-06 — la escala tipografica de Vice. **Segunda seccion: a la tercera es P0**

Una cartela renderiza **10 tamanos**: 352 / 73,6 / 23,2 / 16 / 12 / 10,56 / 10,4 / 9,92 / 9,28 /
8,48 px. Cinco caben en una banda de 2,08 px, con diferencias del 1,5% al 8,6%: nadie distingue
el rotulo de seccion (10,56) del rotulo "Problema" (10,4). Eso no es una escala, es ruido. Mas
cuatro pesos de Manrope en el mismo fotograma.

Las etiquetas de meta van a **8,48 px**. Pasan contraste de sobra (15,59:1), pero estan por
debajo de cualquier suelo practico.

Es el mismo hallazgo que Vera dio en `about` (v1.1). Por su regla de recurrencia, la tercera
aparicion lo convierte en P0 automatico. **Definir la escala del tema de una vez sale mas barato
que arreglarlo por secciones.**

### 3. F-02 — la columna de texto flota entre mesetas

Posicion vertical del bloque de texto en las cinco mesetas asentadas:

| | m1 | m2 | m3 | m4 | m5 | rango |
|---|---|---|---|---|---|---|
| titulo `y` | 244,4 | 250,2 | 231,5 | 224,2 | 237,2 | **26,0 px** |
| meta `y` | 365,1 | 403,4 | 352,1 | 377,4 | 390,4 | **51,3 px** |
| tope mascaras | 452,4 | 490,7 | 439,5 | 464,7 | 477,7 | **51,2 px** |

Mientras tanto el ordinal (`y = 90,7`) y la galeria (`y = 266,6`) son identicos en las cinco. La
causa: el bloque va centrado en vertical y su altura varia (lead de 1 o 2 lineas, mascaras de
131,6 a 209,6 px).

El CSS es anterior, pero **antes era invisible**: con la cinta continua nunca veias dos cartelas
quietas que comparar. Ahora son cinco fotogramas fijos consecutivos y el titulo salta de pase a
pase, que en una gramatica de moviola es la diapositiva mal registrada en la ventanilla.

Arreglo: anclar la primera linea del titulo a una `y` fija en vez de `align-items: center`.
**Misma causa raiz que el desfase de 15/11/11 px de la prueba en `about`** — arreglar las dos
juntas.

### 4. F-01 + F-05 juntos — la meseta 1 y la direccion de la mascara

**Van juntos a proposito.** Vera pidio F-01 antes del merge y se decidio que no; la razon esta
aqui para que se pueda discutir.

F-01: la obra 1 termina de montarse a ~265 px de los 363 del reposo de cabeza, asi que quedan
~98 px de quietud frente a los ~326 de las obras 2-5. Medido con sondeo directo de opacidad y
`clipPath`:

```
off 160   lead 1.000  gal 0.000  masks 22.8% / 47.5%
off 200   lead 1.000  gal 0.852  masks  0.9% /  4.0%
off 240   lead 1.000  gal 0.998  masks    0% /   0%
```

(De paso, eso refuta el hallazgo nº2 de Lidia: dijo que sobraban ~300 px muertos tras completarse
la obra 1. Son ~98, y en el punto que ella dio por completo — y≈3982, off 181 — las mascaras
estaban a medio barrer.)

F-05: la guillotina de `clipPath` **corta los glifos a mitad de palabra** durante ~310 ms, en las
cinco obras. Y barre izquierda→derecha, **en contra** de la direccion por la que la pieza entra
(el track va hacia la izquierda, la pieza llega desde la derecha).

**Por que juntos:** la prueba de Vera de que la meseta 1 "se lee como rota" son precisamente los
glifos cortados. Eso es F-05, y pasa en las cinco piezas; en las 2-5 no se nota porque ocurre
durante el transito. Acortar la ventana de la obra 1 (`slateWindow(0)`: `OBRA_REST * 0.8` →
`* 0.5`) no arregla el corte, solo hace que pase mas rapido — y monta esa cartela 3x mas rapido
que las otras cuatro, cambiando una asimetria por otra.

Probar primero `inset(0 0 0 100%)`, para que la mascara barra a favor del movimiento. Puede que
F-01 se disuelva solo.

### 5. F-03 — la segunda imagen de cada galeria no se ve nunca

En 4 de las 5 piezas el segundo `.gallery-item` cae en `x` 1414,9-1973: fuera del contenedor
(acaba en 1403,7) y fuera del viewport. En reposo es invisible **siempre**. Solo cruza el
encuadre durante el transito.

**Es el unico punto donde el cambio de ritmo empeoro algo:** el transito ahora pica a ~2321 px/s
frente a los 644 px/s constantes de antes, asi que su unica ventana es 3,6x mas rapida. Decidir
si entra en el encuadre en reposo o se quita — antes de que lleguen las capturas reales y alguien
descubra que la mitad no se ve.

### 6. F-07 — la caption sin scrim, a 1 px del marco

`background: transparent`; borde inferior del item en `y = 619,3`, caption en `618,3`. En el
render los trazos cruzan la linea del marco. Hoy el placeholder casi vacio perdona; con una
captura real detras, la caption cae sobre pixeles de interfaz sin proteccion.

**Hacerlo ANTES de meter las capturas reales, no despues.**

### 7. F-04 — el parallax descompensa el encuadre 19,4 px

Durante un solo reposo el margen derecho de la galeria va de 43,7 a 28,6 px mientras el izquierdo
del texto esta clavado en 48. Es el precio del parallax-sobre-reposo, que existe para que la
meseta no se lea como colgada — la intencion es correcta y **no hay que quitarlo**. Acotar el
rango (`xPercent −2 → 2` da ±11 px y sigue matando la sensacion de colgado) o aplicarlo a un hijo
interior en vez de al contenedor que define el margen.

### 8. Las nueve capturas de `public/media/obra/`

Son marcadores "Captura pendiente". Son los 12 fallos de fixtures de la linea base de
`verify.py`. Bloquean el juicio visual de la mitad derecha de cada meseta: la galeria ocupa el
~40% del area del fotograma y es el **ultimo escalon** de la entrada, o sea la recompensa de toda
la construccion.

Lidia, en una frase: *"he recorrido cinco proyectos y lo unico que he visto es un rotulo CAPTURA
PENDIENTE repetido nueve veces. Con capturas reales esto sube de contactaria a llamaria hoy."*
Le costo el eje de fotos, de 6 a 4.

**Dato tranquilizador:** la monoespaciada que se ve esta **dentro del PNG**, no en el sistema. El
DOM solo tiene Passion One y Manrope. Desaparece sola con las capturas reales; no hay una tercera
familia que perseguir.

## Deuda del instrumento

`scripts/measure-obra-rail.py` publica `v_lateral_encuadre_px_s` y **el campo esta roto**. Sobre
el codigo viejo daba 0,5-5,1 px/s a velocidad de lectura, en un carril lineal cuya velocidad
lateral era la del scroll (~236 px/s) en todo instante. Y el spec habia registrado 220-245 px/s
para esa misma metrica. No se ha diagnosticado la causa y no se uso para decidir nada. **Esta
retirado de la tabla de objetivos del spec, pero el campo se sigue imprimiendo.** O se arregla o
se quita.

## Verificaciones que hay que repetir siempre que se toque esta seccion

- **`prefers-reduced-motion` a >=901px.** Ya fallo una vez y de la peor manera: cuatro de las
  cinco obras eran inalcanzables (`dcc7998`). Lidia lo re-testea a proposito en cada ronda.
- **Los cuatro puntos que miden contra la distancia del pin** (`railBound`, trigger de creditos,
  letterbox, `scrollrail:refresh`). Tarea 3 del plan del ritmo.
- **El propio instrumento.** Al cambiar la geometria, `measure-obra-rail.py` se quedo midiendo
  contra el recorrido lateral en vez de contra el presupuesto del pin, y contra un mapeo lineal
  que ya no existia. La mediana de M1 paso de 386 px a 4 px al arreglarlo: era casi todo
  artefacto. **El medidor es una de las cosas que mide contra la distancia.**
