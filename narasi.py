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

_BULAN_ID = {
    "January":"Januari","February":"Februari","March":"Maret",
    "April":"April","May":"Mei","June":"Juni",
    "July":"Juli","August":"Agustus","September":"September",
    "October":"Oktober","November":"November","December":"Desember",
}

def _tgl_id(x):
    x = str(x).strip()
    m = re.match(r"(\\d{4})-(\\d{2})-(\\d{2})", x)
    if m:
        y, mo, d = m.groups()
        try:
            from datetime import date as _d
            dt = _d(int(y), int(mo), int(d))
            b = dt.strftime("%B")
            hari = dt.strftime("%A")
            hari_id = {
                "Monday":"Senin","Tuesday":"Selasa","Wednesday":"Rabu",
                "Thursday":"Kamis","Friday":"Jumat","Saturday":"Sabtu","Sunday":"Minggu",
            }.get(hari, hari)
            return f"{hari_id}, {int(d)} {_BULAN_ID.get(b, b)} {y}"
        except:
            pass
    return x

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-1.0-pro",
]
GEMINI_BASE = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/{model}:generateContent"
)
OPENROUTER_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "deepseek/deepseek-r1:free",
    "mistralai/mistral-7b-instruct:free",
]

# ════════════════════════════════════════════════════════════
# PROMPT BUILDER
# ════════════════════════════════════════════════════════════
def _build_prompt(info):
    tgl        = _tgl_id(info["tanggal"])
    waktu      = info["waktu"]
    tipe       = info["tipe_label"]           # "Shio" atau "Zodiak"
    tanda_list = info["tanda_list"]
    tanda_terbaik = info["tanda_terbaik"]
    peruntungan_hari = info["peruntungan_hari"]
    warna_hari = info["warna_hari"]
    angka_hari = info["angka_hari"]

    # Ringkasan ramalan per tanda untuk prompt
    ringkasan = ""
    for tanda, r in info["ramalan"].items():
        ringkasan += (
            f"- {tanda}: bintang {r['bintang']}/5, peruntungan {r['peruntungan']}, "
            f"warna hoki {r['warna_hoki']}, angka hoki {r['angka_hoki']}\\n"
            f"  Afirmasi: {r['afirmasi']}\\n"
            f"  Cinta: {r['cinta']}\\n"
            f"  Karir: {r['karir']}\\n"
            f"  Keuangan: {r['keuangan']}\\n"
            f"  Kesehatan: {r['kesehatan']}\\n"
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
        f'Kamu adalah narrator video YouTube channel "{NAMA_CHANNEL}".\\n\\n'
        f"{gaya_instruksi}\\n\\n"
        f"DATA RAMALAN {tipe.upper()} HARI INI:\\n"
        f"- Tanggal    : {tgl}\\n"
        f"- Waktu      : {waktu}\\n"
        f"- {tipe} Terbaik Hari Ini: {tanda_terbaik}\\n"
        f"- Peruntungan Hari : {peruntungan_hari}\\n"
        f"- Warna Hoki Hari  : {warna_hari}\\n"
        f"- Angka Hoki Hari  : {angka_hari}\\n\\n"
        f"DATA LENGKAP RAMALAN TIAP {tipe.upper()}:\\n"
        f"{ringkasan}\\n"
        f"TUGAS:\\n"
        f"1. Buat JUDUL video menarik (maksimal 80 karakter)\\n"
        f"2. Buat NARASI video berdurasi 6‑8 menit (900‑1100 kata)\\n\\n"
        f"FORMAT OUTPUT (WAJIB IKUTI PERSIS):\\n"
        f"JUDUL: [judul video di sini]\\n"
        f"NARASI:\\n"
        f"[narasi lengkap di sini]\\n\\n"
        f"ATURAN NARASI:\\n"
        f"\\- Kalimat pertama WAJIB: \"Halo {SAPAAN},\\\"\\n"
        f"\\- Sebutkan tanggal dan tema hari ini\\n"
        f"\\- Bacakan ramalan untuk SEMUA {len(tanda_list)} {tipe}: afirmasi, cinta, karir, keuangan, kesehatan\\n"
        f"\\- Setiap {tipe} mendapat porsi yang cukup (minimal 4 kalimat)\\n"
        f"\\- Sampaikan pesan positif dan afirmatif untuk setiap {tipe}\\n"
        f"\\- Sebutkan warna hoki dan angka hoki masing-masing {tipe}\\n"
        f"\\- Tutup dengan pesan inspiratif dan ajakan subscribe & like\\n"
        f"\\- JANGAN gunakan emoji, simbol bintang (*), atau markdown\\n"
        f"\\- JANGAN gunakan tanda bintang atau tanda pagar\\n"
        f"\\- Natural saat dibaca/didengar untuk text-to-speech\\n"
        f"\\- WAJIB minimal 900 kata, maksimal 1100 kata\\n"
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
                            "maxOutputTokens": 4000,   # ↑ untuk narasi lebih panjang
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
                resp.raise_for_status()
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                log(f" -> Gemini [{model}] OK!")
                return text
            except requests.exceptions.HTTPError as e:
                log(f" -> HTTP error: {e}")
                if attempt < 3: time.sleep(attempt * 15)
            except Exception as e:
                log(f" -> Error: {e}")
                if attempt < 3: time.sleep(attempt * 10)
        log(f" -> [{model}] gagal, coba model lain...")
        time.sleep(5)
    log(" -> Semua model Gemini gagal")
    return None

# ════════════════════════════════════════════════════════════
# CALL OPENROUTER (Fallback ke-2)
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
                        "max_tokens": 4000,   # ↑ untuk narasi lebih panjang
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
                if attempt < 2: time.sleep(attempt * 10)
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
            narasi = "\\n".join(lines[i+1:]).strip()
            break
    if not judul and lines:
        judul = lines[0].strip()
    if not narasi:
        narasi = raw.strip()
    judul = re.sub(r'[*_`#\\[\\]|]', "", judul).strip()
    baris_bersih = []
    for bl in narasi.splitlines():
        bl = bl.strip()
        if not bl:
            baris_bersih.append(""); continue
        bl_l = bl.lower()
        if any(bl_l.startswith(skip) for skip in ["narasi:","judul:","**","##","--","catatan:","note:"]):
            continue
        baris_bersih.append(bl)
    narasi_bersih = re.sub(r'[*_`#\\[\\]|]', "", "\\n".join(baris_bersih)).strip()
    return judul, narasi_bersih

# ════════════════════════════════════════════════════════════
# FALLBACK TEMPLATES (jika Gemini & OpenRouter gagal) – LEBIH PANJANG
# ════════════════════════════════════════════════════════════
def _build_fallback(info):
    tgl          = _tgl_id(info["tanggal"])
    tanda_terbaik = info["tanda_terbaik"]
    peruntungan_hari = info["peruntungan_hari"]
    warna_hari   = info["warna_hari"]
    angka_hari   = info["angka_hari"]
    tipe         = info["tipe_label"]
    pesan_hari   = info["pesan_hari"]
    ramalan      = info["ramalan"]

    # Pembukaan beragam (lebih deskriptif)
    openings = [
        f"Halo {SAPAAN}, selamat pagi/siang/sore/malam tergantung di mana kamu menonton video ini. Selamat datang kembali di channel {NAMA_CHANNEL}. Hari ini, {tgl}, kami hadir menyaji ramalan {tipe} lengkap yang dipenuhi dengan energi positif, afirmasi yang membangun, dan petunjuk praktis untuk menjalani hari dengan lebih maksimal.",
        f"Halo {SAPAAN}, hangat salam dari tim {NAMA_CHANNEL}. Di hari yang indah ini, {tgl}, kami siap membawakan ramalan {tipe} yang terperinci sehingga kamu bisa merencanakan setiap aspek hidup—cinta, karir, keuangan, dan kesehatan—denganKeyakinan yang lebih besar.",
        f"Halo {SAPAAN}, terima kasih telah menyediakan beberapa menitmu untuk bersama channel {NAMA_CHANNEL}. Pada kesempatan hari ini, {tgl}, kami akan membuka rakasial ramalan {tipe} yang telah disusun dengan hati-hati agar setiap kata menjadi cahaya yang menerjang jalanmu.",
        f"Halo {SAPAAN}, salam sejahtera untukmu. Hari ini, {tgl}, universo mengirimkan pesan-pesan khusus melalui gerakan bintang dan zodiak. Yuk, kita simak bersama ramalan {tipe} lengkap yang akan menemani langkahmu hari ini.",
        f"Halo {SAPAAN}, selamat datang di ruang ramalan {NAMA_CHANNEL}. Hari ini, {tgl}, bintang-bintang menyalakan cahaya harapan untuk semua {tipe}. Mari kita selami arti di balik gerakan kosmik tersebut.",
    ]

    # Pembaruan energi hari
    intro_hari = [
        f"Sebelum kita masuk ke ramalan masing-masing {tipe}, izinkan kami memberikan gambaran umum tentang energi hari ini. Secara keseluruhan, hari ini berenergi {peruntungan_hari.lower()}, dengan warna keberuntungan yang memancarkan dari {warna_hari} dan angka hoki yang bergetar pada {angka_hari}. {pesan_hari}",
        f"Mari kita mulai dengan mengenali kosmologi hari ini: getaran umumnya cenderung {peruntungan_hari.lower()}. Warna yang menuntun keberuntungan adalah {warna_hari}, sementara angka yang berfungsi sebagai pintu fortuna adalah {angka_hari}. Ingatlah bahwa {pesan_hari}",
        f"Energi hari ini terasa {peruntungan_hari.lower()} dan mengalir dengan cara yang sangat harmonis untuk mereka yang bersedia menerima. Manfaatkan warna {warna_hari} dan angka {angka_hari} sebagai alat bantu dalam bermeditasi atau menetapkan niat. {pesan_hari}",
        f"Hari ini alam semesta menunjukkan bahwa {peruntungan_hari.lower()} adalah dominasi utama. Oleh karena itu, warna {warna_hari} dan angka {angka_hari} menjadi pahala kecil yang dapat kamu gunakan untuk meningkatkan fokus dan intenzitas. {pesan_hari}",
        f"Mari kita catat: frekuensi hari ini bergetar pada level {peruntungan_hari.lower()}, yang menunjukkan kesempatan baik untuk tumbuh. Manfaatkan warna pelindung {warna_hari} dan angka pengikat {angka_hari} dalam segala usahamu. {pesan_hari}",
    ]

    # Penyorotan tanda terbaik
    tanda_terbaik_intro = [
        f"Dan kini, saat yang ditunggu-tunggu: {tipe} yang paling bersinar hari ini adalah {tanda_terbaik}. Bila kamu termasuk golongan ini, persiapkan diri untuk menerima aliran luck yang luar biasa.",
        f"Fokus istimewa hari ini bersinar pad {tanda_terbaik}. Ini adalah tanda bahwa energi kosmik sedang menyatu dengan getaran bawaanmu, {tanda_terbaik}, sehingga setiap usaha kamu akan ditambah nilai.",
        f"Dalam hierarki keberuntungan hari ini, {tipe} {tanda_terbaik} menduduki puncak. Bila kamu berziarah ke tanda ini, persiapkan diri untuk tas ketuk rezeki yang akan mengalir deras.",
        f"Kita perhatikan bahwa zodiak/shio {tanda_terbaik} memperoleh pasokan energi tambahan dari gerakan planet hari ini. Ini momen yang sangat tepa untuk memulai proyek baru atau membuat keputusan penting.",
        f"Sebagai tanda terbaik, {tanda_terbaik} menerima istimewa dari langit. Gunakan momentum ini untuk mengoptimalkan aspek-aspek kehidupanmu—mulai dari hubungan hingga keuangan.",
    ]

    # Fungsi untuk membuat ramalan per zodiak/shio dengan detail lebih
    def ramalan_tanda(nama, r):
        bintang   = r["bintang"]
        bintang_kata = {
            5: "lima bintang keajaiban",
            4: "empat bintang mega luck",
            3: "tiga bintang solid",
        }
        bk = bintang_kata.get(bintang, f"{bintang} bintang")
        return (
            f"Mari kita bahas {tipe} {nama} secara mendalam. Pada hari ini, bintang-bintang menyiratkan bahwa kamu mendapat rating {bk} dari segi keseluruhan, dengan kategori peruntungan yang {r['peruntungan'].lower()}. "
            f"{r['afirmasi']} "
            f"Dalam konteks cinta dan hubungan, {r['cinta']}. Ini adalah waktu yang bagus untuk mengekspresikan perasaan, memperbaiki komunikasi, atau bahkan menggelar momen romantis yang tak terduga. "
            f"Beralih ke dunia karir dan produktivitas: {r['karir']}. Pertimbangkan untuk mengambil inisiatif, menawarkan ide baru, atau mengajukan proyek yang lama tertunda—energi saat ini mendukung usaha berani. "
            f"Selanjutnya, aspek keuangan: {r['keuangan']}. Ini adalah saran untuk menjadi lebih bijak dalam pengeluaran, mencari sumber pendapatan tambahan, atau menanamkan bibit investasi yang sesuai dengan profil risikommu. "
            f"Terakhir, mari kita perhatikan kesejahteraan fisik dan mental: {r['kesehatan']}. Luangkan waktu untuk istirahat yang cukup, gerakan ringan, dan praktik mindfulness agar energi positif ini tersalur secara merata. "
            f"Warna yang berfungsi sebagai penguat keberuntunganmu hari ini adalah {r['warna_hoki']}, sedangkan angka yang berfungsi sebagai kode activa adalah {r['angka_hoki']}. Gunakan keduanya—misalnya mengenakan pakaian berwarna tersebut atau mencatet angka di buku catatan harian—sebagai pengingat niat positif."
        )

    # Penutup yang lebih inspiratif dan mengajak interaksi
    penutup = [
        f"Ini selesai rangkuman ramalan {tipe} lengkap untuk hari ini, {tgl}, dari channel {NAMA_CHANNEL}. Ingatlah bahwa ramalan adalah petunjuk, bukan nasib yang tak dapat diubah. Kekuatan sejati tetap berada di tanganmu—keberanian untuk bertindak, kesadaran untuk merespons, dan rasa syukur untuk menghargai setiap langkah. Jika video ini memberikan inspirasi atau sekadar menyenangkan hatimu, tolong tekan tombol like, tulis komentar di bawah tentang zodiak/shiomu hari ini, dan jangan lupa subscribe agar kamu tidak ketinggalan update besok. Terima kasih telah bersamamu, semoga harimu penuh berkah!",
        f"Itulah akhir dari sesi ramalan {tipe} hari ini. Kami di {NAMA_CHANNEL} berharap setiap kalimat yang kamu dengar menjadi benih positif yang tumbuh dalam hati dan pikiranmu. Sebuah like adalah bentuk apresiasi terkecil yang sangat berarti untuk kami, komentar kamu adalah bahan bahan evaluasi dan motivasi, dan subscribe adalah janji kamu untuk terus bersama kami dalam menjelajahi kosmik setiap hari. Sampai jumpa di edisi besok, dan selalu ingat: kamu adalah penulis takdirmu sendiri.",
        f"Mari kita akhiri dengan kutipan singkat: 'Bintang tidak menentukan jalannya kita, namun mereka menerangi jalan sehingga kita bisa memilih dengan bijak.' Terima kasih telah menonton video ramalan {tipe} dari {NAMA_CHANNEL}. Jika kamu merasa video ini membantu, dukung kami dengan tombol like dan sebarkan kepada teman-temanmu yang juga mencari panduan harian. Don't forget to subscribe and turn on notifications so you never miss a cosmic update. Salam hangat dan sampai ketemu lagi!",
        f"Kami sangat menghargai waktu yang kamu berikan untuk menyaksikan video ini. Segala informasi yang disampaikan adalah hasil dari pemikiran, analisis simbolika, dan niat baik. Yuk, jadikan video ini sebagai awal ritual harianmu: tonton, refleksikan, lalu bertindak sesuai dengan intuisi yang dituntun oleh ramalan. Jika kamu menyukai konten kami, show your support dengan menombol like, menyumbang komentar, dan menekan tombol subscribe. Mari kita terus tumbuh bersama dalam menyambut setiap hari dengan optimisme dan semangat. Wassalam!",
        f"Penutup hari ini kita akhiri dengan doa singkat: semoga setiap affirmasi yang kamu dengar menjadi benar dalam hidupmu, semoga warna dan angka hoki menjadi penguat keberuntungan, dan semoga langkahmu selalu diarahkan ke jalan yang paling sesuai dengan tujuan jiwamu. Jika kamu merasa video ini bermanfaat, tolong dukung channel kami dengan menekan like, menulikan komentar apa adanya, dan mengklik subscribe. Bersama-sama kita akan terus menjelajahi misteri kosmos setiap hari. Sampai jumpa!",
    ]

    # Variasi judul yang lebih menarik
    judul_pool = [
        f"Ramalan {tipe} Hari Ini {tgl} | {tanda_terbaik} Mengapis Luck",
        f"{tipe} {tgl} | Energi {peruntungan_hari} untuk Semua Zodiak/Shio",
        f"Ramalan {tipe} Lengkap {tgl} | Panduan Hari yang Menyeluruh",
        f"Buka Ramalan {tipe}mu Hari Ini {tgl} | {NAMA_CHANNEL}",
        f"{tipe} Harian {tgl} | Semua {tipe} | Afirmasi Positif & Tips Praktis",
        f"Ramalan {tipe} Istimewa {tgl} | Fokus pada {tanda_terbaik} + Tips Warna & Angka",
    ]

    # Susun narasi akhir dengan semua komponen
    opening   = random.choice(openings)
    intro     = random.choice(intro_hari)
    terbaik   = random.choice(tanda_terbaik_intro)
    detail    = "\n\n".join([ramalan_tanda(nama, r) for nama, r in ramalan.items()])
    penutupan = random.choice(penutup)
    judul     = random.choice(judul_pool)

    # Gabungkan menjadi satu blok narasi (minimal 900 kata)
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

    # Coba Gemini dulu
    raw = _call_gemini(prompt)
    if raw:
        judul, narasi = _parse_output(raw)
        if judul and len(narasi) > 500:   # minimal panjang yang diterima
            log(f"[narasi] Narasi via Gemini OK ({len(narasi)} karakter)")
            return judul, narasi

    # Fallback ke OpenRouter
    log("[narasi] Mencoba OpenRouter sebagai fallback...")
    raw = _call_openrouter(prompt)
    if raw:
        judul, narasi = _parse_output(raw)
        if judul and len(narasi) > 500:
            log(f"[narasi] Narasi via OpenRouter OK ({len(narasi)} karakter)")
            return judul, narasi

    # Fallback lokal (template panjang)
    log("[narasi] Menggunakan fallback template lokal...")
    judul, narasi = _build_fallback(info)
    log(f"[narasi] Fallback OK ({len(narasi)} karakter)")
    return judul, narasi
