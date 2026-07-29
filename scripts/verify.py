"""Arnes de verificacion visual. Cada tarea del plan anade aserciones aqui.

Uso: python3 scripts/verify.py [--theme vice] [--url http://127.0.0.1:5173]
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

# Hashes exactos de los fixtures sinteticos generados con ffmpeg en la Task 3
# (poster de color solido + barras de test SMPTE). Un hash exacto es la unica
# forma fiable de identificarlos: el tamano o el nombre de archivo sobreviven
# a un reemplazo; el contenido (sha256) no. En cuanto la Task 11 suba los
# assets reales, el hash deja de coincidir y esta asercion pasa a estar en
# verde sola, sin tocar el arnes otra vez.
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_HASHES = {
    "public/media/vice-poster.webp": "32ec2c6747aee5394913209ae7698a8c6a7ccdc9bbce9c03745a7b93be1c0be5",
    "public/media/vice-hero.webm": "09f7c04887ec97edf76ca664227797bd92ec3f6c797765daffdf7645165bee1c",
    "public/media/vice-hero.mp4": "fbe241445d4b68a78f20a5d5847b310cfd72e9ed526edad5c960ce9a64934e8a",
}

# Hashes exactos de los rellenos honestos generados con ffmpeg para la
# galeria de "Obra" (fondo solido + "CAPTURA PENDIENTE" + pie de foto — nunca
# una captura simulada de la app real). Mismo patron que FIXTURE_HASHES: el
# nombre de archivo y las dimensiones sobreviven a que el usuario suba la
# captura real; el contenido (sha256) no. En cuanto una ruta se sustituye por
# la captura definitiva, esta comprobacion deja de marcarla sola, sin tocar
# el arnes otra vez.
GALLERY_PLACEHOLDER_HASHES = {
    "public/media/obra/echoplan-tablero.webp": "768b4bd5cc8edf81a170ec9d2a9d01cd1ce535c84230b09b5b8c7c83bd9a3229",
    "public/media/obra/echoplan-aprobaciones.webp": "aca10c4dd5954df32187c60ff9df667dcb8283648a0dd50700c20109f33f8087",
    "public/media/obra/hyprfinance-resumen.webp": "c15b76977f515c9e348b225dcbf80f8e67923b719113c21a3658ac4b062112c4",
    "public/media/obra/hyprfinance-movimientos.webp": "289a2c793195c3ff4cfda2a3fa7cde2b1be142e658a8de5d6b6002cb7dfa5396",
    "public/media/obra/ciberseg-panel.webp": "2323ea1199979d4a7a866d056b54f4bbe3f4e9ab179f67e727a142c406871355",
    "public/media/obra/ciberseg-vulnerabilidades.webp": "bf04d000599c121160668c20f05c3d54b92d6fcb999aa2c6eb808642d51b6333",
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


def check_fixture_assets() -> None:
    """Defecto 3: falla mientras public/media/ siga sirviendo los fixtures
    sinteticos de la Task 3 (poster solido + barras SMPTE). Gate obligatorio
    para la Task 11 — no un checklist opcional."""
    for rel_path, fixture_hash in FIXTURE_HASHES.items():
        full_path = REPO_ROOT / rel_path
        is_fixture = full_path.exists() and sha256_of(full_path) == fixture_hash
        check(not is_fixture, f"{rel_path} no es el fixture sintetico de la Task 3")


GALLERY_SETTLE_TIMEOUT_MS = 4000
GALLERY_SETTLE_POLL_MS = 200


def check_gallery_placeholder(page) -> None:
    """Las imagenes de la galeria (`/media/obra/*.webp`) todavia no existen:
    llegan con las capturas reales en la Task 11. Mientras tanto cada
    `<img>` de `gallery.ts` falla su carga y `.gallery-fallback` ("Imagen
    pendiente") queda visible en su lugar — un fallback honesto para el
    usuario, pero texto placeholder visible en una seccion publicada, que la
    norma del proyecto prohibe. Mismo patron que `check_fixture_assets`: este
    gate falla mientras el placeholder siga presente, para que sustituirlo
    por los assets reales sea obligatorio en la Task 11, no un checklist
    opcional. Silenciable con `--allow-gallery-placeholder` mientras dure el
    desarrollo (activo por defecto, igual que `--allow-fixture-assets`).

    Las imagenes llevan `loading="lazy"` (no empiezan a cargar hasta que el
    scroll las acerca al viewport) y el intento de red — aunque sea un 404
    local — tarda un instante en resolver. Por eso se espera activamente
    (poll de `img.complete`, que el navegador marca `true` tanto en `load`
    como en `error`) antes de leer `[data-broken]`, el marcador que
    `gallery.ts` fija en el listener de `error` de cada imagen."""
    elapsed = 0
    while elapsed < GALLERY_SETTLE_TIMEOUT_MS:
        pending = page.evaluate(
            "() => Array.from(document.querySelectorAll('[data-gallery-track] .gallery-img'))"
            ".filter((img) => !img.complete).length"
        )
        if pending == 0:
            break
        page.wait_for_timeout(GALLERY_SETTLE_POLL_MS)
        elapsed += GALLERY_SETTLE_POLL_MS
    else:
        print(f"  NOTA galeria: alguna imagen no resolvio su carga en {GALLERY_SETTLE_TIMEOUT_MS}ms")
    # Margen extra: `data-broken` lo fija un listener de `error` que puede
    # correr un tick despues de que `img.complete` ya sea `true`.
    page.wait_for_timeout(200)

    total = page.evaluate(
        "() => document.querySelectorAll('[data-gallery-track] .gallery-img').length"
    )
    broken = page.evaluate(
        "() => document.querySelectorAll('[data-gallery-track] [data-broken]').length"
    )
    check(total > 0, "la galeria tiene imagenes que verificar")
    check(
        broken == 0,
        f"galeria: ninguna imagen cae al fallback de placeholder "
        f'("Imagen pendiente" visible en {broken}/{total})',
    )


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
        """(() => {
      const out = [];
      const nodes = document.querySelectorAll('body *');
      for (const el of nodes) {
        if (el.children.length > 0) continue; // solo hojas
        const text = (el.textContent || '').trim();
        if (!text) continue;
        if (el.closest('[data-decorative]')) continue; // decorativo, exento por WCAG 1.4.3
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
        out.push({
          tag: el.tagName.toLowerCase(),
          text: text.slice(0, 40),
          color: pintaSoloElTrazo ? strokeC : style.color,
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
    headings = page.evaluate(
        """() => Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).map((h) => ({
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


def check_gallery_progress_bar(browser, url: str, theme: str) -> None:
    """Hallazgo I-4 de la revision final: la barra de progreso de la galeria
    (`gallery.ts`) mentia en el primer pintado en movil — se pintaba llena al
    100% aunque hubiera carril oculto por arrastrar. Causa real: `updateBar()`
    se llamaba de forma sincrona en la construccion del componente, con
    `track` todavia desconectado del documento (`createGallery` solo devuelve
    el nodo; quien la llama lo apendiza despues). `scrollWidth`/`clientWidth`
    valian 0 en ese instante, la division daba `NaN`, `Math.max(14, NaN)` es
    tambien `NaN`, y `style.width = "NaN%"` es un valor invalido que el
    navegador descarta — el inline queda vacio y el `<i>` hereda el 100% de
    `.gallery-bar` (`display: block`, sin ancho propio). Solo lo corregia el
    listener de `scroll` del propio carril, que no dispara hasta que alguien
    ya arrastro: para entonces el visitante ya vio la barra mintiendo.

    Contexto nuevo con viewport movil (mismo motivo que `galleries_mobile` mas
    abajo: el ancho minimo de cada pieza garantiza desborde real con 2+ piezas)
    para medir el estado justo tras el primer pintado SIN arrastrar ni
    scrollear el carril — asi se prueba lo que ve el visitante antes de tocar
    nada, no un estado ya corregido por una interaccion previa del arnes."""
    context = browser.new_context(viewport=MOBILE)
    try:
        page = context.new_page()
        page.goto(f"{url}/?theme={theme}", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1200)
        data = page.evaluate("""() => {
          const out = [];
          for (const gallery of document.querySelectorAll('[data-gallery]')) {
            const track = gallery.querySelector('[data-gallery-track]');
            const bar = gallery.querySelector('[data-gallery-bar]');
            const indicator = bar ? bar.firstElementChild : null;
            if (!track || !bar || !indicator) continue;
            if (track.children.length < 2) continue; // sin desborde posible
            const scrollable = track.scrollWidth > track.clientWidth + 10;
            if (!scrollable) continue;
            const barWidth = bar.getBoundingClientRect().width;
            const indicatorWidth = indicator.getBoundingClientRect().width;
            out.push({
              styleWidth: indicator.style.width,
              ratio: barWidth > 0 ? (indicatorWidth / barWidth) * 100 : null,
            });
          }
          return out;
        }""")
        check(
            len(data) >= 1,
            "hay al menos una galeria desplazable en movil para medir la barra en el primer pintado",
        )
        for i, g in enumerate(data):
            check(
                g["styleWidth"] != "" and "NaN" not in g["styleWidth"],
                f"galeria #{i} ({theme}): la barra tiene un ancho valido en el primer pintado "
                f"(style.width={g['styleWidth']!r})",
            )
            ratio = g["ratio"]
            check(
                ratio is not None and ratio < 95,
                f"galeria #{i} ({theme}): la barra no se pinta llena en el primer pintado pese a "
                f"haber carril oculto por arrastrar (ratio medido={ratio})",
            )
    finally:
        context.close()


def check_theme_identity(page, theme: str) -> None:
    """Hallazgo I-5 de la revision final: el gate solo protegia Vice de
    verdad (41 aserciones no-contraste) frente a Hyprland/Caelestia (8 cada
    uno, solo lo generico: creditos, galeria...). El modo de fallo real que ya
    ha pasado tres veces en este proyecto es "una tarea que reescribe una
    seccion COMPARTIDA (`style.css`/`themes.css`) rompe la identidad de otro
    tema" — y el gate de contraste no lo caza: el caso canonico (borrar
    `.hero-surface` en Caelestia) deja el texto igual de legible, lo roto es
    la ESTRUCTURA (tarjeta Material You -> texto suelto sobre el degradado),
    no el contraste.

    Se mide el pixel EFECTIVO via `getComputedStyle`, no la regla CSS
    declarada: `getComputedStyle` ya devuelve el valor resuelto tras cascada
    (a diferencia de leer el `cssText` de una regla, que solo demuestra que
    la regla EXISTE en la hoja, no que gane la especificidad real ni que siga
    aplicando sobre el elemento correcto).

    Tres marcadores de identidad, elegidos porque cada uno protege un bloque
    compartido distinto de `themes.css`/`style.css`:
      1. Caelestia: `.hero-surface`/`.scene-surface` deben tener fondo
         tonal solido, blur y sombra reales — la tarjeta Material You que
         distingue a Caelestia de "texto suelto sobre un degradado". Sin
         esto Caelestia deja de leerse como Material You.
      2. Hyprland/Caelestia comparten el re-skin de creditos en pildoras
         (`flex-direction: row`, `.credit-role` oculto) — la alternativa al
         rodillo vertical de cine de Vice. Si se borra ese bloque, ambos
         temas caen silenciosamente al layout de Vice sin que ningun otro
         gate lo note (el gate de creditos existente solo comprueba
         interaccion/cuenta, no layout).
      3. Hyprland NO debe heredar la tarjeta de Caelestia — la marca no es
         "sin fondo" (Vice tambien anadio su propio scrim de ink para el
         hallazgo I-1, asi que un fondo no nulo ya no basta para distinguir),
         sino el borde + sombra que son exclusivos del recibo Material You de
         Caelestia (`border: 1px solid ...` + `box-shadow` real; el scrim de
         Vice no lleva ninguno de los dos). Protege contra el error inverso
         al (1): ampliar el selector de Caelestia para que tambien alcance a
         Hyprland (o a Vice)."""
    hero_surface = page.evaluate("""(() => {
      const el = document.querySelector('.hero-surface');
      if (!el) return null;
      const s = getComputedStyle(el);
      return {
        background: s.backgroundColor,
        backdropFilter: s.backdropFilter,
        boxShadow: s.boxShadow,
        borderWidth: s.borderTopWidth,
      };
    })()""")
    scene_surface = page.evaluate("""(() => {
      const el = document.querySelector('.about-stats');
      if (!el) return null;
      const s = getComputedStyle(el);
      return { background: s.backgroundColor, backdropFilter: s.backdropFilter };
    })()""")

    def _is_transparent(css_color: str) -> bool:
        return css_color in ("rgba(0, 0, 0, 0)", "transparent", "") or css_color is None

    if theme == "caelestia":
        check(
            hero_surface is not None and not _is_transparent(hero_surface["background"]),
            f"Caelestia: .hero-surface tiene fondo tonal solido (no transparente) "
            f"(background={hero_surface['background'] if hero_surface else None})",
        )
        check(
            hero_surface is not None and "blur" in hero_surface["backdropFilter"],
            f"Caelestia: .hero-surface aplica backdrop-filter con blur real "
            f"(backdropFilter={hero_surface['backdropFilter'] if hero_surface else None})",
        )
        check(
            hero_surface is not None and hero_surface["boxShadow"] != "none",
            f"Caelestia: .hero-surface proyecta sombra real "
            f"(boxShadow={hero_surface['boxShadow'] if hero_surface else None})",
        )
        check(
            scene_surface is not None and not _is_transparent(scene_surface["background"]),
            f"Caelestia: .scene-surface (.about-stats) tiene fondo tonal solido "
            f"(background={scene_surface['background'] if scene_surface else None})",
        )
    else:
        no_caelestia_card = (
            hero_surface is not None
            and hero_surface["boxShadow"] == "none"
            and hero_surface["borderWidth"] == "0px"
        )
        check(
            no_caelestia_card,
            f"{theme}: .hero-surface no hereda la tarjeta Material You de Caelestia "
            "(sin borde, sin sombra propia) "
            f"(boxShadow={hero_surface['boxShadow'] if hero_surface else None}, "
            f"borderWidth={hero_surface['borderWidth'] if hero_surface else None})",
        )

    if theme in ("hyprland", "caelestia"):
        credits_layout = page.evaluate("""(() => {
          const list = document.querySelector('.credits-list');
          const role = document.querySelector('.credit-role');
          if (!list) return null;
          const s = getComputedStyle(list);
          return {
            flexDirection: s.flexDirection,
            roleDisplay: role ? getComputedStyle(role).display : null,
          };
        })()""")
        check(
            credits_layout is not None and credits_layout["flexDirection"] == "row",
            f"{theme}: .credits-list se re-skinea en pildoras horizontales "
            f"(flexDirection={credits_layout['flexDirection'] if credits_layout else None})",
        )
        check(
            credits_layout is not None and credits_layout["roleDisplay"] == "none",
            f"{theme}: el rol se oculta en formato pildora "
            f"(roleDisplay={credits_layout['roleDisplay'] if credits_layout else None})",
        )


def check_reduced_motion_chrome(browser, url: str, theme: str) -> None:
    """El cromo de cine (letterbox + barra de orientacion) es decoracion pura
    de Vice: con `prefers-reduced-motion` no debe aparecer. Sin este check,
    quitar el `@media (prefers-reduced-motion: reduce) { .cinema-chrome {
    display: none !important; } }` de `style.css` pasaria desapercibido: la
    coreografia que anima letterbox/atenuador ya no corre bajo motion reducido
    (`initScrollReveal` corta antes de cargar GSAP), asi que el letterbox
    seguiria en su estado de reposo (0 altura) igualmente — pero la barra de
    orientacion es texto ESTATICO sin animacion propia, y sin el gate CSS
    quedaria visible para siempre. Solo tiene sentido para Vice: en los otros
    dos temas el cromo ya esta oculto sin depender de `prefers-reduced-motion`.
    """
    context = browser.new_context(viewport=DESKTOP, reduced_motion="reduce")
    try:
        page = context.new_page()
        page.goto(f"{url}/?theme={theme}", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(1500)
        visible = page.evaluate(
            "() => { const c = document.querySelector('.cinema-chrome');"
            " return c ? getComputedStyle(c).display !== 'none' : null; }"
        )
        check(
            visible is False,
            f"el cromo de cine no aparece con prefers-reduced-motion ({theme}, display visible={visible})",
        )
    finally:
        context.close()


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

            # Placeholder de galeria (defecto 3-bis): la escena "obra" es
            # theme-agnostic (`createProjectScene` la monta igual en los tres
            # temas), asi que corre en los tres, igual que el resto de gates
            # base. El barrido de arriba ya hizo scroll por cada escena, asi
            # que las imagenes `loading="lazy"` de la galeria ya tuvieron
            # ocasion de intentar cargar.
            if not allow_gallery_placeholder:
                check_gallery_placeholder(page)
                check_gallery_placeholder_hashes()

            # Hallazgo I-4: la barra de progreso de la galeria en el primer
            # pintado movil, sin interaccion previa. Contexto/pagina propios
            # (ver comentario de la funcion) — no reutiliza `page` porque
            # necesita medir ANTES de que ningun otro gate scrollee nada.
            check_gallery_progress_bar(browser, url, theme)

            # Task 9: creditos interactivos ("Con que construyo"). Corre en
            # LOS TRES temas, no solo Vice: `createCredits` monta el mismo
            # DOM en los tres (un solo componente, presentacion por CSS via
            # `[data-theme]`), asi que la interaccion real (el panel cambia
            # al pasar el raton o el foco por una fila) tiene que sobrevivir
            # al re-skinning de Hyprland/Caelestia en pildoras, no solo verse
            # bien en Vice como creditos de cine.
            credits = page.evaluate("""(() => {
              const rows = document.querySelectorAll('[data-credit]');
              if (!rows.length) return null;
              const panel = document.querySelector('[data-credit-panel]');
              const before = panel ? panel.textContent.trim() : "";
              rows[rows.length - 1].dispatchEvent(new MouseEvent('mouseenter', {bubbles:true}));
              const after = panel ? panel.textContent.trim() : "";
              return {
                rows: rows.length,
                hasPanel: !!panel,
                hasIcon: !!(panel && panel.querySelector('svg')),
                changed: before !== after,
                focusable: rows[0].tabIndex >= 0,
              };
            })()""")
            check(credits is not None and credits["rows"] >= 6, "hay filas de creditos")
            check(credits is not None and credits["hasPanel"], "hay panel de detalle")
            check(credits is not None and credits["hasIcon"], "el panel muestra icono")
            check(credits is not None and credits["changed"], "el panel cambia al interactuar")
            check(credits is not None and credits["focusable"], "los creditos son enfocables")

            # Hallazgo I-5: cobertura estructural de identidad para los dos
            # temas aprobados (Hyprland/Caelestia), no solo contraste — ver
            # comentario de `check_theme_identity`.
            check_theme_identity(page, theme)

            if theme == "vice":
                # El backdrop de Vice ya no es video+poster: es la bruma
                # generativa de `src/backgrounds/viceHaze.ts`, un canvas WebGL
                # como el de los otros dos temas. El cambio fue deliberado —
                # el video servia el fixture SMPTE, cuyas franjas de color
                # primario obligaban a tapar hero y contacto con un scrim casi
                # opaco para poder medir contraste. Con la bruma (brillo
                # acotado en el propio shader) el scrim desaparecio; lo que
                # este gate vigila ahora es que el canvas exista y pinte.
                backdrop = page.evaluate("""(() => {
                  const host = document.querySelector('.bg-theme');
                  if (!host) return null;
                  const canvas = host.querySelector('canvas');
                  return {
                    canvas: !!canvas,
                    painted: canvas ? canvas.width > 0 && canvas.height > 0 : false,
                    legacyMedia: !!host.querySelector('img, video'),
                  };
                })()""")
                check(backdrop is not None and backdrop["canvas"], "hay canvas de fondo en el backdrop")
                check(backdrop is not None and backdrop["painted"], "el canvas del backdrop tiene tamano")
                # Con reduced-motion el shader pinta UN fotograma estatico y no
                # arranca el RAF (`mountShaderBackground`), asi que el canvas
                # sigue presente en los dos modos: no hay ramificacion aqui.
                check(
                    backdrop is not None and not backdrop["legacyMedia"],
                    "el backdrop no reintroduce el video/poster de fixture",
                )

                fonts = page.evaluate("""(() => {
                  const root = getComputedStyle(document.documentElement);
                  const registry = Array.from(document.fonts);
                  const isLoaded = (name) => registry.some(
                    (f) => f.family.replace(/["']/g, '').includes(name) && f.status === 'loaded'
                  );
                  return {
                    display: root.getPropertyValue('--font-display').trim(),
                    body: root.getPropertyValue('--font-body').trim(),
                    accent: root.getPropertyValue('--color-accent').trim(),
                    passionOneLoaded: isLoaded('Passion One'),
                    manropeLoaded: isLoaded('Manrope'),
                  };
                })()""")
                check("Passion One" in fonts["display"], "display es Passion One")
                check("Manrope" in fonts["body"], "cuerpo es Manrope")
                check(fonts["accent"].lower() == "#ffd166", "acento es ambar")
                check("mono" not in fonts["body"].lower(), "Vice no usa monoespaciada (token --font-body)")
                check(fonts["passionOneLoaded"], "Passion One presente y cargada en document.fonts")
                check(fonts["manropeLoaded"], "Manrope presente y cargada en document.fonts")

                # Defecto 2: el token de --font-body nunca fue monoespaciado, asi
                # que la asercion de arriba pasa siempre y no habria cazado el
                # bug real (clase `font-mono` a pelo + fallback del sistema).
                # Esta mide la fuente EFECTIVAMENTE renderizada: getComputedStyle
                # devuelve el valor DECLARADO (la cadena de fallback completa),
                # no cual de esos nombres gano la resolucion real del navegador.
                # Por eso se renderiza en un <canvas> y se compara el ancho de
                # una "i" contra una "W": en una fuente monoespaciada (la que
                # cae el navegador si la webfont no cargo) todos los caracteres
                # miden lo mismo; en una proporcional (Manrope) no.
                mono_offenders = page.evaluate("""(() => {
                  function isMonospace(font) {
                    if (!font) return false;
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    ctx.font = font;
                    const narrow = ctx.measureText('iiiiiiiiiiiiiiiiiiii').width;
                    const wide = ctx.measureText('WWWWWWWWWWWWWWWWWWWW').width;
                    return wide > 0 && Math.abs(narrow - wide) < 0.1;
                  }
                  const offenders = [];
                  for (const el of document.querySelectorAll('body *')) {
                    if (el.children.length > 0) continue; // solo elementos hoja
                    const text = (el.textContent || '').trim();
                    if (!text) continue;
                    if (el.offsetParent === null) continue; // no visible
                    const style = getComputedStyle(el);
                    if (isMonospace(style.font)) {
                      offenders.push(`${el.tagName.toLowerCase()}:\"${text.slice(0, 30)}\"`);
                    }
                  }
                  return offenders;
                })()""")
                check(len(mono_offenders) == 0,
                      f"ningun texto visible resuelve a fuente monoespaciada real ({mono_offenders[:3]})")

                # Defecto 1: [data-hero-name] debe verse a scroll 0. La condicion
                # de carrera entre la CSS de `.js-intro` y el tween con scrub de
                # wireHeroZoom lo deja en opacity:0 para siempre si el orden de
                # cableado no es deterministico.
                hero_name_opacity = page.evaluate("""(() => {
                  const el = document.querySelector('[data-hero-name]');
                  return el ? parseFloat(getComputedStyle(el).opacity) : null;
                })()""")
                check(hero_name_opacity is not None and hero_name_opacity > 0.9,
                      f"[data-hero-name] visible a scroll 0 (opacity={hero_name_opacity})")

                # Task 6: el gesto de titulo (Task 6) parte el nombre en spans por
                # caracter para el zoom con scrub, y el hero deja email visible en
                # el primer viewport (suelo de conversion, sin depender de scroll).
                hero = page.evaluate("""(() => {
                  const s = document.querySelector('[data-scene="hero"]');
                  if (!s) return null;
                  const name = s.querySelector('[data-hero-name]');
                  const mail = document.querySelector('a[href^="mailto:"]');
                  const r = mail ? mail.getBoundingClientRect() : null;
                  return {
                    name: !!name,
                    chars: name ? name.querySelectorAll('span span').length : 0,
                    mailVisible: !!(r && r.top >= 0 && r.top < window.innerHeight),
                  };
                })()""")
                check(hero is not None and hero["name"], "el hero tiene nombre marcado")
                # `splitChars` (vice.choreography.ts) solo corre dentro de la
                # coreografia de GSAP, que `initScrollReveal` (reveal.ts) NO
                # carga con reduced-motion (`if (prefersReducedMotion) return;`
                # antes del import de gsap). Sin coreografia el nombre se queda
                # como texto plano, legible igual (ver "el nombre es legible
                # con reduced-motion" mas abajo) — partirlo en spans es un
                # requisito del gesto de zoom, no de la legibilidad.
                if not reduced:
                    check(hero is not None and hero["chars"] > 5, "el nombre se parte en caracteres")
                check(hero is not None and hero["mailVisible"],
                      "el email es visible en el primer viewport")

                # Task 7: "Quien es" deja de tener el lado derecho vacio — ficha
                # de reparto (avatar + datos), cuatro cifras y trayectoria. Sin
                # chips de tecnologia: duplicarian los creditos de obra.
                about = page.evaluate("""(() => {
                  const s = document.querySelector('[data-scene="about"]');
                  if (!s) return null;
                  return {
                    card: !!s.querySelector('[data-card]'),
                    avatar: !!s.querySelector('[data-card] img'),
                    stats: s.querySelectorAll('[data-stats] > *').length,
                    track: !!s.querySelector('[data-track]'),
                    chips: s.querySelectorAll('[data-tech-chip]').length,
                  };
                })()""")
                check(about is not None and about["card"], "hay ficha de reparto")
                check(about is not None and about["avatar"], "la ficha lleva avatar")
                check(about is not None and about["stats"] == 4, "hay cuatro cifras")
                check(about is not None and about["track"], "hay trayectoria")
                check(about is not None and about["chips"] == 0,
                      "sin chips de tecnologia (duplicarian los creditos)")

                # Task 8: "Obra" gana galeria horizontal arrastrable (collage)
                # y fila de metadatos.
                #
                # Lo que importa aqui es el COMPONENTE, no el contenido: que
                # una galeria con pocas piezas quepa entera a 1440px sin
                # desbordar es correcto (nada que arrastrar), no un fallo. La
                # version anterior de este check media `scrollWidth >
                # clientWidth` de la PRIMERA galeria del DOM a 1440px, que es
                # justo lo que rompio cuando el primer proyecto de
                # content.ts paso de 3 a 2 imagenes: 2 piezas de 300px caben
                # en el ancho de columna a esa resolucion, asi que dejaron de
                # desbordar aunque el carril siga funcionando perfectamente.
                #
                # Fix: se mide en un viewport movil (390px), donde el ancho
                # minimo de cada pieza (`min(300px, 74vw)` en style.css)
                # garantiza que 2 o mas piezas desbordan el carril sea cual
                # sea el recuento exacto — no hace falta adivinar cuantas
                # imagenes tiene cada proyecto. Y se evaluan TODAS las
                # galerias del DOM (`querySelectorAll`), no solo la primera:
                # una galeria de una sola pieza (el editor de texto) puede
                # caber sin desbordar y eso tambien es correcto, asi que se
                # excluye de la comprobacion de desborde en vez de forzarla a
                # pasar con un margen inventado.
                page.evaluate("window.scrollTo(0, 0)")
                page.set_viewport_size(MOBILE)
                page.wait_for_timeout(300)
                galleries_mobile = page.evaluate("""(() => {
                  const tracks = Array.from(document.querySelectorAll('[data-gallery-track]'));
                  return tracks
                    .filter((t) => t.children.length >= 2)
                    .map((t) => ({
                      items: t.children.length,
                      scrollable: t.scrollWidth > t.clientWidth + 10,
                    }));
                })()""")
                page.set_viewport_size(DESKTOP)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(300)

                check(len(galleries_mobile) >= 1,
                      "hay al menos una galeria con 2+ piezas que comprobar")
                non_scrollable = [g for g in galleries_mobile if not g["scrollable"]]
                check(
                    len(galleries_mobile) >= 1 and not non_scrollable,
                    "todas las galerias con 2+ piezas son desplazables en horizontal "
                    f"en movil ({non_scrollable})",
                )

                track_count = page.evaluate(
                    "() => document.querySelectorAll('[data-gallery-track]').length"
                )
                check(track_count >= 2, "hay galerias de proyecto en la escena de obra")

                # Los metadatos de la cartela (Rol/Periodo/Stack/Estado) son
                # independientes de que exista o no el carril de galeria — un
                # proyecto sin piezas (`project.gallery.length === 0`) sigue
                # teniendo su `[data-meta]`. Antes esta comprobacion vivia
                # dentro del mismo `gal` que la galeria, asi que si el carril
                # faltaba (`gal === null`) esta aserción fallaba tambien,
                # aunque los metadatos estuvieran perfectamente presentes:
                # dos cosas distintas acopladas a una sola condicion.
                metas = page.evaluate(
                    '() => document.querySelectorAll(\'[data-scene="obra"] [data-meta]\').length'
                )
                check(metas >= 1, "las obras tienen fila de metadatos")

                # Task 10: contacto (cierre del portfolio), letterbox y barra de
                # orientacion. `cinemaChrome.ts` monta el mismo DOM en los tres
                # temas; el arnes solo lo instrumenta aqui porque el gate de
                # visibilidad (CSS) y la coreografia que lo anima son de Vice.
                chrome = page.evaluate("""(() => ({
                  contacto: !!document.querySelector('[data-scene="contacto"]'),
                  letterbox: document.querySelectorAll('[data-letterbox]').length,
                  rail: !!document.querySelector('[data-rail]'),
                }))()""")
                check(chrome["contacto"], "existe la seccion de contacto")
                check(chrome["letterbox"] == 2, "hay dos barras de letterbox")
                check(chrome["rail"], "existe la barra de orientacion")

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

                # Solo hero y contacto van a plena luz; las intermedias se atenuan.
                # Causa real vigilada: la coreografia `cinemaChrome` de
                # `vice.choreography.ts` sube `[data-dim]` a 0.62 fuera de esas dos
                # escenas — no un valor de opacidad puesto a mano en el DOM.
                letterbox_hero = page.evaluate(
                    "parseFloat(getComputedStyle(document.querySelector('[data-letterbox]')).height)"
                )
                check(letterbox_hero < 2, f"el letterbox no aparece en el hero ({letterbox_hero}px)")

                # `_scroll_to_and_settle` y no `scrollTo` crudo + espera fija: es
                # justo la desincronizacion que documenta el docstring del
                # helper. Aqui se llega despues de una tanda de barridos con
                # rueda simulada, asi que el target interno de Lenis esta
                # caliente; un `scrollTo` mueve el scroll nativo y NO ese
                # target, y 1200ms fijos no bastan para el viaje. Se vio al
                # crecer "about" a escena de dos pantallas (rediseno de
                # afirmacion y prueba): el documento paso de ~12000 a 12370px,
                # el salto al 45% crecio con el, y las dos aserciones de cromo
                # empezaron a medir con Lenis todavia a mitad de camino
                # (atenuador en 0.0968 de un reposo de 0.62). El cromo estaba
                # bien —verificado a 0.35, 0.45, 0.55, 0.65 y 0.75 del
                # documento, siempre 0.62 y 58.5px—; lo que fallaba era la
                # medicion. Latente desde antes: solo hacia falta un documento
                # algo mas largo para cruzar el limite.
                _scroll_to_and_settle(page, page.evaluate("document.body.scrollHeight") * 0.45)
                dimmed = page.evaluate(
                    "parseFloat(getComputedStyle(document.querySelector('[data-dim]')).opacity)"
                )
                # El atenuador y el letterbox durante la obra los cablea la
                # coreografia `cinemaChrome` via ScrollTrigger, que no corre
                # con reduced-motion (misma causa que "el nombre se parte en
                # caracteres" arriba): [data-dim] y [data-letterbox] se quedan
                # en su reposo (0) todo el scroll — degradacion correcta, no
                # un defecto. Silenciado con `if not reduced`, no un exento
                # generico: `check_reduced_motion_chrome` mas abajo SI exige
                # que el cromo no aparezca con reduced-motion.
                if not reduced:
                    check(dimmed > 0.3, f"el fondo se atenua en secciones interiores ({dimmed})")

                # El letterbox solo entra durante la obra: en esta misma posicion de
                # scroll (~45%, dentro de una escena "obra" con 4 casos de estudio)
                # debe estar desplegado.
                letterbox_obra = page.evaluate(
                    "parseFloat(getComputedStyle(document.querySelector('[data-letterbox]')).height)"
                )
                if not reduced:
                    check(letterbox_obra > 20, f"el letterbox se despliega durante la obra ({letterbox_obra}px)")

                _scroll_to_and_settle(page, page.evaluate("document.body.scrollHeight"))
                dimmed_end = page.evaluate(
                    "parseFloat(getComputedStyle(document.querySelector('[data-dim]')).opacity)"
                )
                check(dimmed_end < 0.1, f"el fondo vuelve a plena luz en contacto ({dimmed_end})")
                _scroll_to_and_settle(page, 0)

                check_reduced_motion_chrome(browser, url, theme)

                if not allow_fixture_assets:
                    check_fixture_assets()

            # Task 12: degradacion con prefers-reduced-motion. Corre solo
            # cuando `--reduced` esta activo (la pagina se abrio con
            # `reduced_motion="reduce"`, arriba). Video/letterbox son
            # decoracion cinematografica pura: deben apagarse. Galeria y
            # creditos son contenido — apagarlos dejaria al visitante sin
            # informacion, asi que se comprueba que siguen operativos, no que
            # desaparecen.
            if reduced:
                degraded = page.evaluate("""(() => {
                  const host = document.querySelector('.bg-theme');
                  const bars = [...document.querySelectorAll('[data-letterbox]')];
                  return {
                    noVideo: !host || !host.querySelector('video'),
                    barsClosed: bars.every(b => b.getBoundingClientRect().height < 1),
                    galleryUsable: !!document.querySelector('[data-gallery-track]'),
                    creditsUsable: document.querySelectorAll('[data-credit]').length > 0,
                    textVisible: (() => {
                      const n = document.querySelector('[data-hero-name]');
                      return !!n && getComputedStyle(n).opacity === "1";
                    })(),
                  };
                })()""")
                check(degraded["noVideo"], "sin video con reduced-motion")
                check(degraded["barsClosed"], "sin letterbox con reduced-motion")
                check(degraded["textVisible"], "el nombre es legible con reduced-motion")
                # Son contenido, no decoracion: apagarlos dejaria sin informacion.
                check(degraded["galleryUsable"], "la galeria sigue disponible")
                check(degraded["creditsUsable"], "los creditos siguen disponibles")
        finally:
            if page:
                page.close()
            browser.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="vice")
    ap.add_argument("--url", default="http://127.0.0.1:5173")
    ap.add_argument(
        "--allow-fixture-assets",
        action="store_true",
        help="Silencia el gate de assets provisionales (defecto 3) mientras dure el desarrollo. "
        "NO esta activo por defecto: hay que pasarlo. Silencia la CATEGORIA entera, asi que "
        "para el uso diario es mejor la linea base, que distingue un fallo nuevo de los "
        "conocidos. El gate final debe correr sin este flag.",
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
        help="Abre la pagina con prefers-reduced-motion:reduce y comprueba la degradacion "
        "accesible (Task 12): sin video, sin letterbox, nombre legible, galeria y creditos "
        "operativos.",
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
