package main

import (
	"log"

	"github.com/GraysLawson/website"
)

func main() {
	err := website.StartServer()
	if err != nil {
		log.Fatalf("Error starting server: %v", err)
	}
}
