from flask_discord import DiscordOAuth2Session

discord = DiscordOAuth2Session()

def init_discord(app):
    discord.init_app(app)

