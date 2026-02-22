import { useEffect, useState } from 'react'
import { getCities, type City} from '../api'
import { API_URLS } from '../config/api'

export default function CitiesCard() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [cities, setCities] = useState<City[]>([])

  useEffect(() => {
    let mounted = true

    const load = async () => {
      setLoading(true)
      try {
        let data = await getCities()

        if (mounted) setCities(Array.isArray(data) ? data : [])
      } catch (e: any) {
        if (mounted) setError(e?.message || String(e))
      } finally {
        if (mounted) setLoading(false)
      }
    }

    load()
    return () => {
      mounted = false
    }
  }, [])

  return (
    <div className="card">
      <h2>Cities</h2>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {!loading && !error && (
        (cities.length === 0) ? (
          <p>No cities found</p>
        ) : (
          <ul>
            {cities.map((c) => (
              <li key={c.id ?? c.name}>
                {c.name} {c.state_code ? `(${c.state_code})` : ''}
              </li>
            ))}
          </ul>
        )
      )}
    </div>
  )
}
