#!/usr/bin/env python3
"""
Python client example for HTML2PDF service.
Demonstrates all major features and use cases.
"""
import requests
import time
import sys
from pathlib import Path


class HTML2PDFClient:
    """Client for HTML2PDF service."""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize client.

        Args:
            base_url: Service base URL (e.g., http://localhost:5000)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {'X-API-Key': api_key}

    def render_sync(self, html: str = None, url: str = None, **options) -> bytes:
        """
        Render PDF synchronously (immediate response).

        Args:
            html: HTML content string
            url: URL to render
            **options: Additional rendering options

        Returns:
            PDF bytes

        Raises:
            requests.HTTPError: If request fails
        """
        data = options.copy()
        if html:
            data['html'] = html
        elif url:
            data['url'] = url
        else:
            raise ValueError("Either html or url must be provided")

        response = requests.post(
            f"{self.base_url}/render-sync",
            json=data,
            headers=self.headers,
            timeout=60
        )
        response.raise_for_status()
        return response.content

    def render_async(self, html: str = None, url: str = None, **options) -> str:
        """
        Queue PDF rendering job (async).

        Args:
            html: HTML content string
            url: URL to render
            **options: Additional rendering options

        Returns:
            Job ID

        Raises:
            requests.HTTPError: If request fails
        """
        data = options.copy()
        if html:
            data['html'] = html
        elif url:
            data['url'] = url
        else:
            raise ValueError("Either html or url must be provided")

        response = requests.post(
            f"{self.base_url}/render",
            json=data,
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()['job_id']

    def get_status(self, job_id: str) -> dict:
        """
        Get job status.

        Args:
            job_id: Job identifier

        Returns:
            Status dict

        Raises:
            requests.HTTPError: If request fails
        """
        response = requests.get(
            f"{self.base_url}/status/{job_id}",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def download(self, job_id: str) -> bytes:
        """
        Download generated PDF.

        Args:
            job_id: Job identifier

        Returns:
            PDF bytes

        Raises:
            requests.HTTPError: If request fails
        """
        response = requests.get(
            f"{self.base_url}/download/{job_id}",
            headers=self.headers,
            timeout=60
        )
        response.raise_for_status()
        return response.content

    def render_and_wait(
        self,
        html: str = None,
        url: str = None,
        timeout: int = 300,
        poll_interval: int = 2,
        **options
    ) -> bytes:
        """
        Queue job and wait for completion.

        Args:
            html: HTML content string
            url: URL to render
            timeout: Maximum wait time in seconds
            poll_interval: Status check interval in seconds
            **options: Additional rendering options

        Returns:
            PDF bytes

        Raises:
            TimeoutError: If job doesn't complete in time
            RuntimeError: If rendering fails
        """
        job_id = self.render_async(html, url, **options)
        print(f"Job queued: {job_id}")

        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status(job_id)
            print(f"Status: {status['status']}")

            if status['status'] == 'completed':
                return self.download(job_id)
            elif status['status'] == 'failed':
                error = status.get('error', 'Unknown error')
                raise RuntimeError(f"Rendering failed: {error}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")

    def batch_render(self, jobs: list) -> list:
        """
        Queue multiple jobs at once.

        Args:
            jobs: List of job dicts with rendering options

        Returns:
            List of job results

        Raises:
            requests.HTTPError: If request fails
        """
        response = requests.post(
            f"{self.base_url}/batch",
            json={'jobs': jobs},
            headers=self.headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()['jobs']


def main():
    """Example usage."""
    # Configuration
    BASE_URL = 'http://localhost:5000'
    API_KEY = 'test-api-key-1'

    # Initialize client
    client = HTML2PDFClient(BASE_URL, API_KEY)

    # Example 1: Simple HTML to PDF (sync)
    print("\n=== Example 1: Simple HTML to PDF ===")
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial; padding: 40px; }
            h1 { color: #2c3e50; }
        </style>
    </head>
    <body>
        <h1>Hello from HTML2PDF!</h1>
        <p>This is a simple example.</p>
    </body>
    </html>
    """

    pdf = client.render_sync(html=html, format='A4')
    Path('output_simple.pdf').write_bytes(pdf)
    print(f"✓ Saved output_simple.pdf ({len(pdf)} bytes)")

    # Example 2: Custom page size
    print("\n=== Example 2: Custom Page Size ===")
    pdf = client.render_sync(
        html=html,
        width='200mm',
        height='280mm',
        margin='20mm'
    )
    Path('output_custom_size.pdf').write_bytes(pdf)
    print(f"✓ Saved output_custom_size.pdf ({len(pdf)} bytes)")

    # Example 3: 16:9 Presentation
    print("\n=== Example 3: 16:9 Presentation ===")
    slide_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            h1 {
                color: white;
                font-size: 72px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h1>Presentation Title</h1>
    </body>
    </html>
    """

    pdf = client.render_sync(
        html=slide_html,
        aspect='16:9',
        landscape=True
    )
    Path('output_presentation.pdf').write_bytes(pdf)
    print(f"✓ Saved output_presentation.pdf ({len(pdf)} bytes)")

    # Example 4: Multi-page document (async)
    print("\n=== Example 4: Multi-page Document (Async) ===")
    multipage_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Georgia; padding: 40px; }
            h1 { color: #34495e; }
            .page-break { page-break-after: always; }
        </style>
    </head>
    <body>
        <h1>Chapter 1</h1>
        <p>Content for chapter 1...</p>
        <div class="page-break"></div>

        <h1>Chapter 2</h1>
        <p>Content for chapter 2...</p>
        <div class="page-break"></div>

        <h1>Chapter 3</h1>
        <p>Content for chapter 3...</p>
    </body>
    </html>
    """

    pdf = client.render_and_wait(
        html=multipage_html,
        format='Letter',
        margin='25mm,20mm,25mm,20mm'
    )
    Path('output_multipage.pdf').write_bytes(pdf)
    print(f"✓ Saved output_multipage.pdf ({len(pdf)} bytes)")

    # Example 5: URL to PDF
    print("\n=== Example 5: URL to PDF ===")
    try:
        pdf = client.render_sync(
            url='https://example.com',
            format='A4',
            wait_for='1000'  # Wait 1 second for page load
        )
        Path('output_url.pdf').write_bytes(pdf)
        print(f"✓ Saved output_url.pdf ({len(pdf)} bytes)")
    except Exception as e:
        print(f"✗ URL rendering failed: {e}")

    # Example 6: Batch rendering
    print("\n=== Example 6: Batch Rendering ===")
    jobs = [
        {'html': '<h1>Document 1</h1>', 'format': 'A4'},
        {'html': '<h1>Document 2</h1>', 'format': 'Letter'},
        {'html': '<h1>Document 3</h1>', 'format': 'A5'},
    ]

    results = client.batch_render(jobs)
    print(f"✓ Queued {len(results)} jobs")
    for i, result in enumerate(results):
        if 'job_id' in result:
            print(f"  Job {i+1}: {result['job_id']} - {result['status']}")

    print("\n✅ All examples completed successfully!")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
