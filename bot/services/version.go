package services

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/GraysLawson/opossum/bot/utils"
)

var Version int

func InitVersioning() {
	// Auto-increment version on deployment by reading from a file
	data, err := os.ReadFile("version.txt")
	if err != nil {
		Version = 1
	} else {
		fmt.Sscanf(string(data), "%d", &Version)
		Version++
	}

	err = os.WriteFile("version.txt", []byte(fmt.Sprintf("%d", Version)), 0644)
	if err != nil {
		utils.GlobalLogger.Error("Failed to write version file:", err)
	}
}

func WaitForExit() {
	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c
	utils.GlobalLogger.Info("Shutting down gracefully...")
}
