export type DiagnosisPayload = {
  company_name: string
  ticker?: string
  skip_market?: boolean
}

export type OwnershipPayload = {
  ceo: string
  major_shareholders: string[]
}

export type DashboardPayload = {
  name: string
  ticker: string | null
  summary: {
    industry: string
    headquarters: string
    market_cap: string
    employees: string
    sector: string
  }
  canvas: Record<string, string>
  financial_text: string
  market_text: string
}

export type KpiRow = {
  kpi: string
  value: string
  sectorAvg: string
  variation: number
}

export type DiagnosisResponse = {
  company_name: string
  ticker: string | null
  cached: boolean
  canvas_text: string
  financial_text: string
  market_text: string
  updated_at: number | null
  dashboard: DashboardPayload
  kpis: KpiRow[]
  ownership: OwnershipPayload
}

const BASE = "/api"

export async function runDiagnosis(payload: DiagnosisPayload): Promise<DiagnosisResponse> {
  const res = await fetch(`${BASE}/diagnose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: `HTTP ${res.status}` }))
    throw new Error(body.error ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<DiagnosisResponse>
}

export async function checkCached(
  companyName: string
): Promise<{ found: boolean; company_name?: string; ticker?: string; updated_at?: number }> {
  const res = await fetch(`${BASE}/cached?company=${encodeURIComponent(companyName)}`)
  if (!res.ok) return { found: false }
  return res.json()
}
