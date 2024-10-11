package handlers

import (
	"strings"

	"github.com/GraysLawson/opossum/bot/config"
	"github.com/GraysLawson/opossum/bot/utils"
	"github.com/bwmarrin/discordgo"
)

var cfg *config.Config

func InitializeDiscord(configuration *config.Config) (*discordgo.Session, error) {
	cfg = configuration
	dg, err := discordgo.New("Bot " + cfg.BotToken)
	if err != nil {
		return nil, err
	}
	return dg, nil
}

func MessageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	if m.Author.ID == s.State.User.ID {
		return
	}

	if !isChannelActive(m.ChannelID) {
		return
	}

	if strings.HasPrefix(m.Content, "!hello") {
		_, err := s.ChannelMessageSend(m.ChannelID, "Hello World")
		if err != nil {
			utils.GlobalLogger.Error("Failed to send message:", err)
		}
	}
}

func isChannelActive(channelID string) bool {
	if len(cfg.ActiveChannels) == 0 || (len(cfg.ActiveChannels) == 1 && cfg.ActiveChannels[0] == "all") {
		return true
	}
	for _, id := range cfg.ActiveChannels {
		if id == channelID {
			return true
		}
	}
	return false
}
