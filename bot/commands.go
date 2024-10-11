package commands

import (
	"fmt"

	"discord-bot-project/bot/config"

	"github.com/bwmarrin/discordgo"
)

// HelloCommand responds with "Hello World"
func HelloCommand(s *discordgo.Session, m *discordgo.MessageCreate) {
	s.ChannelMessageSend(m.ChannelID, "Hello World")
}

// ActivateChannelCommand activates the current channel
func ActivateChannelCommand(s *discordgo.Session, m *discordgo.MessageCreate) {
	channelID := m.ChannelID
	for _, id := range config.BotConfig.ActiveChannels {
		if id == channelID {
			s.ChannelMessageSend(channelID, "Channel is already active.")
			return
		}
	}
	config.BotConfig.ActiveChannels = append(config.BotConfig.ActiveChannels, channelID)
	config.SaveConfig()
	s.ChannelMessageSend(channelID, "Channel activated.")
}

// DeactivateChannelCommand deactivates the current channel
func DeactivateChannelCommand(s *discordgo.Session, m *discordgo.MessageCreate) {
	channelID := m.ChannelID
	for i, id := range config.BotConfig.ActiveChannels {
		if id == channelID {
			config.BotConfig.ActiveChannels = append(config.BotConfig.ActiveChannels[:i], config.BotConfig.ActiveChannels[i+1:]...)
			config.SaveConfig()
			s.ChannelMessageSend(channelID, "Channel deactivated.")
			return
		}
	}
	s.ChannelMessageSend(channelID, "Channel is not active.")
}

// VersionCommand responds with the bot's version
func VersionCommand(s *discordgo.Session, m *discordgo.MessageCreate) {
	version := config.BotConfig.Version
	s.ChannelMessageSend(m.ChannelID, fmt.Sprintf("Bot version: %s", version))
}
