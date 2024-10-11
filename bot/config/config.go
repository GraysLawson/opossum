package config

import (
	"encoding/json"
	"io/ioutil"
)

// Config holds the configuration for the bot
type Config struct {
	Token          string   `json:"Token"`
	OpenAIAPIKey   string   `json:"OpenAIAPIKey"`
	ActiveChannels []string `json:"ActiveChannels"`
	Version        string   `json:"Version"`
}

// BotConfig is the global configuration instance
var BotConfig Config

// LoadConfig reads the configuration from config.json
func LoadConfig() error {
	data, err := ioutil.ReadFile("bot/config/config.json")
	if err != nil {
		return err
	}
	err = json.Unmarshal(data, &BotConfig)
	if err != nil {
		return err
	}
	return nil
}

// SaveConfig writes the current config to config.json
func SaveConfig() error {
	data, err := json.MarshalIndent(BotConfig, "", "  ")
	if err != nil {
		return err
	}
	err = ioutil.WriteFile("bot/config/config.json", data, 0644)
	if err != nil {
		return err
	}
	return nil
}
