
import os
import hashlib
import requests
import numpy as np
from elasticsearch import Elasticsearch

ES = Elasticsearch(
    os.environ.get(
        "ES_URL",
        os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
    ),
    api_key=os.environ.get("RAG_ES_API_KEY")
)

OLLAMA = "http://localhost:11434"
LLM = os.environ.get("LLM_MODEL", "qwen2.5:3b")


def sid(*parts):
    """Generate a deterministic ID from the supplied values."""
    return hashlib.sha1(
        "|".join(map(str, parts)).encode()
    ).hexdigest()[:20]


def llm(
    prompt,
    system=None,
    temperature=0,
    seed=0,
    fmt=None,
    num_predict=512,
    top_p=0.9,
    top_k=40
):
    body = {
        "model": LLM,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "seed": seed,
            "top_p": top_p,
            "top_k": top_k,
            "num_predict": num_predict
        }
    }

    if system:
        body["system"] = system

    if fmt:
        body["format"] = fmt

    response = requests.post(
        f"{OLLAMA}/api/generate",
        json=body,
        timeout=300
    )
    response.raise_for_status()
    result = response.json()

    return result["response"], result
