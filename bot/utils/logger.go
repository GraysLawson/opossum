package utils

import (
	"fmt"
	"log"
	"os"

	"github.com/GraysLawson/opossum/website/models"
)

type Logger struct {
	*log.Logger
}

var GlobalLogger *Logger

func InitLogger() {
	GlobalLogger = &Logger{
		Logger: log.New(os.Stdout, "", log.Ldate|log.Ltime|log.Lshortfile),
	}
}

func (l *Logger) Debug(v ...interface{}) {
	message := fmt.Sprint(v...)
	l.Output(2, "DEBUG: "+message)
	models.AddBotLog(message, "DEBUG")
}

func (l *Logger) Info(v ...interface{}) {
	message := fmt.Sprint(v...)
	l.Output(2, "INFO: "+message)
	models.AddBotLog(message, "INFO")
}

func (l *Logger) Error(v ...interface{}) {
	message := fmt.Sprint(v...)
	l.Output(2, "ERROR: "+message)
	models.AddBotLog(message, "ERROR")
}

func (l *Logger) Fatal(v ...interface{}) {
	message := fmt.Sprint(v...)
	l.Output(2, "FATAL: "+message)
	models.AddBotLog(message, "FATAL")
	os.Exit(1)
}
