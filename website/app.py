from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = psycopg2.extras.DictCursor
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bot_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level VARCHAR(10),
                message TEXT
            )
        """)
        conn.commit()
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def logs():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM bot_logs ORDER BY timestamp DESC LIMIT 100')
        logs = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('logs.html', logs=logs)
    except Exception as e:
        app.logger.error(f"An error occurred while fetching logs: {str(e)}")
        return render_template('logs.html', logs=[], error="An error occurred while fetching logs.")

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        discord_token = request.form.get('discord_token')
        openai_api_key = request.form.get('openai_api_key')
        active_channels = request.form.get('active_channels')

        # Update the environment variables accordingly
        os.environ['DISCORD_TOKEN'] = discord_token
        os.environ['OPENAI_API_KEY'] = openai_api_key
        os.environ['ACTIVE_CHANNELS'] = active_channels

        # You may want to persist these changes in a safe way (e.g., database or config file)
        # For security reasons, avoid storing sensitive information in plain text

        return redirect(url_for('config'))
    else:
        discord_token = os.getenv('DISCORD_TOKEN', '')
        openai_api_key = os.getenv('OPENAI_API_KEY', '')
        active_channels = os.getenv('ACTIVE_CHANNELS', '')
        return render_template('config.html', discord_token=discord_token, openai_api_key=openai_api_key, active_channels=active_channels)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
