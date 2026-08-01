"""Utility functions: image processing, embedding similarity."""

from .embedding import compute_similarity
from .image_utils import generate_corruptions

__all__ = ["generate_corruptions", "compute_similarity"]
