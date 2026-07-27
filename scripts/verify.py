"""Arnes de verificacion visual. Cada tarea del plan anade aserciones aqui.

Uso: python3 scripts/verify.py [--theme vice] [--url http://127.0.0.1:5173]
Requiere el servidor de desarrollo levantado (npm run dev).
"""
import argparse
import sys
from playwright.sync_api import sync_playwright

CHROME = "/usr/bin/google-chrome"
ARGS = ["--no-sandbox", "--use-gl=swiftshader", "--enable-unsafe-swiftshader"]
DESKTOP = {"width": 1440, "height": 900}
MOBILE = {"width": 390, "height": 844}

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


def run(theme: str, url: str) -> None:
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
        finally:
            if page:
                page.close()
            browser.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", default="vice")
    ap.add_argument("--url", default="http://127.0.0.1:5173")
    args = ap.parse_args()
    run(args.theme, args.url)
    print()
    if failures:
        print(f"FALLOS: {len(failures)}")
        return 1
    print("TODO OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
