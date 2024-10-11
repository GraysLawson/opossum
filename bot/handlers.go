package bot

import (
	"strings"

	"discord-bot-project/bot/commands"
	"discord-bot-project/bot/config"
	"discord-bot-project/bot/utils"

	"github.com/bwmarrin/discordgo"
)

// messageCreate handles incoming messages
func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	// Ignore messages from the bot itself
	if m.Author.ID == s.State.User.ID {
		return
	}

	content := m.Content

	// Handle commands
	if strings.HasPrefix(content, "!") {
		command := strings.TrimPrefix(content, "!")
		args := strings.Fields(command)
		if len(args) == 0 {
			return
		}
		switch args[0] {
		case "hello":
			commands.HelloCommand(s, m)
		case "activate":
			commands.ActivateChannelCommand(s, m)
		case "deactivate":
			commands.DeactivateChannelCommand(s, m)
		case "version":
			commands.VersionCommand(s, m)
		default:
			s.ChannelMessageSend(m.ChannelID, "Unknown command")
		}
	}

	// Check if channel is active
	if !isActiveChannel(m.ChannelID) {
		return
	}

	// Monitor for image uploads
	if len(m.Attachments) > 0 {
		for _, attachment := range m.Attachments {
			if isImage(attachment.URL) {
				utils.LogImageUpload(m.ChannelID, m.Author.Username, attachment.URL)
				// Add reaction with a button
				s.MessageReactionAdd(m.ChannelID, m.ID, "🖼️")
			}
		}
	}
}

// messageReactionAdd handles reactions to messages
func messageReactionAdd(s *discordgo.Session, r *discordgo.MessageReactionAdd) {
	// Ignore if the reaction is from the bot
	if r.UserID == s.State.User.ID {
		return
	}

	// Check if the reaction is the image reaction
	if r.Emoji.Name == "🖼️" {
		// Fetch the message
		m, err := s.ChannelMessage(r.ChannelID, r.MessageID)
		if err != nil {
			return
		}

		// Check if the message has attachments
		if len(m.Attachments) > 0 {
			for _, attachment := range m.Attachments {
				if isImage(attachment.URL) {
					// Generate description using OpenAI
					description, err := utils.GenerateImageDescription(attachment.URL)
					if err != nil {
						s.ChannelMessageSend(r.ChannelID, "Error generating description.")
						return
					}
					s.ChannelMessageSend(r.ChannelID, description)
				}
			}
		}
	}
}

// isActiveChannel checks if a channel is active
func isActiveChannel(channelID string) bool {
	if len(config.BotConfig.ActiveChannels) == 0 {
		// No active channels specified; default to all channels
		return true
	}
	for _, id := range config.BotConfig.ActiveChannels {
		if id == channelID {
			return true
		}
	}
	return false
}

// isImage checks if a URL points to an image file
func isImage(url string) bool {
	// Simple check based on file extension
	url = strings.ToLower(url)
	return strings.HasSuffix(url, ".jpg") || strings.HasSuffix(url, ".jpeg") || strings.HasSuffix(url, ".png") || strings.HasSuffix(url, ".gif")
}
