package models

import (
	"database/sql"
	"os"
	"time"

	"github.com/GraysLawson/opossum/website/utils"
	_ "github.com/lib/pq"
	"github.com/GraysLawson/opossum/common/logger"
)

var GlobalLogger = logger.GlobalLogger

func InitLogger() {
	logger.InitLogger()
}

var db *sql.DB

func InitDB() {
	utils.GlobalLogger.Debug("Initializing database connection")
	var err error
	db, err = sql.Open("postgres", os.Getenv("DATABASE_URL"))
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot connect to database:", err)
	}

	err = db.Ping()
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot ping database:", err)
	}

	// Create logs table if it doesn't exist
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS logs (
			id SERIAL PRIMARY KEY,
			log TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		utils.GlobalLogger.Fatal("Cannot create logs table:", err)
	}

	utils.GlobalLogger.Debug("Database connection established and logs table created successfully")
}

func UpdateConfig(openAIKey, discordKey string) {
	_, err := db.Exec("UPDATE configs SET openai_api_key=$1, discord_bot_key=$2 WHERE id=1", openAIKey, discordKey)
	if err != nil {
		utils.GlobalLogger.Error("Failed to update config:", err)
	}
}

func GetLogs() []string {
	utils.GlobalLogger.Debug("Attempting to retrieve logs from database")
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
	utils.GlobalLogger.Debug("Retrieved", len(logs), "log entries")
	return logs
}

func AddLog(logEntry string) error {
	_, err := db.Exec("INSERT INTO logs (log) VALUES ($1)", logEntry)
	if err != nil {
		utils.GlobalLogger.Error("Failed to insert log:", err)
		return err
	}
	return nil
}

func AddBotLog(logEntry string, severity string) error {
	_, err := db.Exec("INSERT INTO bot_logs (log, severity) VALUES ($1, $2)", logEntry, severity)
	if err != nil {
		utils.GlobalLogger.Error("Failed to insert bot log:", err)
		return err
	}
	return nil
}

func AddWebsiteLog(logEntry string, severity string) error {
	_, err := db.Exec("INSERT INTO website_logs (log, severity) VALUES ($1, $2)", logEntry, severity)
	if err != nil {
		utils.GlobalLogger.Error("Failed to insert website log:", err)
		return err
	}
	return nil
}

func GetBotLogs(severity string) []LogEntry {
	query := "SELECT log, severity, created_at FROM bot_logs"
	if severity != "" {
		query += " WHERE severity = $1"
	}
	query += " ORDER BY created_at DESC LIMIT 100"

	var rows *sql.Rows
	var err error
	if severity != "" {
		rows, err = db.Query(query, severity)
	} else {
		rows, err = db.Query(query)
	}

	if err != nil {
		utils.GlobalLogger.Error("Failed to retrieve bot logs:", err)
		return nil
	}
	defer rows.Close()

	return scanLogs(rows)
}

func GetWebsiteLogs(severity string) []LogEntry {
	query := "SELECT log, severity, created_at FROM website_logs"
	if severity != "" {
		query += " WHERE severity = $1"
	}
	query += " ORDER BY created_at DESC LIMIT 100"

	var rows *sql.Rows
	var err error
	if severity != "" {
		rows, err = db.Query(query, severity)
	} else {
		rows, err = db.Query(query)
	}

	if err != nil {
		utils.GlobalLogger.Error("Failed to retrieve website logs:", err)
		return nil
	}
	defer rows.Close()

	return scanLogs(rows)
}

func scanLogs(rows *sql.Rows) []LogEntry {
	var logs []LogEntry
	for rows.Next() {
		var entry LogEntry
		err := rows.Scan(&entry.Log, &entry.Severity, &entry.CreatedAt)
		if err != nil {
			utils.GlobalLogger.Error("Failed to scan log entry:", err)
			continue
		}
		logs = append(logs, entry)
	}
	return logs
}

type LogEntry struct {
	Log       string
	Severity  string
	CreatedAt time.Time
}