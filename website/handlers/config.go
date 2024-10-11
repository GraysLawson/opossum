package handlers

import (
	"html/template"
	"net/http"

	"github.com/GraysLawson/opossum/website/models"
)

func ConfigHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet {
		tmpl, err := template.ParseFiles("../templates/config.html")
		if err != nil {
			http.Error(w, "Unable to load template", http.StatusInternalServerError)
			return
		}
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
