import json
from pathlib import Path

import geopandas as gpd

from ingest.normalize import normalize_name, similarity

GPKG = Path.home() / "Downloads" / "schools.gpkg"
ENTITIES = Path("data/entities.jsonl")
OUTPUT = Path("data/linked_schools.jsonl")
UNLINKED = Path("unlinked_schools.txt")
THRESHOLD = 0.85


def main():
    if not ENTITIES.exists():
        raise SystemExit(
            f"{ENTITIES} does not exist yet. Run entity extraction and "
            "entity consolidation before school linking."
        )

    schools = gpd.read_file(GPKG).to_crs("EPSG:4326")
    gazetteer = []

    for _, row in schools.iterrows():
        if not isinstance(row.get("name"), str) or not row["name"].strip():
            continue
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue

        centroid = geom.centroid
        gazetteer.append({
            "name": row["name"].strip(),
            "osm_id": str(row["osm_id"]),
            "lat": centroid.y,
            "lon": centroid.x,
        })

    entities = [
        json.loads(line)
        for line in ENTITIES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    linked, unlinked = [], []

    for entity in entities:
        if entity.get("type") != "School":
            continue

        name = entity.get("name", "").strip()
        if not name:
            unlinked.append(name)
            continue

        candidates = [
            (similarity(name, item["name"]), item)
            for item in gazetteer
        ]
        score, match = max(candidates, key=lambda pair: pair[0], default=(0, None))

        if match is not None and score >= THRESHOLD:
            entity.setdefault("attrs", {})["osm_id"] = match["osm_id"]
            entity["attrs"]["location"] = {
                "lat": match["lat"],
                "lon": match["lon"],
            }
            entity["attrs"]["match_score"] = round(score, 4)
            linked.append(entity)
        else:
            unlinked.append(name)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in linked),
        encoding="utf-8",
    )
    UNLINKED.write_text(
        "\n".join(unlinked) + ("\n" if unlinked else ""),
        encoding="utf-8",
    )

    print(f"Gazetteer schools: {len(gazetteer)}")
    print(f"School entities processed: {len(linked) + len(unlinked)}")
    print(f"Linked: {len(linked)}")
    print(f"Unlinked: {len(unlinked)}")
    print(f"Linked output: {OUTPUT}")
    print(f"Unlinked names: {UNLINKED}")


if __name__ == "__main__":
    main()
