# Traspaso — arreglar el iris del leader de apertura (tema Vice)

> **RESUELTO (2026-07-28).** Se aplico la "alternativa recomendada" de mas
> abajo: `@property --iris` + radio de `mask-image` animado sobre una capa
> negra a pantalla completa. El `box-shadow` de 130vmax escalado y el
> `mask-size` animado ya no existen. El resto del documento se conserva porque
> las trampas y el metodo de medicion siguen valiendo; lo que describe como
> "implementacion de hoy" es la ANTIGUA.

## Objetivo

Al cargar la pagina en el tema Vice hay un "leader" de academia: cuenta atras
3-2-1 con brazo barredor, y al llegar a uno **el propio circulo se abre como el
diafragma de una camara** (iris) dejando ver el hero por dentro. El gesto lo
eligio el usuario viendo mockups animados; el diseno esta aprobado y no se
discute. **Lo que falla es la implementacion del iris.**

Sintoma reportado por el usuario en navegador real: "el iris no funciona bien".

## Como arrancar

```bash
# El Node del sistema es 18.19.1 y Vite 8 exige >= 20.
export PATH="$HOME/.nvm/versions/node/v22.22.3/bin:$PATH"
npm run dev        # http://127.0.0.1:5173/?theme=vice
npm run build      # tsc + vite build
npm run lint
python3 scripts/verify.py            # arnes propio (ver "Estado del arnes")
```

El tema se sortea al azar por visita: usar SIEMPRE `?theme=vice`.

## Donde vive el codigo

| Archivo | Que hace |
|---|---|
| `src/components/introLeader.ts` | Construye el DOM del leader (nuevo) |
| `src/style.css` | Bloque "Leader de apertura (Vice)": `.intro-leader`, `.leader-iris`, `.leader-ring`, `.leader-sweep`, `.leader-num`, `.leader-cue`, `.leader-cross`, `.leader-foot` |
| `src/themes/vice.choreography.ts` | `sceneIntro(gsap)` — la timeline. Se llama la PRIMERA en `viceChoreography` |
| `src/main.ts` | Monta el leader, anade `.js-leader`, arma los dos seguros |
| `src/utils/reveal.ts` | `gsap.ticker.lagSmoothing(500, 33)` |

## Como esta implementado hoy el iris (y por que sospecho que es el fallo)

`.leader-iris` es un circulo de 20px centrado con margen negativo, y **el negro
de toda la pantalla lo pinta su `box-shadow`**:

```css
.leader-iris {
  position: absolute; top: 50%; left: 50%;
  width: 20px; height: 20px; margin: -10px 0 0 -10px;
  border-radius: 50%;
  box-shadow: 0 0 0 130vmax #07050c;
  transform: scale(0);
}
```

La timeline lo anima `scale: 0 -> 120`, de modo que el agujero transparente
crece desde el centro.

**Sospecha principal:** `transform: scale()` escala TAMBIEN el `box-shadow`. A
`scale(120)`, una extension de `130vmax` pasa a ser del orden de cientos de
miles de pixeles de area pintada. Es un caso patologico de rasterizado: el
navegador puede quedarse clavado, pintar mal, o directamente descartar la capa.
Eso encaja con "no funciona bien" en maquina real aunque los numeros de la
timeline sean correctos.

**Intento anterior, tambien fallido:** mascara con `mask-image:
radial-gradient(circle, transparent 49.5%, #000 50%)` y `mask-size` animado de
`0% 0%` a `320% 320%`. Medido: `getComputedStyle(...).maskSize` se quedaba en
`auto`, o sea la mascara no llegaba a aplicarse. No investigue por que; puede
ser que GSAP no escriba bien esa propiedad, o que hiciera falta el prefijo
`-webkit-`.

### Alternativa recomendada para el arreglo

Registrar una custom property y animar el radio de la mascara. `@property`
esta soportado en todos los navegadores modernos y GSAP anima propiedades
registradas sin problema:

```css
@property --iris {
  syntax: "<length-percentage>";
  inherits: false;
  initial-value: 0%;
}

.intro-leader {
  --iris: 0%;
  -webkit-mask-image: radial-gradient(circle at 50% 50%, transparent var(--iris), #000 var(--iris));
          mask-image: radial-gradient(circle at 50% 50%, transparent var(--iris), #000 var(--iris));
}
```

y en la timeline `tl.to(leader, { "--iris": "150%", duration: 0.66 })`. Asi el
agujero crece de verdad desde el centro sin escalar ninguna sombra. Si esto
tampoco tira, el plan C es dos mitades de pantalla que se separan (deja de ser
un iris, hay que consultarlo con el usuario antes).

## Trampas ya pagadas — NO repetirlas

1. **`gsap.from` esta prohibido de facto en este repo.** Deduce un extremo
   leyendo el DOM y ha causado tres regresiones reales (bloques del hero que no
   volvian nunca, 12 filas de creditos desplazadas 34px para siempre, el pie de
   contacto invisible). **Usa siempre `fromTo` con los dos extremos escritos a
   mano.** Y si animas hijos de un contenedor, materializa con `Array.from(...)`:
   pasar una `HTMLCollection` viva fue el detonante en dos de los tres casos.

2. **Un `transform` inline de GSAP gana siempre a una regla CSS.** Si un
   elemento recibe una entrada con GSAP, su hover no puede usar `transform` en
   CSS. Ya mordio en `.credit` y en el CTA de contacto; la solucion fue animar
   un hijo o el envoltorio.

3. **`transform` de GSAP sobrescribe la propiedad entera.** Por eso
   `.leader-iris` se centra con `margin` negativo y no con
   `translate(-50%,-50%)`: el translate se perderia en el primer fotograma.

4. **Los seguros no pueden anclarse a la carga de la pagina.** La timeline no
   arranca hasta que cargan GSAP, Lenis y el modulo de coreografia — cerca de
   un segundo. Un `setTimeout` de 1,8 s desde la carga saltaba a mitad de la
   cuenta atras y arrancaba el leader de la pantalla. Hoy hay DOS seguros
   encadenados: uno de 2,6 s desde la carga ("GSAP no llego nunca") y otro de
   3 s que se arma cuando `sceneIntro` emite el evento `leader:start`.

5. **`gsap.ticker.lagSmoothing(0)` estaba puesto** (copiado de los ejemplos de
   Lenis). Con el desactivado, tras un paron del hilo principal GSAP aplica todo
   el tiempo transcurrido de golpe y la apertura se evapora en un fotograma. Se
   cambio al umbral por defecto `(500, 33)`. **No lo devuelvas a 0.**

## Como medir sin enganarte

Esto me costo mucho tiempo, no lo repitas:

- **`page.screenshot()` en headless perturba el resultado.** Bloquea el
  compositor y GSAP salta hacia delante, con lo que parece que la timeline se
  completa antes de tiempo cuando no es cierto.
- La medicion fiable fue muestrear el progreso **desde dentro de la pagina**,
  sin capturas:

```js
// exponer temporalmente la timeline en sceneIntro:
//   window.__LEADER__ = tl;
await page.evaluate(() => new Promise(res => {
  const out = []; const t0 = performance.now();
  const id = setInterval(() => {
    const tl = window.__LEADER__;
    out.push({ t: Math.round(performance.now() - t0), prog: tl && +tl.progress().toFixed(3) });
    if (performance.now() - t0 > 2200) { clearInterval(id); res(out); }
  }, 120);
}));
```

Con ese metodo la timeline salio **correcta**: duracion 1,62 s, 15 hijos, y
progreso 0,26 -> 0,39 -> 0,55 -> 0,81 -> 1,0 en ~1,6 s reales. O sea: **el
problema no es el ritmo de la timeline, es como se pinta el iris.**

- Para capturas deterministas: `window.__LEADER__.pause()` y luego
  `.progress(x)` antes de cada `screenshot()`. AVISO: con el shader de fondo
  activo en headless (`--use-gl=swiftshader`) esto tarda muchisimo; a mi me
  agoto un timeout de 5 minutos. Bloquea el shader con
  `page.route("**/viceInk*", r => r.abort())` (era `viceHaze` en el momento de
  este handoff; el fondo de Vice cambio de modulo en `2026-08-04-vice-fondo-tinta`)
  mientras depuras el iris.

## Estado del arnes

`python3 scripts/verify.py` deja **12 fallos, todos preexistentes** y ninguno
relacionado con el leader: 9 son rellenos de galeria en `public/media/obra/` y
3 son los ficheros `public/media/vice-*` (el video de fixture, que ya no se usa
porque el fondo de Vice es un shader — `viceInk.ts` hoy, `viceHaze.ts` en el
momento de este handoff — se pueden borrar, sigue pendiente de decision del
usuario a fecha de `2026-08-04-vice-fondo-tinta`). Cualquier fallo distinto de
esos 12 lo has introducido tu.

`npm run build` y `npm run lint` estan en verde. Manten ambos en verde.

## Requisitos que no se negocian

- TypeScript strict, cero `any`.
- Cero emojis. Comentarios en espanol **sin tildes**, siguiendo el estilo denso
  del repo: explican POR QUE, no QUE.
- `prefers-reduced-motion`: el leader no debe montarse siquiera (hoy se gatea en
  `main.ts` y ademas hay un cinturon en CSS que lo fuerza a `display:none`).
- El leader es decoracion: `aria-hidden`, `pointer-events: none`, nunca bloquea
  scroll ni clics.
- Pase lo que pase, **la pagina no puede quedarse en negro**. Los dos seguros
  existen por eso.
- Verificacion visual obligatoria antes de dar nada por hecho: desktop
  1440x900 y movil 390x844.
