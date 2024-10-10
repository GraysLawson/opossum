import { useSession, getSession } from 'next-auth/react'
import { useEffect, useState } from 'react'
import axios from 'axios'

export default function Dashboard() {
  const { data: session, status } = useSession()
  const [settings, setSettings] = useState({ theme: 'light', notifications: true })

  useEffect(() => {
    if (session) {
      // Fetch user settings from the bot's API
      axios.get(`${process.env.API_BASE_URL}/settings`, { params: { discordId: session.user.id } })
        .then(response => setSettings(response.data))
        .catch(error => console.error(error))
    }
  }, [session])

  const updateSettings = () => {
    // Update settings via the bot's API
    axios.post(`${process.env.API_BASE_URL}/settings`, { discordId: session.user.id, settings })
      .then(response => alert('Settings updated'))
      .catch(error => console.error(error))
  }

  if (status === 'loading') {
    return <div>Loading...</div>
  }

  if (!session) {
    return <div>Please log in.</div>
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <label>
        Theme:
        <select value={settings.theme} onChange={e => setSettings({ ...settings, theme: e.target.value })}>
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </label>
      <label>
        Notifications:
        <input
          type="checkbox"
          checked={settings.notifications}
          onChange={e => setSettings({ ...settings, notifications: e.target.checked })}
        />
      </label>
      <button onClick={updateSettings}>Save</button>
    </div>
  )
}

export async function getServerSideProps(context) {
  const session = await getSession(context)
  if (!session) {
    return {
      redirect: {
        destination: '/login',
        permanent: false,
      },
    }
  }
  return {
    props: { session },
  }
}
