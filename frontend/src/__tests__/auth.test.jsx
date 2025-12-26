import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'
import { vi } from 'vitest'
import '@testing-library/jest-dom'

const API_BASE = 'http://127.0.0.1:8000'

describe('Auth integration', () => {
  beforeEach(() => {
    // mock fetch
    global.fetch = vi.fn((input, init) => {
      const url = input.toString()
      if (url === `${API_BASE}/api/auth/token/`) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ token: 'stub.token.value' })
        })
      }
      if (url === `${API_BASE}/api/auth/me/`) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ id: 1, username: 'testuser', email: 't@example.com' })
        })
      }
      // fallback
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) })
    })
  })

  afterEach(() => {
    vi.resetAllMocks()
    try { localStorage.clear() } catch(e) {}
  })

  it('logs in and shows home profile', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )

    // wait for auth form to render
    const userInput = await screen.findByPlaceholderText('username')
    const passInput = screen.getByPlaceholderText('password')
    const loginBtn = screen.getByText(/Login \(token\)/i)

    fireEvent.change(userInput, { target: { value: 'testuser' } })
    fireEvent.change(passInput, { target: { value: 'secret' } })
    fireEvent.click(loginBtn)

    // Wait for home heading
    await waitFor(() => expect(screen.getByText(/Home/i)).toBeInTheDocument())
    expect(screen.getByText(/Welcome, testuser/i)).toBeInTheDocument()
  })
})
