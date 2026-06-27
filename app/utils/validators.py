from fastapi import UploadFile
from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

def validate_file(file: UploadFile):
    if file.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise ValueError(f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB} MB")
    ext = "." + file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File format not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")