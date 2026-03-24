# render.py  –  Versi HYBRID CEPAT (zoom statis + xfade + color grade)
import os, random, glob, time, requests, subprocess
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, FPS,
    KATA_KUNCI_GAMBAR, KATA_KUNCI_VIDEO,
    PIXABAY_API_KEY, PEXELS_API_KEY,
    VOICE, VOICE_RATE,
    FOLDER_GAMBAR, FOLDER_VIDEO_BANK, FFMPEG_LOG,
    TIPE_KONTEN,
)
from utils import log, ensure_dir

DURASI_GAMBAR_MIN = 5.0
DURASI_GAMBAR_MAX = 8.0

XFADE_EFFECTS = [
    "fade", "fadeblack", "fadegrays",
    "slideright", "slideleft", "slideup",
    "dissolve", "smoothleft", "smoothright",
]

COLOR_GRADE = {
    "shio":   "eq=saturation=1.4:contrast=1.1:brightness=0.02,hue=h=5",
    "zodiak": "eq=saturation=1.3:contrast=1.15:brightness=0.01,hue=h=-5",
}

ZOOM_LEVELS = [
    f"scale={int(VIDEO_WIDTH*1.00)}:{int(VIDEO_HEIGHT*1.00)},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
    f"scale={int(VIDEO_WIDTH*1.05)}:{int(VIDEO_HEIGHT*1.05)},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
    f"scale={int(VIDEO_WIDTH*1.10)}:{int(VIDEO_HEIGHT*1.10)},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
    f"scale={int(VIDEO_WIDTH*1.15)}:{int(VIDEO_HEIGHT*1.15)},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
    f"scale={int(VIDEO_WIDTH*1.10)}:{int(VIDEO_HEIGHT*1.10)},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:0:0",
    f"scale={int(VIDEO_WIDTH*1.10)}:{int(VIDEO_HEIGHT*1.10)},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:iw-ow:ih-oh",
    f"scale={int(VIDEO_WIDTH*1.10)}:{int(VIDEO_HEIGHT*1.10)},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:iw-ow:0",
    f"scale={int(VIDEO_WIDTH*1.10)}:{int(VIDEO_HEIGHT*1.10)},crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}:0:ih-oh",
]

# ════════════════════════════════════════════════════════════
# 1. TTS
# ════════════════════════════════════════════════════════════
def buat_audio(narasi, output_path="audio.mp3"):
    log(f"[TTS] Membuat audio dengan voice {VOICE}...")
    try:
        import edge_tts, asyncio
        async def _gen():
            comm = edge_tts.Communicate(narasi, VOICE, rate=VOICE_RATE)
            await comm.save(output_path)
        asyncio.run(_gen())
        if os.path.exists(output_path):
            log(f"[TTS] OK – {os.path.getsize(output_path):,} bytes")
            return True
        log("[TTS] Gagal: file tidak ditemukan")
        return False
    except Exception as e:
        log(f"[TTS] Error: {e}")
        return False

# ════════════════════════════════════════════════════════════
# 2. DOWNLOAD STOK
# ════════════════════════════════════════════════════════════
def download_stok():
    log("[Stok] Memeriksa stok gambar & video...")
    ensure_dir(FOLDER_GAMBAR)
    ensure_dir(FOLDER_VIDEO_BANK)

    gambar_ada = (
        glob.glob(f"{FOLDER_GAMBAR}/*.jpg") +
        glob.glob(f"{FOLDER_GAMBAR}/*.jpeg") +
        glob.glob(f"{FOLDER_GAMBAR}/*.png") +
        glob.glob("gambar_static/*.jpg") +
        glob.glob("gambar_static/*.jpeg") +
        glob.glob("gambar_static/*.png")
    )
    video_ada = glob.glob(f"{FOLDER_VIDEO_BANK}/*.mp4")
    log(f"[Stok] Gambar: {len(gambar_ada)} (termasuk gambar_static), Video: {len(video_ada)}")

    if len(gambar_ada) >= 5:
        log("[Stok] Gambar sudah cukup, skip download Pixabay")
    elif PIXABAY_API_KEY:
        log("[Stok] Download gambar dari Pixabay...")
        keyword = random.choice(KATA_KUNCI_GAMBAR)
        try:
            url = (
                f"https://pixabay.com/api/?key={PIXABAY_API_KEY}"
                f"&q={keyword}&image_type=photo&orientation=horizontal&per_page=15"
            )
            hits = requests.get(url, timeout=15).json().get("hits", [])
            for i, item in enumerate(hits[:10]):
                img_url = item.get("largeImageURL")
                if img_url:
                    r = requests.get(img_url, timeout=15)
                    with open(f"{FOLDER_GAMBAR}/pix_{int(time.time())}_{i}.jpg", "wb") as f:
                        f.write(r.content)
            log("[Stok] Gambar Pixabay OK")
        except Exception as e:
            log(f"[Stok] Gagal Pixabay: {e}")
    else:
        log("[Stok] PIXABAY_API_KEY kosong, skip download gambar")

    if len(video_ada) < 4 and PEXELS_API_KEY:
        log("[Stok] Download video dari Pexels...")
        keyword = random.choice(KATA_KUNCI_VIDEO)
        try:
            url = f"https://api.pexels.com/videos/search?query={keyword}&per_page=6&orientation=landscape"
            videos = requests.get(
                url, headers={"Authorization": PEXELS_API_KEY}, timeout=15
            ).json().get("videos", [])
            for i, item in enumerate(videos):
                files = [f for f in item.get("video_files", []) if f.get("width", 0) >= 1280]
                if not files:
                    continue
                r = requests.get(files[0]["link"], timeout=30)
                with open(f"{FOLDER_VIDEO_BANK}/pex_{int(time.time())}_{i}.mp4", "wb") as f:
                    f.write(r.content)
            log("[Stok] Video Pexels OK")
        except Exception as e:
            log(f"[Stok] Gagal Pexels: {e}")
    elif not PEXELS_API_KEY:
        log("[Stok] PEXELS_API_KEY kosong, skip download video")

# ════════════════════════════════════════════════════════════
# 3. FALLBACK GAMBAR DARURAT
# ════════════════════════════════════════════════════════════
def _buat_gambar_fallback():
    from PIL import Image, ImageDraw
    ensure_dir(FOLDER_GAMBAR)
    warna_list = [
        (15, 5, 40), (30, 5, 20), (5, 20, 40),
        (25, 10, 50), (40, 10, 10), (10, 30, 30),
    ]
    files = []
    for i, warna in enumerate(warna_list):
        path = f"{FOLDER_GAMBAR}/fallback_{i}.jpg"
        img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), warna)
        draw = ImageDraw.Draw(img)
        for y in range(0, VIDEO_HEIGHT, 3):
            alpha = int(40 * (y / VIDEO_HEIGHT))
            draw.line(
                [(0, y), (VIDEO_WIDTH, y)],
                fill=(
                    min(255, warna[0] + alpha),
                    min(255, warna[1] + alpha),
                    min(255, warna[2] + alpha),
                )
            )
        img.save(path, "JPEG", quality=90)
        files.append(path)
    log(f"[Stok] {len(files)} gambar fallback darurat dibuat.")
    return files

# ════════════════════════════════════════════════════════════
# 4. HELPER DURASI
# ════════════════════════════════════════════════════════════
def _durasi(path):
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path
        ]).decode().strip()
        return float(out)
    except:
        return 0.0

# ════════════════════════════════════════════════════════════
# 5. KLIP DARI GAMBAR (zoom statis + color grade)
# ════════════════════════════════════════════════════════════
def _klip_dari_gambar(img_path, durasi, output, zoom_filter, grade_filter):
    vf = (
        f"scale={int(VIDEO_WIDTH*1.2)}:{int(VIDEO_HEIGHT*1.2)}"
        f":force_original_aspect_ratio=increase,"
        f"{zoom_filter},"
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},"
        f"setsar=1,"
        f"{grade_filter}"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(durasi),
        "-i", img_path,
        "-vf", vf,
        "-r", str(FPS),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-an", output,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return os.path.exists(output)

# ════════════════════════════════════════════════════════════
# 6. KLIP DARI VIDEO STOK
# ════════════════════════════════════════════════════════════
def _klip_dari_video(vid_path, output, grade_filter):
    vf = (
        f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}"
        f":force_original_aspect_ratio=decrease,"
        f"pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,"
        f"{grade_filter}"
    )
    cmd = [
        "ffmpeg", "-y", "-i", vid_path,
        "-vf", vf,
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-an", output,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return os.path.exists(output)

# ════════════════════════════════════════════════════════════
# 7. GABUNG KLIP DENGAN XFADE TRANSITION
# ════════════════════════════════════════════════════════════
def _gabung_dengan_xfade(klip_list, durasi_list, output):
    if len(klip_list) == 1:
        import shutil
        shutil.copy(klip_list[0], output)
        return os.path.exists(output)

    DURASI_TRANSISI = 1.0

    inputs = []
    for k in klip_list:
        inputs += ["-i", k]

    filter_parts = []
    offset = 0.0
    prev_label = "[0:v]"

    for i in range(1, len(klip_list)):
        offset += durasi_list[i-1] - DURASI_TRANSISI
        efek = random.choice(XFADE_EFFECTS)
        next_label = f"[v{i}]" if i < len(klip_list) - 1 else "[vout]"
        filter_parts.append(
            f"{prev_label}[{i}:v]xfade=transition={efek}"
            f":duration={DURASI_TRANSISI}:offset={offset:.3f}{next_label}"
        )
        prev_label = f"[v{i}]"

    filter_complex = ";".join(filter_parts)

    cmd = (
        ["ffmpeg", "-y"] +
        inputs +
        [
            "-filter_complex", filter_complex,
            "-map", "[vout]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            "-pix_fmt", "yuv420p",
            "-an", output,
        ]
    )

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        if os.path.exists(output):
            return True
    except subprocess.TimeoutExpired:
        log("[Render] xfade timeout, fallback ke concat biasa...")

    # Fallback concat tanpa transisi
    concat_file = "concat_xfade_fallback.txt"
    with open(concat_file, "w") as f:
        for k in klip_list:
            f.write(f"file '{k}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file, "-c", "copy", output
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(concat_file):
        os.remove(concat_file)
    return os.path.exists(output)

# ════════════════════════════════════════════════════════════
# 8. RENDER UTAMA
# ════════════════════════════════════════════════════════════
def render_video(info, audio_path="audio.mp3", output_path="final_video.mp4"):
    log("[Render] Memulai render video (hybrid: zoom statis + xfade)...")

    durasi_audio = _durasi(audio_path)
    if durasi_audio <= 0:
        log("[Render] Gagal baca durasi audio")
        return False
    log(f"[Render] Durasi audio: {durasi_audio:.1f}s ({durasi_audio/60:.1f} menit)")

    # Kumpulkan semua aset visual
    gambar_files = (
        glob.glob(f"{FOLDER_GAMBAR}/*.jpg") +
        glob.glob(f"{FOLDER_GAMBAR}/*.jpeg") +
        glob.glob(f"{FOLDER_GAMBAR}/*.png") +
        glob.glob("gambar_static/*.jpg") +
        glob.glob("gambar_static/*.jpeg") +
        glob.glob("gambar_static/*.png")
    )
    video_files = glob.glob(f"{FOLDER_VIDEO_BANK}/*.mp4")

    # Fallback darurat jika benar-benar kosong
    if not gambar_files:
        gambar_files = _buat_gambar_fallback()

    random.shuffle(gambar_files)
    random.shuffle(video_files)

    grade = COLOR_GRADE.get(TIPE_KONTEN, COLOR_GRADE["shio"])

    klip_list   = []
    durasi_list = []
    waktu       = 0.0
    idx         = 0

    log("[Render] Membuat klip individual...")
    while waktu < (durasi_audio + 5) and idx < 200:
        pakai_video = bool(video_files) and (random.random() > 0.4)
        out = f"klip_{idx:04d}.mp4"

        if pakai_video:
            src = video_files[idx % len(video_files)]
            if _klip_dari_video(src, out, grade):
                dur = _durasi(out)
                if dur > 0:
                    klip_list.append(out)
                    durasi_list.append(dur)
                    waktu += dur
                    log(f"  [{idx:03d}] VIDEO {dur:.1f}s → total {waktu:.1f}s")
        else:
            src  = gambar_files[idx % len(gambar_files)]
            dur  = random.uniform(DURASI_GAMBAR_MIN, DURASI_GAMBAR_MAX)
            zoom = random.choice(ZOOM_LEVELS)
            if _klip_dari_gambar(src, dur, out, zoom, grade):
                klip_list.append(out)
                durasi_list.append(dur)
                waktu += dur
                log(f"  [{idx:03d}] GAMBAR {dur:.1f}s → total {waktu:.1f}s")

        idx += 1

    if not klip_list:
        log("[Render] Tidak ada klip yang berhasil dibuat!")
        return False

    log(f"[Render] {len(klip_list)} klip siap, {waktu:.1f}s. Gabung dengan xfade...")

    visual = "visual_only.mp4"
    BATCH  = 15

    if len(klip_list) > BATCH:
        log(f"[Render] Klip >{BATCH}, proses xfade per batch...")
        batch_results = []
        for b_start in range(0, len(klip_list), BATCH):
            b_klip = klip_list[b_start:b_start + BATCH]
            b_dur  = durasi_list[b_start:b_start + BATCH]
            b_out  = f"batch_{b_start:04d}.mp4"
            _gabung_dengan_xfade(b_klip, b_dur, b_out)
            if os.path.exists(b_out):
                batch_results.append(b_out)

        concat_file = "concat_batch.txt"
        with open(concat_file, "w") as f:
            for b in batch_results:
                f.write(f"file '{b}'\n")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_file, "-c", "copy", visual
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(concat_file):
            os.remove(concat_file)
        for b in batch_results:
            if os.path.exists(b):
                os.remove(b)
    else:
        _gabung_dengan_xfade(klip_list, durasi_list, visual)

    if not os.path.exists(visual):
        log("[Render] Gagal membuat visual_only.mp4")
        return False

    # Gabung visual + audio
    log("[Render] Menggabungkan visual + audio...")

    if os.path.exists("bgm.mp3"):
        log("[Render] Tambahkan BGM...")
        cmd_final = [
            "ffmpeg", "-y",
            "-i", visual,
            "-i", audio_path,
            "-stream_loop", "-1", "-i", "bgm.mp3",
            "-filter_complex",
            "[1:a]volume=1.0[a1];[2:a]volume=0.08[a2];[a1][a2]amix=inputs=2:duration=first[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", output_path,
        ]
    else:
        cmd_final = [
            "ffmpeg", "-y",
            "-i", visual,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            output_path,
        ]

    try:
        with open(FFMPEG_LOG, "w") as lf:
            subprocess.run(cmd_final, stdout=lf, stderr=subprocess.STDOUT, check=True)
        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / 1024 / 1024
            log(f"[Render] SUKSES! {output_path} ({size_mb:.1f} MB)")
            for k in klip_list:
                if os.path.exists(k):
                    os.remove(k)
            if os.path.exists(visual):
                os.remove(visual)
            return output_path
    except subprocess.CalledProcessError as e:
        log(f"[Render] FFmpeg error: {e}")
    except Exception as e:
        log(f"[Render] Error tak terduga: {e}")

    return False
