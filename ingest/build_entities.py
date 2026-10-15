import json
from pathlib import Path
from collections import defaultdict

from ingest.normalize import normalize_name
from app.common import sid

INPUT = Path("data/entities_extracted.jsonl")
OUTPUT = Path("data/entities.jsonl")
CHUNKS = Path("data/chunks.jsonl")


def main():
    chunks = {
        item["chunk_id"]: item
        for line in CHUNKS.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for item in [json.loads(line)]
    }

    groups = defaultdict(list)

    for line in INPUT.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        mention = json.loads(line)
        key = (mention["type"], normalize_name(mention["text"]))
        groups[key].append(mention)

    entities = []

    for (entity_type, _), mentions in groups.items():
        variants = [m["text"] for m in mentions]
        canonical = max(set(variants), key=lambda name: (variants.count(name), len(name)))

        unique_mentions = {}
        for m in mentions:
            key = (m["chunk_id"], m["start"], m["end"])
            unique_mentions[key] = {
                "chunk_id": m["chunk_id"],
                "start": m["start"],
                "end": m["end"],
            }

        entity = {
            "id": sid(entity_type, normalize_name(canonical)),
            "type": entity_type,
            "name": canonical,
            "mentions": list(unique_mentions.values()),
            "attrs": {},
        }

        if entity_type == "Date":
            entity["attrs"]["date_text"] = canonical
        elif entity_type == "Quantity":
            entity["attrs"]["quantity_text"] = canonical

        entities.append(entity)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entities),
        encoding="utf-8",
    )

    print(f"Extracted mentions: {sum(len(v) for v in groups.values())}")
    print(f"Canonical entities: {len(entities)}")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
