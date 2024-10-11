import discord
from discord.ext import commands
from config import DISCORD_TOKEN, VERSION
from events import BotEvents
from commands import BotCommands

def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)
    bot.version = VERSION

    bot.add_cog(BotEvents(bot))
    bot.add_cog(BotCommands(bot))

    bot.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
