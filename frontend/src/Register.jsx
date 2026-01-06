import React, {useState} from 'react'
import { showToast } from './Toasts'
import { Link, useNavigate } from 'react-router-dom'

const API_BASE = 'http://127.0.0.1:8000'

export default function Register({onLogin}) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [desiredRole, setDesiredRole] = useState('regular')
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

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
        body: JSON.stringify({ username, password, email, desired_role: desiredRole }),
        credentials: 'include'
      })
      const data = await res.json()
      if (!res.ok) throw new Error(JSON.stringify(data))
      // registration returned payload; try to auto-login with returned token
      // store tokens if returned (support JWT pair or DRF token)
      const token = data.access || data.token || data.key
      if (data.refresh) {
        try { localStorage.setItem('__KK_REFRESH', data.refresh) } catch (e) {}
      }
      if (token) {
        try {
          window.__KK_TOKEN = token
          try { localStorage.setItem('__KK_TOKEN', token) } catch(e) {}
          if (onLogin) {
            const r = onLogin(token)
            if (r && typeof r.then === 'function') await r
          }
          setMessage('Registered. Logging in...')
          showToast({ message: 'Registered and logged in', type: 'success' })
          navigate('/home')
          return
        } catch (e) {
          // fallthrough to showing success message
        }
      }
      setMessage('Registered — you can now login.')
      showToast({ message: 'Registration complete', type: 'success' })
    } catch (err) {
      setMessage('Register error: ' + err)
      showToast({ message: 'Register error: ' + String(err), type: 'error' })
    }
  }

  return (
    <div style={{maxWidth:640}}>
      <h2>Register</h2>
      <input placeholder="username" value={username} onChange={e => setUsername(e.target.value)} />
      <input placeholder="email" value={email} onChange={e => setEmail(e.target.value)} />
      <input placeholder="password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <div style={{marginTop:8}}>
        <label style={{marginRight:8}}>Register as:</label>
        <select value={desiredRole} onChange={e => setDesiredRole(e.target.value)}>
          <option value="regular">Regular</option>
          <option value="nutritionist">Nutritionist</option>
          <option value="regulator">Regulator</option>
          <option value="admin">Admin</option>
        </select>
      </div>
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
