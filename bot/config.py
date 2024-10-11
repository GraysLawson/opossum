import os

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
VERSION = os.getenv('BOT_VERSION', '0.1.0')
ACTIVE_CHANNELS = os.getenv('ACTIVE_CHANNELS', '').split(',')

if not DISCORD_TOKEN:
    raise ValueError("Discord token not provided")

if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not provided")

if not ACTIVE_CHANNELS or ACTIVE_CHANNELS == ['']:
    ACTIVE_CHANNELS = None  # Defaults to all channels
else:
    ACTIVE_CHANNELS = [int(ch.strip()) for ch in ACTIVE_CHANNELS if ch.strip()]
