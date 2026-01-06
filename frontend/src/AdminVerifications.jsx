import React, { useEffect, useState } from 'react'
import ToastContainer, { showToast } from './Toasts'

const API_BASE = 'http://127.0.0.1:8000'

function authHeaders() {
  const token = window.__KK_TOKEN || localStorage.getItem('__KK_TOKEN')
  return token ? { Authorization: `Token ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
}

export default function AdminVerifications({ user }) {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!user || !(user.role === 'admin' || (user.admin_level && user.admin_level >= 50))) {
      setError('Not authorized')
      setLoading(false)
      return
    }
    fetch(`${API_BASE}/api/auth/verification/requests/`, { headers: authHeaders() })
      .then(r => {
        if (!r.ok) throw new Error(r.statusText)
        return r.json()
      }).then(d => { setRequests(d); setLoading(false) }).catch(e => { setError(String(e)); setLoading(false) })
  }, [user])

  async function review(id, status) {
    try {
      const res = await fetch(`${API_BASE}/api/auth/verification/requests/${id}/`, {
        method: 'PATCH',
        headers: authHeaders(),
        body: JSON.stringify({ status })
      })
      if (!res.ok) throw new Error(await res.text())
      const updated = await res.json()
      setRequests(reqs => reqs.map(r => r.id === updated.id ? updated : r))
      showToast({ message: `Request ${id} ${status}`, type: 'success' })
    } catch (e) {
      setError(String(e))
      showToast({ message: `Error reviewing ${id}: ${String(e)}`, type: 'error' })
    }
  }

  if (loading) return <div>Loading verification requests...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div style={{ maxWidth: 900 }}>
      <ToastContainer />
      <h2>Verification Requests</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>User</th>
            <th>Requested Role</th>
            <th>Message</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.map(r => (
            <tr key={r.id} style={{ borderTop: '1px solid #eee' }}>
              <td>{r.id}</td>
              <td>{r.user}</td>
              <td>{r.requested_role}</td>
              <td style={{ maxWidth: 300 }}>{r.message}</td>
              <td>{r.status}</td>
              <td>
                <button onClick={() => review(r.id, 'approved')}>Approve</button>
                <button onClick={() => review(r.id, 'rejected')} style={{ marginLeft: 8 }}>Reject</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
