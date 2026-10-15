
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.common import sid

def pages(path):
    p = pathlib.Path(path)

    if p.suffix.lower() == ".pdf":
        import fitz
        with fitz.open(p) as pdf:
            return [
                (i + 1, page.get_text())
                for i, page in enumerate(pdf)
            ]

    if p.suffix.lower() in {".md", ".txt"}:
        return [(1, p.read_text(encoding="utf-8"))]

    raise ValueError(f"Unsupported file type: {p.suffix}")


def chunk_doc(path, size=800, overlap=150):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > overlap >= 0")

    output = []

    for page_no, text in pages(path):
        start = 0

        while start < len(text):
            end = min(start + size, len(text))

            # Prefer a sentence boundary in the second half of the window.
            if end < len(text):
                cut = text.rfind(". ", start + size // 2, end)
                if cut != -1:
                    end = cut + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                output.append({
                    "chunk_id": sid(pathlib.Path(path).name, page_no, start, end),
                    "doc": pathlib.Path(path).name,
                    "page": page_no,
                    "char_start": start,
                    "char_end": end,
                    "text": chunk_text
                })

            if end >= len(text):
                break

            start = end - overlap

    return output


def save_chunks(paths, output_path="data/chunks.jsonl"):
    all_chunks = []

    for path in paths:
        all_chunks.extend(chunk_doc(path))

    destination = pathlib.Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as file:
        for chunk in all_chunks:
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"Saved {len(all_chunks)} chunks to {destination}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python ingest/chunk.py <file1.pdf|file1.md|file1.txt> [...]"
        )

    save_chunks(sys.argv[1:])
