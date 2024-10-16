import os

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
VERSION = os.environ['BOT_VERSION']
ACTIVE_CHANNELS = os.environ.get('ACTIVE_CHANNELS', '').split(',')
REDIS_URL = os.environ['REDIS_URL']
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

DISCORD_CLIENT_ID = os.environ['DISCORD_CLIENT_ID']
DISCORD_CLIENT_SECRET = os.environ['DISCORD_CLIENT_SECRET']
DISCORD_REDIRECT_URI = os.environ['DISCORD_REDIRECT_URI']

DISCORD_GUILD_ID = os.environ.get('DISCORD_GUILD_ID')

if not DISCORD_TOKEN:
    raise ValueError("Discord token not provided")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not provided")

if not ACTIVE_CHANNELS or ACTIVE_CHANNELS == ['']:
    ACTIVE_CHANNELS = None  # Defaults to all channels
else:
    ACTIVE_CHANNELS = [int(ch.strip()) for ch in ACTIVE_CHANNELS if ch.strip()]
