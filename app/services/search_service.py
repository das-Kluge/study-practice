from app.core.elasticsearch import es_client
from app.core.config import settings

async def search_documents(query: str, page: int, size: int):
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
    response = await es_client.search(index=index, body=body)
    results = []
    for hit in response["hits"]["hits"]:
        src = hit["_source"]
        highlight = hit.get("highlight", {}).get("text", [src["text"]])[0]
        results.append({
            "chunk_id": src.get("chunk_id", ""),
            "file_name": src["file_name"],
            "page": src["page_number"],
            "text": highlight,
            "score": hit["_score"]
        })
    return results