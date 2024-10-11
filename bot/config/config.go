package config

import (
	"os"
	"strings"

	"github.com/joho/godotenv"
)

type Config struct {
	BotToken       string
	OpenAIAPIKey   string
	ActiveChannels []string
	Version        int
}

var cfg *Config

func LoadConfig() (*Config, error) {
	err := godotenv.Load("../.env")
	if err != nil {
		return nil, err
	}

	activeChannels := []string{}
	channels := os.Getenv("ACTIVE_CHANNELS")
	if channels != "" {
		activeChannels = strings.Split(channels, ",")
	} else {
		activeChannels = append(activeChannels, "all")
	}

	version := 1 // This should be auto-incremented during deployment

	cfg = &Config{
		BotToken:       os.Getenv("DISCORD_BOT_TOKEN"),
		OpenAIAPIKey:   os.Getenv("OPENAI_API_KEY"),
		ActiveChannels: activeChannels,
		Version:        version,
	}

	return cfg, nil
}

func GetConfig() *Config {
	return cfg
}
