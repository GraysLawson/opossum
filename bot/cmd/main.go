package main

import (
	"github.com/GraysLawson/opossum/bot/config"
	"github.com/GraysLawson/opossum/bot/handlers"
	"github.com/GraysLawson/opossum/bot/services"
	"github.com/GraysLawson/opossum/bot/utils"
)

func main() {
	utils.InitLogger()
	utils.GlobalLogger.Debug("Logger initialized")

	utils.GlobalLogger.Debug("Loading configuration")
	cfg, err := config.LoadConfig()
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot load config:", err)
	}
	utils.GlobalLogger.Debug("Configuration loaded successfully")

	utils.GlobalLogger.Debug("Initializing versioning")
	services.InitVersioning()
	utils.GlobalLogger.Debug("Versioning initialized. Current version:", services.Version)

	utils.GlobalLogger.Debug("Initializing Discord session")
	discordSession, err := handlers.InitializeDiscord(cfg)
	if err != nil {
		utils.GlobalLogger.Fatal("Failed to initialize Discord session:", err)
	}
	utils.GlobalLogger.Debug("Discord session initialized successfully")

	utils.GlobalLogger.Debug("Adding message handler")
	discordSession.AddHandler(handlers.MessageCreate)
	utils.GlobalLogger.Debug("Adding image upload handler")
	discordSession.AddHandler(handlers.ImageUpload)

	utils.GlobalLogger.Debug("Opening Discord session")
	err = discordSession.Open()
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot open Discord session:", err)
	}
	utils.GlobalLogger.Info("Bot is now running. Press CTRL+C to exit.")

	services.WaitForExit()
}
