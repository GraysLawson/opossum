# Discord Bot and Monitoring Websites

## Overview

This project includes a Discord bot written in Python and a Flask-based monitoring website. The bot can respond to specific commands, monitor image uploads, and interact with OpenAI's API to generate text descriptions. The website allows for configuration of the bot and displays activity logs.

## Features

### Discord Bot

- **Versioning System**: Auto-increment versioning on deployment.
- **Channel-Specific Activation**: Configurable active channels.
- **Commands**:
  - Responds to `!hello` with "Hello World" in active channels and DMs.
- **Image Monitoring**:
  - Monitors image uploads in active channels.
  - Provides a reaction (as a placeholder for a button) to generate OpenAI text descriptions.
- **Modular Design**: Structured for easy feature implementation.

### Website

- **Configuration Management**:
  - Configure OpenAI API key, Discord bot token, and active channels.
- **Activity Monitoring**:
  - View logs with severity filtering.
- **Logs Display**: Separate windows for website and bot logs.

## Setup Instructions

### Prerequisites

- **Docker** and **Docker Compose** installed.
- **Fly.io** account and CLI tools installed.
- **Python 3.9** if running locally.

### Setup

1. **Clone the repository**:

   ```bash
   git clone <repository_url>
   cd project
   ```

2. **Run the setup script**:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Set Environment Variables**:

   - Create a `.env` file in the root directory and add:

     ```dotenv
     DISCORD_TOKEN=your_discord_token
     OPENAI_API_KEY=your_openai_api_key
     ACTIVE_CHANNELS=channel_id1,channel_id2
     BOT_VERSION=0.1.0
     ```

4. **Build and Run with Docker Compose**:

   ```bash
   docker-compose up --build
   ```

5. **Access the Website**:

   - Open your browser and navigate to `http://localhost` to access the monitoring website.

### Deployment to Fly.io

1. **Login to Fly.io**:

   ```bash
   fly auth login
   ```

2. **Initialize Fly.io App**:

   ```bash
   fly launch
   ```

   - When prompted, choose to deploy now (or not, as per preference).

3. **Set Secrets**:

   ```bash
   fly secrets set DISCORD_TOKEN=your_discord_token
   fly secrets set OPENAI_API_KEY=your_openai_api_key
   fly secrets set ACTIVE_CHANNELS=channel_id1,channel_id2
   fly secrets set BOT_VERSION=0.1.0
   ```

4. **Deploy**:

   ```bash
   fly deploy
   ```

## Notes

- **Logging**: Implement logging functionality by integrating Python's `logging` module and configuring it to output to both console and file. Update the `logs.html` template to display logs accordingly.
- **Security**: Ensure that secret keys are handled securely and not exposed in logs or through the web interface.
- **OpenAI Integration**: The `generate_image_description` function is a placeholder. Implementation may vary based on OpenAI's API capabilities regarding image analysis.

## License

This project is licensed under the MIT License.
s