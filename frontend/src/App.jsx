import React, {useEffect, useState} from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import Login from './Login'
import Register from './Register'
import Home from './Home'
import AdminUsers from './AdminUsers'
import AdminVerifications from './AdminVerifications'
import { PublicPage, AdminOnly, NutritionistOnly, RegulatorOnly } from './RolePages'
import { Link } from 'react-router-dom'
import ToastContainer from './Toasts'

const API_BASE = 'http://127.0.0.1:8000'

function decodeJwt(token) {
  try {
    const parts = token.split('.')
    if (parts.length < 2) return null
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
    return payload
  } catch (e) {
    return null
  }
}

export default function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  async function validateToken(token) {
    // If token looks like JWT, check exp
    const payload = decodeJwt(token)
    if (payload && payload.exp) {
      const now = Math.floor(Date.now() / 1000)
      if (payload.exp < now) {
        // token expired; try refresh if available
        const refresh = localStorage.getItem('__KK_REFRESH') || window.__KK_REFRESH
        if (refresh) {
          try {
            const rres = await fetch(`${API_BASE}/api/auth/token/refresh/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh })
            })
            if (rres.ok) {
              const rdata = await rres.json()
              if (rdata.access) {
                token = rdata.access
                window.__KK_TOKEN = token
                try { localStorage.setItem('__KK_TOKEN', token) } catch (e) {}
                if (rdata.refresh) try { localStorage.setItem('__KK_REFRESH', rdata.refresh) } catch (e) {}
              } else {
                return false
              }
            } else {
              return false
            }
          } catch (e) {
            return false
          }
        } else {
          return false
        }
      }
    }
    try {
      const headers = {}
      // Auto-detect token type: JWTs have dot-separated parts.
      // Send `Bearer` for JWT access tokens, `Token` for DRF TokenAuth keys.
      const looksLikeJwt = typeof token === 'string' && token.split('.').length >= 2
      if (looksLikeJwt) headers['Authorization'] = `Bearer ${token}`
      else headers['Authorization'] = `Token ${token}`
      const res = await fetch(`${API_BASE}/api/auth/me/`, { headers })
      if (!res.ok) return false
      const data = await res.json()
      setUser(data)
      return true
    } catch (e) {
      return false
    }
  }

  useEffect(() => {
    // Try to restore token from localStorage
    const token = localStorage.getItem('__KK_TOKEN') || window.__KK_TOKEN
    if (token) {
      validateToken(token).then(valid => {
        if (!valid) {
          localStorage.removeItem('__KK_TOKEN')
          window.__KK_TOKEN = null
          setUser(null)
        }
        setLoading(false)
      })
    } else {
      setLoading(false)
    }
  }, [])

  function handleLogin(token) {
    window.__KK_TOKEN = token
    localStorage.setItem('__KK_TOKEN', token)
    // validate and fetch profile — return promise so callers can await
    return validateToken(token).then(valid => {
      if (valid) navigate('/home')
      return valid
    })
  }

  function handleLogout() {
    localStorage.removeItem('__KK_TOKEN')
    window.__KK_TOKEN = null
    setUser(null)
    navigate('/')
  }

  return (
    <div style={{fontFamily: 'sans-serif', padding: 20}}>
      <h1>KitchenKonnect — Auth Test</h1>
      <div style={{marginBottom:12}}>
        <Link to="/home" style={{marginRight:8}}>Home</Link>
        <Link to="/public" style={{marginRight:8}}>Public</Link>
        <Link to="/admin/users" style={{marginRight:8}}>Manage Users</Link>
        <Link to="/admin/verifications" style={{marginRight:8}}>Verifications</Link>
        <Link to="/admin-only" style={{marginRight:8}}>Admin Page</Link>
        <Link to="/nutritionist-only" style={{marginRight:8}}>Nutritionist Page</Link>
        <Link to="/regulator-only" style={{marginRight:8}}>Regulator Page</Link>
      </div>
      <ToastContainer />
      {loading ? (
        <div>Loading...</div>
      ) : (
        <Routes>
          <Route path="/" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register onLogin={handleLogin} />} />
          <Route path="/home" element={<Home user={user} onLogout={handleLogout} />} />
          <Route path="/admin/users" element={<AdminUsers user={user} />} />
          <Route path="/admin/verifications" element={<AdminVerifications user={user} />} />
          <Route path="/admin-only" element={<AdminOnly user={user} />} />
          <Route path="/nutritionist-only" element={<NutritionistOnly user={user} />} />
          <Route path="/regulator-only" element={<RegulatorOnly user={user} />} />
          <Route path="/public" element={<PublicPage />} />
        </Routes>
      )}
    </div>
  )
}
