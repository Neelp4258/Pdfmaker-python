#!/bin/bash
# cURL examples for HTML2PDF service

API_URL="http://localhost:5000"
API_KEY="test-api-key-1"

echo "=== HTML2PDF Service - cURL Examples ==="
echo ""

# Example 1: Simple HTML to PDF (sync)
echo "1. Simple HTML to PDF (synchronous)"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Hello World</h1><p>This is a test PDF.</p></body></html>",
    "format": "A4"
  }' \
  --output simple.pdf

echo "✓ Saved simple.pdf"
echo ""

# Example 2: Custom page size
echo "2. Custom page dimensions"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Custom Size</h1></body></html>",
    "width": "200mm",
    "height": "280mm",
    "margin": "20mm"
  }' \
  --output custom_size.pdf

echo "✓ Saved custom_size.pdf"
echo ""

# Example 3: Landscape A4
echo "3. Landscape orientation"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Landscape Document</h1></body></html>",
    "format": "A4",
    "landscape": true
  }' \
  --output landscape.pdf

echo "✓ Saved landscape.pdf"
echo ""

# Example 4: 16:9 Presentation
echo "4. 16:9 presentation format"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><head><style>body{background:#667eea;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}h1{color:white;font-size:48px;}</style></head><body><h1>Slide Title</h1></body></html>",
    "aspect": "16:9",
    "landscape": true
  }' \
  --output presentation.pdf

echo "✓ Saved presentation.pdf"
echo ""

# Example 5: With custom CSS
echo "5. Custom CSS injection"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Styled Document</h1><p>Custom styling applied.</p></body></html>",
    "format": "A4",
    "css": "body { background-color: #f0f0f0; font-family: Georgia; padding: 40px; } h1 { color: #e74c3c; }"
  }' \
  --output styled.pdf

echo "✓ Saved styled.pdf"
echo ""

# Example 6: Receipt format
echo "6. Receipt format"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body style=\"font-family:monospace;font-size:12px;\"><h2>RECEIPT</h2><p>Date: 2024-01-01</p><hr><p>Item 1: $10.00</p><p>Item 2: $20.00</p><hr><p><b>Total: $30.00</b></p></body></html>",
    "format": "receipt",
    "margin": "5mm"
  }' \
  --output receipt.pdf

echo "✓ Saved receipt.pdf"
echo ""

# Example 7: Multi-page document
echo "7. Multi-page document"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><head><style>.page-break{page-break-after:always;}</style></head><body><h1>Page 1</h1><p>Content...</p><div class=\"page-break\"></div><h1>Page 2</h1><p>More content...</p></body></html>",
    "format": "Letter"
  }' \
  --output multipage.pdf

echo "✓ Saved multipage.pdf"
echo ""

# Example 8: URL to PDF
echo "8. URL to PDF"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "format": "A4",
    "wait_for": "2000"
  }' \
  --output url.pdf

echo "✓ Saved url.pdf"
echo ""

# Example 9: Async rendering
echo "9. Async rendering workflow"

# Queue job
JOB_RESPONSE=$(curl -s -X POST "$API_URL/render" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Async Document</h1></body></html>",
    "format": "A4"
  }')

JOB_ID=$(echo $JOB_RESPONSE | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)
echo "Job queued: $JOB_ID"

# Check status
sleep 2
STATUS=$(curl -s "$API_URL/status/$JOB_ID" -H "X-API-Key: $API_KEY")
echo "Status: $STATUS"

# Download (if completed)
curl -X GET "$API_URL/download/$JOB_ID" \
  -H "X-API-Key: $API_KEY" \
  --output async.pdf

echo "✓ Saved async.pdf"
echo ""

# Example 10: Batch rendering
echo "10. Batch rendering"
BATCH_RESPONSE=$(curl -s -X POST "$API_URL/batch" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jobs": [
      {"html": "<h1>Doc 1</h1>", "format": "A4"},
      {"html": "<h1>Doc 2</h1>", "format": "Letter"},
      {"html": "<h1>Doc 3</h1>", "format": "A5"}
    ]
  }')

echo "Batch response: $BATCH_RESPONSE"
echo ""

# Example 11: With scale
echo "11. Scaled document"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><body><h1>Scaled to 80%</h1></body></html>",
    "format": "A4",
    "scale": 0.8
  }' \
  --output scaled.pdf

echo "✓ Saved scaled.pdf"
echo ""

# Example 12: Page ranges
echo "12. Specific page ranges"
curl -X POST "$API_URL/render-sync" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<html><head><style>.page-break{page-break-after:always;}</style></head><body><h1>P1</h1><div class=\"page-break\"></div><h1>P2</h1><div class=\"page-break\"></div><h1>P3</h1><div class=\"page-break\"></div><h1>P4</h1></body></html>",
    "format": "A4",
    "page_ranges": "1-2"
  }' \
  --output pages_1_2.pdf

echo "✓ Saved pages_1_2.pdf (pages 1-2 only)"
echo ""

echo "✅ All examples completed!"
echo "Check the generated PDF files in the current directory."
