"""
Entry point for running the Flask application in development mode.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

if __name__ == "__main__":
    app = create_app('development')
    app.run(
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", 5001)),
        debug=os.getenv("FLASK_DEBUG", "True").lower() == "true"
    )