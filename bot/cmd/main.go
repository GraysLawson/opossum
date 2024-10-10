package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/GraysLawson/bot/config"
	"github.com/GraysLawson/bot/services"
)

func main() {
	incrementVersion := flag.Bool("increment-version", false, "Increment version and exit")
	flag.Parse()

	newVersion := loadAndIncrementVersion()

	if *incrementVersion {
		fmt.Println("Version incremented to:", newVersion)
		return
	}

	// Set the new version as an environment variable
	os.Setenv("VERSION", newVersion)

	cfg := config.LoadConfig()

	// Set active channels
	services.SetActiveChannels(cfg.ActiveChannels)
	// Set the new version
	services.SetVersion(newVersion)

	// Initialize Database
	services.InitDatabase(cfg)

	// Initialize Redis
	services.InitRedis(cfg)

	// Initialize Discord Session
	dg := services.InitDiscordSession(cfg)
	defer dg.Close()

	// Update bot status
	services.UpdateStatus(dg)

	// Start HTTP server in a goroutine
	go startHTTPServer()

	// Wait for a termination signal
	sc := make(chan os.Signal, 1)
	signal.Notify(sc, syscall.SIGINT, syscall.SIGTERM, os.Interrupt)
	<-sc
}

func loadAndIncrementVersion() string {
	version := os.Getenv("VERSION")
	if version == "" {
		version = "1.0.0"
	}

	parts := strings.Split(version, ".")
	if len(parts) == 3 {
		patch, _ := strconv.Atoi(parts[2])
		patch++
		version = fmt.Sprintf("%s.%s.%d", parts[0], parts[1], patch)
	}

	// Log the new version
	log.Printf("New version: %s", version)

	return version
}

func startHTTPServer() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080" // Default port if not specified
	}

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	server := &http.Server{
		Addr:         ":" + port,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
	}

	log.Printf("Starting HTTP server on port %s", port)
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("HTTP server error: %v", err)
	}
}
