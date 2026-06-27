import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from app.services.parser import extract_text_from_file
from app.services.chunker import chunk_text
from app.services.indexer import index_chunks
from app.utils.validators import validate_file
from app.core.config import settings

router = APIRouter()

# Папка для временных файлов в корне проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # поднимаемся на 4 уровня до корня
TEMP_DIR = BASE_DIR / "temp_uploads"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    try:
        validate_file(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    doc_uuid = str(uuid.uuid4())
    file_path = TEMP_DIR / f"{doc_uuid}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(process_document, doc_uuid, file.filename, file_path)

    return {
        "document_uuid": doc_uuid,
        "file_name": file.filename,
        "status": "processing",
        "message": "Document uploaded, processing started"
    }

async def process_document(doc_uuid: str, file_name: str, file_path: Path):
    try:
        pages_text = extract_text_from_file(file_path)
        all_chunks = []
        for page_num, text in enumerate(pages_text, start=1):
            chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            for chunk in chunks:
                all_chunks.append({
                    "document_uuid": doc_uuid,
                    "file_name": file_name,
                    "page_number": page_num,
                    "text": chunk
                })
        await index_chunks(all_chunks)
        file_path.unlink(missing_ok=True)
    except Exception as e:
        print(f"Error processing {file_name}: {e}")