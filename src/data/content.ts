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
  githubAvatar: string;
  /** Estado visible en la ficha: la senal mas util para quien recluta. */
  availability: string;
  since: string;
}

export const identity: Identity = {
  name: "Aoshi Blanco Sanz",
  role: "Desarrollador Full Stack",
  headline: "Construyo sistemas que aguantan producción, no demos.",
  subheadline: "Uso Python, React y Django para llevar datos reales a interfaces reales.",
  location: "Caracas, Venezuela",
  email: "a.blanco1501@gmail.com",
  phone: "+58 424 228 1033",
  github: "https://github.com/Aoshi346",
  githubAvatar: "https://avatars.githubusercontent.com/u/137179835?v=4",
  availability: "Abierto a oportunidades",
  since: "2021",
};

export interface Stat {
  value: string;
  label: string;
}

/** Lectura instantanea antes de leer una sola frase. */
export const stats: Stat[] = [
  { value: "2021", label: "Desde" },
  { value: "9.º", label: "Semestre" },
  { value: "4", label: "Proyectos" },
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
    period: "2021 — presente (9no semestre)",
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
    period: "Ago 2025 — presente",
    description:
      "Desarrollo herramientas internas para el equipo de conocimiento al cliente, con foco en datos de campañas a gran escala.",
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

export const skillGroups: SkillGroup[] = [
  {
    label: "Frontend",
    items: [
      {
        name: "React",
        slug: "react",
        detail: "Lo uso para interfaces con estado complejo, como los paneles de campañas de Telefónica.",
      },
      {
        name: "TypeScript",
        slug: "typescript",
        detail: "Tipo todo lo que escribo: menos bugs en producción, más confianza al refactorizar.",
      },
      {
        name: "Tailwind CSS",
        slug: "tailwindcss",
        detail: "Mi forma de maquetar rápido sin perder consistencia visual entre componentes.",
      },
      {
        name: "Vite",
        slug: "vite",
        detail: "El bundler que uso por defecto: arranque instantáneo y builds que no me hacen esperar.",
      },
    ],
  },
  {
    label: "Backend",
    items: [
      {
        name: "Python",
        slug: "python",
        detail: "Mi lenguaje base para automatizar, procesar datos y construir APIs.",
      },
      {
        name: "Django",
        slug: "django",
        detail: "Lo elijo cuando necesito un backend robusto rápido: ORM, admin y auth ya resueltos.",
      },
      {
        name: "MySQL",
        slug: "mysql",
        detail: "Donde persisto los datos a gran escala de las plataformas que construyo.",
      },
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

export const secondarySkills: SkillItem[] = [
  { name: "JavaScript", slug: "javascript", detail: "Base de todo lo que corre en el navegador." },
  { name: "HTML", slug: "html5", detail: "Estructura semántica antes que nada." },
  { name: "CSS", slug: "css", detail: "Lo que no cubre Tailwind, lo escribo a mano." },
  { name: "C", slug: "c", detail: "Donde aprendí a pensar en memoria y punteros." },
  { name: "C++", slug: "cplusplus", detail: "Para el editor de texto nativo y proyectos de sistemas." },
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
    period: "Ago 2025 — hoy",
    status: "Sistema interno de empresa",
    problem:
      "Las campañas pasaban por varias áreas antes de salir, cada una con sus aprobaciones, y el seguimiento vivía repartido entre correos y hojas de cálculo. Nadie podía responder de un vistazo en qué punto estaba cada una.",
    solution:
      "Un sistema interno que reúne el recorrido completo de la campaña en un mismo sitio: quién la creó, qué aprobaciones lleva, si ya se configuró y cuándo salió. Con permisos por rol y tableros que muestran cómo va todo sin tener que preguntar.",
    stack: ["Python", "Django", "TypeScript", "React", "Vite"],
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
    gallery: [
      { src: "/media/obra/hyprfinance-resumen.webp", caption: "Resumen financiero" },
      { src: "/media/obra/hyprfinance-movimientos.webp", caption: "Registro de movimientos" },
    ],
    privateProject: true,
  },
  {
    slug: "ciberseg",
    title: "Proyecto CiberSeg",
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
    gallery: [{ src: "/media/obra/editor-interfaz.webp", caption: "Interfaz en GTK4" }],
    link: {
      label: "Ver repositorio",
      href: "https://github.com/Aoshi346/Text-Editor-Application",
    },
  },
];
