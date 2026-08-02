"""Text embedding similarity via OpenAI text-embedding-3-small.

Supports configurable model name and API key via EmbeddingConfig.
Falls back to environment variables when no explicit config is provided.
"""

from typing import Optional

import numpy as np
from openai import OpenAI

# Client cache to avoid creating new clients for each call
# Key: (api_key, base_url) tuple
_clients = {}

# Default embedding model
_DEFAULT_MODEL = "text-embedding-3-small"


def _get_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> OpenAI:
    """Get or create an OpenAI client with caching.

    Args:
        api_key: Optional API key. If None, reads from env.
        base_url: Optional base URL for custom endpoints.

    Returns:
        Cached OpenAI client instance.
    """
    cache_key = (api_key or "default", base_url or "default")
    if cache_key not in _clients:
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        _clients[cache_key] = OpenAI(**kwargs)
    return _clients[cache_key]


def compute_similarity(
    text_a: str,
    text_b: str,
    api_key: Optional[str] = None,
    model: str = _DEFAULT_MODEL,
    base_url: Optional[str] = None,
) -> float:
    """Compute cosine similarity between two texts using OpenAI embeddings.

    Args:
        text_a: First text.
        text_b: Second text.
        api_key: OpenAI API key. If None, reads from env.
        model: Embedding model name. Defaults to text-embedding-3-small.
        base_url: Optional base URL for custom endpoints.

    Returns:
        Cosine similarity in [0, 1].
    """
    client = _get_client(api_key, base_url)

    response = client.embeddings.create(
        model=model,
        input=[text_a, text_b],
    )
    emb_a = np.array(response.data[0].embedding)
    emb_b = np.array(response.data[1].embedding)

    # Cosine similarity
    dot = np.dot(emb_a, emb_b)
    norm_a = np.linalg.norm(emb_a)
    norm_b = np.linalg.norm(emb_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


def compute_similarities(
    reference: str,
    candidates: list[str],
    api_key: Optional[str] = None,
    model: str = _DEFAULT_MODEL,
    base_url: Optional[str] = None,
) -> list[float]:
    """Compute similarity of multiple candidates against a reference text.

    Args:
        reference: The reference text.
        candidates: List of candidate texts.
        api_key: OpenAI API key.
        model: Embedding model name. Defaults to text-embedding-3-small.
        base_url: Optional base URL for custom endpoints.

    Returns:
        List of cosine similarities, one per candidate.
    """
    if not candidates:
        return []

    client = _get_client(api_key, base_url)
    all_texts = [reference] + candidates

    response = client.embeddings.create(
        model=model,
        input=all_texts,
    )
    embeddings = [np.array(d.embedding) for d in response.data]
    ref_emb = embeddings[0]
    ref_norm = np.linalg.norm(ref_emb)

    if ref_norm == 0:
        return [0.0] * len(candidates)

    similarities = []
    for cand_emb in embeddings[1:]:
        cand_norm = np.linalg.norm(cand_emb)
        if cand_norm == 0:
            similarities.append(0.0)
        else:
            sim = float(np.dot(ref_emb, cand_emb) / (ref_norm * cand_norm))
            similarities.append(sim)

    return similarities
