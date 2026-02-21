import { useState, useEffect } from 'react'

const API_BASE = '/api'

export default function App() {
  const [cities, setCities] = useState([])
  const [citiesLoading, setCitiesLoading] = useState(true)
  const [city, setCity] = useState('')
  const [price, setPrice] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/cities`)
      .then((r) => r.json())
      .then((data) => {
        setCities(data.cities || [])
        if (data.cities?.length && !city) setCity(data.cities[0])
      })
      .catch(() => setCities([]))
      .finally(() => setCitiesLoading(false))
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    setLoading(true)
    fetch(`${API_BASE}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ city: city.trim(), price: price.trim() }),
    })
      .then(async (r) => {
        const data = await r.json()
        if (!r.ok) {
          setError(data.error || `Error ${r.status}`)
          setResult(null)
          return
        }
        setResult(data)
        setError(data.error || null)
      })
      .catch((err) => setError(err.message || 'Request failed'))
      .finally(() => setLoading(false))
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Zomato AI</h1>
        <p>Restaurant recommendations by city and budget</p>
      </header>

      <form onSubmit={handleSubmit} className="form">
        <div className="field">
          <label htmlFor="city">City / Locality</label>
          {citiesLoading ? (
            <span className="hint">Loading cities...</span>
          ) : cities.length > 0 ? (
            <select
              id="city"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              required
            >
              <option value="">Select city</option>
              {cities.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          ) : (
            <input
              id="city"
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="e.g. btm, koramangala"
              required
            />
          )}
        </div>
        <div className="field">
          <label htmlFor="price">Price</label>
          <input
            id="price"
            type="text"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            placeholder="e.g. 500, 500-1000, Low, Medium, High"
            required
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Finding recommendations...' : 'Get recommendations'}
        </button>
      </form>

      {error && (
        <div className="message error" role="alert">
          {error}
        </div>
      )}

      {result?.ok && result.empty && (
        <div className="message empty">
          {result.message || 'No recommendations found. Try a higher budget or different city.'}
        </div>
      )}

      {result?.ok && result.recommendations?.length > 0 && (
        <section className="results">
          <h2>Recommendations</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Name</th>
                  <th>Rating</th>
                  <th>Votes</th>
                  <th>Cost (for 2)</th>
                  <th>Cuisines</th>
                  <th>Locality</th>
                  <th>Address</th>
                </tr>
              </thead>
              <tbody>
                {result.recommendations.map((r, i) => (
                  <tr key={i}>
                    <td>{i + 1}</td>
                    <td>{r.name ?? '-'}</td>
                    <td>{r.rating ?? r.rate ?? '-'}</td>
                    <td>{r.votes ?? '-'}</td>
                    <td>{r.cost_for_two ?? '-'}</td>
                    <td>{r.cuisines ?? '-'}</td>
                    <td>{r.locality ?? '-'}</td>
                    <td>{r.address ?? '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}
