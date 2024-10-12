import discord
from discord.ext import commands, tasks
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

class RoleAssignmentButton(ui.Button):
    def __init__(self, role_id: int, label: str):
        super().__init__(style=ButtonStyle.primary, label=label)
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if role is None:
            await interaction.response.send_message("Role not found.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"Removed {role.name} role.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"Added {role.name} role.", ephemeral=True)

class RoleAssignmentView(ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        for role_id, label in roles.items():
            self.add_item(RoleAssignmentButton(int(role_id), label))

class BotEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis_client = redis.Redis.from_url(REDIS_URL)
        self.update_role_assignments.start()

    def cog_unload(self):
        self.update_role_assignments.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.bot.user.name} has connected to Discord.")
        logger.info(f"Version: {self.bot.version}")
        await self.bot.change_presence(activity=discord.Game(name=f"v{self.bot.version}"))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.update_channel_list()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.update_channel_list()

   
async def update_channel_list(self):
    channels = []
    for guild in self.bot.guilds:
        for channel in guild.channels:
            # Consider only text channels
            if isinstance(channel, discord.TextChannel):
                channels.append({
                    'id': str(channel.id),
                    'name': channel.name,
                    'guild_id': str(guild.id),
                    'guild_name': guild.name
                })
    self.redis_client.set('discord_channels', json.dumps(channels))
    logger.info(f"Updated channel list in Redis with {len(channels)} channels")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if ACTIVE_CHANNELS and str(message.channel.id) not in ACTIVE_CHANNELS:
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

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def create_role_message(self, ctx):
        guild_id = str(ctx.guild.id)
        config_json = self.redis_client.get(f'role_assignment_config:{guild_id}')
        if not config_json:
            await ctx.send("No roles configured for assignment. Please configure them on the website.")
            return

        config = json.loads(config_json)
        roles = config.get('roles', {})
        channel_id = config.get('channel_id')
        message_format = config.get('message_format', "Assign yourself a role by clicking a button below:")

        channel = self.bot.get_channel(int(channel_id))
        if channel is None:
            await ctx.send("Configured channel not found.")
            return

        view = RoleAssignmentView(roles)
        message_content = message_format

        message = await channel.send(message_content, view=view)
        config['message_id'] = str(message.id)
        self.redis_client.set(f'role_assignment_config:{guild_id}', json.dumps(config))
        await ctx.send(f"Role assignment message created in {channel.mention}")

    @tasks.loop(minutes=5)
    async def update_role_assignments(self):
        try:
            all_keys = self.redis_client.keys('role_assignment_config:*')
            for key in all_keys:
                guild_id = key.decode().split(':')[1]
                config_json = self.redis_client.get(key)
                if not config_json:
                    continue
                config = json.loads(config_json)
                channel_id = config.get('channel_id')
                message_format = config.get('message_format', "Assign yourself a role by clicking the buttons below:")
                roles = config.get('roles', {})
                message_id = config.get('message_id')

                channel = self.bot.get_channel(int(channel_id))
                if channel is None:
                    logger.error(f"Channel ID {channel_id} not found for guild {guild_id}")
                    continue

                if message_id:
                    try:
                        message = await channel.fetch_message(int(message_id))
                        # Update message content and view if necessary
                        view = RoleAssignmentView(roles)
                        if message.content != message_format:
                            await message.edit(content=message_format, view=view)
                    except discord.NotFound:
                        logger.warning(f"Message ID {message_id} not found in channel {channel_id}. Creating a new message.")
                        view = RoleAssignmentView(roles)
                        message = await channel.send(message_format, view=view)
                        config['message_id'] = str(message.id)
                        self.redis_client.set(key, json.dumps(config))
                else:
                    # No message_id, create a new message
                    view = RoleAssignmentView(roles)
                    message = await channel.send(message_format, view=view)
                    config['message_id'] = str(message.id)
                    self.redis_client.set(key, json.dumps(config))
        except Exception as e:
            logger.error(f"Error in update_role_assignments: {str(e)}")

    @update_role_assignments.before_loop
    async def before_update_role_assignments(self):
        await self.bot.wait_until_ready()