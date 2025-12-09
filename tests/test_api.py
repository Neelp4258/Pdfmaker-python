"""Unit tests for API endpoints."""
import pytest
import json
from io import BytesIO


@pytest.mark.unit
class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns 200."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'html2pdf'


@pytest.mark.unit
class TestRenderSyncEndpoint:
    """Test synchronous PDF rendering endpoint."""

    def test_render_simple_html(self, client, sample_html):
        """Test rendering simple HTML to PDF."""
        response = client.post(
            '/render-sync',
            json={'html': sample_html, 'format': 'A4'},
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'
        assert len(response.data) > 0
        assert response.data[:4] == b'%PDF'  # PDF magic number

    def test_render_with_custom_dimensions(self, client, sample_html):
        """Test rendering with custom width and height."""
        response = client.post(
            '/render-sync',
            json={
                'html': sample_html,
                'width': '200mm',
                'height': '280mm'
            }
        )

        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'

    def test_render_landscape(self, client, sample_html):
        """Test rendering in landscape orientation."""
        response = client.post(
            '/render-sync',
            json={
                'html': sample_html,
                'format': 'A4',
                'landscape': True
            }
        )

        assert response.status_code == 200

    def test_render_with_margins(self, client, sample_html):
        """Test rendering with custom margins."""
        response = client.post(
            '/render-sync',
            json={
                'html': sample_html,
                'format': 'A4',
                'margin': '20mm,15mm,20mm,15mm'
            }
        )

        assert response.status_code == 200

    def test_render_with_custom_css(self, client, sample_html):
        """Test rendering with injected CSS."""
        custom_css = "body { background-color: lightblue; }"
        response = client.post(
            '/render-sync',
            json={
                'html': sample_html,
                'css': custom_css
            }
        )

        assert response.status_code == 200

    def test_render_missing_content(self, client):
        """Test error when neither html nor url provided."""
        response = client.post(
            '/render-sync',
            json={'format': 'A4'}
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_render_both_html_and_url(self, client, sample_html):
        """Test error when both html and url provided."""
        response = client.post(
            '/render-sync',
            json={
                'html': sample_html,
                'url': 'https://example.com'
            }
        )

        assert response.status_code == 400

    def test_render_invalid_scale(self, client, sample_html):
        """Test error with invalid scale value."""
        response = client.post(
            '/render-sync',
            json={
                'html': sample_html,
                'scale': 5.0  # Invalid, should be 0.1-2.0
            }
        )

        assert response.status_code == 400


@pytest.mark.unit
class TestRenderAsyncEndpoint:
    """Test asynchronous PDF rendering endpoint."""

    def test_queue_render_job(self, client, sample_html):
        """Test queueing async render job."""
        response = client.post(
            '/render',
            json={'html': sample_html, 'format': 'Letter'}
        )

        assert response.status_code == 202
        data = response.get_json()
        assert 'job_id' in data
        assert 'status' in data
        assert data['status'] == 'queued'
        assert 'status_url' in data

    def test_queue_with_all_options(self, client, sample_html):
        """Test queueing job with all options."""
        response = client.post(
            '/render',
            json={
                'html': sample_html,
                'format': 'A3',
                'landscape': True,
                'margin': '10mm',
                'scale': 0.8,
                'css': 'body { color: red; }'
            }
        )

        assert response.status_code == 202


@pytest.mark.unit
class TestStatusEndpoint:
    """Test job status endpoint."""

    def test_get_status_for_queued_job(self, client, sample_html):
        """Test getting status of queued job."""
        # Queue a job
        response = client.post('/render', json={'html': sample_html})
        job_data = response.get_json()
        job_id = job_data['job_id']

        # Get status
        response = client.get(f'/status/{job_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['job_id'] == job_id
        assert 'status' in data


@pytest.mark.unit
class TestBatchEndpoint:
    """Test batch rendering endpoint."""

    def test_batch_render(self, client, sample_html, complex_html):
        """Test batch rendering multiple jobs."""
        response = client.post(
            '/batch',
            json={
                'jobs': [
                    {'html': sample_html, 'format': 'A4'},
                    {'html': complex_html, 'format': 'Letter'},
                    {'html': '<h1>Simple</h1>', 'format': 'A5'}
                ]
            }
        )

        assert response.status_code == 202
        data = response.get_json()
        assert 'jobs' in data
        assert len(data['jobs']) == 3

        for job in data['jobs']:
            assert 'job_id' in job or 'error' in job

    def test_batch_empty(self, client):
        """Test batch with no jobs."""
        response = client.post('/batch', json={'jobs': []})
        assert response.status_code == 400

    def test_batch_too_many(self, client):
        """Test batch with too many jobs."""
        jobs = [{'html': '<p>test</p>'} for _ in range(101)]
        response = client.post('/batch', json={'jobs': jobs})
        assert response.status_code == 400


@pytest.mark.unit
class TestAspectRatios:
    """Test aspect ratio calculations."""

    def test_16_9_aspect(self, client, sample_html):
        """Test 16:9 aspect ratio."""
        response = client.post(
            '/render-sync',
            json={'html': sample_html, 'aspect': '16:9'}
        )
        assert response.status_code == 200

    def test_4_3_aspect(self, client, sample_html):
        """Test 4:3 aspect ratio."""
        response = client.post(
            '/render-sync',
            json={'html': sample_html, 'aspect': '4:3'}
        )
        assert response.status_code == 200

    def test_custom_aspect(self, client, sample_html):
        """Test custom aspect ratio."""
        response = client.post(
            '/render-sync',
            json={'html': sample_html, 'aspect': '21:9'}
        )
        assert response.status_code == 200
