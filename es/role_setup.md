
# Elasticsearch `rag_app` Role Setup

## Purpose
Restrict the GeoAssistant application to read and write access on three designated indices.

## Role JSON

```json
{
  "indices": [
    {
      "names": [
        "east_india_chunks",
        "east_india_entities",
        "east_india_relations"
      ],
      "privileges": ["read", "write"]
    }
  ]
}
```

## Security Notes
- The role has no cluster privileges.
- The role cannot create indices; indices are created separately by an administrator.
- The application authenticates using a restricted API key.
- The API key is stored locally in `.env`, which is excluded from Git.
- The application must not use the `elastic` administrator account.
