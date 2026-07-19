import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import sys

sys.path.append(os.path.abspath('scripts'))
from utils.config_parser import load_all_configs
from preprocessing.image_processor import ImageProcessor
from ascii.generator import ASCIIGenerator, ASCIICell

configs = load_all_configs()
img_path = configs.get("portrait", {}).get("source", "")
processor = ImageProcessor(configs)

# 1. Original Preprocessing Image
img_source = processor.process(img_path)
out_dir = r"C:\Users\flash\.gemini\antigravity\brain\e4da0dde-be9c-4219-960e-dffd9b9be5c8"
img_source.save(os.path.join(out_dir, "step1_preprocessed.png"))

# Hook into ASCIIGenerator to extract intermediate maps
generator = ASCIIGenerator(configs)

# We basically run the generator logic manually here to extract the intermediate maps
img = img_source.convert("RGBA")
img_w, img_h = img.size
target_h = int((img_h / img_w) * generator.output_width * generator.char_aspect_ratio)

small_img = img.resize((generator.output_width, target_h), Image.Resampling.BOX)
pixels = np.array(small_img, dtype=np.float32)

char_len = len(generator.charset)
lum_map_raw = np.zeros((target_h, generator.output_width), dtype=np.float32)

for y in range(target_h):
    for x in range(generator.output_width):
        r, g, b, a = pixels[y, x]
        lum_map_raw[y, x] = generator._luminance(r, g, b)

# 2. Brightness Map (Before dithering)
lum_img = Image.fromarray(np.clip(lum_map_raw, 0, 255).astype(np.uint8), mode="L")
lum_img.save(os.path.join(out_dir, "step2_brightness_map.png"))

# Run dithering
lum_map_dithered = lum_map_raw.copy()
if generator.dithering == "floyd-steinberg":
    for y in range(target_h):
        for x in range(generator.output_width):
            if pixels[y, x, 3] == 0: continue
            old_lum = lum_map_dithered[y, x]
            idx = int(np.clip((old_lum / 255.0) * (char_len - 1), 0, char_len - 1))
            new_lum = (idx / max(1, (char_len - 1))) * 255.0
            error = old_lum - new_lum
            lum_map_dithered[y, x] = new_lum
            
            if x + 1 < generator.output_width: lum_map_dithered[y, x+1] += error * 7/16
            if y + 1 < target_h:
                if x > 0: lum_map_dithered[y+1, x-1] += error * 3/16
                lum_map_dithered[y+1, x] += error * 5/16
                if x + 1 < generator.output_width: lum_map_dithered[y+1, x+1] += error * 1/16

# 3. Character density map
density_img = Image.new("L", (generator.output_width, target_h))
density_pixels = density_img.load()
for y in range(target_h):
    for x in range(generator.output_width):
        lum = np.clip(lum_map_dithered[y, x], 0, 255)
        idx = int((lum / 255.0) * (char_len - 1))
        # Map char index to 0-255
        val = int((idx / (char_len - 1)) * 255.0) if char_len > 1 else 255
        density_pixels[x, y] = val

density_img.save(os.path.join(out_dir, "step3_character_density.png"))

# Create Matrix
cells = []
for y in range(target_h):
    row = []
    for x in range(generator.output_width):
        r, g, b, a = pixels[y, x]
        if a == 0:
            row.append(ASCIICell(" ", (0,0,0,0)))
            continue
        lum = np.clip(lum_map_dithered[y, x], 0, 255)
        idx = int((lum / 255.0) * (char_len - 1))
        row.append(ASCIICell(generator.charset[idx], (int(r), int(g), int(b), int(a))))
    cells.append(row)
    
matrix = generator.generate(img_source)

# 4. Colored ASCII matrix before rasterization (Pure block colors, bypassing fonts entirely)
# Render each cell as a 4x4 pixel block representing its exact internal color assignment
block_w = 4
block_h = 4
bg_color = configs.get("theme", {}).get("colors", {}).get("background", "#121212")
matrix_img = Image.new("RGBA", (generator.output_width * block_w, target_h * block_h), bg_color)
matrix_draw = ImageDraw.Draw(matrix_img)

for y, row in enumerate(matrix.cells):
    for x, cell in enumerate(row):
        if cell.char != " ":
            matrix_draw.rectangle([x * block_w, y * block_h, (x+1) * block_w - 1, (y+1) * block_h - 1], fill=cell.color)
            
matrix_img.save(os.path.join(out_dir, "step4_matrix_colors.png"))

# 5. Final Raster
from ascii.raster_renderer import RasterRenderer
renderer = RasterRenderer(configs)
renderer.render(matrix, os.path.join(out_dir, "step5_final_raster.svg"))

# Also save an intermediate raw raster for comparison natively
img_w = matrix.width * 8
img_h = matrix.height * 9
raw_raster = Image.new("RGBA", (img_w, img_h), bg_color)
raw_draw = ImageDraw.Draw(raw_raster)
for y, row in enumerate(matrix.cells):
    for x, cell in enumerate(row):
        if cell.char != " ":
            raw_draw.text((x * 8, y * 9), cell.char, font=renderer.font, fill=cell.color)
raw_raster.save(os.path.join(out_dir, "step5_raw_font_raster.png"))

print("ASCII debugging complete.")
