package utils

import (
	"fmt"
	"log"
	"os"
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

func (l *Logger) Info(v ...interface{}) {
	l.Output(2, "INFO: "+fmt.Sprint(v...))
}

func (l *Logger) Error(v ...interface{}) {
	l.Output(2, "ERROR: "+fmt.Sprint(v...))
}

func (l *Logger) Fatal(v ...interface{}) {
	l.Output(2, "FATAL: "+fmt.Sprint(v...))
	os.Exit(1)
}

func (l *Logger) Debug(v ...interface{}) {
	l.Output(2, "DEBUG: "+fmt.Sprint(v...))
}
