# utils.py
import os
import sys
import textwrap
from datetime import datetime
from PIL import ImageDraw

def log(msg):
    """Fungsi sederhana untuk mencetak log dengan timestamp."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def ensure_dir(path):
    """Pastikan direktori ada."""
    if not os.path.exists(path):
        os.makedirs(path)

def font_path():
    """Mengembalikan path font standar (Arial) jika ada, atau None."""
    paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", # Linux alt
        "C:\\Windows\\Fonts\\arialbd.ttf", # Windows
        "/Library/Fonts/Arial Bold.ttf", # Mac
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None # Akan menggunakan default font PIL

def get_font(path, size):
    """Mengambil object font PIL berdasarkan path dan ukuran."""
    from PIL import ImageFont
    if path and os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def wrap_text(text, font, max_width):
    """Membungkus teks agar tidak melebihi lebar maksimum."""
    return textwrap.fill(text, width=int(max_width / (font.size * 0.6)))

def draw_rounded_rect(draw, x1, y1, x2, y2, r, fill):
    """Menggambar kotak dengan sudut melengkung."""
    draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
    draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)
    draw.pieslice([x1, y1, x1 + 2*r, y1 + 2*r], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*r, y1, x2, y1 + 2*r], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*r, x1 + 2*r, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*r, y2 - 2*r, x2, y2], 0, 90, fill=fill)

def draw_text_stroke(draw, x, y, text, font, fill, stroke=2, stroke_fill=(0,0,0), anchor="la"):
    """Menggambar teks dengan garis tepi (outline)."""
    # Outline
    for dx in range(-stroke, stroke+1):
        for dy in range(-stroke, stroke+1):
            if dx*dx + dy*dy > stroke*stroke:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=stroke_fill, anchor=anchor)
    # Teks utama
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)

def crop_center_resize(img, target_width, target_height):
    """Memotong bagian tengah gambar dan meresize sesuai target."""
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # Gambar lebih lebar dari target, potong kiri kanan
        new_width = int(img.height * target_ratio)
        offset = (img.width - new_width) // 2
        img = img.crop((offset, 0, offset + new_width, img.height))
    elif img_ratio < target_ratio:
        # Gambar lebih tinggi dari target, potong atas bawah
        new_height = int(img.width / target_ratio)
        offset = (img.height - new_height) // 2
        img = img.crop((0, offset, img.width, offset + new_height))
    
    return img.resize((target_width, target_height), resample=1)
