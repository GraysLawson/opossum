#!/bin/bash

echo "Setting up the Discord Bot Project..."

# Install dependencies
echo "Installing Go modules..."
go mod tidy

# Build the bot
echo "Building the bot..."
go build -o bot/bot ./bot/main.go

# Build the website
echo "Building the website..."
go build -o website/website ./website/main.go

# Set execution permissions
chmod +x bot/bot
chmod +x website/website

# Increment version
echo "Incrementing version..."
go run bot/version.go

echo "Setup complete."
