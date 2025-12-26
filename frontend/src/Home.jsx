import React from 'react'
import { Link } from 'react-router-dom'

export default function Home({user, onLogout}) {
  return (
    <div style={{maxWidth:800}}>
      <h2>Home</h2>
      {user ? (
        <>
          <div>Welcome, {user.username}!</div>
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
