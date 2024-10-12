import discord
from discord.ext import commands
from discord import ButtonStyle, ui
from config import ACTIVE_CHANNELS, REDIS_URL
from utils import generate_image_description
from logger import logger
import redis
import json
import asyncio

class DescribeImageButton(ui.Button):
    def __init__(self, image_url):
        super().__init__(style=ButtonStyle.primary, label="Describe Image")
        self.image_url = image_url

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        
        try:
            await interaction.edit_original_response(content="Analyzing the image...")
            description = await generate_image_description(self.image_url)
            
            # Format the description with a header
            formatted_description = "# 🖼️ Image Analysis\n\n" + description
            
            # Split the formatted description into chunks of 2000 characters or less
            chunks = [formatted_description[i:i+2000] for i in range(0, len(formatted_description), 2000)]
            
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await interaction.edit_original_response(content=chunk)
                else:
                    await interaction.followup.send(chunk)
            
            # Disable the button after description is sent
            self.disabled = True
            await interaction.edit_original_response(view=self.view)
        except Exception as e:
            logger.error(f"Error in DescribeImageButton callback: {str(e)}")
            await interaction.edit_original_response(content="Sorry, I couldn't generate a description for this image.")

class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis_client = redis.Redis.from_url(REDIS_URL)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.bot.user.name} has connected to Discord.")
        logger.info(f"Version: {self.bot.version}")
        await self.bot.change_presence(activity=discord.Game(name=f"v{self.bot.version}"))
        await self.update_channel_list()

    async def update_channel_list(self):
        channels = []
        for guild in self.bot.guilds:
            for channel in guild.channels:
                channels.append({
                    'id': str(channel.id),
                    'name': channel.name,
                    'guild_name': guild.name
                })
        self.redis_client.set('discord_channels', json.dumps(channels))
        logger.info(f"Updated channel list in Redis with {len(channels)} channels")

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
                    view = ui.View()
                    view.add_item(DescribeImageButton(attachment.url))
                    await message.reply("Click the button to get a description of the image:", view=view)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        if reaction.emoji == '🔍' and reaction.message.author != self.bot.user:
            for attachment in reaction.message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                    logger.info(f"Generating image description for {attachment.filename}")
                    description = await generate_image_description(attachment.url, lambda x: asyncio.sleep(0))
                    await reaction.message.channel.send(f"Image Description: {description}")
                    break
