# uploader.py
import os
import json
import httplib2
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from utils import log
from config import YOUTUBE_CATEGORY, YOUTUBE_TAGS, CHANNEL_ID

# Map Channel ID ke nama kredensial di GitHub Secrets
# Pastikan di GitHub Secrets ada: YT_CREDS_1, YT_CREDS_2, dst.
CRED_ENV_NAME = f"YT_CREDS_{CHANNEL_ID}"

def get_authenticated_service():
    """Mengambil kredensial dari Environment Variable dan membuat service YouTube."""
    creds_str = os.environ.get(CRED_ENV_NAME, "")
    if not creds_str:
        log(f"[Uploader] ERROR: Secret {CRED_ENV_NAME} tidak ditemukan!")
        return None
        
    try:
        creds_info = json.loads(creds_str)
        creds = Credentials.from_authorized_user_info(creds_info)
        youtube = build('youtube', 'v3', credentials=creds)
        return youtube
    except Exception as e:
        log(f"[Uploader] Gagal parse kredensial {CRED_ENV_NAME}: {e}")
        return None

def upload_video(video_path, title, description, thumbnail_path=None):
    """Mengunggah video ke YouTube dan mengatur Thumbnail."""
    youtube = get_authenticated_service()
    if not youtube:
        return False

    log(f"[Uploader] Memulai upload video: {title}")
    
    # Ambil waktu sekarang untuk tambahan deskripsi
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    full_description = f"{description}\n\nDiperbarui pada: {now_str}"

    body = {
        'snippet': {
            'title': title[:100],  # Max 100 karakter
            'description': full_description[:5000],
            'tags': YOUTUBE_TAGS[:15],
            'categoryId': YOUTUBE_CATEGORY
        },
        'status': {
            'privacyStatus': 'public', # Ubah ke 'private'/'unlisted' jika ingin ditinjau dulu
            'selfDeclaredMadeForKids': False
        }
    }

    try:
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                log(f"[Uploader] Progress upload: {progress}%")

        video_id = response.get('id')
        log(f"[Uploader] Sukses! Video ID: {video_id}")
        log(f"[Uploader] Link: https://youtu.be/{video_id}")

        # Upload Thumbnail jika ada
        if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
            log(f"[Uploader] Mengunggah thumbnail: {thumbnail_path}...")
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path)
                ).execute()
                log("[Uploader] Thumbnail berhasil dipasang.")
            except Exception as e:
                log(f"[Uploader] Peringatan: Gagal set thumbnail: {e}")

        return True

    except httplib2.HttpLib2Error as e:
        log(f"[Uploader] Network Error saat upload: {e}")
        return False
    except Exception as e:
        log(f"[Uploader] Error tidak terduga saat upload: {e}")
        return False
