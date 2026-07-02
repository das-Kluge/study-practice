import logging
from elasticsearch.helpers import async_bulk
from app.core.config import settings
import app.core.elasticsearch as es_module

logger = logging.getLogger(__name__)

async def index_chunks(chunks: list[dict]):
    if not chunks:
        return
    index_name = settings.ELASTICSEARCH_INDEX
    actions = []
    for chunk in chunks:
        chunk_id = f"{chunk['document_uuid']}_{chunk['page_number']}_{hash(chunk['text'])}"
        chunk["chunk_id"] = chunk_id
        actions.append({
            "_index": index_name,
            "_source": chunk
        })
    # Используем актуальный экземпляр через модуль
    success, failed = await async_bulk(es_module.es_client, actions)
    if failed:
        logger.error(f"Failed to index {len(failed)} chunks")
    else:
        logger.info(f"Indexed {success} chunks")