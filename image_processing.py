from PIL import Image
from pathlib import Path
import os


def load_downscale_image(path: str, target_size=(128, 128)):
    img = Image.open(path)
    img = img.resize(target_size, Image.ANTIALIAS)
    return img


def save_image(img: Image, path: str):
    create_full_path(path)
    img.save(path, optimize=True, quality=95)


def create_full_path(path: str):
    path = Path(path)
    path = path.parents[0] if path.is_file() else path
    path.mkdir(parents=True, exist_ok=True)


def delete_image(path: str):
    if Path(path).exists():
        os.remove(path)


def get_image(path: str):
    if Path(path).exists():
        img = Image.open(path)
        return img
    return None
