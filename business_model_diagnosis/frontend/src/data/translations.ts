export type Language = "en" | "es"

export const translations = {
  en: {
    appTitle: "Company Value Assessment",
    overviewTitle: "Company Value Assessment Dashboard",
    overviewIntro:
      "A structured workspace to evaluate company fundamentals, ownership profile, business model design, and financial performance vs. sector benchmarks.",
    sectionSearch: "Search",
    searchPlaceholder: "Search public companies",
    researchButton: "Research",
    suggestionsLabel: "Suggested Companies",
    sectionSummary: "Company Summary",
    sectionOwnership: "Ownership",
    ownershipTextPrefix: "Leadership and major ownership references:",
    sectionCanvas: "Business Model Canvas",
    sectionKpi: "Financial KPI Table",
    summaryField: "Field",
    summaryValue: "Value",
    kpiColName: "KPI",
    kpiColValue: "Value",
    kpiColSector: "Sector Avg",
    kpiColVariation: "% Var",
    languageEn: "EN",
    languageEs: "ES",
    publicBadge: "Public"
  },
  es: {
    appTitle: "Evaluación de Valor Empresarial",
    overviewTitle: "Panel de Evaluación de Valor Empresarial",
    overviewIntro:
      "Un espacio estructurado para evaluar fundamentos de la empresa, perfil de propiedad, diseño del modelo de negocio y desempeño financiero frente al sector.",
    sectionSearch: "Búsqueda",
    searchPlaceholder: "Buscar empresas públicas",
    researchButton: "Investigar",
    suggestionsLabel: "Empresas sugeridas",
    sectionSummary: "Resumen de la Empresa",
    sectionOwnership: "Propiedad",
    ownershipTextPrefix: "Referencias de liderazgo y principales accionistas:",
    sectionCanvas: "Lienzo de Modelo de Negocio",
    sectionKpi: "Tabla de KPI Financieros",
    summaryField: "Campo",
    summaryValue: "Valor",
    kpiColName: "KPI",
    kpiColValue: "Valor",
    kpiColSector: "Prom. Sector",
    kpiColVariation: "% Var",
    languageEn: "EN",
    languageEs: "ES",
    publicBadge: "Pública"
  }
} as const

export type Translation = (typeof translations)[Language]