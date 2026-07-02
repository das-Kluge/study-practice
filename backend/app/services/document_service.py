from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.document import Document
from uuid import UUID

async def create_document(db: AsyncSession, file_name: str, file_size: int) -> UUID:
    doc = Document(file_name=file_name, file_size=file_size)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc.id

async def update_document_status(
    db: AsyncSession,
    doc_id: UUID,
    status: str,
    error_msg: str = None,
    page_count: int = None
):
    values = {"status": status}
    if error_msg is not None:
        values["error_message"] = error_msg
    if page_count is not None:
        values["page_count"] = page_count
    stmt = update(Document).where(Document.id == doc_id).values(**values)
    await db.execute(stmt)
    await db.commit()

async def get_documents(db: AsyncSession, limit: int = 100, offset: int = 0):
    result = await db.execute(
        select(Document).order_by(Document.uploaded_at.desc()).offset(offset).limit(limit)
    )
    return result.scalars().all()