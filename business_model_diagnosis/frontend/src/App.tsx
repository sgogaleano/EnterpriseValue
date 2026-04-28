import { useState } from "react"
import { CanvasSection } from "@/components/dashboard/CanvasSection"
import { KpiSection } from "@/components/dashboard/KpiSection"
import { OverviewSection } from "@/components/dashboard/OverviewSection"
import { OwnershipSection } from "@/components/dashboard/OwnershipSection"
import { SearchSection } from "@/components/dashboard/SearchSection"
import { StickyHeader } from "@/components/dashboard/StickyHeader"
import { SummarySection } from "@/components/dashboard/SummarySection"
import { DiagnosisResult } from "@/components/dashboard/DiagnosisResult"
import { Card, CardContent } from "@/components/ui/card"
import { runDiagnosis, type DiagnosisResponse } from "@/lib/api"
import type { Language } from "@/data/translations"

export default function App() {
  const [language, setLanguage] = useState<Language>("en")
  const [companyInput, setCompanyInput] = useState("")
  const [tickerInput, setTickerInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DiagnosisResponse | null>(null)

  const handleResearch = async () => {
    const name = companyInput.trim()
    if (!name || loading) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await runDiagnosis({
        company_name: name,
        ticker: tickerInput.trim() || undefined
      })
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <StickyHeader language={language} onLanguageChange={setLanguage} />
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-4 py-8 md:px-8">
        <OverviewSection language={language} />
        <SearchSection
          language={language}
          companyInput={companyInput}
          tickerInput={tickerInput}
          loading={loading}
          onCompanyChange={setCompanyInput}
          onTickerChange={setTickerInput}
          onResearch={handleResearch}
        />

        {error && (
          <Card className="border-rose-200">
            <CardContent className="pt-6">
              <p className="text-sm font-medium text-rose-600">{language === "en" ? "Error" : "Error"}: {error}</p>
            </CardContent>
          </Card>
        )}

        {result && !loading && <DiagnosisResult language={language} result={result} />}

        {!result && !loading && (
          <>
            <SummarySection language={language} />
            <OwnershipSection language={language} />
            <CanvasSection language={language} />
            <KpiSection language={language} />
          </>
        )}
      </main>
    </div>
  )
}
