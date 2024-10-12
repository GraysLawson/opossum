import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from logger import logger
import asyncio

# Initialize the OpenAI client
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_image_description(image_url, progress_callback):
    try:
        await progress_callback("Initializing image analysis...")
        
        # Define the prompt
        prompt = f"Describe this image in detail: {image_url}"
        
        # Use the new async API
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300
        )
        
        await progress_callback("Generating description...")
        
        # Extract the description from the response
        description = response.choices[0].message.content.strip()
        
        return description
    except Exception as e:
        logger.error(f"Error generating image description: {str(e)}")
        return "Sorry, I couldn't generate a description for this image."
