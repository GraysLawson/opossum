import discord
from discord.ext import commands
from config import ACTIVE_CHANNELS
from utils import generate_image_description
from logger import logger

class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.bot.user.name} has connected to Discord.")
        logger.info(f"Version: {self.bot.version}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if ACTIVE_CHANNELS and message.channel.id not in ACTIVE_CHANNELS:
            return

        if message.content.startswith('!hello'):
            logger.info(f"Received !hello command from {message.author}")
            await message.channel.send("Hello World")
            return

        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                    logger.info(f"Image uploaded by {message.author}: {attachment.filename}")
                    await message.add_reaction('🔍')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        if reaction.emoji == '🔍' and reaction.message.author != self.bot.user:
            for attachment in reaction.message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                    logger.info(f"Generating image description for {attachment.filename}")
                    description = generate_image_description(attachment.url)
                    await reaction.message.channel.send(f"Image Description: {description}")
                    break
