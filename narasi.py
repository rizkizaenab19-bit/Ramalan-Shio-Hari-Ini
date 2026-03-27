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
# MODEL LIST
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
# PROMPT BUILDER (CLICKBAIT VERSION)
# ════════════════════════════════════════════════════════════
def _build_prompt(info):
    tgl              = _tgl_id(info["tanggal"])
    waktu            = info["waktu"]
    tipe             = info["tipe_label"]
    tanda_list       = info["tanda_list"]
    tanda_terbaik    = info["tanda_terbaik"]
    peruntungan_hari = info["peruntungan_hari"]
    warna_hari       = info["warna_hari"]
    angka_hari       = info["angka_hari"]

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

    return (
        f'Kamu adalah narrator video YouTube channel "{NAMA_CHANNEL}" yang ahli membuat konten VIRAL dan CLICKBAIT.\n\n'
        f"INSTRUKSI UTAMA — WAJIB DIIKUTI:\n"
        f"1. Buat JUDUL yang SANGAT CLICKBAIT, mengandung unsur kejutan, rasa ingin tahu, atau ancaman/peluang besar.\n"
        f"   Contoh pola judul bagus:\n"
        f"   - 'HATI-HATI! {tipe} Ini Akan Mengalami Kejutan BESAR Hari Ini!'\n"
        f"   - 'LUAR BIASA! Rezeki Nomplok Datang Tiba-tiba untuk {tipe} Ini!'\n"
        f"   - 'WASPADA! 3 {tipe} Ini Harus Ekstra Hati-hati {tgl}'\n"
        f"   - 'BOCORAN SEMESTA: {tipe} {tanda_terbaik} Dipilih Alam Semesta Hari Ini!'\n"
        f"   - 'SHOCK! Peruntungan {tipe} Ini Berubah Drastis Mulai Hari Ini!'\n\n"
        f"2. Narasi harus DRAMATIS, EMOSIONAL, dan MENGHIPNOTIS seperti konten YouTube viral.\n"
        f"   - Gunakan kalimat pendek dan menghentak di awal\n"
        f"   - Tambahkan JEDA DRAMATIS: 'Dan yang paling mengejutkan...', 'Tapi tunggu dulu...'\n"
        f"   - Buat penonton penasaran dengan cliffhanger\n"
        f"   - Sisipkan ajakan interaksi: 'Tulis di kolom komentar...', 'Tonton sampai habis karena...'\n"
        f"   - Gunakan kata-kata kuat: LUAR BIASA, MENGEJUTKAN, DAHSYAT, WASPADA, BOCORAN, RAHASIA\n\n"
        f"DATA RAMALAN {tipe.upper()} HARI INI:\n"
        f"- Tanggal           : {tgl}\n"
        f"- Waktu             : {waktu}\n"
        f"- {tipe} Terbaik    : {tanda_terbaik}\n"
        f"- Peruntungan Hari  : {peruntungan_hari}\n"
        f"- Warna Hoki Hari   : {warna_hari}\n"
        f"- Angka Hoki Hari   : {angka_hari}\n\n"
        f"DATA LENGKAP TIAP {tipe.upper()}:\n"
        f"{ringkasan}\n"
        f"FORMAT OUTPUT (WAJIB IKUTI PERSIS):\n"
        f"JUDUL: [judul clickbait maksimal 90 karakter]\n"
        f"NARASI:\n"
        f"[narasi lengkap]\n\n"
        f"ATURAN NARASI:\n"
        f'- Kalimat PERTAMA wajib menghentak, contoh: "STOP! Sebelum kamu memulai harimu hari ini, dengarkan ini baik-baik..."\n'
        f"- Langsung sebut tanggal dan tema dramatis hari ini\n"
        f"- Setiap {tipe} dibahas dengan nada dramatis dan emosional\n"
        f"- Tambahkan kata KEJUTAN atau PERINGATAN untuk {tipe} bintangnya rendah\n"
        f"- Tambahkan kata SELAMAT atau LUAR BIASA untuk {tipe} bintangnya tinggi\n"
        f"- Setiap {tipe} wajib ada: afirmasi, cinta, karir, keuangan, kesehatan, warna hoki, angka hoki\n"
        f"- Di tengah video sisipkan: 'Tonton terus, karena di bagian akhir ada pesan RAHASIA dari semesta...'\n"
        f"- Tutup dramatis + paksa subscribe: 'Jika kamu tidak subscribe sekarang, kamu akan melewatkan ramalan PENTING besok!'\n"
        f"- JANGAN pakai emoji, tanda bintang (*), atau markdown\n"
        f"- Natural saat dibaca untuk text-to-speech\n"
        f"- WAJIB minimal 500 kata, maksimal 650 kata\n"
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
                            "temperature": 0.9,
                            "maxOutputTokens": 4000,
                            "topP": 0.95,
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
                    log(f" -> 404 model tidak ditemukan, skip")
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
# CALL GROQ
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
                        "temperature": 0.9,
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
# CALL OPENROUTER
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
                        "temperature": 0.9,
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
# FALLBACK TEMPLATE LOKAL (CLICKBAIT VERSION)
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
        f"STOP! Sebelum kamu memulai harimu hari ini, {tgl}, dengarkan pesan penting ini baik-baik. Semesta sedang mengirimkan sinyal yang tidak boleh kamu abaikan. Di channel {NAMA_CHANNEL}, hari ini kami membawa bocoran ramalan {tipe} yang akan mengubah cara pandangmu tentang hari ini!",
        f"PERINGATAN dari alam semesta! Hari ini, {tgl}, ada pergerakan energi besar yang akan mempengaruhi seluruh {tipe} tanpa terkecuali. Sebelum kamu melangkah keluar rumah, simak dulu ramalan lengkap dari {NAMA_CHANNEL} ini. Jangan sampai kamu menyesal karena melewatkannya!",
        f"Hai, kamu yang sedang menonton ini! Tahukah kamu bahwa hari ini, {tgl}, semesta sedang menyiapkan sesuatu yang LUAR BIASA untuk beberapa {tipe}? Dan mungkin kamu adalah salah satunya! Tonton video ini sampai habis karena di bagian akhir ada pesan rahasia yang sayang untuk dilewatkan!",
        f"BOCORAN SEMESTA hari ini, {tgl}! Channel {NAMA_CHANNEL} hadir membawakan ramalan {tipe} terlengkap yang akan membuatmu tercengang. Ada {tipe} yang akan menerima rezeki nomplok hari ini, dan ada juga yang harus ekstra waspada. Kamu masuk yang mana? Simak sampai selesai!",
        f"Kamu harus dengar ini sekarang! Hari ini, {tgl}, getaran kosmik sedang bergerak dengan cara yang sangat tidak biasa. {NAMA_CHANNEL} telah menganalisis pergerakan bintang dan menghasilkan ramalan {tipe} yang sangat akurat untuk harimu. Bersiaplah untuk terkejut!",
    ]

    intro_hari = [
        f"Sebelum kita masuk ke ramalan masing-masing, ada yang perlu kamu tahu tentang energi besar hari ini. Hari ini energinya {peruntungan_hari.lower()} dan ini bukan hal yang biasa! Warna {warna_hari} adalah kunci keberuntunganmu hari ini, dan angka {angka_hari} bisa menjadi angka paling ajaib yang kamu temui. {pesan_hari} Simpan informasi ini baik-baik!",
        f"Tonton terus, karena di bagian akhir ada pesan RAHASIA dari semesta yang hanya diperuntukkan bagi yang setia menonton sampai selesai! Tapi sebelum itu, kenali dulu energi hari ini yang luar biasa dahsyat. Getarannya {peruntungan_hari.lower()}, warna hoki {warna_hari}, dan angka keberuntungan {angka_hari}. {pesan_hari}",
        f"Dan inilah yang membuat hari ini begitu istimewa dan berbeda dari hari-hari biasanya! Energi kosmik hari ini digambarkan sebagai {peruntungan_hari.lower()}, sebuah getaran yang jarang terjadi. Manfaatkan warna {warna_hari} dan angka sakral {angka_hari} sebagai penghubungmu dengan energi semesta. {pesan_hari}",
    ]

    tanda_terbaik_intro = [
        f"Dan sekarang, saat yang paling ditunggu-tunggu! Siapakah {tipe} yang dipilih semesta sebagai yang paling beruntung hari ini? Jawabannya adalah {tanda_terbaik}! Jika kamu lahir di bawah naungan {tanda_terbaik}, hari ini adalah harimu! Energi terbaik sedang mengalir deras ke arahmu!",
        f"PENGUMUMAN BESAR! Dari semua {tipe} yang ada, semesta hari ini memilih {tanda_terbaik} sebagai bintang utama! Keberuntungan, rezeki, dan peluang emas semuanya tertuju pada {tanda_terbaik} hari ini. Apakah kamu salah satunya? Jika iya, bersiaplah untuk hari yang luar biasa!",
        f"Sebelum kita bahas satu per satu, kami harus mengumumkan sesuatu yang mengejutkan! {tipe} {tanda_terbaik} hari ini berada di puncak keberuntungan! Semesta sedang berpihak penuh padamu, wahai {tanda_terbaik}. Tapi tunggu dulu, bagaimana dengan {tipe}-{tipe} lainnya? Simak terus!",
    ]

    def ramalan_tanda(nama, r):
        bintang_kata = {5: "LUAR BIASA lima bintang", 4: "sangat baik empat bintang", 3: "cukup menjanjikan tiga bintang"}
        bk = bintang_kata.get(r["bintang"], f"{r['bintang']} bintang")
        level = "SELAMAT" if r["bintang"] >= 4 else "PERHATIAN" if r["bintang"] == 3 else "WASPADA"
        return (
            f"{level}! Sekarang mari kita bahas {tipe} {nama}. "
            f"Hari ini kamu mendapatkan rating {bk} dari semesta, dengan peruntungan yang {r['peruntungan'].lower()}. "
            f"{r['afirmasi']} "
            f"Dalam urusan cinta dan hubungan, simaklah ini baik-baik: {r['cinta'].lower()} "
            f"Jangan abaikan sinyal yang dikirimkan pasanganmu hari ini. "
            f"Beralih ke dunia karir, ada kabar yang menarik! {r['karir'].lower()} "
            f"Ini adalah momen yang tepat untuk mengambil langkah berani. "
            f"Untuk keuangan, dan ini yang paling mengejutkan: {r['keuangan'].lower()} "
            f"Bijak dalam mengambil keputusan finansial hari ini. "
            f"Dari sisi kesehatan, semesta berpesan: {r['kesehatan'].lower()} "
            f"Jaga energimu agar tetap prima sepanjang hari. "
            f"Dan jangan lupakan kunci hoki hari ini: warna {r['warna_hoki']} dan angka ajaib {r['angka_hoki']}."
        )

    penutup = [
        f"Itulah ramalan lengkap {tipe} hari ini, {tgl}, dari {NAMA_CHANNEL}! Luar biasa bukan? Dan inilah pesan RAHASIA dari semesta yang kami janjikan: semesta selalu berpihak pada mereka yang percaya dan terus berusaha. JANGAN lupa klik tombol SUBSCRIBE dan nyalakan lonceng notifikasi sekarang juga! Karena jika kamu tidak subscribe hari ini, kamu berisiko melewatkan ramalan penting yang mungkin akan mengubah hidupmu besok. Sampai jumpa besok dengan ramalan yang lebih mengejutkan!",
        f"Dan itulah pesan rahasia dari semesta yang kami janjikan di awal tadi! Terima kasih sudah setia menonton {NAMA_CHANNEL} sampai selesai. Kamu adalah yang terpilih! Buktikan dengan klik SUBSCRIBE, nyalakan notifikasi, dan bagikan video ini ke orang-orang terkasihmu agar mereka juga mendapat berkah hari ini. Sampai jumpa besok!",
        f"WOW! Luar biasa sekali pergerakan energi hari ini! Dan hanya penonton setia {NAMA_CHANNEL} yang mendapatkan bocoran istimewa ini. Jika video ini bermanfaat, berikan LIKE sebagai tanda syukur, tulis {tipe}mu di kolom komentar, dan SUBSCRIBE agar kamu tidak pernah lagi melewatkan satu pun ramalan harian kami. Sampai jumpa besok, dan ingat, keberuntunganmu ada di tanganmu sendiri!",
    ]

    judul_pool = [
        f"HATI-HATI! {tipe} Ini Akan Alami Kejutan BESAR Hari Ini {tgl}",
        f"BOCORAN SEMESTA! {tanda_terbaik} Dipilih Sebagai {tipe} Paling Beruntung {tgl}",
        f"LUAR BIASA! Rezeki Nomplok Menanti {tipe} Ini Hari Ini {tgl}",
        f"WASPADA! Ramalan {tipe} Lengkap {tgl} Ada Yang Harus Ekstra Hati-hati!",
        f"SHOCK! Peruntungan {tipe} Berubah Drastis {tgl} Kamu Masuk Yang Mana?",
        f"RAHASIA SEMESTA {tgl}: {tipe} {tanda_terbaik} Menerima Energi Terkuat Hari Ini!",
        f"PERINGATAN KERAS! Beberapa {tipe} Harus Waspada Penuh Hari Ini {tgl}",
        f"KEJUTAN! Ada {tipe} Yang Rezekinya Mengalir Deras Hari Ini {tgl} Siapa?",
    ]

    opening   = random.choice(openings)
    intro     = random.choice(intro_hari)
    terbaik   = random.choice(tanda_terbaik_intro)
    detail    = "\n\n".join([ramalan_tanda(nama, r) for nama, r in ramalan.items()])
    penutupan = random.choice(penutup)
    judul     = random.choice(judul_pool)

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

    # 1. Coba Gemini
    raw = _call_gemini(prompt)
    if raw:
        judul, narasi = _parse_output(raw)
        if judul and len(narasi) > 500:
            log(f"[narasi] Narasi via Gemini OK ({len(narasi)} karakter)")
            return judul, narasi

    # 2. Fallback Groq
    log("[narasi] Mencoba Groq sebagai fallback ke-2...")
    raw = _call_groq(prompt)
    if raw:
        judul, narasi = _parse_output(raw)
        if judul and len(narasi) > 500:
            log(f"[narasi] Narasi via Groq OK ({len(narasi)} karakter)")
            return judul, narasi

    # 3. Fallback OpenRouter
    log("[narasi] Mencoba OpenRouter sebagai fallback ke-3...")
    raw = _call_openrouter(prompt)
    if raw:
        judul, narasi = _parse_output(raw)
        if judul and len(narasi) > 500:
            log(f"[narasi] Narasi via OpenRouter OK ({len(narasi)} karakter)")
            return judul, narasi

    # 4. Fallback lokal
    log("[narasi] Menggunakan fallback template lokal...")
    judul, narasi = _build_fallback(info)
    log(f"[narasi] Fallback lokal OK ({len(narasi)} karakter)")
    return judul, narasi
