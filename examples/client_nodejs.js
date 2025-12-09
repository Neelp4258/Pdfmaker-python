#!/usr/bin/env node
/**
 * Node.js client example for HTML2PDF service.
 * Demonstrates all major features and use cases.
 */

const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

class HTML2PDFClient {
  /**
   * Initialize client.
   * @param {string} baseURL - Service base URL
   * @param {string} apiKey - API key for authentication
   */
  constructor(baseURL, apiKey) {
    this.client = axios.create({
      baseURL: baseURL.replace(/\/$/, ''),
      headers: { 'X-API-Key': apiKey },
      timeout: 60000,
    });
  }

  /**
   * Render PDF synchronously.
   * @param {Object} options - Rendering options
   * @returns {Promise<Buffer>} PDF buffer
   */
  async renderSync(options) {
    const response = await this.client.post('/render-sync', options, {
      responseType: 'arraybuffer',
    });
    return Buffer.from(response.data);
  }

  /**
   * Queue PDF rendering job.
   * @param {Object} options - Rendering options
   * @returns {Promise<string>} Job ID
   */
  async renderAsync(options) {
    const response = await this.client.post('/render', options);
    return response.data.job_id;
  }

  /**
   * Get job status.
   * @param {string} jobId - Job identifier
   * @returns {Promise<Object>} Status object
   */
  async getStatus(jobId) {
    const response = await this.client.get(`/status/${jobId}`);
    return response.data;
  }

  /**
   * Download generated PDF.
   * @param {string} jobId - Job identifier
   * @returns {Promise<Buffer>} PDF buffer
   */
  async download(jobId) {
    const response = await this.client.get(`/download/${jobId}`, {
      responseType: 'arraybuffer',
    });
    return Buffer.from(response.data);
  }

  /**
   * Queue job and wait for completion.
   * @param {Object} options - Rendering options
   * @param {number} timeout - Maximum wait time in ms
   * @param {number} pollInterval - Status check interval in ms
   * @returns {Promise<Buffer>} PDF buffer
   */
  async renderAndWait(options, timeout = 300000, pollInterval = 2000) {
    const jobId = await this.renderAsync(options);
    console.log(`Job queued: ${jobId}`);

    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
      const status = await this.getStatus(jobId);
      console.log(`Status: ${status.status}`);

      if (status.status === 'completed') {
        return await this.download(jobId);
      } else if (status.status === 'failed') {
        throw new Error(`Rendering failed: ${status.error || 'Unknown error'}`);
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }

    throw new Error(`Job ${jobId} did not complete within ${timeout}ms`);
  }

  /**
   * Queue multiple jobs at once.
   * @param {Array<Object>} jobs - Array of job options
   * @returns {Promise<Array>} Array of job results
   */
  async batchRender(jobs) {
    const response = await this.client.post('/batch', { jobs });
    return response.data.jobs;
  }
}

async function main() {
  // Configuration
  const BASE_URL = 'http://localhost:5000';
  const API_KEY = 'test-api-key-1';

  // Initialize client
  const client = new HTML2PDFClient(BASE_URL, API_KEY);

  // Example 1: Simple HTML to PDF (sync)
  console.log('\n=== Example 1: Simple HTML to PDF ===');
  const html = `
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
  `;

  let pdf = await client.renderSync({ html, format: 'A4' });
  await fs.writeFile('output_simple.pdf', pdf);
  console.log(`✓ Saved output_simple.pdf (${pdf.length} bytes)`);

  // Example 2: Custom page size
  console.log('\n=== Example 2: Custom Page Size ===');
  pdf = await client.renderSync({
    html,
    width: '200mm',
    height: '280mm',
    margin: '20mm',
  });
  await fs.writeFile('output_custom_size.pdf', pdf);
  console.log(`✓ Saved output_custom_size.pdf (${pdf.length} bytes)`);

  // Example 3: 16:9 Presentation
  console.log('\n=== Example 3: 16:9 Presentation ===');
  const slideHtml = `
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
  `;

  pdf = await client.renderSync({
    html: slideHtml,
    aspect: '16:9',
    landscape: true,
  });
  await fs.writeFile('output_presentation.pdf', pdf);
  console.log(`✓ Saved output_presentation.pdf (${pdf.length} bytes)`);

  // Example 4: Multi-page document (async)
  console.log('\n=== Example 4: Multi-page Document (Async) ===');
  const multipageHtml = `
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
  `;

  pdf = await client.renderAndWait({
    html: multipageHtml,
    format: 'Letter',
    margin: '25mm,20mm,25mm,20mm',
  });
  await fs.writeFile('output_multipage.pdf', pdf);
  console.log(`✓ Saved output_multipage.pdf (${pdf.length} bytes)`);

  // Example 5: URL to PDF
  console.log('\n=== Example 5: URL to PDF ===');
  try {
    pdf = await client.renderSync({
      url: 'https://example.com',
      format: 'A4',
      wait_for: '1000',
    });
    await fs.writeFile('output_url.pdf', pdf);
    console.log(`✓ Saved output_url.pdf (${pdf.length} bytes)`);
  } catch (error) {
    console.log(`✗ URL rendering failed: ${error.message}`);
  }

  // Example 6: Batch rendering
  console.log('\n=== Example 6: Batch Rendering ===');
  const jobs = [
    { html: '<h1>Document 1</h1>', format: 'A4' },
    { html: '<h1>Document 2</h1>', format: 'Letter' },
    { html: '<h1>Document 3</h1>', format: 'A5' },
  ];

  const results = await client.batchRender(jobs);
  console.log(`✓ Queued ${results.length} jobs`);
  results.forEach((result, i) => {
    if (result.job_id) {
      console.log(`  Job ${i + 1}: ${result.job_id} - ${result.status}`);
    }
  });

  console.log('\n✅ All examples completed successfully!');
}

// Run examples
main().catch(error => {
  console.error(`\n❌ Error: ${error.message}`);
  process.exit(1);
});
