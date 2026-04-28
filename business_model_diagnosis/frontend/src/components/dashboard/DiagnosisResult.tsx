import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { DiagnosisResponse } from "@/lib/api"
import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

type Props = {
  language: Language
  result: DiagnosisResponse
}

function AiTextBlock({ text }: { text: string }) {
  if (!text) return null
  return <div className="whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm leading-relaxed text-slate-800">{text}</div>
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
          <CardTitle>{t.sectionCanvas}</CardTitle>
        </CardHeader>
        <CardContent>
          <AiTextBlock text={result.canvas_text} />
        </CardContent>
      </Card>

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
