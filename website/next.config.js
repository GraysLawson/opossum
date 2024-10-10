module.exports = {
  reactStrictMode: true,
  env: {
    DISCORD_CLIENT_ID: process.env.DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET: process.env.DISCORD_CLIENT_SECRET,
    NEXTAUTH_URL: process.env.NEXTAUTH_URL,
    API_BASE_URL: process.env.API_BASE_URL, // URL of your bot's backend API
  },
}
