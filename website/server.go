package website

import (
	"net/http"
)

// StartServer starts the HTTP server
func StartServer() error {
	http.HandleFunc("/", indexHandler)
	http.HandleFunc("/logs", logsHandler)
	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("website/static")))
	return http.ListenAndServe(":8080", nil)
}
