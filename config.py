# config.py
import os

_ch_raw = os.environ.get("CHANNEL_ID", "1").strip()
CHANNEL_ID = int(_ch_raw) if _ch_raw.isdigit() else 1

CHANNEL_CONFIG = {
    1: {
        "nama": "Ramalan Shio Hari Ini",
        "sapaan": "Sobat Shio",
        "voice": "id-ID-ArdiNeural",
        "rate": "+5%",
        "gaya": "mistis_bijak",
        "skema_warna": "merah_emas",
        "tipe": "shio",
        "keywords_img": [
            "chinese zodiac animals art",
            "shio tionghoa colorful",
            "chinese horoscope symbols",
            "zodiac animal chinese new year",
            "feng shui lucky symbols",
            "chinese astrology wheel",
            "mystical zodiac symbols",
            "chinese zodiac illustration",
            "shio keberuntungan art",
            "chinese astrology colorful",
        ],
        "keywords_vid": [
            "chinese zodiac animation",
            "mystical stars cosmic background",
            "zodiac symbols floating animation",
            "feng shui energy background",
        ],
    },
    2: {
        "nama": "Zodiak Harian Update",
        "sapaan": "teman-teman",
        "voice": "id-ID-GadisNeural",
        "rate": "+3%",
        "gaya": "santai_edukatif",
        "skema_warna": "biru_perak",
        "tipe": "zodiak",
        "keywords_img": [
            "western zodiac signs gold",
            "horoscope symbols stars",
            "zodiac constellation night sky",
            "astrology wheel horoscope",
            "zodiac symbols beautiful art",
            "horoscope daily fortune stars",
            "astrology celestial background",
            "zodiac constellation glow",
            "horoscope fortune stars",
            "zodiac signs illustration",
        ],
        "keywords_vid": [
            "zodiac constellation animation",
            "stars night sky cosmic",
            "horoscope symbols floating",
            "astrology background glow",
        ],
    },
    3: {
        "nama": "Info Shio & Bintang",
        "sapaan": "pemirsa",
        "voice": "id-ID-ArdiNeural",
        "rate": "-3%",
        "gaya": "berita_singkat",
        "skema_warna": "hijau_platinum",
        "tipe": "shio",
        "keywords_img": [
            "shio chinese zodiac art",
            "chinese astrology symbols",
            "zodiac animal cute art",
            "chinese horoscope art colorful",
            "lucky symbols chinese",
            "feng shui symbols art",
            "chinese zodiac colorful",
            "horoscope fortune art",
            "zodiac signs traditional chinese",
            "chinese astrology mystical",
        ],
        "keywords_vid": [
            "chinese zodiac background animation",
            "fortune symbols animation",
            "feng shui background mystical",
            "mystical chinese symbols glow",
        ],
    },
    4: {
        "nama": "Peruntungan Zodiak",
        "sapaan": "guys",
        "voice": "id-ID-GadisNeural",
        "rate": "+8%",
        "gaya": "energik_motivatif",
        "skema_warna": "ungu_mewah",
        "tipe": "zodiak",
        "keywords_img": [
            "zodiac signs glowing neon",
            "horoscope neon symbols art",
            "zodiac wheel glowing cosmic",
            "astrology symbols vibrant glow",
            "constellation zodiac glow",
            "zodiac fortune colorful vibrant",
            "horoscope symbols bright neon",
            "astrology wheel cosmic glow",
            "zodiac energy symbols art",
            "fortune zodiac neon glow",
        ],
        "keywords_vid": [
            "zodiac symbols glowing animation",
            "cosmic energy galaxy background",
            "stars galaxy animation cosmic",
            "fortune symbols glow animation",
        ],
    },
    5: {
        "nama": "Cek Shio Sekarang",
        "sapaan": "sahabat",
        "voice": "id-ID-ArdiNeural",
        "rate": "+0%",
        "gaya": "percakapan_akrab",
        "skema_warna": "oranye_tembaga",
        "tipe": "shio",
        "keywords_img": [
            "shio tionghoa cute illustration",
            "chinese zodiac cute art",
            "zodiac animal illustration fun",
            "chinese horoscope colorful cute",
            "shio animal art colorful",
            "chinese new year symbols art",
            "zodiac fortune art cute",
            "lucky animal chinese art",
            "chinese zodiac illustration fun",
            "shio hoki art",
        ],
        "keywords_vid": [
            "chinese zodiac cute animation",
            "lucky symbols animation fun",
            "chinese new year animation",
            "zodiac animals animation cute",
        ],
    },
}

CFG = CHANNEL_CONFIG.get(CHANNEL_ID, CHANNEL_CONFIG[1])
NAMA_CHANNEL      = CFG["nama"]
SAPAAN            = CFG["sapaan"]
VOICE             = CFG["voice"]
VOICE_RATE        = CFG["rate"]
NARASI_GAYA       = CFG["gaya"]
TIPE_KONTEN       = CFG["tipe"]
KATA_KUNCI_GAMBAR = CFG["keywords_img"]
KATA_KUNCI_VIDEO  = CFG["keywords_vid"]

GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "")
PEXELS_API_KEY  = os.environ.get("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

YOUTUBE_CATEGORY = "22"  # People & Blogs
YOUTUBE_TAGS = [
    "ramalan zodiak", "shio hari ini", "zodiak harian",
    "ramalan bintang", "peruntungan zodiak", "shio tionghoa",
    "horoscope indonesia", "ramalan hari ini", "zodiak 2026", "shio 2026",
]

VIDEO_WIDTH  = 1920
VIDEO_HEIGHT = 1080
FPS          = 30
FOLDER_GAMBAR      = "gambar_bank"
FOLDER_VIDEO_BANK  = "video_bank"
JUMLAH_GAMBAR_MIN  = 10
JUMLAH_DL_GAMBAR   = 20
JUMLAH_VIDEO_MIN   = 4
JUMLAH_DL_VIDEO    = 8
SIMPAN_VIDEO_MAKS  = 3
FFMPEG_LOG         = "ffmpeg_log.txt"

SKEMA_THUMBNAIL = {
    "merah_emas": {
        "Sangat Baik": {
            "badge": (200, 0, 0), "aksen": (255, 80, 0),
            "teks": (255, 220, 0), "sub": (255, 200, 150),
            "hl_teks": (255, 255, 255), "icon": "SANGAT BAIK",
            "bg_grad_atas": (60, 0, 0),
        },
        "Baik": {
            "badge": (140, 100, 0), "aksen": (255, 190, 0),
            "teks": (255, 230, 100), "sub": (255, 240, 180),
            "hl_teks": (255, 255, 255), "icon": "BAIK",
            "bg_grad_atas": (40, 30, 0),
        },
        "Cukup": {
            "badge": (100, 60, 0), "aksen": (180, 120, 40),
            "teks": (220, 190, 120), "sub": (240, 215, 160),
            "hl_teks": (255, 255, 255), "icon": "CUKUP",
            "bg_grad_atas": (30, 20, 0),
        },
    },
    "biru_perak": {
        "Sangat Baik": {
            "badge": (0, 60, 180), "aksen": (0, 160, 255),
            "teks": (150, 220, 255), "sub": (200, 230, 255),
            "hl_teks": (255, 255, 255), "icon": "SANGAT BAIK",
            "bg_grad_atas": (0, 20, 60),
        },
        "Baik": {
            "badge": (80, 80, 160), "aksen": (160, 160, 255),
            "teks": (200, 200, 255), "sub": (220, 220, 255),
            "hl_teks": (255, 255, 255), "icon": "BAIK",
            "bg_grad_atas": (20, 20, 50),
        },
        "Cukup": {
            "badge": (60, 60, 120), "aksen": (120, 130, 200),
            "teks": (180, 190, 240), "sub": (210, 215, 250),
            "hl_teks": (255, 255, 255), "icon": "CUKUP",
            "bg_grad_atas": (15, 15, 40),
        },
    },
    "hijau_platinum": {
        "Sangat Baik": {
            "badge": (0, 130, 60), "aksen": (0, 230, 100),
            "teks": (200, 255, 200), "sub": (220, 255, 220),
            "hl_teks": (0, 50, 0), "icon": "SANGAT BAIK",
            "bg_grad_atas": (0, 40, 15),
        },
        "Baik": {
            "badge": (60, 120, 60), "aksen": (150, 255, 150),
            "teks": (220, 255, 220), "sub": (230, 255, 230),
            "hl_teks": (0, 50, 0), "icon": "BAIK",
            "bg_grad_atas": (15, 35, 15),
        },
        "Cukup": {
            "badge": (40, 100, 50), "aksen": (120, 200, 130),
            "teks": (190, 240, 200), "sub": (210, 245, 215),
            "hl_teks": (0, 40, 10), "icon": "CUKUP",
            "bg_grad_atas": (10, 25, 12),
        },
    },
    "ungu_mewah": {
        "Sangat Baik": {
            "badge": (120, 0, 180), "aksen": (220, 0, 255),
            "teks": (255, 180, 255), "sub": (240, 200, 255),
            "hl_teks": (255, 255, 255), "icon": "SANGAT BAIK",
            "bg_grad_atas": (40, 0, 60),
        },
        "Baik": {
            "badge": (100, 50, 150), "aksen": (200, 150, 255),
            "teks": (240, 220, 255), "sub": (245, 230, 255),
            "hl_teks": (255, 255, 255), "icon": "BAIK",
            "bg_grad_atas": (30, 15, 50),
        },
        "Cukup": {
            "badge": (80, 40, 120), "aksen": (170, 120, 220),
            "teks": (220, 200, 245), "sub": (235, 220, 250),
            "hl_teks": (255, 255, 255), "icon": "CUKUP",
            "bg_grad_atas": (20, 10, 35),
        },
    },
    "oranye_tembaga": {
        "Sangat Baik": {
            "badge": (200, 80, 0), "aksen": (255, 140, 0),
            "teks": (255, 210, 100), "sub": (255, 225, 150),
            "hl_teks": (50, 20, 0), "icon": "SANGAT BAIK",
            "bg_grad_atas": (60, 25, 0),
        },
        "Baik": {
            "badge": (180, 100, 0), "aksen": (255, 160, 50),
            "teks": (255, 220, 150), "sub": (255, 235, 180),
            "hl_teks": (50, 25, 0), "icon": "BAIK",
            "bg_grad_atas": (55, 30, 0),
        },
        "Cukup": {
            "badge": (150, 80, 0), "aksen": (220, 130, 40),
            "teks": (240, 200, 130), "sub": (245, 220, 170),
            "hl_teks": (40, 20, 0), "icon": "CUKUP",
            "bg_grad_atas": (45, 24, 0),
        },
    },
}

SKEMA_AKTIF = SKEMA_THUMBNAIL.get(CFG["skema_warna"], SKEMA_THUMBNAIL["merah_emas"])

def log(msg):
    from datetime import datetime
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)
