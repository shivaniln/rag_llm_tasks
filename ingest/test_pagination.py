from app.common import ES

INDEX = "east_india_chunks_v2"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PAGE_SIZE = 5

query = {"term": {"embedding_model": MODEL}}
sort = [{"chunk_id": "asc"}]

cursor = None
all_ids = []
page_number = 0

while True:
    kwargs = {
        "index": INDEX,
        "size": PAGE_SIZE,
        "query": query,
        "sort": sort,
        "source": ["chunk_id"],
    }

    if cursor is not None:
        kwargs["search_after"] = cursor

    response = ES.search(**kwargs)
    hits = response["hits"]["hits"]

    if not hits:
        break

    page_number += 1
    page_ids = [hit["_source"]["chunk_id"] for hit in hits]
    all_ids.extend(page_ids)

    print(f"Page {page_number}: {len(page_ids)} documents")

    cursor = hits[-1]["sort"]

print("\nTotal retrieved:", len(all_ids))
print("Unique chunk IDs:", len(set(all_ids)))
print("Duplicates found:", len(all_ids) - len(set(all_ids)))
print("Pagination test:", "PASS" if len(all_ids) == len(set(all_ids)) else "FAIL")