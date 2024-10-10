package main

import (
    "os"
    "os/signal"
    "syscall"

    "github.com/yourusername/bot/config"
    "github.com/yourusername/bot/services"
)

func main() {
    cfg := config.LoadConfig()

    // Initialize Database
    services.InitDatabase(cfg)

    // Initialize Discord Session
    dg := services.InitDiscordSession(cfg)
    defer dg.Close()

    // Wait for a termination signal
    sc := make(chan os.Signal, 1)
    signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt, os.Kill)
    <-sc
}
