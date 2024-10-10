package services

import (
	"fmt"
	"log"

	"github.com/GraysLawson/bot/config"
	"github.com/GraysLawson/bot/models"
	"github.com/bwmarrin/discordgo"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB

func InitDatabase(cfg config.Config) {
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		cfg.DBHost, cfg.DBPort, cfg.DBUser, cfg.DBPassword, cfg.DBName, cfg.DBSSLMode)
	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect database: %v", err)
	}

	// Migrate the schema
	err = DB.AutoMigrate(&models.User{}, &models.UserSettings{})
	if err != nil {
		log.Fatalf("failed to migrate database: %v", err)
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

	log.Println("Bot is now running. Press CTRL-C to exit.")
	return dg
}

func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	// Ignore messages from the bot itself
	if m.Author.ID == s.State.User.ID {
		return
	}

	if m.Content == "!ping" {
		s.ChannelMessageSend(m.ChannelID, "Pong!")
	}

	// Add more command handlers here
}
