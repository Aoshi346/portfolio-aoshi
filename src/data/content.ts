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
};

export const aboutCopy: string[] = [
  "Soy desarrollador full stack enfocado en Python, React, Django y TypeScript: llevo datos reales a interfaces que la gente usa todos los días.",
  "Curso noveno semestre de Ingeniería de Sistemas en la Universidad Santa María, en Caracas, mientras trabajo como pasante en Telefónica Venezuela.",
  "La mayoría de mis repositorios son privados. En este portfolio reúno los públicos que mejor muestran cómo pienso y qué construyo.",
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

export const secondarySkills: SkillItem[] = [
  { name: "JavaScript", slug: "javascript", detail: "Base de todo lo que corre en el navegador." },
  { name: "HTML", slug: "html5", detail: "Estructura semántica antes que nada." },
  { name: "CSS", slug: "css", detail: "Lo que no cubre Tailwind, lo escribo a mano." },
  { name: "C", slug: "c", detail: "Donde aprendí a pensar en memoria y punteros." },
  { name: "C++", slug: "cplusplus", detail: "Para el editor de texto nativo y proyectos de sistemas." },
];

export interface CaseStudy {
  slug: string;
  title: string;
  tag: string;
  problem: string;
  solution: string;
  stack: string[];
  link?: { label: string; href: string };
  privateProject?: boolean;
}

export const caseStudies: CaseStudy[] = [
  {
    slug: "campaign-analytics",
    title: "Plataforma de estadísticas de campañas",
    tag: "Telefónica Venezuela · Pasantía",
    problem:
      "El equipo necesitaba planificar campañas y extraer sus estadísticas de forma centralizada, en lugar de reconstruir el mismo análisis manualmente cada vez.",
    solution:
      "Lideré una plataforma web integral durante la pasantía: backend en Django + MySQL para manejar datos a gran escala, frontend en React + TypeScript + Vite + Tailwind, y conexión MySQL–frontend a través de un servidor Linux remoto.",
    stack: ["Django", "MySQL", "React", "TypeScript", "Vite", "Tailwind CSS", "Linux"],
    privateProject: true,
  },
  {
    slug: "teg-web-app",
    title: "teg-web-app",
    tag: "Gestión académica",
    problem:
      "Coordinar el Trabajo Especial de Grado entre estudiantes, tutores y jurados es, en la mayoría de universidades, un proceso manual y fragmentado por correo y hojas de cálculo.",
    solution:
      "Construí una plataforma que gestiona el ciclo completo del TEG: entregas de avances, coordinación estudiantes–tutores y evaluación por jurados, todo en un mismo lugar.",
    stack: ["TypeScript", "Next.js"],
    link: { label: "Ver repositorio", href: "https://github.com/Aoshi346/teg-web-app" },
  },
  {
    slug: "text-editor",
    title: "Text-Editor-Application",
    tag: "Software de sistemas",
    problem:
      "La mayoría de editores de texto de portfolio son ejercicios triviales de CRUD. El reto era construir uno con funcionalidad real, cerca del sistema.",
    solution:
      "Escribí un editor de texto nativo en C con interfaz GTK4: corrector ortográfico, cifrado y descifrado de archivos, y exportación a TXT.",
    stack: ["C", "GTK4"],
    link: {
      label: "Ver repositorio",
      href: "https://github.com/Aoshi346/Text-Editor-Application",
    },
  },
  {
    slug: "ciberseg",
    title: "Proyecto CiberSeg",
    tag: "Suite de escritorio",
    problem:
      "Los profesionales de ciberseguridad suelen depender de herramientas de línea de comandos dispersas para tareas cotidianas: escaneo de vulnerabilidades, gestión de contraseñas, monitoreo de red.",
    solution:
      "Construí una suite de escritorio con Electron que centraliza esas herramientas en una interfaz moderna, con aislamiento de contexto habilitado y comunicación IPC segura entre procesos.",
    stack: ["Electron", "JavaScript", "IPC seguro"],
    link: { label: "Ver repositorio", href: "https://github.com/Aoshi346/Proyecto-CiberSeg" },
  },
];
