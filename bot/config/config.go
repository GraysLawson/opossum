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
