import Link from 'next/link'
import { useSession, signIn, signOut } from 'next-auth/react'

export default function Navbar() {
  const { data: session } = useSession()

  return (
    <nav>
      <Link href="/">Home</Link>
      {session ? (
        <>
          <Link href="/dashboard">Dashboard</Link>
          <button onClick={() => signOut()}>Logout</button>
        </>
      ) : (
        <button onClick={() => signIn('discord')}>Login</button>
      )}
    </nav>
  )
}
