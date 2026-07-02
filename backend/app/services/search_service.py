import logging
from app.core.config import settings
import app.core.elasticsearch as es_module

logger = logging.getLogger(__name__)

async def search_documents(query: str, page: int = 1, size: int = 10):
    index = settings.ELASTICSEARCH_INDEX
    from_ = (page - 1) * size
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["text^3", "file_name^1.5"],
                "type": "best_fields",
                "fuzziness": "AUTO"
            }
        },
        "from": from_,
        "size": size,
        "highlight": {
            "fields": {
                "text": {
                    "fragment_size": 200,
                    "number_of_fragments": 1
                }
            }
        }
    }
    try:
        response = await es_module.es_client.search(index=index, body=body)
    except Exception as e:
        logger.error(f"Elasticsearch search error: {e}")
        raise

    results = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        highlight = hit.get("highlight", {}).get("text", [src.get("text", "")])[0]
        results.append({
            "chunk_id": src.get("chunk_id"),
            "file_name": src.get("file_name"),
            "page": src.get("page_number"),
            "text": highlight,
            "score": hit["_score"]
        })
    return results