import discord
from discord.ext import commands
import os
from config import DISCORD_TOKEN, VERSION
from events import BotEvents
from commands import BotCommands
from logger import setup_logger

# Set up the logger
logger = setup_logger()

async def main():
    logger.info("Starting bot...")
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.version = VERSION

    logger.info(f"Bot version: {VERSION}")

    await bot.add_cog(BotEvents(bot))
    await bot.add_cog(BotCommands(bot))

    logger.info("Running bot...")
    await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
