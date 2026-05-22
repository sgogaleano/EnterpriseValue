import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import type { DiagnosisResponse } from "@/lib/api"
import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

type Props = {
  language: Language
  result: DiagnosisResponse
}

const CANVAS_ORDER = [
  "Key Partnerships",
  "Key Activities",
  "Value Propositions",
  "Customer Relationships",
  "Customer Segments",
  "Key Resources",
  "Channels",
  "Cost Structure",
  "Revenue Streams"
]

const CANVAS_TITLES: Record<string, { en: string; es: string }> = {
  "Key Partnerships": { en: "Key Partners", es: "Socios Clave" },
  "Key Activities": { en: "Key Activities", es: "Actividades Clave" },
  "Value Propositions": { en: "Value Propositions", es: "Propuesta de Valor" },
  "Customer Relationships": { en: "Customer Relationships", es: "Relación con Clientes" },
  "Customer Segments": { en: "Customer Segments", es: "Segmentos de Clientes" },
  "Key Resources": { en: "Key Resources", es: "Recursos Clave" },
  Channels: { en: "Channels", es: "Canales" },
  "Cost Structure": { en: "Cost Structure", es: "Estructura de Costes" },
  "Revenue Streams": { en: "Revenue Streams", es: "Fuentes de Ingresos" }
}

const CANVAS_PREVIEW_CHARS = 280

function AiTextBlock({ text }: { text: string }) {
  if (!text) return null
  return <div className="whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm leading-relaxed text-slate-800">{text}</div>
}

function CanvasBlockContent({ language, text }: { language: Language; text: string }) {
  const [expanded, setExpanded] = useState(false)
  const normalized = (text || "").trim()
  if (!normalized) {
    return <p className="text-sm whitespace-pre-wrap text-slate-700">N/A</p>
  }
  const shouldTruncate = normalized.length > CANVAS_PREVIEW_CHARS
  const displayText = shouldTruncate && !expanded ? `${normalized.slice(0, CANVAS_PREVIEW_CHARS).trimEnd()}...` : normalized

  return (
    <div className="flex flex-col gap-2">
      <p className="text-sm whitespace-pre-wrap text-slate-700">{displayText}</p>
      {shouldTruncate && (
        <button className="self-start text-xs font-medium text-blue-600" onClick={() => setExpanded((prev) => !prev)} type="button">
          {expanded ? (language === "en" ? "Show less" : "Ver menos") : (language === "en" ? "Read more" : "Ver más")}
        </button>
      )}
    </div>
  )
}

export function DiagnosisResult({ language, result }: Props) {
  const t = translations[language]
  const formattedDate = result.updated_at
    ? new Date(result.updated_at * 1000).toLocaleDateString(language === "en" ? "en-US" : "es-ES", {
        year: "numeric",
        month: "short",
        day: "numeric"
      })
    : null

  const dashboard = result.dashboard
  const ownership = result.ownership

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-2xl">{result.company_name}</CardTitle>
            {result.ticker && <p className="mt-1 text-sm text-slate-500">[{result.ticker}]</p>}
          </div>
          <div className="flex flex-col items-end gap-1">
            {result.cached ? <Badge variant="secondary">{language === "en" ? "Cached" : "En caché"}</Badge> : <Badge>{language === "en" ? "Fresh analysis" : "Análisis nuevo"}</Badge>}
            {formattedDate && <p className="text-xs text-slate-500">{language === "en" ? "Updated" : "Actualizado"}: {formattedDate}</p>}
          </div>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t.sectionOwnership}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-700">
            {t.ownershipTextPrefix} CEO {ownership.ceo || "N/A"}
            {", "}
            {(ownership.major_shareholders && ownership.major_shareholders.length > 0 ? ownership.major_shareholders : ["N/A"]).join(", ")}
            .
          </p>
        </CardContent>
      </Card>


      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>{t.sectionSummary}</CardTitle>
          <Badge>{t.publicBadge}</Badge>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t.summaryField}</TableHead>
                <TableHead>{t.summaryValue}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">{language === "en" ? "Industry" : "Industria"}</TableCell>
                <TableCell>{dashboard.summary.industry}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">{language === "en" ? "Headquarters" : "Sede"}</TableCell>
                <TableCell>{dashboard.summary.headquarters}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">{language === "en" ? "Market Cap" : "Capitalización"}</TableCell>
                <TableCell>{dashboard.summary.market_cap}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">{language === "en" ? "Employees" : "Empleados"}</TableCell>
                <TableCell>{dashboard.summary.employees}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">{language === "en" ? "Sector" : "Sector"}</TableCell>
                <TableCell>{dashboard.summary.sector}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t.sectionCanvas}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
            {CANVAS_ORDER.map((key) => (
              <div key={key} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <h3 className="mb-2 text-sm font-semibold text-slate-900">{language === "en" ? CANVAS_TITLES[key].en : CANVAS_TITLES[key].es}</h3>
                <CanvasBlockContent language={language} text={dashboard.canvas[key] || ""} />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {result.kpis.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t.sectionKpi}</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t.kpiColName}</TableHead>
                  <TableHead>{t.kpiColValue}</TableHead>
                  <TableHead>{t.kpiColSector}</TableHead>
                  <TableHead>{t.kpiColVariation}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.kpis.map((row) => (
                  <TableRow key={row.kpi}>
                    <TableCell className="font-medium">{row.kpi}</TableCell>
                    <TableCell>{row.value}</TableCell>
                    <TableCell>{row.sectorAvg}</TableCell>
                    <TableCell className={row.variation >= 0 ? "text-emerald-600" : "text-rose-600"}>
                      {row.variation >= 0 ? "+" : ""}
                      {row.variation.toFixed(1)}%
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {result.financial_text && (
        <Card>
          <CardHeader>
            <CardTitle>{language === "en" ? "Financial Analysis" : "Análisis Financiero"}</CardTitle>
          </CardHeader>
          <CardContent>
            <AiTextBlock text={result.financial_text} />
          </CardContent>
        </Card>
      )}

      {result.market_text && (
        <Card>
          <CardHeader>
            <CardTitle>{language === "en" ? "Market & Equity Analysis" : "Análisis de Mercado y Renta Variable"}</CardTitle>
          </CardHeader>
          <CardContent>
            <AiTextBlock text={result.market_text} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
