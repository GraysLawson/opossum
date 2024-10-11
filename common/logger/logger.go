package logger

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

func (l *Logger) Debug(v ...interface{}) {
	message := fmt.Sprint(v...)
	l.Output(2, "DEBUG: "+message)
}

func (l *Logger) Info(v ...interface{}) {
	message := fmt.Sprint(v...)
	l.Output(2, "INFO: "+message)
}

func (l *Logger) Error(v ...interface{}) {
	message := fmt.Sprint(v...)
	l.Output(2, "ERROR: "+message)
}

func (l *Logger) Fatal(v ...interface{}) {
	message := fmt.Sprint(v...)
	l.Output(2, "FATAL: "+message)
	os.Exit(1)
}
