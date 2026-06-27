from app.core.elasticsearch import es_client
from app.core.config import settings
from elasticsearch.helpers import async_bulk
import logging

logger = logging.getLogger(__name__)

async def index_chunks(chunks: list[dict]):
    if not chunks:
        return
    index_name = settings.ELASTICSEARCH_INDEX
    actions = []
    for chunk in chunks:
        # генерируем уникальный chunk_id
        chunk_id = f"{chunk['document_uuid']}_{chunk['page_number']}_{hash(chunk['text'])}"
        chunk["chunk_id"] = chunk_id
        actions.append({
            "_index": index_name,
            "_source": chunk
        })
    success, failed = await async_bulk(es_client, actions)
    if failed:
        logger.error(f"Failed to index {len(failed)} chunks")
    else:
        logger.info(f"Indexed {success} chunks")