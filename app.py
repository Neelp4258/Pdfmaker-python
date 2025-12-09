"""
HTML2PDF Service - Main entry point.
Run with: python app.py or gunicorn app:app
"""
import os
import sys
from app import create_app

# Create Flask app
app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
