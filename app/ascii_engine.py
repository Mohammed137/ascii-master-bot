"""
Core ASCII conversion functions.
- text_to_ascii: uses pyfiglet for fonts
- image_to_ascii_text: converts image bytes -> ascii string
- render_text_to_png: render ascii text into a PNG image (monospace)
"""
import io
import os
from PIL import Image, ImageFont, ImageDraw
import pyfiglet

# TEXT -> ASCII using FIGlet
def text_to_ascii(text: str, font: str = "standard"):
    try:
        fig = pyfiglet.Figlet(font=font)
        out = fig.renderText(text)
        return out
    except Exception as e:
        return text

# IMAGE -> ASCII (text)
def image_to_ascii_text(image_bytes: bytes, width: int = 80, charset: list = None):
    if charset is None:
        charset = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']
    img = Image.open(io.BytesIO(image_bytes)).convert("L")  # grayscale
    w, h = img.size
    aspect = 0.55  # character aspect correction
    new_w = max(10, int(width))
    new_h = max(1, int((h / w) * new_w * aspect))
    img = img.resize((new_w, new_h))
    pixels = list(img.getdata())
    lines = []
    for y in range(new_h):
        row = []
        for x in range(new_w):
            p = pixels[y * new_w + x]
            idx = int((p / 255) * (len(charset) - 1))
            row.append(charset[idx])
        lines.append("".join(row))
    return "\n".join(lines)

# Render ascii text to png file and return path
def render_text_to_png(ascii_text: str, font_path: str = None, font_size: int = 12, out_dir: str = "cache"):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    lines = ascii_text.splitlines() or [""]
    # choose font
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    # measure size
    max_w = max([font.getsize(line)[0] for line in lines]) + 8
    line_h = font.getsize("A")[1] + 2
    img_h = line_h * len(lines) + 8
    img = Image.new("RGB", (max_w, img_h), (255,255,255))
    draw = ImageDraw.Draw(img)
    y = 4
    for line in lines:
        draw.text((4, y), line, font=font, fill=(0,0,0))
        y += line_h
    key = str(abs(hash(ascii_text)))[:16]
    out_path = os.path.join(out_dir, f"ascii_{key}.png")
    img.save(out_path)
    return out_path
