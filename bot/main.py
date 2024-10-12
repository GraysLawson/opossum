import discord
from discord.ext import commands
import os
from config import DISCORD_TOKEN, VERSION
from events import BotEvents
from commands import BotCommands
from logger import setup_logger
import asyncio
import signal
from utils import increment_version

# Set up the logger
logger = setup_logger()

async def main():
    logger.info("Starting bot...")
    intents = discord.Intents.default()
    intents.message_content = True
    intents.reactions = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    new_version = increment_version()
    bot.version = new_version
    
    logger.info(f"Bot version: {new_version}")

    await bot.add_cog(BotEvents(bot))
    await bot.add_cog(BotCommands(bot))

    # Set up signal handlers
    loop = asyncio.get_event_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, bot))
        )

    try:
        logger.info("Running bot...")
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
    finally:
        await bot.close()

async def shutdown(signal, bot):
    logger.info(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    await bot.close()
    logger.info("Bot shutdown complete.")

if __name__ == '__main__':
    asyncio.run(main())
