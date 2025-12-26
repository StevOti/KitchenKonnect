import React, {useState} from 'react'
import { Link } from 'react-router-dom'

const API_BASE = 'http://127.0.0.1:8000'

export default function Register() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')

  async function ensureCsrf() {
    try {
      const res = await fetch(`${API_BASE}/api/csrf/`, { credentials: 'include' })
      if (!res.ok) return null
      const data = await res.json()
      return data.csrfToken || null
    } catch (e) {
      return null
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
      setMessage('Registered — you can now login.')
    } catch (err) {
      setMessage('Register error: ' + err)
    }
  }

  return (
    <div style={{maxWidth:640}}>
      <h2>Register</h2>
      <input placeholder="username" value={username} onChange={e => setUsername(e.target.value)} />
      <input placeholder="email" value={email} onChange={e => setEmail(e.target.value)} />
      <input placeholder="password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <div style={{marginTop:8}}>
        <button onClick={register}>Register</button>
        <Link to="/"><button style={{marginLeft:8}}>Back to Login</button></Link>
      </div>
      <div style={{marginTop:12}}>
        <strong>Status:</strong>
        <div style={{whiteSpace:'pre-wrap'}}>{message}</div>
      </div>
    </div>
  )
}
