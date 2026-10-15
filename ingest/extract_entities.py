import json
import time
from pathlib import Path

from ingest.baseline_extractor import extract_entities
from ingest.llm_extractor import llm_extract

CHUNKS = Path("data/chunks.jsonl")
OUTPUT = Path("data/entities_extracted.jsonl")


def main():
    if not CHUNKS.exists():
        raise SystemExit(f"Missing input: {CHUNKS}")

    chunks = [
        json.loads(line)
        for line in CHUNKS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    results = []
    baseline_seconds = 0.0
    llm_seconds = 0.0

    for chunk in chunks:
        text = chunk["text"]
        chunk_id = chunk["chunk_id"]

        start = time.perf_counter()
        baseline = extract_entities(text)
        baseline_seconds += time.perf_counter() - start

        start = time.perf_counter()
        try:
            llm_entities = llm_extract(text, temperature=0, seed=0)
        except ValueError as exc:
            print(f"LLM extraction failed for chunk {chunk_id}: {exc}")
            llm_entities = []
        llm_seconds += time.perf_counter() - start

        for method, spans in (
            ("baseline", baseline),
            ("llm", llm_entities),
        ):
            for entity_type, start_pos, end_pos, mention in spans:
                results.append({
                    "chunk_id": chunk_id,
                    "method": method,
                    "type": entity_type,
                    "text": mention,
                    "start": start_pos,
                    "end": end_pos,
                })

    OUTPUT.write_text(
        "".join(
            json.dumps(item, ensure_ascii=False) + "\n"
            for item in results
        ),
        encoding="utf-8",
    )

    print(f"Chunks processed: {len(chunks)}")
    print(f"Baseline mentions: {sum(r['method'] == 'baseline' for r in results)}")
    print(f"LLM mentions: {sum(r['method'] == 'llm' for r in results)}")
    print(f"Baseline time: {baseline_seconds:.2f}s")
    print(f"LLM time: {llm_seconds:.2f}s")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
