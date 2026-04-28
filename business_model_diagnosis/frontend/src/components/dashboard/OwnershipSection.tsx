import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { companyData } from "@/data/dashboard-data"
import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

export function OwnershipSection({ language }: { language: Language }) {
  const t = translations[language]
  return (
    <Card>
      <CardHeader>
        <CardTitle>{t.sectionOwnership}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-slate-700">
          {t.ownershipTextPrefix} CEO{" "}
          <a className="text-blue-600" href={companyData.ceo.href} target="_blank" rel="noreferrer">
            {companyData.ceo.name}
          </a>
          {", "}
          {companyData.shareholders.map((shareholder, index) => (
            <span key={shareholder.name}>
              <a className="text-blue-600" href={shareholder.href} target="_blank" rel="noreferrer">
                {shareholder.name}
              </a>
              {index < companyData.shareholders.length - 1 ? ", " : ""}
            </span>
          ))}
          .
        </p>
      </CardContent>
    </Card>
  )
}