package handlers

import (
	"html/template"
	"net/http"
)

func HomeHandler(templates *template.Template) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		err := templates.ExecuteTemplate(w, "index.html", nil)
		if err != nil {
			http.Error(w, "Unable to load template", http.StatusInternalServerError)
			return
		}
	}
}
