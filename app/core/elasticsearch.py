from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
es_client: AsyncElasticsearch | None = None

async def init_elasticsearch():
    global es_client
    es_client = AsyncElasticsearch(
        hosts=[f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"],
        verify_certs=False,
        request_timeout=30
    )
    try:
        await es_client.ping()
        logger.info("Connected to Elasticsearch")
    except ConnectionError:
        logger.error("Cannot connect to Elasticsearch")
        raise

    index_name = settings.ELASTICSEARCH_INDEX
    if not await es_client.indices.exists(index=index_name):
        mapping = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "russian_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "russian_morphology", "stopwords_ru"]
                        }
                    },
                    "filter": {
                        "russian_morphology": {
                            "type": "stemmer",
                            "language": "russian"
                        },
                        "stopwords_ru": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "text": {"type": "text", "analyzer": "russian_analyzer"},
                    "file_name": {"type": "keyword"},
                    "page_number": {"type": "integer"},
                    "chunk_id": {"type": "keyword"},
                    "document_uuid": {"type": "keyword"}
                }
            }
        }
        await es_client.indices.create(index=index_name, body=mapping)
        logger.info(f"Index '{index_name}' created")

async def close_elasticsearch():
    if es_client:
        await es_client.close()
        logger.info("Elasticsearch connection closed")