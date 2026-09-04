"""Las 23 figuras de la bandeja de Creditos (Caelestia, fase B4).

REGLA: a igual dato, igual tamano VISTO. Y eso son dos medidas, no una:

  1. la silueta llega al canto de la caja en los DOS ejes — si el punto mas
     lejano cae en una diagonal, la figura se queda corta y se ve mas pequena;
  2. la mancha de tinta mide lo mismo — el area encajada.

Historia de los tres intentos, porque cada uno arreglaba uno y rompia el otro:
  · normalizar por RADIO MAXIMO -> areas distintas (un triangulo pinta la mitad
    que una galleta con el mismo dato);
  · normalizar por AREA -> extensiones distintas: medido en la maqueta, 13,7% de
    diferencia dentro del mismo escalon (React 73,9 px de ancho, RxDB 84);
  · encajar en la caja Y exigir area comun con figuras de canto recto ->
    imposible: un hexagono o un cuadrado no bajan de area sin dejar de serlo, y
    el despeje los aplanaba a circulos (relieve 0,3%).

Lo que si funciona: UNA SOLA familia armonica para las 23. Todas encajan exactas
en su caja por construccion, y su amplitud se despeja hasta que el area encajada
es la misma. Medido: dispersion de area 0,00%, relieve minimo 17,8% del radio.

  r(t) = 1 + a·cos(n·t) + s·cos(2n·t)

`n` es el numero de lobulos —lo que distingue una figura de otra— y el signo de
`a` decide si son concavos (galleta) o convexos (trebol / flor / estrella).
"""
import math, json, pathlib

N = 240
OBJ = 2.86          # area encajada comun, en unidades de caja (la caja mide 4)

def arm(n, a, s, f=0.0):
    rmax = max(1 + a*math.cos(n*t + f) + s*math.cos(2*n*t + 2*f)
               for t in [i*2*math.pi/4000 for i in range(4000)])
    return [(1 + a*math.cos(n*(i*2*math.pi/N) + f) + s*math.cos(2*n*(i*2*math.pi/N) + 2*f))/rmax
            for i in range(N)]

def puntos(rs):
    return [(r*math.cos(i*2*math.pi/N), r*math.sin(i*2*math.pi/N)) for i, r in enumerate(rs)]

def encaja(P):
    """Encaja el poligono en su caja: se normaliza el VANO de cada eje y se
    recentra.

    No vale dividir por `max(abs(x))`: eso es el radio, no la media anchura, y
    en una figura de lobulos IMPARES la silueta no es simetrica respecto al
    centro. Medido con la version anterior: el trebol de 3 de JavaScript ocupaba
    90,4 px de ancho donde el trebol de 4 de Git ocupaba 102 — un 13,7% menos
    con el mismo dato, que es justo lo que se veia."""
    xs = [x for x, _ in P]; ys = [y for _, y in P]
    cx = (max(xs) + min(xs))/2; cy = (max(ys) + min(ys))/2
    hx = (max(xs) - min(xs))/2; hy = (max(ys) - min(ys))/2
    return [((x - cx)/hx, (y - cy)/hy) for x, y in P], max(hx, hy)/min(hx, hy)

def area(P):
    return abs(sum(P[i][0]*P[(i+1) % N][1] - P[(i+1) % N][0]*P[i][1] for i in range(N)))/2

def areaEncajada(rs):
    return area(encaja(puntos(rs))[0])

def familia(tipo, n):
    return (lambda a: arm(n, -a, a*0.18)) if tipo == "galleta" else (lambda a: arm(n, a, -a*0.14))

def despeja(f, nom, lo=1e-4, hi=0.85):
    a, b = areaEncajada(f(lo)), areaEncajada(f(hi))
    assert min(a, b) < OBJ < max(a, b), f"{nom}: OBJ fuera de rango {min(a,b):.3f}..{max(a,b):.3f}"
    cre = b > a
    for _ in range(80):
        m = (lo + hi)/2
        if (areaEncajada(f(m)) < OBJ) == cre: lo = m
        else: hi = m
    return (lo + hi)/2

#  Concavas: Interfaz y Backend.   Convexas: Lenguajes y Herramientas.
#  El territorio ya lo dice la banda y su rotulo; la figura identifica la pieza.
#  Ninguna concava por debajo de 5 lobulos: con 3 o 4 la cintura se cierra tanto
#  que la figura se lee como un aspa y el icono se sale por los brazos. Medido en
#  la maqueta con `react` (galleta de 4) y `python` (galleta de 3).
#  El territorio ya lo dicen la banda y su rotulo; la figura identifica la pieza.
DEF = [
    # Interfaz (8) — concavas
    ("react",        "galleta de 5",  "galleta", 5),
    ("nextdotjs",    "galleta de 6",  "galleta", 6),
    ("typescript",   "galleta de 7",  "galleta", 7),
    ("tailwindcss",  "galleta de 8",  "galleta", 8),
    ("vite",         "galleta de 9",  "galleta", 9),
    ("gsap",         "galleta de 10", "galleta", 10),
    ("electron",     "galleta de 11", "galleta", 11),
    ("gtk",          "galleta de 12", "galleta", 12),
    # Backend y datos (5) — convexas de pocos lobulos
    ("python",       "trebol de 3",   "trebol", 3),
    ("django",       "trebol de 4",   "trebol", 4),
    ("nodedotjs",    "trebol de 5",   "trebol", 5),
    ("mysql",        "trebol de 6",   "trebol", 6),
    ("rxdb",         "trebol de 7",   "trebol", 7),
    # Lenguajes base (5) — convexas de muchos lobulos
    ("javascript",   "flor de 8",     "trebol", 8),
    ("html5",        "flor de 9",     "trebol", 9),
    ("css",          "flor de 10",    "trebol", 10),
    ("c",            "flor de 11",    "trebol", 11),
    ("cplusplus",    "flor de 12",    "trebol", 12),
    # Herramientas (5) — concavas de muchos lobulos
    ("git",          "galleta de 13", "galleta", 13),
    ("github",       "galleta de 14", "galleta", 14),
    ("n8n",          "galleta de 15", "galleta", 15),
    ("claude",       "galleta de 16", "galleta", 16),
    ("googlegemini", "galleta de 18", "galleta", 18),
]

def poly(P):
    return 'polygon(' + ', '.join(f'{50+50*x:.2f}% {50+50*y:.2f}%' for x, y in P) + ')'

FIG, SUAVE, NOM, RIN = {}, {}, {}, {}
areas, anis, relieve = [], [], []
for sl, nom, tipo, n in DEF:
    f = familia(tipo, n)
    v = despeja(f, nom)
    rs = f(v)
    P, an = encaja(puntos(rs))
    FIG[sl] = poly(P); NOM[sl] = nom
    PS, _ = encaja(puntos([1 + (r - 1)*0.42 for r in rs]))   # al rozar: se ablanda, sin cambiar de caja
    SUAVE[sl] = poly(PS)
    areas.append(area(P)); anis.append((nom, round(an, 3)))
    RIN[sl] = round(min(math.hypot(x, y) for x, y in P), 4)
    relieve.append((nom, round((max(rs) - min(rs))*100, 1)))
CIRC = poly(encaja(puntos([1.0]*N))[0])

# ---------- gates: ninguno se da por bueno sin haberlo visto dar rojo ----------
d = lambda xs: (max(xs) - min(xs))/min(xs)
assert len(FIG) == 23, f"faltan figuras: {len(FIG)}"
assert len(set(FIG.values())) == 23, "hay figuras repetidas"
assert all(v.count('%')//2 == N for v in list(FIG.values()) + list(SUAVE.values()) + [CIRC]), \
    "no todas tienen 240 vertices: con distinto numero un polygon() no morfa, corta de golpe"
assert d(areas) < 0.005, f"areas distintas tras encajar: {d(areas)*100:.2f}%"
peor_rel = min(r[1] for r in relieve)
assert peor_rel >= 6.0, f"«{[r[0] for r in relieve if r[1]==peor_rel][0]}» se queda casi lisa: {peor_rel}%"
peor_an = max(a[1] for a in anis)
assert peor_an < 1.25, f"«{[a[0] for a in anis if a[1]==peor_an][0]}» se deforma x{peor_an} al encajar"

pathlib.Path("/home/aoshi/proyectos/portfolio-aoshi/.superpowers/brainstorm/3051416-1788476200/content/figuras23.js").write_text(
    "window.FIG23=" + json.dumps(FIG) + ";\nwindow.FIG23S=" + json.dumps(SUAVE) +
    ";\nwindow.FIG23N=" + json.dumps(NOM) + ";\nwindow.FIG23R=" + json.dumps(RIN) +
    ";\nwindow.FIGCIRC=" + json.dumps(CIRC) + ";\n")
print(f"OK · 23 figuras · encajan exactas en su caja (dos ejes) · area dispersion {d(areas)*100:.2f}% "
      f"· relieve minimo {peor_rel}% · deformacion peor x{peor_an} · radio inscrito {min(RIN.values()):.2f}..{max(RIN.values()):.2f}")
