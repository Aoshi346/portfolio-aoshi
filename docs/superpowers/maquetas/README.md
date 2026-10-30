# Maquetas de la fase B5 — Fundido

Rescatadas del companion de brainstorming el 2026-09-04, porque `.superpowers/` está en
`.gitignore` (línea 47) y lo que se queda ahí se pierde.

Son **fragmentos de pantalla**, no páginas: se escribieron para incrustarse en el companion, así
que abiertas sueltas no traen `<html>` ni `<head>`. El navegador las muestra igual.

| fichero | qué decidió |
|---|---|
| `…-composicion.html` | K · la contraportada, y las micro-interacciones del bicho |
| `…-escala.html` | `--t-10` para el cierre, y los cuatro tokens de ejes |
| `…-canales.html` | B · el pie de imprenta: dos actos y dos destinos |
| `…-movimiento.html` | el fundido: 7 gestos, 1900 ms, con partitura viva |
| `…-entrada.html` | la entrada de 440 ms, y la regla de «suena una vez» |
| `…-movil.html` | 390 px, el sello entero y la figura de ocho lóbulos |

Composición, movimiento y entrada cargan GSAP del CDN; en el companion venía de `/files/`.

La maqueta de móvil trae su captura de «hoy» como PNG hermano (`2026-09-04-caelestia-fundido-movil-hoy.png`). Compara el estado actual del build contra la propuesta viva en iframe.

# Maqueta del Título — el nombre en el centro (2026-10-29)

Spec: `docs/superpowers/specs/2026-10-29-caelestia-titulo-nombre-design.md`.

| fichero | qué decidió |
|---|---|
| `2026-10-29-caelestia-titulo-entradas.html` | B · Trazo, sin pastilla: el nombre se dibuja con sus contornos de Fraunces, se rellena y el rol entra con un corte |
| `2026-10-29-caelestia-titulo-entradas-generar.py` | el generador de la maqueta |

Esta sí es una página entera (lleva su `<html>`), con fondos y contornos incrustados. El generador
leía sus entradas (fondos capturados, `tokens.json`, los contornos a opsz 144) de una carpeta de
la sesión que no se conserva: sirve para leer cómo se hizo, no para volver a ejecutarlo tal cual.
