# Vice City — diseño del tema

Fecha: 2026-07-24 · Estado: aprobado, pendiente de plan de implementación
Rama: `design/redesign-cinematic-themes`

## Contexto

El portfolio tiene un sistema de temas "rice" que sortea uno al azar en cada visita
(Vice City, Hyprland, Caelestia). Hyprland está **aprobado y no se toca**. Este spec
cubre solo **Vice City**, que se rechazó en tres iteraciones:

1. Degradado plano con sol → *"muy meh, no hay visual storytelling"*.
2. Shader synthwave (skyline en bandas, sol cortado, reflejo) → *"no me gusta"*.
3. Foto única teñida con progresión horaria → *"podemos hacerlo mejor"*.

Diagnóstico: un shader procedural **siempre se ve dibujado**. El look de GTA VI es
fotográfico. La materia prima estaba mal elegida, no la ejecución.

Resultado buscado: un hero cinematográfico real, que se sienta rodado y no ilustrado,
sin romper el suelo de conversión (nombre, rol y contacto legibles al instante).

## Decisiones (no re-litigar)

| Decisión | Elección |
|---|---|
| Materia prima del fondo | **Fotografía y vídeo reales**, no procedural |
| Hero | **Vídeo en bucle autónomo** (opción A), no scrubbing |
| Secciones interiores | Fotografía atenuada (~30% de brillo) como textura |
| Acento | Ámbar `#ffd166` |
| Texto | Crema cálido `#fff4e8` (no blanco frío) |
| Display | Passion One 900, mayúsculas |
| Subtítulo | Manrope **200** a 20–27 px — línea de cartel, no párrafo |
| Cuerpo | Manrope 400, 15 px, interlineado 1,7 |
| Etiquetas | Manrope 700 en mayúsculas con tracking — **sin mono** |
| Contenedor del stack | **Créditos de película**: `rol · nombre · nota`, sin cajas |
| Gesto de scroll | Se conserva el zoom del nombre tipo GTA |

### Por qué bucle y no scrubbing

Se prototiparon ambos. El scrubbing mejorado (deriva en reposo, suavizado, metraje
direccional, puerta de carga) quedó defendible, pero pierde en lo que importa aquí:

- Exige **descargar el vídeo entero** antes de responder (~2,5–4 MB frente a ~1,2 MB).
- Decodifica en cada búsqueda: caro en CPU y batería, con tirones en móvil medio.
- **Falla de forma visible**: promete una interacción que no responde.
- **Compite con el zoom del nombre por el mismo scroll.** No caben los dos.

Con bucle, el scroll queda libre para que el protagonista sea el nombre — que es
además lo que hace la web real de GTA VI.

### Por qué no se incrusta Pricedown

GTA VI usa **Pricedown Black** + **GTAArtDeco** (custom de Rockstar, no licenciable).
La licencia gratuita de Typodermic para Pricedown dice literalmente:

> Allowed: `web page (not embedded)` · **Not allowed: `web page (embedded)`**

Incrustarla como webfont violaría su licencia. **Passion One 900** es la alternativa
libre más cercana (Google Fonts). Si en el futuro se compra una licencia web de
Typodermic, basta cambiar el token `--font-display`.

## Arquitectura

### Principio: un solo DOM semántico, presentación por tema

Los créditos no son un cambio de color: son otra estructura. Para no triplicar el JS,
el stack se renderiza **siempre** con la misma información (`rol`, `nombre`, `nota` —
datos que ya existen en `src/data/content.ts`), y cada tema decide con CSS cómo se ve:

- **Vice** → fila de créditos con las tres partes visibles.
- **Hyprland** → píldora: oculta la nota (mantiene su aspecto actual).
- **Caelestia** → contenedor tonal redondeado.

Se conserva así la propiedad clave del motor: cambiar `data-theme` re-skinea todo.
Solo se cae a variantes en JS cuando el CSS no dé.

### Fondo

`Theme.mountBackground(container) -> { destroy() }` ya soporta esto sin cambios de
interfaz: Vice montará capas de `<video>` + `<img>` en lugar de un canvas WebGL.

Capas del hero, de abajo arriba:
1. `<img>` póster (la foto), visible al instante.
2. `<video autoplay muted loop playsinline>`, que entra fundido al estar listo.
3. Gradación Vice (`soft-light`) + capa de color.
4. Scrim (degradado oscuro) — **garantiza contraste pase lo que pase en la imagen**.
5. Grano animado (`steps`), textura de película proyectada.

**Degradación sin culpa:** en móvil, con `save-data` o con `prefers-reduced-motion`,
el vídeo no se carga y se queda el póster. El vídeo es un lujo para quien puede.

### Tokens nuevos

`--font-lead` y `--lead-weight` (el subtítulo tiene familia y peso propios por tema),
además de los ya existentes `--display-weight`, `--display-transform`, `--display-tracking`.

### Assets

- **Foto base:** Unsplash `aT2JKn38cqw` (ciudad al atardecer con palmeras). Licencia
  libre, uso comercial, sin atribución obligatoria. Criterio de elección: **la zona
  donde va el nombre queda oscura**.
- **Vídeo del hero:** clip de Mixkit (licencia libre, sin atribución). Candidatos:
  `41375` (vuelo sobre ciudad al anochecer) y `44499` (atardecer con palmera).
  **Decisión abierta:** se propondrán ambos recortados y en bucle durante la
  implementación, y el usuario elige antes de dar el hero por cerrado.
- **Optimización obligatoria:** recortar a 6–8 s con bucle limpio, re-codificar a
  WebM/AV1 con MP4 de respaldo a 1280×720 y bitrate bajo. El grano y la gradación van
  encima, así que aguanta más compresión de lo normal. Objetivo: **≈1,2 MB**.
  Sin optimizar, los originales pesan 40–89 MB (medido); es inaceptable.
- Fotos a WebP con tamaños responsive y `preload` del póster del hero.

## Estructura de secciones (Vice)

| Sección | Fondo | Notas |
|---|---|---|
| Hero | Vídeo en bucle | Centrado. Nombre + rol + subtítulo + contacto visibles al instante |
| Sobre mí | Foto atenuada | 2–3 líneas escuetas |
| Obra ×4 | Foto atenuada | Ordinal gigante, problema/solución, y los créditos **de ese proyecto** (su stack) |
| Stack | Foto atenuada | Créditos **completos**: todas las tecnologías agrupadas por rol |
| Contacto | Foto a plena luz | Cierre |

Solo hero y contacto van a plena luz. Si todas las secciones fueran imagen brillante,
se rompen la legibilidad del texto largo y la fatiga visual al scrollear.

## Alcance

**Dentro:** el tema Vice City completo.

**Fuera (diferido, no implementar ahora):**
- Metáfora estructural por tema (Hyprland como gestor de ventanas en mosaico,
  Caelestia como superficies Material You). **Aprobado como concepto**, se hará
  tema a tema después de Vice.
- Parallax 2.5D sobre las fotos.
- Secuencia de 4 fotos cruzándose por sección.
- Progresión horaria del color al scroll (dorada → noche). Gustó como idea; la maqueta
  no convenció. Reevaluar sobre el sitio real, donde hay mucho más recorrido de scroll.
- Segundo vídeo nocturno en secciones interiores.

**No se toca:** Hyprland (aprobado por el usuario).

## Verificación

1. `npm run build` (tsc + vite) sin errores y `npm run lint` limpio. Requiere **Node 22**
   (`.nvmrc`); con Node 18 el build de Vite 8 falla.
2. Screenshots con Playwright (`--use-gl=swiftshader`) en 1440×900 y 390×844 para
   `?theme=vice`, y de control para `?theme=hyprland` (no debe regresar).
3. Confirmar: vídeo reproduciéndose, póster visible antes de que cargue, nombre + rol +
   contacto legibles en el primer viewport, cero errores de consola.
4. Emular `prefers-reduced-motion: reduce` → sin vídeo, sin animación, contenido legible.
5. Emular `save-data` y viewport móvil → no se descarga el vídeo.
6. Medir el peso real del vídeo servido; si supera ~1,5 MB, volver a codificar.
7. Anti-mock: `grep -rE "lorem|placeholder|mockData" src/` → vacío.

## Riesgos

- **Peso del vídeo.** Es el riesgo principal. Mitigado por recorte, re-codificación y
  degradación en móvil. Si no se baja de ~1,5 MB, el hero se queda en foto.
- **Legibilidad sobre imagen variable.** Mitigada por el scrim, que es obligatorio.
- **Licencias.** Solo Unsplash y Mixkit (libres, comerciales, sin atribución).
  Pricedown queda descartada por licencia; ver arriba.
- **Coste de la metáfora por tema.** Multiplica el trabajo por tres. Por eso se difiere
  y se hace tema a tema.
