import os

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
VERSION = os.environ['BOT_VERSION']
ACTIVE_CHANNELS = os.environ.get('ACTIVE_CHANNELS', '').split(',')
DATABASE_URL = os.environ['DATABASE_URL']

if not DISCORD_TOKEN:
    raise ValueError("Discord token not provided")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not provided")

if not ACTIVE_CHANNELS or ACTIVE_CHANNELS == ['']:
    ACTIVE_CHANNELS = None  # Defaults to all channels
else:
    ACTIVE_CHANNELS = [int(ch.strip()) for ch in ACTIVE_CHANNELS if ch.strip()]
