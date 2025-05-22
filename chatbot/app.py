import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from dotenv import load_dotenv  # Load environment variables from .env
from logger import CustomLogger
from chatbot import Chatbot

# Load .env variables at startup
load_dotenv()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    logger = CustomLogger().get_logger()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        """Render the API key input page and handle form submissions."""
        error_message = None

        # ✅ Auto-load API key from .env if not already in session
        if 'groq_api_key' not in session:
            env_key = os.getenv("GROQ_API_KEY")
            if env_key:
                session['groq_api_key'] = env_key
                logger.info("API Key loaded from environment.")
                return redirect(url_for('chat'))

        if request.method == 'POST':
            api_key = request.form['api_key']
            try:
                session['groq_api_key'] = api_key
                chatbot_instance = Chatbot(api_key)
                logger.info("API Key set via form.")
                return redirect(url_for('chat'))
            except Exception as e:
                logger.error(f"Error setting API Key: {e}")
                error_message = "Error setting API Key. Please try again."

        return render_template('index.html', error_message=error_message)

    @app.route('/chat')
    def chat():
        """Render the chat interface."""
        if 'groq_api_key' not in session:
            return redirect(url_for('index'))
        return render_template('chat.html')

    @app.route('/ask', methods=['POST'])
    def ask():
        """Handle user questions and return responses."""
        question = request.json.get('question')

        try:
            api_key = session.get('groq_api_key')
            if not api_key:
                return jsonify({"response": "API Key is not set."}), 500

            chatbot_instance = Chatbot(api_key)
            response = chatbot_instance.ask(question)
            logger.info(f"User asked: {question}")
            return jsonify({"response": response})

        except Exception as e:
            logger.error(f"Error processing question '{question}': {e}")
            return jsonify({"response": "An error occurred while processing your request."}), 500

    @app.route('/logout', methods=['POST'])
    def logout():
        """Clear the GROQ API key and reset chatbot instance."""
        session.pop('groq_api_key', None)
        session.pop('chatbot_instance', None)
        logger.info("API Key and Chatbot instance cleared.")
        return redirect(url_for('index'))

    return app
