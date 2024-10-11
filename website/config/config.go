package config

import (
	"os"
)

type Config struct {
	OpenAIAPIKey  string
	DiscordBotKey string
	DatabaseURL   string
}

func LoadConfig() (*Config, error) {
	return &Config{
		OpenAIAPIKey:  os.Getenv("OPENAI_API_KEY"),
		DiscordBotKey: os.Getenv("DISCORD_BOT_KEY"),
		DatabaseURL:   os.Getenv("DATABASE_URL"),
	}, nil
}
