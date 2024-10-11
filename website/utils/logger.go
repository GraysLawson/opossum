package utils

import (
	"github.com/GraysLawson/opossum/common/logger"
)

var GlobalLogger = logger.GlobalLogger

func InitLogger() {
	logger.InitLogger()
}
