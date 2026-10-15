ENTITY_TYPES = [
    "School",
    "Board",
    "Circular",
    "Rule",
    "Locality",
    "Road",
    "Date",
    "Quantity",
]

ENTITY_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "type": {"type": "string", "enum": ENTITY_TYPES},
        "name": {"type": "string"},
        "mentions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "chunk_id": {"type": "string"},
                    "start": {"type": "integer"},
                    "end": {"type": "integer"},
                },
                "required": ["chunk_id", "start", "end"],
            },
        },
        "attrs": {"type": "object"},
    },
    "required": ["id", "type", "name", "mentions", "attrs"],
}
