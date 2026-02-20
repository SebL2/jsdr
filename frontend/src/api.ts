import { API_URLS } from './config/api'

export type City = { id: string; name: string; [key: string]: any }

async function parseResponse(res: Response) {
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return await res.json()
  return await res.text()
}

export async function getHello(): Promise<string> {
  const res = await fetch(API_URLS.HELLO)
  if (!res.ok) throw new Error(`getHello failed: ${res.status}`)
  const body = await parseResponse(res)
  if (typeof body === 'string') return body
  if (body && typeof body === 'object') {
    if ('message' in body) return String((body as any).message)
    return JSON.stringify(body)
  }
  return String(body)
}

export async function getEndpoints(): Promise<string[]> {
  const res = await fetch(API_URLS.ENDPOINTS)
  if (!res.ok) throw new Error(`getEndpoints failed: ${res.status}`)
  const data = await res.json()
  return Array.isArray(data) ? data : []
}

export async function getCities(): Promise<City[]> {
  const res = await fetch(API_URLS.CITIES)
  if (!res.ok) throw new Error(`getCities failed: ${res.status}`)
  const data = await res.json()
  return Array.isArray(data) ? data : []
}
