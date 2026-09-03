#!/usr/bin/env python3
"""
Arnes de la fase B3 (Obra) de Caelestia. Ver
docs/superpowers/specs/2026-09-03-caelestia-obra-design.md, seccion "## Los gates".

Uso:
    npm run build && npx vite preview --port 4173 &
    python3 scripts/measure-caelestia-obra.py --base http://localhost:4173
"""
import argparse
import sys

from playwright.sync_api import sync_playwright

FALLOS = []


def assert_true(cond: bool, mensaje: str) -> None:
    if not cond:
        FALLOS.append(mensaje)


# ---------------------------------------------------------------------------
# Los cinco proyectos reales de `src/data/content.ts` (`caseStudies`), copiados
# literalmente — no parafraseados — para las aserciones anti-mock (4c, 4d).
# Cada entrada lleva lo que la Editorial pinta de verdad: title/tag/role/status,
# period (None si el campo no existe: solo TesisFar), y como se resuelve el pie
# (un enlace real, o "privado").
# ---------------------------------------------------------------------------
PROYECTOS = [
    {
        "title": "EchoPlan",
        "tag": "Gestión de campañas",
        "role": "Desarrollo full stack",
        "status": "Sistema interno · Telefónica Venezuela",
        "period": "Ago 2025 — May 2026",
        "problem": (
            "Las campañas pasaban por varias áreas antes de salir, cada una con sus "
            "aprobaciones, y el seguimiento vivía repartido entre correos y hojas de "
            "cálculo. Nadie podía responder de un vistazo en qué punto estaba cada una."
        ),
        "solution": (
            "Un sistema interno que reúne el recorrido completo de la campaña en un "
            "mismo sitio: quién la creó, qué aprobaciones lleva, si ya se configuró y "
            "cuándo salió. Con permisos por rol y tableros que muestran cómo va todo "
            "sin tener que preguntar."
        ),
        "private": True,
        "link_href": None,
    },
    {
        "title": "TesisFar",
        "tag": "Gestión académica",
        "role": "Diseño y desarrollo",
        "status": "Repositorio público",
        "period": None,
        "problem": (
            "Coordinar el Trabajo Especial de Grado entre estudiantes, tutores y "
            "jurados es, en la mayoría de universidades, un proceso manual y "
            "fragmentado por correo y hojas de cálculo."
        ),
        "solution": (
            "Construí una plataforma que gestiona el ciclo completo del TEG: entregas "
            "de avances, coordinación estudiantes–tutores y evaluación por jurados, "
            "todo en un mismo lugar."
        ),
        "private": False,
        "link_href": "https://github.com/Aoshi346/teg-web-app",
    },
    {
        "title": "HyprFinance",
        "tag": "Finanzas personales",
        "role": "Diseño y desarrollo",
        "status": "Repositorio privado",
        "period": "Jun 2026 — hoy",
        "problem": (
            "Llevar las cuentas cuando manejas varias monedas termina en hojas de "
            "cálculo que nunca cuadran, porque el cambio de ayer no es el de hoy. Y "
            "las aplicaciones que lo resuelven te piden subir todo tu historial "
            "financiero a un servidor de otro."
        ),
        "solution": (
            "Una aplicación donde tus datos se quedan en tu propio equipo, cifrados, "
            "y la nube solo sirve para sincronizar entre tus dispositivos. Guarda cada "
            "movimiento con el cambio del día en que ocurrió, así el total nunca "
            "miente, y reparte solo las compras a cuotas para que sepas qué te queda "
            "por pagar."
        ),
        "private": True,
        "link_href": None,
    },
    {
        "title": "WatchDog",
        "tag": "Ciberseguridad",
        "role": "Desarrollo principal",
        "status": "Repositorio público",
        "period": "Sep — Oct 2025",
        "problem": (
            "Revisar la seguridad de un equipo obliga a saltar entre herramientas "
            "sueltas, cada una con su propia forma de usarse, y casi todas pensadas "
            "para quien ya sabe de seguridad."
        ),
        "solution": (
            "Una aplicación de escritorio que reúne en un mismo sitio el análisis de "
            "vulnerabilidades, la gestión de contraseñas, el monitor de red y las "
            "herramientas de análisis forense, con una interfaz que no exige ser "
            "experto para entenderla."
        ),
        "private": False,
        "link_href": "https://github.com/Aoshi346/Proyecto-CiberSeg",
    },
    {
        "title": "Editor de texto",
        "tag": "Programación de sistemas",
        "role": "Proyecto académico individual",
        "status": "Repositorio público",
        "period": "2024",
        "problem": (
            "Un ejercicio de fin de curso con una lista cerrada de requisitos: "
            "corrector ortográfico, varias páginas, cifrado y descifrado del "
            "contenido, guardado en archivo y una interfaz gráfica de verdad."
        ),
        "solution": (
            "Un editor completo en C con interfaz en GTK4, donde el bloque de texto "
            "crece según se escribe, el corrector señala las palabras y el contenido "
            "puede cifrarse antes de guardarlo."
        ),
        "private": False,
        "link_href": "https://github.com/Aoshi346/Text-Editor-Application",
    },
]

TITULOS = [p["title"] for p in PROYECTOS]


def ir_a_obra(page) -> None:
    page.click('[data-cae-ws="obra"]')
    page.wait_for_timeout(2500)  # cubre la entrada Caida completa a velocidad real


def medir_cabe(page) -> None:
    rect = page.evaluate(
        """
        () => {
          const rail = document.querySelector('[data-obra-rail]');
          const r = rail.getBoundingClientRect();
          let maxBottom = 0;
          rail.querySelectorAll('*').forEach(el => {
            const er = el.getBoundingClientRect();
            maxBottom = Math.max(maxBottom, er.bottom - r.top);
          });
          const win = rail.closest('[data-cae-track] > *') || rail.parentElement;
          return { contenido: maxBottom, ventana: win.getBoundingClientRect().height };
        }
        """
    )
    desborda = rect["contenido"] - rect["ventana"]
    assert_true(desborda <= 2, f"Cabe: contenido {rect['contenido']:.0f}px vs ventana {rect['ventana']:.0f}px (desborda {desborda:.0f}px)")


def check_alcanzables(page) -> None:
    """4a. Los cinco proyectos son alcanzables: cada tarjeta dentro del carril,
    y las cinco alcanzables tabulando desde la pastilla del workspace."""
    datos = page.evaluate(
        """
        () => {
          const rail = document.querySelector('[data-obra-rail]');
          const r = rail.getBoundingClientRect();
          const cards = Array.from(document.querySelectorAll('.cae-obra-card'));
          return cards.map(c => {
            const cr = c.getBoundingClientRect();
            return {
              dentro: cr.left >= r.left - 0.5 && cr.right <= r.right + 0.5 &&
                       cr.top >= r.top - 0.5 && cr.bottom <= r.bottom + 0.5,
              idx: c.dataset.obraCard,
            };
          });
        }
        """
    )
    assert_true(len(datos) == 5, f"Alcanzables: se esperaban 5 tarjetas, hay {len(datos)}")
    for d in datos:
        assert_true(d["dentro"], f"Alcanzables: la tarjeta {d['idx']} se sale del carril")

    # Tabular desde la pastilla del workspace y recoger que indice de tarjeta
    # de obra recibe el foco, hasta ver las cinco (o agotar un margen amplio).
    page.evaluate("document.querySelector('[data-cae-ws=\"obra\"]').focus()")
    vistos = set()
    for _ in range(40):
        page.keyboard.press("Tab")
        idx = page.evaluate(
            "document.activeElement && document.activeElement.dataset ? "
            "document.activeElement.dataset.obraCard : null"
        )
        if idx is not None:
            vistos.add(idx)
        if len(vistos) == 5:
            break
    assert_true(len(vistos) == 5, f"Alcanzables: solo {len(vistos)}/5 tarjetas reciben foco por Tab ({sorted(vistos)})")


def check_capturas_no_cortadas(page, viewport: dict) -> None:
    """4b. Ninguna captura queda cortada — dentro del viewport y del carril."""
    datos = page.evaluate(
        """
        () => {
          const rail = document.querySelector('[data-obra-rail]');
          const r = rail.getBoundingClientRect();
          const thumbs = Array.from(document.querySelectorAll('.cae-obra-thumb'));
          return thumbs.map((t, i) => {
            const tr = t.getBoundingClientRect();
            return {
              i,
              enCarril: tr.left >= r.left - 0.5 && tr.right <= r.right + 0.5 &&
                        tr.top >= r.top - 0.5 && tr.bottom <= r.bottom + 0.5,
              rect: { left: tr.left, right: tr.right, top: tr.top, bottom: tr.bottom },
            };
          });
        }
        """
    )
    assert_true(len(datos) == 6, f"Capturas: se esperaban 6 miniaturas (5 tarjetas + 1 preview), hay {len(datos)}")
    for d in datos:
        r = d["rect"]
        en_viewport = (
            r["left"] >= -0.5
            and r["top"] >= -0.5
            and r["right"] <= viewport["width"] + 0.5
            and r["bottom"] <= viewport["height"] + 0.5
        )
        assert_true(en_viewport, f"Capturas: thumb {d['i']} se sale del viewport ({r})")
        assert_true(d["enCarril"], f"Capturas: thumb {d['i']} se sale del carril [data-obra-rail]")


def check_anti_mock(page) -> None:
    """4c. Anti-mock — cada tarjeta abierta pinta exactamente lo que dice
    `content.ts`, "tooling" no aparece nunca, y el `<dt>Periodo</dt>` falta
    solo para TesisFar (el unico caso sin `period`)."""
    for i, esperado in enumerate(PROYECTOS):
        page.evaluate(f"document.querySelectorAll('.cae-obra-card')[{i}].click()")
        page.wait_for_timeout(400)
        datos = page.evaluate(
            """
            () => {
              const drawer = document.querySelector('.cae-obra-drawer');
              const h3 = drawer.querySelector('[data-cae-obra-h3]');
              const kick = drawer.querySelector('.cae-obra-drawer-kick');
              const rows = Array.from(drawer.querySelectorAll('.cae-obra-drawer-meta > div'));
              const meta = {};
              rows.forEach(row => {
                const dt = row.querySelector('dt');
                const dd = row.querySelector('dd');
                if (dt && dd) meta[dt.textContent.trim()] = dd.textContent.trim();
              });
              const foot = drawer.querySelector('.cae-obra-foot');
              const link = foot ? foot.querySelector('a') : null;
              const privado = foot ? foot.querySelector('.cae-obra-foot-private') : null;
              const problem = drawer.querySelectorAll('.cae-obra-prose p')[0];
              const solution = drawer.querySelectorAll('.cae-obra-prose p')[1];
              return {
                titulo: h3 ? h3.textContent.trim() : null,
                tag: kick ? kick.textContent.trim() : null,
                meta,
                tieneLink: !!link,
                hrefLink: link ? link.href : null,
                esPrivado: !!privado,
                textoRail: drawer.parentElement.innerText,
                problem: problem ? problem.textContent.trim() : null,
                solution: solution ? solution.textContent.trim() : null,
              };
            }
            """
        )
        assert_true(datos["titulo"] == esperado["title"], f"Anti-mock: titulo '{datos['titulo']}' != '{esperado['title']}'")
        assert_true(datos["tag"] == esperado["tag"], f"Anti-mock: tag '{datos['tag']}' != '{esperado['tag']}' en {esperado['title']}")
        assert_true(datos["meta"].get("Rol") == esperado["role"], f"Anti-mock: role '{datos['meta'].get('Rol')}' != '{esperado['role']}' en {esperado['title']}")
        assert_true(datos["meta"].get("Estado") == esperado["status"], f"Anti-mock: status '{datos['meta'].get('Estado')}' != '{esperado['status']}' en {esperado['title']}")
        assert_true(datos["problem"] == esperado["problem"], f"Anti-mock: problem no coincide en {esperado['title']}")
        assert_true(datos["solution"] == esperado["solution"], f"Anti-mock: solution no coincide en {esperado['title']}")

        if esperado["period"] is None:
            assert_true("Periodo" not in datos["meta"], f"Anti-mock: {esperado['title']} NO deberia tener <dt>Periodo</dt>")
        else:
            assert_true(datos["meta"].get("Periodo") == esperado["period"], f"Anti-mock: periodo '{datos['meta'].get('Periodo')}' != '{esperado['period']}' en {esperado['title']}")

        if esperado["private"]:
            assert_true(datos["esPrivado"], f"Anti-mock: {esperado['title']} deberia mostrarse como proyecto privado")
        else:
            assert_true(datos["tieneLink"] and datos["hrefLink"] == esperado["link_href"], f"Anti-mock: enlace de {esperado['title']} no coincide (visto {datos['hrefLink']})")

        assert_true(
            "Claude Code" not in datos["textoRail"] and "Gemini CLI" not in datos["textoRail"],
            f"Anti-mock: 'tooling' (Claude Code / Gemini CLI) no aparece en la ficha ({esperado['title']})",
        )

        # Los titulos/tags visibles en TODO el carril (no solo el abierto)
        # deben ser uno de los cinco reales.
        titulos_visibles = page.evaluate(
            "Array.from(document.querySelectorAll('.cae-obra-caption')).map(c => "
            "c.childNodes[0].textContent.trim())"
        )
        for t in titulos_visibles:
            assert_true(t in TITULOS, f"Anti-mock: titulo de tarjeta '{t}' no es uno de los cinco reales")


def check_extremos(page) -> None:
    """4d. Aguanta los dos extremos de contenido: EchoPlan y TesisFar, cada
    uno con parrafos de problema/solucion no vacios y dentro del carril."""
    for i, titulo in ((0, "EchoPlan"), (1, "TesisFar")):
        page.evaluate(f"document.querySelectorAll('.cae-obra-card')[{i}].click()")
        page.wait_for_timeout(400)
        datos = page.evaluate(
            """
            () => {
              const rail = document.querySelector('[data-obra-rail]');
              const r = rail.getBoundingClientRect();
              const ps = Array.from(document.querySelectorAll('.cae-obra-prose p'));
              return ps.map(p => {
                const pr = p.getBoundingClientRect();
                return {
                  texto: p.textContent.trim().length,
                  dentro: pr.bottom <= r.bottom + 0.5,
                };
              });
            }
            """
        )
        assert_true(len(datos) == 2, f"Extremos ({titulo}): se esperaban 2 parrafos, hay {len(datos)}")
        for d in datos:
            assert_true(d["texto"] > 0, f"Extremos ({titulo}): parrafo vacio")
            assert_true(d["dentro"], f"Extremos ({titulo}): parrafo se sale del carril por abajo")


def _oklab_to_srgb255(l: float, a_: float, b_: float) -> tuple[float, float, float]:
    """OKLab -> sRGB (0..255). Mismas matrices que `scripts/verify.py`
    (Bjorn Ottosson)."""

    def clamp01(v: float) -> float:
        return max(0.0, min(1.0, v))

    l_ = l + 0.3963377774 * a_ + 0.2158037573 * b_
    m_ = l - 0.1055613458 * a_ - 0.0638541728 * b_
    s_ = l - 0.0894841775 * a_ - 1.2914855480 * b_
    l3, m3, s3 = l_**3, m_**3, s_**3

    lin_r = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    lin_g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    lin_b = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3

    def to_gamma(c: float) -> float:
        c = clamp01(c)
        return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

    return to_gamma(lin_r) * 255, to_gamma(lin_g) * 255, to_gamma(lin_b) * 255


def _parse_rgb(css: str) -> tuple[float, float, float, float] | None:
    """Parser minimo de color computado. Cubre `rgb()`/`rgba()` y `oklch()`
    (lo que Chromium devuelve para los tokens de Caelestia, resueltos por
    Tailwind 4 via `oklch()` en `themes.css`) — NO cubre `oklab()`/`color()`
    como hace el parser completo de `scripts/verify.py`
    (`_parse_css_color`). Si algun dia una de estas reglas empieza a
    resolver a otro espacio de color, esta funcion devuelve `None` y la
    asercion de contraste lo reporta en vez de fallar en silencio."""
    css = css.strip()

    if css.startswith("oklch("):
        inner = css[css.index("(") + 1 : css.rindex(")")]
        comps, _, alpha_s = inner.partition("/")
        vals = comps.split()
        ell, c, h = float(vals[0]), float(vals[1]), float(vals[2])
        import math

        rad = math.radians(h)
        a_ = c * math.cos(rad)
        b_ = c * math.sin(rad)
        r, g, b = _oklab_to_srgb255(ell, a_, b_)
        a = float(alpha_s.strip()) if alpha_s.strip() else 1.0
        return r, g, b, a

    if css.startswith("rgb(") or css.startswith("rgba("):
        inner = css[css.index("(") + 1 : css.rindex(")")]
        parts = [p.strip() for p in inner.replace("/", ",").split(",") if p.strip()]
        if len(parts) < 3:
            return None
        r, g, b = float(parts[0]), float(parts[1]), float(parts[2])
        a = float(parts[3]) if len(parts) > 3 else 1.0
        return r, g, b, a

    return None


def _luminancia(rgb: tuple[float, float, float]) -> float:
    def canal(c: float) -> float:
        cs = c / 255
        return cs / 12.92 if cs <= 0.03928 else ((cs + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def _ratio(fg: tuple[float, float, float], bg: tuple[float, float, float]) -> float:
    l1, l2 = _luminancia(fg) + 0.05, _luminancia(bg) + 0.05
    return max(l1, l2) / min(l1, l2)


def check_contraste(page) -> None:
    """4e. Contraste — GAP CONOCIDO: esto mide un solo instante (la hora real
    del sistema al correr el arnes), NO un barrido de las 24 horas. El motor
    de color de Caelestia gobierna el matiz por la hora del visitante
    (ver `docs/superpowers/specs/2026-08-20-caelestia-escritorio-design.md`),
    asi que un solo punto no prueba que las otras 23 horas tambien pasen AA.
    El patron correcto para un barrido de verdad — sobreescribir el reloj del
    sistema ANTES de cargar la pagina y recorrer las 24 horas — ya existe en
    `scripts/measure-caelestia-hora.py`; si el contraste de la Editorial de
    Obra se vuelve un requisito real, hay que reusar ese patron aqui en vez de
    este muestreo de un solo instante.

    Ademas, esto compara contra el FONDO PROPIO calculado del elemento
    (`getComputedStyle(el).backgroundColor`, subiendo por los ancestros hasta
    encontrar uno opaco) — no contra lo que de verdad se ve pintado detras
    (el fondo generativo compuesto con el resto del shell), que es lo que
    hace `check_contrast_wcag` en `scripts/verify.py` con una captura de
    pantalla real. Para este arnes, el fondo propio calculado es suficiente
    (los tres selectores viven dentro de paneles con `background` opaco de
    Material 3, no directamente sobre el shader)."""
    # '.cae-obra-foot a' solo existe cuando el proyecto abierto tiene enlace
    # real (EchoPlan, la tarjeta 0 que queda abierta por defecto, es privado
    # y no lo tiene) — se abre TesisFar (tarjeta 1) para que los tres
    # selectores existan a la vez.
    page.evaluate("document.querySelectorAll('.cae-obra-card')[1].click()")
    page.wait_for_timeout(400)

    selectores = [".cae-obra-drawer-title h3", ".cae-obra-drawer-kick", ".cae-obra-foot a"]
    for sel in selectores:
        datos = page.evaluate(
            """
            (sel) => {
              const el = document.querySelector(sel);
              if (!el) return null;
              const fg = getComputedStyle(el).color;
              let node = el;
              let bg = 'rgba(0, 0, 0, 0)';
              while (node) {
                const c = getComputedStyle(node).backgroundColor;
                const esOpaco = /^rgba?\\(/.test(c)
                  ? (() => {
                      const m = c.match(/rgba?\\(([^)]+)\\)/);
                      const parts = m[1].split(',').map(s => parseFloat(s));
                      return !parts[3] || parts[3] >= 0.98;
                    })()
                  : (c.startsWith('oklch(') && !c.includes('/ 0)') && !c.includes('/0)'));
                if (esOpaco) { bg = c; break; }
                node = node.parentElement;
              }
              return { fg, bg };
            }
            """,
            sel,
        )
        if datos is None:
            assert_true(False, f"Contraste: no se encontro el selector '{sel}'")
            continue
        fg = _parse_rgb(datos["fg"])
        bg = _parse_rgb(datos["bg"])
        if fg is None or bg is None:
            assert_true(False, f"Contraste: '{sel}' devolvio un color que este parser minimo no cubre (fg={datos['fg']!r} bg={datos['bg']!r})")
            continue
        ratio = _ratio(fg[:3], bg[:3])
        assert_true(ratio >= 4.5, f"Contraste: '{sel}' ratio {ratio:.2f}:1 (fg={datos['fg']}, bg={datos['bg']}) — bajo AA (4.5:1)")


def check_movimiento_reducido(browser, base: str) -> None:
    """4f. Movimiento reducido: la tarjeta seleccionada aparece casi de
    inmediato (300ms, no 2500ms) y ninguna tarjeta queda con un translateY
    residual de la animacion de caida."""
    contexto = browser.new_context(viewport={"width": 1440, "height": 900}, reduced_motion="reduce")
    page = contexto.new_page()
    page.goto(f"{base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    page.click('[data-cae-ws="obra"]')
    page.wait_for_timeout(300)

    datos = page.evaluate(
        """
        () => {
          const cards = Array.from(document.querySelectorAll('.cae-obra-card'));
          return {
            haySeleccion: cards.some(c => c.classList.contains('is-sel')),
            translates: cards.map(c => {
              const t = getComputedStyle(c).transform;
              if (t === 'none') return 0;
              // matrix(a, b, c, d, tx, ty) -> el 6o componente es ty
              const m = t.match(/matrix\\(([^)]+)\\)/);
              if (!m) return 0;
              const partes = m[1].split(',').map(v => parseFloat(v));
              return partes[5] || 0;
            }),
          };
        }
        """
    )
    assert_true(datos["haySeleccion"], "Movimiento reducido: ninguna tarjeta tiene is-sel a los 300ms")
    for i, ty in enumerate(datos["translates"]):
        assert_true(abs(ty) < 0.5, f"Movimiento reducido: tarjeta {i} tiene translateY {ty:.1f}px (deberia ser 0, sin animacion de caida)")

    contexto.close()


def check_foco_visible(page) -> None:
    """4g. Foco visible — TesisFar tiene enlace real (EchoPlan es privado).
    Se tabula desde la tarjeta hasta el enlace del cajon y se comprueba que
    el foco cae ahi con un anillo visible."""
    href_esperado = PROYECTOS[1]["link_href"]
    page.evaluate("document.querySelectorAll('.cae-obra-card')[1].click()")
    page.wait_for_timeout(400)
    page.evaluate("document.querySelectorAll('.cae-obra-card')[1].focus()")

    encontrado = False
    for _ in range(15):
        page.keyboard.press("Tab")
        coincide = page.evaluate(
            "(href) => document.activeElement && document.activeElement.tagName === 'A' "
            "&& document.activeElement.href === href",
            href_esperado,
        )
        if coincide:
            encontrado = True
            break
    assert_true(encontrado, f"Foco visible: no se alcanzo por Tab el enlace del cajon de TesisFar ({href_esperado})")
    if encontrado:
        estilo_outline = page.evaluate("getComputedStyle(document.activeElement).outlineStyle")
        assert_true(estilo_outline != "none", f"Foco visible: outlineStyle del enlace es 'none' (sin anillo de foco)")


def check_vice_hyprland_intactos(browser, base: str) -> None:
    """4h. El unico invariante que establece la CSS de la Task 1: el carril
    clasico (`[data-obra-track]`) sigue visible en Vice/Hyprland y solo se
    oculta bajo Caelestia."""
    for theme, deberia_verse in (("vice", True), ("hyprland", True), ("caelestia", False)):
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(f"{base}/?theme={theme}", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        visible = page.evaluate(
            """
            () => {
              const el = document.querySelector('[data-obra-track]');
              if (!el) return false;
              return getComputedStyle(el).display !== 'none';
            }
            """
        )
        if deberia_verse:
            assert_true(visible, f"Vice/Hyprland intactos: [data-obra-track] deberia verse bajo ?theme={theme}")
        else:
            assert_true(not visible, f"Vice/Hyprland intactos: [data-obra-track] deberia estar oculto bajo ?theme={theme}")
        page.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:4173")
    args = parser.parse_args()
    viewport = {"width": 1440, "height": 900}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])

        page = browser.new_page(viewport=viewport)
        page.goto(f"{args.base}/?theme=caelestia", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        ir_a_obra(page)
        medir_cabe(page)
        check_alcanzables(page)
        check_capturas_no_cortadas(page, viewport)
        check_anti_mock(page)
        check_extremos(page)
        check_contraste(page)
        check_foco_visible(page)
        page.close()

        check_movimiento_reducido(browser, args.base)
        check_vice_hyprland_intactos(browser, args.base)

        browser.close()

    if FALLOS:
        print(f"FALLA ({len(FALLOS)}):")
        for f in FALLOS:
            print(f"  - {f}")
        return 1
    print("Todo verde.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
