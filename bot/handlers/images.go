package handlers

import (
	"strings"

	"github.com/GraysLawson/opossum/bot/services"
	"github.com/GraysLawson/opossum/bot/utils"
	"github.com/bwmarrin/discordgo"
)

func ImageUpload(s *discordgo.Session, m *discordgo.MessageCreate) {
	utils.GlobalLogger.Debug("Received message with potential image upload")

	if m.Author.ID == s.State.User.ID {
		utils.GlobalLogger.Debug("Ignoring message from self")
		return
	}

	if !isChannelActive(m.ChannelID) {
		utils.GlobalLogger.Debug("Channel not active:", m.ChannelID)
		return
	}

	for _, attachment := range m.Attachments {
		utils.GlobalLogger.Debug("Processing attachment:", attachment.Filename)
		if isImage(attachment.ContentType) {
			utils.GlobalLogger.Debug("Attachment is an image, adding description button")
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
			} else {
				utils.GlobalLogger.Debug("Message with description button sent successfully")
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
	utils.GlobalLogger.Debug("Checking if content type is an image:", contentType)
	return strings.HasPrefix(contentType, "image/")
}
