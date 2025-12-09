"""Pytest configuration and fixtures."""
import pytest
import os
import sys

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import TestConfig


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app('test')
    app.config.from_object(TestConfig)

    # Disable auth and rate limiting for tests
    app.config['API_KEY_REQUIRED'] = False
    app.config['RATE_LIMIT_ENABLED'] = False

    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def sample_html():
    """Sample HTML for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Document</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { color: #333; }
            .page-break { page-break-after: always; }
        </style>
    </head>
    <body>
        <h1>Test Page 1</h1>
        <p>This is a test document with multiple pages.</p>
        <div class="page-break"></div>

        <h1>Test Page 2</h1>
        <p>This is the second page of the test document.</p>
    </body>
    </html>
    """


@pytest.fixture
def complex_html():
    """Complex HTML with images and tables."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Complex Document</title>
        <style>
            body { margin: 0; padding: 20px; font-family: Arial; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #4CAF50; color: white; }
            .chart { width: 100%; height: 300px; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); }
        </style>
    </head>
    <body>
        <h1>Sales Report 2024</h1>
        <div class="chart"></div>

        <h2>Monthly Data</h2>
        <table>
            <tr><th>Month</th><th>Sales</th><th>Growth</th></tr>
            <tr><td>January</td><td>$50,000</td><td>10%</td></tr>
            <tr><td>February</td><td>$55,000</td><td>10%</td></tr>
            <tr><td>March</td><td>$60,500</td><td>10%</td></tr>
        </table>
    </body>
    </html>
    """
