import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from logger import logger
import asyncio
import base64
import requests
from openai import AsyncOpenAI

# Initialize the OpenAI client
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

async def generate_image_description(image_url, progress_callback):
    try:
        await progress_callback("Initializing image analysis...")
        
        # Download the image
        response = requests.get(image_url)
        image_data = base64.b64encode(response.content).decode('utf-8')
        
        logger.info(f"Using OpenAI model: {OPENAI_MODEL}")
        
        # Use the new async API with vision capabilities
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Use the vision-capable model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        logger.info(f"Received response from OpenAI API: {response}")
        
        await progress_callback("Generating description...")
        
        # Extract the description from the response
        description = response.choices[0].message.content.strip()
        
        logger.info(f"Generated description: {description}")
        
        return description
    except Exception as e:
        logger.error(f"Error generating image description: {str(e)}", exc_info=True)
        return "Sorry, I couldn't generate a description for this image."
