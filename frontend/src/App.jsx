import React, { useEffect, useState } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'

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
    const payload = decodeJwt(token)
    if (payload && payload.exp) {
      const now = Math.floor(Date.now() / 1000)
      if (payload.exp < now) {
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
      const apiFetch = (await import('./apiClient')).default
      const headers = {}
      const looksLikeJwt = typeof token === 'string' && token.split('.').length >= 2
      if (looksLikeJwt) {
        headers['Authorization'] = `Bearer ${token}`
      } else {
        headers['Authorization'] = `Token ${token}`
      }
      const res = await apiFetch(`${API_BASE}/api/auth/me/`, { headers })
      if (!res.ok) return false
      const data = await res.json()
      setUser(data)
      return true
    } catch (e) {
      return false
    }
  }

  useEffect(() => {
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
    try { localStorage.setItem('__KK_TOKEN', token) } catch (e) {}
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
    <div>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register onLogin={handleLogin} />} />
          <Route path="/home" element={<Home user={user} onLogout={handleLogout} />} />
        </Routes>
      )}
    </div>
  )
}
