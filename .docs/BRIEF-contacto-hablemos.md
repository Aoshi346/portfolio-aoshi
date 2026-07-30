# BRIEF — la sección de contacto ("Hablemos")

> Escrito el 2026-07-30 al cerrar el encargo del ritmo del carril. Para arrancar una sesión
> nueva. El prompt para pegar está al final; lo de arriba es el contexto que lo sostiene.

## Qué es hoy, literal

`src/sections/contacto.ts`. Léelo entero antes de proponer nada: son 60 líneas y sus comentarios
explican tres decisiones que ya costaron un hallazgo cada una.

Estructura actual, de arriba abajo:

```
.hero-surface                       (el MISMO envoltorio que el hero, a proposito)
  p.hero-kick        "Contacto"
  h2.display-xl      "Hablemos"      clamp(2rem, 6vw, 4rem)
  p.contacto-status  identity.availability -> "Disponible para proyectos"
  p.contacto-cta     <a mailto:>     a.blanco1501@gmail.com
.hero-corner.contacto-corner
  <a tel:>  <a linkedin>  <a github>
```

`section.contacto`, `min-h-screen`, centrada vertical y horizontalmente, `text-center`,
`data-scene="contacto"`. Contenido real en `src/data/content.ts` (`identity`) — **no hay copy
inventado que limpiar**, y no lo introduzcas: el proyecto tiene regla anti-mock.

Coreografía en `vice.choreography.ts:1257`: "Hablemos" se monta letra a letra, mismo gesto que
cierra las otras piezas.

## Tres cosas que NO se pueden romper, con su razón

Están comentadas en el fichero porque cada una viene de un fallo real:

1. **La coreografía anima el envoltorio `.contacto-cta`, no el enlace.** Si animara el enlace, el
   `transform` inline de GSAP le ganaría siempre al `translateY` del hover declarado en
   `themes.css`, y el CTA se quedaría sin gesto al pasar el ratón.
2. **El teléfono es un `tel:`, no texto suelto.** Como texto obligaba a copiarlo a mano, que es
   fricción justo en el punto donde alguien decide contactar. Igual el email como `mailto:`.
3. **Vice le pone un scrim propio medible al `.hero-surface`.** Sin él, el gate de contraste no
   lograba muestrear NINGÚN elemento de esta escena sobre el vídeo (hallazgo I-1).

Y las de siempre: `rel="noopener noreferrer"` en los externos, `prefers-reduced-motion`, cero
`gsap.from`, `destroy()` en `pagehide`, un solo DOM para los tres temas — **la piel la decide el
CSS, nunca el marcado**.

## Lo que ya sabemos de esta sección por los gates

- **Lidia (naive tester), v3, 2026-07-30.** El eje de CTA subió de 4 a 6, pero **por el email del
  hero**, no por esta sección: *"el email en la primera pantalla es lo mejor que ha pasado desde
  la ronda anterior"*. Aprobó explícitamente el hover del botón: *"no es clickbait — solo cambia
  fondo, borde y una sombra suave. Sin brillo que barre, sin borde giratorio, sin animación en
  bucle."* **No lo conviertas en un botón con efectos**; ya pasó el examen así.
- **La falta de navegación va por su segunda ronda con Lidia.** A la tercera la escala a P0
  automático. Cero enlaces de menú, cero anclas internas en todo el sitio. Si esta sección va a
  ser el suelo de conversión, la pregunta "¿cómo llego aquí sin scrollear 10.700 px?" es suya.
- **Aviso serio, y es el que más pesa:** Vera tiene la escala tipográfica del tema como hallazgo
  recurrente y **va por su segunda sección** (`about` en v1.1, `obra` en v1.2). Su regla de
  recurrencia convierte la tercera aparición en **P0 automático**. Una sección de contacto
  rediseñada sin arreglar la escala sería justo esa tercera. Detalle en
  `.docs/HANDOFF-obra-siguiente-iteracion.md`, apartado F-06: 10 tamaños en una cartela, cinco de
  ellos dentro de una banda de 2,08 px.

Antes de empezar, lee `.claude/agents/lidia-naive-tester/memory.md` y
`.claude/agents/vera-art-director/memory.md`: llevan memoria histórica cross-versión y ya
detectaron un P0 que nadie había visto.

## Método que funcionó dos veces seguidas, y por qué

Lo de "Quién es" y lo del ritmo del carril salieron bien con el mismo procedimiento:

1. **Medir antes de opinar.** En el carril el primer entregable no fue código, fue una tabla de
   números. Evitó dos hipótesis falsas que ya estaban escritas en un handoff.
2. **Companion visual con mockups VIVOS y servidos**, nunca capturas ni artifacts, con la piel
   real del tema, las fuentes reales y contenido real de `content.ts`.
3. **Los dos especialistas en paralelo sobre el mismo brief**, y convergencia después. Opciones
   que los dos firmen, no un ranking con descartes. Defecto que señalan los dos, dado por bueno;
   defecto de uno solo, se discute.
4. **No tocar `src/` hasta elegir dirección.** Luego worktree aparte, nunca `git stash`.
5. **Gate final** con lidia y vera antes de merge.

**La trampa que costó más tiempo en el encargo anterior no fue un bug: fue medir dos cosas
distintas con el mismo nombre.** Pasó tres veces (el lead contra la cartela entera; el final del
tween contra el cruce de 0,99; el presupuesto del pin contra el recorrido lateral), y hasta los
dos críticos dieron veredictos opuestos sobre la misma meseta por eso. Si defines un objetivo
numérico, define **con qué instrumento y en qué umbral se mide**, en la misma frase.

## Preguntas abiertas que el brainstorm debería atacar

No son requisitos: son las que quedaron sin respuesta.

- ¿Esta sección tiene que hacer algo más que existir? Hoy es un email centrado en una pantalla en
  blanco. ¿Es suficiente para el suelo de conversión, o le falta una razón para escribir?
- ¿Formulario o `mailto:`? El proyecto **no tiene backend** — un formulario implica un endpoint de
  terceros, y todo `VITE_*` va al bundle y es público.
- ¿Qué hace la esquina (`tel`, LinkedIn, GitHub)? Para mucha gente de selección LinkedIn es la vía
  por defecto **antes** que el correo, y hoy está en letra pequeña en una esquina.
- ¿Cómo se llega aquí sin recorrer el sitio entero? Es la pregunta de navegación, y esta sección
  es donde duele.
- ¿Se ve igual de bien en los tres temas? Caelestia ya viste `.hero-surface` como tarjeta Material
  You; Hyprland tiene su propia paleta.

## Disciplina de sesión

- **Modelo:** brainstorm y convergencia en modelo top; implementación baja a Sonnet. **Pinea el
  modelo de cada subagente** — heredan el de la sesión y un fan-out sin pinear factura todo a
  tarifa top.
- **Medir en el build de producción**, nunca en `dev`: el HMR corrompe las medidas de
  ScrollTrigger. Siempre `?theme=vice` (el tema se sortea por visita).
- `scroll-behavior` es `smooth` y hay Lenis: un `scrollTo` sin `behavior: "instant"` aterriza
  corto y da falsos negativos.
- `free -h` antes del arnés: con menos de ~3 GB disponibles el navegador muere a mitad. No es
  regresión, es presión de memoria. Por lo mismo, **no lances dos navegadores a la vez**.
- `python3 scripts/verify.py` debe salir 0 (12 fallos de fixtures en la línea base, ninguno nuevo).

---

## Prompt para pegar en la sesión nueva

```
Lee .docs/BRIEF-contacto-hablemos.md entero antes de nada, y desde el te los ficheros que cita.

Quiero mejorar la seccion de contacto ("Hablemos", src/sections/contacto.ts). Hoy es un email
centrado en una pantalla y funciona, pero es el suelo de conversion del portfolio y no esta a
la altura del resto del sitio.

Mismo metodo que funciono con "Quien es" y con el ritmo del carril:

- superpowers:brainstorming con companion visual: mockups VIVOS y servidos, nunca capturas ni
  artifacts. Con la piel real del tema, las fuentes reales y el contenido real de content.ts.
  Nada de barras grises ni monoespaciada: el proyecto tiene regla anti-mock y Vice prohibe la
  monoespaciada explicitamente.
- Invoca especialista-ux-ui y especialista-animaciones en paralelo sobre el mismo brief, y
  converge tu despues. Quiero opciones que los DOS firmen, no un ranking con descartes. Cuando
  los dos coincidan en un defecto lo doy por bueno; cuando lo diga solo uno, lo discutimos.
- Antes del brainstorm, dame una lectura de lo que hay: que se ve, en cuanto scroll se llega,
  como se comporta en los tres temas y en movil. Si algo se puede medir, mide.
- No toques src/ hasta que yo elija una direccion. Cuando implementes, worktree aparte.
- Gate final: lidia-naive-tester y vera-art-director, los dos leyendo su memory.md antes.

Sobre el modelo: el brainstorm y la convergencia son decision de diseno, sesion con modelo top;
la implementacion baja a Sonnet. Pinea el modelo de cada subagente.

Mide en el build de produccion, no en dev, y siempre con ?theme=vice.

Dos avisos del encargo anterior que quiero que tengas presentes:
- La escala tipografica del tema va por su segunda seccion con Vera; la tercera se le convierte
  en P0 automatico. Tenlo en cuenta al proponer tipografia aqui.
- Si defines un objetivo numerico, di en la misma frase con que instrumento y en que umbral se
  mide. El encargo del carril perdio tiempo tres veces por medir dos cosas distintas con el
  mismo nombre.
```
