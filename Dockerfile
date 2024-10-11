# Use the official Go image
FROM golang:1.23.1-alpine

# Set the working directory
WORKDIR /app

# Copy the Go mod and sum files
COPY go.mod go.sum ./

# Download the dependencies
RUN go mod download

# Copy the source code
COPY . .

# Build the bot
RUN go build -o bot ./bot/main.go

# Build the website
RUN go build -o website ./website/main.go

# Expose port 8080 for the website
EXPOSE 8080

# Start both the bot and the website
CMD ["sh", "-c", "./bot & ./website"]
