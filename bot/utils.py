import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from logger import logger

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_image_description(image_url):
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail:"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ],
                }
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating image description: {str(e)}")
        return "Sorry, I couldn't generate a description for this image."
