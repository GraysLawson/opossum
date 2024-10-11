package config

import (
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	OpenAIAPIKey  string
	DiscordBotKey string
	DatabaseURL   string
}

func LoadConfig() (*Config, error) {
	err := godotenv.Load("../.env")
	if err != nil {
		return nil, err
	}

	return &Config{
		OpenAIAPIKey:  os.Getenv("OPENAI_API_KEY"),
		DiscordBotKey: os.Getenv("DISCORD_BOT_KEY"),
		DatabaseURL:   os.Getenv("DATABASE_URL"),
	}, nil
}
