import React from 'react'
import { Link } from 'react-router-dom'

export default function Home({user, onLogout}) {
  return (
    <div style={{maxWidth:800}}>
      <h2>Home</h2>
      {user ? (
        <>
          <div style={{display:'flex', alignItems:'center', gap:12}}>
            <div style={{fontSize:18}}>Welcome, <strong>{user.username}</strong>!</div>
            <div style={{padding:6, border:'1px solid #ddd', borderRadius:6}}>
              <div><strong>Role:</strong> {user.role || 'regular'}</div>
              <div><strong>Admin level:</strong> {user.admin_level ?? 0}</div>
            </div>
            {((user.role==='admin' && (user.admin_level||0) >= 50) || (user.admin_level || 0) >= 50) && (
              <div>
                <a href="/admin/users" style={{marginLeft:12}}><button>Manage users</button></a>
              </div>
            )}
          </div>
          <pre style={{marginTop:12}}>{JSON.stringify(user, null, 2)}</pre>
        </>
      ) : (
        <div>You are not logged in.</div>
      )}

      <div style={{marginTop:12}}>
        <button onClick={onLogout}>Logout</button>
        <Link to="/">
          <button style={{marginLeft:8}}>Back to Login</button>
        </Link>
      </div>
    </div>
  )
}
