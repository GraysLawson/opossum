package config

import (
	"os"
	"strings"
)

type Config struct {
	BotToken       string
	OpenAIAPIKey   string
	ActiveChannels []string
	Version        int
	DatabaseURL    string
}

var cfg *Config

func LoadConfig() (*Config, error) {
	activeChannels := []string{}
	channels := os.Getenv("ACTIVE_CHANNELS")
	if channels != "" {
		activeChannels = strings.Split(channels, ",")
	} else {
		activeChannels = append(activeChannels, "all")
	}

	version := 1 // This should be auto-incremented during deployment

	cfg = &Config{
		BotToken:       os.Getenv("DISCORD_BOT_KEY"),
		OpenAIAPIKey:   os.Getenv("OPENAI_API_KEY"),
		ActiveChannels: activeChannels,
		Version:        version,
		DatabaseURL:    os.Getenv("DATABASE_URL"),
	}

	return cfg, nil
}

func GetConfig() *Config {
	return cfg
}
