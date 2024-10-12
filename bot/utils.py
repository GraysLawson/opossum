import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from logger import logger
import asyncio
import base64
import requests
from openai import AsyncOpenAI
import redis
import os
import json

# Initialize the OpenAI client
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

redis_client = redis.Redis.from_url(os.environ['REDIS_URL'])

async def generate_image_description(image_url):
    try:
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
                        {"type": "text", "text": "Describe this image in detail and provide up to 3 potentially helpful links related to the main subject of the image. Format the response as: Description: [description] Links: [link1], [link2], [link3]"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        logger.info(f"Received response from OpenAI API: {response}")

        # Extract the description and links from the response
        content = response.choices[0].message.content.strip()
        description_part, links_part = content.split("Links:", 1)
        description = description_part.replace("Description:", "").strip()
        links = [link.strip() for link in links_part.split(",")]
        
        # Format the description with Discord markdown
        formatted_description = "**Image Description:**\n"
        formatted_description += "• " + description.replace(". ", ".\n• ") + "\n\n"
        formatted_description += "__**Helpful Links:**__\n"
        for i, link in enumerate(links, 1):
            formatted_description += f"{i}. {link}\n"
        
        logger.info(f"Generated response: {formatted_description}")
        
        return formatted_description
    except Exception as e:
        logger.error(f"Error generating image description: {str(e)}", exc_info=True)
        return "Sorry, I couldn't generate a description for this image."

def increment_version():
    current_version = redis_client.get('bot_version')
    if current_version is None:
        new_version = '1.0.0'
    else:
        major, minor, patch = map(int, current_version.decode().split('.'))
        patch += 1
        new_version = f"{major}.{minor}.{patch}"
    redis_client.set('bot_version', new_version)
    return new_version

async def update_guild_list(bot):
    guild_ids = [str(guild.id) for guild in bot.guilds]
    redis_client.set('bot_guild_ids', json.dumps(guild_ids))
    logger.info(f"Updated guild list in Redis: {guild_ids}")

async def update_guild_list(bot):
    guild_ids = [str(guild.id) for guild in bot.guilds]
    redis_client = redis.Redis.from_url(os.environ['REDIS_URL'])
    redis_client.set('bot_guild_ids', json.dumps(guild_ids))
    logger.info(f"Updated guild list in Redis: {guild_ids}")
