package main

import (
	"net/http"

	"github.com/GraysLawson/opossum/website/config"
	"github.com/GraysLawson/opossum/website/handlers"
	"github.com/GraysLawson/opossum/website/models"
	"github.com/GraysLawson/opossum/website/utils"
)

func main() {
	utils.InitLogger()

	_, err := config.LoadConfig()
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot load config:", err)
	}

	models.InitDB()

	// Serve static files
	fs := http.FileServer(http.Dir("../static"))
	http.Handle("/static/", http.StripPrefix("/static/", fs))

	http.HandleFunc("/", handlers.HomeHandler)
	http.HandleFunc("/config", handlers.ConfigHandler)
	http.HandleFunc("/logs", handlers.LogsHandler)

	utils.GlobalLogger.Info("Website is running on port 8080")
	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		utils.GlobalLogger.Fatal("ListenAndServe:", err)
	}
}
