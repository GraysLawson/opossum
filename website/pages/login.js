import { signIn } from 'next-auth/react'

export default function Login() {
  return (
    <div>
      <h1>Login with Discord</h1>
      <button onClick={() => signIn('discord')}>Login</button>
    </div>
  )
}
