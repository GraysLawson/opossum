package main

import (
	"github.com/GraysLawson/opossum/bot/config"
	"github.com/GraysLawson/opossum/bot/handlers"
	"github.com/GraysLawson/opossum/bot/services"
	"github.com/GraysLawson/opossum/bot/utils"
)

func main() {
	utils.InitLogger()

	cfg, err := config.LoadConfig()
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot load config:", err)
	}

	services.InitVersioning()

	discordSession, err := handlers.InitializeDiscord(cfg)
	if err != nil {
		utils.GlobalLogger.Fatal("Failed to initialize Discord session:", err)
	}

	discordSession.AddHandler(handlers.MessageCreate)
	discordSession.AddHandler(handlers.ImageUpload)

	err = discordSession.Open()
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot open Discord session:", err)
	}

	utils.GlobalLogger.Info("Bot is now running. Press CTRL+C to exit.")
	services.WaitForExit()
}
