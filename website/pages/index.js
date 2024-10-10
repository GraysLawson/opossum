import Link from 'next/link'

export default function Home() {
  return (
    <div>
      <h1>Welcome to Our Discord Bot!</h1>
      <p>Enhance your Discord server with amazing features.</p>
      <Link href="/login"><a>Get Started</a></Link>
    </div>
  )
}
