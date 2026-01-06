import React, { useEffect, useState } from 'react'
import ToastContainer, { showToast } from './Toasts'

const API_BASE = 'http://127.0.0.1:8000'

function authHeaders() {
  const token = window.__KK_TOKEN || localStorage.getItem('__KK_TOKEN')
  return token ? { Authorization: `Token ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
}

export default function AdminUsers({ user }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(new Set())
  const [query, setQuery] = useState('')
  const [rowStatus, setRowStatus] = useState({})
  const [selectAll, setSelectAll] = useState(false)
  const [originalMap, setOriginalMap] = useState({})
  const [bulkRole, setBulkRole] = useState('nutritionist')

  useEffect(() => {
    if (!user || !(user.role === 'admin' || (user.admin_level && user.admin_level >= 50))) {
      setError('Not authorized')
      setLoading(false)
      return
    }
    const url = query ? `${API_BASE}/api/auth/admin/users/?search=${encodeURIComponent(query)}` : `${API_BASE}/api/auth/admin/users/`
    fetch(url, { headers: authHeaders() })
      .then(r => {
        if (!r.ok) throw new Error(r.statusText)
        return r.json()
      })
      .then(data => {
        setUsers(data)
        // capture original state for undo
        const map = {}
        data.forEach(u => { map[u.id] = { ...u } })
        setOriginalMap(map)
        setLoading(false)
      }).catch(e => { setError(String(e)); setLoading(false) })
  }, [user])

  async function saveUser(u) {
    try {
      setRowStatus(s => ({ ...s, [u.id]: { loading: true } }))
      const res = await fetch(`${API_BASE}/api/auth/admin/users/${u.id}/`, {
        method: 'PATCH',
        headers: authHeaders(),
        body: JSON.stringify({ role: u.role, admin_level: u.admin_level })
      })
      if (!res.ok) throw new Error(await res.text())
      const updated = await res.json()
      setUsers(users.map(x => x.id === updated.id ? updated : x))
      setRowStatus(s => ({ ...s, [u.id]: { success: true, loading: false } }))
      // update original map
      setOriginalMap(m => ({ ...m, [updated.id]: { ...updated } }))
      showToast({ message: `Updated ${updated.username}`, type: 'success' })
    } catch (e) {
      setRowStatus(s => ({ ...s, [u.id]: { error: String(e), loading: false } }))
      showToast({ message: `Error updating ${u.username}: ${String(e)}`, type: 'error' })
    }
  }

  function toggleSelect(id) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  async function bulkPromote(role, level) {
    const ids = Array.from(selected)
    for (const id of ids) {
      const u = users.find(x => x.id === id)
      if (!u) continue
      u.role = role
      u.admin_level = level
      await saveUser(u)
    }
    showToast({ message: `Bulk promote to ${role} completed`, type: 'success' })
  }

  function undoUser(id) {
    const orig = originalMap[id]
    if (!orig) return
    setUsers(users.map(x => x.id === id ? { ...orig } : x))
    setRowStatus(s => ({ ...s, [id]: { undone: true } }))
  }

  function toggleSelectAll() {
    if (!selectAll) {
      setSelected(new Set(users.map(u => u.id)))
      setSelectAll(true)
    } else {
      setSelected(new Set())
      setSelectAll(false)
    }
  }

  function applyBulkRoleToSelected() {
    const ids = Array.from(selected)
    for (const id of ids) {
      setUsers(prev => prev.map(u => u.id === id ? { ...u, role: bulkRole } : u))
    }
  }

  async function bulkDemote() {
    const ids = Array.from(selected)
    for (const id of ids) {
      const u = users.find(x => x.id === id)
      if (!u) continue
      u.role = 'regular'
      u.admin_level = 0
      await saveUser(u)
    }
    showToast({ message: 'Bulk demote completed', type: 'success' })
  }

  if (loading) return <div>Loading admin users...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div style={{ maxWidth: 900 }}>
      <ToastContainer />
      <h2>Admin: Manage Users</h2>
      <div style={{ marginBottom: 12 }}>
        <input placeholder="Search username/email" value={query} onChange={e => setQuery(e.target.value)} style={{ width: 300 }} />
        <button onClick={() => { setLoading(true); setError(null); fetch(`${API_BASE}/api/auth/admin/users/?search=${encodeURIComponent(query)}`, { headers: authHeaders() }).then(r => r.json()).then(d => { setUsers(d); setLoading(false) }).catch(e => { setError(String(e)); setLoading(false) }) }} style={{ marginLeft: 8 }}>Search</button>
        <select value={bulkRole} onChange={e => setBulkRole(e.target.value)} style={{ marginLeft: 12 }}>
          <option value="nutritionist">Nutritionist</option>
          <option value="regulator">Regulator</option>
          <option value="admin">Admin</option>
          <option value="regular">Regular</option>
        </select>
        <button onClick={applyBulkRoleToSelected} style={{ marginLeft: 8 }}>Apply role to selected</button>
        <button onClick={() => bulkPromote('nutritionist', 10)} style={{ marginLeft: 12 }}>Promote selected to Nutritionist</button>
        <button onClick={() => bulkPromote('regulator', 10)} style={{ marginLeft: 8 }}>Promote selected to Regulator</button>
        <button onClick={bulkDemote} style={{ marginLeft: 8 }}>Bulk Demote to Regular</button>
      </div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th><input type="checkbox" checked={selectAll} onChange={toggleSelectAll} /></th>
            <th style={{ textAlign: 'left' }}>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Admin level</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id} style={{ borderTop: '1px solid #eee' }}>
              <td><input type="checkbox" checked={selected.has(u.id)} onChange={() => toggleSelect(u.id)} /></td>
              <td>{u.id}</td>
              <td>{u.username}</td>
              <td>{u.email}</td>
              <td>
                <select value={u.role} onChange={e => setUsers(users.map(x => x.id === u.id ? { ...x, role: e.target.value } : x))}>
                  <option value="regular">regular</option>
                  <option value="nutritionist">nutritionist</option>
                  <option value="admin">admin</option>
                  <option value="regulator">regulator</option>
                </select>
              </td>
              <td>
                <input type="number" value={u.admin_level || 0} onChange={e => setUsers(users.map(x => x.id === u.id ? { ...x, admin_level: Number(e.target.value) } : x))} style={{ width: 80 }} />
              </td>
              <td>
                <button onClick={() => saveUser(u)}>Save</button>
                <button onClick={() => undoUser(u.id)} style={{ marginLeft: 6 }}>Undo</button>
                {rowStatus[u.id] && rowStatus[u.id].loading && <span style={{ marginLeft: 8 }}>Saving...</span>}
                {rowStatus[u.id] && rowStatus[u.id].success && <span style={{ marginLeft: 8, color: 'green' }}>Saved</span>}
                {rowStatus[u.id] && rowStatus[u.id].error && <span style={{ marginLeft: 8, color: 'red' }}>Error</span>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
