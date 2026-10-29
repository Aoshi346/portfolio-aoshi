/**
 * Contenido centralizado del portfolio, en español.
 * Estructura de datos pensada para que anadir un locale nuevo (ej. `content.en.ts`)
 * sea cuestion de copiar este shape, no de tocar componentes.
 */

export interface Identity {
  name: string;
  role: string;
  headline: string;
  subheadline: string;
  location: string;
  email: string;
  phone: string;
  github: string;
  /** Perfil de LinkedIn: para mucha gente de seleccion es la via de contacto
   *  por defecto, antes que el correo. */
  linkedin: string;
  githubAvatar: string;
  /** Estado visible en la ficha: la senal mas util para quien recluta. */
  availability: string;
  /** Situacion actual. No se deriva de `experience[0]`: la pasantia termino en
   *  mayo de 2026 y esa entrada sigue siendo historial valido, no el presente. */
  now: string;
  since: string;
  /**
   * La frase de la escena de cierre. Elegida por el autor entre once
   * alternativas: corta, en el lado de quien lee y sin prometer un plazo de
   * respuesta, que es la promesa mas facil de incumplir.
   */
  invitation: string;
}

export const identity: Identity = {
  name: "Aoshi Blanco Sanz",
  role: "Desarrollador Full Stack",
  headline: "Construyo sistemas que aguantan producción, no demos.",
  subheadline: "Caracas. Full stack. Desde 2021.",
  location: "Caracas, Venezuela",
  email: "a.blanco1501@gmail.com",
  phone: "+58 424 228 1033",
  github: "https://github.com/Aoshi346",
  linkedin: "https://www.linkedin.com/in/aoshi-blanco-sanz-14119b2b7",
  githubAvatar: "https://avatars.githubusercontent.com/u/137179835?v=4",
  availability: "Disponible para proyectos",
  now: "Full Stack Developer",
  since: "2021",
  invitation: "Cuéntame tu idea.",
};

export interface Stat {
  value: string;
  label: string;
}

/** Lectura instantanea antes de leer una sola frase. */
export const stats: Stat[] = [
  { value: "2021", label: "Desde" },
  // Sin el ordinal volado: a tamano de cartel el "º" de
  // Passion One se separa tanto de la cifra que se lee como otro caracter.
  { value: "10", label: "Semestre" },
  { value: "5", label: "Proyectos" },
  { value: "1", label: "En producción" },
];

export const aboutCopy: string[] = [
  "Llevo datos reales a interfaces que la gente usa todos los días.",
  "La mayoría de mis repositorios son privados. Aquí están los públicos que mejor muestran cómo pienso y qué construyo.",
];

export interface Education {
  degree: string;
  institution: string;
  period: string;
  note?: string;
}

export const education: Education[] = [
  {
    degree: "Ingeniería de Sistemas",
    institution: "Universidad Santa María",
    period: "2021 — presente (10.º semestre)",
  },
];

export interface Experience {
  role: string;
  organization: string;
  period: string;
  description: string;
}

export const experience: Experience[] = [
  {
    role: "Pasante B2C Conocimiento al Cliente",
    organization: "Telefónica Venezuela",
    period: "Ago 2025 — May 2026",
    description:
      "Desarrollé herramientas internas para el equipo de conocimiento al cliente, con foco en datos de campañas a gran escala.",
  },
];

export type SkillItem = {
  name: string;
  /** slug del paquete `simple-icons` para este icono */
  slug: string;
  /** por qué lo uso, en primera persona */
  detail: string;
};

export type SkillGroup = {
  label: string;
  items: SkillItem[];
};

/*
 * El reparto del cartel, en cuatro bloques de 8, 5, 5 y 5. Las frases son
 * cortas y de longitud pareja a proposito: el pie del cartel reserva altura
 * fija, y frases dispares obligarian a reservar hueco para la mas larga y
 * dejarlo medio vacio casi siempre. Por eso se acortaron tambien las doce que
 * ya existian.
 *
 * El corte es por LO QUE SON las cosas, no por su tamano. Antes habia seis
 * bloques y tres de ellos tenian 2, 3 y 2 nombres: en un cartel eso se lee
 * como sobras. Se descarto la consolidacion obvia — fundir "Escritorio",
 * "Herramientas" e "IA" en un bloque de 7 — porque el rotulo resultante
 * mentiria: GTK4 no es una herramienta con la que trabajas, es
 * aquello con lo que construyes la interfaz, al mismo nivel que React. De ahi
 * "Interfaz", que cubre web y escritorio, y un "Herramientas" honesto donde
 * las cinco entradas si son cosas con las que se trabaja.
 *
 * Coste asumido: "IA" pierde rotulo propio. Se acepta porque queda junto a lo
 * que de verdad se le parece, y porque el rotulo propio no compensaba un
 * bloque de dos nombres.
 *
 * Cada `slug` tiene que estar registrado en `src/utils/icons.ts`:
 * `getIconMarkup()` lanza excepcion con un slug desconocido, y lo hace al
 * montar la bandeja de Creditos.
 */
export const skillGroups: SkillGroup[] = [
  {
    label: "Interfaz",
    items: [
      { name: "React", slug: "react", detail: "Interfaces con estado complejo." },
      { name: "TypeScript", slug: "typescript", detail: "Tipado en todo lo que escribo." },
      { name: "Next.js", slug: "nextdotjs", detail: "Para apps con rutas y render en servidor." },
      { name: "Tailwind CSS", slug: "tailwindcss", detail: "Maquetación rápida y consistente." },
      { name: "Vite", slug: "vite", detail: "Mi bundler por defecto." },
      { name: "GSAP", slug: "gsap", detail: "Las animaciones y las transiciones." },
      { name: "GTK4", slug: "gtk", detail: "Interfaces nativas en C." },
    ],
  },
  {
    label: "Backend y datos",
    items: [
      { name: "Python", slug: "python", detail: "Automatización, datos y APIs." },
      { name: "Django", slug: "django", detail: "Backend robusto: ORM, admin y auth." },
      { name: "FastAPI", slug: "fastapi", detail: "APIs en Python, validadas por sus tipos." },
      { name: "SQLAlchemy", slug: "sqlalchemy", detail: "El acceso a datos cuando no hay Django." },
      { name: "Node.js", slug: "nodedotjs", detail: "JavaScript fuera del navegador." },
      { name: "PostgreSQL", slug: "postgresql", detail: "Relacional, con transacciones de verdad." },
      { name: "MySQL", slug: "mysql", detail: "Donde persisto los datos." },
      { name: "RxDB", slug: "rxdb", detail: "Datos locales en el navegador." },
    ],
  },
  {
    label: "Lenguajes base",
    items: [
      { name: "JavaScript", slug: "javascript", detail: "Base de todo lo que corre en el navegador." },
      { name: "HTML", slug: "html5", detail: "Estructura semántica antes que nada." },
      { name: "CSS", slug: "css", detail: "Lo que no cubre Tailwind, lo escribo a mano." },
      { name: "C", slug: "c", detail: "Donde aprendí a pensar en memoria y punteros." },
      { name: "C++", slug: "cplusplus", detail: "Sistemas y aplicaciones nativas." },
    ],
  },
  {
    label: "Herramientas",
    items: [
      { name: "Git", slug: "git", detail: "Control de versiones en todo lo que hago." },
      { name: "GitHub", slug: "github", detail: "Donde publico y comparto el código." },
      { name: "n8n", slug: "n8n", detail: "Automatizo tareas repetitivas entre servicios." },
      { name: "Claude Code", slug: "claude", detail: "Asistente en terminal para escribir y revisar código." },
      { name: "Gemini CLI", slug: "googlegemini", detail: "Consultas rápidas desde la terminal." },
    ],
  },
];

export interface FocusArea {
  title: string;
  detail: string;
}

/** Pares titulo/detalle de "En que me enfoco", especificos de Aoshi. */
export const focusAreas: FocusArea[] = [
  {
    title: "Datos a gran escala",
    detail: "Que la consulta siga siendo rápida con volumen real",
  },
  {
    title: "Interfaces que aguantan",
    detail: "Estado complejo sin romperse en producción",
  },
];

/**
 * La fila Stack de la ficha de Quien soy: las cuatro piezas que mas pesan y
 * una linea con las que siguen. Los nombres tienen que existir en
 * `skillGroups`; la ficha descarta en silencio cualquiera que no este.
 *
 * `principal` es tambien lo que la bandeja de Stack pinta en el tono de
 * acento: las dos escenas dicen lo mismo con una sola lista.
 */
export const stackDestacado = {
  principal: ["Python", "Django", "React", "TypeScript"],
  resto: "También Next.js, Node.js, MySQL y n8n",
} as const;

export interface GalleryShot {
  /** Ruta bajo /public. Capturas reales del proyecto. */
  src: string;
  caption: string;
}

export interface CaseStudy {
  title: string;
  tag: string;
  /** Linea de cartel: una frase, grande y ligera. */
  lead: string;
  role: string;
  period?: string;
  status: string;
  problem: string;
  solution: string;
  stack: string[];
  /**
   * Lo transversal: control de versiones y asistentes con los que se
   * construyo el proyecto, no con lo que el producto funciona. Va aparte de
   * `stack` porque `stack` se pinta literal en la ficha de obra
   * (`caelestiaObraEditorial.ts`) y meter aqui cuatro nombres repetidos
   * identicos en los cinco proyectos alargaba esa linea sin distinguir nada:
   * Git no separa un proyecto de otro.
   *
   * Solo alimenta el cruce "Aparece en" de los creditos. La ficha de obra
   * sigue mostrando unicamente `stack`, y eso es la decision, no un olvido.
   */
  tooling?: string[];
  gallery: GalleryShot[];
  link?: { label: string; href: string };
  privateProject?: boolean;
}

export const caseStudies: CaseStudy[] = [
  {
    title: "Parallax",
    tag: "Tesis de grado",
    lead: "Probar una campaña con una audiencia simulada antes de pagarla.",
    role: "Diseño, desarrollo e investigación",
    period: "Abr 2026 — hoy",
    status: "Trabajo Especial de Grado · en curso",
    problem:
      "Para saber si un anuncio en redes va a funcionar, lo normal es invertir el presupuesto y medir después. Si sale mal, el dinero ya se gastó.",
    solution:
      "Un instrumento de medición para mi Trabajo Especial de Grado: genera una audiencia de agentes con modelos de lenguaje, la expone al anuncio en Instagram, Facebook, TikTok y YouTube, y mide cómo cambia su opinión ronda a ronda, en público y en conversaciones a solas, antes de invertir nada.",
    stack: ["Python", "FastAPI", "SQLAlchemy", "React", "TypeScript", "Vite", "Tailwind CSS"],
    tooling: ["Git", "GitHub", "Claude Code"],
    gallery: [
      { src: "/media/obra/parallax-instagram.webp", caption: "El anuncio y los agentes comentándolo en Instagram" },
      { src: "/media/obra/parallax-brief.webp", caption: "Nueva corrida: el brief de la campaña" },
    ],
    privateProject: true,
  },
  {
    title: "Vela",
    tag: "E-commerce",
    lead: "Una boutique de skincare servida desde el servidor, con React donde hace falta.",
    role: "Diseño y desarrollo",
    status: "Repositorio privado",
    problem:
      "Una tienda de cuidado facial en Caracas necesita que el catálogo cargue rápido y aparezca en los buscadores, sin renunciar a un carrito y un checkout que respondan al momento.",
    solution:
      "Django genera las páginas en el servidor, que es lo que hace rápido el catálogo y lo deja indexable, y React con TypeScript entra solo en las piezas interactivas: el carrito, el checkout, la galería de producto y los formularios. Pago contra entrega en dólares, como se compra en Caracas.",
    stack: ["Python", "Django", "PostgreSQL", "React", "TypeScript", "Vite", "Tailwind CSS", "GSAP"],
    tooling: ["Git", "GitHub", "Claude Code"],
    gallery: [
      { src: "/media/obra/vela-carrito.webp", caption: "Carrito" },
      { src: "/media/obra/vela-checkout.webp", caption: "Checkout" },
    ],
    privateProject: true,
  },
  {
    title: "TesisFar",
    tag: "Gestión académica",
    lead: "El ciclo completo del TEG, en un mismo lugar.",
    role: "Diseño y desarrollo",
    status: "Repositorio público",
    problem:
      "Coordinar el Trabajo Especial de Grado entre estudiantes, tutores y jurados es, en la mayoría de universidades, un proceso manual y fragmentado por correo y hojas de cálculo.",
    solution:
      "Construí una plataforma que gestiona el ciclo completo del TEG: entregas de avances, coordinación estudiantes–tutores y evaluación por jurados, todo en un mismo lugar.",
    stack: ["TypeScript", "Next.js"],
    tooling: ["Git", "GitHub", "Claude Code", "Gemini CLI"],
    gallery: [
      { src: "/media/obra/teg-planificacion.webp", caption: "Planificación de defensas con su tribunal" },
      { src: "/media/obra/teg-entregas.webp", caption: "Entregas de avances del estudiante" },
    ],
    link: { label: "Ver repositorio", href: "https://github.com/Aoshi346/teg-web-app" },
  },
  {
    title: "HyprFinance",
    tag: "Finanzas personales",
    lead: "Tus cuentas, solo en tu equipo.",
    role: "Diseño y desarrollo",
    period: "Jun 2026 — hoy",
    status: "Repositorio privado",
    problem:
      "Llevar las cuentas cuando manejas varias monedas termina en hojas de cálculo que nunca cuadran, porque el cambio de ayer no es el de hoy. Y las aplicaciones que lo resuelven te piden subir todo tu historial financiero a un servidor de otro.",
    solution:
      "Una aplicación donde tus datos se quedan en tu propio equipo, cifrados, y la nube solo sirve para sincronizar entre tus dispositivos. Guarda cada movimiento con el cambio del día en que ocurrió, así el total nunca miente, y reparte solo las compras a cuotas para que sepas qué te queda por pagar.",
    stack: ["TypeScript", "React", "RxDB", "GSAP", "Zustand"],
    tooling: ["Git", "GitHub", "Claude Code", "Gemini CLI"],
    gallery: [
      { src: "/media/obra/hyprfinance-analitica.webp", caption: "Analítica del mes" },
      { src: "/media/obra/hyprfinance-panel.webp", caption: "Panel general" },
    ],
    privateProject: true,
  },
  {
    title: "Editor de texto",
    tag: "Programación de sistemas",
    lead: "Un editor de texto escrito desde cero, en C.",
    role: "Proyecto académico individual",
    period: "2024",
    status: "Repositorio público",
    problem:
      "Un ejercicio de fin de curso con una lista cerrada de requisitos: corrector ortográfico, varias páginas, cifrado y descifrado del contenido, guardado en archivo y una interfaz gráfica de verdad.",
    solution:
      "Un editor completo en C con interfaz en GTK4, donde el bloque de texto crece según se escribe, el corrector señala las palabras y el contenido puede cifrarse antes de guardarlo.",
    stack: ["C", "GTK4"],
    tooling: ["Git", "GitHub"],
    gallery: [{ src: "/media/obra/editor-interfaz.webp", caption: "Interfaz en GTK4" }],
    link: {
      label: "Ver repositorio",
      href: "https://github.com/Aoshi346/Text-Editor-Application",
    },
  },
];

export interface ContactChannel {
  key: "correo" | "linkedin" | "telefono" | "github";
  label: string;
  /** Lo que se lee en pantalla. No siempre es el href: LinkedIn muestra el nombre. */
  value: string;
  href: string;
  external: boolean;
}

/**
 * Las cuatro barras de la carta de ajuste, en orden de encuadre. El correo va
 * primero porque es la via principal, y su barra es la unica en magenta.
 */
export const contactChannels: ContactChannel[] = [
  {
    key: "correo",
    label: "Correo",
    value: identity.email,
    href: `mailto:${identity.email}`,
    external: false,
  },
  {
    key: "linkedin",
    label: "LinkedIn",
    value: identity.name,
    href: identity.linkedin,
    external: true,
  },
  {
    key: "telefono",
    label: "Teléfono",
    value: identity.phone,
    // Sin espacios ni guiones: el marcador del movil no los tolera.
    href: `tel:${identity.phone.replace(/[^+\d]/g, "")}`,
    external: false,
  },
  {
    key: "github",
    label: "GitHub",
    value: "Aoshi346",
    href: identity.github,
    external: true,
  },
];

export interface SceneEntry {
  id: string;
  /** Nombre de cine. Es lo que se lee grande en el indice. */
  label: string;
  /** Lo que la escena contiene, en llano. Cierra el hallazgo de que
   *  "Fundido" no comunica "contacto" a quien llega de fuera. */
  blurb: string;
}

// "Stack" y "Contacto" sustituyen a "Créditos" y "Fundido" por decisión de
// Aoshi (repaso de interfaces 2026-09-05).
export const sceneIndex: SceneEntry[] = [
  { id: "hero", label: "Título", blurb: "Desarrollador full stack" },
  { id: "quien-es", label: "Quién soy", blurb: "Trayectoria y cifras" },
  { id: "obra", label: "Obra", blurb: "Cinco proyectos" },
  { id: "creditos", label: "Stack", blurb: "Con qué construyo" },
  { id: "contacto", label: "Contacto", blurb: "Hablemos de tu proyecto" },
];
