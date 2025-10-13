from PIL import Image
import io, base64

def compress_image_to_base64(image_path, max_size_kb=200, max_width=1024):
    # Open the image
    img = Image.open(image_path)
    
    # Resize if width too large
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Compress quality progressively
    quality = 85
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality)
    
    while buffer.tell() / 1024 > max_size_kb and quality > 30:
        buffer = io.BytesIO()
        quality -= 10
        img.save(buffer, format="JPEG", quality=quality)
    
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

# Example
compressed_base64 = compress_image_to_base64("diagram.png", max_size_kb=300, max_width=1024)