package services

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/GraysLawson/opossum/bot/config"
)

type OpenAIResponse struct {
	Choices []struct {
		Text string `json:"text"`
	} `json:"choices"`
}

func GenerateOpenAIDescription(imageURL string) (string, error) {
	apiKey := config.GetConfig().OpenAIAPIKey
	endpoint := "https://api.openai.com/v1/engines/davinci/completions"

	requestBody, err := json.Marshal(map[string]interface{}{
		"prompt":     fmt.Sprintf("Describe the following image in detail: %s", imageURL),
		"max_tokens": 150,
	})
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(requestBody))
	if err != nil {
		return "", err
	}

	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var openAIResp OpenAIResponse
	err = json.NewDecoder(resp.Body).Decode(&openAIResp)
	if err != nil {
		return "", err
	}

	if len(openAIResp.Choices) == 0 {
		return "No description available.", nil
	}

	return openAIResp.Choices[0].Text, nil
}
