import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { companyData } from "@/data/dashboard-data"
import type { Language } from "@/data/translations"
import { translations } from "@/data/translations"

export function KpiSection({ language }: { language: Language }) {
  const t = translations[language]
  return (
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
            {companyData.kpis.map((row) => (
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
  )
}