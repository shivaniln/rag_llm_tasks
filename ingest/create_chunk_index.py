from app.common import ES

INDEX = "east_india_chunks_v2"

mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "english_analyzer": {
                    "type": "english"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "chunk_id": {"type": "keyword"},
            "doc": {"type": "keyword"},
            "page": {"type": "integer"},
            "char_start": {"type": "integer"},
            "char_end": {"type": "integer"},
            "text": {
                "type": "text",
                "analyzer": "english_analyzer"
            },
            "embedding_model": {"type": "keyword"},
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine",
                "index_options": {
                    "type": "hnsw",
                    "m": 16,
                    "ef_construction": 100
                }
            },
            "category": {
                "type": "keyword"
            },
            "name": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "location": {
                "properties": {
                    "lat": {"type": "float"},
                    "lon": {"type": "float"}
                }
            }
        }
    }
}

if ES.indices.exists(index=INDEX):
    current = ES.indices.get_mapping(index=INDEX)[INDEX]["mappings"]["properties"]

    required = {"chunk_id", "doc", "page", "char_start", "char_end",
                "text", "embedding_model", "embedding"}

    missing = required - set(current)

    if missing:
        raise SystemExit(
            f"Index already exists with an incomplete mapping: {sorted(missing)}. "
            "Existing index was not modified. Create a versioned index or reindex "
            "after preserving existing data."
        )

    print(f"Index '{INDEX}' already has the required fields.")
else:
    ES.indices.create(index=INDEX, **mapping)
    print(f"Created index '{INDEX}' with a 384-dimensional cosine vector mapping.")