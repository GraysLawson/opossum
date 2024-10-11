package handlers

import (
	"strings"

	"github.com/GraysLawson/opossum/bot/config"
	"github.com/GraysLawson/opossum/bot/utils"
	"github.com/bwmarrin/discordgo"
)

var cfg *config.Config

func InitializeDiscord(configuration *config.Config) (*discordgo.Session, error) {
	utils.GlobalLogger.Debug("Initializing Discord with configuration")
	cfg = configuration
	dg, err := discordgo.New("Bot " + cfg.BotToken) // Note: cfg.BotToken now contains the DISCORD_BOT_KEY
	if err != nil {
		utils.GlobalLogger.Error("Failed to create Discord session:", err)
		return nil, err
	}
	utils.GlobalLogger.Debug("Discord session created successfully")
	return dg, nil
}

func MessageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	utils.GlobalLogger.Debug("Received message:", m.Content)

	if m.Author.ID == s.State.User.ID {
		utils.GlobalLogger.Debug("Ignoring message from self")
		return
	}

	if !isChannelActive(m.ChannelID) {
		utils.GlobalLogger.Debug("Channel not active:", m.ChannelID)
		return
	}

	if strings.HasPrefix(m.Content, "!hello") {
		utils.GlobalLogger.Debug("Responding to !hello command")
		_, err := s.ChannelMessageSend(m.ChannelID, "Hello World")
		if err != nil {
			utils.GlobalLogger.Error("Failed to send message:", err)
		} else {
			utils.GlobalLogger.Debug("Hello World message sent successfully")
		}
	}
}

func isChannelActive(channelID string) bool {
	utils.GlobalLogger.Debug("Checking if channel is active:", channelID)
	if len(cfg.ActiveChannels) == 0 || (len(cfg.ActiveChannels) == 1 && cfg.ActiveChannels[0] == "all") {
		utils.GlobalLogger.Debug("All channels are active")
		return true
	}
	for _, id := range cfg.ActiveChannels {
		if id == channelID {
			utils.GlobalLogger.Debug("Channel is active:", channelID)
			return true
		}
	}
	utils.GlobalLogger.Debug("Channel is not active:", channelID)
	return false
}
