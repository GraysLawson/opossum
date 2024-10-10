#!/bin/bash

# Create .gitignore
cat <<EOL > .gitignore
# Go dependencies
/vendor/
*.exe
*.log
*.test

# Node dependencies
/node_modules
/.next
/out
.DS_Store

# Environment variables
.env
.env.local
.env.*.local

# Fly.io
.fly/
EOL

# -------------------
# Discord Bot
# -------------------
mkdir -p bot/cmd
mkdir -p bot/config
mkdir -p bot/models
mkdir -p bot/services

# bot/go.mod
cat <<EOL > bot/go.mod
module github.com/yourusername/bot

go 1.20

require (
    github.com/bwmarrin/discordgo v0.31.1
    gorm.io/driver/postgres v1.4.6
    gorm.io/gorm v1.25.1
)
EOL

# bot/cmd/main.go
cat <<'EOL' > bot/cmd/main.go
package main

import (
    "os"
    "os/signal"
    "syscall"

    "github.com/yourusername/bot/config"
    "github.com/yourusername/bot/services"
)

func main() {
    cfg := config.LoadConfig()

    // Initialize Database
    services.InitDatabase(cfg)

    // Initialize Discord Session
    dg := services.InitDiscordSession(cfg)
    defer dg.Close()

    // Wait for a termination signal
    sc := make(chan os.Signal, 1)
    signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt, os.Kill)
    <-sc
}
EOL

# bot/config/config.go
cat <<'EOL' > bot/config/config.go
package config

import (
    "os"
)

type Config struct {
    DiscordToken string
    DBHost       string
    DBPort       string
    DBUser       string
    DBPassword   string
    DBName       string
    DBSSLMode    string
}

func LoadConfig() Config {
    return Config{
        DiscordToken: os.Getenv("DISCORD_TOKEN"),
        DBHost:       os.Getenv("DB_HOST"),
        DBPort:       os.Getenv("DB_PORT"),
        DBUser:       os.Getenv("DB_USER"),
        DBPassword:   os.Getenv("DB_PASSWORD"),
        DBName:       os.Getenv("DB_NAME"),
        DBSSLMode:    os.Getenv("DB_SSLMODE"),
    }
}
EOL

# bot/models/user.go
cat <<'EOL' > bot/models/user.go
package models

import (
    "time"

    "gorm.io/gorm"
)

type User struct {
    ID        uint           `gorm:"primaryKey"`
    DiscordID string         `gorm:"uniqueIndex;not null"`
    Settings  UserSettings   `gorm:"constraint:OnUpdate:CASCADE,OnDelete:SET NULL;"`
    CreatedAt time.Time
    UpdatedAt time.Time
}

type UserSettings struct {
    ID            uint   `gorm:"primaryKey"`
    Theme         string `gorm:"default:'light'"`
    Notifications bool   `gorm:"default:true"`
    UserID        uint
    CreatedAt     time.Time
    UpdatedAt     time.Time
}
EOL

# bot/services/discord.go
cat <<'EOL' > bot/services/discord.go
package services

import (
    "fmt"
    "log"

    "github.com/bwmarrin/discordgo"
    "github.com/yourusername/bot/config"
    "github.com/yourusername/bot/models"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
)

var DB *gorm.DB

func InitDatabase(cfg config.Config) {
    dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
        cfg.DBHost, cfg.DBPort, cfg.DBUser, cfg.DBPassword, cfg.DBName, cfg.DBSSLMode)
    var err error
    DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatalf("failed to connect database: %v", err)
    }

    // Migrate the schema
    err = DB.AutoMigrate(&models.User{}, &models.UserSettings{})
    if err != nil {
        log.Fatalf("failed to migrate database: %v", err)
    }
}

func InitDiscordSession(cfg config.Config) *discordgo.Session {
    dg, err := discordgo.New("Bot " + cfg.DiscordToken)
    if err != nil {
        log.Fatalf("error creating Discord session: %v", err)
    }

    dg.AddHandler(messageCreate)

    err = dg.Open()
    if err != nil {
        log.Fatalf("error opening connection: %v", err)
    }

    log.Println("Bot is now running. Press CTRL-C to exit.")
    return dg
}

func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
    // Ignore messages from the bot itself
    if m.Author.ID == s.State.User.ID {
        return
    }

    if m.Content == "!ping" {
        s.ChannelMessageSend(m.ChannelID, "Pong!")
    }

    // Add more command handlers here
}
EOL

# -------------------
# Website
# -------------------
mkdir -p website/pages
mkdir -p website/components
mkdir -p website/lib
mkdir -p website/styles

# website/package.json
cat <<EOL > website/package.json
{
  "name": "discord-bot-website",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "13.4.10",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "next-auth": "^4.22.1",
    "axios": "^1.4.0"
  }
}
EOL

# website/next.config.js
cat <<'EOL' > website/next.config.js
module.exports = {
  reactStrictMode: true,
  env: {
    DISCORD_CLIENT_ID: process.env.DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET: process.env.DISCORD_CLIENT_SECRET,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    API_BASE_URL: process.env.API_BASE_URL, // URL of your bot's backend API
  },
}
EOL

# website/pages/_app.js
cat <<'EOL' > website/pages/_app.js
import '../styles/globals.css'
import { SessionProvider } from 'next-auth/react'

function MyApp({ Component, pageProps: { session, ...pageProps } }) {
  return (
    <SessionProvider session={session}>
      <Component {...pageProps} />
    </SessionProvider>
  )
}

export default MyApp
EOL

# website/pages/index.js
cat <<'EOL' > website/pages/index.js
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
EOL

# website/pages/login.js
cat <<'EOL' > website/pages/login.js
import { signIn } from 'next-auth/react'

export default function Login() {
  return (
    <div>
      <h1>Login with Discord</h1>
      <button onClick={() => signIn('discord')}>Login</button>
    </div>
  )
}
EOL

# website/pages/dashboard.js
cat <<'EOL' > website/pages/dashboard.js
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
EOL

# website/components/Navbar.js
cat <<'EOL' > website/components/Navbar.js
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
EOL

# website/lib/auth.js
cat <<'EOL' > website/lib/auth.js
import NextAuth from 'next-auth'
import DiscordProvider from 'next-auth/providers/discord'

export default NextAuth({
  providers: [
    DiscordProvider({
      clientId: process.env.DISCORD_CLIENT_ID,
      clientSecret: process.env.DISCORD_CLIENT_SECRET,
      authorization: { params: { scope: 'identify email guilds' } },
    }),
  ],
  callbacks: {
    async session({ session, token, user }) {
      // Add Discord ID to session
      session.user.id = token.sub
      return session
    },
  },
})
EOL

# website/pages/api/auth/[...nextauth].js
mkdir -p website/pages/api/auth
cat <<'EOL' > website/pages/api/auth/[...nextauth].js
import auth from '../../../lib/auth'

export default auth
EOL

# website/styles/globals.css
cat <<'EOL' > website/styles/globals.css
/* Add your global styles here */
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
}
nav {
  background-color: #333;
  padding: 1rem;
}
nav a, nav button {
  color: #fff;
  margin-right: 1rem;
  text-decoration: none;
}
nav button {
  background: none;
  border: none;
  cursor: pointer;
}
EOL

# Initialize Go modules
cd bot || exit
go mod tidy

# Initialize Node modules
cd ../website || exit
npm install

echo "Project structure initialized successfully."