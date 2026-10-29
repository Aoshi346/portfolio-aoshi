"""Arnes de verificacion visual. Cada tarea del plan anade aserciones aqui.

Uso: python3 scripts/verify.py [--theme caelestia] [--url http://127.0.0.1:5173]
             [--allow-fixture-assets] [--allow-gallery-placeholder]
Requiere el servidor de desarrollo levantado (npm run dev).

--allow-fixture-assets silencia el gate de assets provisionales (Tarea C /
defecto 3) mientras dure el desarrollo. Esta desactivado por defecto: el gate
final debe correr sin el flag.

--allow-gallery-placeholder silencia el gate del placeholder "Imagen
pendiente" de la galeria (defecto 3-bis, Task 11) mientras dure el
desarrollo. Esta desactivado por defecto: el gate final debe correr sin el
flag.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

CHROME = "/usr/bin/google-chrome"
ARGS = ["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"]
DESKTOP = {"width": 1440, "height": 900}
MOBILE = {"width": 390, "height": 844}

REPO_ROOT = Path(__file__).resolve().parent.parent

# Hashes exactos de los rellenos honestos generados con ffmpeg para la
# galeria de "Obra" (fondo solido + "CAPTURA PENDIENTE" + pie de foto — nunca
# una captura simulada de la app real). Mismo patron que FIXTURE_HASHES: el
# nombre de archivo y las dimensiones sobreviven a que el usuario suba la
# captura real; el contenido (sha256) no. En cuanto una ruta se sustituye por
# la captura definitiva, esta comprobacion deja de marcarla sola, sin tocar
# el arnes otra vez.
GALLERY_PLACEHOLDER_HASHES = {
    "public/media/obra/editor-interfaz.webp": "c2470fca671c103c70c692bbe589bb4b9aebf0fd008475d20f6c008f76d9e0a7",
    "public/media/obra/teg-entregas.webp": "4cb8c297efbaf7566f694ba40c5a35147606e67ab153b38d337f4c7f7c123595",
    "public/media/obra/teg-jurados.webp": "fa5cc1c41d9af46427199a47e2618757d272d21053af1df9f2ecdb220ce14137",
}


def check_gallery_placeholder_hashes() -> None:
    """Defecto 3-bis (rellenos): falla mientras `public/media/obra/*.webp`
    siga sirviendo los rellenos honestos generados con ffmpeg en vez de las
    capturas reales del usuario. A diferencia de `check_gallery_placeholder`
    (que detecta imagenes que ni siquiera cargan, un 404), este gate detecta
    imagenes que SI cargan pero siguen siendo el marcador "CAPTURA
    PENDIENTE" — el estado en el que quedan las nueve rutas de
    `GALLERY_PLACEHOLDER_HASHES` (las siete de la Task 11 mas las dos de
    TesisFar anadidas en la Task 12) tras sustituir el 404 por un relleno.
    Gate obligatorio, no un checklist
    opcional: sin el, un relleno podria llegar a produccion sin que nadie se
    entere. Silenciable con --allow-gallery-placeholder, igual que el resto
    del gate de galeria."""
    for rel_path, placeholder_hash in GALLERY_PLACEHOLDER_HASHES.items():
        full_path = REPO_ROOT / rel_path
        is_placeholder = full_path.exists() and sha256_of(full_path) == placeholder_hash
        check(not is_placeholder, f"{rel_path} no es el relleno honesto de la galeria")


failures: list[str] = []


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


GALLERY_SETTLE_TIMEOUT_MS = 4000
GALLERY_SETTLE_POLL_MS = 200


def check_gallery_placeholder(page) -> None:
    """Las capturas de la Editorial de Obra (`caelestiaObraEditorial.ts`,
    `/media/obra/*.webp`) tienen que cargar: una imagen rota en una seccion
    publicada es un placeholder visible, y la norma del proyecto lo prohibe.

    Las miniaturas llevan `loading="lazy"` y viven en un workspace que esta
    `inert` hasta que se abre, asi que primero se abre Obra desde la barra y
    despues se espera a que cada `<img>` resuelva (`complete` es `true` tanto
    en `load` como en `error`). Rota = resuelta con `naturalWidth` 0.

    Hasta el 2026-10-29 esto media `gallery.ts`, la galeria de las escenas de
    obra de los tres temas; Caelestia la ocultaba y se retiro."""
    page.click('[data-cae-ws="obra"]')
    page.wait_for_timeout(1500)
    elapsed = 0
    while elapsed < GALLERY_SETTLE_TIMEOUT_MS:
        pending = page.evaluate(
            "() => Array.from(document.querySelectorAll('#obra img')).filter((img) => !img.complete).length"
        )
        if pending == 0:
            break
        page.wait_for_timeout(GALLERY_SETTLE_POLL_MS)
        elapsed += GALLERY_SETTLE_POLL_MS
    else:
        print(f"  NOTA obra: alguna imagen no resolvio su carga en {GALLERY_SETTLE_TIMEOUT_MS}ms")

    total = page.evaluate("() => document.querySelectorAll('#obra img').length")
    broken = page.evaluate(
        "() => Array.from(document.querySelectorAll('#obra img'))"
        ".filter((img) => img.complete && img.naturalWidth === 0).length"
    )
    check(total > 0, "la Editorial de Obra tiene imagenes que verificar")
    check(broken == 0, f"obra: ninguna imagen rota ({broken}/{total})")


# --------------------------------------------------------------------------
# Deriva de la documentacion: las instrucciones afirman hechos sobre el codigo
# (rutas, dependencias, binarios) y nada los verificaba nunca. El 29-jul-2026
# se encontro que CINCO ficheros daban Three.js como stack y citaban
# `src/three/*`, que no existe y jamas fue dependencia; el aviso llevaba cinco
# dias anotado en un plan sin aplicarse. Peor: el snippet de `verification.md`
# — el gate de DONE — apuntaba a /usr/bin/chromium-browser, que no existe en
# esta maquina, asi que fallaba en el acto.
#
# Esta comprobacion caza esa clase entera: referencias que ya no resuelven.
# NO caza deriva semantica (que el design system citado sea de otro proyecto,
# por ejemplo); para eso hace falta revision humana.
# --------------------------------------------------------------------------

# Solo ficheros que describen ESTE proyecto. `speckit-workflow.md` y
# `loop-workflow.md` quedan fuera a proposito: son plantillas genericas con
# rutas de ejemplo (`backend/apps/[mod]`) que darian ruido en cada corrida.
DOC_FILES = [
    # El README es el documento que MAS deriva de todos: es el unico que
    # describe el proyecto entero y el unico que lee alguien de fuera, asi que
    # una ruta muerta ahi cuesta mas que en cualquier otro sitio. Entra por eso,
    # no por completismo.
    "README.md",
    "CLAUDE.md",
    ".claude/CLAUDE.md",
    ".claude/rules/code-style.md",
    ".claude/rules/verification.md",
    ".claude/rules/security.md",
    "MEMORY.md",
    ".docs/CURSOR-VICE.md",
]

# Prefijos de rutas absolutas del sistema cuya existencia se comprueba.
# El fallo original — /usr/bin/chromium-browser en el snippet del gate de
# DONE — se escapaba de una version anterior de esta regla que exigia un punto
# en el nombre del fichero, y "chromium-browser" no lo tiene.
SYSTEM_PATH_PREFIXES = ("/usr/", "/bin/", "/opt/", "/etc/", "/var/", "/srv/", "/home/")

# Prefijos que se consideran rutas del repo y deben resolver.
DOC_PATH_PREFIXES = ("src/", "scripts/", "public/", "docs/", ".docs/", ".ai/", ".claude/")

# Termino que aparece en la doc -> paquete que tendria que estar en package.json.
# Si el termino aparece SIN negacion y el paquete no esta instalado, es deriva.
DOC_DEPENDENCY_TERMS = {
    "three.js": "three",
    "react": "react",
    "vue": "vue",
    "svelte": "svelte",
    "next.js": "next",
    "gsap": "gsap",
    "lenis": "lenis",
}

# Una linea que niega el termino no es una afirmacion falsa: "sin Three.js" o
# "no Three.js" es justo lo que queremos que la doc diga.
DOC_NEGATIONS = ("sin ", "no ", "nunca", "obsolet", "ya no", "jamas", "en vez de", "NO ")


def _doc_paragraphs(text: str) -> list[str]:
    """
    El texto partido en parrafos de markdown (bloques separados por linea en
    blanco), en el mismo orden.

    La negacion se evalua sobre el PARRAFO y no sobre la linea porque una frase
    con salto de linea duro se reparte entre varias lineas y la negacion cae en
    otra que el termino. Caso real que dejaba el gate en rojo permanente
    (29-jul-2026): esta misma regla, en `.claude/rules/verification.md`, cuenta
    el fallo historico nombrando "Three.js" y `src/three/*` al final de una
    linea y aclarando "que no existe y nunca fue dependencia" en la siguiente.
    Con la ventana de una linea el arnes se acusaba a si mismo.

    El coste esta medido y aceptado: un parrafo que niegue una cosa y afirme
    otra falsa en la misma respiracion se escapa. Se elige asi porque un gate
    que falla siempre no se lee — y ese modo de fallo ya se pago una vez.
    """
    return re.split(r"\n\s*\n", text)


def _doc_citations(text: str) -> list[str]:
    """Todo lo citado entre acentos graves, sin puntuacion de cierre."""
    out = []
    for raw in re.findall(r"`([^`\n]+)`", text):
        token = raw.strip().rstrip(".,;:)").strip()
        if token:
            out.append(token)
    return out


def check_docs_references() -> None:
    """Falla si la documentacion cita rutas, binarios o dependencias inexistentes."""
    print("[docs] referencias de la documentacion")

    pkg_path = REPO_ROOT / "package.json"
    installed: set[str] = set()
    if pkg_path.exists():
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        installed = set(pkg.get("dependencies", {})) | set(pkg.get("devDependencies", {}))

    bad_paths: list[str] = []
    bad_bins: list[str] = []
    bad_deps: list[str] = []

    for rel in DOC_FILES:
        doc = REPO_ROOT / rel
        if not doc.exists():
            # No es fallo: varios de estos estan en .gitignore y pueden no
            # existir en un clon limpio.
            continue
        text = doc.read_text(encoding="utf-8")

        for parrafo in _doc_paragraphs(text):
            negado = any(neg.lower() in parrafo.lower() for neg in DOC_NEGATIONS)

            for token in _doc_citations(parrafo):
                # Placeholders de plantilla: `src/sections/[nombre].ts`, `${VAR}`.
                if any(ch in token for ch in "[]<>${}"):
                    continue

                if token.startswith(DOC_PATH_PREFIXES):
                    # Una ruta citada dentro de una frase que la niega ("`src/three/*`,
                    # que no existe") es documentacion correcta del fallo, no el fallo.
                    if negado:
                        continue
                    target = token.rstrip("/")
                    if "*" in target:
                        if not list(REPO_ROOT.glob(target)):
                            bad_paths.append(f"{rel} -> {token}")
                    elif not (REPO_ROOT / target).exists():
                        bad_paths.append(f"{rel} -> {token}")

                elif token.startswith(SYSTEM_PATH_PREFIXES) and " " not in token:
                    # Ruta absoluta a un binario o fichero del sistema. Se exige el
                    # prefijo para no confundirla con un slash-command (`/dream`) ni
                    # con una ruta servida por HTTP (`/files/...`).
                    #
                    # Los binarios NO llevan escape de negacion: el fallo original
                    # era justo un snippet que apuntaba a /usr/bin/chromium-browser
                    # y lo rodeaba de prosa explicativa. Aqui interesa que exista.
                    if not Path(token).exists():
                        bad_bins.append(f"{rel} -> {token}")

        for term, package in DOC_DEPENDENCY_TERMS.items():
            if package in installed:
                continue
            # Palabra completa, no subcadena: "vue" hacia match dentro de
            # "vuelve" y "react" dentro de cualquier palabra que lo contenga.
            pattern = re.compile(r"(?<![\w.])" + re.escape(term) + r"(?![\w])", re.IGNORECASE)
            if not pattern.search(text):
                continue
            for parrafo in _doc_paragraphs(text):
                if not pattern.search(parrafo):
                    continue
                if any(neg.lower() in parrafo.lower() for neg in DOC_NEGATIONS):
                    continue
                bad_deps.append(f"{rel} -> '{term}' pero '{package}' no esta en package.json")
                break

    check(not bad_paths, f"la doc no cita rutas inexistentes ({bad_paths[:3]})")
    check(not bad_bins, f"la doc no cita binarios inexistentes ({bad_bins[:3]})")
    check(not bad_deps, f"la doc no cita dependencias no instaladas ({bad_deps[:3]})")


# Vocabulario cerrado del campo `Estado:` de un spec. Cerrado a proposito: con
# prosa libre nadie puede cruzar el estado declarado contra nada.
SPEC_STATES = (
    "en diseno",
    "pendiente de plan",
    "en ejecucion",
    "implementado",
    "descartado",
)

# Un plan que nunca se marco casilla a casilla lleva esta marca en cabecera. No
# es una excusa: es la verdad registrada, y es mejor que ticar en bloque 141
# casillas de trabajo que nadie siguio paso a paso.
PLAN_HISTORIC_MARKER = "Tracking: historico"


def _normaliza(texto: str) -> str:
    """Minusculas sin markdown ni acentos, para comparar el estado declarado."""
    out = texto.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        out = out.replace(a, b)
    return out.replace("*", "").replace("`", "").replace("_", "")


def check_spec_plan_consistency() -> None:
    """
    Falla si el estado declarado de un spec contradice las casillas de su plan.

    Nace del fallo del 29-jul-2026: las ocho tareas del cartel de reparto se
    ejecutaron y commitearon con las 47 casillas del plan sin marcar, y al
    cerrarlas de golpe al final hubo que reconstruir el estado leyendo commits —
    que es justo donde aparecieron cuatro divergencias que nadie habia anotado.
    `.claude/rules/speckit-progress-tracking.md` ya lo prohibia; lo que faltaba
    no era la regla, era que algo la comprobara.

    Se comprueba una contradiccion, no la disciplina: un plan a medio marcar es
    trabajo en curso y es legitimo. Lo que no puede ser es que el spec diga
    "implementado" y su plan siga con pasos pendientes, ni al contrario.
    """
    print("[docs] estado de specs y planes")

    specs = sorted((REPO_ROOT / "docs/superpowers/specs").glob("*.md"))
    planes = sorted((REPO_ROOT / "docs/superpowers/plans").glob("*.md"))
    if not specs:
        check(True, "no hay specs que cruzar")
        return

    sin_estado: list[str] = []
    estado_ambiguo: list[str] = []
    contradicciones: list[str] = []
    planes_citados: dict[Path, str] = {}

    for spec in specs:
        rel = spec.relative_to(REPO_ROOT).as_posix()
        texto = spec.read_text(encoding="utf-8")

        # "estado:" en cualquier parte de la linea, no solo al principio: los dos
        # specs de julio lo llevan compartido con la fecha ("Fecha: ... · Estado:
        # ...") y exigir que abriera linea los dejaba pasar sin mirar, que es el
        # agujero por el que se colaron dos estados falsos.
        linea = next((ln for ln in texto.splitlines() if "estado:" in _normaliza(ln)), None)
        if linea is None:
            sin_estado.append(rel)
            continue

        encontrados = [s for s in SPEC_STATES if s in _normaliza(linea)]
        if len(encontrados) != 1:
            estado_ambiguo.append(f"{rel} -> {encontrados or 'ninguno del vocabulario'}")
            continue
        estado = encontrados[0]

        # El plan se localiza por el puntero que el propio spec declara. Si no
        # cita ninguno, no hay nada que cruzar: no todo spec tiene plan.
        cita = next(
            (t for t in _doc_citations(texto) if t.startswith("docs/superpowers/plans/")), None
        )
        if cita is None:
            continue
        plan = REPO_ROOT / cita
        # `is_file()` y no `exists()`: un spec puede citar el DIRECTORIO de
        # planes en prosa —"no lleva plan en `docs/superpowers/plans/`"— y ahi
        # `exists()` dice si, con lo que el `read_text()` de abajo revienta con
        # IsADirectoryError y se lleva por delante el arnes entero antes de
        # abrir el navegador. Paso de fallo real, no hipotetico: lo disparo el
        # spec de about al declararse implementado sin plan.
        if not plan.is_file():
            continue  # check_docs_references() ya se queja de la ruta muerta
        planes_citados[plan] = estado

        cuerpo = plan.read_text(encoding="utf-8")
        if PLAN_HISTORIC_MARKER in cuerpo:
            continue
        pendientes = len(re.findall(r"^\s*- \[ \]", cuerpo, re.MULTILINE))
        hechas = len(re.findall(r"^\s*- \[x\]", cuerpo, re.MULTILINE))

        if estado == "implementado" and pendientes:
            contradicciones.append(
                f"{rel} dice 'implementado' pero {cita} tiene {pendientes} pasos sin marcar"
            )
        if pendientes == 0 and hechas and estado != "implementado":
            contradicciones.append(
                f"{cita} esta marcado al completo pero {rel} dice '{estado}'"
            )

    for plan in planes:
        rel = plan.relative_to(REPO_ROOT).as_posix()
        cuerpo = plan.read_text(encoding="utf-8")
        if PLAN_HISTORIC_MARKER in cuerpo or plan in planes_citados:
            continue
        pendientes = len(re.findall(r"^\s*- \[ \]", cuerpo, re.MULTILINE))
        hechas = len(re.findall(r"^\s*- \[x\]", cuerpo, re.MULTILINE))
        if pendientes and not hechas:
            contradicciones.append(
                f"{rel} tiene {pendientes} pasos y ninguno marcado, y ningun spec lo reclama: "
                f"marca el progreso o pon '{PLAN_HISTORIC_MARKER}' en cabecera"
            )

    check(not sin_estado, f"todo spec declara Estado: ({sin_estado[:3]})")
    check(not estado_ambiguo, f"el Estado: usa el vocabulario cerrado ({estado_ambiguo[:3]})")
    check(not contradicciones, f"el estado del spec concuerda con su plan ({contradicciones[:3]})")


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


# --------------------------------------------------------------------------
# Linea base de fallos conocidos.
#
# El problema que resuelve, medido el 29-jul-2026: el arnes salia SIEMPRE con
# codigo 1, porque arrastra 12 fallos de fixtures pendientes de sustituir. Un
# gate que nunca se pone verde no se lee — es el mismo modo de fallo que tuvo el
# gate documental cuando se acusaba a si mismo. Con 12 fallos fijos en pantalla,
# el 13 no lo ve nadie, y distinguirlos obligaba a filtrar la salida a mano en
# cada ejecucion.
#
# Por que no bastan `--allow-fixture-assets` y `--allow-gallery-placeholder`,
# que ya existian y dejan el arnes en verde: silencian CATEGORIAS enteras. Con
# ellos puestos, una imagen de galeria que falte manana tampoco se ve. La linea
# base guarda los fallos concretos, asi que un fallo nuevo de la misma categoria
# sigue saltando.
#
# La comparacion normaliza los numeros del texto: varias etiquetas llevan
# medidas dentro (ratios de contraste, pixeles) que oscilan entre ejecuciones
# porque el fondo es generativo. Sin normalizar, "ratio 6.97:1" y "ratio 7.00:1"
# serian dos fallos distintos y la base daria falsas alarmas cada dia.
# --------------------------------------------------------------------------

BASELINE_PATH = REPO_ROOT / "scripts" / "verify-baseline.json"


def _clave_fallo(label: str) -> str:
    """Etiqueta sin sus numeros, para que las medidas que oscilan no cuenten."""
    return re.sub(r"\d+(?:[.,]\d+)?", "#", label)


def escribir_baseline(actuales: list[str]) -> None:
    BASELINE_PATH.write_text(
        json.dumps(
            {
                "_comentario": (
                    "Fallos conocidos y aceptados de scripts/verify.py. El arnes sale 0 "
                    "mientras la ejecucion coincida con esta lista, y 1 en cuanto aparezca "
                    "uno nuevo O se arregle uno de estos sin quitarlo de aqui. Regenerar "
                    "con: python3 scripts/verify.py --update-baseline"
                ),
                "fallos": sorted(actuales),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def comparar_con_baseline(actuales: list[str]) -> int:
    if not BASELINE_PATH.exists():
        if actuales:
            print(f"FALLOS: {len(actuales)} (sin linea base; crea una con --update-baseline)")
            return 1
        print("TODO OK")
        return 0

    base = json.loads(BASELINE_PATH.read_text(encoding="utf-8")).get("fallos", [])
    claves_base = [_clave_fallo(f) for f in base]
    claves_ahora = [_clave_fallo(f) for f in actuales]

    nuevos = [a for a, k in zip(actuales, claves_ahora) if k not in claves_base]
    # Un fallo de la base que ya no aparece tambien rompe el gate, a proposito:
    # una linea base que se queda grande vuelve a esconder cosas, que es
    # exactamente lo que se venia a evitar.
    resueltos = [b for b, k in zip(base, claves_base) if k not in claves_ahora]

    if nuevos:
        print(f"FALLOS NUEVOS: {len(nuevos)} (fuera de la linea base)")
        for f in nuevos:
            print(f"  - {f}")
    if resueltos:
        print(f"ARREGLADOS respecto a la linea base: {len(resueltos)}")
        for f in resueltos:
            print(f"  - {f}")
        print("  Quitalos de la base: python3 scripts/verify.py --update-baseline")

    if nuevos or resueltos:
        return 1

    if actuales:
        print(f"TODO OK — {len(actuales)} fallos conocidos, 0 nuevos ({BASELINE_PATH.name})")
    else:
        print("TODO OK")
    return 0


# --------------------------------------------------------------------------
# Contraste WCAG AA — medido sobre el PIXEL renderizado, no sobre el CSS.
#
# Por que pixel y no `getComputedStyle` a secas: el fondo efectivo de un texto
# en este sitio casi nunca es un `background-color` solido y ancestro directo.
# `.bg-theme` es un canvas WebGL/shader (o video+poster en Vice) fijo detras
# de TODO el sitio (z-index -20, ver style.css); encima puede haber un scrim
# en gradiente, y encima de eso una tarjeta con `backdrop-filter: blur()`
# (Caelestia). Sumar esas capas "a mano" leyendo el DOM/CSS es o bien
# incorrecto (backdrop-filter no es componible por formula simple) o bien
# requiere reimplementar un compositor. En vez de eso: se hace una captura
# real de la pagina ya renderizada (canvas + blur + scrims incluidos) y se
# muestrea el pixel de fondo efectivo directamente del PNG.
#
# Metodo:
#   1. Playwright entrega el rect (viewport-relative, device-scale-factor=1)
#      de cada nodo de texto hoja visible.
#   2. Se muestrean varias franjas de pixeles pegadas al borde del rect
#      (arriba, abajo, izquierda, derecha) en el screenshot ya compuesto.
#   3. Se cuantizan esos pixeles y se toma la moda: es el fondo efectivo.
#   4. El color de texto (con su propio alfa, via getComputedStyle) se
#      compone sobre ese fondo para obtener el color de tinta EFECTIVO.
#   5. Ratio WCAG entre tinta efectiva y fondo efectivo; umbral 3:1 si el
#      texto es "grande" (>=24px, o >=18.66px en negrita), 4.5:1 si no.
#
# Limites conocidos (deliberados, no bugs):
#   - Si las franjas muestreadas no son uniformes (>2 colores cuantizados
#     distintos), el fondo no es un color solido en ese punto — casi siempre
#     porque el texto esta directamente sobre video/imagen/canvas con detalle
#     (sin scrim, sin tarjeta). Ese caso se EXCLUYE del gate pass/fail y se
#     reporta explicitamente como "excluido" con la razon, en vez de forzar
#     un veredicto sobre un fondo que no es una sola muestra representativa.
#   - Fondo de VIDEO (Vice): el video es dinamico en el tiempo; el ratio
#     medido es una fotografia del frame en el instante de la captura
#     (t~3.5s tras cargar), no una garantia para todos los frames. Vice ya
#     lleva un scrim fijo (`.bg-theme::after`) precisamente para acotar este
#     riesgo, pero el arnes no puede probar "todos los frames posibles".
#   - Solo cubre desktop 1440x900 (mismo viewport que el resto del arnes).
#   - No seguimos gradientes de TEXTO (`background-clip: text`): no se usan
#     en este proyecto, pero si se introdujeran, `color` de por si no
#     reflejaria el pixel real y el check quedaria invalidado silenciosamente.
CONTRAST_MIN_NORMAL = 4.5
CONTRAST_MIN_LARGE = 3.0
# Desviacion tipica maxima (por canal, 0-255) tolerada en la muestra de fondo
# para considerarla "un color solido". El grano de `.bg-noise` (opacity
# 0.035) y el antialiasing del texto meten ruido de +-5 incluso sobre un
# fondo solido real; un umbral demasiado bajo marcaria como "no solido"
# fondos que en la practica son planos, y uno demasiado alto dejaria pasar
# video/imagen con detalle real. 18 es el punto donde el grano cae dentro
# pero un borde de video/imagen con contraste real lo supera.
MAX_BG_STDDEV = 18.0
# Separacion del borde del texto para evitar leer antialiasing del propio
# glifo (ascendentes/descendentes) como si fuera "fondo".
SAMPLE_GAP = 5
SAMPLE_THICKNESS = 5


def _relative_luminance(rgb: tuple[float, float, float]) -> float:
    def channel(c: float) -> float:
        cs = c / 255
        return cs / 12.92 if cs <= 0.03928 else ((cs + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast_ratio(fg: tuple[float, float, float], bg: tuple[float, float, float]) -> float:
    l1 = _relative_luminance(fg) + 0.05
    l2 = _relative_luminance(bg) + 0.05
    return max(l1, l2) / min(l1, l2)


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, v))


def _oklab_to_srgb255(l: float, a_: float, b_: float) -> tuple[float, float, float]:
    """OKLab -> sRGB (0..255). Matrices estandar de Bjorn Ottosson."""
    l_ = l + 0.3963377774 * a_ + 0.2158037573 * b_
    m_ = l - 0.1055613458 * a_ - 0.0638541728 * b_
    s_ = l - 0.0894841775 * a_ - 1.2914855480 * b_
    l3, m3, s3 = l_**3, m_**3, s_**3

    lin_r = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    lin_g = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    lin_b = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3

    def to_gamma(c: float) -> float:
        c = _clamp01(c)
        return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

    return to_gamma(lin_r) * 255, to_gamma(lin_g) * 255, to_gamma(lin_b) * 255


def _parse_css_color(css: str) -> tuple[float, float, float, float]:
    """Parsea el color que devuelve `getComputedStyle` en Chromium.

    Formatos observados en este proyecto:
      - `rgb(r, g, b)` / `rgba(r, g, b, a)` — la mayoria de los casos.
      - `color(srgb r g b / a)` — variante de CSS Color 4 con r/g/b en 0..1.
      - `oklab(L a b / alpha)` — Chromium serializa ASI un color resuelto por
        Tailwind 4 al aplicar opacidad sobre un token `@theme`
        (`text-paper/85`): la resolucion interna usa OKLab/relative color
        syntax y el computed style vuelve en ese espacio, no en rgb(). Sin
        convertir esto, el parser reventaba (visto en el FAIL real contra
        `.lead.text-paper/85`) — no es un caso hipotetico, es el formato que
        Chromium realmente devuelve para varias utilidades de este sitio.
      En los tres casos los canales pueden salirse ligeramente de 0..1/0..255
      por interpolacion; se clampan.
    """
    css = css.strip()
    inner = css[css.index("(") + 1 : css.rindex(")")]

    if css.startswith("oklab("):
        comps, _, alpha_s = inner.partition("/")
        vals = [float(v) for v in comps.split()]
        r, g, b = _oklab_to_srgb255(*vals)
        a = float(alpha_s.strip()) if alpha_s.strip() else 1.0
        return r, g, b, a

    if css.startswith("oklch("):
        comps, _, alpha_s = inner.partition("/")
        l_s, c_s, h_s = comps.split()
        l = float(l_s[:-1]) / 100 if l_s.endswith("%") else float(l_s)
        c = float(c_s)
        h = math.radians(float(h_s.removesuffix("deg")))
        r, g, b = _oklab_to_srgb255(l, c * math.cos(h), c * math.sin(h))
        a = float(alpha_s.strip()) if alpha_s.strip() else 1.0
        return r, g, b, a

    if css.startswith("color("):
        body = inner.replace("srgb", "").strip()
        comps, _, alpha_s = body.partition("/")
        r01, g01, b01 = (float(v) for v in comps.split())
        a = float(alpha_s.strip()) if alpha_s.strip() else 1.0
        return _clamp01(r01) * 255, _clamp01(g01) * 255, _clamp01(b01) * 255, a

    parts = [p.strip() for p in inner.split(",")]
    r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
    a = float(parts[3]) if len(parts) > 3 else 1.0
    return r, g, b, a


def _composite(fg_rgba: tuple[float, float, float, float], bg_rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b, a = fg_rgba
    return (
        r * a + bg_rgb[0] * (1 - a),
        g * a + bg_rgb[1] * (1 - a),
        b * a + bg_rgb[2] * (1 - a),
    )


def _sample_strip(img: Image.Image, x0: float, y0: float, x1: float, y1: float) -> list[tuple[int, int, int]]:
    width, height = img.size
    x0i, x1i = max(0, int(x0)), min(width, int(x1))
    y0i, y1i = max(0, int(y0)), min(height, int(y1))
    if x1i <= x0i or y1i <= y0i:
        return []
    region = img.crop((x0i, y0i, x1i, y1i)).convert("RGB")
    return list(region.getdata())


def check_contrast_wcag(page, theme: str, screenshot_bytes: bytes) -> None:
    """Defecto de contraste (barra de esquina del hero): el bug real era un
    `color: rgb(255 244 232 / 0.6)` fijado a mano en `.hero-corner`, el mismo
    en los tres temas, ilegible en Caelestia (fondo claro). Este check no
    apunta solo a esa clase: barre TODO el texto hoja visible del viewport
    para que cualquier color fijado a mano que rompa el contraste en algun
    tema quede atrapado, no solo el caso ya conocido.

    Excluye texto marcado `[data-decorative]` (o dentro de un ancestro con ese
    atributo): WCAG 1.4.3 exime explicitamente el texto puramente decorativo,
    sin contenido informativo, del minimo de contraste. `data-decorative` es
    un marcador propio de este proyecto, de un unico significado, reservado a
    quien lo lea: "esto es decoracion pura, ignoralo". Los ordinales gigantes
    de fondo ("01"/"02" al 6% de alfa en `caseStudyPanel.ts` y `[data-ord]` en
    `projectScene.ts`) son el caso legitimo: el orden real lo da el DOM, el
    numero visible es watermark, no informacion.

    Antes esta exencion reutilizaba `[aria-hidden="true"]`, que NO significa
    "decorativo": solo oculta el nodo a tecnologias de asistencia, y en este
    proyecto se usa tambien por motivos que nada tienen que ver con
    decoracion — p.ej. `.gallery-fallback` ("Imagen pendiente" en
    `gallery.ts`) lleva `aria-hidden="true"` para no duplicar al lector de
    pantalla el `alt` de la imagen, pero su texto SI es informativo para
    quien ve la pantalla (avisa de que la imagen no cargo). Reutilizar
    `aria-hidden` como exencion de contraste dejaba una puerta abierta:
    bastaba anadir ese atributo a cualquier texto para sacarlo del gate, la
    misma clase de regresion que este gate existe para atrapar. Con
    `data-decorative` la exencion queda acotada a lo que de verdad es
    decoracion, sin arrastrar los demas usos legitimos de `aria-hidden`.

    Encontrado al instrumentar la Task 8 (`data-scene="obra"` nuevo en el
    gate bajo el pliegue): el filtro de opacidad de mas abajo no lo atrapaba
    porque el alfa vive en `color`, no en la propiedad `opacity`."""
    candidates = page.evaluate(
        r"""(() => {
      const out = [];
      const nodes = document.querySelectorAll('body *');
      for (const el of nodes) {
        if (el.children.length > 0) continue; // solo hojas
        const text = (el.textContent || '').trim();
        if (!text) continue;
        if (el.closest('[data-decorative]')) continue; // decorativo, exento por WCAG 1.4.3
        /*
         * `.scene-index` (el menu de navegacion) se OCULTA con
         * `clip-path: inset(0 0 100% 0)`, no con `display`/`visibility`: su
         * fondo solido (`--color-ink`) deja de pintarse pero el texto sigue
         * teniendo un rect valido y `opacity: 1`, asi que el filtro de mas
         * abajo no lo atrapaba. El resultado era medir el rotulo del menu
         * CERRADO contra lo que hay detras en la pagina (fondo Ascua, muy
         * variable) en vez de contra su propio telon opaco cuando esta
         * abierto — encontrado al instrumentar Ascua, con el fondo animado
         * nuevo exponiendo un hueco que ya existia para los tres temas.
         */
        if (el.closest('.scene-index') && !el.closest('.scene-index.is-open')) continue;
        /*
         * Texto RECORTADO por un ancestro con `overflow: hidden`: conserva un
         * rect valido, asi que el gate lo medía contra lo que hay detras en la
         * pagina, aunque no se vea nunca.
         *
         * El caso que lo destapo: el disparador de Hyprland apila dos versiones
         * del rotulo en la misma celda y desplaza la que no toca 38px fuera de
         * un contenedor recortado. El gate daba OK 17.75:1 a "Cerrar" — que en
         * reposo no se ve — mientras el rotulo VISIBLE salia SKIP por fondo no
         * solido. Neto: el widget parecia cubierto y verde y su texto real no
         * lo medía nadie. Un OK fantasma es peor que un hueco, porque ademas
         * cuenta para el suelo de "al menos un elemento medible por escena".
         */
        let clipped = false;
        for (let a = el.parentElement; a && a !== document.body; a = a.parentElement) {
          const ov = getComputedStyle(a);
          if (ov.overflow === 'visible' && ov.overflowX === 'visible'
              && ov.overflowY === 'visible') continue;
          const ar = a.getBoundingClientRect();
          const er = el.getBoundingClientRect();
          if (er.bottom <= ar.top + 1 || er.top >= ar.bottom - 1
              || er.right <= ar.left + 1 || er.left >= ar.right - 1) { clipped = true; break; }
        }
        if (clipped) continue;
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || style.display === 'none') continue;
        if (parseFloat(style.opacity) < 0.2) continue;
        const rect = el.getBoundingClientRect();
        if (rect.width < 2 || rect.height < 2) continue;
        if (rect.bottom <= 0 || rect.top >= window.innerHeight) continue;
        if (rect.right <= 0 || rect.left >= window.innerWidth) continue;
        /*
         * Tipografia en CONTORNO: si `color` es transparente pero el elemento
         * lleva `-webkit-text-stroke`, lo que se ve es el trazo, y el color del
         * trazo es el primer plano real. Sin esto el arnes leia `color:
         * transparent`, lo componia sobre el fondo y obtenia fg == bg, o sea
         * 1.00:1 — un fallo fantasma sobre texto perfectamente legible (medido
         * aparte en 12.88:1). Lo destaparon las tres afirmaciones de "Quien es"
         * en Vice, que van en contorno de 0.028em a proposito.
         */
        const strokeW = parseFloat(style.webkitTextStrokeWidth) || 0;
        const strokeC = style.webkitTextStrokeColor;
        const pintaSoloElTrazo =
          /^(transparent|rgba\(0,\s*0,\s*0,\s*0\))$/.test(style.color.trim()) && strokeW > 0;
        /*
         * Mismo defecto, otra tecnica: `background-clip: text` (Hyprland,
         * tarea 2 de Ascua) tambien deja `color: transparent` en el
         * elemento, y el pixel real que se ve es un degradado recortado al
         * glifo, no un solido. Componer `transparent` sobre el fondo da
         * fg == bg exacto — el mismo fallo fantasma que el contorno, medido
         * aparte en 14.4:1 (ver Tarea 9). Sin forma fiable de reducir un
         * degradado a un unico par fg/bg, se excluye aqui igual que un fondo
         * de video/canvas no solido, no se inventa un color.
         */
        const colorTransparente = /^(transparent|rgba\(0,\s*0,\s*0,\s*0\))$/.test(
          style.color.trim(),
        );
        const recortadoAGlifo =
          (style.backgroundClip === "text" || style.webkitBackgroundClip === "text") &&
          colorTransparente &&
          strokeW === 0;
        out.push({
          tag: el.tagName.toLowerCase(),
          text: text.slice(0, 40),
          color: pintaSoloElTrazo ? strokeC : style.color,
          recortadoAGlifo,
          fontSize: parseFloat(style.fontSize),
          fontWeight: style.fontWeight,
          rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height },
        });
      }
      return out;
    })()"""
    )

    img = Image.open(BytesIO(screenshot_bytes))
    checked = 0
    excluded = 0

    for c in candidates:
        rect = c["rect"]
        x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]
        gap, thick = SAMPLE_GAP, SAMPLE_THICKNESS
        samples: list[tuple[int, int, int]] = []
        samples += _sample_strip(img, x, y - gap - thick, x + w, y - gap)  # arriba
        samples += _sample_strip(img, x, y + h + gap, x + w, y + h + gap + thick)  # abajo
        samples += _sample_strip(img, x - gap - thick, y, x - gap, y + h)  # izquierda
        samples += _sample_strip(img, x + w + gap, y, x + w + gap + thick, y + h)  # derecha

        label_base = f"contraste AA — {theme}: {c['tag']} \"{c['text']}\""

        if c.get("recortadoAGlifo"):
            # `background-clip: text` no tiene un fg solido que leer de
            # `color` (ver comentario en el evaluate de arriba): excluido del
            # gate automatico, igual que un fondo de video/canvas no solido.
            # La medida real de este texto la hace la Tarea 9, paso 4, con
            # recorte ajustado al glifo.
            excluded += 1
            print(f"  SKIP {label_base} (background-clip:text — medido aparte, ver Tarea 9)")
            continue

        if len(samples) < 8:
            excluded += 1
            print(f"  SKIP {label_base} (sin margen suficiente para muestrear fondo)")
            continue

        n = len(samples)
        means = [sum(s[ch] for s in samples) / n for ch in range(3)]
        variances = [sum((s[ch] - means[ch]) ** 2 for s in samples) / n for ch in range(3)]
        stddevs = [v**0.5 for v in variances]

        if max(stddevs) > MAX_BG_STDDEV:
            # Fondo no uniforme bajo el muestreo: video/imagen/canvas con
            # detalle real justo ahi, sin scrim ni tarjeta solida encima.
            # Se excluye del gate pass/fail — no es un color solido y no hay
            # forma fiable de reducirlo a un solo par fg/bg comparable.
            excluded += 1
            print(
                f"  SKIP {label_base} (fondo no solido bajo el texto — "
                f"desviacion tipica {max(stddevs):.1f} > {MAX_BG_STDDEV}; "
                "probablemente video/imagen/canvas sin scrim solido, excluido "
                "del gate de contraste, no silenciado)"
            )
            continue

        bg_rgb = tuple(round(m) for m in means)
        r, g, b, a = _parse_css_color(c["color"])
        fg_rgb = _composite((r, g, b, a), bg_rgb)
        ratio = _contrast_ratio(fg_rgb, bg_rgb)

        font_weight = c["fontWeight"]
        weight_num = 700 if font_weight == "bold" else (400 if font_weight == "normal" else int(float(font_weight)))
        is_large = c["fontSize"] >= 24 or (weight_num >= 700 and c["fontSize"] >= 18.66)
        threshold = CONTRAST_MIN_LARGE if is_large else CONTRAST_MIN_NORMAL

        checked += 1
        check(
            ratio >= threshold,
            f"{label_base}: ratio {ratio:.2f}:1 (min {threshold}:1, fg={tuple(round(v) for v in fg_rgb)}, "
            f"bg={bg_rgb}, desv.tipica={max(stddevs):.1f}, n={n})",
        )

    print(f"  [contraste] {checked} elementos evaluados, {excluded} excluidos (fondo no muestreable/no solido)")

    # Hallazgo I-1 de la revision final: el gate median CERO elementos en
    # hero y contacto (los candidatos ahi caen todos en la exclusion de
    # "fondo no solido") y aun asi `main()` solo cuenta `failures` — cero
    # aserciones evaluadas es indistinguible de "todo paso" para el
    # contador, asi que imprimia TODO OK con una escena entera sin vigilar.
    # La degradacion es ademas SILENCIOSA y UNIDIRECCIONAL: cuanto peor el
    # fondo bajo un texto, menos mide el gate y mas verde se ve — el
    # incentivo va justo al reves de lo que hace falta. Este suelo de
    # cobertura lo hace ruidoso: si una escena no logra medir NINGUN
    # elemento, es un FAIL explicito, no un SKIP mas que main() ignora.
    # Umbral en 1 (no un porcentaje del total de candidatos): con 0
    # medibles no hay ninguna garantia de contraste en la escena, sea cual
    # sea el numero de exclusiones; con 1 o mas, al menos una pieza de
    # texto real quedo verificada. Subir el umbral a un porcentaje fijo
    # penalizaria escenas con mucho texto decorativo/sobre imagen por
    # diseno (parte del limite conocido y declarado del gate), que no es el
    # problema que este hallazgo describe.
    check(
        checked >= 1,
        f"cobertura de contraste — {theme}: al menos un elemento medible "
        f"(evaluados={checked}, excluidos={excluded}) — cero evaluados en una "
        "escena a plena luz es un agujero de cobertura, no un fondo dificil",
    )


# --------------------------------------------------------------------------
# Contraste bajo el pliegue — recorre cada [data-scene] y repite el barrido.
#
# El gate original tomaba una sola captura justo tras `goto`: solo el primer
# viewport quedaba vigilado. El defecto real que motivo esto (acento sobre
# fondo crudo en "Quien es" de Caelestia, por debajo del pliegue en 1440x900)
# no lo caza ese gate — hizo falta un script suelto para encontrarlo. Esta
# funcion cierra ese hueco: por cada escena marcada `[data-scene]` hace scroll
# hasta ella y repite `check_contrast_wcag` ahi.
#
# Por que rueda simulada y no `window.scrollTo`/`scrollIntoView` directos:
# Lenis (`src/utils/reveal.ts`) intercepta la rueda para animar el scroll con
# inercia (`duration: 1.15`); un salto de posicion via `scrollTo` cambia el
# scroll del documento pero no pasa por esa animacion, así que no reproduce
# las condiciones reales bajo las que se vio el defecto (fondo shader/blur
# todavia interpolando). Se dispara con `page.mouse.wheel` en pasos, como
# haria un visitante real, y luego se espera a que `window.scrollY` deje de
# cambiar entre lecturas (asentado), en vez de un `wait_for_timeout` fijo:
# el tiempo real hasta asentar depende de la distancia recorrida, no es
# constante.
#
# Limite nuevo (deliberado): solo cubre escenas que ya llevan el atributo
# `[data-scene]`. Secciones aun sin construir (contact, skills, experience,
# caseStudies fuera de las 2 primeras) no estan instrumentadas todavia y no
# se cubren hasta que lo esten — no es un fondo no muestreable, es que la
# escena no existe como tal en el DOM.
SETTLE_POLL_MS = 150
SETTLE_STABLE_READS = 2
SETTLE_TIMEOUT_MS = 4000
WHEEL_STEP = 800
WHEEL_STEP_PAUSE_MS = 80


def _scroll_to_and_settle(page, target_y: float) -> None:
    """Encontrado al instrumentar la Task 9 (quinta escena, `data-scene="credits"`,
    anadida al final del documento): forzar `window.scrollTo(0, 0)` antes de
    cada barrido desincroniza a Lenis. Lenis intercepta el wheel y lleva su
    propio "target" de scroll suave; `window.scrollTo` mueve el scroll nativo
    pero no el estado interno de Lenis. En la siguiente llamada, los deltas de
    `mouse.wheel` se sumaban al target STALE de Lenis (el de la escena
    anterior), no a 0 — el resultado era un sobre-scroll que aterrizaba en el
    maximo scrolleable del documento en vez del target pedido. Con 4 escenas
    pasaba desapercibido (la escena 2 sobre-scrolleaba exactamente a la
    posicion de la escena 3, ambas "obra": mismo texto, ningun sintoma
    visible). Con la quinta escena el sobre-scroll aterrizaba dentro de
    "creditos", y el gate de contraste se puso a medir texto de creditos
    etiquetado como "obra" — la escena de obra real dejaba de verificarse.
    Fix: no resetear a 0 nunca; mover solo el delta real desde la posicion
    actual (que ya deberia coincidir con el target anterior, por eso la
    funcion se llama "settle"), en cualquier direccion."""
    current = page.evaluate("window.scrollY")
    remaining = target_y - current
    direction = 1 if remaining >= 0 else -1
    remaining = abs(remaining)
    while remaining > 1:
        delta = min(WHEEL_STEP, remaining)
        page.mouse.wheel(0, direction * delta)
        remaining -= delta
        page.wait_for_timeout(WHEEL_STEP_PAUSE_MS)

    last: float | None = None
    stable_reads = 0
    elapsed = 0
    while elapsed < SETTLE_TIMEOUT_MS:
        page.wait_for_timeout(SETTLE_POLL_MS)
        elapsed += SETTLE_POLL_MS
        current = page.evaluate("window.scrollY")
        if last is not None and abs(current - last) < 0.5:
            stable_reads += 1
            if stable_reads >= SETTLE_STABLE_READS:
                return
        else:
            stable_reads = 0
        last = current
    print(f"  NOTA scroll no se asento en {SETTLE_TIMEOUT_MS}ms (ultima lectura y={last})")


def check_contrast_offscreen_scenes(page, theme: str) -> None:
    scenes = page.evaluate(
        """() => Array.from(document.querySelectorAll('[data-scene]')).map((el, i) => ({
          index: i,
          name: el.dataset.scene || String(i),
        }))"""
    )
    for scene in scenes:
        if scene["index"] == 0:
            # Escena 0 (hero) ya vive en el primer viewport y la cubre el
            # barrido inicial en scroll 0 — repetirla aqui solo duplicaria
            # ruido en el reporte.
            continue

        target_y = page.evaluate(
            "(i) => { const el = document.querySelectorAll('[data-scene]')[i]; "
            "return el.getBoundingClientRect().top + window.scrollY; }",
            scene["index"],
        )
        _scroll_to_and_settle(page, target_y)
        screenshot_bytes = page.screenshot(full_page=False)
        check_contrast_wcag(page, f"{theme}·scroll:{scene['name']}", screenshot_bytes)

    # Las aserciones especificas de Vice que corren despues (hero visible a
    # scroll 0, email en el primer viewport) asumen que la pagina sigue en el
    # tope: este barrido debe devolverla ahi, no dejarla en la ultima escena
    # visitada.
    _scroll_to_and_settle(page, 0)


def check_heading_hierarchy(page) -> None:
    """Jerarquia de encabezados: hallazgo de la revision final de rama. `about.ts`
    y `skills.ts` usaban `<p class="hero-kick">` como titulo de seccion en vez
    de un encabezado real, dejando sus `<h3>` colgados de la nada (saltan el
    `<h2>` que deberian tener encima) y a la seccion entera fuera del indice
    de encabezados de cualquier lector de pantalla. `hero.ts`/`contacto.ts`/
    `projectScene.ts` ya usaban `hero-kick` correctamente: un ANTETITULO sobre
    un encabezado real (`<h1>`/`<h2>`), nunca en su lugar.

    Dos aserciones, sobre el DOM real (no una convencion de nombres):
      1. Sin saltos de nivel: recorriendo los encabezados en orden de
         documento, cada nivel nuevo no puede superar en mas de 1 al nivel
         mas profundo visto hasta ese punto (regla estandar de outline HTML).
         Un `<h3>` sin `<h2>` anterior en su rama es un salto de 2 (de nivel 1
         implicito, o del nivel del `<h2>` de la escena previa que no es su
         padre real) y lo cazaria.
      2. Cada `[data-scene]` (una seccion del one-pager) contiene al menos un
         encabezado real (`h1`-`h6`) — no solo un `<p class="hero-kick">` que
         parezca titulo mirandolo, sino un nodo que un lector de pantalla
         cuenta como encabezado."""
    # Solo los encabezados REALMENTE expuestos. El DOM es compartido por los
    # tres temas y cada uno oculta el titular de los otros con `display: none`
    # en un ancestro: ese nodo no esta en el arbol de accesibilidad, no lo lee
    # un lector de pantalla y no lo indexa un crawler. Contarlo daba "2 h1"
    # en Vice/Hyprland/Caelestia por igual — un fallo del instrumento, no del
    # diseno: medido, en los tres temas se pinta exactamente uno.
    # `getClientRects()` vacio distingue `display: none` de "fuera de pantalla"
    # (un encabezado que hay que desplazar para ver SI tiene rects).
    headings = page.evaluate(
        """() => Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6'))
          .filter((h) => h.getClientRects().length > 0)
          .map((h) => ({
            level: Number(h.tagName[1]),
            text: (h.textContent || '').trim().slice(0, 40),
          }))"""
    )
    check(len(headings) > 0, "hay encabezados en el documento")

    max_seen = 0
    jumps: list[str] = []
    for h in headings:
        if h["level"] > max_seen + 1:
            jumps.append(f"h{h['level']} \"{h['text']}\" tras nivel maximo h{max_seen}")
        max_seen = max(max_seen, h["level"])
    check(not jumps, f"sin saltos de nivel en la jerarquia de encabezados ({jumps})")

    h1_count = sum(1 for h in headings if h["level"] == 1)
    check(h1_count == 1, f"hay exactamente un h1 ({h1_count})")

    scenes_without_heading = page.evaluate(
        """() => Array.from(document.querySelectorAll('[data-scene]'))
          .filter((s) => !s.querySelector('h1,h2,h3,h4,h5,h6'))
          .map((s) => s.dataset.scene)"""
    )
    check(not scenes_without_heading,
          f"toda escena [data-scene] tiene un encabezado real dentro ({scenes_without_heading})")


def run(
    theme: str,
    url: str,
    allow_fixture_assets: bool = False,
    allow_gallery_placeholder: bool = False,
    reduced: bool = False,
) -> None:
    global failures
    failures = []

    # Estaticas: no necesitan navegador ni servidor.
    check_docs_references()
    check_spec_plan_consistency()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME, args=ARGS)
        page = None
        try:
            page = browser.new_page(
                viewport=DESKTOP,
                reduced_motion="reduce" if reduced else "no-preference",
            )
            errors: list[str] = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))

            page.goto(f"{url}/?theme={theme}", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3500)

            print(f"[{theme}] desktop")
            check(page.evaluate("document.documentElement.dataset.theme") == theme,
                  "data-theme aplicado")
            check(not errors, f"cero errores de consola ({errors[:2]})")

            shape = page.evaluate("""(() => {
              const w = window;
              return w.__CONTENT_SHAPE__ || null;
            })()""")
            check(shape is not None and shape.get("galleries", 0) >= 2,
                  "content.ts expone galerias en al menos 2 casos de estudio")

            check_heading_hierarchy(page)

            # Defecto de contraste: corre en LOS TRES temas. El bug nacio de
            # asumir que un color que se lee bien en los dos temas oscuros
            # (Vice, Hyprland) se lee igual en Caelestia (claro) — por eso
            # este check no es condicional a un tema, es parte del gate base.
            screenshot_bytes = page.screenshot(full_page=False)
            # Mismo formato de etiqueta que `check_contrast_offscreen_scenes`
            # ("{theme}·scroll:{escena}"): la escena 0 (hero) vive en este
            # primer viewport, sin pasar por el barrido de scroll. Antes esto
            # se etiquetaba solo como `theme`, indistinguible en el reporte
            # de "el tema en general" — necesario para que el suelo de
            # cobertura del hallazgo I-1 identifique la escena exacta que
            # queda sin medir, no solo el tema.
            check_contrast_wcag(page, f"{theme}·scroll:hero", screenshot_bytes)

            # Defecto de contraste bajo el pliegue: corre en LOS TRES temas,
            # igual que el barrido de scroll 0 — ver comentario de
            # `check_contrast_offscreen_scenes`.
            check_contrast_offscreen_scenes(page, theme)

            # Placeholder de galeria (defecto 3-bis): las capturas de la
            # Editorial de Obra cargan y no son los rellenos honestos.
            if not allow_gallery_placeholder:
                check_gallery_placeholder(page)
                check_gallery_placeholder_hashes()

            # Creditos: la bandeja de Caelestia (`caelestiaCreditosBandeja.ts`),
            # 23 piezas pulsables que marcan con `aria-pressed` la elegida.
            page.click('[data-cae-ws="creditos"]')
            page.wait_for_timeout(1500)
            credits = page.evaluate("""(() => {
              const piezas = document.querySelectorAll('[data-scene="credits"] button.cae-cred-pieza');
              if (!piezas.length) return null;
              const ultima = piezas[piezas.length - 1];
              ultima.click();
              return {
                piezas: piezas.length,
                marcada: ultima.getAttribute('aria-pressed') === 'true',
                focusable: piezas[0].tabIndex >= 0,
              };
            })()""")
            check(credits is not None and credits["piezas"] >= 20, "la bandeja de creditos tiene sus piezas")
            check(credits is not None and credits["marcada"], "pulsar una pieza la marca con aria-pressed")
            check(credits is not None and credits["focusable"], "las piezas de creditos son enfocables")

            # Obra: la Editorial (`caelestiaObraEditorial.ts`), una tarjeta por
            # caso de estudio de `content.ts` y un cajon con su ficha.
            obra = page.evaluate("""(() => ({
              tarjetas: document.querySelectorAll('#obra .cae-obra-card').length,
              cajon: !!document.querySelector('#obra .cae-obra-drawer-title'),
            }))()""")
            check(obra["tarjetas"] >= 2, f"la Editorial de Obra tiene tarjetas ({obra['tarjetas']})")
            check(obra["cajon"], "la Editorial de Obra tiene cajon con la ficha del proyecto")

            check(page.evaluate("() => !!document.querySelector('[data-scene=\"contacto\"]')"), "existe la seccion de contacto")

            contact_links = page.evaluate("""(() => {
              const scene = document.querySelector('[data-scene="contacto"]');
              if (!scene) return null;
              const mail = scene.querySelector('a[href^="mailto:"]');
              const external = Array.from(scene.querySelectorAll('a[target="_blank"]'))[0] ?? null;
              return {
                mail: !!mail,
                externalRel: external ? external.getAttribute('rel') : null,
              };
            })()""")
            check(contact_links is not None and contact_links["mail"],
                  "el email de contacto es un enlace mailto accionable")
            check(
                contact_links is not None and contact_links["externalRel"] == "noopener noreferrer",
                "el enlace externo de contacto lleva rel=noopener noreferrer "
                f"(rel={contact_links['externalRel'] if contact_links else None})",
            )

            # Degradacion con prefers-reduced-motion (`--reduced`): obra y
            # creditos son contenido, no decoracion; apagarlos dejaria al
            # visitante sin informacion.
            if reduced:
                degraded = page.evaluate("""(() => ({
                  obraUsable: document.querySelectorAll('#obra .cae-obra-card').length > 0,
                  creditsUsable: document.querySelectorAll('button.cae-cred-pieza').length > 0,
                }))()""")
                check(degraded["obraUsable"], "la obra sigue disponible")
                check(degraded["creditsUsable"], "los creditos siguen disponibles")
        finally:
            if page:
                page.close()
            browser.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="caelestia", choices=["caelestia"],
                    help="Unico tema que queda (se conserva el flag por compatibilidad).")
    ap.add_argument("--url", default="http://127.0.0.1:5173")
    ap.add_argument(
        "--allow-fixture-assets",
        action="store_true",
        help="Sin efecto: el gate de fixtures de video de Vice se retiro con el tema. "
        "Se acepta para no romper las invocaciones existentes.",
    )
    ap.add_argument(
        "--allow-gallery-placeholder",
        action="store_true",
        help="Silencia el gate del placeholder 'Imagen pendiente' de la galeria (defecto 3-bis, "
        "Task 11) mientras dure el desarrollo. NO esta activo por defecto: hay que pasarlo. "
        "Silencia la CATEGORIA entera; para el uso diario, la linea base. El gate final debe "
        "correr sin este flag.",
    )
    ap.add_argument(
        "--reduced",
        action="store_true",
        help="Abre la pagina con prefers-reduced-motion:reduce y comprueba que galeria y "
        "creditos siguen operativos.",
    )
    ap.add_argument(
        "--update-baseline",
        action="store_true",
        help="Reescribe scripts/verify-baseline.json con los fallos de esta ejecucion. "
        "Usalo solo cuando el cambio de la linea base sea deliberado y este justificado.",
    )
    ap.add_argument(
        "--no-baseline",
        action="store_true",
        help="Ignora la linea base: cualquier fallo cuenta. Es el modo del gate final, "
        "cuando ya no queden fixtures pendientes.",
    )
    args = ap.parse_args()
    run(
        args.theme,
        args.url,
        allow_fixture_assets=args.allow_fixture_assets,
        allow_gallery_placeholder=args.allow_gallery_placeholder,
        reduced=args.reduced,
    )
    print()

    if args.update_baseline:
        escribir_baseline(failures)
        print(f"Linea base reescrita con {len(failures)} fallos -> {BASELINE_PATH.name}")
        return 0
    if args.no_baseline:
        if failures:
            print(f"FALLOS: {len(failures)}")
            return 1
        print("TODO OK")
        return 0
    return comparar_con_baseline(failures)


if __name__ == "__main__":
    sys.exit(main())
