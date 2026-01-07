import React from 'react'

export function PublicPage() {
  return (
    <div>
      <h2>Public Page</h2>
      <p>This page is accessible by all authenticated users and guests.</p>
    </div>
  )
}

export function AdminOnly({ user }) {
  if (!user || !(user.role === 'admin' || (user.admin_level && user.admin_level >= 50))) {
    return <div>Not authorized (admin only)</div>
  }
  return (
    <div>
      <h2>Admin Page</h2>
      <p>Only admins (admin_level &gt;= 50) can see this.</p>
    </div>
  )
}

export function NutritionistOnly({ user }) {
  if (!user || user.role !== 'nutritionist') return <div>Not authorized (nutritionist only)</div>
  return (
    <div>
      <h2>Nutritionist Page</h2>
      <p>Only nutritionists can see this content.</p>
    </div>
  )
}

export function RegulatorOnly({ user }) {
  if (!user || user.role !== 'regulator') return <div>Not authorized (regulator only)</div>
  return (
    <div>
      <h2>Regulator Page</h2>
      <p>Only regulators can see this content.</p>
    </div>
  )
}

export default null
