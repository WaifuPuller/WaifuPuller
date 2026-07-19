import numpy as np
from PIL import Image
from typing import Dict, Any, List, Tuple
from utils.logger import setup_logger

logger = setup_logger("ascii_generator")

class ASCIICell:
    def __init__(self, char: str, color: Tuple[int, int, int, int]):
        self.char = char
        self.color = color

class ASCIIMatrix:
    def __init__(self, cells: List[List[ASCIICell]], width: int, height: int):
        self.cells = cells
        self.width = width
        self.height = height

class ASCIIGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.portrait_config = config.get("portrait", {})
        
        # We lock the preset mapped from the config
        preset_name = self.portrait_config.get("preset", "artistic")
        presets = {
            "ultra_dense": "@%#*+=-:. ",
            "dense": "█▓▒░ ",
            "balanced": "WMB8&%#*+=-:. ",
            "minimal": "10 ",
            "artistic": "WMB8&%#*+=-:. ",
            "shading": "█▓▒░ "
        }
        self.charset = presets.get(preset_name, presets["artistic"])
            
        self.output_width = self.portrait_config.get("width", 240)
        self.char_aspect_ratio = 0.5
        self.dithering = self.portrait_config.get("dithering", "floyd-steinberg").lower()

    def _luminance(self, r: int, g: int, b: int) -> float:
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def generate(self, img: Image.Image) -> ASCIIMatrix:
        logger.info(f"Generating ASCII matrix with width {self.output_width} chars using '{self.portrait_config.get('preset')}' preset")
        
        if img.mode != "RGBA":
            img = img.convert("RGBA")
            
        img_w, img_h = img.size
        target_h = int((img_h / img_w) * self.output_width * self.char_aspect_ratio)
        
        logger.debug(f"Scaling image for ASCII sampling to {self.output_width}x{target_h}")
        small_img = img.resize((self.output_width, target_h), Image.Resampling.BOX)
        pixels = np.array(small_img, dtype=np.float32)
        
        cells = []
        char_len = len(self.charset)
        
        lum_map = np.zeros((target_h, self.output_width), dtype=np.float32)
        for y in range(target_h):
            for x in range(self.output_width):
                r, g, b, a = pixels[y, x]
                lum_map[y, x] = self._luminance(r, g, b)
                
        if self.dithering == "floyd-steinberg":
            for y in range(target_h):
                for x in range(self.output_width):
                    if pixels[y, x, 3] == 0: continue
                    old_lum = lum_map[y, x]
                    idx = int(np.clip((old_lum / 255.0) * (char_len - 1), 0, char_len - 1))
                    new_lum = (idx / max(1, (char_len - 1))) * 255.0
                    error = old_lum - new_lum
                    lum_map[y, x] = new_lum
                    
                    if x + 1 < self.output_width:
                        lum_map[y, x+1] += error * 7/16
                    if y + 1 < target_h:
                        if x > 0:
                            lum_map[y+1, x-1] += error * 3/16
                        lum_map[y+1, x] += error * 5/16
                        if x + 1 < self.output_width:
                            lum_map[y+1, x+1] += error * 1/16
                            
        for y in range(target_h):
            row = []
            for x in range(self.output_width):
                r, g, b, a = pixels[y, x]
                if a == 0:
                    row.append(ASCIICell(" ", (0,0,0,0)))
                    continue
                    
                lum = np.clip(lum_map[y, x], 0, 255)
                idx = int((lum / 255.0) * (char_len - 1))
                char = self.charset[idx]
                
                row.append(ASCIICell(char, (int(r), int(g), int(b), int(a))))
            cells.append(row)
            
        return ASCIIMatrix(cells, self.output_width, target_h)
