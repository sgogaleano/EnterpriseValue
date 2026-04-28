import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

export function OverviewSection({ language }: { language: Language }) {
  const t = translations[language]
  return (
    <section>
      <h1 className="text-3xl font-semibold text-slate-900">{t.overviewTitle}</h1>
      <p className="mt-3 text-slate-500">{t.overviewIntro}</p>
    </section>
  )
}