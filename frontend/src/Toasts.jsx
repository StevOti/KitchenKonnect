import React, { useEffect, useState } from 'react'

export function showToast({ message, type = 'success', ttl = 4000 }) {
  const ev = new CustomEvent('kk-toast', { detail: { id: Date.now() + Math.random(), message, type, ttl } })
  window.dispatchEvent(ev)
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState([])

  useEffect(() => {
    function onToast(e) {
      const t = e.detail
      setToasts(prev => [...prev, t])
      setTimeout(() => {
        setToasts(prev => prev.filter(x => x.id !== t.id))
      }, t.ttl || 4000)
    }
    window.addEventListener('kk-toast', onToast)
    return () => window.removeEventListener('kk-toast', onToast)
  }, [])

  return (
    <div style={{ position: 'fixed', top: 12, right: 12, zIndex: 9999 }}>
      {toasts.map(t => (
        <div key={t.id} style={{ marginBottom: 8, padding: '8px 12px', borderRadius: 6, background: t.type === 'error' ? '#f44336' : '#4caf50', color: 'white', boxShadow: '0 2px 6px rgba(0,0,0,0.2)' }}>
          {t.message}
        </div>
      ))}
    </div>
  )
}
