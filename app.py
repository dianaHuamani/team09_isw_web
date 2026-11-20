"""Convenience entry point for running the pharmacy app with ``py app.py``."""

from dotenv import load_dotenv

load_dotenv()

from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=application.config["DEBUG"])
