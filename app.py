import os
import sys
from PIL import Image

def resize_image(input_path, output_path, target_width=300):
    """
    Concept: Aspect-Ratio Preserving Resize
    We don't want to stretch or distort the image. We calculate the new height 
    proportionally based on our target width.
    """
    try:
        if not os.path.exists(input_path):
            print(f"Error: Input file '{input_path}' not found.")
            sys.exit(1)
            
        with Image.open(input_path) as img:
            # Calculate proportional height
            width_percent = (target_width / float(img.size[0]))
            target_height = int((float(img.size[1]) * float(width_percent)))
            
            # Perform the resize operation
            resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Save the processed image
            resized_img.save(output_path)
            print(f"Success! Resized image saved to: {output_path} ({target_width}x{target_height})")
            
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # In a production microservice, paths are often handled via environment variables
    # or command-line arguments passed by the orchestrator.
    INPUT_FILE = os.getenv("INPUT_IMAGE", "input.jpg")
    OUTPUT_FILE = os.getenv("OUTPUT_IMAGE", "output_thumbnail.jpg")
    
    print("Starting Image Processing Microservice...")
    resize_image(INPUT_FILE, OUTPUT_FILE)