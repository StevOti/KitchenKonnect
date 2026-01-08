import React, { useState } from 'react'
import { useAuth } from '../AuthProvider'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const auth = useAuth()

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    try {
      await auth.login(username, password)
      window.location.href = '/'
    } catch (err) {
      setError(err.message || 'Login failed')
    }
  }

  return (
    <div className="page auth-page">
      <main className="container">
        <h2>Login</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error">{error}</div>}
          <label>
            Username
            <input value={username} onChange={e => setUsername(e.target.value)} />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
          </label>
          <button type="submit" className="site-btn">Login</button>
        </form>
      </main>
    </div>
  )
}
