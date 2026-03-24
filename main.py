# main.py
import os
import sys
import json
from datetime import datetime
from utils import log, ensure_dir
from config import CHANNEL_ID, NAMA_CHANNEL, TIPE_KONTEN

# Import modul-modul yang sudah kita buat
from scrape import ambil_data
from narasi import buat_narasi
from thumb import buat_thumbnail
from render import download_stok, buat_audio, render_video
# Jika uploader.py masih menggunakan versi lama, pastikan tidak ada dependency harga emas
try:
    from uploader import upload_video
except ImportError:
    upload_video = None

def bersihkan_file_lama():
    """Menghapus file sisa run sebelumnya agar tidak tercampur."""
    log("[Init] Membersihkan file sementara...")
    file_sampah = ["audio.mp3", "final_video.mp4", "thumbnail.jpg", "narasi.txt"]
    for f in file_sampah:
        if os.path.exists(f):
            os.remove(f)

def main():
    log(f"==================================================")
    log(f" MEMULAI GENERATOR VIDEO OTOMATIS ")
    log(f" Channel : {NAMA_CHANNEL} (ID: {CHANNEL_ID})")
    log(f" Tipe    : {TIPE_KONTEN.upper()}")
    log(f"==================================================")

    # 1. Persiapan
    bersihkan_file_lama()
    ensure_dir("gambar_bank")
    ensure_dir("video_bank")
    ensure_dir("gambar_static") # Opsional, untuk background fallback

    # 2. Generate Data Zodiak / Shio Hari Ini
    log("\n[Tahap 1] Mengumpulkan Data Ramalan...")
    info_hari_ini = ambil_data()
    
    if not info_hari_ini:
        log("Gagal mendapatkan data ramalan. Berhenti.")
        sys.exit(1)

    # 3. Generate Narasi (Gemini / Fallback)
    log("\n[Tahap 2] Membuat Narasi Video...")
    judul_video, teks_narasi = buat_narasi(info_hari_ini)
    
    if not teks_narasi:
        log("Gagal membuat narasi. Berhenti.")
        sys.exit(1)
        
    # Simpan narasi ke file untuk keperluan deskripsi YouTube/debugging
    with open("narasi.txt", "w", encoding="utf-8") as f:
        f.write(f"JUDUL: {judul_video}\n\nNARASI:\n{teks_narasi}")

    log(f"[Info] Judul Video: {judul_video}")
    log(f"[Info] Panjang Narasi: {len(teks_narasi)} karakter")

    # 4. Generate Suara (Text-to-Speech)
    log("\n[Tahap 3] Membuat Audio (TTS)...")
    sukses_audio = buat_audio(teks_narasi, "audio.mp3")
    if not sukses_audio:
        log("Gagal membuat audio. Berhenti.")
        sys.exit(1)

    # 5. Siapkan Stok Visual (Download Pixabay/Pexels)
    log("\n[Tahap 4] Menyiapkan Aset Visual...")
    download_stok()

    # 6. Render Video Final
    log("\n[Tahap 5] Merender Video...")
    video_final = render_video(info_hari_ini, audio_path="audio.mp3", output_path="final_video.mp4")
    if not video_final:
        log("Gagal merender video. Berhenti.")
        sys.exit(1)

    # 7. Generate Thumbnail
    log("\n[Tahap 6] Membuat Thumbnail...")
    thumbnail_final = buat_thumbnail(info_hari_ini, judul_video, output_path="thumbnail.jpg")
    if not thumbnail_final:
        log("Peringatan: Gagal membuat thumbnail, namun video berhasil dibuat.")

    # 8. Upload ke YouTube (Opsional)
    if upload_video:
        log("\n[Tahap 7] Mengunggah ke YouTube...")
        # Buat deskripsi dinamis
        tgl_str = info_hari_ini["tanggal"]
        deskripsi = (
            f"{judul_video}\n\n"
            f"Ramalan {TIPE_KONTEN} hari ini, {tgl_str}.\n"
            f"Tanda terbaik hari ini: {info_hari_ini['tanda_terbaik']}\n"
            f"Warna Keberuntungan: {info_hari_ini['warna_hari']}\n"
            f"Angka Hoki: {info_hari_ini['angka_hari']}\n\n"
            f"Jangan lupa LIKE, COMMENT, dan SUBSCRIBE untuk ramalan harian lainnya!\n\n"
            f"#Ramalan{TIPE_KONTEN.capitalize()} #Zodiak #Shio #HoroskopHariIni"
        )
        
        sukses_upload = upload_video(
            video_path="final_video.mp4",
            title=judul_video,
            description=deskripsi,
            thumbnail_path="thumbnail.jpg" if os.path.exists("thumbnail.jpg") else None
        )
        
        if sukses_upload:
            log("[Upload] Selesai!")
        else:
            log("[Upload] Gagal mengunggah video.")
    else:
        log("\n[Tahap 7] Modul uploader.py tidak ditemukan/diimport. Skip upload YouTube.")

    log("\n[SELESAI] Seluruh proses telah berhasil diselesaikan!")

if __name__ == "__main__":
    main()
