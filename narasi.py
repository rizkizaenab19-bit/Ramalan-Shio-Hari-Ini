# narasi.py
import re, random, time
import requests
from datetime import datetime
from config import (
    NAMA_CHANNEL, NARASI_GAYA, TIPE_KONTEN,
    GEMINI_API_KEY, CHANNEL_ID, SAPAAN,
)
from utils import log
import os

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
GROQ_API_KEY       = os.environ.get("GROQ_API_KEY", "")

_BULAN_ID = {
    "January":"Januari","February":"Februari","March":"Maret",
    "April":"April","May":"Mei","June":"Juni",
    "July":"Juli","August":"Agustus","September":"September",
    "October":"Oktober","November":"November","December":"Desember",
}

def _tgl_id(x):
    x = str(x).strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", x)
    if m:
        y, mo, d = m.groups()
        try:
            from datetime import date as _d
            dt = _d(int(y), int(mo), int(d))
            b = dt.strftime("%B")
            hari = dt.strftime("%A")
            hari_id = {
                "Monday":"Senin","Tuesday":"Selasa","Wednesday":"Rabu",
                "Thursday":"Kamis","Friday":"Jumat","Saturday":"Sabtu",
                "Sunday":"Minggu",
            }.get(hari, hari)
            return f"{hari_id}, {int(d)} {_BULAN_ID.get(b, b)} {y}"
        except:
            pass
    return x

# ════════════════════════════════════════════════════════════
# MODEL LIST (Semua aktif per 2026)
# ════════════════════════════════════════════════════════════
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

GEMINI_BASE = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/{model}:generateContent"
)

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-8b-8192",
    "mixtral-8x7b-32768",
]

OPENROUTER_MODELS = [
    "meta-llama/llama-3.3-70b-instruct",
    "google/gemini-2.0-flash-001",
    "deepseek/deepseek-chat",
    "mistralai/mistral-small",
]

# ════════════════════════════════════════════════════════════
# PROMPT BUILDER
# ════════════════════════════════════════════════════════════
def _build_prompt(info):
    tgl           = _tgl_id(info["tanggal"])
    waktu         = info["waktu"]
    tipe          = info["tipe_label"]
    tanda_list    = info["tanda_list"]
    tanda_terbaik = info["tanda_terbaik"]
    peruntungan_hari = info["peruntungan_hari"]
    warna_hari    = info["warna_hari"]
    angka_hari    = info["angka_hari"]

    ringkasan = ""
    for tanda, r in info["ramalan"].items():
        ringkasan += (
            f"- {tanda}: bintang {r['bintang']}/5, peruntungan {r['peruntungan']}, "
            f"warna hoki {r['warna_hoki']}, angka hoki {r['angka_hoki']}\n"
            f"  Afirmasi: {r['afirmasi']}\n"
            f"  Cinta: {r['cinta']}\n"
            f"  Karir: {r['karir']}\n"
            f"  Keuangan: {r['keuangan']}\n"
            f"  Kesehatan: {r['kesehatan']}\n"
        )

    gaya_map = {
        "mistis_bijak": (
            "Gunakan gaya bahasa MISTIS dan BIJAK seperti seorang ahli astrologi yang bijaksana. "
            "Penuh dengan kata-kata positif, afirmatif, dan memberi harapan."
        ),
        "santai_edukatif": (
            "Gunakan gaya bahasa SANTAI dan EDUKATIF. "
            "Ramah, mudah dipahami, sisipkan penjelasan singkat tentang makna zodiak."
        ),
        "berita_singkat": (
            "Gunakan gaya bahasa BERITA SINGKAT seperti reporter TV. "
            "Padat, jelas, namun tetap penuh energi positif."
        ),
        "energik_motivatif": (
            "Gunakan gaya bahasa ENERGIK dan MOTIVATIF. "
            "Semangati penonton dengan afirmasi positif dan kata-kata pemberdayaan diri."
        ),
        "percakapan_akrab": (
            "Gunakan gaya bahasa PERCAKAPAN AKRAB seperti ngobrol dengan sahabat. "
            "Santai, natural, dan penuh semangat positif."
        ),
    }
    gaya_instruksi = gaya_map.get(NARASI_GAYA, gaya_map["santai_edukatif"])

    return (
        f'Kamu adalah narrator video YouTube channel "{NAMA_CHANNEL}".\n\n'
        f"{gaya_instruksi}\n\n"
        f"DATA RAMALAN {tipe.upper()} HARI INI:\n"
        f"- Tanggal           : {tgl}\n"
        f"- Waktu             : {waktu}\n"
        f"- {tipe} Terbaik    : {tanda_terbaik}\n"
        f"- Peruntungan Hari  : {peruntungan_hari}\n"
        f"- Warna Hoki Hari   : {warna_hari}\n"
        f"- Angka Hoki Hari   : {angka_hari}\n\n"
        f"DATA LENGKAP RAMALAN TIAP {tipe.upper()}:\n"
        f"{ringkasan}\n"
        f"TUGAS:\n"
        f"1. Buat JUDUL video menarik (maksimal 80 karakter)\n"
        f"2. Buat NARASI video berdurasi 6-8 menit (900-1100 kata)\n\n"
        f"FORMAT OUTPUT (WAJIB IKUTI PERSIS):\n"
        f"JUDUL: [judul video di sini]\n"
        f"NARASI:\n"
        f"[narasi lengkap di sini]\n\n"
        f"ATURAN NARASI:\n"
        f'- Kalimat pertama WAJIB: "Halo {SAPAAN},"\n'
        f"- Sebutkan tanggal dan tema hari ini\n"
        f"- Bacakan ramalan untuk SEMUA {len(tanda_list)} {tipe}\n"
        f"- Setiap {tipe} mendapat porsi yang cukup (minimal 4 kalimat)\n"
        f"- Sampaikan afirmasi, cinta, karir, keuangan, kesehatan setiap {tipe}\n"
        f"- Sebutkan warna hoki dan angka hoki masing-masing {tipe}\n"
        f"- Tutup dengan pesan inspiratif dan ajakan subscribe & like\n"
        f"- JANGAN gunakan emoji, simbol bintang (*), atau markdown\n"
        f"- JANGAN gunakan tanda bintang atau tanda pagar\n"
        f"- Natural saat dibaca/didengar untuk text-to-speech\n"
        # BARU - lebih singkat, render lebih cepat
        f"- WAJIB minimal 400 kata, maksimal 550 kata\n"
        f"- Durasi video target: 4-5 menit saja\n"
        f"- Setiap {tipe} cukup 2 kalimat singkat saja\n"
    )

# ════════════════════════════════════════════════════════════
# CALL GEMINI
# ════════════════════════════════════════════════════════════
def _call_gemini(prompt):
    if not GEMINI_API_KEY:
        log(" -> GEMINI_API_KEY kosong, skip Gemini")
        return None
    for model in GEMINI_MODELS:
        url = GEMINI_BASE.format(model=model)
        for attempt in range(1, 4):
            try:
                log(f" -> Gemini [{model}] attempt {attempt}/3...")
                resp = requests.post(
                    url,
                    params={"key": GEMINI_API_KEY},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "temperature": 0.85,
                            "maxOutputTokens": 4000,
                            "topP": 0.9,
                        },
                    },
                    timeout=60,
                )
                if resp.status_code == 429:
                    wait = attempt * 20
                    log(f" -> Rate limit 429, tunggu {wait}s...")
                    time.sleep(wait); continue
                if resp.status_code == 503:
                    wait = attempt * 10
                    log(f" -> 503, tunggu {wait}s...")
                    time.sleep(wait); continue
                if resp.status_code == 404:
                    log(f" -> 404 model tidak ditemukan, skip ke model lain")
                    break
                resp.raise_for_status()
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                log(f" -> Gemini [{model}] OK!")
                return text
            except requests.exceptions.HTTPError as e:
                log(f" -> HTTP error: {e}")
                if resp.status_code == 404:
                    break
                if attempt < 3: time.sleep(attempt * 10)
            except Exception as e:
                log(f" -> Error: {e}")
                if attempt < 3: time.sleep(attempt * 5)
        log(f" -> [{model}] gagal, coba model lain...")
        time.sleep(3)
    log(" -> Semua model Gemini gagal")
    return None

# ════════════════════════════════════════════════════════════
# CALL GROQ (Fallback ke-2, GRATIS & SANGAT CEPAT)
# Daftar gratis: https://console.groq.com
# ════════════════════════════════════════════════════════════
def _call_groq(prompt):
    if not GROQ_API_KEY:
        log(" -> GROQ_API_KEY kosong, skip Groq")
        return None
    for model in GROQ_MODELS:
        for attempt in range(1, 3):
            try:
                log(f" -> Groq [{model}] attempt {attempt}/2...")
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.85,
                    },
                    timeout=60,
                )
                if resp.status_code == 429:
                    log(f" -> Rate limit Groq, tunggu 15s...")
                    time.sleep(15); continue
                if resp.status_code in (500, 502, 503):
                    time.sleep(10); continue
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                if text and len(text.strip()) > 200:
                    log(f" -> Groq [{model}] OK!")
                    return text
            except Exception as e:
                log(f" -> Error: {e}")
                if attempt < 2: time.sleep(10)
        log(f" -> [{model}] gagal, coba model Groq lain...")
        time.sleep(2)
    log(" -> Semua model Groq gagal")
    return None

# ════════════════════════════════════════════════════════════
# CALL OPENROUTER (Fallback ke-3)
# ════════════════════════════════════════════════════════════
def _call_openrouter(prompt):
    if not OPENROUTER_API_KEY:
        log(" -> OPENROUTER_API_KEY kosong, skip")
        return None
    for model in OPENROUTER_MODELS:
        for attempt in range(1, 3):
            try:
                log(f" -> OpenRouter [{model}] attempt {attempt}/2...")
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com",
                        "X-Title": NAMA_CHANNEL,
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 4000,
                        "temperature": 0.85,
                    },
                    timeout=80,
                )
                if resp.status_code == 429:
                    time.sleep(attempt * 15); continue
                if resp.status_code in (500, 502, 503):
                    time.sleep(attempt * 10); continue
                resp.raise_for_status()
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                if text and len(text.strip()) > 200:
                    log(f" -> OpenRouter [{model}] OK!")
                    return text
            except Exception as e:
                log(f" -> Error: {e}")
                if attempt < 2: time.sleep(10)
        log(f" -> [{model}] gagal, coba model lain...")
        time.sleep(3)
    log(" -> Semua model OpenRouter gagal")
    return None

# ════════════════════════════════════════════════════════════
# PARSE OUTPUT
# ════════════════════════════════════════════════════════════
def _parse_output(raw):
    judul  = ""
    narasi = ""
    lines  = raw.strip().splitlines()
    for i, line in enumerate(lines):
        ls = line.strip()
        if ls.upper().startswith("JUDUL:"):
            judul = ls[6:].strip()
        elif ls.upper().startswith("NARASI:"):
            narasi = "\n".join(lines[i+1:]).strip()
            break
    if not judul and lines:
        judul = lines[0].strip()
    if not narasi:
        narasi = raw.strip()
    judul = re.sub(r'[*_`#\[\]|]', "", judul).strip()
    baris_bersih = []
    for bl in narasi.splitlines():
        bl = bl.strip()
        if not bl:
            baris_bersih.append(""); continue
        bl_l = bl.lower()
        if any(bl_l.startswith(skip) for skip in [
            "narasi:","judul:","**","##","--","catatan:","note:"
        ]):
            continue
        baris_bersih.append(bl)
    narasi_bersih = re.sub(r'[*_`#\[\]|]', "", "\n".join(baris_bersih)).strip()
    return judul, narasi_bersih

# ════════════════════════════════════════════════════════════
# FALLBACK TEMPLATE LOKAL (Jika semua AI gagal)
# ════════════════════════════════════════════════════════════
def _build_fallback(info):
    tgl              = _tgl_id(info["tanggal"])
    tanda_terbaik    = info["tanda_terbaik"]
    peruntungan_hari = info["peruntungan_hari"]
    warna_hari       = info["warna_hari"]
    angka_hari       = info["angka_hari"]
    tipe             = info["tipe_label"]
    pesan_hari       = info["pesan_hari"]
    ramalan          = info["ramalan"]

    openings = [
        f"Halo {SAPAAN}, selamat datang kembali di channel {NAMA_CHANNEL}. Hari ini, {tgl}, kami hadir membawakan ramalan {tipe} lengkap yang dipenuhi dengan energi positif, afirmasi yang membangun, dan petunjuk praktis untuk menjalani hari dengan lebih maksimal.",
        f"Halo {SAPAAN}, salam hangat dari channel {NAMA_CHANNEL}. Di hari yang indah ini, {tgl}, mari kita buka diri terhadap energi positif yang mengalir melalui ramalan {tipe} hari ini.",
        f"Halo {SAPAAN}, terima kasih telah setia bersama channel {NAMA_CHANNEL}. Pada hari yang penuh berkah ini, {tgl}, kami akan memandu perjalananmu melalui ramalan {tipe} yang memotivasi dan menginspirasi.",
        f"Halo {SAPAAN}, selamat datang di channel {NAMA_CHANNEL}. Hari ini, {tgl}, semesta telah menyiapkan pesan-pesan indah yang tersimpan dalam ramalan {tipe} khusus untukmu.",
        f"Halo {SAPAAN}, salam penuh semangat dari tim {NAMA_CHANNEL}. Di hari yang cerah ini, {tgl}, kami siap membawakan ramalan {tipe} yang lengkap dan terperinci sehingga kamu bisa menjalani hari dengan keyakinan yang lebih besar.",
    ]

    intro_hari = [
        f"Sebelum kita masuk ke ramalan masing-masing {tipe}, izinkan kami memberikan gambaran umum tentang energi hari ini. Secara keseluruhan, hari ini berenergi {peruntungan_hari.lower()}, dengan warna keberuntungan {warna_hari} dan angka hoki {angka_hari}. {pesan_hari}",
        f"Mari kita mulai dengan mengenali energi hari ini. Getaran umumnya cenderung {peruntungan_hari.lower()}. Warna yang menuntun keberuntungan adalah {warna_hari}, sementara angka yang membuka pintu fortuna adalah {angka_hari}. {pesan_hari}",
        f"Energi hari ini terasa {peruntungan_hari.lower()} dan mengalir dengan sangat harmonis. Manfaatkan warna {warna_hari} dan angka {angka_hari} sebagai alat bantu dalam bermeditasi atau menetapkan niat hari ini. {pesan_hari}",
    ]

    tanda_terbaik_intro = [
        f"Dan {tipe} yang paling bersinar hari ini adalah {tanda_terbaik}. Jika kamu termasuk golongan ini, bersiaplah menerima aliran keberuntungan yang luar biasa sepanjang hari.",
        f"Fokus istimewa hari ini bersinar pada {tanda_terbaik}. Energi kosmik sedang menyatu dengan getaran bawaan {tanda_terbaik}, sehingga setiap usaha akan mendapat nilai tambah.",
        f"Dalam hierarki keberuntungan hari ini, {tipe} {tanda_terbaik} menduduki puncak. Ini adalah tanda bahwa semesta sedang berpihak penuh padamu, wahai {tanda_terbaik}.",
    ]

    def ramalan_tanda(nama, r):
        bintang_kata = {
            5: "lima bintang keajaiban",
            4: "empat bintang luar biasa",
            3: "tiga bintang yang menjanjikan",
        }
        bk = bintang_kata.get(r["bintang"], f"{r['bintang']} bintang")
        return (
            f"Sekarang mari kita bahas {tipe} {nama} secara mendalam. "
            f"Hari ini kamu mendapatkan rating {bk} dari semesta, dengan peruntungan yang {r['peruntungan'].lower()}. "
            f"{r['afirmasi']} "
            f"Dalam urusan cinta dan hubungan, {r['cinta'].lower()} "
            f"Ini adalah waktu yang tepat untuk mengekspresikan perasaan dan mempererat komunikasi. "
            f"Beralih ke dunia karir dan produktivitas, {r['karir'].lower()} "
            f"Pertimbangkan untuk mengambil inisiatif baru dan menawarkan ide segar kepada tim. "
            f"Untuk aspek keuangan dan rezeki, {r['keuangan'].lower()} "
            f"Bijak dalam mengelola pengeluaran dan jangan ragu mencari peluang tambahan. "
            f"Dari sisi kesehatan dan vitalitas, {r['kesehatan'].lower()} "
            f"Luangkan waktu untuk istirahat berkualitas dan jaga pola makan dengan baik. "
            f"Warna hoki yang membawa keberuntungan untukmu hari ini adalah {r['warna_hoki']}, "
            f"dan angka yang memancarkan energi terbaik adalah {r['angka_hoki']}."
        )

    penutup = [
        f"Demikianlah ramalan {tipe} lengkap hari ini, {tgl}, dari channel {NAMA_CHANNEL}. Ingatlah bahwa ramalan adalah panduan positif untuk menjalani hari, namun kekuatan terbesar tetap berada dalam dirimu sendiri. Percayakan dirimu pada proses, tetap bersyukur, dan teruslah bertumbuh. Jangan lupa berikan like jika video ini memberimu semangat, tulis komentarmu di bawah tentang zodiak atau shiomu, dan subscribe agar kamu tidak melewatkan ramalan harian kami. Sampai jumpa besok dengan semangat yang semakin membara.",
        f"Itulah seluruh ramalan {tipe} untuk hari ini, {tgl}. Kami di channel {NAMA_CHANNEL} berharap setiap kalimat yang kamu dengar menjadi benih positif yang tumbuh dalam hati dan pikiranmu. Like, komentar, dan subscribe adalah bentuk dukungan terbaik untukmu. Sampai jumpa di edisi besok, dan selalu ingat bahwa kamu adalah penulis takdirmu sendiri.",
        f"Channel {NAMA_CHANNEL} berterima kasih atas kesetiaan dan kepercayaanmu. Ramalan {tipe} hari ini, {tgl}, telah kami sampaikan dengan sepenuh hati. Jadikan setiap kata afirmasi sebagai mantra positif yang menemanimu sepanjang hari. Jangan lupa like, comment, dan subscribe untuk mendapatkan panduan ramalan setiap hari. Sampai jumpa di esok hari yang penuh berkah.",
    ]

    judul_pool = [
        f"Ramalan {tipe} Hari Ini {tgl} - {tanda_terbaik} Bersinar Terang",
        f"{tipe} {tgl} - Peruntungan {peruntungan_hari} Untuk Semua Tanda",
        f"Ramalan {tipe} Lengkap {tgl} - Penuh Energi Positif",
        f"Cek Ramalan {tipe}mu Hari Ini {tgl} - {NAMA_CHANNEL}",
        f"{tipe} Harian {tgl} - Semua Tanda - Afirmasi dan Inspirasi",
    ]

    opening    = random.choice(openings)
    intro      = random.choice(intro_hari)
    terbaik    = random.choice(tanda_terbaik_intro)
    detail     = "\n\n".join([ramalan_tanda(nama, r) for nama, r in ramalan.items()])
    penutupan  = random.choice(penutup)
    judul      = random.choice(judul_pool)

    narasi_lengkap = (
        f"{opening}\n\n"
        f"{intro}\n\n"
        f"{terbaik}\n\n"
        f"{detail}\n\n"
        f"{penutupan}"
    )
    return judul, narasi_lengkap

# ════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════
def buat_narasi(info):
    log("[narasi] Memulai pembuatan narasi...")
    prompt = _build_prompt(info)

    # 1. Coba Gemini (model terbaru 2026)
    raw = _call_gemini(prompt)
    if raw:
        judul, narasi = _parse_output(raw)
        if judul and len(narasi) > 500:
            log(f"[narasi] Narasi via Gemini OK ({len(narasi)} karakter)")
            return judul, narasi

    # 2. Fallback ke Groq (GRATIS & CEPAT)
    log("[narasi] Mencoba Groq sebagai fallback ke-2...")
    raw = _call_groq(prompt)
    if raw:
        judul, narasi = _parse_output(raw)
        if judul and len(narasi) > 500:
            log(f"[narasi] Narasi via Groq OK ({len(narasi)} karakter)")
            return judul, narasi

    # 3. Fallback ke OpenRouter
    log("[narasi] Mencoba OpenRouter sebagai fallback ke-3...")
    raw = _call_openrouter(prompt)
    if raw:
        judul, narasi = _parse_output(raw)
        if judul and len(narasi) > 500:
            log(f"[narasi] Narasi via OpenRouter OK ({len(narasi)} karakter)")
            return judul, narasi

    # 4. Fallback lokal (template, selalu berhasil)
    log("[narasi] Menggunakan fallback template lokal...")
    judul, narasi = _build_fallback(info)
    log(f"[narasi] Fallback lokal OK ({len(narasi)} karakter)")
    return judul, narasi
