import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from logger import logger

client = openai.OpenAI(api_key=OPENAI_API_KEY)

import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from logger import logger

# Properly set the OpenAI API key
openai.api_key = OPENAI_API_KEY

async def generate_image_description(image_url, progress_callback):
    try:
        await progress_callback("Initializing image analysis...")
        # Note: Adjust the API call based on the actual OpenAI API for image analysis
        response = await openai.ChatCompletion.acreate(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": f"Describe this image in detail: {image_url}"
                }
            ],
            max_tokens=300
        )
        await progress_callback("Generating description...")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error generating image description: {str(e)}")
        return "Sorry, I couldn't generate a description for this image."
