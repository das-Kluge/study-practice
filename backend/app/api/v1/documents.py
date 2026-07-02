import shutil
import logging
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, AsyncSessionLocal
from app.services.parser import extract_text_from_file
from app.services.chunker import chunk_text
from app.services.indexer import index_chunks
from app.services.document_service import create_document, update_document_status
from app.utils.validators import validate_file
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
TEMP_DIR = Path("/tmp/uploads")
TEMP_DIR.mkdir(exist_ok=True)


@router.post("/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    validate_file(file)
    doc_uuid = await create_document(db, file.filename, file.size)
    file_path = TEMP_DIR / f"{doc_uuid}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    background_tasks.add_task(process_document, doc_uuid, file.filename, file_path)
    return {"document_uuid": str(doc_uuid), "file_name": file.filename, "status": "processing"}


async def process_document(doc_uuid: UUID, file_name: str, file_path: Path):
    logger.info(f"=== START processing {file_name} (UUID: {doc_uuid}) ===")
    try:
        logger.info("Step 1: Extracting text...")
        pages = extract_text_from_file(file_path)
        logger.info(f"Extracted {len(pages)} pages")

        logger.info("Step 2: Chunking text...")
        all_chunks = []
        for page_num, text in enumerate(pages, start=1):
            logger.info(f"Chunking page {page_num} (length {len(text)})")
            chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            logger.info(f"Page {page_num}: {len(chunks)} chunks")
            for chunk in chunks:
                all_chunks.append({
                    "document_uuid": str(doc_uuid),
                    "file_name": file_name,
                    "page_number": page_num,
                    "text": chunk,
                })
        logger.info(f"Total chunks: {len(all_chunks)}")

        logger.info("Step 3: Indexing chunks in Elasticsearch...")
        await index_chunks(all_chunks)
        logger.info("Indexing completed")

        logger.info("Step 4: Updating document status in DB...")
        async with AsyncSessionLocal() as db:
            await update_document_status(db, doc_uuid, "ready", page_count=len(pages))
        logger.info("Status updated to ready")

        file_path.unlink(missing_ok=True)
        logger.info(f"=== FINISHED processing {file_name} ===")

    except Exception as e:
        logger.error(f"!!! ERROR processing {file_name}: {e}", exc_info=True)
        async with AsyncSessionLocal() as db:
            await update_document_status(db, doc_uuid, "error", str(e))


@router.get("/documents")
async def list_documents(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    from app.services.document_service import get_documents
    docs = await get_documents(db, limit, offset)
    return [{
        "id": str(d.id),
        "file_name": d.file_name,
        "status": d.status,
        "uploaded_at": d.uploaded_at.isoformat(),
        "page_count": d.page_count,
        "file_size": d.file_size,
    } for d in docs]