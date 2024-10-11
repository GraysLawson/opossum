package models

import (
	"database/sql"

	"github.com/GraysLawson/opossum/website/utils"
	_ "github.com/lib/pq"
)

var db *sql.DB

func InitDB(databaseURL string) {
	var err error
	db, err = sql.Open("postgres", databaseURL)
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot connect to database:", err)
	}

	err = db.Ping()
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot ping database:", err)
	}
}

func UpdateConfig(openAIKey, discordKey string) {
	_, err := db.Exec("UPDATE configs SET openai_api_key=$1, discord_bot_key=$2 WHERE id=1", openAIKey, discordKey)
	if err != nil {
		utils.GlobalLogger.Error("Failed to update config:", err)
	}
}

func GetLogs() []string {
	rows, err := db.Query("SELECT log FROM logs ORDER BY created_at DESC LIMIT 100")
	if err != nil {
		utils.GlobalLogger.Error("Failed to retrieve logs:", err)
		return nil
	}
	defer rows.Close()

	var logs []string
	for rows.Next() {
		var logEntry string
		err := rows.Scan(&logEntry)
		if err != nil {
			utils.GlobalLogger.Error("Failed to scan log entry:", err)
			continue
		}
		logs = append(logs, logEntry)
	}
	return logs
}
