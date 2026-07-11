import os
from flask import Flask, request, send_file, jsonify, render_template_string
from PIL import Image
import io
import base64

app = Flask(__name__)

# Complete interactive single-page dashboard app
HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Resizer Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f1f5f9;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            max-width: 900px;
            width: 100%;
        }
        .header { text-align: center; margin-bottom: 30px; }
        h2 { color: #1e293b; margin: 0 0 8px 0; }
        p { color: #64748b; margin: 0; font-size: 15px; }
        
        .workspace {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-top: 20px;
        }
        @media (max-width: 768px) {
            .workspace { grid-template-columns: 1fr; }
        }
        
        .control-panel {
            border-right: 1px solid #e2e8f0;
            padding-right: 20px;
        }
        @media (max-width: 768px) {
            .control-panel { border-right: none; padding-right: 0; }
        }
        
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #475569; font-weight: 600; font-size: 14px; }
        input[type="file"] {
            width: 100%;
            padding: 12px;
            background: #f8fafc;
            border: 2px dashed #cbd5e1;
            border-radius: 8px;
            box-sizing: border-box;
            cursor: pointer;
        }
        .dimensions { display: flex; gap: 15px; }
        .dimensions .form-group { flex: 1; }
        input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            box-sizing: border-box;
        }
        
        button {
            width: 100%;
            background: #2563eb;
            color: white;
            border: none;
            padding: 14px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 10px;
        }
        button:hover { background: #1d4ed8; }
        
        .result-panel {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #f8fafc;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 20px;
            min-height: 300px;
            text-align: center;
        }
        .preview-box {
            max-width: 100%;
            max-height: 350px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            display: none;
            margin-bottom: 15px;
        }
        .placeholder-text { color: #94a3b8; font-style: italic; }
        .download-btn {
            background: #10b981;
            display: none;
            text-decoration: none;
            text-align: center;
            box-sizing: border-box;
        }
        .download-btn:hover { background: #059669; }
        .footer { text-align: center; margin-top: 35px; font-size: 12px; color: #94a3b8; border-top: 1px solid #f1f5f9; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📷 Microservice Image Control Panel</h2>
            <p>Live image manipulation architecture running on AWS infrastructure</p>
        </div>
        
        <div class="workspace">
            <!-- Left Side: Controls -->
            <div class="control-panel">
                <form id="uploadForm">
                    <div class="form-group">
                        <label for="imageInput">Upload Image File</label>
                        <input type="file" id="imageInput" accept="image/*" required>
                    </div>
                    
                    <div class="dimensions">
                        <div class="form-group">
                            <label for="widthInput">Target Width (px)</label>
                            <input type="number" id="widthInput" value="400" min="10" max="2000">
                        </div>
                        <div class="form-group">
                            <label for="heightInput">Target Height (px)</label>
                            <input type="number" id="heightInput" value="400" min="10" max="2000">
                        </div>
                    </div>
                    
                    <button type="submit" id="submitBtn">Process & Display Result</button>
                </form>
            </div>
            
            <!-- Right Side: Live Results View -->
            <div class="result-panel" id="resultPanel">
                <span class="placeholder-text" id="placeholder">Processed image display area</span>
                <img src="" id="resultPreview" class="preview-box" alt="Resized output preview">
                <a href="" id="downloadLink" class="download-btn" download="resized_image.jpg">Download Image Asset</a>
            </div>
        </div>
        
        <div class="footer">Continuous Deployment Management Engine • Active State</div>
    </div>

    <!-- JavaScript to intercept form submission and show results instantly on page -->
    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('imageInput').files[0];
            const width = document.getElementById('widthInput').value;
            const height = document.getElementById('heightInput').value;
            const submitBtn = document.getElementById('submitBtn');
            const placeholder = document.getElementById('placeholder');
            const preview = document.getElementById('resultPreview');
            const downloadBtn = document.getElementById('downloadLink');
            
            if (!fileInput) return;
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerText = "Processing in Cloud Container...";
            placeholder.innerText = "Processing image tensors...";
            preview.style.display = "none";
            downloadBtn.style.display = "none";
            
            const formData = new FormData();
            formData.append('image', fileInput);
            formData.append('width', width);
            formData.append('height', height);
            
            try {
                // Submit payload via background API call
                const response = await fetch('/resize', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) throw new Error("Processing failure");
                
                // Read binary response data stream
                const blob = await response.blob();
                const imageUrl = URL.createObjectURL(blob);
                
                // Inject the image dynamically into the DOM view
                placeholder.style.display = "none";
                preview.src = imageUrl;
                preview.style.display = "block";
                
                // Prepare live context download button
                downloadBtn.href = imageUrl;
                downloadBtn.style.display = "block";
                downloadBtn.style.width = "100%";
                downloadBtn.style.marginTop = "15px";
                
            } catch (error) {
                alert("Error handling image manipulation request.");
                placeholder.innerText = "Error processing data.";
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerText = "Process & Display Result";
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
        return jsonify({"error": "No image data"}), 400
    
    file = request.files['image']
    try:
        width = int(request.form.get('width', 400))
        height = int(request.form.get('height', 400))

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
