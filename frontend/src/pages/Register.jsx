import React, { useState } from 'react'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    try {
      const apiFetch = (await import('../apiClient')).default
      const res = await apiFetch('/api/auth/register/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      })
      if (!res.ok) {
        const txt = await res.text()
        setError(txt || 'Registration failed')
        return
      }
      // after register, redirect to login
      window.location.href = '/login'
    } catch (e) {
      setError('Network error')
    }
  }

  return (
    <div className="page auth-page">
      <main className="container">
        <h2>Register</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error">{error}</div>}
          <label>
            Username
            <input value={username} onChange={e => setUsername(e.target.value)} />
          </label>
          <label>
            Email
            <input value={email} onChange={e => setEmail(e.target.value)} />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
          </label>
          <button type="submit" className="site-btn">Register</button>
        </form>
      </main>
    </div>
  )
}
