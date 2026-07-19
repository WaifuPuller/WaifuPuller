import base64
from io import BytesIO
import os
import sys

sys.path.append(os.path.abspath('scripts'))
from utils.config_parser import load_all_configs
from preprocessing.image_processor import ImageProcessor
from ascii.generator import ASCIIGenerator
from PIL import Image, ImageDraw, ImageFont, ImageFilter

configs = load_all_configs()
img_path = configs.get("portrait", {}).get("source", "")
processor = ImageProcessor(configs)
img_source = processor.process(img_path)
generator = ASCIIGenerator(configs)
matrix = generator.generate(img_source)

bg_color = configs.get("theme", {}).get("colors", {}).get("background", "#121212")

font_path = "C:\\Windows\\Fonts\\consola.ttf"
if not os.path.exists(font_path):
    font_path = "C:\\Windows\\Fonts\\cour.ttf"
font = ImageFont.truetype(font_path, 14)
left, top, right, bottom = font.getbbox("@")
char_w = right - left
char_h = bottom - top
char_w = max(1, int(char_w * 1.0))
char_h = max(1, int(char_h * 1.2))

img_w = matrix.width * char_w
img_h = matrix.height * char_h

# 1. Original Raster (no blur/bloom)
img = Image.new("RGBA", (img_w, img_h), bg_color)
draw = ImageDraw.Draw(img)

for y, row in enumerate(matrix.cells):
    for x, cell in enumerate(row):
        if cell.char != " ":
            draw.text((x * char_w, y * char_h), cell.char, font=font, fill=cell.color)

out_dir = r"C:\Users\flash\.gemini\antigravity\brain\e4da0dde-be9c-4219-960e-dffd9b9be5c8"
img.save(os.path.join(out_dir, "step1_raw_raster.png"))

# 2. Gaussian Blur
blurred = img.filter(ImageFilter.GaussianBlur(4))
blurred.save(os.path.join(out_dir, "step2_gaussian_blur.png"))

# 3. Image.blend (Bloom)
img_bloom = Image.blend(img, blurred, 0.6)
img_bloom.save(os.path.join(out_dir, "step3_blend_bloom.png"))

# 4. Final WebP (lossless)
img_bloom.save(os.path.join(out_dir, "step4_final.webp"), format="WEBP", lossless=True, quality=100, method=6)

# Test A Untouched (using step 1 raw raster)
buffer = BytesIO()
img.save(buffer, format="WEBP", lossless=True, quality=100, method=6)
b64_webp = base64.b64encode(buffer.getvalue()).decode('utf-8')

svg_A = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img_w} {img_h}" width="{img_w}" height="{img_h}">
    <rect width="100%" height="100%" fill="{bg_color}" />
    <image href="data:image/webp;base64,{b64_webp}" width="100%" height="100%" />
</svg>"""
with open(os.path.join(out_dir, "test_A_untouched.svg"), "w", encoding="utf-8") as f:
    f.write(svg_A)

print("Raster diagnostics generated successfully.")
