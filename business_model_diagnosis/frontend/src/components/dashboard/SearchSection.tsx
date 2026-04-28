import { Search, Loader2 } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { companySuggestions } from "@/data/dashboard-data"
import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

type SearchSectionProps = {
  language: Language
  companyInput: string
  tickerInput: string
  loading: boolean
  onCompanyChange: (v: string) => void
  onTickerChange: (v: string) => void
  onResearch: () => void
}

export function SearchSection({
  language,
  companyInput,
  tickerInput,
  loading,
  onCompanyChange,
  onTickerChange,
  onResearch
}: SearchSectionProps) {
  const t = translations[language]
  const [showSuggestions, setShowSuggestions] = useState(false)
  const filtered = companySuggestions.filter((s) => s.toLowerCase().includes(companyInput.toLowerCase()))

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sectionSearch}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <Input
                className="pl-10"
                placeholder={t.searchPlaceholder}
                value={companyInput}
                onChange={(e) => {
                  onCompanyChange(e.target.value)
                  setShowSuggestions(true)
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
                onKeyDown={(e) => e.key === "Enter" && !loading && onResearch()}
              />
              {showSuggestions && companyInput && filtered.length > 0 && (
                <ul className="absolute z-10 mt-1 w-full rounded-xl border border-slate-200 bg-white py-1 shadow-md">
                  {filtered.map((item) => (
                    <li
                      key={item}
                      className="cursor-pointer px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                      onMouseDown={() => {
                        onCompanyChange(item)
                        setShowSuggestions(false)
                      }}
                    >
                      {item}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <Input
              className="w-full sm:w-32"
              placeholder="Ticker (e.g. AAPL)"
              value={tickerInput}
              onChange={(e) => onTickerChange(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === "Enter" && !loading && onResearch()}
            />

            <Button onClick={onResearch} disabled={loading || !companyInput.trim()} className="sm:self-start">
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {language === "en" ? "Analyzing…" : "Analizando…"}
                </>
              ) : (
                t.researchButton
              )}
            </Button>
          </div>

          {!companyInput && (
            <div className="flex flex-wrap gap-2">
              <span className="text-xs text-slate-500">{t.suggestionsLabel}:</span>
              {companySuggestions.map((item) => (
                <button key={item} type="button" className="rounded-full border border-slate-200 bg-white px-3 py-0.5 text-xs text-slate-700 hover:bg-slate-50" onClick={() => onCompanyChange(item)}>
                  {item}
                </button>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
