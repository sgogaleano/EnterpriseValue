import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { companyData } from "@/data/dashboard-data"
import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

export function CanvasSection({ language }: { language: Language }) {
  const t = translations[language]
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sectionCanvas}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
          {companyData.canvas.map((item) => (
            <div key={item.titleEn} className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h3 className="mb-2 text-sm font-semibold text-slate-900">{language === "en" ? item.titleEn : item.titleEs}</h3>
              <p className="text-sm text-slate-700">{item.content}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}