# render.py
import os
import random
import glob
import time
import requests
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS, KATA_KUNCI_GAMBAR, KATA_KUNCI_VIDEO,
    PIXABAY_API_KEY, PEXELS_API_KEY, VOICE, VOICE_RATE, FOLDER_GAMBAR, FOLDER_VIDEO_BANK,
    NAMA_CHANNEL, TIPE_KONTEN, SKEMA_AKTIF, FFMPEG_LOG
)
from utils import log, ensure_dir
import subprocess
import shutil

# ════════════════════════════════════════════════════════════
# 1. TEXT TO SPEECH (TTS) MENGGUNAKAN EDGE-TTS
# ════════════════════════════════════════════════════════════
def buat_audio(narasi, output_path="audio.mp3"):
    log(f"[TTS] Membuat audio narasi dengan voice {VOICE}...")
    try:
        import edge_tts
        import asyncio

        async def _generate():
            communicate = edge_tts.Communicate(narasi, VOICE, rate=VOICE_RATE)
            await communicate.save(output_path)

        asyncio.run(_generate())
        if os.path.exists(output_path):
            log(f"[TTS] Audio berhasil dibuat: {output_path}")
            return True
        else:
            log("[TTS] Gagal: file audio tidak ditemukan.")
            return False
    except Exception as e:
        log(f"[TTS] Error: {e}")
        return False

# ════════════════════════════════════════════════════════════
# 2. DOWNLOAD GAMBAR/VIDEO STOK (PIXABAY & PEXELS)
# ════════════════════════════════════════════════════════════
def download_stok():
    log("[Stok] Memeriksa stok gambar & video...")
    ensure_dir(FOLDER_GAMBAR)
    ensure_dir(FOLDER_VIDEO_BANK)

    # Cek jumlah saat ini
    gambar_ada = glob.glob(f"{FOLDER_GAMBAR}/*.jpg") + glob.glob(f"{FOLDER_GAMBAR}/*.jpeg") + glob.glob(f"{FOLDER_GAMBAR}/*.png")
    video_ada = glob.glob(f"{FOLDER_VIDEO_BANK}/*.mp4")

    log(f"[Stok] Gambar: {len(gambar_ada)}, Video: {len(video_ada)}")

    # Download Gambar jika kurang
    if len(gambar_ada) < 10 and PIXABAY_API_KEY:
        log("[Stok] Mengunduh gambar tambahan dari Pixabay...")
        keyword = random.choice(KATA_KUNCI_GAMBAR)
        try:
            url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={keyword}&image_type=photo&orientation=horizontal&per_page=15"
            res = requests.get(url, timeout=15).json()
            for i, item in enumerate(res.get("hits", [])[:10]):
                img_url = item.get("largeImageURL")
                if img_url:
                    r = requests.get(img_url, timeout=15)
                    with open(f"{FOLDER_GAMBAR}/dl_pix_{int(time.time())}_{i}.jpg", "wb") as f:
                        f.write(r.content)
            log("[Stok] Berhasil mengunduh gambar.")
        except Exception as e:
            log(f"[Stok] Gagal download gambar: {e}")

    # Download Video jika kurang
    if len(video_ada) < 4 and PEXELS_API_KEY:
        log("[Stok] Mengunduh video tambahan dari Pexels...")
        keyword = random.choice(KATA_KUNCI_VIDEO)
        headers = {"Authorization": PEXELS_API_KEY}
        try:
            url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=5&orientation=landscape"
            res = requests.get(url, headers=headers, timeout=15).json()
            for i, item in enumerate(res.get("videos", [])):
                video_files = item.get("video_files", [])
                # Cari resolusi HD/FHD
                hd_files = [f for f in video_files if f.get("width", 0) >= 1280]
                if not hd_files: continue
                
                vid_url = hd_files[0].get("link")
                if vid_url:
                    r = requests.get(vid_url, timeout=30)
                    with open(f"{FOLDER_VIDEO_BANK}/dl_pex_{int(time.time())}_{i}.mp4", "wb") as f:
                        f.write(r.content)
            log("[Stok] Berhasil mengunduh video.")
        except Exception as e:
            log(f"[Stok] Gagal download video: {e}")

# ════════════════════════════════════════════════════════════
# 3. MENGGABUNGKAN VIDEO (FFMPEG)
# ════════════════════════════════════════════════════════════
def render_video(info, audio_path="audio.mp3", output_path="final_video.mp4"):
    log("[Render] Memulai proses render video...")
    
    # 1. Pastikan durasi audio
    durasi_audio = 0
    try:
        cmd_dur = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path
        ]
        out = subprocess.check_output(cmd_dur).decode().strip()
        durasi_audio = float(out)
        log(f"[Render] Durasi audio: {durasi_audio:.2f} detik")
    except Exception as e:
        log(f"[Render] Gagal membaca durasi audio: {e}")
        return False

    # 2. Siapkan aset gambar & video
    gambar_files = glob.glob(f"{FOLDER_GAMBAR}/*.jpg") + glob.glob(f"{FOLDER_GAMBAR}/*.jpeg") + glob.glob(f"{FOLDER_GAMBAR}/*.png")
    video_files = glob.glob(f"{FOLDER_VIDEO_BANK}/*.mp4")
    
    if not gambar_files and not video_files:
        log("[Render] ERROR: Tidak ada aset gambar/video sama sekali!")
        return False

    # Acak urutan
    random.shuffle(gambar_files)
    random.shuffle(video_files)
    
    # Buat file concat sementara
    concat_file = "concat_list.txt"
    waktu_terkumpul = 0
    
    with open(concat_file, "w", encoding="utf-8") as f:
        # Loop sampai durasi memenuhi audio + buffer 5 detik
        idx_img = 0
        idx_vid = 0
        
        while waktu_terkumpul < (durasi_audio + 5):
            # Selang-seling antara video dan gambar
            pakai_video = (random.random() > 0.4) and (len(video_files) > 0)
            
            if pakai_video:
                vid = video_files[idx_vid % len(video_files)]
                idx_vid += 1
                try:
                    # Cek durasi video
                    cmd_v = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", vid]
                    vdur = float(subprocess.check_output(cmd_v).decode().strip())
                    
                    # Konversi video ke resolusi seragam (1920x1080) dan fps 30 agar concat lancar
                    tmp_vid = f"tmp_v_{idx_vid}.mp4"
                    cmd_conv = [
                        "ffmpeg", "-y", "-i", vid,
                        "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                        "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
                        "-an", tmp_vid
                    ]
                    subprocess.run(cmd_conv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    
                    f.write(f"file '{tmp_vid}'\n")
                    waktu_terkumpul += vdur
                except:
                    continue
            else:
                img = gambar_files[idx_img % len(gambar_files)]
                idx_img += 1
                img_dur = random.uniform(5.0, 8.0) # Tampilkan gambar 5-8 detik
                
                # Buat video dari gambar dengan efek Ken Burns (Zoom/Pan lambat)
                tmp_vid = f"tmp_i_{idx_img}.mp4"
                
                # Arah zoom random
                zoom_dir = random.choice([
                    "zoompan=z='min(zoom+0.0015,1.5)':d=300", # Zoom in lambat
                    "zoompan=z='1.5-min((1.5-1)*(time/10),1.5-1)':d=300" # Zoom out lambat
                ])
                
                cmd_img = [
                    "ffmpeg", "-y", "-loop", "1", "-t", str(img_dur), "-i", img,
                    "-vf", f"scale=8000:-1,{zoom_dir},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},setsar=1",
                    "-r", str(FPS), "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
                    "-pix_fmt", "yuv420p", tmp_vid
                ]
                subprocess.run(cmd_img, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                f.write(f"file '{tmp_vid}'\n")
                waktu_terkumpul += img_dur

    log(f"[Render] Menggabungkan klip visual (total {waktu_terkumpul:.2f}s)...")
    
    # Concat semua klip visual menjadi satu video utuh
    visual_output = "visual_only.mp4"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c", "copy", visual_output
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 3. Gabungkan Video Visual dengan Audio TTS
    log("[Render] Menggabungkan visual dengan audio narasi...")
    cmd_final = [
        "ffmpeg", "-y", 
        "-i", visual_output, 
        "-i", audio_path, 
        "-c:v", "copy", 
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", # Potong video agar sesuai panjang audio
        output_path
    ]
    
    # BGM / Musik latar (opsional, jika ada file bgm.mp3 di folder)
    if os.path.exists("bgm.mp3"):
        log("[Render] Menambahkan musik latar (BGM)...")
        cmd_final = [
            "ffmpeg", "-y", 
            "-i", visual_output, 
            "-i", audio_path, 
            "-stream_loop", "-1", "-i", "bgm.mp3", # Loop BGM
            "-filter_complex", "[1:a]volume=1.0[a1];[2:a]volume=0.1[a2];[a1][a2]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", output_path
        ]

    try:
        with open(FFMPEG_LOG, "w") as log_f:
            subprocess.run(cmd_final, stdout=log_f, stderr=subprocess.STDOUT, check=True)
            
        if os.path.exists(output_path):
            log(f"[Render] SUKSES! Video akhir tersimpan di: {output_path}")
            
            # Bersihkan file temporary
            for f in glob.glob("tmp_*.mp4"): os.remove(f)
            if os.path.exists(concat_file): os.remove(concat_file)
            if os.path.exists(visual_output): os.remove(visual_output)
            
            return output_path
    except Exception as e:
        log(f"[Render] Gagal saat render final: {e}")
        return False
