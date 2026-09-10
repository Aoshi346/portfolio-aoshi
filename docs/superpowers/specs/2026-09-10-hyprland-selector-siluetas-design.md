# El selector de escenas — las siluetas dejan de envejecer en silencio

Estado: en ejecucion
Fecha: 2026-09-10
Alcance: **solo el tema Hyprland**, y dentro de el **solo el indice de escenas**.
`src/components/sceneNav.siluetas.ts`, `scripts/measure-cortinilla.py` y el fichero nuevo
`scripts/scene-nav-firmas.json`. **No se toca ninguna escena** — ni `src/sections/`, ni
`src/themes/themes.css`, ni `src/data/content.ts` — ni `scripts/verify.py`. Vice y Caelestia no se
rozan: Caelestia ni siquiera monta este indice (`sceneNav` va con `display: none` alli).

---

## El encargo

Aoshi, dictando el cuarto y ultimo fallo del repaso de Hyprland:

> Por ultimo, el selector de escenas y sus previews ya no reflejan como se ve actualmente la
> pagina, por ende, hay que arreglarlo de ultimo.

## Que es una silueta

El indice de escenas es un panel con cinco fichas. Cada una lleva una **silueta**: la escena
reducida a su estructura — filetes, bloques de texto abstraidos, cajas, uno o dos textos reales —
dibujada en coordenadas de un plano de **1440x900** que el CSS escala al encuadre de la ficha.

**Son copias a mano, y eso es deliberado.** No se leen del DOM porque el indice se pinta con la
cortinilla cerrada y las escenas ni siquiera estan montadas del todo. La cabecera del modulo ya
declaraba el precio desde el primer dia:

> El precio es que pueden envejecer — si una escena cambia de dispositivo y su silueta no, la hoja
> miente en silencio.

## El fallo: cuatro de cinco

Medido a 1440x900 contra el build servido, con oyente de consola y la consola limpia:

| escena | silueta | estado |
|---|---|---|
| `hero` (Titulo) | filete vertical, nombre, linea italica, regla, pie a dos lados | **fiel** |
| `quien-es` | caja corta + dos filas sueltas debajo, retrato como circulo | **derivada** — la placa real es una rejilla con borde de tres bandas, con retrato fotografico y el bloque de estado en `--l1` |
| `obra` | cuatro divisorias verticales + ordinales escalonados | **derivada** — es el carril horizontal, el dispositivo ANTERIOR. La escena real son cinco filas apiladas de 1440x109 |
| `creditos` (Stack) | parrilla densa + un punto y la palabra "React" | **obsoleta entera** — el catastro retirado el 2026-09-09 |
| `contacto` | cuatro filas apiladas a todo lo ancho | **derivada** — los cuatro canales son hoy columnas al pie |

**Y el arnes no veia nada.** `measure-cortinilla.py` medía COMO se pintan las siluetas — que hay
cinco, que ninguna esta vacia, que el plano escala, que las piezas no bajan de 1px en movil — pero
**nunca las comparaba con la escena**. No podia detectar deriva por construccion.

**Correccion del propio diagnostico, que conviene que quede escrita.** El primer recuento decia
tres derivadas y daba `obra` por fiel, porque sus cinco nombres de proyecto coinciden con
`content.ts`. Lo destapo el subagente que construia el gate: la silueta dibuja columnas y la escena
son filas. Medido despues: `.obra-abrir` en y=396, 506, 615, 725 y 834, todas a x=0 y ancho
completo. **Coincidir en el texto no es coincidir en el dispositivo.**

## El instrumento: dos disenos, y por que gana el segundo

### Descartado: el indice de similitud

La primera idea fue responder "¿se parece la silueta a su escena?": extraer la tinta real del DOM,
cuantizar las dos a una rejilla y comparar la ocupacion (Jaccard).

**No separa.** Medido en rejillas de 2x2 a 20x12, con Jaccard binario, correlacion de densidad,
coseno, y subconjuntos de solo-texto y solo-bordes: el orden salia practicamente invertido —
`creditos`, declarada obsoleta entera, puntuaba **por encima** de `hero`, la unica fiel.

La razon es de fondo, no de calibracion: **"¿sigue representando esto al dispositivo actual?" es un
juicio semantico**, y un solape de rectangulos no puede verlo. El implementador paro en vez de
mover el umbral hasta que saliera el resultado deseado, que es lo que el encargo exigia y lo que
este proyecto lleva quince instrumentos rotos pagando.

### Aceptado: la firma de deriva

Se cambia la pregunta. La que de verdad fallo aqui no es "¿se parece?" sino:

> **¿ha cambiado alguna escena sin que nadie revisara su silueta?**

La deriva no fue el problema. El **silencio** lo fue.

- Se extrae la tinta real de cada escena del DOM (nodos con texto propio y bordes visibles), con
  los rects **relativos al origen de la escena** y con `reduced_motion="reduce"`, que es como se
  mide maquetacion y no un fotograma de la entrada animada.
- Se cuantiza a una rejilla y se reduce a una firma corta y estable.
- Las firmas **bendecidas** viven en `scripts/scene-nav-firmas.json`, junto al arnes y no dentro de
  `src/`: son dato de instrumento, no codigo de la aplicacion.
- Si una escena cambia y su firma no se ha vuelto a bendecir, **rojo**, con un mensaje que dice que
  hacer: revisar la silueta de esa escena y, si sigue representandola, volver a bendecir.
- `--update-firmas` bendice. Es un acto deliberado que se revisa en el diff, el mismo idioma que
  `verify.py` ya usa con `--update-baseline`.

**Lo que este gate NO hace, y esta declarado en su docstring:** no comprueba que la silueta sea
correcta. Solo que nadie cambie una escena sin pasar por delante de ella. Un indice de similitud
daria confianza falsa, y esta demostrado midiendo que no puede darla.

## Las reglas del repintado

- **El plano de 1440x900 representa lo que el visitante VE de esa escena, y ninguna pieza puede
  caer fuera de el.** El encuadre lleva `overflow: hidden`, asi que una pieza que se sale no avisa:
  se recorta. Ocurrio con `obra`, cuyas coordenadas se tomaron del **viewport en un scroll
  concreto** en vez del marco de la escena — el tercio superior del fotograma quedaba vacio y la
  quinta fila cortada.
- **Medir esa escena tiene trampa**: `[data-scene="obra"]` reporta un `getBoundingClientRect()` de
  ~109 px de alto mientras las cinco filas (`position: absolute`) ocupan ~547. **La caja de la
  seccion no describe lo que se ve.**
- **Una silueta no es un calco: es la escena reducida a su estructura.** Si necesita veinte piezas
  para leerse, esta calcando. Piezas antes -> despues: `quien-es` 20 -> 16, `obra` 42 -> 16,
  `creditos` 32 -> 24, `contacto` 23 -> 18.
- Los textos reales (`disp`) salen **literales de `content.ts`** (o de la seccion, en el caso de
  "Hablemos"), nunca inventados.
- Las reglas de legibilidad en movil no se tocan para que algo pase: `GROSOR_MINIMO = 9`,
  `CUERPO_MINIMO = 40`, `esFino()`, `ACENTOS`/`OPACIDAD_QUE_AGUANTA`. Si una pieza no sobrevive, la
  respuesta es **dibujar menos**, nunca bajar el umbral.

## Los gates

Sobre lo que `measure-cortinilla.py` ya vigilaba, entran:

1. **La firma de deriva por escena**, con su fichero de firmas bendecidas y su `--update-firmas`.
2. **Recorte parcial.** La asercion vieja solo contaba piezas **enteramente** fuera del encuadre, y
   el unico recorte que produce un repintado es el parcial: era invisible. Ahora se detecta, mas una
   comprobacion estatica sobre `SILUETAS` de que toda pieza cabe en 1440x900.
3. **Los textos de las siluetas existen en el contenido real.** Estan copiados a mano, y cambiar un
   texto casi nunca mueve la ocupacion de celdas: sin esta asercion, la misma deriva silenciosa
   volvia por la otra puerta.
4. **Las tres listas de escenas concuerdan** — las claves de `SILUETAS`, los selectores de firma y
   las escenas de `content.ts`. Sin esto una escena nueva queda sin vigilancia.

## Rulings

**El limite de la transposicion se cierra, no se acepta.** La primera version del gate hasheaba la
union de celdas encendidas, asi que una transposicion fila/columna que cubriera las mismas celdas
daba el MISMO hash — y esa es exactamente la clase de deriva que le paso a `obra`. Se cierra
hasheando el **multiconjunto de cajas de pieza en celdas** `(c0, r0, c1, r1)`, cuatro enteros que
ya se calculaban y se tiraban; de paso cubre el otro limite declarado (una pieza nueva dentro de una
celda ya encendida). **Una limitacion que se cierra moviendo cuatro enteros es una decision, no una
limitacion.** Sube la sensibilidad, asi que la prueba de estabilidad se repite **bajo carga**.

**Bendecir es por escena, nunca todo a la vez.** Si derivan dos escenas la misma semana, bendecir
en bloque tras revisar una entierra el rojo de la otra, que no ha mirado nadie. Eso niega la premisa
del dispositivo.

**Todo el arnes mide contra `--base`.** Hacer el flag obligatorio para las firmas mientras el resto
del arnes seguia apuntando a una constante del dev server dejaba dos cosas rotas a la vez: el
comando documentado reventaba antes de llegar a las firmas, y las familias que miden la geometria de
las siluetas — las que tendrian que haber cazado el recorte de `obra` — seguian midiendo contra
HMR, que este repo tiene escrito que "corrompe las medidas y miente en los dos sentidos".

## Lo que queda abierto

- **Las siluetas siguen siendo copias a mano.** Derivarlas del DOM eliminaria la clase de fallo
  entera, pero choca con la razon por la que se hicieron asi y seria rediseñar un dispositivo
  cerrado. Aoshi eligio repintar y anadir el gate; queda anotado como la alternativa no tomada.
- **El gate no juzga si una silueta es buena**, solo si su escena cambio sin que nadie la mirara.
  Esa parte la siguen haciendo ojos humanos.
