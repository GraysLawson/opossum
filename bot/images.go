package utils

import (
	"context"
	"io"
	"net/http"

	"discord-bot-project/bot/config"

	openai "github.com/sashabaranov/go-openai"
)

// GenerateImageDescription generates a description for an image using OpenAI
func GenerateImageDescription(imageURL string) (string, error) {
	// Download the image
	resp, err := http.Get(imageURL)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	imageData, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	// Use OpenAI API to generate a description
	client := openai.NewClient(config.BotConfig.OpenAIAPIKey)
	ctx := context.Background()

	// Create a request to generate a description
	req := openai.CompletionRequest{
		Model:     openai.GPT3TextDavinci003,
		Prompt:    "Describe the following image in detail.",
		MaxTokens: 100,
	}

	// Attach the image data
	req.Images = []openai.Image{
		{
			Data: imageData,
		},
	}

	respText, err := client.CreateCompletion(ctx, req)
	if err != nil {
		return "", err
	}
	return respText.Choices[0].Text, nil
}
