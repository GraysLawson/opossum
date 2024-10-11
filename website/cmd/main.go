package main

import (
	"log"
	"net/http"

	"github.com/GraysLawson/opossum/website/config"
	"github.com/GraysLawson/opossum/website/handlers"
	"github.com/GraysLawson/opossum/website/models"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatal("Cannot load config:", err)
	}

	models.InitDB(cfg.DatabaseURL)

	// Serve static files
	fs := http.FileServer(http.Dir("../static"))
	http.Handle("/static/", http.StripPrefix("/static/", fs))

	http.HandleFunc("/", handlers.Home)
	http.HandleFunc("/config", handlers.ConfigHandler)
	http.HandleFunc("/logs", handlers.LogsHandler)

	log.Println("Website is running on port 8080")
	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		log.Fatal("ListenAndServe:", err)
	}
}
