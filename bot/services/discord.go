package services

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/GraysLawson/bot/config"
	"github.com/GraysLawson/bot/models"
	"github.com/bwmarrin/discordgo"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB
var Version string
var ActiveChannels []string

func SetVersion(v string) {
	Version = v
}

func UpdateStatus(s *discordgo.Session) {
	err := s.UpdateGameStatus(0, fmt.Sprintf("v%s", Version))
	if err != nil {
		log.Printf("Error updating status: %v", err)
	}
}

func updateStatus(s *discordgo.Session) {
	UpdateStatus(s)
}

func InitDatabase(cfg config.Config) {
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		cfg.DBHost, cfg.DBPort, cfg.DBUser, cfg.DBPassword, cfg.DBName, cfg.DBSSLMode)
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect to opossum database: %v", err)
	}

	// Migrate the schema
	err = DB.AutoMigrate(&models.User{}, &models.UserSettings{})
	if err != nil {
		log.Printf("Warning: failed to migrate database: %v", err)
	}
}

func InitDiscordSession(cfg config.Config) *discordgo.Session {
	dg, err := discordgo.New("Bot " + cfg.DiscordToken)
	if err != nil {
		log.Fatalf("error creating Discord session: %v", err)
	}

	dg.AddHandler(messageCreate)

	err = dg.Open()
	if err != nil {
		log.Fatalf("error opening connection: %v", err)
	}

	UpdateStatus(dg)

	log.Println("Bot is now running. Press CTRL-C to exit.")
	return dg
}

func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	// Ignore messages from the bot itself
	if m.Author.ID == s.State.User.ID {
		return
	}

	// Check if the message is in an active channel or if no active channels are specified
	if len(ActiveChannels) > 0 {
		isActiveChannel := false
		for _, channelID := range ActiveChannels {
			if m.ChannelID == channelID {
				isActiveChannel = true
				break
			}
		}
		if !isActiveChannel {
			return
		}
	}

	// Create a unique lock key for this message
	lockKey := "lock:message:" + m.ID
	ctx := context.Background()

	// Try to acquire the lock
	locked, err := RedisClient.SetNX(ctx, lockKey, "1", 5*time.Second).Result()
	if err != nil {
		log.Printf("Error acquiring lock: %v", err)
		return
	}

	// If we couldn't acquire the lock, another instance is handling this message
	if !locked {
		return
	}

	// Process the message
	log.Printf("Received message: %s from user: %s#%s in channel: %s", m.Content, m.Author.Username, m.Author.Discriminator, m.ChannelID)

	// Check if the message contains an image
	if len(m.Attachments) > 0 && isImage(m.Attachments[0].URL) {
		// Create a button for image description
		components := []discordgo.MessageComponent{
			discordgo.Button{
				Label:    "Describe Image",
				Style:    discordgo.PrimaryButton,
				CustomID: "describe_image:" + m.ID,
			},
		}

		// Send a reply with the button
		_, err := s.ChannelMessageSendComplex(m.ChannelID, &discordgo.MessageSend{
			Content:    "Click the button to get an AI-generated description of the image.",
			Reference:  m.Reference(),
			Components: components,
		})
		if err != nil {
			log.Printf("Error sending message with button: %v", err)
		}
	}

	if m.Content == "!ping" {
		// ... rest of the function
	}

	// Release the lock (it will auto-expire after 5 seconds anyway)
	RedisClient.Del(ctx, lockKey)
}

func SetActiveChannels(channels []string) {
	ActiveChannels = channels
}
func isImage(url string) bool {
	extensions := []string{".jpg", ".jpeg", ".png", ".gif", ".webp"}
	lowercaseURL := strings.ToLower(url)
	for _, ext := range extensions {
		if strings.HasSuffix(lowercaseURL, ext) {
			return true
		}
	}
	return false
}

func handleInteraction(s *discordgo.Session, i *discordgo.InteractionCreate) {
	if i.Type == discordgo.InteractionMessageComponent {
		data := i.MessageComponentData()
		if strings.HasPrefix(data.CustomID, "describe_image:") {
			messageID := strings.TrimPrefix(data.CustomID, "describe_image:")
			message, err := s.ChannelMessage(i.ChannelID, messageID)
			if err != nil {
				log.Printf("Error fetching message: %v", err)
				return
			}

			if len(message.Attachments) > 0 {
				imageURL := message.Attachments[0].URL
				description := getImageDescription(imageURL)

				// Update the original message with the description
				_, err = s.ChannelMessageEditComplex(&discordgo.MessageEdit{
					ID:      i.Message.ID,
					Channel: i.ChannelID,
					Content: &i.Message.Content,
					Embed: &discordgo.MessageEmbed{
						Description: description,
					},
					Components: []discordgo.MessageComponent{},
				})
				if err != nil {
					log.Printf("Error updating message with description: %v", err)
				}
			}
		}
	}
}

func getImageDescription(imageURL string) string {
	client := openai.NewClient(os.Getenv("OPENAI_API_KEY"))
	ctx := context.Background()

	// Download the image
	resp, err := http.Get(imageURL)
	if err != nil {
		log.Printf("Error downloading image: %v", err)
		return "Error downloading image"
	}
	defer resp.Body.Close()

	imageData, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Error reading image data: %v", err)
		return "Error reading image data"
	}

	// Create a request to the OpenAI API
	req := openai.ImageAnalysisRequest{
		Image:  imageData,
		Model:  "gpt-4-vision-preview",
		Prompt: "Describe this image in detail.",
	}

	resp, err := client.AnalyzeImage(ctx, req)
	if err != nil {
		log.Printf("Error analyzing image: %v", err)
		return "Error analyzing image"
	}

	return resp.Choices[0].Text
}
