import discord
from discord.ext import commands
import os
from config import DISCORD_TOKEN, VERSION
from events import BotEvents
from commands import BotCommands
from logger import setup_logger

# Set up the logger
logger = setup_logger()

def main():
    logger.info("Starting bot...")
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.version = VERSION

    logger.info(f"Bot version: {VERSION}")

    bot.add_cog(BotEvents(bot))
    bot.add_cog(BotCommands(bot))

    logger.info("Running bot...")
    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
