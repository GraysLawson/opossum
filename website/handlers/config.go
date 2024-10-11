package handlers

import (
	"html/template"
	"net/http"

	"github.com/GraysLawson/opossum/website/models"
)

func ConfigHandler(templates *template.Template) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodGet {
			err := templates.ExecuteTemplate(w, "config.html", nil)
			if err != nil {
				http.Error(w, "Unable to load template", http.StatusInternalServerError)
				return
			}
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
}
