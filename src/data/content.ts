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
  now: "Freelancer",
  since: "2021",
};

export interface Stat {
  value: string;
  label: string;
}

/** Lectura instantanea antes de leer una sola frase. */
export const stats: Stat[] = [
  { value: "2021", label: "Desde" },
  // Sin el ordinal volado: a tamano de cartel (3.4rem en Vice) el "º" de
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
  {
    degree: "100 Days of Code: Python Pro Bootcamp",
    institution: "Udemy — Dra. Angela Yu",
    period: "En curso",
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
 * El reparto del cartel, en seis bloques. Las frases son cortas y de longitud
 * pareja a proposito: el pie del cartel reserva altura fija, y frases dispares
 * obligarian a reservar hueco para la mas larga y dejarlo medio vacio casi
 * siempre. Por eso se acortaron tambien las doce que ya existian.
 *
 * Cada `slug` tiene que estar registrado en `src/utils/icons.ts`:
 * `getIconMarkup()` lanza excepcion con un slug desconocido, y lo hace en los
 * tres temas, no solo en Vice.
 */
export const skillGroups: SkillGroup[] = [
  {
    label: "Frontend",
    items: [
      { name: "React", slug: "react", detail: "Interfaces con estado complejo." },
      { name: "Next.js", slug: "nextdotjs", detail: "Para apps con rutas y render en servidor." },
      { name: "TypeScript", slug: "typescript", detail: "Tipado en todo lo que escribo." },
      { name: "Tailwind CSS", slug: "tailwindcss", detail: "Maquetación rápida y consistente." },
      { name: "Vite", slug: "vite", detail: "Mi bundler por defecto." },
      { name: "GSAP", slug: "gsap", detail: "Las animaciones y las transiciones." },
    ],
  },
  {
    label: "Backend y datos",
    items: [
      { name: "Python", slug: "python", detail: "Automatización, datos y APIs." },
      { name: "Django", slug: "django", detail: "Backend robusto: ORM, admin y auth." },
      { name: "Node.js", slug: "nodedotjs", detail: "JavaScript fuera del navegador." },
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
    label: "Escritorio",
    items: [
      { name: "Electron", slug: "electron", detail: "Aplicaciones de escritorio con tecnología web." },
      { name: "GTK4", slug: "gtk", detail: "Interfaces nativas en C." },
    ],
  },
  {
    label: "Herramientas",
    items: [
      { name: "Git", slug: "git", detail: "Control de versiones en todo lo que hago." },
      { name: "GitHub", slug: "github", detail: "Donde publico y comparto el código." },
      { name: "n8n", slug: "n8n", detail: "Automatizo tareas repetitivas entre servicios." },
    ],
  },
  {
    label: "IA",
    items: [
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

export interface GalleryShot {
  /** Ruta bajo /public. Capturas reales del proyecto. */
  src: string;
  caption: string;
}

export interface CaseStudy {
  slug: string;
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
   * (`sections/obra/projectScene.ts`) y meter aqui cuatro nombres repetidos
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
    slug: "echoplan",
    title: "EchoPlan",
    tag: "Gestión de campañas",
    lead: "Todas las campañas, un solo tablero.",
    role: "Desarrollo full stack",
    period: "Ago 2025 — May 2026",
    status: "Sistema interno · Telefónica Venezuela",
    problem:
      "Las campañas pasaban por varias áreas antes de salir, cada una con sus aprobaciones, y el seguimiento vivía repartido entre correos y hojas de cálculo. Nadie podía responder de un vistazo en qué punto estaba cada una.",
    solution:
      "Un sistema interno que reúne el recorrido completo de la campaña en un mismo sitio: quién la creó, qué aprobaciones lleva, si ya se configuró y cuándo salió. Con permisos por rol y tableros que muestran cómo va todo sin tener que preguntar.",
    stack: ["Python", "Django", "TypeScript", "React", "Vite"],
    tooling: ["Git", "GitHub", "Claude Code", "Gemini CLI"],
    gallery: [
      { src: "/media/obra/echoplan-tablero.webp", caption: "Tablero de campañas" },
      { src: "/media/obra/echoplan-aprobaciones.webp", caption: "Estado de aprobaciones" },
    ],
    privateProject: true,
  },
  {
    slug: "teg-web-app",
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
      { src: "/media/obra/teg-entregas.webp", caption: "Entregas de avances" },
      { src: "/media/obra/teg-jurados.webp", caption: "Asignación de jurados" },
    ],
    link: { label: "Ver repositorio", href: "https://github.com/Aoshi346/teg-web-app" },
  },
  {
    slug: "hyprfinance",
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
      { src: "/media/obra/hyprfinance-resumen.webp", caption: "Resumen financiero" },
      { src: "/media/obra/hyprfinance-movimientos.webp", caption: "Registro de movimientos" },
    ],
    privateProject: true,
  },
  {
    slug: "ciberseg",
    title: "WatchDog",
    tag: "Ciberseguridad",
    lead: "Las herramientas de seguridad, en una sola aplicación.",
    role: "Desarrollo principal",
    period: "Sep — Oct 2025",
    status: "Repositorio público",
    problem:
      "Revisar la seguridad de un equipo obliga a saltar entre herramientas sueltas, cada una con su propia forma de usarse, y casi todas pensadas para quien ya sabe de seguridad.",
    solution:
      "Una aplicación de escritorio que reúne en un mismo sitio el análisis de vulnerabilidades, la gestión de contraseñas, el monitor de red y las herramientas de análisis forense, con una interfaz que no exige ser experto para entenderla.",
    stack: ["JavaScript", "Electron", "Python"],
    tooling: ["Git", "GitHub", "Claude Code", "Gemini CLI"],
    gallery: [
      { src: "/media/obra/ciberseg-panel.webp", caption: "Panel de la suite" },
      { src: "/media/obra/ciberseg-vulnerabilidades.webp", caption: "Análisis de vulnerabilidades" },
    ],
    link: { label: "Ver repositorio", href: "https://github.com/Aoshi346/Proyecto-CiberSeg" },
  },
  {
    slug: "text-editor",
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
