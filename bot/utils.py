import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def generate_image_description(image_url):
    # Placeholder function to generate description using OpenAI
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Describe the following image: {image_url}",
        max_tokens=50
    )
    return response.choices[0].text.strip()
