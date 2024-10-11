package website

import (
	"html/template"
	"net/http"
	"os"

	"github.com/GraysLawson/bot/config"
)

// indexHandler handles the index page
func indexHandler(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFiles("website/templates/index.html")
	if err != nil {
		http.Error(w, "Error parsing template", http.StatusInternalServerError)
		return
	}
	data := struct {
		ActiveChannels []string
		Version        string
	}{
		ActiveChannels: config.BotConfig.ActiveChannels,
		Version:        config.BotConfig.Version,
	}
	tmpl.Execute(w, data)
}

// logsHandler handles the logs page
func logsHandler(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFiles("website/templates/logs.html")
	if err != nil {
		http.Error(w, "Error parsing template", http.StatusInternalServerError)
		return
	}
	logData, err := os.ReadFile("bot.log")
	if err != nil {
		http.Error(w, "Error reading log file", http.StatusInternalServerError)
		return
	}
	data := struct {
		Logs string
	}{
		Logs: string(logData),
	}
	tmpl.Execute(w, data)
}
