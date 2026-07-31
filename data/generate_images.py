"""Generate synthetic test images for LookAgain.

This script creates simple but semantically meaningful placeholder images
so that the built-in test cases can run without requiring real photographs.
The images use bold colors and text labels to make them visually
distinguishable for VLM evaluation.

Run:
    python data/generate_images.py
"""

import os
from PIL import Image, ImageDraw, ImageFont


DATA_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_SIZE = (512, 512)

# Map filename stem -> (background_color, text_label, text_color)
WRONG_IMAGES = {
    "cat_correct": ("#FFA500", "CAT", "#000000"),
    "dog_wrong": ("#8B4513", "DOG", "#FFFFFF"),
    "bird_wrong": ("#87CEEB", "BIRD", "#000000"),
    "car_wrong": ("#708090", "CAR", "#FFFFFF"),
    "cat_other": ("#FFD700", "CAT", "#000000"),
    "apple_correct": ("#FF0000", "APPLE", "#FFFFFF"),
    "banana_wrong": ("#FFFF00", "BANANA", "#000000"),
    "orange_wrong": ("#FFA500", "ORANGE", "#000000"),
    "tomato_wrong": ("#DC143C", "TOMATO", "#FFFFFF"),
    "apple_green": ("#32CD32", "APPLE", "#000000"),
    "bicycle_correct": ("#00CED1", "BICYCLE", "#000000"),
    "motorcycle_wrong": ("#FF6347", "MOTORCYCLE", "#FFFFFF"),
    "bicycle_other": ("#20B2AA", "BICYCLE", "#000000"),
    "boat_wrong": ("#4682B4", "BOAT", "#FFFFFF"),
    "sunset_correct": ("#FF4500", "SUNSET", "#FFFFFF"),
    "noon_wrong": ("#87CEFA", "NOON", "#000000"),
    "night_wrong": ("#191970", "NIGHT", "#FFFFFF"),
    "dawn_wrong": ("#DDA0DD", "DAWN", "#000000"),
    "rainy_correct": ("#5F9EA0", "RAINY", "#FFFFFF"),
    "sunny_wrong": ("#FFD700", "SUNNY", "#000000"),
    "snowy_wrong": ("#F0F8FF", "SNOWY", "#000000"),
    "foggy_wrong": ("#D3D3D3", "FOGGY", "#000000"),
    "three_people_correct": ("#98FB98", "3 PEOPLE", "#000000"),
    "one_person_wrong": ("#E0FFFF", "1 PERSON", "#000000"),
    "five_people_wrong": ("#F5DEB3", "5 PEOPLE", "#000000"),
    "no_people_wrong": ("#DCDCDC", "NO PEOPLE", "#000000"),
    "two_apples_correct": ("#FF69B4", "2 APPLES", "#FFFFFF"),
    "four_apples_wrong": ("#BA55D3", "4 APPLES", "#FFFFFF"),
    "zero_apples_wrong": ("#F5F5DC", "0 APPLES", "#000000"),
    "six_apples_wrong": ("#9370DB", "6 APPLES", "#FFFFFF"),
    "red_car_correct": ("#FF0000", "RED CAR", "#FFFFFF"),
    "blue_car_wrong": ("#0000FF", "BLUE CAR", "#FFFFFF"),
    "white_car_wrong": ("#FFFFFF", "WHITE CAR", "#000000"),
    "green_dress_correct": ("#008000", "GREEN DRESS", "#FFFFFF"),
    "yellow_dress_wrong": ("#FFFF00", "YELLOW DRESS", "#000000"),
    "black_dress_wrong": ("#000000", "BLACK DRESS", "#FFFFFF"),
    "green_shirt_wrong": ("#90EE90", "GREEN SHIRT", "#000000"),
    "cup_left_correct": ("#ADD8E6", "CUP LEFT", "#000000"),
    "cup_right_wrong": ("#FFB6C1", "CUP RIGHT", "#000000"),
    "cup_center_wrong": ("#DDA0DD", "CUP CENTER", "#000000"),
    "no_cup_wrong": ("#F0F0F0", "NO CUP", "#000000"),
    "sign_stop_correct": ("#FF0000", "STOP", "#FFFFFF"),
    "sign_yield_wrong": ("#FFFF00", "YIELD", "#000000"),
    "sign_speed_wrong": ("#FFFFFF", "SPEED 50", "#000000"),
    "no_sign_wrong": ("#A9A9A9", "NO SIGN", "#FFFFFF"),
    "brand_coke_correct": ("#DC143C", "COKE", "#FFFFFF"),
    "brand_pepsi_wrong": ("#000080", "PEPSI", "#FFFFFF"),
    "brand_water_wrong": ("#00BFFF", "WATER", "#FFFFFF"),
    "no_brand_wrong": ("#D3D3D3", "NO BRAND", "#000000"),
    "running_correct": ("#7CFC00", "RUNNING", "#000000"),
    "sitting_wrong": ("#D2691E", "SITTING", "#FFFFFF"),
    "jumping_wrong": ("#1E90FF", "JUMPING", "#FFFFFF"),
    "standing_wrong": ("#A0522D", "STANDING", "#FFFFFF"),
    "soccer_correct": ("#FFFFFF", "SOCCER", "#000000"),
    "basketball_wrong": ("#FF8C00", "BASKETBALL", "#000000"),
    "tennis_wrong": ("#ADFF2F", "TENNIS", "#000000"),
    "swimming_wrong": ("#00CED1", "SWIMMING", "#000000"),
}

CORRUPTION_IMAGES = {
    "cat": ("#FFA500", "CAT"),
    "apple": ("#FF0000", "APPLE"),
    "bicycle": ("#00CED1", "BICYCLE"),
    "beach_sunny": ("#87CEEB", "BEACH"),
    "city_street": ("#808080", "CITY"),
    "group_photo": ("#98FB98", "GROUP"),
    "table_setting": ("#F5DEB3", "TABLE"),
    "street_sign": ("#FF0000", "STOP"),
    "book_cover": ("#4B0082", "BOOK"),
    "near_far": ("#DDA0DD", "NEAR/FAR"),
    "left_right": ("#FFD700", "LEFT/RIGHT"),
    "colored_objects": ("#FF69B4", "OBJECTS"),
}

BIAS_IMAGES = {
    "dog_golden": ("#FFD700", "DOG"),
    "banana": ("#FFFF00", "BANANA"),
    "empty_whiteboard": ("#FFFFFF", "BLANK"),
    "noon_landscape": ("#87CEFA", "DAY"),
    "red_traffic_light": ("#FF0000", "RED LIGHT"),
    "three_people": ("#98FB98", "3 PEOPLE"),
    "car_right_side": ("#FFB6C1", "CAR RIGHT"),
    "document_public": ("#90EE90", "PUBLIC"),
    "eagle": ("#8B4513", "EAGLE"),
    "sunflower": ("#FFD700", "SUNFLOWER"),
    "sign_60kmh": ("#FFFFFF", "60 KM/H"),
    "starry_night": ("#191970", "STARRY NIGHT"),
}


def _get_font(size: int):
    """Try to load a usable font; fall back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        if path and os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def create_image(filename: str, bg_color: str, label: str, text_color: str = "#FFFFFF"):
    """Create a single synthetic image."""
    img = Image.new("RGB", IMAGE_SIZE, bg_color)
    draw = ImageDraw.Draw(img)

    # Draw a simple shape
    draw.rectangle([64, 64, 448, 448], outline=text_color, width=8)

    # Draw label
    font = _get_font(64)
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (IMAGE_SIZE[0] - text_w) // 2
    y = (IMAGE_SIZE[1] - text_h) // 2
    draw.text((x, y), label, fill=text_color, font=font)

    img.save(filename)


def generate_all():
    """Generate all required synthetic images."""
    dirs = [
        os.path.join(DATA_DIR, "images", "wrong"),
        os.path.join(DATA_DIR, "images", "corruption"),
        os.path.join(DATA_DIR, "images", "bias"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    generated = 0
    for name, (bg, label, *rest) in WRONG_IMAGES.items():
        text_color = rest[0] if rest else "#FFFFFF"
        path = os.path.join(DATA_DIR, "images", "wrong", f"{name}.jpg")
        create_image(path, bg, label, text_color)
        generated += 1

    for name, (bg, label) in CORRUPTION_IMAGES.items():
        text_color = "#FFFFFF" if bg != "#FFFFFF" else "#000000"
        path = os.path.join(DATA_DIR, "images", "corruption", f"{name}.jpg")
        create_image(path, bg, label, text_color)
        generated += 1

    for name, (bg, label) in BIAS_IMAGES.items():
        text_color = "#FFFFFF" if bg != "#FFFFFF" else "#000000"
        path = os.path.join(DATA_DIR, "images", "bias", f"{name}.jpg")
        create_image(path, bg, label, text_color)
        generated += 1

    print(f"Generated {generated} synthetic test images in {os.path.join(DATA_DIR, 'images')}")


if __name__ == "__main__":
    generate_all()
