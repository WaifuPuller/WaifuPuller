import os
from pathlib import Path
from typing import Dict, Any
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from utils.logger import setup_logger

logger = setup_logger("preprocessing")

class ImageProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.portrait_config = config.get("portrait", {})
        self.config = self.portrait_config.get("preprocessing", {})
        
    def process(self, image_path: str) -> Image.Image:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        logger.info(f"Loading image from {image_path}")
        img = Image.open(path)
        img.load()
        
        # Orientation
        img = ImageOps.exif_transpose(img)
        
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Auto crop to trim transparent padding
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            
        # Optional Resize
        target_w = 800
        if img.width > target_w:
            ratio = target_w / img.width
            img = img.resize((target_w, int(img.height * ratio)), Image.Resampling.LANCZOS)
            
        # Enhancements
        if self.config.get("clahe", True):
            img = img.filter(ImageFilter.UnsharpMask(radius=15, percent=200, threshold=3))
            
        if self.config.get("adaptive_edge_enhancement", True):
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            
        return img
