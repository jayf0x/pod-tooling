from __future__ import annotations

"""
YouTube posting stage.

Uploads a music track + cover image to YouTube via the Data API v3.
Requires OAuth2 credentials (client_secrets.json + token).
"""

import logging
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def upload_to_youtube(
    audio_path: Path,
    title: str,
    description: str,
    cover_path: Path | None = None,
    tags: list[str] | None = None,
    privacy: str = "private",
) -> dict:
    """Upload a track to YouTube.

    The audio file is uploaded as a video (YouTube requires video format).
    In production, this should first combine audio + cover image into an MP4.

    Args:
        audio_path: Path to the audio/video file to upload.
        title: Video title.
        description: Video description.
        cover_path: Optional cover image (used as thumbnail).
        tags: Optional list of tags.
        privacy: Privacy status — "private", "unlisted", or "public".

    Returns:
        Dict with upload result including video ID and URL.

    Raises:
        FileNotFoundError: If the audio file doesn't exist.
        RuntimeError: If upload fails.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    tags = tags or ["AI Music", "Blanc Beats", "Generated"]

    # Check for credentials
    secrets_path = Path(config.YOUTUBE_CLIENT_SECRETS_FILE)
    if not secrets_path.exists():
        logger.warning(
            "YouTube client_secrets.json not found at %s — running in dry-run mode.",
            secrets_path,
        )
        return _dry_run(audio_path, title, description, tags, privacy)

    return _do_upload(audio_path, title, description, cover_path, tags, privacy)


def _do_upload(
    audio_path: Path,
    title: str,
    description: str,
    cover_path: Path | None,
    tags: list[str],
    privacy: str,
) -> dict:
    """Perform the actual YouTube upload via google-api-python-client.

    Args:
        audio_path: Path to video/audio file.
        title: Video title.
        description: Video description.
        cover_path: Optional thumbnail image.
        tags: Video tags.
        privacy: Privacy status.

    Returns:
        Dict with video_id and url.
    """
    # REASON: Import here to avoid hard dependency when running in dry-run/test mode
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    token_path = Path(config.YOUTUBE_OAUTH_TOKEN_FILE)
    if not token_path.exists():
        raise RuntimeError(
            f"OAuth token file not found: {token_path}. "
            "Run the OAuth flow first to generate it."
        )

    import json
    token_data = json.loads(token_path.read_text())
    credentials = Credentials.from_authorized_user_info(token_data)

    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "10",  # Music category
        },
        "status": {
            "privacyStatus": privacy,
        },
    }

    media = MediaFileUpload(
        str(audio_path),
        mimetype="video/mp4",
        resumable=True,
    )

    logger.info("Uploading '%s' to YouTube (privacy=%s)", title, privacy)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info("Upload progress: %d%%", int(status.progress() * 100))

    video_id = response["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info("Upload complete: %s", url)

    # Set thumbnail if provided
    if cover_path and cover_path.exists():
        try:
            thumb_media = MediaFileUpload(str(cover_path), mimetype="image/png")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=thumb_media,
            ).execute()
            logger.info("Thumbnail set for %s", video_id)
        except Exception as exc:
            logger.error("Failed to set thumbnail: %s", exc)

    return {"video_id": video_id, "url": url, "privacy": privacy}


def _dry_run(
    audio_path: Path,
    title: str,
    description: str,
    tags: list[str],
    privacy: str,
) -> dict:
    """Simulate an upload when credentials aren't available.

    Args:
        audio_path: Path to the audio file.
        title: Video title.
        description: Video description.
        tags: Video tags.
        privacy: Privacy status.

    Returns:
        Dict with dry_run flag and simulated data.
    """
    logger.info(
        "[DRY RUN] Would upload '%s' (%s) — privacy=%s, tags=%s",
        title, audio_path.name, privacy, tags,
    )
    return {
        "dry_run": True,
        "title": title,
        "description": description[:100],
        "audio_file": audio_path.name,
        "privacy": privacy,
    }
