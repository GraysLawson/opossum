package utils

import (
	"fmt"
	"os"
	"time"
)

// LogImageUpload logs the image upload event
func LogImageUpload(channelID, username, imageURL string) {
	logEntry := fmt.Sprintf("%s [ChannelID: %s] [User: %s] Image Uploaded: %s\n",
		time.Now().Format(time.RFC3339), channelID, username, imageURL)
	f, err := os.OpenFile("bot.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println("Error opening log file:", err)
		return
	}
	defer f.Close()
	_, err = f.WriteString(logEntry)
	if err != nil {
		fmt.Println("Error writing to log file:", err)
	}
}
