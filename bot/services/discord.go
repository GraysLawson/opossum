package services

import (
	"fmt"
	"log"

	"github.com/GraysLawson/bot/config"
	"github.com/GraysLawson/bot/models"
	"github.com/bwmarrin/discordgo"
	"github.com/go-redis/redis/v8"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var DB *gorm.DB
var Version string
var ActiveChannels []string
var RedisClient *redis.Client

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
	// Connect to the default 'postgres' database first
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=postgres sslmode=%s",
		cfg.DBHost, cfg.DBPort, cfg.DBUser, cfg.DBPassword, cfg.DBSSLMode)
	tempDB, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatalf("failed to connect to postgres database: %v", err)
	}

	// Check if the 'opossum' database exists
	var dbExists int
	tempDB.Raw("SELECT 1 FROM pg_database WHERE datname = 'opossum'").Scan(&dbExists)

	if dbExists == 0 {
		// Create the 'opossum' database if it doesn't exist
		tempDB.Exec("CREATE DATABASE opossum")
	}

	// Now connect to the 'opossum' database
	dsn = fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
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
	dg.AddHandler(handleInteraction)

	dg.Identify.Intents = discordgo.IntentsGuildMessages | discordgo.IntentsMessageContent

	err = dg.Open()
	if err != nil {
		log.Fatalf("error opening connection: %v", err)
	}

	UpdateStatus(dg)

	log.Println("Bot is now running. Press CTRL-C to exit.")
	return dg
}

func SetActiveChannels(channels []string) {
	ActiveChannels = channels
}
