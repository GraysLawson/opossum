package handlers

import (
	"html/template"
	"net/http"

	"github.com/GraysLawson/opossum/website/models"
)

func LogsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodGet {
		logs := models.GetLogs()
		tmpl, err := template.ParseFiles("../templates/logs.html")
		if err != nil {
			http.Error(w, "Unable to load template", http.StatusInternalServerError)
			return
		}
		tmpl.Execute(w, logs)
		return
	}
}
