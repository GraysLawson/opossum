package handlers

import (
	"strings"

	"github.com/GraysLawson/opossum/bot/services"
	"github.com/GraysLawson/opossum/bot/utils"
	"github.com/bwmarrin/discordgo"
)

func ImageUpload(s *discordgo.Session, m *discordgo.MessageCreate) {
	if m.Author.ID == s.State.User.ID {
		return
	}

	if !isChannelActive(m.ChannelID) {
		return
	}

	for _, attachment := range m.Attachments {
		if isImage(attachment.ContentType) {
			// Add button for generating OpenAI description
			button := discordgo.Button{
				Label:    "Generate Description",
				Style:    discordgo.PrimaryButton,
				CustomID: "generate_description_" + attachment.ID,
			}

			buttons := []discordgo.Button{button}
			actionRow := discordgo.ActionsRow{
				Components: []discordgo.MessageComponent{&buttons[0]},
			}

			_, err := s.ChannelMessageSendComplex(m.ChannelID, &discordgo.MessageSend{
				Content: "Image uploaded:",
				Components: []discordgo.MessageComponent{
					&actionRow,
				},
			})
			if err != nil {
				utils.GlobalLogger.Error("Failed to send message with button:", err)
			}

			// Handle button interaction
			s.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
				if i.Type != discordgo.InteractionMessageComponent {
					return
				}

				if strings.HasPrefix(i.MessageComponentData().CustomID, "generate_description_") {
					description, err := services.GenerateOpenAIDescription(attachment.URL)
					if err != nil {
						s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
							Type: discordgo.InteractionResponseChannelMessageWithSource,
							Data: &discordgo.InteractionResponseData{
								Content: "Failed to generate description.",
							},
						})
						return
					}

					s.InteractionRespond(i.Interaction, &discordgo.InteractionResponse{
						Type: discordgo.InteractionResponseChannelMessageWithSource,
						Data: &discordgo.InteractionResponseData{
							Content: "Description: " + description,
						},
					})
				}
			})
		}
	}
}

func isImage(contentType string) bool {
	return strings.HasPrefix(contentType, "image/")
}
