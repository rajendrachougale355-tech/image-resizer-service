import os
from flask import Flask, request, send_file, jsonify, render_template_string
from PIL import Image
import io
import zipfile

app = Flask(__name__)

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudScale | Bulk Image Optimization</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-accent: #334155;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-blue: #3b82f6;
            --accent-blue-hover: #2563eb;
            --accent-green: #10b981;
            --border-color: #475569;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .navbar {
            background-color: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav-logo {
            font-weight: 700;
            font-size: 18px;
            letter-spacing: -0.5px;
        }
        .nav-logo span { color: var(--accent-blue); }
        .badge {
            background: rgba(59, 130, 246, 0.15);
            color: var(--accent-blue);
            border: 1px solid rgba(59, 130, 246, 0.3);
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }

        .main-layout {
            max-width: 1280px;
            width: 100%;
            margin: 40px auto;
            padding: 0 24px;
            box-sizing: border-box;
            display: grid;
            grid-template-columns: 400px 1fr;
            gap: 32px;
            flex-grow: 1;
        }

        @media (max-width: 968px) {
            .main-layout { grid-template-columns: 1fr; }
        }

        .card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            display: flex;
            flex-direction: column;
        }
        .card-title { font-size: 16px; font-weight: 600; margin-top: 0; margin-bottom: 8px; }
        .card-subtitle { color: var(--text-muted); font-size: 13px; margin-bottom: 24px; }

        .form-group { margin-bottom: 20px; }
        label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 8px; color: var(--text-muted); }
        
        .file-upload-wrapper {
            position: relative;
            border: 2px dashed var(--border-color);
            border-radius: 8px;
            padding: 30px 20px;
            text-align: center;
            background: rgba(15, 23, 42, 0.4);
            transition: border-color 0.2s;
        }
        .file-upload-wrapper:hover { border-color: var(--accent-blue); }
        .file-upload-wrapper input[type="file"] {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            opacity: 0; cursor: pointer;
        }
        .upload-text { font-size: 13px; color: var(--text-muted); }
        .upload-text strong { color: var(--accent-blue); }

        .dimensions-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        input[type="number"] {
            width: 100%;
            background-color: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            color: var(--text-main);
            font-size: 14px;
            box-sizing: border-box;
        }

        button {
            background-color: var(--accent-blue);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            width: 100%;
            margin-top: 10px;
        }
        button:hover { background-color: var(--accent-blue-hover); }
        button:disabled { background-color: var(--bg-accent); color: var(--text-muted); cursor: not-allowed; }

        .viewport-card { min-height: 450px; justify-content: flex-start; position: relative; }
        .empty-state { text-align: center; color: var(--text-muted); font-size: 14px; margin: auto; }
        .empty-state-icon { font-size: 40px; margin-bottom: 12px; opacity: 0.5; }

        /* Multi-preview Grid */
        .preview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
            gap: 16px;
            width: 100%;
            margin-bottom: 24px;
            max-height: 320px;
            overflow-y: auto;
            padding-right: 4px;
        }
        .preview-item {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 6px;
            text-align: center;
        }
        .preview-item img {
            width: 100%;
            height: 90px;
            object-fit: cover;
            border-radius: 4px;
        }
        .preview-item-name {
            font-size: 11px;
            color: var(--text-muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-top: 4px;
        }

        .results-container { display: none; flex-direction: column; width: 100%; height: 100%; }

        .metrics-bar {
            display: flex;
            justify-content: space-between;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            padding: 12px 20px;
            border-radius: 8px;
            box-sizing: border-box;
            width: 100%;
        }
        .metric-item { font-size: 12px; color: var(--text-muted); }
        .metric-item strong { color: var(--text-main); display: block; font-size: 14px; margin-top: 2px; }

        .btn-download {
            background-color: var(--accent-green);
            color: white;
            text-decoration: none;
            padding: 14px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
            margin-top: 16px;
            display: block;
        }

        .footer-banner {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            background-color: var(--bg-secondary);
            margin-top: auto;
        }
    </style>
</head>
<body>

    <div class="navbar">
        <div class="nav-logo">⚡ CloudScale <span>// Bulk Engine</span></div>
        <div class="badge">AWS RUNTIME ACTIVE</div>
    </div>

    <div class="main-layout">
        <!-- Control Card -->
        <div class="card">
            <h3 class="card-title">Configuration</h3>
            <div class="card-subtitle">Upload up to 20 images at once</div>
            
            <form id="bulkResizerForm">
                <div class="form-group">
                    <label>INPUT TARGET SOURCES (MAX 20)</label>
                    <div class="file-upload-wrapper">
                        <span class="upload-text" id="fileStatusLabel">Select or drag files</span>
                        <input type="file" id="imageInput" accept="image/*" multiple required>
                    </div>
                </div>
                
                <div class="dimensions-grid">
                    <div class="form-group">
                        <label>TARGET WIDTH (PX)</label>
                        <input type="number" id="widthInput" value="500" min="10" max="3000">
                    </div>
                    <div class="form-group">
                        <label>TARGET HEIGHT (PX)</label>
                        <input type="number" id="heightInput" value="500" min="10" max="3000">
                    </div>
                </div>
                
                <button type="submit" id="processBtn">Execute Batch Job</button>
            </form>
        </div>

        <!-- Viewport Card -->
        <div class="card viewport-card">
            <div class="empty-state" id="emptyState">
                <div class="empty-state-icon">📂</div>
                <div>Awaiting batch payload image assets...</div>
            </div>

            <div class="results-container" id="resultsContainer">
                <h3 style="font-size: 15px; margin-top:0; margin-bottom:12px; font-weight:600;">Optimized Output Previews</h3>
                <div class="preview-grid" id="previewGrid"></div>
                
                <div class="metrics-bar">
                    <div class="metric-item">BATCH COUNT <strong id="metricCount">0 Files</strong></div>
                    <div class="metric-item">TARGET RESOLUTION <strong id="metricDim">500 x 500</strong></div>
                    <div class="metric-item">OUTPUT PACKAGE <strong>ZIP Archive</strong></div>
                </div>

                <a href="" id="downloadLink" class="btn-download">Download All Resized Images (.ZIP)</a>
            </div>
        </div>
    </div>

    <div class="footer-banner">
        Infrastructure Orchestration Node Deployed via Jenkins CI/CD Lifecycle Automation.
    </div>

    <script>
        const imageInput = document.getElementById('imageInput');
        const fileStatusLabel = document.getElementById('fileStatusLabel');

        // Limit files to 20 and show names
        imageInput.addEventListener('change', function(e) {
            const files = e.target.files;
            if (files.length > 20) {
                alert("Please select a maximum of 20 images at one time.");
                imageInput.value = '';
                fileStatusLabel.innerText = "Select or drag files";
                return;
            }
            fileStatusLabel.innerText = `${files.length} images staged for pipeline`;
        });

        document.getElementById('bulkResizerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const files = imageInput.files;
            const width = document.getElementById('widthInput').value;
            const height = document.getElementById('heightInput').value;
            
            const processBtn = document.getElementById('processBtn');
            const emptyState = document.getElementById('emptyState');
            const resultsContainer = document.getElementById('resultsContainer');
            const previewGrid = document.getElementById('previewGrid');
            const downloadLink = document.getElementById('downloadLink');

            if (files.length === 0) return;

            processBtn.disabled = true;
            processBtn.innerText = "Running Batch Cluster...";
            previewGrid.innerHTML = ''; // Clear previous images

            const formData = new FormData();
            formData.append('width', width);
            formData.append('height', height);
            
            // Loop and add all images to form data layout
            for (let i = 0; i < files.length; i++) {
                formData.append('images', files[i]);
            }

            try {
                const response = await fetch('/resize-bulk', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error("Batch job failed");

                const blob = await response.blob();
                const zipUrl = URL.createObjectURL(blob);

                // Populate instant preview icons using browser cache mapping
                for (let i = 0; i < files.length; i++) {
                    const itemUrl = URL.createObjectURL(files[i]);
                    const itemHtml = `
                        <div class="preview-item">
                            <img src="${itemUrl}">
                            <div class="preview-item-name">${files[i].name}</div>
                        </div>
                    `;
                    previewGrid.insertAdjacentHTML('beforeend', itemHtml);
                }

                emptyState.style.display = "none";
                resultsContainer.style.display = "flex";
                
                document.getElementById('metricCount').innerText = `${files.length} Files`;
                document.getElementById('metricDim').innerText = `${width}px × ${height}px`;
                
                downloadLink.href = zipUrl;
                downloadLink.download = "cloudscale_optimized_images.zip";

            } catch (err) {
                alert("Runtime error during batch operations.");
            } finally {
                processBtn.disabled = false;
                processBtn.innerText = "Execute Batch Job";
            }
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    return render_template_string(HTML_UI)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/resize-bulk', methods=['POST'])
def resize_bulk():
    if 'images' not in request.files:
        return jsonify({"error": "No image assets uploaded"}), 400
    
    files = request.files.getlist('images')
    width = int(request.form.get('width', 500))
    height = int(request.form.get('height', 500))

    # Output streaming zip memory allocation
    zip_buffer = io.BytesIO()

    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                if file.filename == '':
                    continue
                
                # Open, identify layout metadata, and resize individual image stream
                img = Image.open(file.stream)
                img_format = img.format if img.format else 'JPEG'
                img = img.resize((width, height), Image.Resampling.LANCZOS)

                # Save output to separate memory slot
                img_io = io.BytesIO()
                img.save(img_io, format=img_format)
                img_io.seek(0)

                # Append optimized file inside zip configuration matrix
                zip_file.writestr(f"resized_{file.filename}", img_io.getvalue())

        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='resized_images.zip')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
