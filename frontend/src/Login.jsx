import React, {useState} from 'react'
import { useNavigate, Link } from 'react-router-dom'

const API_BASE = 'http://127.0.0.1:8000'

export default function Login({onLogin}) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

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
      // support multiple token response formats: {'token':...}, {'access':...}
      const token = data.token || data.access || data.key
      if (!token) throw new Error('no token in response')
      window.__KK_TOKEN = token
      try { localStorage.setItem('__KK_TOKEN', token) } catch(e) {}
      // If parent handler returns a promise, await validation result
      if (onLogin) {
        const result = onLogin(token)
        if (result && typeof result.then === 'function') {
          const valid = await result
          if (valid) navigate('/home')
        } else {
          // fallback: navigate to home
          navigate('/home')
        }
      } else {
        navigate('/home')
      }
      setMessage('Token received. Redirecting to Home...')
    } catch (err) {
      setMessage('Login error: ' + err)
    }
  }

  return (
    <div style={{maxWidth:640}}>
      <h2>Login</h2>
      <input placeholder="username" value={username} onChange={e => setUsername(e.target.value)} />
      <input placeholder="password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <div style={{marginTop:8, display:'flex', gap:8}}>
        <button onClick={login}>Login</button>
        <Link to="/register"><button>Register</button></Link>
      </div>

      <div style={{marginTop:12}}>
        <strong>Status:</strong>
        <div style={{whiteSpace:'pre-wrap'}}>{message}</div>
      </div>
    </div>
  )
}
