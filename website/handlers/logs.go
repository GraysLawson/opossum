package handlers

import (
	"html/template"
	"net/http"
	"github.com/GraysLawson/opossum/website/models"
	"github.com/GraysLawson/opossum/website/utils" // Assuming utils is in the same package
)

func LogsHandler(templates *template.Template) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			utils.GlobalLogger.Debug("Fetching logs")
			severity := r.URL.Query().Get("severity")
			botLogs := models.GetBotLogs(severity)
			websiteLogs := models.GetWebsiteLogs(severity)

			data := struct {
				BotLogs     []models.LogEntry
				WebsiteLogs []models.LogEntry
				Severity    string
			}{
				BotLogs:     botLogs,
				WebsiteLogs: websiteLogs,
				Severity:    severity,
			}

			err := templates.ExecuteTemplate(w, "logs.html", data)
			if err != nil {
				utils.GlobalLogger.Error("Unable to execute template:", err)
				http.Error(w, "Unable to load template", http.StatusInternalServerError)
				return
			}
		}
	}
}
