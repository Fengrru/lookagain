"""Image corruption utilities for Corruption test scenario."""

import os
import random
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter


def generate_corruptions(image: Image.Image) -> dict[str, Image.Image]:
    """Generate multiple degraded versions of an image.

    Args:
        image: PIL Image in RGB mode.

    Returns:
        dict mapping corruption name to corrupted PIL Image.
    """
    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    w, h = image.size

    corruptions = {}

    # Gaussian blur at varying intensities
    corruptions["blur_light"] = image.filter(ImageFilter.GaussianBlur(radius=2))
    corruptions["blur_medium"] = image.filter(ImageFilter.GaussianBlur(radius=4))
    corruptions["blur_heavy"] = image.filter(ImageFilter.GaussianBlur(radius=8))

    # Random occlusion: overlay black rectangles over 30% of the image
    corruptions["occlusion"] = _add_random_occlusion(image.copy(), ratio=0.3)

    # Center occlusion: black out the center 30% region
    corruptions["center_occlusion"] = _add_center_occlusion(image.copy(), ratio=0.3)

    # Downscale then upscale (loss of detail)
    corruptions["low_res_50"] = _downscale_upscale(image, scale=0.5)
    corruptions["low_res_25"] = _downscale_upscale(image, scale=0.25)

    return corruptions


def _add_random_occlusion(image: Image.Image, ratio: float = 0.3) -> Image.Image:
    """Overlay random black rectangles covering `ratio` fraction of image area."""
    w, h = image.size
    area = w * h
    target_area = int(area * ratio)

    draw = ImageDraw.Draw(image)
    covered = 0

    while covered < target_area:
        bw = random.randint(w // 8, w // 3)
        bh = random.randint(h // 8, h // 3)
        bx = random.randint(0, max(0, w - bw))
        by = random.randint(0, max(0, h - bh))
        draw.rectangle([bx, by, bx + bw, by + bh], fill="black")
        covered += bw * bh

    return image


def _add_center_occlusion(image: Image.Image, ratio: float = 0.3) -> Image.Image:
    """Black out the center region of the image."""
    w, h = image.size
    cw = int(w * ratio**0.5)
    ch = int(h * ratio**0.5)
    cx = (w - cw) // 2
    cy = (h - ch) // 2

    draw = ImageDraw.Draw(image)
    draw.rectangle([cx, cy, cx + cw, cy + ch], fill="black")
    return image


def _downscale_upscale(image: Image.Image, scale: float) -> Image.Image:
    """Downscale image by `scale`, then upscale back to original size."""
    w, h = image.size
    small = image.resize((int(w * scale), int(h * scale)), Image.BILINEAR)
    return small.resize((w, h), Image.BILINEAR)


def load_image(path: str) -> Optional[Image.Image]:
    """Load an image from path, return None on failure.

    Args:
        path: Path to image file.

    Returns:
        PIL Image in RGB mode, or None if loading fails.
    """
    if not path or not os.path.exists(path):
        return None
    try:
        return Image.open(path).convert("RGB")
    except Exception:
        return None
