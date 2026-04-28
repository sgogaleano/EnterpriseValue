export type SummaryItem = {
  labelEn: string
  labelEs: string
  value: string
}

export type CanvasItem = {
  titleEn: string
  titleEs: string
  content: string
}

export type KpiItem = {
  kpi: string
  value: string
  sectorAvg: string
  variation: number
}

export type CompanyData = {
  name: string
  ticker: string
  summary: SummaryItem[]
  ceo: { name: string; href: string }
  shareholders: { name: string; href: string }[]
  canvas: CanvasItem[]
  kpis: KpiItem[]
}

export const companySuggestions = ["Microsoft", "Apple", "NVIDIA", "Amazon", "Alphabet"]

export const companyData: CompanyData = {
  name: "Microsoft Corporation",
  ticker: "MSFT",
  summary: [
    { labelEn: "Industry", labelEs: "Industria", value: "Software & Cloud" },
    { labelEn: "Headquarters", labelEs: "Sede", value: "Redmond, Washington, USA" },
    { labelEn: "Market Cap", labelEs: "Capitalización", value: "$3.1T" },
    { labelEn: "Employees", labelEs: "Empleados", value: "221,000" },
    { labelEn: "Fiscal Year", labelEs: "Año Fiscal", value: "Jul - Jun" }
  ],
  ceo: {
    name: "Satya Nadella",
    href: "https://www.microsoft.com/en-us/about/leadership/satya-nadella"
  },
  shareholders: [
    { name: "Vanguard Group", href: "https://investor.vanguard.com" },
    { name: "BlackRock", href: "https://www.blackrock.com" }
  ],
  canvas: [
    { titleEn: "Key Partners", titleEs: "Socios Clave", content: "Global integrators, OEM partners, and ecosystem channels." },
    { titleEn: "Key Activities", titleEs: "Actividades Clave", content: "Platform R&D, cloud operations, AI innovation, and security." },
    { titleEn: "Value Propositions", titleEs: "Propuesta de Valor", content: "Secure, scalable productivity and cloud for enterprise and consumer." },
    { titleEn: "Customer Relationships", titleEs: "Relación con Clientes", content: "Enterprise contracts, support tiers, and self-service subscriptions." },
    { titleEn: "Customer Segments", titleEs: "Segmentos de Clientes", content: "Enterprises, SMBs, developers, governments, and consumers." },
    { titleEn: "Key Resources", titleEs: "Recursos Clave", content: "Global data centers, engineering talent, IP portfolio, and brand trust." },
    { titleEn: "Channels", titleEs: "Canales", content: "Direct sales, partners, marketplaces, and online subscriptions." },
    { titleEn: "Cost Structure", titleEs: "Estructura de Costes", content: "Infrastructure capex, talent, compliance, and go-to-market programs." },
    { titleEn: "Revenue Streams", titleEs: "Fuentes de Ingresos", content: "SaaS, cloud usage, licensing, support services, and enterprise agreements." }
  ],
  kpis: [
    { kpi: "Revenue Growth (YoY)", value: "15.2%", sectorAvg: "10.1%", variation: 5.1 },
    { kpi: "Gross Margin", value: "69.4%", sectorAvg: "63.0%", variation: 6.4 },
    { kpi: "Operating Margin", value: "44.6%", sectorAvg: "32.9%", variation: 11.7 },
    { kpi: "ROIC", value: "27.3%", sectorAvg: "18.6%", variation: 8.7 }
  ]
}