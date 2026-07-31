"""Text embedding similarity via OpenAI text-embedding-3-small."""

from typing import List, Optional

import numpy as np
from openai import OpenAI


def compute_similarity(
    text_a: str,
    text_b: str,
    api_key: Optional[str] = None,
) -> float:
    """Compute cosine similarity between two texts using OpenAI embeddings.

    Args:
        text_a: First text.
        text_b: Second text.
        api_key: OpenAI API key. If None, reads from env.

    Returns:
        Cosine similarity in [0, 1].
    """
    client = OpenAI(api_key=api_key)

    response = client.embeddings.create(
        model="text-embedding-3-small",
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
    candidates: List[str],
    api_key: Optional[str] = None,
) -> List[float]:
    """Compute similarity of multiple candidates against a reference text.

    Args:
        reference: The reference text.
        candidates: List of candidate texts.
        api_key: OpenAI API key.

    Returns:
        List of cosine similarities, one per candidate.
    """
    if not candidates:
        return []

    client = OpenAI(api_key=api_key)
    all_texts = [reference] + candidates

    response = client.embeddings.create(
        model="text-embedding-3-small",
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
