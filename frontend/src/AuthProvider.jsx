import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import { registerAccessGetter } from './apiClient'

const AuthContext = createContext(null)

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [access, setAccess] = useState(null)
  const [loading, setLoading] = useState(true)
  const accessRef = useRef(null)

  const fetchAccessFromServer = useCallback(async () => {
    try {
      const apiFetch = (await import('./apiClient')).default
      const res = await apiFetch('/api/auth/cookie/refresh/', { method: 'POST' })
      if (!res.ok) {
        setAccess(null)
        return null
      }
      const data = await res.json()
      if (data.access) {
        setAccess(data.access)
        return data.access
      }
      return null
    } catch (e) {
      setAccess(null)
      return null
    }
  }, [])

  useEffect(() => {
    // Try refresh on mount to obtain an access token from cookie
    (async () => {
      await fetchAccessFromServer()
      setLoading(false)
    })()
    // register getter so apiClient can read latest access
    registerAccessGetter(() => accessRef.current)
  }, [fetchAccessFromServer])

  // keep ref updated so getter returns latest value
  useEffect(() => { accessRef.current = access }, [access])

  const login = async (username, password) => {
    const apiFetch = (await import('./apiClient')).default
    const res = await apiFetch('/api/auth/cookie/token/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!res.ok) {
      const txt = await res.text()
      throw new Error(txt || 'Login failed')
    }
    const data = await res.json()
    if (data.access) setAccess(data.access)
    return data
  }

  const logout = async () => {
    const apiFetch = (await import('./apiClient')).default
    await apiFetch('/api/auth/cookie/logout/', { method: 'POST' })
    setAccess(null)
  }

  const value = {
    access,
    setAccess,
    login,
    logout,
    refresh: fetchAccessFromServer,
    loading,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
