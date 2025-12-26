import React, {useState} from 'react'

const API_BASE = 'http://127.0.0.1:8000'

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'))
  return match ? decodeURIComponent(match[2]) : null
}

export default function AuthTest({onLogin}) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [me, setMe] = useState(null)

  async function ensureCsrf() {
    // Request a JSON CSRF token endpoint which also sets the csrftoken cookie
    try {
      const res = await fetch(`${API_BASE}/api/csrf/`, { credentials: 'include' })
      if (!res.ok) return null
      const data = await res.json()
      return data.csrfToken || getCookie('csrftoken')
    } catch (e) {
      return getCookie('csrftoken')
    }
  }

  async function register() {
    setMessage('Registering...')
    try {
      const csrftoken = await ensureCsrf()
      const res = await fetch(`${API_BASE}/api/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken || '' },
        body: JSON.stringify({ username, password, email }),
        credentials: 'include'
      })
      const data = await res.json()
      if (!res.ok) throw new Error(JSON.stringify(data))
      setMessage('Registered — now you can "Login" using session auth via fetch.')
    } catch (err) {
      setMessage('Register error: ' + err)
    }
  }

  async function login() {
    setMessage('Requesting token...')
    try {
      const res = await fetch(`${API_BASE}/api/auth/token/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(JSON.stringify(data))
      // store token persistently and notify parent
      window.__KK_TOKEN = data.token
      try { localStorage.setItem('__KK_TOKEN', data.token) } catch(e) {}
      if (onLogin) onLogin(data.token)
      setMessage('Token received. Redirecting to Home...')
    } catch (err) {
      setMessage('Login error: ' + err)
    }
  }

  function logoutLocal() {
    window.__KK_TOKEN = null
    try { localStorage.removeItem('__KK_TOKEN') } catch(e) {}
    setMe(null)
    setMessage('Local token cleared')
  }

  async function getMe() {
    setMessage('Fetching /api/auth/me/')
    try {
      const headers = {}
      if (window.__KK_TOKEN) headers['Authorization'] = `Token ${window.__KK_TOKEN}`
      const res = await fetch(`${API_BASE}/api/auth/me/`, { headers })
      if (!res.ok) {
        const d = await res.text()
        throw new Error(d || res.statusText)
      }
      const data = await res.json()
      setMe(data)
      setMessage('Fetched profile')
    } catch (err) {
      setMessage('Get /me error: ' + err)
    }
  }

  return (
    <div style={{maxWidth: 640}}>
      <div style={{display: 'grid', gap: 8}}>
        <input placeholder="username" value={username} onChange={e => setUsername(e.target.value)} />
        <input placeholder="email" value={email} onChange={e => setEmail(e.target.value)} />
        <input placeholder="password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        <div style={{display: 'flex', gap: 8}}>
          <button onClick={register}>Register</button>
          <button onClick={login}>Login (token)</button>
          <button onClick={getMe}>Get /me</button>
          <button onClick={logoutLocal}>Clear token</button>
        </div>
      </div>

      <div style={{marginTop: 12}}>
        <strong>Status:</strong>
        <div style={{whiteSpace: 'pre-wrap'}}>{message}</div>
      </div>

      {me && (
        <div style={{marginTop: 12}}>
          <h3>Profile</h3>
          <pre>{JSON.stringify(me, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
