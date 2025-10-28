import { useState } from 'react'
import { signup, login } from '../services/auth'

export default function Auth({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [err, setErr] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErr('')
    if (!email || !password) return setErr('email and password required')
    try {
      const fn = mode === 'login' ? login : signup
      const res = await fn({ email, password })
      if (res?.token) {
        localStorage.setItem('token', res.token)
        onLogin(res.token)
        setEmail(''); setPassword('')
      } else {
        setErr(res?.error || 'Auth failed')
      }
    } catch (err) {
      setErr('Network error')
      console.error(err)
    }
  }

  return (
    <div className="p-4 bg-white rounded shadow-sm">
      <div className="flex justify-between mb-3">
        <h3 className="text-lg">{mode === 'login' ? 'Login' : 'Sign up'}</h3>
        <div className="text-sm">
          <button className="mr-2" onClick={() => setMode('login')}>Login</button>
          <button onClick={() => setMode('signup')}>Sign up</button>
        </div>
      </div>
      <form onSubmit={handleSubmit} className="space-y-2">
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" className="w-full p-2 border rounded" />
        <input value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" type="password" className="w-full p-2 border rounded" />
        <button className="w-full p-2 rounded bg-blue-600 text-white" type="submit">{mode === 'login' ? 'Login' : 'Sign up'}</button>
        {err && <p className="text-red-600">{err}</p>}
      </form>
    </div>
  )
}
