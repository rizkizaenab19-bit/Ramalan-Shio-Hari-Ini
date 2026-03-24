# thumb.py
import os, re, random
from datetime import datetime
from config import (CHANNEL_ID, NAMA_CHANNEL, SKEMA_AKTIF)
from utils import (log, font_path, get_font, wrap_text,
                   draw_rounded_rect, draw_text_stroke, crop_center_resize)

W, H = 1280, 720

def _list_gambar():
    import glob
    return sorted(
        glob.glob("gambar_bank/*.jpg") + glob.glob("gambar_bank/*.jpeg") +
        glob.glob("gambar_bank/*.png") + glob.glob("gambar_static/*.jpg") +
        glob.glob("gambar_static/*.jpeg") + glob.glob("gambar_static/*.png")
    )

def buat_thumbnail(info, judul, output_path="thumbnail.jpg"):
    log("[+] Membuat thumbnail...")
    TEMPLATE_MAP = {1: _tmpl_ch1, 2: _tmpl_ch2, 3: _tmpl_ch3, 4: _tmpl_ch4, 5: _tmpl_ch5}
    fn = TEMPLATE_MAP.get(CHANNEL_ID, _tmpl_ch1)
    return fn(info, judul, output_path)

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════
def _sk(info):
    return SKEMA_AKTIF.get(info["peruntungan_hari"], SKEMA_AKTIF.get("Baik"))

def _fp():
    return font_path()

def _foto_bg(brightness=0.85, blur=2):
    from PIL import Image, ImageFilter, ImageEnhance
    gb = _list_gambar()
    if not gb:
        return _solid_bg((10, 5, 30))
    try:
        img = Image.open(random.choice(gb)).convert("RGB")
        img = crop_center_resize(img, W, H)
        if blur > 0:
            img = img.filter(ImageFilter.GaussianBlur(blur))
        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Color(img).enhance(1.3)
        return img
    except Exception:
        return _solid_bg((10, 5, 30))

def _solid_bg(color=(10, 5, 30)):
    from PIL import Image
    return Image.new("RGB", (W, H), color)

def _overlay_warna(img, color, alpha):
    from PIL import Image
    ov = Image.new("RGBA", (W, H), (color[0], color[1], color[2], alpha))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

def _overlay_gradient(img, color, dari="kiri", alpha_maks=200, alpha_min=20):
    from PIL import Image, ImageDraw
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    r, g, b = color
    for i in range(W):
        if dari == "kiri":
            a = int(alpha_maks - (alpha_maks - alpha_min) * (i / W))
        elif dari == "kanan":
            a = int(alpha_min + (alpha_maks - alpha_min) * (i / W))
        else:
            a = int(alpha_maks - (alpha_maks - alpha_min) * (i / W))
        od.line([(i, 0), (i, H)], fill=(r, g, b, a))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

def _overlay_gradient_vertikal(img, color, dari="bawah", alpha_maks=220, alpha_min=0):
    from PIL import Image, ImageDraw
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    r, g, b = color
    for i in range(H):
        if dari == "bawah":
            a = int(alpha_min + (alpha_maks - alpha_min) * (i / H))
        else:
            a = int(alpha_maks - (alpha_maks - alpha_min) * (i / H))
        od.line([(0, i), (W, i)], fill=(r, g, b, a))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

# ═══════════════════════════════════════════════════════════
# TEMPLATE 1 – Ramalan Shio Hari Ini
# Gaya: Merah Emas | Badge kiri atas | Tanda besar kiri bawah
# ═══════════════════════════════════════════════════════════
def _tmpl_ch1(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)
    img = _foto_bg(brightness=0.90, blur=2)
    img = _overlay_gradient_vertikal(img, (40, 0, 10), dari="bawah", alpha_maks=215, alpha_min=10)
    img = _overlay_gradient(img, (20, 0, 5), dari="kiri", alpha_maks=130, alpha_min=0)
    draw = ImageDraw.Draw(img)

    tanda    = info.get("tanda_terbaik", "")
    prt      = info.get("peruntungan_hari", "Baik")
    warna    = info.get("warna_hari", "")
    angka    = info.get("angka_hari", "")
    tgl      = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # Badge peruntungan kiri atas
    bg_badge = sk.get("badge", (200, 0, 0))
    tc_badge = sk.get("hl_teks", (255, 255, 255))
    bw = len(icon_txt) * 20 + 50
    draw_rounded_rect(draw, 30, 24, 30 + bw, 78, 24, fill=bg_badge)
    draw.text((48, 32), icon_txt, font=get_font(fp, 30), fill=tc_badge)

    # Nama channel kanan atas
    draw_text_stroke(draw, W - 30, 28, NAMA_CHANNEL, get_font(fp, 26),
                     sk.get("teks", (255, 220, 0)), stroke=3,
                     stroke_fill=(60, 0, 0), anchor="rt")

    # Label "Tanda Terbaik Hari Ini"
    draw_text_stroke(draw, 34, H - 240, "Tanda Terbaik Hari Ini", get_font(fp, 28),
                     sk.get("sub", (255, 200, 150)), stroke=2, stroke_fill=(0, 0, 0))

    # Nama tanda besar
    draw_text_stroke(draw, 30, H - 208, tanda, get_font(fp, 100),
                     sk.get("teks", (255, 220, 0)), stroke=6, stroke_fill=(80, 0, 0))

    # Warna & angka hoki
    draw_text_stroke(draw, 34, H - 90, f"Warna: {warna}  |  Angka: {angka}",
                     get_font(fp, 30), sk.get("sub", (255, 200, 150)),
                     stroke=2, stroke_fill=(0, 0, 0))

    # Tanggal kanan bawah
    draw_text_stroke(draw, W - 30, H - 36, tgl, get_font(fp, 26),
                     sk.get("sub", (255, 200, 150)), stroke=2,
                     stroke_fill=(0, 0, 0), anchor="rb")

    # Strip bawah
    draw.rectangle([0, H - 10, W, H], fill=sk.get("aksen", (255, 80, 0)))
    img.save(output_path, "JPEG", quality=96)
    log(f" -> T1 saved: {output_path}")
    return output_path

# ═══════════════════════════════════════════════════════════
# TEMPLATE 2 – Zodiak Harian Update
# Gaya: Biru Perak | Teks kanan bawah | Stripe biru
# ═══════════════════════════════════════════════════════════
def _tmpl_ch2(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)
    img = _foto_bg(brightness=1.0, blur=0)
    img = _overlay_gradient(img, (0, 20, 80), dari="kanan", alpha_maks=235, alpha_min=0)
    draw = ImageDraw.Draw(img)

    tanda    = info.get("tanda_terbaik", "")
    prt      = info.get("peruntungan_hari", "Baik")
    warna    = info.get("warna_hari", "")
    angka    = info.get("angka_hari", "")
    tgl      = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # Stripe biru atas
    draw.rectangle([0, 0, W, 10], fill=sk.get("aksen", (0, 160, 255)))

    # Badge peruntungan kiri atas
    bg_badge = sk.get("badge", (0, 60, 180))
    bw = len(icon_txt) * 20 + 50
    draw_rounded_rect(draw, 24, 20, 24 + bw, 74, 24, fill=bg_badge)
    draw.text((40, 28), icon_txt, font=get_font(fp, 30),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # Nama channel kiri bawah
    draw_text_stroke(draw, 30, H - 44, NAMA_CHANNEL, get_font(fp, 28),
                     sk.get("teks", (150, 220, 255)), stroke=3,
                     stroke_fill=(0, 15, 60))

    # Label zodiak terbaik kanan
    draw_text_stroke(draw, W - 36, H - 240, "Zodiak Terbaik Hari Ini",
                     get_font(fp, 28), sk.get("sub", (200, 230, 255)),
                     stroke=2, stroke_fill=(0, 0, 0), anchor="rt")

    # Nama tanda besar kanan
    draw_text_stroke(draw, W - 30, H - 200, tanda, get_font(fp, 98),
                     sk.get("teks", (150, 220, 255)), stroke=6,
                     stroke_fill=(0, 25, 80), anchor="rt")

    # Warna & angka hoki kanan
    draw_text_stroke(draw, W - 30, H - 92,
                     f"Warna: {warna}  |  Angka: {angka}",
                     get_font(fp, 30), sk.get("sub", (200, 230, 255)),
                     stroke=2, stroke_fill=(0, 0, 0), anchor="rt")

    # Tanggal kanan bawah
    draw_text_stroke(draw, W - 30, H - 50, tgl, get_font(fp, 26),
                     sk.get("sub", (200, 230, 255)), stroke=2,
                     stroke_fill=(0, 0, 0), anchor="rt")

    # Stripe biru bawah
    draw.rectangle([0, H - 10, W, H], fill=sk.get("aksen", (0, 160, 255)))
    img.save(output_path, "JPEG", quality=96)
    log(f" -> T2 saved: {output_path}")
    return output_path

# ═══════════════════════════════════════════════════════════
# TEMPLATE 3 – Info Shio & Bintang
# Gaya: Hijau Platinum | Teks tengah bawah
# ═══════════════════════════════════════════════════════════
def _tmpl_ch3(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)
    img = _foto_bg(brightness=1.0, blur=1)
    img = _overlay_gradient_vertikal(img, (0, 25, 10), dari="bawah",
                                     alpha_maks=235, alpha_min=0)
    draw = ImageDraw.Draw(img)

    tanda    = info.get("tanda_terbaik", "")
    prt      = info.get("peruntungan_hari", "Baik")
    warna    = info.get("warna_hari", "")
    angka    = info.get("angka_hari", "")
    tgl      = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # Bar atas
    draw.rectangle([0, 0, W, 12], fill=sk.get("aksen", (0, 230, 100)))

    # Nama channel kiri atas
    draw_text_stroke(draw, 30, 24, NAMA_CHANNEL, get_font(fp, 28),
                     sk.get("teks", (200, 255, 200)), stroke=3,
                     stroke_fill=(0, 40, 15))

    # Tanggal kanan atas
    draw_text_stroke(draw, W - 30, 24, tgl, get_font(fp, 26),
                     sk.get("teks", (200, 255, 200)), stroke=2,
                     stroke_fill=(0, 0, 0), anchor="rt")

    # Tanda besar tengah
    draw_text_stroke(draw, W // 2, H - 200, tanda, get_font(fp, 110),
                     sk.get("teks", (200, 255, 200)), stroke=7,
                     stroke_fill=(0, 50, 20), anchor="mt")

    draw_text_stroke(draw, W // 2, H - 82, "Tanda Terbaik Hari Ini",
                     get_font(fp, 32), sk.get("sub", (220, 255, 220)),
                     stroke=3, stroke_fill=(0, 0, 0), anchor="mt")

    # Badge peruntungan + warna + angka center bawah
    label_full = f"{icon_txt}  |  {warna}  |  {angka}"
    bw = len(label_full) * 17 + 60
    bx = W // 2 - bw // 2
    draw_rounded_rect(draw, bx, H - 44, bx + bw, H - 6, 18,
                      fill=sk.get("badge", (0, 130, 60)))
    draw.text((bx + 20, H - 40), label_full, font=get_font(fp, 26),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # Bar bawah
    draw.rectangle([0, H - 6, W, H], fill=sk.get("aksen", (0, 230, 100)))
    img.save(output_path, "JPEG", quality=96)
    log(f" -> T3 saved: {output_path}")
    return output_path

# ═══════════════════════════════════════════════════════════
# TEMPLATE 4 – Peruntungan Zodiak
# Gaya: Ungu Mewah | Teks kiri atas + kiri bawah
# ═══════════════════════════════════════════════════════════
def _tmpl_ch4(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)
    img = _foto_bg(brightness=0.88, blur=2)
    img = _overlay_gradient(img, (35, 0, 70), dari="kiri",
                            alpha_maks=215, alpha_min=10)
    draw = ImageDraw.Draw(img)

    tanda    = info.get("tanda_terbaik", "")
    prt      = info.get("peruntungan_hari", "Baik")
    warna    = info.get("warna_hari", "")
    angka    = info.get("angka_hari", "")
    tgl      = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # Badge "RAMALAN HARI INI" kiri atas
    draw_rounded_rect(draw, 28, 22, 370, 74, 20,
                      fill=sk.get("badge", (120, 0, 180)))
    draw.text((44, 28), "RAMALAN HARI INI", font=get_font(fp, 28),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # Nama channel kanan atas
    draw_text_stroke(draw, W - 30, 28, NAMA_CHANNEL, get_font(fp, 26),
                     sk.get("sub", (240, 200, 255)), stroke=3,
                     stroke_fill=(35, 0, 70), anchor="rt")

    # Label kiri
    draw_text_stroke(draw, 30, 96, "Zodiak Terbaik", get_font(fp, 32),
                     sk.get("sub", (240, 200, 255)), stroke=2,
                     stroke_fill=(0, 0, 0))

    # Nama tanda besar kiri
    draw_text_stroke(draw, 28, 130, tanda, get_font(fp, 100),
                     sk.get("teks", (255, 180, 255)), stroke=6,
                     stroke_fill=(50, 0, 100))

    # Peruntungan kiri
    draw_text_stroke(draw, 30, 242, f"Peruntungan: {prt}",
                     get_font(fp, 30), sk.get("sub", (240, 200, 255)),
                     stroke=2, stroke_fill=(0, 0, 0))

    # Badge warna & angka kiri
    badge_txt = f"{warna}  |  {angka}"
    bw = len(badge_txt) * 19 + 50
    draw_rounded_rect(draw, 28, 290, 28 + bw, 342, 20,
                      fill=sk.get("aksen", (220, 0, 255)))
    draw.text((46, 296), badge_txt, font=get_font(fp, 28),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # Tanggal bawah kiri
    draw_text_stroke(draw, 30, H - 44, tgl, get_font(fp, 26),
                     sk.get("sub", (240, 200, 255)), stroke=2,
                     stroke_fill=(0, 0, 0))

    # Border atas & bawah
    draw.rectangle([0, 0, W, 6], fill=sk.get("aksen", (220, 0, 255)))
    draw.rectangle([0, H - 6, W, H], fill=sk.get("aksen", (220, 0, 255)))
    img.save(output_path, "JPEG", quality=96)
    log(f" -> T4 saved: {output_path}")
    return output_path

# ═══════════════════════════════════════════════════════════
# TEMPLATE 5 – Cek Shio Sekarang
# Gaya: Oranye Tembaga | Card tengah layar
# ═══════════════════════════════════════════════════════════
def _tmpl_ch5(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)
    img = _foto_bg(brightness=0.88, blur=2)
    img = _overlay_warna(img, (50, 25, 0), 100)

    card_w = W - 100
    card_h = 320
    card_x = 50
    card_y = H // 2 - 160
    card = Image.new("RGBA", (card_w, card_h), (255, 245, 220, 195))
    card_full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    card_full.paste(card, (card_x, card_y))
    img = Image.alpha_composite(img.convert("RGBA"), card_full).convert("RGB")
    draw = ImageDraw.Draw(img)

    tanda    = info.get("tanda_terbaik", "")
    prt      = info.get("peruntungan_hari", "Baik")
    warna    = info.get("warna_hari", "")
    angka    = info.get("angka_hari", "")
    tgl      = datetime.now().strftime("%d %B %Y")

    # Nama channel tengah atas
    draw_text_stroke(draw, W // 2, 24, NAMA_CHANNEL, get_font(fp, 30),
                     sk.get("teks", (255, 210, 100)), stroke=3,
                     stroke_fill=(80, 40, 0), anchor="mt")

    # Label dalam card
    draw_text_stroke(draw, W // 2, H // 2 - 148, "Shio Terbaik Hari Ini",
                     get_font(fp, 28), (100, 55, 0), stroke=1,
                     stroke_fill=(200, 160, 60), anchor="mt")

    # Nama tanda besar
    draw_text_stroke(draw, W // 2, H // 2 - 116, tanda, get_font(fp, 102),
                     (75, 40, 0), stroke=4,
                     stroke_fill=(255, 200, 60), anchor="mt")

    # Peruntungan
    draw_text_stroke(draw, W // 2, H // 2 + 10, f"Peruntungan: {prt}",
                     get_font(fp, 28), (110, 65, 10), stroke=2,
                     stroke_fill=(255, 215, 100), anchor="mt")

    # Badge warna & angka
    badge_txt = f"Warna: {warna}  |  Angka: {angka}"
    bw = len(badge_txt) * 17 + 60
    bx = W // 2 - bw // 2
    draw_rounded_rect(draw, bx, H // 2 + 56, bx + bw, H // 2 + 106, 20,
                      fill=sk.get("badge", (200, 80, 0)))
    draw.text((bx + 20, H // 2 + 62), badge_txt, font=get_font(fp, 28),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # Tanggal tengah bawah
    draw_text_stroke(draw, W // 2, H - 38, tgl, get_font(fp, 28),
                     sk.get("teks", (255, 210, 100)), stroke=3,
                     stroke_fill=(80, 40, 0), anchor="mt")

    # Strip atas & bawah
    draw.rectangle([0, 0, W, 8], fill=sk.get("aksen", (255, 140, 0)))
    draw.rectangle([0, H - 8, W, H], fill=sk.get("aksen", (255, 140, 0)))
    img.save(output_path, "JPEG", quality=96)
    log(f" -> T5 saved: {output_path}")
    return output_path
