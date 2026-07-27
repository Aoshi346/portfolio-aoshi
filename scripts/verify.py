"""Arnes de verificacion visual. Cada tarea del plan anade aserciones aqui.

Uso: python3 scripts/verify.py [--theme vice] [--url http://127.0.0.1:5173]
             [--allow-fixture-assets]
Requiere el servidor de desarrollo levantado (npm run dev).

--allow-fixture-assets silencia el gate de assets provisionales (Tarea C /
defecto 3) mientras dure el desarrollo. Esta desactivado por defecto: el gate
final debe correr sin el flag.
"""
import argparse
import hashlib
import sys
from pathlib import Path

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


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


def run(theme: str, url: str, allow_fixture_assets: bool = False) -> None:
    global failures
    failures = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=CHROME, args=ARGS)
        page = None
        try:
            page = browser.new_page(viewport=DESKTOP)
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

            if theme == "vice":
                backdrop = page.evaluate("""(() => {
                  const host = document.querySelector('.bg-theme');
                  if (!host) return null;
                  const img = host.querySelector('img');
                  const video = host.querySelector('video');
                  return {
                    poster: !!img,
                    video: !!video,
                    playing: video ? !video.paused : false,
                  };
                })()""")
                check(backdrop is not None and backdrop["poster"], "hay poster en el backdrop")
                check(backdrop is not None and backdrop["video"], "hay video en el backdrop")
                check(backdrop is not None and backdrop["playing"], "el video se reproduce")

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

                if not allow_fixture_assets:
                    check_fixture_assets()
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
        "Activo por defecto: el gate final debe correr SIN este flag.",
    )
    args = ap.parse_args()
    run(args.theme, args.url, allow_fixture_assets=args.allow_fixture_assets)
    print()
    if failures:
        print(f"FALLOS: {len(failures)}")
        return 1
    print("TODO OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
