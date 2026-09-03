# Caelestia B2 — Quién soy: plan de maquetado

> **Esto NO es un plan de implementación.** Es la agenda de diseño de la fase B2: qué maquetas hay
> que construir en el companion, en qué orden y contra qué medirlas, para poder escribir después el
> spec y el plan. B2 **no tiene spec todavía**, y por eso no puede tener plan de implementación:
> planificar trabajo sin diseñar es lo que dejó en este repo planes con 86 y 57 casillas sin marcar.

Fecha: 2026-08-26
Spec que lo reclama: `docs/superpowers/specs/2026-09-02-caelestia-quien-soy-design.md` — ejecutado entero en la sesion de diseno previa a esa spec.
Fase: **B2** de seis. La anterior, **B1 (Título)**, está especificada y planificada:
`docs/superpowers/specs/2026-08-26-caelestia-titulo-design.md` ·
`docs/superpowers/plans/2026-08-26-caelestia-titulo.md`

---

## Qué es B2 y por qué va la segunda

La escena `#about` — rotulada **«Quién soy»** en `sceneIndex` — es **la más sana de las cinco**.
Medida sobre el build de producción en la ventana de 1412 × 748 que impone el carril de workspaces:

| | valor |
|---|---|
| alto del contenido | **443 px** (y0 189 → y1 632) |
| ¿cabe en 748? | **sí**, con holgura |
| aire sin usar | 189 px arriba, 116 px abajo |
| defecto visible | la ficha de perfil va apretada: **el nombre parte en tres líneas** y «disponible para proyectos» en dos |

Va la segunda **precisamente por sana**: es la que menos riesgo tiene para confirmar que el patrón
«cada escena es una aplicación» aguanta una segunda vez, ahora que B1 lo estrena. Si el patrón falla,
falla aquí barato y no en Obra, que es la que está rota de verdad (4964 px en una ventana de 748).

---

## Lo que ya está decidido y NO se vuelve a abrir

Estas decisiones vienen de la fase A y de B1. Entran en B2 como dadas:

- **Cada escena es una aplicación.** Quién soy es **la ficha del sistema** — el «Acerca de este
  equipo». Es la dirección que Aoshi aprobó; lo que falta es la ejecución.
- **La ventana es 1412 × 748 y no se desplaza.** Ley de la sección: *lo que quede bajo el pliegue es
  ampliación, nunca lo que hacía falta para entender la escena.*
- **El motor de color** (`caelestia.color.ts`): matiz por la hora, claridad fija, esquema sin
  interpolar. No se toca.
- **La tipografía**: Fraunces display, Hanken Grotesk cuerpo, Martian Mono utilidad. Y la lección de
  B1: **`opsz` se elige por el tamaño al que se lee**. Cualquier texto grande de B2 usa
  `--cae-display-axes-cartel`; lo de 15–30 px sigue con `--cae-display-axes`.
- **El fondo** lo estrena B1 y B2 lo hereda sin tocarlo. En esta escena la aplicación llena la
  ventana, así que apenas asoma.
- **La micro-interacción es N4** («el fondo se aparta»).
- **Anti-mock:** todo dato visible sale de `content.ts` literal. El fallo de B1 —«Repositorios
  públicos · 2», un dato que no existe— no se repite.

---

## Contenido real disponible

De `src/data/content.ts`, lo que esta escena puede pintar y nada más:

| origen | contenido |
|---|---|
| `identity` | name, role, location, availability, now, since, githubAvatar |
| `aboutCopy` | dos frases |
| `education[0]` | Ingeniería de Sistemas · Universidad Santa María · 2021 — presente (10.º semestre) |
| `experience[0]` | Pasante B2C Conocimiento al Cliente · Telefónica Venezuela · Ago 2025 — May 2026 |
| `focusAreas` | dos pares título/detalle |
| `stats` | cuatro cifras — **ya las usa B1 en su columna derecha**, así que repetirlas aquí hay que justificarlo o evitarlo |

**Aviso heredado de B1:** «10.º semestre» **no es un campo**: vive dentro de `education[0].period`.

---

## La agenda de maquetas

Cada punto es una pantalla del companion, construida con `/frontend-design:frontend-design`, con la
piel real de Caelestia y **capturada y mirada antes de enseñarla**.

- [x] **M1 · Diagnóstico.** La escena actual dentro de la ventana, con las medidas encima: los 443 px
      de contenido, los 189 arriba y 116 abajo sin usar, y el nombre partido en tres líneas. Es el
      punto de partida contra el que se juzga todo lo demás.

- [x] **M2 · Tres composiciones de la ficha del sistema.** No tres tallas de la misma: tres maneras
      distintas de repartir. Punto de partida sugerido, a discutir con Aoshi:
      - una ficha a la izquierda y especificaciones en filas clave/valor a la derecha (lo que ya se
        esbozó y él vio);
      - una ficha centrada tipo «Acerca de» de escritorio, con el retrato grande y las
        especificaciones debajo en dos columnas;
      - un panel de ajustes con secciones plegables, donde formación, experiencia y enfoque son
        entradas de una lista de sistema.

- [x] **M3 · El retrato.** `identity.githubAvatar` es la única imagen real que tiene el proyecto
      —las nueve de obra siguen siendo marcadores—. Decidir tamaño, recorte y si lleva forma de
      Material 3 (la biblioteca que ya se usa en el fondo) en vez de círculo. **Es la única pieza de
      B2 que puede tener un gesto propio.**

- [x] **M4 · Composiciones del pie.** Dónde van las dos áreas de `focusAreas` y si las cuatro cifras
      de `stats` se repiten aquí o se dejan solo en Título. Tres repartos.

- [x] **M5 · La entrada de escena.** Coherente con B1 sin copiarla: allí la terminal pregunta
      `whoami` y el nombre se traza. Aquí el comando natural sería otro —`neofetch`, `uname -a`, o
      la ficha que se rellena campo a campo—. Tres opciones, todas con el shell ya montado antes de
      que pase nada.

- [x] **M6 · Micro-interacciones propias**, si las necesita. N4 es la del tema; lo que se decida
      aquí es qué responde al roce **dentro** de la ficha.

- [x] **M7 · Movimiento reducido** de lo que se elija, y la escena a las 03:00 en esquema oscuro.
      La lección de B1: **el croma no es el mismo en los dos esquemas** — croma alto con claridad
      baja da barro en OkLCH.

---

## Contra qué se mide

El arnés de B2 (`scripts/measure-caelestia-quien-soy.py`, aún sin escribir) hereda de B1:

1. **Cabe.** Alto del contenido y aire bajo el pie ≥ 0. Este gate ya cazó dos desbordamientos de
   138 y 142 px en B1.
2. **El nombre no parte.** Es el defecto concreto de esta escena: una aserción sobre el número de
   líneas de caja del nombre.
3. **Anti-mock.** Todo texto visible existe en `content.ts`.
4. **Contraste** contra el fondo real, barriendo las 24 horas, ≥ 4.5:1.
5. **Movimiento reducido**: escena montada, sin recorrido.
6. **Los ejes del shell no se han movido.**

**Ningún gate se da por bueno sin haberlo visto dar rojo contra el fallo que dice cazar.**

---

## Entregables de la fase

En este orden, que es el que ya funcionó en la fase A y en B1:

1. Las maquetas M1–M7 en el companion, con aprobación de Aoshi por pieza.
2. `docs/superpowers/specs/2026-08-2X-caelestia-quien-soy-design.md`, con `Estado: pendiente de plan`.
   **Reutilizar este spec de B1 como plantilla**: la mitad de sus secciones —color y contraste,
   gates, movimiento reducido, anti-mock, lo que queda fuera— son idénticas.
3. Rescatar al repo cualquier artefacto aprobado que viva en el companion. **`.superpowers/` está en
   `.gitignore` (línea 47)**: lo que se quede ahí se pierde.
4. `docs/superpowers/plans/2026-08-2X-caelestia-quien-soy.md` con `superpowers:writing-plans`.
5. El traspaso, con modelo y esfuerzo recomendados.

---

## Estado al escribir esto

- **B1 (Título):** spec y plan escritos. **Sin implementar.** Es una decisión abierta si B2 se
  maqueta antes o después de que B1 se ejecute. **Recomendación: maquetar B2 ahora y ejecutar B1 en
  paralelo en otra sesión** — el maquetado es trabajo de diseño con Aoshi y la implementación es
  mecánica; no se estorban, y solo comparten `hero.ts`, que B2 no toca (`about.ts` es otro fichero).
- **B3 (Obra):** bloqueada fuera del código. Las nueve capturas de `public/media/obra/` siguen siendo
  marcadores «CAPTURA PENDIENTE» con la paleta de Vice, y el gestor de archivos las pone a 620×490.
  **Va la última.**
- **B4 (Créditos) y B5 (Fundido):** con encargo pendiente de la fase A — Créditos necesita un resumen
  que se sostenga solo en vez de 23 nombres que empiezan y siguen; Fundido llega corto y deja media
  ventana vacía en la escena de cierre.
- **Companion de esta sesión:** `.superpowers/brainstorm/2412334-1787752791/content/` — quince
  pantallas, de `01-diagnostico` a `15-fondo-composicion`. **No versionado.** El servidor se
  relanza con
  `/root/.claude/plugins/cache/claude-plugins-official/superpowers/6.3.0/skills/brainstorming/scripts/start-server.sh --project-dir /home/aoshi/proyectos/portfolio-aoshi`
  y con `--project-dir` reutiliza el puerto.
- **Sin commitear:** los cinco ficheros de B1 (`git status`), en la rama `main`.
