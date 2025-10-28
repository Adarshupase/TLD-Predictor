const API = import.meta.env.VITE_API_URL || "http://localhost:8080"

export async function signup({ email, password }) {
  const res = await fetch(`${API}/api/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })
  return res.ok
    ? res.json()
    : res.json().then((j) => ({ error: j?.message || j?.error || "signup failed" }))
}

export async function login({ email, password }) {
  const res = await fetch(`${API}/api/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })
  return res.ok
    ? res.json()
    : res.json().then((j) => ({ error: j?.message || j?.error || "login failed" }))
}

export async function getProfile(token) {
  const res = await fetch(`${API}/api/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.json()
}
