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
  const body = await res.json()

  if (Array.isArray(body)) return body

  if (body && typeof body === 'object') {
    const citiesField = (body as any).Cities
    if (Array.isArray(citiesField)) return citiesField
    if (citiesField && typeof citiesField === 'object') {
      return Object.entries(citiesField).map(([id, v]) => ({ id, ...(v as any) })) as City[]
    }
  }

  return []
}

export async function getCityExists(cityId: string): Promise<boolean> {
  const res = await fetch(API_URLS.CITY_EXISTS(cityId))
  if (!res.ok) throw new Error(`getCityExists failed: ${res.status}`)
  const body = await parseResponse(res)
  if (body && typeof body === 'object' && typeof (body as any).exists === 'boolean') {
    return (body as any).exists
  }
  return false
}

export async function getCity(cityId: string): Promise<City> {
  const res = await fetch(API_URLS.CITY_BY_ID(cityId))
  if (!res.ok) {
    if (res.status === 404) throw new Error('City not found')
    throw new Error(`getCity failed: ${res.status}`)
  }
  const body = await res.json()
  const cityData = body?.Cities ?? body
  return { id: cityId, ...cityData } as City
}
