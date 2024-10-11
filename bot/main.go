package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"discord-bot-project/bot"
	"discord-bot-project/bot/config"
)

func main() {
	err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	bot.Session, err = bot.NewBotSession(config.BotConfig.Token)
	if err != nil {
		log.Fatalf("Error creating Discord session: %v", err)
	}

	bot.RegisterHandlers()

	defer bot.Session.Close()

	fmt.Println("Bot is now running. Press CTRL+C to exit.")
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-stop

	fmt.Println("Bot is shutting down.")
}
