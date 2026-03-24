# scrape.py  –  Generator data ramalan zodiak/shio (random per hari, tanpa scraping)
import random
from datetime import datetime, date
from config import TIPE_KONTEN, log

SHIO_LIST = [
    "Tikus", "Kerbau", "Macan", "Kelinci", "Naga", "Ular",
    "Kuda", "Kambing", "Monyet", "Ayam", "Anjing", "Babi",
]

ZODIAK_LIST = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagitarius", "Capricorn", "Aquarius", "Pisces",
]

_AFIRMASI = [
    "Hari ini semesta mendukung setiap langkah positif yang kamu ambil.",
    "Energi baik mengalir deras menuju dirimu, sambut dengan penuh syukur.",
    "Keberuntungan tersembunyi di balik setiap tindakan kecil yang kamu lakukan hari ini.",
    "Hari ini adalah kesempatan emas untuk mewujudkan harapan yang sudah lama tersimpan.",
    "Bintang-bintang bersinar untukmu hari ini, percayakan dirimu pada aliran energi positif.",
    "Setiap pilihan yang kamu buat hari ini membawa kamu lebih dekat pada tujuan hidupmu.",
    "Alam semesta berbisik bahwa hari ini adalah hari penuh kejutan menyenangkan bagimu.",
    "Potensimu sedang berada di puncak terbaik, manfaatkan energi ini sebaik mungkin.",
    "Hari ini pintu-pintu rezeki terbuka lebar, beranikan diri untuk melangkah masuk.",
    "Cahaya keberuntungan menerangi jalanmu, tetap fokus dan penuh semangat.",
    "Hari ini adalah momen yang sempurna untuk memulai hal baru yang sudah lama kamu impikan.",
    "Kepercayaan dirimu adalah kunci keberuntungan terbesar yang kamu miliki hari ini.",
    "Semesta sedang bekerja keras untukmu di balik layar, tetap percaya dan bersyukur.",
    "Hari ini rezekimu mengalir dari arah yang tidak terduga, buka hati dan pikiranmu.",
    "Energi cinta dan kasih sayang menyelimuti perjalananmu hari ini.",
]

_CINTA = [
    "Hubungan menjadi lebih hangat dan penuh perhatian hari ini.",
    "Momen istimewa menanti kamu bersama orang tersayang.",
    "Komunikasi yang tulus membuka pintu keharmonisan baru.",
    "Energi cinta mengalir indah, sampaikan perasaanmu dengan berani.",
    "Ketulusan hatimu hari ini menjadi magnet yang menarik cinta sejati.",
    "Pertemuan bermakna mungkin terjadi, tetap terbuka terhadap koneksi baru.",
    "Kasih sayang tumbuh subur saat kamu bersedia untuk hadir sepenuhnya.",
    "Hari ini adalah waktu yang tepat untuk mempererat ikatan emosional.",
]

_KARIR = [
    "Ide-ide brillian mengalir lancar, ekspresikan kreativitasmu tanpa ragu.",
    "Peluang baru muncul dari arah tak terduga, tetap waspada dan sigap.",
    "Kerja keras hari ini akan membuahkan hasil yang memuaskan dalam waktu dekat.",
    "Kolaborasi dengan rekan membuka jalan menuju pencapaian luar biasa.",
    "Kemampuanmu diakui dan diapresiasi oleh orang-orang di sekitarmu.",
    "Langkah berani dalam karir hari ini akan membawa dampak positif jangka panjang.",
    "Produktivitasmu berada di level tertinggi, manfaatkan momentum ini.",
    "Networking hari ini bisa membuka pintu kesempatan yang belum pernah kamu bayangkan.",
]

_KEUANGAN = [
    "Rezeki mengalir dari berbagai sumber yang menggembirakan hari ini.",
    "Kebijaksanaan finansialmu hari ini menjadi fondasi kemakmuran masa depan.",
    "Pengeluaran yang tepat sasaran membawa manfaat berlipat ganda.",
    "Investasi terbaik hari ini adalah pada dirimu sendiri dan pengetahuanmu.",
    "Peluang finansial yang menjanjikan mendekat, analisa dengan kepala dingin.",
    "Keseimbangan antara menabung dan menikmati hidup membawa kebahagiaan nyata.",
    "Hari ini adalah momen yang tepat untuk merencanakan masa depan finansialmu.",
    "Kemurahan hati yang kamu tunjukkan hari ini kembali berlipat ganda untukmu.",
]

_KESEHATAN = [
    "Vitalitas dan semangat hidupmu berada di puncak yang optimal hari ini.",
    "Tubuh dan pikiran selaras sempurna, manfaatkan energi positif ini.",
    "Istirahat yang berkualitas malam ini akan memulihkan tenagamu dengan luar biasa.",
    "Perhatian pada pola makan hari ini memberikan dampak positif yang nyata.",
    "Aktivitas ringan yang menyenangkan membuat harimu semakin bersemangat.",
    "Ketenangan pikiran yang kamu rasakan hari ini adalah hadiah terbaik dari semesta.",
    "Tubuhmu merespons dengan baik terhadap hal-hal positif yang kamu lakukan.",
    "Senyum dan tawa hari ini adalah obat terbaik bagi jiwa dan ragamu.",
]

_WARNA_HOKI = [
    "Merah", "Emas", "Biru", "Hijau", "Ungu", "Putih",
    "Oranye", "Kuning", "Merah Muda", "Tosca", "Coklat Muda", "Silver",
]

def _seed_hari_ini():
    from config import CHANNEL_ID
    today = date.today()
    seed = int(today.strftime("%Y%m%d")) + CHANNEL_ID * 1000
    random.seed(seed)

def _bintang_str(n):
    return ("*" * n) + ("." * (5 - n))

def _tingkat_peruntungan(bintang):
    if bintang >= 4:
        return "Sangat Baik"
    elif bintang == 3:
        return "Baik"
    else:
        return "Cukup"

def _ramalan_satu_tanda(nama):
    bintang   = random.randint(3, 5)
    return {
        "nama"       : nama,
        "bintang"    : bintang,
        "bintang_str": _bintang_str(bintang),
        "peruntungan": _tingkat_peruntungan(bintang),
        "afirmasi"   : random.choice(_AFIRMASI),
        "cinta"      : random.choice(_CINTA),
        "karir"      : random.choice(_KARIR),
        "keuangan"   : random.choice(_KEUANGAN),
        "kesehatan"  : random.choice(_KESEHATAN),
        "warna_hoki" : random.choice(_WARNA_HOKI),
        "angka_hoki" : random.randint(1, 9),
    }

def ambil_data():
    _seed_hari_ini()
    tanda_list  = SHIO_LIST if TIPE_KONTEN == "shio" else ZODIAK_LIST
    tipe_label  = "Shio" if TIPE_KONTEN == "shio" else "Zodiak"

    ramalan = {tanda: _ramalan_satu_tanda(tanda) for tanda in tanda_list}

    tanda_terbaik    = max(ramalan, key=lambda x: ramalan[x]["bintang"])
    rata_bintang     = sum(v["bintang"] for v in ramalan.values()) / len(ramalan)
    peruntungan_hari = _tingkat_peruntungan(round(rata_bintang))
    warna_hari       = random.choice(_WARNA_HOKI)
    angka_hari       = random.randint(1, 9)
    pesan_hari       = random.choice(_AFIRMASI)

    now  = datetime.now()
    info = {
        "tanggal"         : now.strftime("%Y-%m-%d"),
        "waktu"           : now.strftime("%H:%M WIB"),
        "tipe"            : TIPE_KONTEN,
        "tipe_label"      : tipe_label,
        "tanda_list"      : tanda_list,
        "ramalan"         : ramalan,
        "tanda_terbaik"   : tanda_terbaik,
        "peruntungan_hari": peruntungan_hari,
        "warna_hari"      : warna_hari,
        "angka_hari"      : angka_hari,
        "pesan_hari"      : pesan_hari,
    }
    log(f"[scrape] Data {tipe_label} berhasil di-generate.")
    log(f"[scrape] Tanda terbaik: {tanda_terbaik} | Peruntungan: {peruntungan_hari}")
    return info
