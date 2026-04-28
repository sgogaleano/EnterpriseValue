import { Button } from "@/components/ui/button"
import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

type StickyHeaderProps = {
  language: Language
  onLanguageChange: (language: Language) => void
}

export function StickyHeader({ language, onLanguageChange }: StickyHeaderProps) {
  const t = translations[language]
  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-slate-50/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-4 md:px-8">
        <p className="text-lg font-semibold text-slate-900">{t.appTitle}</p>
        <div className="flex items-center rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
          <Button
            variant="ghost"
            size="sm"
            className={language === "en" ? "bg-slate-100 text-slate-900" : "text-slate-500"}
            onClick={() => onLanguageChange("en")}
          >
            {t.languageEn}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className={language === "es" ? "bg-slate-100 text-slate-900" : "text-slate-500"}
            onClick={() => onLanguageChange("es")}
          >
            {t.languageEs}
          </Button>
        </div>
      </div>
    </header>
  )
}