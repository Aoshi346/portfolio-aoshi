"""Precision de aterrizaje de cada ancla, en las cinco escenas y los tres temas.

Umbral: |y_reposo - y_destino| <= 8 px, medido tras 3,5 s de asentamiento de
Lenis. Lenis sigue desplazando la pagina despues de un scrollTo: medir antes de
que asiente da falsos positivos.
"""
import pathlib
import re
import sys
from playwright.sync_api import sync_playwright

TOLERANCIA = 8
ANCLAS = ["hero", "quien-es", "obra", "creditos", "contacto"]
TEMAS = ["vice", "hyprland", "caelestia"]

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def _constante(fichero: str, nombre: str) -> float:
    texto = (RAIZ / fichero).read_text(encoding="utf-8")
    hallazgo = re.search(rf"^(?:export )?const {nombre} = ([\d.]+);", texto, re.M)
    if hallazgo is None:
        raise SystemExit(f"no encuentro {nombre} en {fichero} — el guardarrail esta roto")
    return float(hallazgo.group(1))


def comprueba_acoplamiento() -> list[str]:
    """`OBRA_TOTAL_U` de sceneNav.ts reimplementa la duracion de la timeline
    maestra del carril, que de verdad vive en vice.choreography.ts como
    OBRA_TRANSIT y OBRA_REST. Es el tercer sitio que copia esas dos constantes
    (el segundo es measure-obra-rail.py) y CLAUDE.md ya avisa de la trampa: si
    divergen, el ancla de obra no falla, ATERRIZA MAL EN SILENCIO. Aqui se
    recalcula y se compara, para que la deriva sea ruidosa.
    """
    transit = _constante("src/themes/vice.choreography.ts", "OBRA_TRANSIT")
    rest = _constante("src/themes/vice.choreography.ts", "OBRA_REST")
    total = _constante("src/components/sceneNav.destino.ts", "OBRA_TOTAL_U")
    saltos = 4  # cinco cartelas, cuatro transiciones entre ellas
    esperado = saltos * transit + (saltos + 1) * rest
    if abs(esperado - total) > 1e-9:
        return [
            f"OBRA_TOTAL_U={total} en sceneNav.ts, pero OBRA_TRANSIT={transit} y "
            f"OBRA_REST={rest} en vice.choreography.ts dan {esperado}. "
            "Alguien movio la coreografia sin mover la navegacion."
        ]
    print(f"OK acoplamiento: OBRA_TOTAL_U {total} coincide con la coreografia")
    return []


def comprueba_indice() -> list[str]:
    """Cinco entradas, ninguna vacia. Que digan la VERDAD es cosa de quien
    cambie la escena; por eso viven en content.ts, que es donde se mira al
    cambiarla. Lo que si se puede comprobar aqui es que no falte ninguna ni
    se quede en blanco."""
    texto = (RAIZ / "src/data/content.ts").read_text(encoding="utf-8")
    bloque = re.search(r"sceneIndex: SceneEntry\[\] = \[(.*?)\];", texto, re.S)
    if bloque is None:
        return ["no encuentro sceneIndex en content.ts"]
    entradas = re.findall(r'blurb:\s*"([^"]*)"', bloque.group(1))
    if len(entradas) != 5:
        return [f"sceneIndex tiene {len(entradas)} descriptores, esperaba 5"]
    vacios = [i for i, e in enumerate(entradas) if not e.strip()]
    if vacios:
        return [f"descriptores vacios en las posiciones {vacios}"]
    print(f"OK indice: 5 descriptores, ninguno vacio")
    return []


def main() -> int:
    fallos = comprueba_acoplamiento() + comprueba_indice()
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        for tema in TEMAS:
            for ancla in ANCLAS:
                pg = b.new_page(viewport={"width": 1440, "height": 900})
                pg.goto(f"http://localhost:4173/?theme={tema}", wait_until="domcontentloaded", timeout=30000)
                pg.wait_for_timeout(9000)  # leader de apertura + GSAP + shader
                enlace = pg.query_selector(f'.scene-nav a[href="#{ancla}"]')
                if enlace is None:
                    fallos.append(f"{tema} #{ancla}: no hay enlace")
                    pg.close()
                    continue
                destino = pg.evaluate("() => window.__navDestino__?.('%s')" % ancla)
                enlace.click()
                pg.wait_for_timeout(3500)  # asentamiento de Lenis
                reposo = pg.evaluate("window.scrollY")
                if destino is None:
                    fallos.append(f"{tema} #{ancla}: sin destino calculado")
                elif abs(reposo - destino) > TOLERANCIA:
                    fallos.append(f"{tema} #{ancla}: reposo {reposo:.0f} vs destino {destino:.0f}")
                else:
                    print(f"OK {tema} #{ancla}: {reposo:.0f} (destino {destino:.0f})")
                pg.close()
        b.close()

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{len(fallos)} anclas fuera de tolerancia")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
