import os
from datetime import datetime
from PIL import Image

def compress_and_save_image(image_file, upload_folder, prefix="img"):
    """
    A common function to compress and save any uploaded image.
    Returns the unique filename if successful, otherwise None.
    """
    # Check if a valid image file is provided
    if not image_file or image_file.filename == '':
        return None
        
    # Ensure the target upload directory exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate a unique filename using the prefix and current timestamp
    unique_filename = f"{prefix}_{int(datetime.now().timestamp())}.jpg"
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Open the image using Pillow
    img = Image.open(image_file)
    
    # Convert images with transparency (RGBA) or palette (P) modes to standard RGB
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    # Resize the image so its maximum width/height is 800px while maintaining aspect ratio
    img.thumbnail((800, 800)) 
    
    # Save the compressed image as a JPEG with 70% quality optimization
    img.save(file_path, format="JPEG", optimize=True, quality=70)
    
    return unique_filename