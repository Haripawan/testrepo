from PIL import Image
import io, base64

def compress_image_to_base64_limit(image_path, max_base64_len=30000, max_width=1024):
    """
    Compresses and resizes image until base64 string length <= max_base64_len
    Returns base64 string.
    """
    img = Image.open(image_path)

    # Convert RGBA to RGB (JPEG doesn’t support alpha)
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # use alpha channel as mask
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    quality = 85
    resize_factor = 1.0

    while True:
        buffer = io.BytesIO()

        # Resize if needed
        if resize_factor < 1.0:
            new_size = (int(img.width * resize_factor), int(img.height * resize_factor))
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
        else:
            resized_img = img

        # Save to buffer with current quality
        resized_img.save(buffer, format="JPEG", quality=quality)
        b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        if len(b64) <= max_base64_len:
            return b64

        # Adjust compression and resize
        if quality > 30:
            quality -= 10
        else:
            resize_factor *= 0.8  # shrink further when quality already low

        # Safety break if it can't reach the limit
        if resize_factor < 0.2:
            print(f"Warning: could not reach {max_base64_len} characters; final len={len(b64)}")
            return b64
            
            
compressed_b64 = compress_image_to_base64_limit("diagram.png", max_base64_len=30000)
print("Final base64 length:", len(compressed_b64))