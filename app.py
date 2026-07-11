import os
from flask import Flask, request, send_file, jsonify, render_template_string
from PIL import Image
import io

app = Flask(__name__)

HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudScale | Image Optimization Microservice</title>
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

        /* Top Enterprise Navbar */
        .navbar {
            background-color: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 14px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav-logo {
            display: flex;
            align-items: center;
            gap: 10px;
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

        /* Main Layout Workspace */
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

        /* App Cards */
        .card {
            background-color: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            display: flex;
            flex-direction: column;
        }
        .card-title {
            font-size: 16px;
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card-subtitle {
            color: var(--text-muted);
            font-size: 13px;
            margin-bottom: 24px;
        }

        /* Forms styling */
        .form-group { margin-bottom: 20px; }
        label {
            display: block;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 8px;
            color: var(--text-muted);
        }
        
        /* Custom Upload Area */
        .file-upload-wrapper {
            position: relative;
            border: 2px dashed var(--border-color);
            border-radius: 8px;
            padding: 20px;
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

        /* Configuration Dimensions */
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
        input[type="number"]:focus { border-color: var(--accent-blue); outline: none; }

        /* Actions Button */
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

        /* Display Viewport (Right Side) */
        .viewport-card { min-height: 450px; justify-content: center; align-items: center; position: relative; }
        .preview-container {
            display: none;
            flex-direction: column;
            align-items: center;
            width: 100%;
            height: 100%;
        }
        .preview-image {
            max-width: 100%;
            max-height: 400px;
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border: 1px solid var(--border-color);
        }
        .empty-state { text-align: center; color: var(--text-muted); font-size: 14px; }
        .empty-state-icon { font-size: 40px; margin-bottom: 12px; opacity: 0.5; }

        /* Metrics Bar */
        .metrics-bar {
            display: flex;
            gap: 24px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            padding: 12px 20px;
            border-radius: 8px;
            margin-top: 20px;
            width: 100%;
            box-sizing: border-box;
        }
        .metric-item { font-size: 12px; color: var(--text-muted); }
        .metric-item strong { color: var(--text-main); display: block; font-size: 14px; margin-top: 2px; }

        .btn-download {
            background-color: var(--accent-green);
            color: white;
            text-decoration: none;
            padding: 12px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
            margin-top: 16px;
            display: block;
        }
        .btn-download:hover { opacity: 0.9; }

        /* System Logs / Footer banner */
        .footer-banner {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: var(--text-muted);
            border-top: 1px solid var(--border-color);
            background-color: var(--bg-secondary);
        }
    </style>
</head>
<body>

    <!-- Header Navigation Bar -->
    <div class="navbar">
        <div class="nav-logo">⚡ CloudScale <span>// Engine</span></div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <div class="badge">RAJ CHOUGALE DEVOPS PROJECT </div>
        </div>
    </div>

    <!-- Main Content Container -->
    <div class="main-layout">
        
        <!-- Left Side: Control Settings Panel -->
        <div class="card">
            <h3 class="card-title">Configuration</h3>
            <div class="card-subtitle">Set execution variables for processing</div>
            
            <form id="resizerForm">
                <div class="form-group">
                    <label>INPUT TARGET SOURCE</label>
                    <div class="file-upload-wrapper">
                        <span class="upload-text" id="fileStatusLabel">Drag file here or <strong>browse</strong></span>
                        <input type="file" id="imageInput" accept="image/*" required>
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
                
                <button type="submit" id="processBtn">Execute Pipeline Tasks</button>
            </form>
        </div>

        <!-- Right Side: Live Asset Output Viewport -->
        <div class="card viewport-card">
            <!-- Default Placeholder State -->
            <div class="empty-state" id="emptyState">
                <div class="empty-state-icon">🖼️</div>
                <div>Awaiting payload image assets for optimization processing...</div>
            </div>

            <!-- Active Output Result State -->
            <div class="preview-container" id="previewContainer">
                <img src="" id="outputImage" class="preview-image" alt="Optimized output asset">
                
                <div class="metrics-bar">
                    <div class="metric-item">OUTPUT DIMENSIONS<strong id="metricDim">0 x 0</strong></div>
                    <div class="metric-item">RUNTIME ENVIRONMENT<strong>AWS EC2 Container</strong></div>
                    <div class="metric-item">STATUS BADGE<strong style="color: var(--accent-green);">SUCCESS (200)</strong></div>
                </div>

                <a href="" id="downloadLink" class="btn-download" download="optimized_asset.jpg">Download Image Asset</a>
            </div>
        </div>

    </div>

    <!-- System Status Footer Banner -->
    <div class="footer-banner">
        Infrastructure Orchestration Node Deployed via Jenkins CI/CD Lifecycle Automation.
    </div>

    <script>
        // Real-time file name reflection
        document.getElementById('imageInput').addEventListener('change', function(e) {
            const fileName = e.target.files[0] ? e.target.files[0].name : "Browse files";
            document.getElementById('fileStatusLabel').innerText = fileName;
        });

        // Intercept network requests via JavaScript
        document.getElementById('resizerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const file = document.getElementById('imageInput').files[0];
            const width = document.getElementById('widthInput').value;
            const height = document.getElementById('heightInput').value;
            
            const processBtn = document.getElementById('processBtn');
            const emptyState = document.getElementById('emptyState');
            const previewContainer = document.getElementById('previewContainer');
            const outputImage = document.getElementById('outputImage');
            const downloadLink = document.getElementById('downloadLink');
            
            if(!file) return;

            // Loading state adjustments
            processBtn.disabled = true;
            processBtn.innerText = "Processing Cloud Tensors...";
            
            const formData = new FormData();
            formData.append('image', file);
            formData.append('width', width);
            formData.append('height', height);

            try {
                const response = await fetch('/resize', {
                    method: 'POST',
                    body: formData
                });

                if(!response.ok) throw new Error("API Failure Status");

                const blob = await response.blob();
                const blobUrl = URL.createObjectURL(blob);

                // Update viewport rendering
                emptyState.style.display = "none";
                previewContainer.style.display = "flex";
                outputImage.src = blobUrl;
                downloadLink.href = blobUrl;
                downloadLink.download = `optimized_${file.name}`;
                
                document.getElementById('metricDim').innerText = `${width}px × ${height}px`;

            } catch (err) {
                alert("Runtime error during remote service manipulation processing tasks.");
            } finally {
                processBtn.disabled = false;
                processBtn.innerText = "Execute Pipeline Tasks";
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

@app.route('/resize', methods=['POST'])
def resize_image():
    if 'image' not in request.files:
        return jsonify({"error": "No asset file parsed"}), 400
    
    file = request.files['image']
    try:
        width = int(request.form.get('width', 500))
        height = int(request.form.get('height', 500))

        img = Image.open(file.stream)
        img_format = img.format if img.format else 'JPEG'
        
        img = img.resize((width, height), Image.Resampling.LANCZOS)

        img_io = io.BytesIO()
        img.save(img_io, format=img_format)
        img_io.seek(0)
        
        return send_file(img_io, mimetype=f'image/{img_format.lower()}')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
