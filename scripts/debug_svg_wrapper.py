import base64
from io import BytesIO
import random
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

# Rasterize
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

img = Image.new("RGBA", (img_w, img_h), bg_color)
draw = ImageDraw.Draw(img)

for y, row in enumerate(matrix.cells):
    for x, cell in enumerate(row):
        if cell.char != " ":
            draw.text((x * char_w, y * char_h), cell.char, font=font, fill=cell.color)

blurred = img.filter(ImageFilter.GaussianBlur(4))
img = Image.blend(img, blurred, 0.6)

buffer = BytesIO()
img.save(buffer, format="WEBP", lossless=True, quality=100, method=6)
b64_webp = base64.b64encode(buffer.getvalue()).decode('utf-8')

out_dir = r"C:\Users\flash\.gemini\antigravity\brain\e4da0dde-be9c-4219-960e-dffd9b9be5c8"

# Test A
svg_A = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img_w} {img_h}" width="{img_w}" height="{img_h}">
    <rect width="100%" height="100%" fill="{bg_color}" />
    <image href="data:image/webp;base64,{b64_webp}" width="100%" height="100%" />
</svg>"""
with open(os.path.join(out_dir, "test_A.svg"), "w", encoding="utf-8") as f:
    f.write(svg_A)

# Test B
mask_rects = []
for i in range(matrix.height):
    y_pos = i * char_h
    mask_rects.append(f'<rect x="0" y="{y_pos}" width="100%" height="{char_h+2}" fill="white" opacity="0" style="animation: reveal-row 0s linear forwards; animation-delay: 0.1s;" />')

svg_B = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img_w} {img_h}" width="{img_w}" height="{img_h}">
    <defs>
        <style>
            @keyframes reveal-row {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
        </style>
        <mask id="reveal">
            {''.join(mask_rects)}
        </mask>
    </defs>
    <rect width="100%" height="100%" fill="{bg_color}" />
    <image href="data:image/webp;base64,{b64_webp}" width="100%" height="100%" mask="url(#reveal)" />
</svg>"""
with open(os.path.join(out_dir, "test_B.svg"), "w", encoding="utf-8") as f:
    f.write(svg_B)

# Test C
svg_C = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img_w} {img_h}" width="{img_w}" height="{img_h}">
    <defs>
        <style>
            @keyframes scan-pass {{ 0% {{ transform: translateY(-40px); opacity: 0; }} 10% {{ opacity: 1; }} 90% {{ opacity: 1; }} 100% {{ transform: translateY({img_h}px); opacity: 0; }} }}
        </style>
        <linearGradient id="scan-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="rgba(255,255,255,0)" />
            <stop offset="50%" stop-color="rgba(255,255,255,0.4)" />
            <stop offset="100%" stop-color="rgba(255,255,255,0)" />
        </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="{bg_color}" />
    <image href="data:image/webp;base64,{b64_webp}" width="100%" height="100%" />
    <rect width="100%" height="40" fill="url(#scan-grad)" opacity="0" style="animation: scan-pass 0.5s ease-in-out forwards; animation-delay: 0.1s;" />
</svg>"""
with open(os.path.join(out_dir, "test_C.svg"), "w", encoding="utf-8") as f:
    f.write(svg_C)

# Test D
flash_rects = []
for i in range(matrix.height):
    y_pos = i * char_h
    flash_rects.append(f'<rect x="0" y="{y_pos}" width="100%" height="{char_h+2}" fill="rgba(255,255,255,0.25)" opacity="0" style="animation: flash-row 0.15s ease-out forwards; animation-delay: 0.1s;" />')

svg_D = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img_w} {img_h}" width="{img_w}" height="{img_h}">
    <defs>
        <style>
            @keyframes reveal-row {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
            @keyframes flash-row {{ 0% {{ opacity: 0; }} 1% {{ opacity: 1; }} 100% {{ opacity: 0; }} }}
            @keyframes scan-pass {{ 0% {{ transform: translateY(-40px); opacity: 0; }} 10% {{ opacity: 1; }} 90% {{ opacity: 1; }} 100% {{ transform: translateY({img_h}px); opacity: 0; }} }}
        </style>
        <linearGradient id="scan-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="rgba(255,255,255,0)" />
            <stop offset="50%" stop-color="rgba(255,255,255,0.4)" />
            <stop offset="100%" stop-color="rgba(255,255,255,0)" />
        </linearGradient>
        <mask id="reveal">
            {''.join(mask_rects)}
        </mask>
    </defs>
    <rect width="100%" height="100%" fill="{bg_color}" />
    <image href="data:image/webp;base64,{b64_webp}" width="100%" height="100%" mask="url(#reveal)" />
    <g id="flashes">
        {''.join(flash_rects)}
    </g>
    <rect width="100%" height="40" fill="url(#scan-grad)" opacity="0" style="animation: scan-pass 0.5s ease-in-out forwards; animation-delay: 0.5s;" />
</svg>"""
with open(os.path.join(out_dir, "test_D.svg"), "w", encoding="utf-8") as f:
    f.write(svg_D)

print("Tests generated successfully.")
