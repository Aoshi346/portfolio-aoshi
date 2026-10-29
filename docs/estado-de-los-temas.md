# Estado de los temas — registro completo

> Sacado de los dos CLAUDE.md el 2026-10-29: cargaban este registro en CADA sesión (~100k caracteres,
> por encima del tope de instrucciones de Claude Code). Los CLAUDE.md conservan un resumen de cinco
> líneas y apuntan aquí. **Léelo antes de tocar un tema**: cada bloque dice qué está cerrado, qué
> se midió y qué no se vuelve a tocar.
>
> La versión en español (abajo) es la vigente: es la que llevaba `.claude/CLAUDE.md` y está más al
> día. La inglesa del `CLAUDE.md` raíz va íntegra en el anexo, sin tocar.

> **2026-10-29: Vice e Hyprland, RETIRADOS.** Por decisión de Aoshi, el sitio deja de sortear tema
> y queda solo Caelestia (rama `design/solo-caelestia`). Su código, sus arneses y sus capturas
> siguen enteros en el tag **`tres-temas`** (`e78f11f`). Los bloques de Vice e Hyprland de abajo
> se quedan como registro histórico; lo que dicen de ficheros ya no existe en `main`. Lo que
> afectaba a Caelestia (escala tipográfica, contraste, `shaderBackground.ts`) sigue vigente.
>
> Segunda pasada, el mismo dia (rama `design/podar-secciones`): fuera las 16 ramas de DOM de las
> secciones que solo pintaban Vice o Hyprland y que Caelestia ocultaba (`credits.ts`, `gallery.ts`
> y `projectScene.ts`, enteros), y su CSS. Caelestia identica en 60 capturas. `verify.py` mide
> ahora la bandeja de Creditos y la Editorial de Obra, no el DOM oculto.


- **Vice: TERMINADO.** Cerrado con el plan `2026-08-04-vice-fondo-tinta` (fondo `viceInk.ts`,
  serigrafía de tinta a dos colores; disparador de navegación de escenas sin caja, con marca de
  registro). Revisado en el sitio real por Aoshi, gate `lidia-naive-tester` en verde, gate
  `vera-art-director` con BLOCK aceptado explícitamente (7.12/10 sobre gate 7.5 — el resto es
  un hallazgo de producto conocido y aceptado, no un defecto). **No tocar el tema Vice** (fondo,
  disparador, coreografía, tipografía) salvo que Aoshi lo pida explícitamente. Detalle completo
  y números finales en `docs/superpowers/specs/2026-08-04-vice-fondo-tinta-design.md`.
- **Caelestia: las seis fases (A, B1-B5) estan FUSIONADAS.** El diseno del tema esta cerrado. Lo
  que impide darlo por TERMINADO no es diseno: **B3 necesita las nueve capturas reales** (hoy son
  marcadores «CAPTURA PENDIENTE» con la paleta de Vice) y **B4 tiene dos P1 de producto abiertos**.
  Y `measure-caelestia-obra.py` falla tres aserciones de contraste — **fallaba igual antes de
  fusionar B5** (comprobado en un worktree aparte contra `1f61752`), y la pinta del fallo
  (`bg=rgba(0, 0, 0, 0)`) apunta a su propio instrumento, no al CSS.
- **El repaso de interfaces de Caelestia con Aoshi (2026-09-05/06): FUSIONADO en `main`**
  (`1c246eb`, rama `fix/repaso-interfaces`, sin push). Nueve fallos dictados y arreglados uno a
  uno, cada uno con su gate visto en rojo antes: el hero ya no se pinta antes de que llegue la
  coreografia (`js-cae-entrada`), la notificacion del shell no salta al cargar, la terminal se va
  antes de trazar el nombre, la barra y el dock entran (CSS, `no-preference`), el cajon de Obra
  llena la ventana como hoja con relieve y relevo del texto por capas, iconos de C y Zustand desde
  Devicon Plain, las escenas 4/5 pasan a **Stack** y **Contacto**, y la chapa «Disponible» sale de
  la barra. De ahi salieron dos cambios de diseno: **la tarjeta «Ahora mismo»** rediseñada
  (`2026-09-05-caelestia-ahora-mismo`: orden quien/que hace/estado, sin caja, figura viva de 240
  vertices, entrada que brota de su luz; Vera 6,6 BLOCK residual, Lidia 6,4) y **el dino de
  Contacto como juguete** (salta, mira, y arrastrarlo es un *vistazo* a otra hora que se deshace al
  soltar; el troquel gira con muelle y **el fondo generativo sigue el vistazo** via
  `caelestia:hora`). El registro completo, con los diez errores pagados en la sesion (medir a
  1412x748, un commit que decia `verify.py` en verde estando en rojo, subagentes parados esperando
  monitores, OOM con arneses en paralelo, el hook de la hora sin llegar al fondo), esta en
  `docs/superpowers/specs/2026-09-05-caelestia-repaso-interfaces.md`. **No medir la tarjeta a
  1412x748**: es la ventana interior con pagina a 1440x900.
- **Hyprland y Caelestia: EN CURSO.** Foco de trabajo actual. Comparten `shaderBackground.ts`
  con Vice (no tocar ese módulo sin confirmar que Vice sigue intacto) pero tienen su propio
  fondo (`hyprGradient.ts` / `caelestiaBlobs.ts`), paleta y tipografía — ver `src/themes/themes.css`.
  La obra en Hyprland tiene dispositivo nuevo (el cartel, plan y spec
  `2026-08-10-hyprland-obra-cartel`): cinco titulares siempre en pantalla, la captura viaja con
  GSAP Flip hasta un visor grande al pulsar. Contraste contra el fondo real medido por glifo (no
  viewport entero, que lo sobrestimaba): solo el titular en reposo cae de AA, y solo en el peor
  0,5% de fotogramas del shader (3,88:1) — techo de brillo pendiente de decisión de producto, no
  un problema de legibilidad — ver `## Color y contraste` / `## Registro de implementación` del
  spec. La sección "Con qué construyo" (la escena Stack) se rediseñó y se fusionó el 2026-09-10 —
  ver su bloque propio más abajo; Hyprland en conjunto se queda EN CURSO.

- **La escena Stack de Hyprland: FUSIONADA** (`2026-09-09-hyprland-stack-cimientos`; el spec sigue
  en `en ejecucion` hasta que Aoshi la revise en el sitio real). El catastro se retira y
  `[data-scene="credits"]` pasa a ser **«los cimientos»**: tres columnas de área sacadas de
  `skillGroups` (Interfaz 8, Backend y datos 5, Herramientas 5; 550/344/344 px a 1440, razón
  1,6/1/1) sobre una línea de brasa de 2px que lleva los cinco lenguajes base, un escalón
  tipográfico **por encima** de los nombres. La composición es la frase: tres cosas que construye,
  apoyadas en cinco que sabe.
  - **No hay jerarquía entre los 23 nombres.** El dispositivo anterior los dimensionaba por en
    cuántas obras aparecían, y ese dato no da de sí: siete tecnologías no aparecen en ninguna obra
    pública y las cuatro transversales están en las cinco. La jerarquía es entre estratos.
  - Módulo nuevo `src/components/hyprStackCimientos.ts`, **sin GSAP**: un `IntersectionObserver`
    decide cuándo y el CSS marca los tiempos. **`credits.ts` NO se toca** — su DOM genérico se
    oculta entero, el patrón que B3/B4 de Caelestia dejaron probado. Retirar el catastro se llevó
    1.662 líneas (797 de CSS, 526 del arnés, 339 de la coreografía) con Vice y Caelestia idénticos,
    comprobado por `git worktree`.
  - **La entrada la manda el suelo**: la línea se traza, enciende los cinco lenguajes a su paso
    (cada retardo derivado de su propia x, no escrito a mano) y sólo después crecen las columnas
    por recorte. Un encendido en la escena, no veintitrés. Su disparador va anclado a la caja del
    **propio dispositivo**, nunca a la sección — el mismo arreglo que esta rama le hizo a la placa,
    donde una entrada se agotaba 119px bajo el pliegue con el arnés en verde.
  - **La frase vive en el aire, no bajo el rótulo del suelo.** Rozar, enfocar o tocar un nombre lo
    enciende a `--l3` y escribe su `detail` literal en Instrument Serif itálica dentro de los 48px
    de aire entre las columnas y el suelo. Al principio estaba junto a «LENGUAJES BASE» y **los dos
    gates de crítica lo llamaron defecto por separado**: para los 18 nombres que no son lenguajes
    base se leía como un error de plantilla. Subirla cuesta cero píxeles y los 48px que mide el
    gate no cambian.
  - **Dos instrumentos que hubo que arreglar.** Un clic de ratón apagaba el nombre bajo el cursor
    (el `blur` del botón anterior llamaba a `apagar()` sin comprobar quién estaba activo), y **el
    gate 4 no hacía clic con ratón en ningún sitio**: se titulaba «el apuntado se apaga al salir» y
    estaba verde mientras pulsar dejaba el dispositivo en blanco. Aparte, el gate 6 comparaba la
    frase pintada contra la copia que el propio DOM guarda, las dos escritas por la misma línea:
    ahora saca los 23 `detail` de `content.ts` y falla si el parseo vuelve vacío.
  - **Dos decisiones que conviene no deshacer.** La guardia de movimiento reducido va selector a
    selector a propósito (`*` no alcanza a los pseudo-elementos) y la regla de apuntado está acotada
    con `[data-cimientos]` para ganarle a la de entrada **por estructura**, no por aparecer después
    en la hoja. Por debajo de 1024px el dispositivo se apila: entre 821 y 1023 la proporción 8/5/5
    se derrumba a columnas iguales y «Claude Code» se parte, así que la banda apilada llega a 1023
    y el gate 8 sólo mide tres columnas desde 1024.
  - **`measure-cursor-luz.py` sale con 1 fallo esperado**, y está escrito en su propio docstring.
    Retirar el catastro se llevó `.credit`, su **única diana ocluida** — la que ejercita el
    mecanismo de `background-image` en vez del lienzo. `.cim-nombre` no vale como reemplazo (los
    cimientos no tienen fondo propio), así que el arnés dice qué falta y desde cuándo en vez de
    sustituirla por una más blanda. **Darle a esa familia una diana ocluida nueva es un encargo
    abierto.**
  - Contraste por glifo contra el shader vivo: nombre 9,66:1 · rótulo 5,79:1 · lenguaje 15,65:1 ·
    icono 6,53:1 sobre un piso decorativo de 3:1 · apuntado 9,66:1 · frase 9,35:1. Lo vigila
    `scripts/measure-cimientos.py` (14 familias; el gate 10, el de contraste, detrás de
    `--contraste`).
  - Gates: `lidia-naive-tester` 6,3/10 en rojo por la colocación vieja de la frase, **arreglada**;
    `vera-art-director` **BLOCK residual 7,42/10**, a 0,08 del gate, **sin P0 accionables**, y da
    por cerrados por construcción los dos hallazgos que bloquearon el catastro. Residual aceptado:
    los linderos de 1px en `--rule` son indistinguibles del shader en el tercio inferior de cada
    columna (medido píxel a píxel; es el mismo techo de brillo que el tema ya arrastra), y el icono
    de GSAP es un wordmark que no escala como el resto a 20px.
  - Abierto y anotado en el spec: el canto naranja del cursor sobre los 23 botones nuevos, las
    siluetas del selector de escenas, la limpieza de los nodos muertos de `credits.ts`
    (`.credits-rail`, `.credits-glow`, `.credits-spark` y `STRIP_REPAINT_EVENT`, que ya no tiene
    ningún oyente), que `8fr 5fr 5fr` está escrito a mano y refleja recuentos que viven en
    `content.ts` sin que ningún gate los cruce, y que `measure-cimientos.py` no está enganchado a
    ningún sitio: se lanza a mano, por decisión.
- **El cursor de Hyprland: TERMINADO y fusionado** (`2026-08-19-hyprland-cursor-luz`), "el hueco
  adaptativo". Al apuntar un pulsable se abre un charco recortado al elemento que **oscurece donde
  el fondo es brillante e ilumina donde ya es oscuro**, con el canto encendido y un punto que marca
  la mano; sobre texto corrido se apaga y manda el cursor del sistema. El signo lo decide la
  luminancia del fondo que tapa el lienzo de `z-index: -4`, leida una vez por diana. Dos
  mecanismos: el lienzo cuando no hay nada opaco encima, y un `background-image` en linea cuando si
  lo hay (se pinta sobre el fondo propio del elemento y bajo su texto). Lo vigila
  `scripts/measure-cursor-luz.py`, con **el gate partido por familia** — la que oscurece tiene que
  mejorar el contraste, la que ilumina tiene que aguantar el piso de AAA **y notarse**. Un solo
  gate para las dos solo podia exigir lo que valiera para ambas, que es nada, y ya se colo asi una
  vez. Antes de recalibrar nada, leer el epilogo del spec: toda la calibracion es anterior al
  arreglo del `gsap`.
- **El canto del cursor de Hyprland pasa a ser LA BRASA** (`2026-09-10-hyprland-cursor-brasa`,
  fusionado, spec `implementado`). El dispositivo rodeaba cada pulsable con un `strokeRect` de 1px
  en `--l1` sobre la caja ENTERA. Aoshi lo rechazo por dos cosas a la vez: **la caja, sea del color
  que sea**, y **que fuera la caja COMPLETA**. En su lugar, un tramo de 2px de la **arista inferior**
  centrado en la x del puntero, con los extremos difuminados y acotado a la caja — asi que en una
  diana mas estrecha que el tramo cubre la arista entera, que era la otra opcion, sin programar el
  caso. 2px en `--l1` es el mismo token y grosor que el suelo de los cimientos.
  - **Medido antes de proponer nada:** sin el canto y sin sustituto, apuntar `.hero-mail` movia la
    luminancia **+0,003**. El canto cargaba con la senal entera. Hoy la mueve +100/255.
  - **El recorte del charco se empluma 14px**, no se quita: el recorte es lo unico que dice hasta
    donde llega la zona pulsable, pero su corte a canto vivo se leia como caja sobre los fotogramas
    brillantes del shader.
  - **`PLUMA = 14` se eligio CONTRA una regla del propio spec**, y es lo que mas conviene no
    deshacer. La regla decia "el contraste vuelve con sus numeros de hoy o mejores; si baja, se
    recorta la pluma": al pie de la letra llevaba a 5, y a 5 vuelve el rectangulo oscuro de cantos
    rectos. Lo que el gate exige no es un ratio sino que el charco MEJORE el contraste 0,15; a 14 lo
    mejora 0,64 (4,3x) con el peor caso en 13,96:1, tres veces AA. Orden de prioridad, ahora escrito:
    primero el suelo de accesibilidad, despues que no se lea como caja, y el ratio el ultimo.
  - **El arnes nunca habia mirado esa senal**: un rectangulo naranja rodeo cada enlace del sitio
    durante semanas con `measure-cursor-luz.py` en verde, porque vigilaba el charco. Entran cuatro
    familias, y **dos salieron tautologicas en su primera version**: una daba VERDE contra el codigo
    sin emplumar, y el umbral de la otra dejaba pasar `PLUMA = 5`, o sea no defendia el valor que
    existia para defender. Las cuatro vistas en rojo antes de aceptarse.
  - Gates: `lidia-naive-tester` 7,8/10 sin P0; `vera-art-director` BLOCK residual 7,3/10 sin P0
    accionables. Abierto: `.hero-mail:focus-visible` no pinta indicador de foco (WCAG 2.4.7,
    **igual en `main` desde antes**), el anillo de teclado sigue siendo la caja completa vetada para
    el raton, y la luz se apaga sobre las miniaturas de obra (no es regresion: con el canto pasaba
    igual, y es la misma familia que la diana ocluida sin recambio).

- **El selector de escenas de Hyprland: FUSIONADO** (`2026-09-10-hyprland-selector-siluetas`, spec
  `implementado`). El indice pinta cinco **siluetas** — cada escena reducida a su estructura, en un
  plano de 1440x900 que el CSS escala al encuadre. Son **copias a mano a proposito** (el indice se
  pinta con la cortinilla cerrada, antes de que las escenas monten del todo) y la cabecera del
  modulo ya avisaba: *"pueden envejecer... la hoja miente en silencio"*. Paso: **cuatro de las
  cinco** ya no representaban su escena.
  - **El arnes no podia verlo por construccion**: medía COMO se pintan, nunca si se parecen.
  - **El instrumento descartado importa tanto como el que se quedo.** Un indice de similitud
    (Jaccard de ocupacion) NO separa: en rejillas de 2x2 a 20x12 y cuatro metricas, `creditos`
    —obsoleta entera— puntuaba POR ENCIMA de `hero`, la unica fiel. *"¿Sigue representando esto al
    dispositivo actual?"* es un juicio semantico que un solape de rectangulos no ve. El implementador
    **paro en vez de mover el umbral**.
  - **El gate que se queda cambia la pregunta**: ¿ha cambiado una escena sin que nadie revisara su
    silueta? La deriva no fue el problema, el silencio lo fue. Firma estructural por escena contra
    `scripts/scene-nav-firmas.json`, y `--update-firmas <escena>` para bendecir — **por escena,
    nunca las cinco**, que enterraria el rojo de una que nadie miro. **No comprueba que la silueta
    sea correcta** y lo dice en su docstring.
  - **El punto ciego de la transposicion se cerro, no se acepto**: hashear la union de celdas da el
    MISMO hash para una transposicion fila/columna — la deriva exacta de `obra`. Ahora hashea el
    multiconjunto de cajas de pieza, cuatro enteros que ya se calculaban.
  - **La trampa del repintado**: el encuadre lleva `overflow: hidden`, asi que una pieza que se sale
    se recorta sin avisar. `obra` tomo sus coordenadas del **viewport en un scroll concreto** y dos
    piezas llegaban a y=940 sobre un plano de 900: **la escena de cinco filas se dibujaba con cuatro
    y media**. Y la asercion que debia verlo solo contaba piezas ENTERAMENTE fuera. Medir esa escena
    engana: `[data-scene="obra"]` reporta ~109px de alto mientras sus cinco filas ocupan ~547.
  - Piezas antes -> despues: `quien-es` 20 -> 16, `obra` 42 -> 16, `creditos` 32 -> 24,
    `contacto` 23 -> 18. Menos piezas y mas parecido: resumen, no calco.
  - **Trampa de entorno**: `vite preview` devuelve 200 `text/html` para cualquier ruta (fallback de
    SPA), asi que sondear `/@vite/client` por codigo de estado da falso positivo.
  - Abierto: las siluetas siguen siendo copias a mano (derivarlas del DOM quitaria la clase de fallo
    entera pero rediseña un dispositivo cerrado; Aoshi eligio repintar + gate), y el arnes arrastra
    **2 fallos preexistentes** del disparador de Caelestia, comprobados identicos en `main`.

- **El cursor de Caelestia: TERMINADO y fusionado** (`2026-09-04-caelestia-cursor`), **«la gota»**:
  una gota translucida del pigmento de la hora. Es un dispositivo de tema entero, no una de las
  fases B1-B5. Sobre un pulsable se tensa en perla y espera; **al PULSAR se derrama y llena la diana
  hasta sus cantos**; sobre las dianas que se eligen al rozar (`button[aria-pressed]`, las piezas de
  Creditos) se derrama **al ENTRAR**. Sobre texto corrido se apaga y manda el I-beam del sistema.
  Los dos estados que pedia el encargo no son dos simbolos: son **un mismo gesto disparado en dos
  momentos**, y asi es como cumple el veto de «un cursor no puede tener manual». Es DOM y no lienzo
  (necesita `backdrop-filter` y `mix-blend-mode`) y **no usa GSAP**: solo transiciones CSS, para que
  el montaje siga siendo sincrono. Sin estela y sin inercia de posicion. Modulo
  `src/components/caelestiaCursor.ts`, vigilado por `scripts/measure-caelestia-cursor.py` (8 gates,
  53 aserciones).
  - **La lista blanca cuelga de la RAIZ, no de `[data-scene]`**, al reves que en Vice y Hyprland.
    Medido: en Caelestia los cinco workspaces son hijos directos de `main`, el de Obra
    (`div#obra.obra-rail`) NO lleva `data-scene`, y la barra y el dock cuelgan de `#app`, fuera de
    `main` — con la regla en `[data-scene]` el puntero del sistema seguiria visible sobre las
    tarjetas de Obra, las pastillas y el dock, tres de las dianas que este cursor viene a vestir.
    Y los pulsables necesitan **opt-in explicito**: `<button>` y `<a>` declaran su propio `cursor`
    en la hoja del navegador, asi que la herencia jamas los alcanza.
  - **Toda la lista blanca vive dentro de `@media (prefers-reduced-motion: no-preference)`.** No es
    cosmetico: la puerta de montaje de `main.ts` solo mira AL CARGAR, asi que quien activa el ajuste
    a mitad de sesion tiene el modulo ya montado — y sin acotar, la guardia escondia la gota
    mientras la lista blanca seguia ocultando el puntero del sistema: **la pagina se quedaba sin
    ningun cursor hasta recargar**, justo para el perfil al que la guardia dice proteger. Se acota
    la lista, NO se le superpone una regla de rescate: un rescate tendria que ganarle en
    especificidad a la regla que quita el glifo, y al hacerlo le ganaria tambien al
    `cursor: pointer` que cada pulsable declara por su cuenta. Ese error exacto ya se pago dos veces
    en esta misma rama.
  - **La opacidad del derrame es 0,22 de dia y 0,20 de noche, y NO se unifican.** No son la misma
    mezcla: `multiply` sobre papel claro oscurece el fondo del texto, `screen` sobre superficie
    oscura lo aclara, y es eso lo que come contraste. A 0,30 la leyenda de la tarjeta de Obra caia a
    4,06:1 a las 06:30, por debajo de AA; a 0,20 el peor caso del barrido de 24 horas es **4,92:1**.
    El margen es de 0,43, no de un orden: correr el gate 6 entero antes de tocarlo.
  - **El mecanismo de reserva que proponia el spec —pintar el derrame bajo el texto como
    `background-image`, el patron de Hyprland— aqui es PEOR, no una red de seguridad**: se pinta por
    debajo de los hijos del elemento, y la tarjeta de Obra lleva un `<img>` que ocupa casi toda su
    caja, asi que el derrame desapareceria justo en la escena donde mas se ve. Pregunta cerrada.
  - `destroy()` retira los cercos vivos **a traves de `retirarCerco`**, nunca con un `remove()`
    crudo: es lo unico que ademas cancela su temporizador de respaldo de 1200 ms.
- **El shell de Caelestia: TERMINADO y fusionado** (`2026-08-20-caelestia-escritorio`, fase A de
  seis). El tema deja de ser un juego de tokens y pasa a ser **un shell de escritorio Material You 3
  cuyo color y esquema los gobierna el reloj del visitante**. El matiz recorre los 360 grados de la
  rueda en 24 horas; la claridad no se mueve nunca, asi que **el contraste es invariante por
  construccion**: se mide una vez y vale para las 1.440 posiciones del reloj. Claro de 07:00 a 20:00,
  oscuro fuera, y **el esquema no se interpola jamas** — superficie y texto intercambian el orden de
  claridad, asi que todo camino continuo cruza por contraste 1:1. Demostrado EN MOVIMIENTO, no solo
  por aritmetica: muestreando cada ~15 ms en el cruce, `L` salta de 0.245 a 0.925 en un solo paso,
  sin ningun valor intermedio en 90+ muestras.
  Las cinco escenas son un **carril horizontal de workspaces** — un espacio de trabajo no se
  desplaza, se cambia — asi que el tema no tiene scroll de pagina y los workspaces inactivos van con
  `inert`. **`sceneNav` esta oculto aqui** (`display: none`): la barra ya lleva las cinco escenas
  como pastillas siempre visibles, y su panel cambiaba el hash sin mover nada. Fraunces
  (`opsz 9 wght 900 SOFT 0 WONK 1`) sobre Hanken Grotesk y Martian Mono. Lo vigila
  `scripts/measure-caelestia-hora.py` con 16 aserciones.
  **Las fases B1-B5 (las cinco secciones de dentro de la ventana) NO estan hechas** — *cierto al
  cerrar la fase A; hoy las cinco estan fusionadas, ver sus bloques mas abajo.* Su maquetacion
  seguia pensada para una pagina que se desplaza, asi que que el contenido se viera apretado dentro
  de un workspace era lo ESPERADO, no un defecto.
  Gate `vera-art-director` con BLOCK aceptado explicitamente (6.55/10 sobre gate 7.5), igual que en
  Vice: su P0 se arreglo y sus tres P1 quedan como decision de producto, anotados en el spec.
  **Antes de recalibrar nada, leer el `Registro de implementacion` del spec.** Ahi esta la leccion
  que mas costo en esta fase: **ocho veces el fallo estuvo en el instrumento, no en el diseno** — una
  regex que leia `oklch()` como bytes RGB (1.00:1 en todo), un reloj congelado que hacia
  *inalcanzable por construccion* la rama del cruce de umbral, un proxy de tamano de PNG que pasaba
  contra el shader que venia a cazar, una asercion titulada "y usa el ancla" que solo leia
  `outlineStyle`, unos `PARES` de contraste que vigilaban roles que no se pintan, y un A/B que se
  provocaba a si mismo el aviso que media. Los numeros del spec aguantaron todos.
  **Ningun gate se da por bueno sin haberlo visto dar rojo contra el fallo que dice cazar.**

- **La fase B1 (Titulo) de Caelestia: TERMINADA** (`2026-08-26-caelestia-titulo`, la primera de las
  cinco fases de dentro de la ventana). La escena `#hero` deja de ser sobras apretadas del shell y
  pasa a ser **el escritorio presentandose solo**: un titular justificado a tres lineas en
  `opsz 144` (el shell se queda en `opsz 9` — dos tokens distintos,
  `--cae-display-axes-cartel` frente a `--cae-display-axes`, nunca se reutiliza uno), firma y
  columna de cifras al canto derecho, el widget "Ahora mismo" armado entero con literales de
  `content.ts` (ningun campo derivado inventado — "10.º semestre" sale del parentesis de
  `education[0].period`, no es un campo nuevo) y una entrada de escena que teclea `whoami` en una
  terminal falsa y aterriza la firma como 15 contornos trazados de Fraunces.
  **`src/backgrounds/caelestiaBlobs.ts` ya no existe**: es `src/backgrounds/caelestiaFiguras.ts`,
  cinco figuras de Material 3 Expressive (puffy/sunny/cookie/clover/burst) que morfan con la hora
  del visitante y comparten `shaderBackground.ts` (solo admite uniforms `float`, asi que el `vec3`/
  `vec2` del prototipo aprobado se repartio en floats sueltos y se reconstruyo dentro del shader).
  Pasar el raton por el widget o una cifra aparta el fondo entero con un transform CSS, el
  movimiento reducido salta la entrada directo al estado aterrizado, y el barrido de tinta y el
  volteo de cifras del cierre corren en la misma timeline.
  `scripts/measure-caelestia-titulo.py` la vigila con las ocho familias de aserciones que documenta
  en sus propios docstrings — las ocho se vieron dar rojo contra el fallo exacto que dicen cazar
  antes de aceptarse (ver el registro de implementacion del spec para el detalle de que rompia
  cada una). **Movil queda fuera del alcance de la fase B1 a proposito**: la medida de
  justificacion del titular es una medida fija de 1080px sin salto a viewport estrecho, asi que a
  390px los titulares se desbordan y la columna de cifras se solapa con ellos — es lo esperado, no
  una regresion que perseguir. **Las fases B2-B5 (Quien soy, Obra, Creditos, Fundido, todas dentro
  de la misma ventana) quedan pendientes** — *cierto al cerrar B1; hoy las cuatro estan
  fusionadas.* La B1 solo cierra `#hero`.
  Gate `lidia-naive-tester` en verde (7,1/10, cero P0). Gate `vera-art-director` dio **BLOCK**
  inicial (6,36/10 contra el gate de 7,5) por un P0 real, no de acabado: la regla generica de panel
  de la fase A le daba a Titulo el mismo `background` opaco que a las otras cuatro escenas (que si
  son "aplicaciones" con ventana), tapando el 78% del fondo generativo — se corrigio antes de
  aceptar el gate (una excepcion de CSS para `[data-scene="hero"]`, revisada, sin fuga a las otras
  escenas ni a Vice/Hyprland). Quedan tres hallazgos de acabado aceptados como conocidos (deuda de
  escala tipografica que recurre por 5ª vez en el proyecto, espaciado del widget fuera de la
  rejilla 4/8px, un eje de fuente repetido como literal) — el detalle completo esta en el
  "Registro de implementacion" y en la seccion "Gates de critica" del spec de B1.

- **La fase B2 (Quien soy) de Caelestia: TERMINADA y fusionada** (`2026-09-02-caelestia-quien-soy`,
  la segunda de las cinco de dentro de la ventana). La escena `#about` deja de ser una ficha
  apretada y pasa a ser **la salida de `neofetch`**: el comando que un escritorio de Linux ejecuta
  para decir que maquina es esta. B1 abre con `whoami`, que pregunta quien eres; este pregunta que
  maquina eres.
  **La desviacion que la hace propia:** el nombre ocupa el sitio donde `neofetch` imprime el titulo
  de la distribucion y es **lo unico que NO va en monoespaciada** — Fraunces a
  `--cae-display-axes-cartel`. Sin eso, la convencion de terminal deja todas las lineas pesando
  igual y la escena no tiene un primero. La cabecera del comando es `identity.email`, no un
  `usuario@host` inventado: es un dato real, es la via de contacto principal y es **la unica parada
  de tabulador de la escena**. El retrato hace de logotipo de la distro, recortado con un squircle
  que **morfa** a otra figura con nombre de Material 3 al rozarlo — morfar es la identidad declarada
  del tema (*«a fluid, morphing shell»*, parametro `deformScale`).
  Medido en la ventana de 1412x748: el aire pasa de **152/121 a 55/56** y el nombre deja de partirse
  en tres lineas. Lo vigila `scripts/measure-caelestia-quien-soy.py` con 9 gates / 42 aserciones, y
  el arnes del shell sigue verde: la fase A no se toco.
  **Las tres trampas que no hay que repetir**, todas pagadas en esta fase:
  1. **Un `polygon()` solo interpola con otro si tienen el MISMO numero de puntos.** Con distinto
     numero el navegador no morfa: corta de golpe, sin error ni aviso. Las figuras se generan a 240
     puntos con `docs/superpowers/specs/2026-09-02-caelestia-quien-soy-figuras.py`.
  2. **El selector universal `*` NO alcanza a los pseudo-elementos.** La guardia de
     `prefers-reduced-motion` dejaba fuera `.ficha-k::before`, que seguia animando. Necesita su
     propia regla explicita.
  3. **Los gates tautologicos.** Se cazaron seis instrumentos rotos: contar lineas de un texto con
     `white-space: nowrap` (no puede partirse), comparar contra el `clientWidth` de una pista `1fr`
     (se auto-expande con el contenido), medir un fotograma de la entrada en vez del estado
     aterrizado, una espera que casi vuelve el gate incapaz de fallar, un `MouseEvent` sintetico que
     **no dispara `:hover`**, y un build de sabotaje que fallo en silencio (`> /dev/null` tragandose
     el error de `tsc` mientras `vite preview` servia el `dist` viejo).
     Y de proceso: **`pkill -f "vite preview"` se mata a si mismo** desde el harness de Bash, porque
     el patron casa con su propia linea de comando.
  **Movil queda fuera de alcance**, igual que en B1: a 390px la parrilla desborda 96px. Es lo
  esperado, no una regresion.

- **La fase B3 (Obra) de Caelestia: FUSIONADA, pero en estado `en ejecucion`**
  (`2026-09-03-caelestia-obra`, la tercera de las cinco de dentro de la ventana). La escena `#obra`
  deja de ser un carril de **4964 px dentro de una ventana de 748** —cuatro de los cinco proyectos
  inalcanzables y scroll interno, justo lo que prohibe la ley de la fase A— y pasa a ser **la
  Editorial**: cinco tarjetas siempre en pantalla (captura 16:10 y leyenda en Fraunces italica, con
  inclinacion alterna de +-3-5 grados que se endereza al pasar el raton) en una fila fija, y un
  **cajon** que se abre debajo con la ficha completa del proyecto. Modulo nuevo
  `src/components/caelestiaObraEditorial.ts`.
  **`src/sections/obra/projectScene.ts` NO se toco** — mejor que lo previsto en el plan: ese DOM
  sigue igual para Vice/Hyprland y bajo Caelestia `themes.css` lo oculta entero en vez de
  reescribirlo. Es el fichero que comparten los tres temas.
  La entrada de escena es **Caida** (las tarjetas caen con una rotacion propia por tarjeta y
  `bounce.out`; el cajon entra en cuatro capas separadas, nunca como bloque plano) — **sin terminal
  tecleada**, que habria sido la tercera. Lo vigila `scripts/measure-caelestia-obra.py`, ya anadido
  a la tabla de `rules/verification.md`.
  **Por que no esta TERMINADA:** las nueve capturas reales de `public/media/obra/*.webp` no existen
  — hoy son marcadores «CAPTURA PENDIENTE» de 1600x1000 pintados con la paleta de **Vice** (morado
  y ambar), que dentro de Caelestia se leen como un error de tema. Es un encargo a Aoshi, no deuda
  de diseno: el gate visual final queda bloqueado hasta que existan. Movil fuera de alcance, igual
  que en B1 y B2.

- **La fase B4 (Creditos) de Caelestia: FUSIONADA, en estado `en ejecucion`**
  (`2026-09-03-caelestia-creditos`, la cuarta de las cinco de dentro de la ventana). La escena
  `#credits` deja de ser un reparto de parcelas con 10 px de scroll interno, 424 px muertos al canto
  derecho y **cuatro rotulos de grupo que existian en el DOM y no pintaba ninguno**, y pasa a ser
  **la bandeja de paquetes**: si cada escena de Caelestia es una aplicacion, Creditos es el gestor
  de paquetes — que hay instalado en esta maquina. Cuatro bandas de la misma altura (una por
  territorio, con el rotulo a bandera derecha en una calle de 158 px), 23 modulos fijos de 142 px, y
  las 23 tecnologias siempre en pantalla. Modulo nuevo `src/components/caelestiaCreditosBandeja.ts`;
  **`src/components/credits.ts` NO se toca y NO se bifurca por tema** — su DOM generico se oculta
  entero desde `themes.css`, el mismo patron que B3 dejo probado con `projectScene.ts`.
  - **El tamano no codifica nada.** Las 23 piezas miden lo mismo (88 px, un unico valor en todo el
    DOM). Las dos varas posibles mienten: la global infla Herramientas porque `tooling` esta en los
    cinco proyectos; la de por territorio hace a JavaScript (una obra) tan grande como Git (cinco).
  - **23 figuras de Material 3 unicas**, una sola familia armonica, **240 vertices cada una** — dos
    `polygon()` solo interpolan con el mismo numero de puntos. Se reconstruyen en runtime desde una
    tabla de 23 filas en `src/utils/figurasM3.ts` (el generador emite 167 KB de literales y no hacen
    falta: dividir por `rmax` es redundante si despues se encaja por el VANO de cada eje, medido en
    4.4e-16).
  - **Rozar elige sin pulsar**, y el foco llega a lo mismo. La entrada es **«la instalacion»**: las
    23 llegan como circulos identicos —paquetes sin abrir— y morfan a su figura, en una onda por
    territorios. Sin terminal tecleada: seria la tercera despues de B1 y B2.
  - Lo vigila `scripts/measure-caelestia-creditos.py` (9 familias de aserciones). **Tarda mas de dos
    minutos** por el barrido de las 24 horas: lanzarlo con `nohup` y esperar POR PID.
  **Por que no esta TERMINADA:** `vera-art-director` dio **BLOCK (5,3/10 sobre un gate de 7,5)**,
  aceptado como residual igual que en Vice, el shell y B1 — pero sus dos P0 de producto se
  arreglaron antes de aceptarlo (`2b8db2c`). `lidia-naive-tester` en verde (7,1/10, cero P0), con dos
  P1 de producto abiertos: el gesto de rozar no es descubrible, y «Aparece en» no enlaza con la
  escena Obra, con lo que se pierde la cadena *«sabe X → lo uso en Y»*, que es lo unico que esta
  escena aporta. Movil fuera de alcance, igual que en B1 y B2 — hoy a 390 px la escena ya arrastra
  154 px de scroll interno, que B4 ni arregla ni empeora.
  **2026-10-29 (`design/stack`):** cerrado el P1 del cruce. Cada titulo de «Aparece en» abre su
  ficha en Obra (evento `caelestia:obra` antes del cambio de workspace; en el carrusel la tarjeta
  se centra), y rozar elige tras 140 ms para que el puntero pueda subir hasta el enlace sin relevar
  la cabecera por el camino. El del gesto se deja: React sale elegida al entrar y eso lo ensena.
  Mismo dia: fuera Electron (sin obra tras retirar WatchDog), entran FastAPI, SQLAlchemy y
  PostgreSQL (25 piezas), y Parallax y Vela llevan Vite y Tailwind CSS (y Vela GSAP), que usan de
  verdad.
  **La leccion que mas costo vuelve a ser sobre los instrumentos:** la entrada se disparaba AL
  MONTAR y terminaba a los 2803 ms con la escena **4334 px fuera del viewport** — el gesto firmado
  de la fase no se veia ni una sola vez. Era una regresion contra un patron que el propio tema tenia
  documentado una fase antes (`caelestiaObraEditorial.ts` escucha `caelestia:workspace`). Y **su
  gate tenia dos aserciones, las dos del camino de movimiento reducido**: se titulaba «la entrada» y
  no comprobaba que la entrada ocurriera. Es el noveno instrumento tautologico de esta pista y el
  unico que no se cazo saboteandolo — se cazo mirando la escena. **Un gate que solo mide la rama
  degradada no vigila el camino que ve el visitante.**

- **La fase B5 (Fundido) de Caelestia: FUSIONADA e `implementado`**
  (`2026-09-04-caelestia-fundido`, la ultima de las cinco de dentro de la ventana; **cierra las seis
  fases del tema**). La escena `#contacto` deja de ser la carta de ajuste compartida y pasa a ser
  **la contraportada del escritorio**: la UNICA de las cinco que invierte a un campo `--cae-primary`
  a sangre en vez de ser una ventana de aplicacion — eso solo ya la hace legible como final sin que
  nadie lo explique. Dentro, un troquel de Material 3 de 240 vertices que sangra 10 px al canto, con
  el dino de Chrome sin conexion de pie sobre el horizonte.
  - **Cuarta voz tipografica**, `--cae-display-axes-cierre` (italica, `opsz 144`, `wght 300`,
    `SOFT 100`, `WONK 1`), en un unico sitio de todo el sitio: la frase de cierre a `--t-10`
    (159,66 px), que **ablanda** desde la voz del cartel de B1 mientras aterriza.
  - **El fundido suena UNA VEZ por sesion** (1900 ms); cada regreso son 440 ms de entrada, que caben
    dentro de los 520 del deslizamiento del carril. Un final que suena cada vez no es un final.
  - **Los cuatro canales pesan distinto a proposito**: dos ACTOS (`mailto:`/`tel:`, sirven sin red,
    85 px de alto) y dos DESTINOS (externos, necesitan red, 42 px). Cuatro columnas iguales dirian
    que son intercambiables, que es falso.
  - **390 px SI entra en el alcance**, al reves que en B1-B4: una escena de contacto que solo
    funciona en escritorio se contradice a si misma. El troquel deja de sangrar y pasa a ser un
    sello cuadrado de 196 px con 8 lobulos en vez de 12 (la complejidad del lobulo baja con el
    tamano, regla del propio Material 3).
  - **Rozar pinta la caja accionable** que el relleno con margen negativo ya creaba: Caelestia era
    la unica de las tres pieles cuya llamada a la accion principal no respondia al raton.
  Lo vigila `scripts/measure-caelestia-fundido.py` con **14 familias de aserciones (95
  comprobaciones)**, todas vistas en rojo contra su propio sabotaje.
  **La leccion que mas costo esta fase — y no la cazo ningun gate hasta el ultimo:** irse de la
  escena A MEDIA PASADA del fundido y volver dejaba el sello roto **para el resto de la visita** (el
  dino congelado medio fuera, la nube invisible, el horizonte a 0,91, y la zancada corriendo para
  siempre). La causa: `aterrizado()` mantenia **a mano** la lista de lo que devolver y se habia
  desincronizado de la partitura, y `pararZancada()` era el `onComplete` del tween del bicho — que
  `kill()` NO dispara. **Una lista en dos sitios se rompe en cuanto alguien anade un tween**: ya no
  hay lista, `anotar()` lee las dianas de la partitura misma al construirla.
  Y **van trece instrumentos rotos** entre la fase A, B2 y B5. Tres de ellos son la misma familia
  nueva: **el cronometro miente en esta sandbox**. Un `setTimeout` dentro de la pagina llega con
  cientos de ms de retraso con `--use-gl=swiftshader`, asi que el gate del camino interrumpido salia
  **rojo bajo carga y verde en vacio**. Los cortes se anclan al ESTADO, no al reloj — y si el punto
  de corte no llega, el gate FALLA en vez de medir otra cosa.
  **Aviso para quien toque el arnes de Obra (B3):** falla con tres hallazgos de contraste y **fallaba
  igual antes de fusionar B5** (comprobado en un worktree aparte). Por la pinta —`bg=rgba(0, 0, 0, 0)`—
  es su propio instrumento, que no resuelve el fondo pintado de verdad: la misma trampa que el arnes
  de B5 corrigio apilando los fondos translucidos hasta el primero OPACO.


- **La fase B6 (movil y tableta) de Caelestia: TERMINADA** (`2026-09-07-caelestia-movil`, rama
  `design/caelestia-movil`). B1-B4 dejaron fuera las pantallas estrechas a proposito; Aoshi abrio el
  sitio en su telefono al cerrar el repaso de interfaces y cuatro de las cinco escenas no cabian
  (Titulo justifica a una medida fija de 1080, Quien soy desbordaba 847 sobre 362, Obra 1316 y
  Stack 1364). **La ley elegida es la opcion A: cada workspace se desplaza por dentro**; el
  documento sigue sin desplazarse nunca y el desplazamiento interior vuelve a cero al cambiar de
  escena. Dos bandas: **compacta** (`max-width: 900px`) y **media** (`901-1365px`, tableta
  apaisada). Titulo pasa a **«Silencioso»** (sin tarjeta «Ahora mismo», sin columna de cifras y sin
  figura viva: tres lineas de prosa, cuatro cifras y un pie), Quien soy a una columna, Obra a
  carrusel con iman donde la centrada es la elegida, y Stack apila sus cuatro bandas. Un gesto por
  escena, todos por debajo de 900 ms. Lo vigila `scripts/measure-caelestia-movil.py` (10 familias,
  143 comprobaciones, a 390x844, 768x1024, 1024x768 y 1180x820).
  **Las dos lecciones de instrumento valen mas que el CSS:**
  1. **`scrollWidth`/`scrollHeight` mienten en los dos ejes.** El campo inundado de Contacto es un
     `<span>` con `transform: scale(5,7)` dentro de un `overflow: clip` y los infla a 1835 y 1629
     sobre una escena que se ve entera. Los gates 1 y 2 miden el CONTENIDO —nodos con texto propio
     o accionables— contra el `getBoundingClientRect()` del workspace.
  2. **El indulto de «alcanzable deslizando» NO vale hacia arriba.** Un contenedor en `scrollTop` 0
     no puede desplazarse hacia atras. Con el indulto generico el gate salia **VERDE contra el
     fallo real**: la cabecera de Stack heredaba `height: 96px` de escritorio (`min-height: 0` no
     lo desactiva) y, centrada sobre 135 px de contenido, sacaba el nombre de la pieza 24 px por
     encima del panel.
  `lidia-naive-tester` 7/10 sin P0. `vera-art-director` **BLOCK 6,22/10**, residual aceptado como en
  Vice, el shell, B1 y B4 — pero **su P0 era real y se arreglo antes**: a 1024x768 el nombre de
  Quien soy quedaba 12 px bajo la barra fija. La causa estaba en B2:
  `[data-ficha="neofetch"]` centra con `justify-content: center` y `height: 100%`, asi que en una
  caja mas baja que su contenido el sobrante se reparte a los dos lados y lo de arriba no lo
  alcanza nadie. Ahora es `safe center` (no mueve nada donde ya cabia) y en la banda media la caja
  crece. **El mismo fallo estaba en `main`** a 1366x768 y 1280x720, portatiles corrientes, con 11 y
  35 px del comando bajo la barra.
  Abiertos y anotados: ~~la deuda de escala tipografica~~ (CERRADA el 2026-09-07, bloque siguiente), el titular
  todavia tecleando a 1,5 s medido bajo `swiftshader` —donde el cronometro miente— y una banda
  negra de 27 px bajo el panel en las tres escenas con panel desplazable, que **sale igual en
  `main`** y solo bajo emulacion de dispositivo, asi que apunta al compositor del headless.

- **La escala tipografica: CERRADA y vigilada** (`2026-09-07-escala-tipografica`, rama
  `design/escala-tipografica`). Vera la marcaba por **septima vez** —fase A, B1, la tarjeta «Ahora
  mismo», B4 y B6— y cada vez se acepto como deuda conocida. La escala existia (cuarta justa, razon
  1,333, diez escalones de 12 a 159,66 px); lo que no existia era **la obligacion de usarla**: 69 de
  177 declaraciones de `font-size` llevaban literal, con 39 valores distintos, y 57 de esos
  literales eran de Caelestia.
  **Que cambia:** un escalon bajo el suelo, `--t-0` (10,67 px), con razon **1,125 y no 1,333** —
  deliberado: a 10 px el ojo distingue un escalon de 1 px y a 120 no distingue quince, asi que una
  razon unica en todo el rango deja o sin tallas abajo o con quince arriba que nadie usa. (Salio con
  **dos** escalones bajo el suelo, `--t-00` a 9,5 px y `--t-0` a 10,67 px — ver «Los escalones que
  se fundieron» mas abajo para el porque de que ahora solo quede uno.)
  La escala se declara **UNA vez y en `:root` a secas**, donde estaba repetida tres veces
  (una por tema, identica) mientras `style.css` la consumia con **17 respaldos**
  (`var(--t-1, 0.53rem)`), que eran una segunda escala escondida: el numero que se pintaria si el
  token faltara. Los 57 literales pasan a su escalon mas cercano, mediana **0,50 px**, maximo 3,90.
  **La unica excepcion va por SELECTOR** (`#hero .cae-ln`): el titular de B1 se justifica midiendo el
  texto y estirandolo hasta la medida, asi que su tamano lo decide el ancho de la caja. Un segundo
  elemento con tamano en linea pone el gate en rojo.
  Lo vigila `scripts/measure-escala-tipografica.py` con **dos familias que se vigilan entre si**. La
  estatica lee el fuente; la viva lee el `font-size` **computado** de todo lo que pinta texto, y no
  es redundante: caza cuatro tallas que ninguna regex podia ver — un `0.92em` que resultaba en
  14,72 px, un `font-size: 0` usado como truco de ocultacion (ahora un `<span>` visualmente oculto,
  mejor que antes: el nombre no sale del arbol de accesibilidad) y un `<small>` que el navegador
  encogia a 7,60 px con su propio `smaller`.
  **Las dos lecciones que costo:**
  1. **`--t-0` YA existia a 9 px**, declarado por B5 para la rotulacion mono de Fundido, con un
     comentario que hace el mismo argumento que este spec — *la sexta vez que ese defecto aparecia*.
     Esta reparacion ya se habia empezado una vez, en pequeno, y se quedo en tres selectores. Y peor:
     al mover la escala a `:root`, esa declaracion vieja **sobrevivio y ganaba por especificidad**,
     asi que dentro de Caelestia el token seguia valiendo 9 — y **el gate estaba ciego**, porque
     comprobaba que `--t-1` se declarara una vez, no los doce.
  2. **Un empate lo decide el suelo de accesibilidad, no el orden de una lista.**
     `.cae-obra-caption` estaba a 14 px, exactamente a 2 px de `--t-1` y de `--t-2`; el script que
     armo la tabla rompio el empate hacia abajo sin criterio. A 12 px el glifo adelgaza y el
     contraste bajo el derrame de la gota cae a **4,21:1 en Obra a las 04:30**, por debajo de AA.
     Ahora es `--t-2`.
  Los literales de Hyprland quedan fuera de alcance a proposito hasta que cierre su rediseno; Vice
  solo pierde la declaracion duplicada, que son los mismos numeros.
  **Los escalones que se fundieron (2026-09-08):** `vera-art-director` midio los dos escalones bajo
  el suelo a triple densidad y `--t-00` (9,5 px) y `--t-0` (10,67 px) —1,17 px de distancia— se leian
  como una unica talla donde de verdad conviven en el mismo encuadre: la barra (`.cae-mark` a 10,67
  junto a `.cae-ws-n` a 9,5) y el cajon de Obra (`.cae-obra-drawer-kick` a 10,67 junto a
  `.cae-obra-drawer-meta dt` y `.cae-obra-prose h4` a 9,5). Si dos escalones se leen como uno, son
  uno: se fundieron en un unico `--t-0` a 10,67 px, la escala tiene **once** tokens y no doce, y las
  18 declaraciones que pedian `var(--t-00)` pasan a pedir `var(--t-0)` (las 6 que ya pedian
  `var(--t-0)` no cambian). Crecer 1,17 px movio el peor caso de la cabecera de Stack
  (`.cae-cred-cab`) de 248 a **251 px**, asi que su `min-height` en telefono paso de `15.5rem` a
  `15.6875rem` — el gate 5b de `measure-caelestia-movil.py` confirma `[251]` uniforme en las 23
  piezas.

---

## Anexo — versión inglesa (del CLAUDE.md raíz, hasta el 2026-10-29)

### Theme Status
- **Vice: DONE.** Closed with the `2026-08-04-vice-fondo-tinta` plan (background `viceInk.ts`, a
  two-ink halftone poster; the scene-nav trigger lost its box, gained a register mark). Reviewed
  live by Aoshi, `lidia-naive-tester` gate green, `vera-art-director` gate BLOCK explicitly
  accepted (7.12/10 against a 7.5 gate — the residual is a known, accepted product finding, not a
  defect). **Do not touch Vice** (background, nav trigger, choreography, typography) unless Aoshi
  asks for it explicitly. Full record in `docs/superpowers/specs/2026-08-04-vice-fondo-tinta-design.md`.
- **Caelestia: all six phases (A, B1-B5) are MERGED.** The theme's design is closed; two things
  keep it from being DONE, and neither is design work: **B3 needs the nine real project captures**
  (today they are "CAPTURA PENDIENTE" markers painted in *Vice's* palette) and **B4 has two open
  product P1s**. Also open: `measure-caelestia-obra.py` fails three contrast assertions — **it failed
  the same way before B5 merged** (verified in a separate worktree against `1f61752`), and the shape
  of the failure (`bg=rgba(0, 0, 0, 0)`) points at its own instrument, not at the CSS. Read each
  phase's block below before touching anything.
- **Caelestia's interface review with Aoshi (2026-09-05/06) is MERGED into `main`** (`1c246eb`,
  branch `fix/repaso-interfaces`, not pushed). Nine dictated faults fixed one by one, each with
  its gate seen red first: the hero no longer paints before the choreography arrives
  (`js-cae-entrada`), the shell toast no longer fires on load, the terminal leaves before the
  name is traced, bar and dock enter (CSS, `no-preference`), the Obra drawer fills the window as
  an elevated sheet with layered text relay, C and Zustand icons from Devicon Plain, scenes 4/5
  renamed **Stack** and **Contacto**, the "Disponible" chip left the bar. Two design changes came
  out of it: the **"Ahora mismo" card** was redesigned (`2026-09-05-caelestia-ahora-mismo`, order
  who/what/status, no box, live 240-vertex figure, entrance blooming from its light; Vera 6.6
  BLOCK residual, Lidia 6.4) and the **Contacto dino is a toy** (jump, eye follow, and dragging is
  a *glance* at another hour that undoes itself on release; the troquel spins with a spring and
  **the generative background follows the glance** via `caelestia:hora`). Full record, including
  the ten mistakes paid during the session (measuring at 1412x748, a commit claiming
  `verify.py` green while it was red, subagents stalling on background monitors, OOM with
  parallel harnesses, the hour hook not reaching the background), in
  `docs/superpowers/specs/2026-09-05-caelestia-repaso-interfaces.md`. **Do not re-measure the
  card at 1412x748**: that is the inner window with a 1440x900 page.
- **Hyprland and Caelestia: IN PROGRESS.** Current focus. They share `shaderBackground.ts` with
  Vice (don't touch that module without confirming Vice still renders) but each has its own
  background (`hyprGradient.ts` / `caelestiaBlobs.ts`), palette, and typography — see `src/themes/themes.css`.
  The obra section in Hyprland has a new device (the cartel, `2026-08-10-hyprland-obra-cartel`
  plan and spec): five titles always on screen, captured screenshot travels with GSAP Flip into a
  large viewer on click. Contrast against the real shader background measured per-glyph (not
  viewport-wide, which overstated it): only the resting title dips below AA, and only in the
  shader's brightest 0.5% of frames (3.88:1) — a shader brightness ceiling, pending a product
  decision, not an illegibility problem (see the spec's `Registro de implementación` /
  `Color y contraste`). The "Con qué construyo" section (the Stack scene) was redesigned and
  merged on 2026-09-10 — see its own block below. Hyprland overall stays IN PROGRESS.
- **Hyprland's cursor is DONE and merged** (`2026-08-19-hyprland-cursor-luz`): "the adaptive
  hollow". Pointing at something pressable opens a pool clipped to the element — it **darkens
  where the background is bright and lights up where it is already dark**, with the edge lit and a
  dot marking the hand; over running text it goes out and the system cursor takes over. The sign is
  decided by the luminance of the background occluding the `z-index: -4` canvas, read once per
  target. Two mechanisms: the canvas for targets with nothing opaque above it, an inline
  `background-image` for the rest (it paints above the element's own background and below its
  text). `scripts/measure-cursor-luz.py` gates it, and its **assertions are split by family** —
  the darkening one must improve contrast, the lighting one must hold an AAA floor *and be
  perceptible*. One gate for both could only demand what holds for both, which is nothing, and that
  already slipped through once. Read the spec's epilogue before re-tuning anything: the whole
  calibration predates the `gsap` fix.
  - **The edge is gone: it is "la brasa" now** (`2026-09-10-hyprland-cursor-brasa`, merged
    2026-09-10, spec `implementado`). The device used to draw a 1px `--l1` `strokeRect` around each
    pressable's **whole box**, and Aoshi rejected it twice over: the box, whatever its colour, and
    that it was the *complete* box. It is replaced by a 2px segment of the **bottom edge only**,
    centred on the pointer's x, feathered to zero at both ends and clamped to the box. The width
    inherits the pool's own law (`radio · 0.75`, and `radio` is dictated by the element's height,
    not the section): ~90px on a Stack name, ~194 on an obra row 1440 wide. **Clamping makes the
    wide case contain the narrow one for free** — on a target narrower than the segment the brasa
    covers the whole edge, which was the discarded option A, with nobody coding the case. 2px in
    `--l1` is not a free choice: it is the same token and thickness as `.cim-suelo`'s `border-top`,
    the ember floor the Stack scene had shipped the day before.
  - **The pool's clip is feathered, not removed.** `PLUMA = 14`px inward from each edge, erased with
    `globalCompositeOperation = "destination-out"` on the `hueco` canvas. The clip itself stays —
    it is the only thing that says how far the pressable area reaches — but its hard cut was reading
    as a box in its own right on the shader's bright frames, where the pool darkens.
  - **`PLUMA = 14` was chosen against a rule this spec itself had written**, and that is the
    decision most worth not undoing. The rule said "the contrast family must come back with today's
    numbers or better; if it drops, cut the pluma". Followed literally it drove `PLUMA` to 5 — and
    at 5 the clipped pool paints a dark rectangle with straight edges around the name, which is the
    exact defect the spec exists to remove. Measured A/B on one build: `PLUMA` 0 → 15,06:1,
    5 → 15,06:1, **14 → 13,96:1**, 24 → 13,68:1, 36 → 13,47:1 (worst-case per-glyph on
    `.obra-abrir`). What the gate actually demands is not a ratio, it is that the pool **improve**
    contrast by at least 0,15; at 14 it improves it by 0,64, **4,3x the floor**, with the absolute
    worst case at 13,96:1 — 3,1x AA. The order of priorities is now written in the spec: first the
    accessibility floor, then that it must not read as a box, and only then the absolute ratio.
    The pool's calibration (`HUECO_*`, `LUZ_*`, `LUM_OSCURA`) stays untouchable either way.
  - **The pluma is for the canvas mechanism only.** The inline `background-image` branch keeps its
    hard cut plus a comment tying the feather to an open commission: that mechanism paints nowhere
    today (its only target, `.credit`, went with the catastro), so no gate could ever see it red.
  - **The harness had never once looked at this signal.** An orange rectangle framed every link on
    the site for weeks with `measure-cursor-luz.py` green, because it watched the pool and never the
    edge. Three families were added — the signal does not enclose the target (only the bottom edge,
    never the four), the brasa follows the hand (its centre of mass moves with the pointer), and the
    pool dies inward with no hard step at the edge — **plus a fourth on a narrow target**, because
    on `.obra-abrir` (1440px) the clamp never executes and a regression removing it would go
    unnoticed. All four were seen red against the real failure before being accepted.
  - **Two of those gates were themselves tautological on the first pass, and both were caught.** The
    step-based one came out **green** against the un-feathered code: `.obra-abrir` spans the whole
    viewport so it has no "outside" on the left, and the top edge shares a pixel with the next
    scene's `border-t`, a static element that dominated the reading. It measures the delta row by
    row between lit and unlit now, which cancels anything static, and the metric is the **width of
    the ramp** (rows from 10% to 90% of the plateau), calibrated live: 11/11/11/11 rows at
    `PLUMA = 14` against 5/4/4/4 at `PLUMA = 5`, threshold 8. The earlier threshold accepted a ramp
    of ~3px, so **`PLUMA = 5` passed the gate that existed to defend `14`** — the only thing holding
    the value was a comment. It also gained an amplitude floor: with no pool to measure (module
    absent, `pot` never rising) it used to compare noise against noise and pass; it now fails
    saying so, and that was seen red by aborting the `hyprCursor` chunk over the network.
  - Gates: `lidia-naive-tester` **7,8/10, would contact, zero P0** — she checked the contiguous
    Stack names ("C" next to "C++" and "CSS") and the brasa never picks the neighbour.
    `vera-art-director` **BLOCK residual 7,3/10, zero actionable P0s**, same shape as Vice (7,12)
    and the cimientos (7,42); she verifies per-pixel that all four edges are single smooth peaks
    with no step, and that the signal went from **+0,003 to +100/255** of luminance delta on
    `.hero-mail` — from imperceptible to unmistakable.
  - **`.hero-mail`'s focus ring — closed 2026-09-10, and the diagnosis it arrived with was wrong.**
    The finding said "no focus indicator at all". Measured, there was one: `:focus-visible` moved
    the colour from `--haze` to `--l1` and grew a 1px `::after` underline. The real defect is
    sharper — **those two colours are 1,03:1 apart**: the hue goes brown to orange while the
    luminance barely moves, so for anyone with reduced colour discrimination the only cue was a 1px
    line, half the 2px perimeter WCAG 2.4.11 asks for. It now carries the theme's keyboard ring,
    `outline: 2px solid var(--l1)`.
    **The offset must be negative, and that is not taste.** `.hero-mail` carries `.hypr-cut`, which
    leaves a `clip-path` in place even at rest (`inset(0 0 0 0)`, fully open) — and **a `clip-path`
    clips the outline too**, so a positive offset paints nothing while `getComputedStyle` cheerfully
    reports `solid 2px`. That is why the original author used `outline: none` and an `::after`
    underline. Two assertions in `verify.py`'s hyprland block cover it, both seen red: one that a
    ring of 2px or more exists, and one that the offset is never positive on a clipped element —
    **the only assertion in the harness that treats the computed style as insufficient evidence
    that something paints**. Note `verify.py` walks Vice by default: this block needs
    `--theme hyprland`.
  - Also open: the keyboard focus ring on `.obra-abrir`/`.cim-nombre` is still the
    2px `--l1` full box Aoshi just vetoed for the mouse (not an error — a strong outline is correct
    for accessibility — but the two channels now speak different vocabularies, and whether to close
    that gap is a product decision); and the pool goes out entirely over an obra row's thumbnail,
    because the image paints above the button covering the row and the cursor resolves the image,
    which is not in `PRESSABLE`. That last one is **not a regression** — the old edge died there
    too — and it is the same family as the occluded-target commission.

- **Hyprland's Stack scene is MERGED** (`2026-09-09-hyprland-stack-cimientos`, spec state
  `en ejecucion` until Aoshi reviews it on the real site): the catastro is retired and
  `[data-scene="credits"]` is now **"los cimientos"** — three area columns from `skillGroups`
  (Interfaz 8, Backend y datos 5, Herramientas 5, widths 550/344/344 at 1440, ratio 1.6/1/1) over a
  2px `--l1` floor line carrying the five base languages one type step **above** the names. The
  composition is the sentence: three things he builds, resting on five things he knows. **There is
  no hierarchy between the 23 names** — the old device sized them by how many projects used them,
  and that data does not stretch (seven technologies appear in no public project, the four
  transversal ones appear in all five). The hierarchy is between strata.
  New module `src/components/hyprStackCimientos.ts`, **no GSAP**: an `IntersectionObserver` decides
  when, CSS marks the times. **`credits.ts` is NOT touched** — its generic DOM is hidden whole,
  the pattern Caelestia's B3/B4 proved. Retiring the catastro removed 1,662 lines (797 CSS, 526
  harness, 339 choreography) with Vice and Caelestia byte-identical, verified by `git worktree`.
  Gated by `scripts/measure-cimientos.py` (14 families; gate 10, the contrast one, sits behind
  `--contraste`). Contrast per glyph against the live shader: name 9.66:1, area label 5.79:1,
  language 15.65:1, icon 6.53:1 against a 3:1 decorative floor, hovered 9.66:1, phrase 9.35:1.
  - **The entrance is commanded by the floor**: the ember line traces left to right, lights the
    five languages in its wake (each delay derived from its own x, not written by hand), and only
    then do the columns grow from it by clipping. One lighting in the scene, not twenty-three.
    Its trigger is anchored to the **device's own box**, never the section's — the same fix this
    branch made to the placa, where an entrance ran to completion 119px below the fold for a month
    with the harness green.
  - **The phrase lives in the air, not under the floor's label.** Hovering, focusing or tapping a
    name lights it `--l3` and writes that technology's literal `detail` in Instrument Serif italic
    inside the 48px of air between the columns and the floor. It first sat beside "LENGUAJES BASE",
    and **both critique gates independently called that a defect**: for the 18 names that are not
    base languages it read as a template bug. Moving it up costs zero pixels — the air was already
    there — and the 48px gap the gate measures is unchanged.
  - **What the harness had to learn the hard way, twice.** A mouse click used to extinguish the
    name under the cursor: `blur` on the previously focused button fired `apagar()` without
    checking who was active. And **gate 4 never clicked with a mouse anywhere** — it hovered,
    tapped and used the keyboard — so a gate titled "the hover extinguishes on leaving" was green
    while ordinary clicking blanked the device. Separately, `gate 6` compared the painted phrase
    against the DOM's own copy of the string, both written by the same line: it now parses the 23
    `detail` values out of `content.ts` and fails loudly if the parse comes back empty.
  - **Two rulings worth keeping.** The reduced-motion guard is written selector by selector on
    purpose (`*` does not reach pseudo-elements) and the apuntado rule is scoped with
    `[data-cimientos]` so it beats the entrance rule **structurally**, not because it appears later
    in the sheet. Below 1024px the device stacks: between 821 and 1023 the 8/5/5 proportion
    collapses to equal columns and "Claude Code" wraps, so the stacked band runs to 1023 and gate
    8 only measures three columns from 1024 up.
  - **`measure-cursor-luz.py` now exits with exactly 1 expected failure**, and that is written in
    its own docstring. Retiring the catastro removed `.credit`, its **only occluded target** — the
    one exercising the `background-image` mechanism instead of the canvas. `.cim-nombre` is not a
    replacement (the cimientos have no opaque background), so the harness says what is missing and
    since when instead of substituting a softer target. **Giving that family a new occluded target
    is an open commission.**
  - Open, and recorded in the spec: ~~the cursor's orange edge around the 23 new buttons~~ (closed
    2026-09-10, see the brasa block), ~~the scene selector's stale silhouettes~~ (closed 2026-09-10,
    see the selector block below), retiring the dead nodes
    `credits.ts` still builds (`.credits-rail`, `.credits-glow`, `.credits-spark` and
    `STRIP_REPAINT_EVENT`, which now has no listener), that `8fr 5fr 5fr` is hand-written and
    mirrors counts that live in `content.ts` with no gate comparing them, and that
    `measure-cimientos.py` is hooked nowhere — it is launched by hand, by decision.
  - Gates: `lidia-naive-tester` 6.3/10 red on the phrase's old placement, **fixed**;
    `vera-art-director` **BLOCK residual 6.22→7.42/10**, 0.08 under the gate, **zero actionable
    P0s**, and she certifies that the two findings which blocked the catastro are closed by
    construction. Residual accepted: the 1px `--rule` dividers are indistinguishable from the
    shader in the lower third of each column (measured pixel by pixel; it is the token's luminance
    sitting inside the shader's range, the same brightness ceiling the theme already carries), and
    GSAP's icon is a wordmark that does not scale like the rest of the set at 20px.

- **Hyprland's scene selector is MERGED** (`2026-09-10-hyprland-selector-siluetas`, spec
  `implementado`). The index paints five **silhouettes** — each scene reduced to its structure,
  drawn in a **1440x900 plane** the CSS scales into the card. They are **hand copies on purpose**:
  the index paints with the curtain closed, before the scenes are fully mounted. The module's own
  header had declared the price from day one — *"they can age: if a scene changes device and its
  silhouette does not, the sheet lies in silence"* — and it came due: **four of the five** no longer
  matched. `creditos` still drew the catastro retired the day before (a grid of bars and a dot
  reading "React"), `obra` drew a horizontal rail of columns when the scene is five stacked rows,
  `quien-es` and `contacto` had drifted the same way. Only `hero` was faithful.
  - **The harness could not see any of it, by construction.** `measure-cortinilla.py` measured HOW
    the silhouettes paint — five of them, none empty, the plane scales, no piece under 1px on mobile
    — and never compared them to the scene.
  - **The instrument that was discarded matters as much as the one that shipped.** The first design
    asked "does the silhouette resemble its scene?" (grid-occupancy Jaccard). It does not separate:
    across grids from 2x2 to 20x12, with Jaccard, density correlation, cosine, and text-only and
    border-only subsets, the order came out inverted — `creditos`, entirely obsolete, scored **above**
    `hero`, the only faithful one. *"Does this still represent the current device"* is a semantic
    judgement a rectangle overlap cannot see. The implementer **stopped instead of moving the
    threshold**, which is the doctrine working.
  - **The shipped gate changes the question** to the one that actually failed: **has a scene changed
    without anyone revisiting its silhouette?** The drift was not the problem; the silence was. Real
    ink per scene is extracted from the DOM (own-text nodes and visible borders, rects relative to
    the scene's own origin, `reduced_motion="reduce"`), quantized and hashed against blessed
    signatures in `scripts/scene-nav-firmas.json`, with `--update-firmas <scene>` to bless — the same
    idiom `verify.py` uses with `--update-baseline`. **It does not check that a silhouette is
    correct**, only that nobody changes a scene without passing in front of it, and it says so in its
    own docstring.
  - **Bless one scene at a time.** Blessing all five buries the red of a scene nobody looked at.
  - **The transposition blind spot was closed, not accepted.** Hashing the union of lit cells gives
    the SAME hash for a row/column transposition covering the same cells — exactly the drift `obra`
    suffered. It hashes the **multiset of per-piece cell boxes** `(c0,r0,c1,r1)` now: four integers
    that were already computed and thrown away. It also closes the other declared limit (new content
    landing in an already-inked cell). **A limitation you close by moving four integers is a
    decision, not a limitation.**
  - **The repaint's own trap, and the one the reviews caught.** Silhouette pieces must fall inside
    the plane: the frame is `overflow: hidden`, so a piece that overflows is clipped in silence. It
    happened — `obra` took its coordinates from the **viewport at one scroll position** instead of
    the scene's frame, and two pieces reached y=940 on a 900 plane, so **the five-row scene was drawn
    with four and a half rows**. The assertion that should have caught it counted only pieces
    *entirely* outside the frame, and partial clipping is the only kind a repaint produces. It
    detects partial clipping now, plus a static check that every piece fits in 1440x900.
    Measuring that scene is genuinely tricky: `[data-scene="obra"]` reports a `getBoundingClientRect()`
    ~109px tall while its five absolutely-positioned rows span ~547. **The section's box does not
    describe what is on screen.**
  - Three more assertions the branch had to add: partial clipping (above), that every `disp` literal
    still exists in the real content (changing a text almost never moves cell occupancy, so the same
    silent drift came back through the other door), and that the three scene lists agree —
    `SILUETAS`, the signature selectors, and `content.ts`.
  - `emite()` no longer exempts text pieces from the minimum-body rule: it was written for 1px accent
    strokes, and it was letting "Disponible para proyectos" survive on mobile at **3.8px** — the very
    blotch `CUERPO_MINIMO` exists to prevent — while hiding the name that identifies the card.
  - **Environment trap found on the way:** `vite preview` returns **200 `text/html` for any path**
    (SPA fallback), so probing `/@vite/client` by status code gives a false positive. Probe by
    content-type. And the harness now measures everything against `--base`: requiring the flag only
    for the signatures while six other families still pointed at a hardcoded dev-server URL broke the
    documented command and left the families that measure silhouette geometry — the ones that should
    have caught `obra` — reading a page with HMR.
  - Piece counts, before -> after: `quien-es` 20 -> 16, `obra` 42 -> 16, `creditos` 32 -> 24,
    `contacto` 23 -> 18. Fewer pieces and a closer likeness, which is the sign it summarized instead
    of tracing.
  - Open: the silhouettes are still hand copies. Deriving them from the DOM would remove the whole
    class of bug but collides with why they are hand-made, and would redesign a closed device —
    Aoshi chose repaint plus gate, and the alternative is recorded as not taken. The harness also
    carries **2 pre-existing failures on Caelestia's trigger**, verified identical on `main` in a
    separate worktree.

- **Caelestia's cursor is BUILT and gated, pending merge** (`2026-09-04-caelestia-cursor`, branch
  `design/caelestia-cursor` in the `portfolio-aoshi-cursor` worktree): **"la gota"** — a drop of the
  hour's pigment. It is a theme-wide device, not one of the B1-B5 phases. Over pressables it tenses
  into a pearl and waits; **on click it spills and floods the target to its edges**; over
  hover-select targets (`button[aria-pressed]`, the Credits pieces) it spills on entry instead. Over
  running text it goes out and the system I-beam takes over. The two states are not two symbols —
  they are **one gesture fired at two moments**, which is how it satisfies "a cursor cannot have a
  manual". DOM, not canvas (it needs `backdrop-filter` and `mix-blend-mode`), and **no GSAP**: CSS
  transitions only, so the mount stays synchronous. No trail, no positional inertia.
  `src/components/caelestiaCursor.ts`, gated by `scripts/measure-caelestia-cursor.py` (8 gates, 53
  assertions, every one seen red against the failure it claims to catch).
  - **The night spill's opacity is 0,20 and the day's is 0,22 — do not unify them.** They are
    different mixes: `multiply` over light paper darkens the text's background, `screen` over dark
    surface lightens it, and that is what eats contrast. At 0,30 the Obra caption fell to 4,06:1 at
    06:30, below AA; at 0,20 the worst of the 24-hour sweep is **4,92:1**. The margin is 0,43, not
    an order of magnitude — re-run gate 6 whole before touching it.
  - **The spec's fallback (paint the spill under the text as an inline `background-image`, the
    Hyprland pattern) is worse here, not a safety net**: a `background-image` paints below the
    element's children, and the Obra card has an `<img>` filling its box, so the spill would vanish
    in the scene where it shows most. That open question is closed.
  - `destroy()` retires live rings **through `retirarCerco`**, never a raw `remove()`: it is the
    only path that also cancels their 1200ms backstop timer.

- **Caelestia's shell is DONE and merged** (`2026-08-20-caelestia-escritorio`, phase A of six): the
  theme stopped being a set of tokens and became **a Material You 3 desktop shell whose colour and
  scheme are governed by the visitor's clock**. The hue walks the full 360-degree wheel over 24
  hours; lightness never moves, so **contrast is invariant by construction** — measured once, valid
  for all 1440 clock positions. Scheme is light 07:00-20:00, dark outside, and **never interpolated**:
  surface and text swap lightness order, so any continuous path between schemes crosses 1:1 contrast.
  Proven in motion, not just by arithmetic: sampling every ~15ms across the threshold, `L` jumps
  0.245 to 0.925 in one step with no intermediate value in 90+ samples.
  The five scenes are a **horizontal workspace rail** — a workspace is not scrolled, it is switched —
  so the theme has no page scroll and inactive workspaces are `inert`. `sceneNav` is hidden here
  (`display: none`): the bar already carries the five scenes as always-visible pills, and its panel
  changed the hash without moving anything. Fraunces (`opsz 9 wght 900 SOFT 0 WONK 1`) over Hanken
  Grotesk and Martian Mono. `scripts/measure-caelestia-hora.py` gates it with 16 assertions.
  **Phases B1-B5 (the five sections inside the window) are NOT done** — *true when phase A closed;
  all five are merged today, see their blocks below.* Their layout still assumed a page that
  scrolls, so cramped content inside a workspace was expected, not a defect.
  `vera-art-director` gate BLOCK explicitly accepted (6.55/10 against a 7.5 gate), same as Vice: its
  P0 was fixed, its three P1s are open product decisions recorded in the spec.
  **Read the spec's `Registro de implementación` before re-tuning anything.** It records the lesson
  that cost this phase most: **eight times the failure was in the instrument, not the design** — a
  regex reading `oklch()` as RGB bytes (1.00:1 everywhere), a frozen clock that made the
  threshold-crossing branch unreachable *by construction*, a PNG-size proxy that passed against the
  very shader it existed to catch, a focus assertion titled "and uses the anchor" that only read
  `outlineStyle`, contrast `PARES` watching roles that are never painted, and an A/B that triggered
  the warning it was measuring (`page.screenshot()` forces its own `ReadPixels`). The spec's numbers
  all held. **Never accept a gate you have not seen go red against the failure it claims to catch.**

- **Caelestia's phase B1 (Título) is DONE** (`2026-08-26-caelestia-titulo`, first of the five
  inside-window phases): the `#hero` scene stopped being cramped shell leftovers and became **the
  desktop presenting itself** — a justified three-line headline at `opsz 144` (the shell stays at
  `opsz 9`; two separate tokens, `--cae-display-axes-cartel` vs `--cae-display-axes`, never one
  reused), a signature and a right-edge stat column, an "Ahora mismo" widget built entirely from
  `content.ts` literals (no derived field invented — `10.º semestre` is parsed out of
  `education[0].period`'s parenthetical, not a new field), and a `whoami`-typed terminal entrance
  whose signature lands as 15 traced Fraunces glyph paths. The background is new too:
  **`src/backgrounds/caelestiaBlobs.ts` no longer exists** — it's `src/backgrounds/caelestiaFiguras.ts`
  now, five Material 3 Expressive figures (puffy/sunny/cookie/clover/burst) that morph with the
  visitor's hour and share `shaderBackground.ts` (float-uniform-only, so a `vec3`/`vec2` in the
  approved prototype got split into loose floats and rebuilt inside the shader). Hovering the
  widget or a stat nudges the whole background aside via a CSS transform, reduced-motion skips the
  entrance straight to the landed state, and the ink-sweep/number-flip closing gestures run off the
  same timeline. `scripts/measure-caelestia-titulo.py` gates it with the eight assertion families in
  its own docstrings — all eight were seen red against the exact failure they claim to catch before
  being accepted (see the spec's implementation notes for what broke each one). **Mobile is
  explicitly out of scope for B1**: the headline's justification target is a fixed 1080px measure
  with no narrow-viewport fallback, so at 390px the titles overflow and the stat column overlaps
  them — known, not a regression to chase. **B2-B5 (Quién soy, Obra, Créditos, Fundido, still
  inside the same window) remain pending** — *true when B1 closed; all four are merged today.*
  B1 only closes `#hero`.
  `lidia-naive-tester` gate green (7.1/10, zero P0). `vera-art-director` gate came back **BLOCK**
  initially (6.36/10 against the 7.5 gate) on a real P0, not a polish issue: the phase-A generic
  workspace-panel rule gave Título the same opaque `background` as the other four scenes (which
  ARE application windows), covering 78% of the generative background — fixed before accepting the
  gate (a scoped CSS exception for `[data-scene="hero"]`, reviewed, no leak to the other scenes or
  to Vice/Hyprland). Three polish findings remain accepted as known debt (a typography-scale gap
  recurring for the 5th time project-wide, widget spacing off the 4/8px grid, one repeated font-axis
  literal) — full detail in the B1 spec's implementation record and "Gates de crítica" section.
- **Caelestia's phase B2 (Quién soy) is DONE and merged** (`2026-09-02-caelestia-quien-soy`, second
  of the five inside-window phases). The `#about` scene stops being a cramped card and becomes **the desktop's
  own `neofetch` output**: a typed `~ $ neofetch` entry, a name/email/status header with a filete
  measured by `Range` (not the `<span>`'s block box, which reports the container's width), a
  `key: value` field list sourced entirely from `content.ts`, and a portrait clipped to a
  `clip-path: polygon(...)` that morphs between two Material 3 figures on hover.
  `scripts/measure-caelestia-quien-soy.py` gates it with 8 assertion families (38 checks); the shell
  harness `scripts/measure-caelestia-hora.py` (16 assertions) stays green, confirming phase A is
  untouched. **The trap not to repeat:** a `clip-path: polygon()` only interpolates against another
  polygon with the **same vertex count** — mismatched point counts (240 vs a lower count) silently
  fall back to a hard cut, no error, no warning. And `*` in a `prefers-reduced-motion` CSS guard does
  **not** reach pseudo-elements — `.ficha-k::before` needed its own explicit rule to stop animating
  under reduced motion; the generic wildcard guard missed it.
- **Caelestia's phase B3 (Obra) is MERGED but still `en ejecucion`** (`2026-09-03-caelestia-obra`,
  third of the five inside-window phases). The `#obra` scene stops being a 4964px rail inside a
  748px window (4 of 5 projects unreachable, plus internal scroll — exactly what phase A's law
  forbids) and becomes **the Editorial**: five always-visible cards (16:10 capture + Fraunces
  italic caption, alternating ±3-5° tilt that straightens on hover) in a fixed row, with a
  **drawer** opening below carrying the full project sheet. New module
  `src/components/caelestiaObraEditorial.ts`. **`src/sections/obra/projectScene.ts` was NOT
  touched** — better than the plan foresaw: that DOM stays as-is for Vice/Hyprland and under
  Caelestia `themes.css` hides it whole instead of rewriting it. Entrance gesture is **Caída**
  (cards fall with a per-card rotation and `bounce.out`; the drawer enters in four separate layers,
  never as a flat block) — no typed terminal, that would have been the third one. Gated by
  `scripts/measure-caelestia-obra.py`.
  **Why it is not DONE:** the nine real captures in `public/media/obra/*.webp` do not exist — they
  are "CAPTURA PENDIENTE" markers painted in **Vice's** palette (purple/amber), which inside
  Caelestia read as a theme error. That is a commission for Aoshi, not design debt; the visual gate
  stays blocked until they exist. Mobile out of scope, same as B1/B2.

- **Caelestia's phase B4 (Créditos) is MERGED and `en ejecucion`** (`2026-09-03-caelestia-creditos`,
  fourth of the five inside-window phases). The `#credits` scene stops being a plot-share layout
  with 10px of internal scroll, 424 dead px at the right edge and **four group labels that existed
  in the DOM and painted none**, and becomes **the package tray**: if each Caelestia scene is an
  application, Credits is the package manager — what is installed on this machine. Four equal-height
  bands (one per territory, label right-aligned in a 158px gutter), 23 fixed 142px modules, all 23
  technologies always on screen. New module `src/components/caelestiaCreditosBandeja.ts`;
  **`src/components/credits.ts` is NOT touched and NOT branched by theme** — its generic DOM is
  hidden whole from `themes.css`, the same pattern B3 proved with `projectScene.ts`.
  - **Size encodes nothing.** All 23 pieces are one size (88px, a single value in the whole DOM).
    Both possible yardsticks lie: a global one inflates Herramientas because `tooling` is in all
    five projects; a per-territory one makes JavaScript (one work) as big as Git (five).
  - **23 unique Material 3 figures**, one harmonic family, **240 vertices each** — two `polygon()`s
    only interpolate with the same vertex count. They are rebuilt at runtime from a 23-row table in
    `src/utils/figurasM3.ts` (the generator emits 167KB of literals and they are not needed:
    dividing by `rmax` is redundant once you box-fit by each axis' *span*, measured at 4.4e-16).
  - **Hover selects without clicking**; focus reaches the same. Entrance is **"la instalación"**:
    the 23 arrive as identical circles — unopened packages — and morph to their figure, in a wave by
    territory. No typed terminal: that would have been the third after B1 and B2.
  - Gated by `scripts/measure-caelestia-creditos.py` (9 assertion families). **It takes over two
    minutes** because of the 24-hour sweep: launch it with `nohup` and wait on the PID.
  **Why it is not DONE:** `vera-art-director` came back **BLOCK (5.3/10 against a 7.5 gate)`, accepted
  as residual like Vice/shell/B1 — but its two product P0s were fixed first (`2b8db2c`).
  `lidia-naive-tester` green (7.1/10, zero P0), with two open product P1s: the hover gesture is not
  discoverable, and "Aparece en" does not link to the Obra scene, breaking the *"knows X → used it
  in Y"* chain that is this scene's whole contribution. Mobile out of scope, same as B1/B2 — today
  at 390px the scene already carries 154px of internal scroll, which B4 neither fixes nor worsens.
  **The lesson that cost this phase most is about instruments, again:** the entrance ran *on mount*,
  finishing 2803ms in with the scene **4334px outside the viewport** — the signature gesture of the
  phase was never once seen. It was a regression against a pattern the same theme had documented one
  phase earlier (`caelestiaObraEditorial.ts` listens for `caelestia:workspace`). And **its gate had
  two assertions, both on the reduced-motion path**: titled "the entrance", it never checked that the
  entrance happened. It is the ninth tautological instrument in this track and the only one not
  caught by sabotage — it was caught by looking at the scene. **A gate that only measures the
  degraded branch does not watch the path the visitor sees.**
- **Caelestia's phase B5 (Fundido) is DONE** (`2026-09-04-caelestia-fundido`, last of the five
  inside-window phases). The `#contacto` scene stops being the shared carta-de-ajuste layout and
  becomes **the desktop's own contraportada**: the only one of the five scenes that inverts to a
  flooded `--cae-primary` field instead of an application window. A Material 3 figure (the
  "troquel", 240 points, bleeding 10px past the right edge, Ruling S) recorta el fondo generativo del
  escritorio; inside it, the Chrome offline dino stands on a horizon with two clouds (BSD-3-Clause
  code, but the sprite is a Google-identifiable asset — a branding risk Aoshi accepted explicitly,
  twice, recorded in the spec). A fourth type voice, `--cae-display-axes-cierre` (italic, `opsz 144`,
  `wght 300`, `SOFT 100`, `WONK 1`), used in exactly one place on the whole site: the closing line,
  set at `--t-10` (159.66px), softening from the B1 cartel voice (`wght 900`) as it lands. The
  fundido plays once per session (the first arrival at the workspace, ~1900ms: the field floods, the
  troquel opens, the line traces and softens, the dino runs in and stops); every return plays only a
  440ms entrance (content settles, the troquel breathes, the dino glances toward wherever you came
  from) — same "you don't reopen the app you're already in" rule B2 established for the ficha. Four
  contact channels split into two *acts* (`mailto:`/`tel:`, work offline, 85px tall) and two
  *destinations* (external links, need network, 42px) — deliberately unequal weight, not four equal
  columns. **390px is explicitly in scope for this phase** (B1-B3 left it out on purpose; a
  contact scene that only works on desktop contradicts the one thing it exists to do): the troquel
  stops bleeding and becomes a whole 196px seal (the figure drops to 8 lobes, matching Material 3's
  own rule that lobe complexity must shrink with size), the headline steps down to `--t-7` (67.4px,
  not the `--t-8` an earlier spec draft assumed — verified against the actual build with `Range`,
  word by word, per this project's "the build is the source of truth" rule), and the four channels
  regroup into full-width acts plus half-width destinations, all touch targets well above the
  48×48 Material floor. `scripts/measure-caelestia-fundido.py` gates it with **fourteen** assertion
  families (95 checks) from the spec's `## Los gates`, each seen red against its own sabotage before
  being accepted. Two pairs are deliberately NOT contrast-checked: the decorative
  clouds (WCAG exempts decoration) and "the day eye" — a pair that never gets painted, since by day
  the eye is the sprite's own cutout in `--cae-surface`, not `--cae-anchor`. **A real environment
  trap paid while building this harness:** this sandbox's `requestAnimationFrame`/`setTimeout`
  fire every 200-400ms under `--use-gl=swiftshader` instead of every ~16ms, so a duration-based
  "how long did it keep animating" measurement is worthless here — it measures the sandbox's frame
  starvation, not the choreography. The fix was reading GSAP's synchronously-rendered first-frame
  value (a timeline renders its tweens' start state the instant it's built and played, no frame
  needed) in the same `evaluate()` call as the click: the fundido's troquel tween starts from
  `scale(0)`, the entrance's from `scale(0.965)`, and "nothing fired" leaves it unchanged — three
  states, one synchronous read, no timing assumptions.
  **The closing round is where the real defect was, and no gate was watching it:** leaving the scene
  *mid-fundido* and coming back left the seal broken for the rest of the visit — the dino frozen half
  outside it, the cloud invisible, the horizon at 0.91 of its stroke, and the run cycle looping
  forever. Cause: `aterrizado()` kept the list of what-to-restore **by hand** and had drifted from
  the score, and `pararZancada()` was the bicho tween's `onComplete` — which `kill()` never fires.
  There is no list any more: `anotar()` reads the score's own targets as it builds. **A list kept in
  two places desyncs the moment someone adds a tween.** Gate 13 covers that path (cuts anchored to
  *state*, never to a stopwatch: with a `setTimeout` the same gate came out red under load and green
  when idle). Gate 14 covers the hover Caelestia was missing — it was the only one of the three skins
  whose primary CTA did not react to the mouse; hovering now paints the actionable box the padding
  already created, `currentColor` at 10%, so the state layer walks with the visitor's clock.
  **Thirteen broken instruments across phase A, B2 and B5.** Two of them were caught by gate 14
  itself: `CONTRASTE_JS` stopped at the first ancestor that painted *anything*, so a translucent
  state layer got composited over **white** and read 1.03:1 for text that reads fine (it now stops at
  the first **opaque** one and stacks the translucent layers); and reading a style in the same tick as
  the `Tab` returned the transition's *first* frame. **The stopwatch has lied three times in this
  phase alone.**

- **Caelestia's phase B6 (mobile and tablet) is DONE** (`2026-09-07-caelestia-movil`, branch
  `design/caelestia-movil`). B1-B4 left narrow viewports out of scope on purpose; Aoshi opened his
  phone at the end of the interface review and four of the five scenes did not fit (Título
  justifies to a fixed 1080px measure, Quién soy overflowed 847 over 362, Obra 1316, Stack 1364).
  **The law he chose is option A: each workspace scrolls inside itself**; the document still never
  scrolls, and the inner scroll returns to zero when you switch scenes. Two bands: **compacta**
  (`max-width: 900px`, phone and tablet portrait) and **media** (`901-1365px`, tablet landscape).
  Título becomes **"Silencioso"** — no "Ahora mismo" card, no stat column, no live figure: three
  lines of prose, four numbers and a footer, and the short branch is decided by
  `widget.getClientRects().length === 0`, what actually paints, never a width read in TS. Quién soy
  goes to one column, Obra becomes a snap carousel where the centred card is the selected one (the
  centre is resolved with `getBoundingClientRect()` against the track — `offsetLeft` measures
  against the workspace rail and only card 1 ever centred), Stack stacks its four bands. One
  gesture per scene, all under 900ms.
  Gated by `scripts/measure-caelestia-movil.py` (10 families, 143 checks).
  **Two instrument lessons worth more than the CSS:**
  1. **`scrollWidth`/`scrollHeight` lie in both axes.** Contacto's flooded field is a `<span>` with
     `transform: scale(5.7)` inside an `overflow: clip`: it inflates them to 1835 and 1629 over a
     scene that is fully visible. Gates 1 and 2 now measure **content** — nodes with their own text
     or focusable — against the workspace's `getBoundingClientRect()`.
  2. **The excuse for "reachable by scrolling" must not apply upwards.** A container at `scrollTop`
     0 cannot scroll backwards, so anything above its edge is unreachable. With the generic excuse
     the gate went **green against the real fault**: Stack's header inherited `height: 96px` from
     desktop (`min-height: 0` does not cancel it) and, centred over 135px of content, pushed the
     piece's name 24px above the panel, cut by its rounded edge.
  `lidia-naive-tester` 7/10, zero P0. `vera-art-director` **BLOCK 6.22/10**, residual accepted as in
  Vice/shell/B1/B4 — but **its P0 was real and fixed first**: at 1024x768 Quién soy's name sat 12px
  under the fixed bar. The cause was in B2, not B6: `[data-ficha="neofetch"]` centres with
  `justify-content: center` at `height: 100%`, so in a box shorter than its content the overflow
  splits both ways and the top half is unreachable. It is `safe center` now (a no-op wherever it
  already fit), and in the media band the box grows. **The same fault was on `main`** at 1366x768
  and 1280x720 — ordinary laptops — with 11 and 35px of the `~ $ neofetch` command under the bar.
  Open and recorded, not fixed here: the typographic-scale debt (Vera's 7th sighting) — **closed on
  2026-09-07, see the type-scale block below**. **Two other open items were closed by Aoshi on his own phone** (2026-09-07, against the
  merged `main` over Tailscale): the headline still typing at 1.5s and a 27px black band under the
  panel. Neither exists on a real device — both were the instrument (the `swiftshader` stopwatch and
  the headless compositor under device emulation; the band showed identically on `main` without B6
  and never at 1440x900). **Do not chase either again from a Playwright capture.** Full record in
  the spec.
  Two later faults Aoshi dictated after the merge, both fixed (`e4beed5`): the mobile Título block
  painted in its final state before the terminal (it was in neither the entrance-hiding CSS rule nor
  the choreography's initial states), and Stack broke on narrow phones — the tira used
  `repeat(4, 1fr)` (`1fr` is `minmax(auto, 1fr)`, so columns never shrink: 351 over 332 at 360px),
  the header figure was a flex child without `flex-shrink: 0`, and **the header changed height on
  selection (164 to 254px), so the tira moved under the finger between `pointerdown` and `click` —
  you tapped one piece and a different one was selected**. The header now has a fixed height, as
  desktop already did. The harness gained a 360x800 band and a walk over all 23 headers.

- **The type scale is closed and gated** (`2026-09-07-escala-tipografica`, branch
  `design/escala-tipografica`). Vera had flagged "no type scale" **seven times** across phase A, B1,
  the "Ahora mismo" card, B4 and B6, and each time it was accepted as known debt. The scale existed
  — a perfect fourth, ratio 1.333, ten steps from 12 to 159.66px — but **nothing obliged anyone to
  use it**: 69 of 177 `font-size` declarations carried a literal, 39 distinct values, and 57 of
  those literals were Caelestia's.
  **What changed:** one step below the floor, `--t-0` (10.67px), at ratio **1.125 instead of
  1.333** — deliberate, because at 10px the eye resolves a 1px step and at 120px it does not
  resolve fifteen, so one ratio across the whole range leaves you either with no small sizes or
  with fifteen large ones nobody uses. (It shipped as **two** steps below the floor, `--t-00` at
  9.5px and `--t-0` at 10.67px — see "The steps that merged" below for why there is only one now.)
  The scale is declared **once, on bare `:root`**,
  where it lived three times over — once per theme, identical — while `style.css` consumed it with
  **17 fallbacks** (`var(--t-1, 0.53rem)`), a second scale in the shadows: the number that would
  paint if the token were missing. All 57 literals moved to their nearest step, median shift
  **0.50px**, max 3.90px.
  **The one exception is named by selector** (`#hero .cae-ln`): B1's headline justifies by measuring
  the text and stretching it to the measure, so its size is decided by the box's width and cannot be
  on the scale by construction. A second element with an inline size turns the gate red.
  Gated by `scripts/measure-escala-tipografica.py`, **two families that watch each other**. The
  static one reads the source; the live one reads the **computed** `font-size` of everything that
  paints text, and it is not redundant — it caught three sizes no regex could see: a `0.92em` that
  computed to 14.72px, a `font-size: 0` used as a hiding trick (now a proper visually-hidden span,
  better than before: the name stays in the accessibility tree), and a `<small>` the browser shrank
  to 7.60px with its own `smaller`.
  **Two lessons this cost:**
  1. **`--t-0` already existed at 9px**, declared by B5 for Fundido's mono labels, with a comment
     making this spec's own argument — *the sixth time that defect appeared*. This repair had been
     started once already, in miniature, and stopped at three selectors. Worse: after moving the
     scale to `:root`, that old declaration **survived and won on specificity**, so inside Caelestia
     the token still read 9px — and **the gate was blind to it**, because it checked that `--t-1`
     was declared once, not all twelve.
  2. **A tie is decided by the accessibility floor, not by list order.** `.cae-obra-caption` sat at
     14px, exactly 2px from both `--t-1` and `--t-2`; the script that built the plan's table broke
     the tie downwards for no reason. At 12px the glyph thins and contrast under the cursor's spill
     falls to **4.21:1 in Obra at 04:30**, below AA. It is `--t-2` now.
  Hyprland's literals are deliberately out of scope until its redesign closes; Vice only lost the
  duplicated declaration — the same numbers.
  **The steps that merged (2026-09-08):** `vera-art-director` measured the two steps below the
  floor at triple density and found `--t-00` (9.5px) and `--t-0` (10.67px) — 1.17px apart — read as
  a single size wherever they actually sit in the same frame: the bar (`.cae-mark` at 10.67 next to
  `.cae-ws-n` at 9.5) and the Obra drawer (`.cae-obra-drawer-kick` at 10.67 next to
  `.cae-obra-drawer-meta dt` and `.cae-obra-prose h4` at 9.5). If two steps read as one, they are
  one: they merged into a single `--t-0` at 10.67px, so the scale has **eleven** tokens, not twelve,
  and the 18 declarations that read `var(--t-00)` now read `var(--t-0)` (the 6 that already read
  `var(--t-0)` are unchanged). Growing 1.17px moved Stack's worst-case header (`.cae-cred-cab`)
  from 248 to **251px**, so its phone `min-height` moved from `15.5rem` to `15.6875rem` — gate 5b of
  `measure-caelestia-movil.py` confirms `[251]` uniform across all 23 pieces.


