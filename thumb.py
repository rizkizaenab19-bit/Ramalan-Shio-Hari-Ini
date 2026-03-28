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

# ─────────────────────────────────────────────────────────
# HELPER: Tulis judul besar dengan auto-wrap, 2 baris maks
# ─────────────────────────────────────────────────────────
def _tulis_judul_besar(draw, judul, fp, sk, y_start=30, font_size=88):
    """Tulis judul clickbait besar di bagian atas thumbnail."""
    from PIL import ImageFont
    judul = judul.upper()
    MAX_W = W - 60  # margin kiri kanan
    font = get_font(fp, font_size)

    # Wrap otomatis
    words = judul.split()
    baris = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        try:
            tw = draw.textlength(test, font=font)
        except Exception:
            tw = len(test) * font_size * 0.6
        if tw <= MAX_W:
            current = test
        else:
            if current:
                baris.append(current)
            current = word
        if len(baris) >= 2:
            current = " ".join([current] + words[words.index(word)+1:])
            break
    if current:
        baris.append(current)
    baris = baris[:3]  # max 3 baris

    line_h = font_size + 10
    y = y_start
    for bl in baris:
        # Background hitam semi-transparan per baris agar terbaca
        try:
            tw = draw.textlength(bl, font=font)
        except Exception:
            tw = len(bl) * font_size * 0.6
        pad = 18
        bx0 = W // 2 - int(tw) // 2 - pad
        bx1 = W // 2 + int(tw) // 2 + pad
        from PIL import Image, ImageDraw
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rounded_rectangle([bx0, y - 8, bx1, y + font_size + 8],
                              radius=14, fill=(0, 0, 0, 160))
        from PIL import Image as _PIL
        base = draw._image if hasattr(draw, "_image") else None
        if base:
            merged = _PIL.alpha_composite(base.convert("RGBA"), ov)
            base.paste(merged.convert("RGB"))
            draw = ImageDraw.Draw(base)

        # Teks dengan stroke tebal
        draw_text_stroke(
            draw, W // 2, y, bl, font,
            sk.get("teks", (255, 220, 0)),
            stroke=5,
            stroke_fill=(0, 0, 0),
            anchor="mt"
        )
        y += line_h
    return draw, y  # kembalikan draw dan posisi Y terakhir


# ═══════════════════════════════════════════════════════════
# TEMPLATE 1 – Ramalan Shio Hari Ini
# Gaya: Merah Emas | JUDUL BESAR ATAS | Tanda besar bawah
# ═══════════════════════════════════════════════════════════
def _tmpl_ch1(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)

    img = _foto_bg(brightness=0.75, blur=3)
    img = _overlay_gradient_vertikal(img, (40, 0, 10), dari="bawah", alpha_maks=230, alpha_min=30)
    img = _overlay_gradient_vertikal(img, (0, 0, 0), dari="atas", alpha_maks=180, alpha_min=0)

    draw = ImageDraw.Draw(img)

    tanda = info.get("tanda_terbaik", "")
    prt   = info.get("peruntungan_hari", "Baik")
    warna = info.get("warna_hari", "")
    angka = info.get("angka_hari", "")
    tgl   = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # ── JUDUL BESAR di bagian atas ──
    judul_bersih = re.sub(r'[^\w\s!?.,|:-]', '', judul).strip()
    draw, y_setelah_judul = _tulis_judul_besar(draw, judul_bersih, fp, sk, y_start=28, font_size=82)

    # ── Badge peruntungan kiri ──
    bg_badge = sk.get("badge", (200, 0, 0))
    tc_badge = sk.get("hl_teks", (255, 255, 255))
    bw = len(icon_txt) * 20 + 50
    draw_rounded_rect(draw, 30, H - 145, 30 + bw, H - 95, 22, fill=bg_badge)
    draw.text((48, H - 140), icon_txt, font=get_font(fp, 30), fill=tc_badge)

    # ── Nama channel kanan atas badge ──
    draw_text_stroke(draw, W - 30, H - 140, NAMA_CHANNEL, get_font(fp, 26),
                     sk.get("teks", (255, 220, 0)), stroke=3,
                     stroke_fill=(60, 0, 0), anchor="rt")

    # ── Tanda besar bawah kiri ──
    draw_text_stroke(draw, 30, H - 90, tanda, get_font(fp, 110),
                     sk.get("teks", (255, 220, 0)), stroke=7, stroke_fill=(80, 0, 0))

    # ── Warna & angka hoki bawah kanan ──
    draw_text_stroke(draw, W - 30, H - 52,
                     f"Warna: {warna} | Angka: {angka}",
                     get_font(fp, 28), sk.get("sub", (255, 200, 150)),
                     stroke=2, stroke_fill=(0, 0, 0), anchor="rt")

    # ── Tanggal bawah kanan ──
    draw_text_stroke(draw, W - 30, H - 22, tgl, get_font(fp, 24),
                     sk.get("sub", (255, 200, 150)), stroke=2,
                     stroke_fill=(0, 0, 0), anchor="rb")

    # ── Strip bawah ──
    draw.rectangle([0, H - 8, W, H], fill=sk.get("aksen", (255, 80, 0)))

    img.save(output_path, "JPEG", quality=96)
    log(f" -> T1 saved: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════
# TEMPLATE 2 – Zodiak Harian Update
# Gaya: Biru Perak | JUDUL BESAR ATAS | Tanda kanan bawah
# ═══════════════════════════════════════════════════════════
def _tmpl_ch2(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)

    img = _foto_bg(brightness=0.75, blur=2)
    img = _overlay_gradient_vertikal(img, (0, 0, 0), dari="atas", alpha_maks=200, alpha_min=0)
    img = _overlay_gradient(img, (0, 20, 80), dari="kanan", alpha_maks=210, alpha_min=0)

    draw = ImageDraw.Draw(img)

    tanda = info.get("tanda_terbaik", "")
    prt   = info.get("peruntungan_hari", "Baik")
    warna = info.get("warna_hari", "")
    angka = info.get("angka_hari", "")
    tgl   = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # ── Strip biru atas ──
    draw.rectangle([0, 0, W, 10], fill=sk.get("aksen", (0, 160, 255)))

    # ── JUDUL BESAR ──
    judul_bersih = re.sub(r'[^\w\s!?.,|:-]', '', judul).strip()
    draw, y_setelah_judul = _tulis_judul_besar(draw, judul_bersih, fp, sk, y_start=22, font_size=80)

    # ── Badge peruntungan kiri bawah ──
    bg_badge = sk.get("badge", (0, 60, 180))
    bw = len(icon_txt) * 20 + 50
    draw_rounded_rect(draw, 24, H - 142, 24 + bw, H - 92, 22, fill=bg_badge)
    draw.text((40, H - 137), icon_txt, font=get_font(fp, 30),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # ── Nama channel kiri bawah ──
    draw_text_stroke(draw, 30, H - 55, NAMA_CHANNEL, get_font(fp, 26),
                     sk.get("teks", (150, 220, 255)), stroke=3,
                     stroke_fill=(0, 15, 60))

    # ── Tanda besar kanan bawah ──
    draw_text_stroke(draw, W - 30, H - 95, tanda, get_font(fp, 110),
                     sk.get("teks", (150, 220, 255)), stroke=7,
                     stroke_fill=(0, 25, 80), anchor="rt")

    # ── Warna & angka ──
    draw_text_stroke(draw, W - 30, H - 50,
                     f"Warna: {warna} | Angka: {angka}",
                     get_font(fp, 26), sk.get("sub", (200, 230, 255)),
                     stroke=2, stroke_fill=(0, 0, 0), anchor="rt")

    # ── Tanggal kiri bawah ──
    draw_text_stroke(draw, 30, H - 24, tgl, get_font(fp, 24),
                     sk.get("sub", (200, 230, 255)), stroke=2,
                     stroke_fill=(0, 0, 0))

    # ── Strip biru bawah ──
    draw.rectangle([0, H - 8, W, H], fill=sk.get("aksen", (0, 160, 255)))

    img.save(output_path, "JPEG", quality=96)
    log(f" -> T2 saved: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════
# TEMPLATE 3 – Info Shio & Bintang
# Gaya: Hijau Platinum | JUDUL BESAR ATAS | Tanda tengah
# ═══════════════════════════════════════════════════════════
def _tmpl_ch3(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)

    img = _foto_bg(brightness=0.75, blur=1)
    img = _overlay_gradient_vertikal(img, (0, 0, 0), dari="atas", alpha_maks=200, alpha_min=0)
    img = _overlay_gradient_vertikal(img, (0, 25, 10), dari="bawah", alpha_maks=220, alpha_min=0)

    draw = ImageDraw.Draw(img)

    tanda = info.get("tanda_terbaik", "")
    prt   = info.get("peruntungan_hari", "Baik")
    warna = info.get("warna_hari", "")
    angka = info.get("angka_hari", "")
    tgl   = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # ── Bar atas ──
    draw.rectangle([0, 0, W, 10], fill=sk.get("aksen", (0, 230, 100)))

    # ── JUDUL BESAR ──
    judul_bersih = re.sub(r'[^\w\s!?.,|:-]', '', judul).strip()
    draw, y_setelah_judul = _tulis_judul_besar(draw, judul_bersih, fp, sk, y_start=22, font_size=80)

    # ── Tanda besar tengah bawah ──
    draw_text_stroke(draw, W // 2, H - 185, tanda, get_font(fp, 120),
                     sk.get("teks", (200, 255, 200)), stroke=8,
                     stroke_fill=(0, 50, 20), anchor="mt")

    # ── Badge bawah tengah ──
    label_full = f"{icon_txt} | Warna: {warna} | Angka: {angka}"
    bw = len(label_full) * 17 + 60
    bx = W // 2 - bw // 2
    draw_rounded_rect(draw, bx, H - 52, bx + bw, H - 10, 18,
                      fill=sk.get("badge", (0, 130, 60)))
    draw.text((bx + 20, H - 46), label_full, font=get_font(fp, 26),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # ── Nama channel & tanggal ──
    draw_text_stroke(draw, 30, H - 90, NAMA_CHANNEL, get_font(fp, 24),
                     sk.get("teks", (200, 255, 200)), stroke=2,
                     stroke_fill=(0, 40, 15))
    draw_text_stroke(draw, W - 30, H - 90, tgl, get_font(fp, 24),
                     sk.get("teks", (200, 255, 200)), stroke=2,
                     stroke_fill=(0, 0, 0), anchor="rt")

    # ── Bar bawah ──
    draw.rectangle([0, H - 8, W, H], fill=sk.get("aksen", (0, 230, 100)))

    img.save(output_path, "JPEG", quality=96)
    log(f" -> T3 saved: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════
# TEMPLATE 4 – Peruntungan Zodiak
# Gaya: Ungu Mewah | JUDUL BESAR ATAS | Tanda kiri
# ═══════════════════════════════════════════════════════════
def _tmpl_ch4(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)

    img = _foto_bg(brightness=0.75, blur=2)
    img = _overlay_gradient_vertikal(img, (0, 0, 0), dari="atas", alpha_maks=200, alpha_min=0)
    img = _overlay_gradient(img, (35, 0, 70), dari="kiri",
                            alpha_maks=200, alpha_min=10)

    draw = ImageDraw.Draw(img)

    tanda = info.get("tanda_terbaik", "")
    prt   = info.get("peruntungan_hari", "Baik")
    warna = info.get("warna_hari", "")
    angka = info.get("angka_hari", "")
    tgl   = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # ── JUDUL BESAR ──
    judul_bersih = re.sub(r'[^\w\s!?.,|:-]', '', judul).strip()
    draw, y_setelah_judul = _tulis_judul_besar(draw, judul_bersih, fp, sk, y_start=22, font_size=80)

    # ── Tanda besar kiri bawah ──
    draw_text_stroke(draw, 28, H - 185, tanda, get_font(fp, 115),
                     sk.get("teks", (255, 180, 255)), stroke=7,
                     stroke_fill=(50, 0, 100))

    # ── Badge peruntungan ──
    draw_rounded_rect(draw, 28, H - 58, 320, H - 10, 18,
                      fill=sk.get("badge", (120, 0, 180)))
    draw.text((44, H - 52), icon_txt, font=get_font(fp, 28),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # ── Warna & angka kanan bawah ──
    draw_text_stroke(draw, W - 30, H - 52,
                     f"Warna: {warna} | Angka: {angka}",
                     get_font(fp, 28), sk.get("sub", (240, 200, 255)),
                     stroke=2, stroke_fill=(0, 0, 0), anchor="rt")

    # ── Nama channel & tanggal ──
    draw_text_stroke(draw, W - 30, H - 90, NAMA_CHANNEL, get_font(fp, 24),
                     sk.get("sub", (240, 200, 255)), stroke=2,
                     stroke_fill=(35, 0, 70), anchor="rt")
    draw_text_stroke(draw, 30, H - 90, tgl, get_font(fp, 24),
                     sk.get("sub", (240, 200, 255)), stroke=2,
                     stroke_fill=(0, 0, 0))

    # ── Border atas & bawah ──
    draw.rectangle([0, 0, W, 6], fill=sk.get("aksen", (220, 0, 255)))
    draw.rectangle([0, H - 8, W, H], fill=sk.get("aksen", (220, 0, 255)))

    img.save(output_path, "JPEG", quality=96)
    log(f" -> T4 saved: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════
# TEMPLATE 5 – Cek Shio Sekarang
# Gaya: Oranye Tembaga | JUDUL BESAR ATAS | Card tengah
# ═══════════════════════════════════════════════════════════
def _tmpl_ch5(info, judul, output_path):
    from PIL import Image, ImageDraw
    fp = _fp()
    sk = _sk(info)

    img = _foto_bg(brightness=0.75, blur=2)
    img = _overlay_gradient_vertikal(img, (0, 0, 0), dari="atas", alpha_maks=200, alpha_min=0)
    img = _overlay_warna(img, (50, 25, 0), 80)

    draw = ImageDraw.Draw(img)

    tanda = info.get("tanda_terbaik", "")
    prt   = info.get("peruntungan_hari", "Baik")
    warna = info.get("warna_hari", "")
    angka = info.get("angka_hari", "")
    tgl   = datetime.now().strftime("%d %B %Y")
    icon_txt = sk.get("icon", prt)

    # ── JUDUL BESAR ──
    judul_bersih = re.sub(r'[^\w\s!?.,|:-]', '', judul).strip()
    draw, y_setelah_judul = _tulis_judul_besar(draw, judul_bersih, fp, sk, y_start=22, font_size=80)

    # ── Card tengah bawah ──
    card_y = H - 270
    card = Image.new("RGBA", (W - 100, 220), (255, 245, 220, 190))
    card_full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    card_full.paste(card, (50, card_y))
    img = Image.alpha_composite(img.convert("RGBA"), card_full).convert("RGB")
    draw = ImageDraw.Draw(img)

    # ── Tanda besar dalam card ──
    draw_text_stroke(draw, W // 2, card_y + 10, tanda, get_font(fp, 110),
                     (75, 40, 0), stroke=5,
                     stroke_fill=(255, 200, 60), anchor="mt")

    # ── Peruntungan dalam card ──
    draw_text_stroke(draw, W // 2, card_y + 130,
                     f"Peruntungan: {prt}",
                     get_font(fp, 28), (110, 65, 10), stroke=2,
                     stroke_fill=(255, 215, 100), anchor="mt")

    # ── Badge warna & angka ──
    badge_txt = f"Warna: {warna} | Angka: {angka}"
    bw = len(badge_txt) * 17 + 60
    bx = W // 2 - bw // 2
    draw_rounded_rect(draw, bx, card_y + 168, bx + bw, card_y + 212, 18,
                      fill=sk.get("badge", (200, 80, 0)))
    draw.text((bx + 20, card_y + 174), badge_txt, font=get_font(fp, 26),
              fill=sk.get("hl_teks", (255, 255, 255)))

    # ── Nama channel & tanggal bawah ──
    draw_text_stroke(draw, 30, H - 24, NAMA_CHANNEL, get_font(fp, 24),
                     sk.get("teks", (255, 210, 100)), stroke=3,
                     stroke_fill=(80, 40, 0))
    draw_text_stroke(draw, W - 30, H - 24, tgl, get_font(fp, 24),
                     sk.get("teks", (255, 210, 100)), stroke=2,
                     stroke_fill=(80, 40, 0), anchor="rt")

    # ── Strip atas & bawah ──
    draw.rectangle([0, 0, W, 8], fill=sk.get("aksen", (255, 140, 0)))
    draw.rectangle([0, H - 8, W, H], fill=sk.get("aksen", (255, 140, 0)))

    img.save(output_path, "JPEG", quality=96)
    log(f" -> T5 saved: {output_path}")
    return output_path
