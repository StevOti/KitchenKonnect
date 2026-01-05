import React, { useEffect, useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000'

function authHeaders() {
  const token = window.__KK_TOKEN || localStorage.getItem('__KK_TOKEN')
  return token ? { Authorization: `Token ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
}

export default function AdminUsers({ user }) {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!user || !(user.role === 'admin' || (user.admin_level && user.admin_level >= 50))) {
      setError('Not authorized')
      setLoading(false)
      return
    }
    fetch(`${API_BASE}/api/auth/admin/users/`, { headers: authHeaders() })
      .then(r => r.json())
      .then(data => {
        setUsers(data)
        setLoading(false)
      }).catch(e => { setError(String(e)); setLoading(false) })
  }, [user])

  async function saveUser(u) {
    try {
      const res = await fetch(`${API_BASE}/api/auth/admin/users/${u.id}/`, {
        method: 'PATCH',
        headers: authHeaders(),
        body: JSON.stringify({ role: u.role, admin_level: u.admin_level })
      })
      if (!res.ok) throw new Error(await res.text())
      const updated = await res.json()
      setUsers(users.map(x => x.id === updated.id ? updated : x))
    } catch (e) {
      setError(String(e))
    }
  }

  if (loading) return <div>Loading admin users...</div>
  if (error) return <div>Error: {error}</div>

  return (
    <div style={{maxWidth:900}}>
      <h2>Admin: Manage Users</h2>
      <table style={{width:'100%', borderCollapse:'collapse'}}>
        <thead>
          <tr>
            <th style={{textAlign:'left'}}>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Admin level</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id} style={{borderTop:'1px solid #eee'}}>
              <td>{u.id}</td>
              <td>{u.username}</td>
              <td>{u.email}</td>
              <td>
                <select value={u.role} onChange={e => setUsers(users.map(x => x.id===u.id ? {...x, role: e.target.value} : x))}>
                  <option value="regular">regular</option>
                  <option value="nutritionist">nutritionist</option>
                  <option value="admin">admin</option>
                  <option value="regulator">regulator</option>
                </select>
              </td>
              <td>
                <input type="number" value={u.admin_level || 0} onChange={e => setUsers(users.map(x => x.id===u.id ? {...x, admin_level: Number(e.target.value)} : x))} style={{width:80}} />
              </td>
              <td>
                <button onClick={() => saveUser(u)}>Save</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
