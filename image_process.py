from PIL import Image
import io, base64, os

def compress_image_to_base64(image_path, max_size_kb=300, max_width=1024):
    # Open image
    img = Image.open(image_path)

    # Convert RGBA (transparency) → RGB
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # 3 = alpha channel
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize if too wide
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    # Compress progressively
    quality = 85
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality)

    while buffer.tell() / 1024 > max_size_kb and quality > 30:
        buffer = io.BytesIO()
        quality -= 10
        img.save(buffer, format="JPEG", quality=quality)

    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# Example usage
compressed_base64 = compress_image_to_base64("diagram.png", max_size_kb=300, max_width=1024)