#!/bin/bash

# Exit on any error
set -e

# Create project directories
mkdir -p opossum/{bot,website,scripts}

# Navigate to bot directory
cd opossum/bot

# Initialize Go module
go mod init github.com/GraysLawson/opossum/bot

# Create necessary directories
mkdir -p cmd config handlers services utils

# Create main.go for bot
cat > cmd/main.go <<EOL
package main

import (
	"github.com/GraysLawson/opossum/bot/config"
	"github.com/GraysLawson/opossum/bot/handlers"
	"github.com/GraysLawson/opossum/bot/services"
	"github.com/GraysLawson/opossum/bot/utils"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		utils.Logger.Fatal("Cannot load config:", err)
	}

	services.InitVersioning()

	discordSession, err := handlers.InitializeDiscord(cfg)
	if err != nil {
		utils.Logger.Fatal("Failed to initialize Discord session:", err)
	}

	discordSession.AddHandler(handlers.MessageCreate)
	discordSession.AddHandler(handlers.ImageUpload)

	err = discordSession.Open()
	if err != nil {
		utils.Logger.Fatal("Cannot open Discord session:", err)
	}

	utils.Logger.Info("Bot is now running. Press CTRL+C to exit.")
	services.WaitForExit()
}
EOL

# Create config.go for bot
cat > config/config.go <<EOL
package config

import (
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	BotToken          string
	OpenAIAPIKey      string
	ActiveChannels    []string
	Version           int
}

func LoadConfig() (*Config, error) {
	err := godotenv.Load("../.env")
	if err != nil {
		return nil, err
	}

	activeChannels := []string{}
	if os.Getenv("ACTIVE_CHANNELS") != "" {
		activeChannels = append(activeChannels, os.Getenv("ACTIVE_CHANNELS"))
	} else {
		activeChannels = append(activeChannels, "all")
	}

	version := 1 // This should be auto-incremented during deployment

	return &Config{
		BotToken:       os.Getenv("DISCORD_BOT_TOKEN"),
		OpenAIAPIKey:   os.Getenv("OPENAI_API_KEY"),
		ActiveChannels: activeChannels,
		Version:        version,
	}, nil
}
EOL

# Create handlers for bot
cat > handlers/message.go <<EOL
package handlers

import (
	"strings"

	"github.com/bwmarrin/discordgo"
	"github.com/GraysLawson/opossum/bot/config"
	"github.com/GraysLawson/opossum/bot/services"
	"github.com/GraysLawson/opossum/bot/utils"
)

var cfg *config.Config

func InitializeDiscord(configuration *config.Config) (*discordgo.Session, error) {
	cfg = configuration
	dg, err := discordgo.New("Bot " + cfg.BotToken)
	if err != nil {
		return nil, err
	}
	return dg, nil
}

func MessageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	if m.Author.ID == s.State.User.ID {
		return
	}

	if !isChannelActive(m.ChannelID) {
		return
	}

	if strings.HasPrefix(m.Content, "!hello") {
		_, err := s.ChannelMessageSend(m.ChannelID, "Hello World")
		if err != nil {
			utils.Logger.Error("Failed to send message:", err)
		}
	}
}

func isChannelActive(channelID string) bool {
	if len(cfg.ActiveChannels) == 0 || (len(cfg.ActiveChannels) == 1 && cfg.ActiveChannels[0] == "all") {
		return true
	}
	for _, id := range cfg.ActiveChannels {
		if id == channelID {
			return true
		}
	}
	return false
}
EOL

cat > handlers/image.go <<EOL
package handlers

import (
	"github.com/bwmarrin/discordgo"
	"github.com/GraysLawson/opossum/bot/services"
	"github.com/GraysLawson/opossum/bot/utils"
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
				utils.Logger.Error("Failed to send message with button:", err)
			}

			// Handle button interaction
			s.AddHandler(func(s *discordgo.Session, i *discordgo.InteractionCreate) {
				if i.Type != discordgo.InteractionMessageComponent {
					return
				}

				if i.MessageComponentData().CustomID == "generate_description_"+attachment.ID {
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
EOL

# Create services for bot
cat > services/version.go <<EOL
package services

import (
	"os"
	"os/signal"
	"syscall"

	"github.com/GraysLawson/opossum/bot/utils"
)

var Version int

func InitVersioning() {
	// Logic to auto-increment version on deployment
	// This could be implemented using build-time variables or external versioning service
	// For simplicity, we'll read from a file

	data, err := os.ReadFile("version.txt")
	if err != nil {
		Version = 1
	} else {
		fmt.Sscanf(string(data), "%d", &Version)
		Version++
	}

	err = os.WriteFile("version.txt", []byte(fmt.Sprintf("%d", Version)), 0644)
	if err != nil {
		utils.Logger.Error("Failed to write version file:", err)
	}
}

func WaitForExit() {
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c
}
EOL

cat > services/openai.go <<EOL
package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/GraysLawson/opossum/bot/config"
	"github.com/GraysLawson/opossum/bot/utils"
)

type OpenAIResponse struct {
	Choices []struct {
		Text string `json:"text"`
	} `json:"choices"`
}

func GenerateOpenAIDescription(imageURL string) (string, error) {
	apiKey := config.GetConfig().OpenAIAPIKey
	endpoint := "https://api.openai.com/v1/engines/davinci/completions"

	requestBody, err := json.Marshal(map[string]interface{}{
		"prompt": fmt.Sprintf("Describe the following image in detail: %s", imageURL),
		"max_tokens": 150,
	})
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(requestBody))
	if err != nil {
		return "", err
	}

	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var openAIResp OpenAIResponse
	err = json.NewDecoder(resp.Body).Decode(&openAIResp)
	if err != nil {
		return "", err
	}

	if len(openAIResp.Choices) == 0 {
		return "No description available.", nil
	}

	return openAIResp.Choices[0].Text, nil
}
EOL

# Create logger utility
cat > utils/logger.go <<EOL
package utils

import (
	"log"
	"os"
)

var Logger *log.Logger

func InitLogger() {
	Logger = log.New(os.Stdout, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)
}
EOL

# Initialize logger in main.go (update cmd/main.go)

# Note: Add the following lines at the beginning of the main function in cmd/main.go
"""
utils.InitLogger()
"""

# Navigate to website directory
cd ../website

# Initialize Go module for website
go mod init github.com/GraysLawson/opossum/website

# Create necessary directories
mkdir -p cmd handlers models templates static/css static/js config

# Create main.go for website
cat > cmd/main.go <<EOL
package main

import (
	"github.com/GraysLawson/opossum/website/config"
	"github.com/GraysLawson/opossum/website/handlers"
	"github.com/GraysLawson/opossum/website/models"
	"github.com/GraysLawson/opossum/website/utils"
	"log"
	"net/http"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatal("Cannot load config:", err)
	}

	models.InitDB(cfg.DatabaseURL)

	http.HandleFunc("/", handlers.Home)
	http.HandleFunc("/config", handlers.ConfigHandler)
	http.HandleFunc("/logs", handlers.LogsHandler)

	log.Println("Website is running on port 8080")
	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal("ListenAndServe:", err)
	}
}
EOL

# Create config.go for website
cat > config/config.go <<EOL
package config

import (
	"os"

	"github.com/joho/godotenv"
)

type Config struct {
	OpenAIAPIKey string
	DiscordBotKey string
	DatabaseURL string
}

func LoadConfig() (*Config, error) {
	err := godotenv.Load("../.env")
	if err != nil {
		return nil, err
	}

	return &Config{
		OpenAIAPIKey: os.Getenv("OPENAI_API_KEY"),
		DiscordBotKey: os.Getenv("DISCORD_BOT_KEY"),
		DatabaseURL: os.Getenv("DATABASE_URL"),
	}, nil
}
EOL

# Create handlers for website
cat > handlers/config.go <<EOL
package handlers

import (
	"html/template"
	"net/http"

	"github.com/GraysLawson/opossum/website/config"
	"github.com/GraysLawson/opossum/website/models"
)

func ConfigHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet {
		tmpl, _ := template.ParseFiles("../templates/config.html")
		tmpl.Execute(w, nil)
		return
	}

	if r.Method == http.MethodPost {
		openAIKey := r.FormValue("openai_api_key")
		discordKey := r.FormValue("discord_bot_key")

		// Update in database or config
		models.UpdateConfig(openAIKey, discordKey)

		http.Redirect(w, r, "/config", http.StatusSeeOther)
		return
	}
}
EOL

cat > handlers/logs.go <<EOL
package handlers

import (
	"html/template"
	"net/http"

	"github.com/GraysLawson/opossum/website/models"
)

func LogsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet {
		logs := models.GetLogs()
		tmpl, _ := template.ParseFiles("../templates/logs.html")
		tmpl.Execute(w, logs)
		return
	}
}
EOL

cat > handlers/auth.go <<EOL
package handlers

import (
	"net/http"
)

// Placeholder for authentication handlers
func LoginHandler(w http.ResponseWriter, r *http.Request) {
	// Implement authentication
}

func LogoutHandler(w http.ResponseWriter, r *http.Request) {
	// Implement logout
}
EOL

# Create models for website
cat > models/models.go <<EOL
package models

import (
	"database/sql"
	"log"

	_ "github.com/lib/pq"
)

var db *sql.DB

func InitDB(databaseURL string) {
	var err error
	db, err = sql.Open("postgres", databaseURL)
	if err != nil {
		log.Fatal("Cannot connect to database:", err)
	}

	err = db.Ping()
	if err != nil {
		log.Fatal("Cannot ping database:", err)
	}
}

func UpdateConfig(openAIKey, discordKey string) {
	_, err := db.Exec("UPDATE configs SET openai_api_key=$1, discord_bot_key=$2 WHERE id=1", openAIKey, discordKey)
	if err != nil {
		log.Println("Failed to update config:", err)
	}
}

func GetLogs() []string {
	rows, err := db.Query("SELECT log FROM logs ORDER BY created_at DESC LIMIT 100")
	if err != nil {
		log.Println("Failed to retrieve logs:", err)
		return nil
	}
	defer rows.Close()

	var logs []string
	for rows.Next() {
		var logEntry string
		err := rows.Scan(&logEntry)
		if err != nil {
			log.Println("Failed to scan log entry:", err)
			continue
		}
		logs = append(logs, logEntry)
	}
	return logs
}
EOL

# Create templates for website
cat > templates/index.html <<EOL
<!DOCTYPE html>
<html>
<head>
    <title>Discord Bot Dashboard</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <h1>Welcome to the Discord Bot Dashboard</h1>
    <nav>
        <a href="/config">Configuration</a> |
        <a href="/logs">Logs</a>
    </nav>
</body>
</html>
EOL

cat > templates/config.html <<EOL
<!DOCTYPE html>
<html>
<head>
    <title>Configure Bot</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <h1>Bot Configuration</h1>
    <form method="POST">
        <label for="openai_api_key">OpenAI API Key:</label><br>
        <input type="text" id="openai_api_key" name="openai_api_key"><br><br>
        <label for="discord_bot_key">Discord Bot Key:</label><br>
        <input type="text" id="discord_bot_key" name="discord_bot_key"><br><br>
        <input type="submit" value="Update">
    </form>
</body>
</html>
EOL

cat > templates/logs.html <<EOL
<!DOCTYPE html>
<html>
<head>
    <title>Bot Logs</title>
    <link rel="stylesheet" href="/static/css/styles.css">
</head>
<body>
    <h1>Bot Activity Logs</h1>
    <ul>
        {{range .}}
            <li>{{.}}</li>
        {{end}}
    </ul>
</body>
</html>
EOL

# Create static files for website
cat > static/css/styles.css <<EOL
body {
    font-family: Arial, sans-serif;
    margin: 20px;
}

nav a {
    margin-right: 15px;
    text-decoration: none;
    color: #333;
}

h1 {
    color: #555;
}
EOL

cat > static/js/scripts.js <<EOL
// Add any JavaScript if needed
EOL

# Navigate back to root
cd ../../

# Create .env.example
cat > .env.example <<EOL
# Discord Bot Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
ACTIVE_CHANNELS=channel_id1,channel_id2

# Website Configuration
DISCORD_BOT_KEY=your_discord_bot_key_here
DATABASE_URL=postgres://user:password@localhost:5432/discord_bot_db
EOL

# Create fly.toml for Fly.io deployment
cat > fly.toml <<EOL
app = "your-app-name"

[build]
  builder = "heroku/buildpacks:20"
  buildpacks = [
    "https://github.com/jbeder/heroku-buildpack-go"
  ]

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[EOL

# Make setup script executable
chmod +x scripts/setup.sh

# Output completion message
echo "Project setup initialized. Please configure the .env file based on .env.example and run the setup.sh script."
