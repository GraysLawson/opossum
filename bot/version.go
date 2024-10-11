package bot

import (
	"strconv"
	"strings"

	"discord-bot-project/bot/config"
)

// IncrementVersion increments the patch version
func IncrementVersion() error {
	version := config.BotConfig.Version
	parts := strings.Split(version, ".")
	if len(parts) != 3 {
		return nil
	}
	patch, err := strconv.Atoi(parts[2])
	if err != nil {
		return err
	}
	patch++
	newVersion := parts[0] + "." + parts[1] + "." + strconv.Itoa(patch)
	config.BotConfig.Version = newVersion
	return config.SaveConfig()
}
