"""Matriz de recorte de las vias de contacto: ancho x estado de hover.

El correo se cortaba por DOS causas independientes, y las dos son estados de
TRANSITO, no de reposo: un viewport intermedio (ni 390 ni 1440, que son los dos
unicos anchos que se venian mirando) y una barra vecina creciendo por hover. Un
ancho fijo en reposo no ve ninguna de las dos. Por eso esto barre el rango.

Se mide con `document.createRange()`, NO con `scrollWidth`: bajo swiftshader
scrollWidth devuelve valores inconsistentes entre ejecuciones (aviso de Vera).
El rectangulo de un Range sobre el nodo de texto es la caja real de los glifos.

Criterio doble, y el segundo se anadio DESPUES de que el primero saliera verde:

1. Cero recorte. El texto de cada via cabe en su propia caja.
2. Cero tamano fuera de la escala. El valor se dimensiona con
   `clamp(var(--t-2), 6.2cqi, var(--t-3))`, y un `clamp` es CONTINUO: entre sus
   dos topes devuelve cualquier numero real. Mirar tres anchos sueltos y ver
   escalones limpios no prueba nada — el tamano roto vive en los anchos que no
   se miraron, que es justo donde la barra queda entre 258 y 344 px. La escala
   va por su tercer aviso, asi que se comprueba en las 65 combinaciones.
"""
import sys
from playwright.sync_api import sync_playwright

# --t-2 y --t-3: los dos unicos escalones que el valor puede tomar.
ESCALONES = (16.0, 21.33)
EPS = 0.05

URL = "http://localhost:4173/?theme=vice"
HOLGURA = 1.0  # px, redondeo subpixel

# 390 (movil real) + el tramo 901..1440 en pasos de ~64, mas los dos anchos
# que abrazan el breakpoint de 1310 para ver el salto en si.
ANCHOS = [390, 901, 965, 1029, 1093, 1157, 1221, 1285, 1305, 1315, 1349, 1413, 1440]
BARRAS = ["correo", "linkedin", "telefono", "github"]

MEDIDA = """() => {
    const salida = [];
    for (const bar of document.querySelectorAll('.contacto-bar')) {
        const v = bar.querySelector('.contacto-bar-value');
        if (!v || !v.firstChild) continue;
        // Range sobre el nodo de texto: la caja real de los glifos, sin
        // depender de scrollWidth.
        const r = document.createRange();
        r.selectNodeContents(v);
        const texto = r.getBoundingClientRect();
        const caja = v.getBoundingClientRect();
        const barra = bar.getBoundingClientRect();
        salida.push({
            via: [...bar.classList].find(c => c.startsWith('contacto-bar--')) || bar.className,
            texto: Math.round(texto.width * 10) / 10,
            caja: Math.round(caja.width * 10) / 10,
            fuera_izq: Math.round((barra.left - texto.left) * 10) / 10,
            fuera_der: Math.round((texto.right - barra.right) * 10) / 10,
            tam: getComputedStyle(v).fontSize,
        });
    }
    return salida;
}"""


def revisa(datos, etiqueta, fallos):
    for d in datos:
        via = d["via"].replace("contacto-bar--", "")
        if d["texto"] > d["caja"] + HOLGURA:
            fallos.append(
                f"{etiqueta}: {via} no cabe en su caja "
                f"({d['texto']} px de texto en {d['caja']} px, tam {d['tam']})"
            )
        elif d["fuera_izq"] > HOLGURA or d["fuera_der"] > HOLGURA:
            fallos.append(
                f"{etiqueta}: {via} se sale de la barra "
                f"(izq {d['fuera_izq']}, der {d['fuera_der']})"
            )
        tam = float(d["tam"].removesuffix("px"))
        if not any(abs(tam - e) < EPS for e in ESCALONES):
            fallos.append(
                f"{etiqueta}: {via} a {tam} px, que no es ningun escalon "
                f"de la escala {ESCALONES}"
            )


def main() -> int:
    fallos = []
    combinaciones = 0
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--use-gl=swiftshader"])
        for ancho in ANCHOS:
            pg = b.new_page(viewport={"width": ancho, "height": 900})
            pg.goto(URL, wait_until="domcontentloaded", timeout=30000)
            pg.wait_for_timeout(9000)
            pg.evaluate("""() => {
                const s = document.querySelector('[data-scene="contacto"]');
                window.scrollTo({top: s.getBoundingClientRect().top + scrollY, behavior: 'instant'});
            }""")
            pg.wait_for_timeout(3500)

            reposo = pg.evaluate(MEDIDA)
            revisa(reposo, f"{ancho}px reposo", fallos)
            combinaciones += 1
            tam_reposo = {d["via"]: d["tam"] for d in reposo}

            # El friso: las cuatro rayas ambar alineadas. No es un criterio
            # estetico blando — 8px de desnivel en la cuarta fue un fallo real,
            # y ningun criterio de recorte podia verlo porque no se recortaba
            # nada. Se mide en reposo, que es donde se ve.
            #
            # El eje depende de la disposicion, y de no mirarlo salieron 8
            # falsos positivos: en columna las cuatro marcas estan a distinta
            # altura POR DEFINICION, una debajo de otra. Ahi lo que tiene que
            # coincidir es el borde izquierdo.
            marcas = pg.evaluate("""() => {
                const fila = getComputedStyle(document.querySelector('.contacto-bars'))
                    .flexDirection !== 'column';
                return {fila, cajas: [...document.querySelectorAll('.contacto-bar-mark')]
                    .map(n => { const r = n.getBoundingClientRect();
                        return {top: Math.round(r.top * 10) / 10,
                                left: Math.round(r.left * 10) / 10,
                                visible: r.width > 0}; })};
            }""")
            eje = "top" if marcas["fila"] else "left"
            bordes = [c[eje] for c in marcas["cajas"] if c["visible"]]
            if bordes and max(bordes) - min(bordes) > HOLGURA:
                como = "en fila" if marcas["fila"] else "apilado"
                fallos.append(
                    f"{ancho}px reposo ({como}): el friso esta desalineado, "
                    f"{eje} {sorted(set(bordes))}"
                )

            for via in BARRAS:
                sel = f".contacto-bar--{via}"
                if pg.query_selector(sel) is None:
                    fallos.append(f"{ancho}px: no existe {sel}")
                    continue
                pg.hover(sel)
                pg.wait_for_timeout(900)  # la transicion de flex-grow dura 520 ms
                datos = pg.evaluate(MEDIDA)
                revisa(datos, f"{ancho}px hover:{via}", fallos)
                # Estabilidad: senalar una barra no puede cambiar el tamano del
                # texto de las OTRAS. Pasaba: apuntar a Telefono bajaba la
                # direccion de correo de 21.33 a 16 px, un 25% menos, por estar
                # el raton en otro sitio.
                for d in datos:
                    otra = d["via"].replace("contacto-bar--", "")
                    if otra != via and tam_reposo.get(d["via"]) != d["tam"]:
                        fallos.append(
                            f"{ancho}px hover:{via}: {otra} cambia de "
                            f"{tam_reposo.get(d['via'])} a {d['tam']} sin que la senalen"
                        )
                combinaciones += 1
            pg.close()
        b.close()

    for f in fallos:
        print("FALLO:", f)
    print(f"\n{combinaciones} combinaciones medidas, {len(fallos)} con recorte")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
