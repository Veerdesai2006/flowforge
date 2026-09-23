"""
=========================================================
FlowForge - File Upload API
=========================================================
Handles profile picture and banner image uploads.
Files are saved to app/static/uploads/ and the URL is
stored in the database.
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.user import UserRepository

router = APIRouter(prefix="/api/upload", tags=["Upload"])

# Where we save uploaded files on disk
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed image types for security
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def save_file(upload: UploadFile, subfolder: str) -> str:
    """
    Save an uploaded file to disk and return its public URL.
    
    We generate a random UUID filename to avoid collisions and
    prevent attackers from guessing file paths.
    """
    if upload.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, WebP, and GIF images are allowed."
        )

    # Read the file bytes
    contents = upload.file.read()

    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be under 5MB."
        )

    # Generate a unique filename: e.g. "avatars/abc123def456.jpg"
    ext = upload.filename.rsplit(".", 1)[-1] if "." in upload.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"

    folder = os.path.join(UPLOAD_DIR, subfolder)
    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    # Return the URL path so the browser can load it via /static/...
    return f"/static/uploads/{subfolder}/{filename}"


@router.post("/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a profile avatar for the currently logged-in user.
    """
    url = save_file(file, "avatars")

    repo = UserRepository(db)
    current_user.avatar_url = url
    repo.update(current_user)

    return {"avatar_url": url}


@router.post("/banner")
def upload_banner(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a profile banner for the currently logged-in user.
    """
    url = save_file(file, "banners")

    repo = UserRepository(db)
    current_user.banner_url = url
    repo.update(current_user)

    return {"banner_url": url}
