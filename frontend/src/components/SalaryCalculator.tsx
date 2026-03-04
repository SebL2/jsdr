import { useState, useEffect } from 'react'
import { getCostOfLiving, getSalaryAdjustment, type SalaryResult } from '../api'

export default function SalaryCalculator() {
  const [cities, setCities] = useState<string[]>([])
  const [fromCity, setFromCity] = useState('')
  const [toCity, setToCity] = useState('')
  const [salary, setSalary] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SalaryResult | null>(null)

  // Fetch city list on mount
  useEffect(() => {
    getCostOfLiving()
      .then((data) => {
        const names = Object.keys(data).sort()
        setCities(names)
        if (names.length >= 2) {
          setFromCity(names[0])
          setToCity(names[1])
        }
      })
      .catch((e) => setError(e?.message || String(e)))
  }, [])

  const handleCalculate = async () => {
    const sal = parseFloat(salary)
    if (isNaN(sal) || sal < 0) {
      setError('Please enter a valid salary')
      return
    }
    if (!fromCity || !toCity) {
      setError('Please select both cities')
      return
    }
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const res = await getSalaryAdjustment(sal, fromCity, toCity)
      setResult(res)
    } catch (e: any) {
      setError(e?.message || String(e))
    } finally {
      setLoading(false)
    }
  }

  const fmt = (n: number) =>
    n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })

  return (
    <div className="card salary-calculator">
      <h2>💰 Salary Adjustment Calculator</h2>
      <p style={{ color: '#aaa', fontSize: '0.9rem', margin: '0 0 1rem' }}>
        Compare purchasing power between cities
      </p>

      <div className="salary-form">
        <div className="salary-row">
          <label htmlFor="salary-input">Annual Salary</label>
          <input
            id="salary-input"
            type="number"
            min="0"
            placeholder="e.g. 100000"
            value={salary}
            onChange={(e) => setSalary(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCalculate()}
          />
        </div>

        <div className="salary-row">
          <label htmlFor="from-city">From</label>
          <select
            id="from-city"
            value={fromCity}
            onChange={(e) => setFromCity(e.target.value)}
          >
            {cities.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="salary-row">
          <label htmlFor="to-city">To</label>
          <select
            id="to-city"
            value={toCity}
            onChange={(e) => setToCity(e.target.value)}
          >
            {cities.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <button
          onClick={handleCalculate}
          disabled={loading || !salary || !fromCity || !toCity}
        >
          {loading ? 'Calculating…' : 'Calculate'}
        </button>
      </div>

      {error && <p style={{ color: '#ff6b6b', marginTop: '1rem' }}>⚠ {error}</p>}

      {result && (
        <div className="salary-result">
          <div className="salary-result-main">
            <span className="salary-label">Equivalent Salary in {result.to_city}</span>
            <span className="salary-amount">{fmt(result.adjusted_salary)}</span>
          </div>
          <div className="salary-breakdown">
            <div className="salary-detail">
              <span>Original ({result.from_city})</span>
              <strong>{fmt(result.original_salary)}</strong>
            </div>
            <div className="salary-detail">
              <span>COL Index — {result.from_city}</span>
              <strong>{result.col_from}</strong>
            </div>
            <div className="salary-detail">
              <span>COL Index — {result.to_city}</span>
              <strong>{result.col_to}</strong>
            </div>
            <div className="salary-detail">
              <span>Difference</span>
              <strong style={{ color: result.difference >= 0 ? '#ff6b6b' : '#51cf66' }}>
                {result.difference >= 0 ? '+' : ''}{fmt(result.difference)} ({result.percentage_change > 0 ? '+' : ''}{result.percentage_change}%)
              </strong>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
