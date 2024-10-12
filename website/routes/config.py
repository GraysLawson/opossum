from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
import os
from utils import get_redis_connection
import json
import requests
import logging

config_bp = Blueprint('config', __name__)

@config_bp.route('/config')
@login_required
def config():
    return render_template('config.html')

@config_bp.route('/config/tokens', methods=['GET', 'POST'])
@login_required
def config_tokens():
    if request.method == 'POST':
        discord_token = request.form.get('discord_token')
        openai_api_key = request.form.get('openai_api_key')
        os.environ['DISCORD_TOKEN'] = discord_token
        os.environ['OPENAI_API_KEY'] = openai_api_key
        flash('Tokens and API keys updated successfully', 'success')
        return redirect(url_for('config.config_tokens'))
    else:
        discord_token = os.getenv('DISCORD_TOKEN', '')
        openai_api_key = os.getenv('OPENAI_API_KEY', '')
        return render_template('config_tokens.html', discord_token=discord_token, openai_api_key=openai_api_key)

@config_bp.route('/config/channels', methods=['GET', 'POST'])
@login_required
def config_channels():
    if request.method == 'POST':
        active_channels = request.form.getlist('active_channels')
        os.environ['ACTIVE_CHANNELS'] = ','.join(active_channels) if active_channels else ''
        flash('Active channels updated successfully', 'success')
        return redirect(url_for('config.config_channels'))
    else:
        active_channels = os.getenv('ACTIVE_CHANNELS', '').split(',')
        redis_client = get_redis_connection()
        channels_json = redis_client.get('discord_channels')
        channels = json.loads(channels_json) if channels_json else []

        # Ensure each channel has a 'guild_id' key
        for channel in channels:
            if 'guild_id' not in channel:
                logging.error(f"Channel data missing 'guild_id': {channel}")
                continue

        # This line was causing the error because selected_guild_id was not defined in this function
        # guild_channels = [channel for channel in channels if str(channel.get('guild_id')) == selected_guild_id]

        return render_template('config_channels.html', active_channels=active_channels, channels=channels)

@config_bp.route('/config/model', methods=['GET', 'POST'])
@login_required
def config_model():
    if request.method == 'POST':
        openai_model = request.form.get('openai_model')
        os.environ['OPENAI_MODEL'] = openai_model
        flash('OpenAI model updated successfully', 'success')
        return redirect(url_for('config.config_model'))
    else:
        openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        available_models = ['gpt-4o-mini', 'gpt-4o', 'chatgpt-4o-latest', 'gpt-4-vision-preview']
        return render_template('config_model.html', openai_model=openai_model, available_models=available_models)

@config_bp.route('/config/roles', methods=['GET', 'POST'])
@login_required
def config_roles():
    redis_client = get_redis_connection()

    if request.method == 'POST':
        selected_roles = request.form.getlist('roles')
        guild_id = request.form.get('guild_id')
        channel_id = request.form.get('channel_id')
        message_format = request.form.get('message_format', '')

        # Fetch all role_ids and role_names
        role_ids = request.form.getlist('role_ids')
        role_names = request.form.getlist('role_names')
        roles = {role_id: role_name for role_id, role_name in zip(role_ids, role_names) if role_id in selected_roles}

        # Prepare the config dictionary
        config_data = {
            'channel_id': channel_id,
            'roles': roles,
            'message_id': redis_client.get(f'role_assignment_message_id:{guild_id}').decode('utf-8') if redis_client.get(f'role_assignment_message_id:{guild_id}') else None
        }

        # Store the config in Redis
        redis_client.set(f'role_assignment_config:{guild_id}', json.dumps(config_data))

        flash('Role configuration updated successfully', 'success')
        return redirect(url_for('config.config_roles'))

    else:
        guild_ids_json = redis_client.get('bot_guild_ids')
        guild_ids = json.loads(guild_ids_json) if guild_ids_json else []
        selected_guild_id = request.args.get('guild_id', guild_ids[0] if guild_ids else None)

        if not selected_guild_id:
            flash('No guilds available for configuration.', 'error')
            return redirect(url_for('config.config'))

        # Fetch roles
        bot_token = os.getenv('DISCORD_TOKEN')
        headers = {'Authorization': f'Bot {bot_token}'}
        response = requests.get(f'https://discord.com/api/v10/guilds/{selected_guild_id}/roles', headers=headers)
        all_roles = response.json() if response.status_code == 200 else []

        # Fetch current config
        config_json = redis_client.get(f'role_assignment_config:{selected_guild_id}')
        if config_json:
            config = json.loads(config_json)
            selected_roles = config.get('roles', {})
            channel_id = config.get('channel_id', '')
            message_format = config.get('message_format', '')
        else:
            selected_roles = {}
            channel_id = ''
            message_format = ''

        # Fetch channels for the guild
        channels_json = redis_client.get('discord_channels')
        channels = json.loads(channels_json) if channels_json else []

        guild_channels = [channel for channel in channels if str(channel.get('guild_id')) == selected_guild_id]

        return render_template(
            'config_roles.html',
            guilds=guild_ids,
            selected_guild_id=selected_guild_id,
            all_roles=all_roles,
            selected_roles=selected_roles,
            channels=guild_channels,
            channel_id=channel_id,
            message_format=message_format
        )
