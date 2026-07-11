import os
from flask import Flask, request, send_file, jsonify
from PIL import Image
import io

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "image-resizer"}), 200

@app.route('/resize', methods=['POST'])
def resize_image():
  
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided in the form field named 'image'"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
       
        width = int(request.form.get('width', 300))
        height = int(request.form.get('height', 300))

      
        img = Image.open(file.stream)
        img = img.resize((width, height), Image.Resampling.LANCZOS)

      
        img_io = io.BytesIO()
        
   
        img_format = img.format if img.format else 'JPEG'
        img.save(img_io, format=img_format)
        img_io.seek(0)

        print(f"Successfully resized image to {width}x{height}")
        
        
        return send_file(img_io, mimetype=f'image/{img_format.lower()}')

    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 500

if __name__ == '__main__':
   
    app.run(host='0.0.0.0', port=5000)
