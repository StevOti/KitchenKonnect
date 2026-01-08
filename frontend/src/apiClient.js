let _getAccess = () => null

export function registerAccessGetter(fn) {
  _getAccess = fn
}

export default async function apiFetch(input, init = {}) {
  const opts = Object.assign({}, init)
  opts.headers = Object.assign({}, opts.headers || {})

  const token = _getAccess()
  if (token) {
    opts.headers['Authorization'] = `Bearer ${token}`
  }

  // default to include credentials so cookie refresh works
  if (typeof opts.credentials === 'undefined') opts.credentials = 'include'

  return fetch(input, opts)
}
