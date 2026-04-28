import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { companyData } from "@/data/dashboard-data"
import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

export function SummarySection({ language }: { language: Language }) {
  const t = translations[language]
  return (
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
            {companyData.summary.map((row) => (
              <TableRow key={row.labelEn}>
                <TableCell className="font-medium">{language === "en" ? row.labelEn : row.labelEs}</TableCell>
                <TableCell>{row.value}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}