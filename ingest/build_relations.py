import json
from pathlib import Path
from ingest.relations import build_near_relations

output = Path("data/relations.jsonl")
relations = build_near_relations()

output.write_text(
    "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in relations),
    encoding="utf-8",
)

print("Relations saved:", len(relations))
print("Output:", output)
