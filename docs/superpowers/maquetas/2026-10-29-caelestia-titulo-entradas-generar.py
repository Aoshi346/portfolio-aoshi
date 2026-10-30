"""Genera la maqueta viva del Titulo (variantes A y B) para el visual companion.

Uso: python3 generar.py <fichero_salida.html>
Todo va embebido: fondos reales (capturas del build con el contenido oculto),
contornos de Fraunces a opsz 144 y tokens leidos del sitio en marcha.
"""
import base64
import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).parent


def b64(nombre: str) -> str:
    return "data:image/jpeg;base64," + base64.b64encode((AQUI / nombre).read_bytes()).decode()


def glifos() -> dict:
    ts = (AQUI / "firma144.ts").read_text()
    ancho = float(re.search(r"ancho: ([0-9.]+)", ts).group(1))
    lista = []
    for c, d in re.findall(r'\{ c: "(.)", d: "([^"]+)" \}', ts):
        nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", d)]
        xs, ys = nums[0::2], nums[1::2]
        lista.append({"c": c, "d": d, "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys)})
    return {"ancho": ancho, "glifos": lista}


FUENTES = (
    "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,100..900,0..100,0..1"
    "&family=Hanken+Grotesk:wght@100..900&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=swap"
)

DATOS = {
    "fondos": {
        "dia": {"desk": b64("fondo-dia-desk.jpg"), "mov": b64("fondo-dia-mov.jpg")},
        "noche": {"desk": b64("fondo-noche-desk.jpg"), "mov": b64("fondo-noche-mov.jpg")},
    },
    # Tokens reales (getComputedStyle sobre el build, 12:00 y 22:30).
    "color": {
        "dia": {"texto": "oklch(0.245 0.035 240)", "rol": "oklch(0.47 0.032 240)",
                 "pilla": "oklch(0.855 0.152 96)", "pillaTxt": "oklch(0.215 0.05 96)"},
        "noche": {"texto": "oklch(0.925 0.005 37.5)", "rol": "oklch(0.795 0.008 37.5)",
                   "pilla": "oklch(0.905 0.152 96)", "pillaTxt": "oklch(0.215 0.05 96)"},
    },
    # Ventana de la escena #hero medida en el build: entre la barra y el dock.
    "ventana": {"desk": [14, 68, 1412, 748], "mov": [14, 68, 362, 692]},
    "firma": glifos(),
    "fuentes": FUENTES,
}

PAGINA = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Titulo: dos entradas</title>
<link rel="stylesheet" href="__FUENTES__">
<style>
  :root { --bg:#f4f4f2; --txt:#1d1d1f; --sub:#5b5b60; --linea:#d4d4d0; --acento:#0b5cad; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--txt); font: 15px/1.5 "Hanken Grotesk", system-ui, sans-serif; }
  header { padding: 22px 28px 10px; }
  h2 { font: 600 22px/1.25 "Hanken Grotesk", sans-serif; margin: 0 0 4px; }
  .sub { color: var(--sub); margin: 0; max-width: 72ch; }
  .barra { display: flex; flex-wrap: wrap; gap: 8px 18px; align-items: center; padding: 12px 28px; border-bottom: 1px solid var(--linea); }
  .grupo { display: inline-flex; border: 1px solid var(--linea); border-radius: 999px; overflow: hidden; }
  .grupo button, .solo { font: 500 14px "Hanken Grotesk", sans-serif; border: 0; background: #fff; color: var(--txt); padding: 7px 14px; cursor: pointer; }
  .grupo button + button { border-left: 1px solid var(--linea); }
  .grupo button[aria-pressed="true"] { background: var(--txt); color: #fff; }
  .solo { border: 1px solid var(--linea); border-radius: 999px; }
  .solo.play { background: var(--acento); color: #fff; border-color: var(--acento); }
  button:focus-visible { outline: 2px solid var(--acento); outline-offset: 2px; }
  label.chk { display: inline-flex; gap: 6px; align-items: center; cursor: pointer; }
  main { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 24px; padding: 20px 28px; align-items: start; }
  .marco { position: relative; overflow: hidden; border-radius: 10px; box-shadow: 0 0 0 1px var(--linea); background: #ddd; }
  .marco iframe { position: absolute; top: 0; left: 0; border: 0; transform-origin: 0 0; }
  .pie { color: var(--sub); font-size: 13px; margin: 6px 2px 0; }
  .ficha { padding: 0 28px 28px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; max-width: 1180px; }
  .ficha section { border: 1px solid var(--linea); border-radius: 10px; padding: 14px 18px; background: #fff; }
  .ficha h3 { margin: 0 0 6px; font: 600 16px "Hanken Grotesk", sans-serif; }
  .ficha p { margin: 0 0 10px; color: var(--sub); }
  .ficha .solo { margin-top: 2px; }
  .ficha section.elegida { box-shadow: 0 0 0 2px var(--acento); }
  @media (max-width: 1100px) { main { grid-template-columns: 1fr; } .ficha { grid-template-columns: 1fr; } }
</style></head>
<body>
<header>
  <h2>Titulo: tu nombre en el centro y dos entradas para elegir</h2>
  <p class="sub">Fondo, barra y dock son capturas del sitio real; el nombre usa los contornos reales de Fraunces a opsz 144. Sin cifras, sin widget y sin «Desde 2021». Pulsa «Reproducir» para ver la entrada otra vez.</p>
</header>
<div class="barra" role="toolbar" aria-label="Controles de la maqueta">
  <span class="grupo" data-grupo="variante"><button aria-pressed="true" data-v="A">A · Enfoque</button><button aria-pressed="false" data-v="B">B · Trazo</button></span>
  <span class="grupo" data-grupo="hora"><button aria-pressed="true" data-v="dia">Dia</button><button aria-pressed="false" data-v="noche">Noche</button></span>
  <button class="solo play" id="play">Reproducir</button>
  <label class="chk"><input type="checkbox" id="reducido"> Movimiento reducido</label>
  <label class="chk"><input type="checkbox" id="pilla"> Pastilla «Disponible para proyectos»</label>
</div>
<main>
  <div><div class="marco" id="mDesk"><iframe id="fDesk" title="Escritorio 1440x900" width="1440" height="900"></iframe></div><p class="pie">Escritorio, 1440 x 900</p></div>
  <div><div class="marco" id="mMov"><iframe id="fMov" title="Movil 390x844" width="390" height="844"></iframe></div><p class="pie">Movil, 390 x 844</p></div>
</main>
<div class="ficha">
  <section data-ficha="A"><h3>A · Enfoque</h3><p>El nombre entra cambiando de tamano optico y de peso, de fino y pequeno a grueso de cartel, en 900 ms con curva blanda; al final las formas torcidas de Fraunces encajan de golpe. Despues el rol se descubre con un corte seco de 400 ms.</p><button class="solo" data-elegir="A">Me quedo con A</button></section>
  <section data-ficha="B"><h3>B · Trazo</h3><p>El nombre se dibuja letra a letra con su contorno real y se rellena; contorno y texto tienen la misma forma, asi que el paso a texto vivo no se nota. El mismo corte seco para el rol.</p><button class="solo" data-elegir="B">Me quedo con B</button></section>
</div>
<script>
const DATOS = __DATOS__;
const estado = { variante: "A", hora: "dia", reducido: false, pilla: false };

let indice = 0;
function svgLinea(glifos) {
  const paths = glifos.map(g => `<path pathLength="1" style="--i:${indice++}" d="${g.d}"></path>`).join("");
  return `<svg class="trazo" aria-hidden="true">${paths}</svg>`;
}

function documento(disp) {
  const c = DATOS.color[estado.hora];
  const [vx, vy, vw, vh] = DATOS.ventana[disp];
  const movil = disp === "mov";
  const g = DATOS.firma.glifos;
  indice = 0;
  // "Aoshi" son los cinco primeros glifos (los espacios no generan contorno).
  const nombreSvg = movil
    ? `<span class="linea">${svgLinea(g.slice(0, 5))}</span><span class="linea">${svgLinea(g.slice(5))}</span>`
    : `<span class="linea">${svgLinea(g)}</span>`;
  const nombreTxt = movil
    ? `<span class="linea">Aoshi</span><span class="linea">Blanco Sanz</span>`
    : `<span class="linea">Aoshi Blanco Sanz</span>`;
  const red = estado.reducido;
  return `<!doctype html><html lang="es"><head><meta charset="utf-8"><link rel="stylesheet" href="${DATOS.fuentes}">
<style>
  html,body{margin:0;height:100%;overflow:hidden}
  body{background:url(${DATOS.fondos[estado.hora][disp]}) 0 0/100% 100% no-repeat;font-family:"Hanken Grotesk",sans-serif}
  .ventana{position:absolute;left:${vx}px;top:${vy}px;width:${vw}px;height:${vh}px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:${movil ? 14 : 22}px}
  h1{margin:0;color:${c.texto};font-family:Fraunces,serif;font-weight:900;font-size:${movil ? "50.52px" : "119.77px"};line-height:1;letter-spacing:-0.01em;
     font-variation-settings:"opsz" 144,"wght" 900,"SOFT" 0,"WONK" 1;display:grid}
  h1 .linea{display:block}
  .rol{margin:0;color:${c.rol};font-weight:400;font-size:${movil ? "21.33px" : "28.43px"};line-height:1.3}
  .pilla{display:inline-flex;align-items:center;gap:8px;font:400 10.67px/16px "Martian Mono",monospace;letter-spacing:.06em;background:${c.pilla};color:${c.pillaTxt};padding:6px 12px;border-radius:999px}
  .pilla i{width:7px;height:7px;border-radius:50%;background:currentColor}
  /* --- A: enfoque --- */
  .A h1{animation:enfoque 900ms cubic-bezier(.2,.7,.2,1) both}
  @keyframes enfoque{
    0%{opacity:0;letter-spacing:.09em;font-variation-settings:"opsz" 9,"wght" 100,"SOFT" 0,"WONK" 0}
    35%{opacity:1}
    99%{font-variation-settings:"opsz" 144,"wght" 900,"SOFT" 0,"WONK" 0}
    100%{opacity:1;letter-spacing:-0.01em;font-variation-settings:"opsz" 144,"wght" 900,"SOFT" 0,"WONK" 1}}
  /* --- B: trazo --- */
  .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
  .B h1 .dib{display:grid;justify-items:center;row-gap:.06em}
  .trazo{display:block;overflow:visible}
  .trazo path{fill:${c.texto};fill-opacity:0;stroke:${c.texto};stroke-width:1.1;stroke-dasharray:1;stroke-dashoffset:1;
     animation:dibuja 760ms cubic-bezier(.45,0,.25,1) calc(var(--i)*55ms) both, rellena 420ms ease-out 1550ms both}
  @keyframes dibuja{to{stroke-dashoffset:0}}
  @keyframes rellena{to{fill-opacity:1;stroke-opacity:0}}
  /* --- rol y pastilla: corte seco, igual en las dos --- */
  .rol,.pilla{animation:corte 400ms cubic-bezier(.7,0,.2,1) both}
  .A .rol{animation-delay:950ms}.A .pilla{animation-delay:1070ms}
  .B .rol{animation-delay:2100ms}.B .pilla{animation-delay:2220ms}
  @keyframes corte{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
  ${red ? "*,*::before,*::after{animation:none!important} .trazo path{fill-opacity:1;stroke-opacity:0;stroke-dashoffset:0}" : ""}
</style></head><body>
<div class="ventana ${estado.variante}">
  <h1>${estado.variante === "B" ? `<span class="sr">Aoshi Blanco Sanz</span><span class="dib" aria-hidden="true">${nombreSvg}</span>` : nombreTxt}</h1>
  <p class="rol">Desarrollador full stack en Caracas.</p>
  ${estado.pilla ? '<span class="pilla"><i></i>Disponible para proyectos</span>' : ""}
</div>
<script>
  const svgs = [...document.querySelectorAll(".trazo")];
  const cajas = svgs.map(s => [...s.querySelectorAll("path")].map(p => p.getBBox()));
  const y0 = Math.min(...cajas.flat().map(b => b.y)), y1 = Math.max(...cajas.flat().map(b => b.y + b.height));
  svgs.forEach((s, i) => {
    const x0 = Math.min(...cajas[i].map(b => b.x)), x1 = Math.max(...cajas[i].map(b => b.x + b.width));
    s.setAttribute("viewBox", [x0, y0, x1 - x0, y1 - y0].join(" "));
    s.style.width = (x1 - x0) / 100 + "em"; s.style.height = (y1 - y0) / 100 + "em";
  });
<\/script><\/body><\/html>`;
}

function encajar() {
  const anchoDesk = Math.min(document.querySelector("main > div").clientWidth, 1100);
  const sD = anchoDesk / 1440;
  const mD = document.getElementById("mDesk");
  mD.style.width = 1440 * sD + "px"; mD.style.height = 900 * sD + "px";
  document.getElementById("fDesk").style.transform = `scale(${sD})`;
  const sM = (900 * sD) / 844;
  const mM = document.getElementById("mMov");
  mM.style.width = 390 * sM + "px"; mM.style.height = 844 * sM + "px";
  document.getElementById("fMov").style.transform = `scale(${sM})`;
}

function pintar() {
  document.getElementById("fDesk").srcdoc = documento("desk");
  document.getElementById("fMov").srcdoc = documento("mov");
  document.querySelectorAll(".ficha section").forEach(s => s.classList.toggle("elegida", s.dataset.ficha === estado.variante));
}

document.querySelectorAll(".grupo").forEach(grupo => {
  grupo.addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    grupo.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    estado[grupo.dataset.grupo === "variante" ? "variante" : "hora"] = b.dataset.v;
    pintar();
  });
});
document.getElementById("play").addEventListener("click", pintar);
document.getElementById("reducido").addEventListener("change", e => { estado.reducido = e.target.checked; pintar(); });
document.getElementById("pilla").addEventListener("change", e => { estado.pilla = e.target.checked; pintar(); });
document.querySelectorAll("[data-elegir]").forEach(b => b.addEventListener("click", () => {
  const v = b.dataset.elegir;
  if (window.brainstorm) window.brainstorm.choice(v, { pilla: estado.pilla, hora: estado.hora });
  document.querySelectorAll("[data-elegir]").forEach(x => x.textContent = x.dataset.elegir === v ? "Elegida" : "Me quedo con " + x.dataset.elegir);
}));
window.addEventListener("resize", encajar);
encajar(); pintar();
</script>
</body></html>
"""

html = PAGINA.replace("__FUENTES__", FUENTES).replace("__DATOS__", json.dumps(DATOS, ensure_ascii=False))
Path(sys.argv[1]).write_text(html)
print(f"{sys.argv[1]}: {len(html) // 1024} KB")
