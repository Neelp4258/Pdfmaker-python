// HTML2PDF - Main JavaScript Application

// Global variables
let htmlEditor, cssEditor;
let currentMode = 'html';
let isLandscape = false;
let jobHistory = [];
let API_KEY = 'test-api-key-1'; // Will be set by user

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeEditors();
    loadSettings();
    setupEventListeners();
    loadJobHistory();
    checkDarkMode();
});

// Initialize CodeMirror editors
function initializeEditors() {
    // HTML Editor
    htmlEditor = CodeMirror.fromTextArea(document.getElementById('htmlCode'), {
        mode: 'htmlmixed',
        theme: 'dracula',
        lineNumbers: true,
        autoCloseTags: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
    });

    htmlEditor.setSize('100%', '100%');
    htmlEditor.setValue(`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #667eea;
            border-bottom: 3px solid #764ba2;
            padding-bottom: 10px;
        }
        .info-box {
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>Welcome to HTML2PDF</h1>
    <p>This is a sample document to get you started.</p>

    <div class="info-box">
        <h3>Features</h3>
        <ul>
            <li>Pixel-perfect PDF rendering</li>
            <li>Custom page sizes and formats</li>
            <li>Multi-page support</li>
            <li>CSS styling and backgrounds</li>
        </ul>
    </div>

    <p>Edit this HTML to create your PDF!</p>
</body>
</html>`);

    // CSS Editor
    cssEditor = CodeMirror.fromTextArea(document.getElementById('cssCode'), {
        mode: 'css',
        theme: 'dracula',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 2,
        tabSize: 2,
    });

    cssEditor.setSize('100%', '200px');
    cssEditor.setValue(`/* Custom CSS */
body {
    background-color: #ffffff;
}
`);
}

// Setup event listeners
function setupEventListeners() {
    // Format selector
    document.getElementById('format').addEventListener('change', (e) => {
        const value = e.target.value;
        document.querySelector('.custom-size').style.display = value === 'custom' ? 'block' : 'none';
        document.querySelector('.aspect-ratio').style.display = value === 'aspect' ? 'block' : 'none';
    });

    // Scale slider
    document.getElementById('scale').addEventListener('input', (e) => {
        document.getElementById('scaleValue').textContent = e.target.value;
    });

    // File input
    document.getElementById('fileInput').addEventListener('change', handleFileUpload);

    // API Key prompt on first load
    if (!localStorage.getItem('html2pdf_api_key')) {
        promptForAPIKey();
    } else {
        API_KEY = localStorage.getItem('html2pdf_api_key');
    }
}

// Prompt for API key
function promptForAPIKey() {
    const key = prompt('Enter your API key:', 'test-api-key-1');
    if (key) {
        API_KEY = key;
        localStorage.setItem('html2pdf_api_key', key);
        showToast('API Key saved', 'success');
    }
}

// Switch input mode (HTML/URL)
function switchInputMode(mode) {
    currentMode = mode;

    // Update button states
    document.querySelectorAll('[data-mode]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
    });

    // Toggle visibility
    document.getElementById('htmlEditor').style.display = mode === 'html' ? 'flex' : 'none';
    document.getElementById('cssEditor').style.display = mode === 'html' ? 'block' : 'none';
    document.getElementById('urlInput').style.display = mode === 'url' ? 'flex' : 'none';
}

// Set orientation
function setOrientation(orientation) {
    isLandscape = orientation === 'landscape';

    document.querySelectorAll('[data-orientation]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.orientation === orientation);
    });
}

// Toggle section
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const isVisible = section.style.display !== 'none';
    section.style.display = isVisible ? 'none' : 'block';
}

// Generate PDF
async function generatePDF() {
    try {
        // Validate input
        const html = currentMode === 'html' ? htmlEditor.getValue() : null;
        const url = currentMode === 'url' ? document.getElementById('urlField').value : null;

        if (!html && !url) {
            showToast('Please provide HTML or URL', 'error');
            return;
        }

        // Gather options
        const options = {
            format: document.getElementById('format').value,
            landscape: isLandscape,
            margin: document.getElementById('margin').value || '10mm',
            scale: parseFloat(document.getElementById('scale').value),
            page_ranges: document.getElementById('pageRanges').value || null,
            wait_for: document.getElementById('waitFor').value || null,
        };

        // Add custom dimensions if selected
        if (options.format === 'custom') {
            options.width = document.getElementById('customWidth').value;
            options.height = document.getElementById('customHeight').value;
            delete options.format;
        } else if (options.format === 'aspect') {
            options.aspect = document.getElementById('aspect').value;
            delete options.format;
        }

        // Add CSS if provided
        const css = cssEditor.getValue().trim();
        if (css && currentMode === 'html') {
            options.css = css;
        }

        // Add HTML or URL
        if (html) {
            options.html = html;
        } else {
            options.url = url;
        }

        // Check sync mode
        const isSyncMode = document.getElementById('syncMode').checked;

        if (isSyncMode) {
            await generatePDFSync(options);
        } else {
            await generatePDFAsync(options);
        }

    } catch (error) {
        console.error('Error generating PDF:', error);
        hideStatus();
        showToast('Failed to generate PDF: ' + error.message, 'error');
    }
}

// Generate PDF synchronously
async function generatePDFSync(options) {
    showStatus('Generating PDF...', 'Please wait while we create your PDF');

    try {
        const response = await fetch('/render-sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY,
            },
            body: JSON.stringify(options),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to generate PDF');
        }

        const blob = await response.blob();
        downloadBlob(blob, 'document.pdf');

        hideStatus();
        showToast('PDF generated successfully!', 'success');

        // Add to history
        addToHistory({
            id: Date.now().toString(),
            name: 'document.pdf',
            status: 'completed',
            timestamp: new Date().toISOString(),
            blob: blob,
        });

    } catch (error) {
        hideStatus();
        throw error;
    }
}

// Generate PDF asynchronously
async function generatePDFAsync(options) {
    showStatus('Queueing job...', 'Your PDF is being queued for processing');

    try {
        // Queue job
        const response = await fetch('/render', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY,
            },
            body: JSON.stringify(options),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to queue job');
        }

        const data = await response.json();
        const jobId = data.job_id;

        showToast('Job queued: ' + jobId, 'info');

        // Add to history
        const job = {
            id: jobId,
            name: `job-${jobId.substring(0, 8)}.pdf`,
            status: 'queued',
            timestamp: new Date().toISOString(),
        };
        addToHistory(job);

        // Poll for status
        await pollJobStatus(jobId, job);

    } catch (error) {
        hideStatus();
        throw error;
    }
}

// Poll job status
async function pollJobStatus(jobId, job) {
    const maxAttempts = 60; // 2 minutes max
    let attempts = 0;

    const poll = async () => {
        try {
            const response = await fetch(`/status/${jobId}`, {
                headers: {
                    'X-API-Key': API_KEY,
                },
            });

            if (!response.ok) {
                throw new Error('Failed to get job status');
            }

            const data = await response.json();
            job.status = data.status;
            updateJobInHistory(job);

            if (data.status === 'completed') {
                hideStatus();
                showToast('PDF ready for download!', 'success');

                // Download PDF
                const pdfResponse = await fetch(`/download/${jobId}`, {
                    headers: {
                        'X-API-Key': API_KEY,
                    },
                });

                if (pdfResponse.ok) {
                    const blob = await pdfResponse.blob();
                    job.blob = blob;
                    updateJobInHistory(job);
                    downloadBlob(blob, job.name);
                }

                return;
            } else if (data.status === 'failed') {
                hideStatus();
                showToast('Job failed: ' + (data.error || 'Unknown error'), 'error');
                return;
            }

            attempts++;
            if (attempts < maxAttempts) {
                updateStatus(`Processing... (${data.status})`, `Attempt ${attempts}/${maxAttempts}`);
                const progress = (attempts / maxAttempts) * 100;
                updateProgress(progress);
                setTimeout(poll, 2000);
            } else {
                hideStatus();
                showToast('Job timeout - check status manually', 'warning');
            }

        } catch (error) {
            console.error('Error polling status:', error);
            hideStatus();
            showToast('Failed to get job status', 'error');
        }
    };

    poll();
}

// Show status overlay
function showStatus(title, message) {
    document.getElementById('statusTitle').textContent = title;
    document.getElementById('statusMessage').textContent = message;
    document.getElementById('statusPanel').style.display = 'flex';
    updateProgress(0);
}

// Update status
function updateStatus(title, message) {
    document.getElementById('statusTitle').textContent = title;
    document.getElementById('statusMessage').textContent = message;
}

// Update progress bar
function updateProgress(percent) {
    document.getElementById('progressBar').style.width = percent + '%';
}

// Hide status overlay
function hideStatus() {
    document.getElementById('statusPanel').style.display = 'none';
}

// Download blob as file
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Job history management
function loadJobHistory() {
    const stored = localStorage.getItem('html2pdf_jobs');
    if (stored) {
        jobHistory = JSON.parse(stored);
        renderJobHistory();
    }
}

function saveJobHistory() {
    // Don't save blobs to localStorage
    const toSave = jobHistory.map(job => ({
        id: job.id,
        name: job.name,
        status: job.status,
        timestamp: job.timestamp,
    }));
    localStorage.setItem('html2pdf_jobs', JSON.stringify(toSave));
}

function addToHistory(job) {
    jobHistory.unshift(job);
    if (jobHistory.length > 10) {
        jobHistory = jobHistory.slice(0, 10);
    }
    saveJobHistory();
    renderJobHistory();
}

function updateJobInHistory(job) {
    const index = jobHistory.findIndex(j => j.id === job.id);
    if (index !== -1) {
        jobHistory[index] = { ...jobHistory[index], ...job };
        saveJobHistory();
        renderJobHistory();
    }
}

function renderJobHistory() {
    const jobList = document.getElementById('jobList');
    const jobHistoryPanel = document.getElementById('jobHistory');

    if (jobHistory.length === 0) {
        jobHistoryPanel.style.display = 'none';
        return;
    }

    jobHistoryPanel.style.display = 'block';
    jobList.innerHTML = '';

    jobHistory.forEach(job => {
        const item = document.createElement('div');
        item.className = 'job-item';
        item.innerHTML = `
            <div class="job-info">
                <div class="job-name">${job.name}</div>
                <div class="job-status">
                    <span class="status-badge status-${job.status}">${job.status}</span>
                </div>
            </div>
            <div class="job-actions">
                ${job.blob ? `<button class="btn btn-icon btn-xs" onclick="downloadJob('${job.id}')" title="Download">
                    <i class="fas fa-download"></i>
                </button>` : ''}
                <button class="btn btn-icon btn-xs" onclick="removeJob('${job.id}')" title="Remove">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        jobList.appendChild(item);
    });
}

function downloadJob(jobId) {
    const job = jobHistory.find(j => j.id === jobId);
    if (job && job.blob) {
        downloadBlob(job.blob, job.name);
    }
}

function removeJob(jobId) {
    jobHistory = jobHistory.filter(j => j.id !== jobId);
    saveJobHistory();
    renderJobHistory();
}

function clearHistory() {
    if (confirm('Clear all job history?')) {
        jobHistory = [];
        localStorage.removeItem('html2pdf_jobs');
        renderJobHistory();
        showToast('History cleared', 'info');
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle',
    };

    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <div class="toast-content">
            <div class="toast-message">${message}</div>
        </div>
        <button class="btn btn-icon btn-xs" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    document.getElementById('toastContainer').appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// File upload
function uploadFile() {
    document.getElementById('fileInput').click();
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        htmlEditor.setValue(e.target.result);
        showToast('File loaded successfully', 'success');
    };
    reader.readAsText(file);
}

// Templates
function loadTemplate() {
    document.getElementById('templateModal').classList.add('active');
}

function closeModal() {
    document.getElementById('templateModal').classList.remove('active');
}

function selectTemplate(templateName) {
    const templates = {
        invoice: `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial; padding: 40px; }
        .header { text-align: center; margin-bottom: 40px; }
        .invoice-details { margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #667eea; color: white; }
        .total { font-size: 1.5em; text-align: right; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>INVOICE</h1>
        <p>Invoice #: INV-001 | Date: 2024-01-01</p>
    </div>
    <div class="invoice-details">
        <p><strong>From:</strong> Your Company</p>
        <p><strong>To:</strong> Client Name</p>
    </div>
    <table>
        <tr><th>Item</th><th>Quantity</th><th>Price</th><th>Total</th></tr>
        <tr><td>Service 1</td><td>1</td><td>$100</td><td>$100</td></tr>
        <tr><td>Service 2</td><td>2</td><td>$50</td><td>$100</td></tr>
    </table>
    <div class="total"><strong>Total: $200.00</strong></div>
</body>
</html>`,
        report: `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Georgia; padding: 40px; max-width: 800px; margin: 0 auto; }
        h1 { color: #2c3e50; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
        .page-break { page-break-after: always; }
        .summary { background: #f8f9fa; padding: 20px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>Annual Report 2024</h1>
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>This report provides an overview of company performance...</p>
    </div>
    <div class="page-break"></div>
    <h2>Financial Results</h2>
    <p>Our financial results show strong growth...</p>
</body>
</html>`,
        resume: `<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Helvetica'; padding: 40px; }
        .name { font-size: 2.5em; color: #667eea; margin-bottom: 5px; }
        .contact { color: #666; margin-bottom: 30px; }
        .section { margin: 30px 0; }
        .section h2 { color: #667eea; border-bottom: 2px solid #764ba2; padding-bottom: 5px; }
        .job { margin: 15px 0; }
        .job-title { font-weight: bold; }
    </style>
</head>
<body>
    <div class="name">John Doe</div>
    <div class="contact">john@example.com | (555) 123-4567</div>
    <div class="section">
        <h2>Experience</h2>
        <div class="job">
            <div class="job-title">Senior Developer - Tech Corp</div>
            <div>2020 - Present</div>
        </div>
    </div>
</body>
</html>`,
        presentation: `<!DOCTYPE html>
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
        .slide {
            text-align: center;
            color: white;
        }
        h1 { font-size: 4em; margin-bottom: 20px; }
        p { font-size: 1.5em; }
    </style>
</head>
<body>
    <div class="slide">
        <h1>Presentation Title</h1>
        <p>Your subtitle here</p>
    </div>
</body>
</html>`,
    };

    htmlEditor.setValue(templates[templateName]);
    closeModal();
    showToast('Template loaded', 'success');
}

// Reset form
function resetForm() {
    if (confirm('Reset all settings to default?')) {
        document.getElementById('format').value = 'A4';
        document.getElementById('scale').value = '1.0';
        document.getElementById('scaleValue').textContent = '1.0';
        document.getElementById('margin').value = '10mm';
        document.getElementById('pageRanges').value = '';
        document.getElementById('waitFor').value = '';
        document.getElementById('syncMode').checked = true;
        setOrientation('portrait');
        showToast('Settings reset', 'info');
    }
}

// Dark mode
function checkDarkMode() {
    const isDark = localStorage.getItem('html2pdf_dark_mode') === 'true';
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateDarkModeIcon(true);
    }
}

document.getElementById('darkModeToggle').addEventListener('click', () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

    if (isDark) {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('html2pdf_dark_mode', 'false');
        updateDarkModeIcon(false);
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('html2pdf_dark_mode', 'true');
        updateDarkModeIcon(true);
    }
});

function updateDarkModeIcon(isDark) {
    const icon = document.querySelector('#darkModeToggle i');
    icon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
}

// Save settings
function loadSettings() {
    const settings = localStorage.getItem('html2pdf_settings');
    if (settings) {
        try {
            const parsed = JSON.parse(settings);
            // Apply saved settings
        } catch (e) {
            console.error('Failed to load settings:', e);
        }
    }
}

// Close modal on outside click
window.addEventListener('click', (e) => {
    const modal = document.getElementById('templateModal');
    if (e.target === modal) {
        closeModal();
    }
});
