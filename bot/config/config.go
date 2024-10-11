package config

import (
	"os"
	"strconv"
	"strings"
)

type Config struct {
	DiscordToken   string
	DBHost         string
	DBPort         string
	DBUser         string
	DBPassword     string
	DBName         string
	DBSSLMode      string
	ActiveChannels []string
	RedisAddr      string
	RedisPassword  string
	RedisDB        int
}

func LoadConfig() Config {
	activeChannels := os.Getenv("ACTIVE_CHANNELS")
	var channels []string
	if activeChannels != "" {
		channels = strings.Split(activeChannels, ",")
	}

	redisDB, _ := strconv.Atoi(os.Getenv("REDIS_DB"))

	return Config{
		DiscordToken:   os.Getenv("DISCORD_TOKEN"),
		DBHost:         os.Getenv("DB_HOST"),
		DBPort:         os.Getenv("DB_PORT"),
		DBUser:         os.Getenv("DB_USER"),
		DBPassword:     os.Getenv("DB_PASSWORD"),
		DBName:         os.Getenv("DB_NAME"),
		DBSSLMode:      os.Getenv("DB_SSLMODE"),
		ActiveChannels: channels,
		RedisAddr:      os.Getenv("REDIS_ADDR"),
		RedisPassword:  os.Getenv("REDIS_PASSWORD"),
		RedisDB:        redisDB,
	}
}
