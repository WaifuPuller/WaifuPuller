import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Dict, Any
from .generator import ASCIIMatrix
from utils.logger import setup_logger

logger = setup_logger("raster_renderer")

class RasterRenderer:
    def __init__(self, config: Dict[str, Any]):
        self.portrait_config = config.get("portrait", {})
        self.theme = config.get("theme", {})
        self.colors = self.theme.get("colors", {})
        self.bg_color = self.colors.get("background", "#121212")
        
        self.font_path = "C:\\Windows\\Fonts\\consolab.ttf"
        if not os.path.exists(self.font_path):
            self.font_path = "C:\\Windows\\Fonts\\courbd.ttf"
            
        self.font_size = 15
        try:
            self.font = ImageFont.truetype(self.font_path, self.font_size)
        except Exception:
            self.font = ImageFont.load_default()
            
        self.bloom = True
        self.bloom_radius = 3
        self.bloom_intensity = 0.4

    def render(self, matrix: ASCIIMatrix, out_path: str):
        # We use a standard char to get bounding box
        left, top, right, bottom = self.font.getbbox("@")
        char_w = right - left
        char_h = bottom - top
        
        # Less tracking to pack characters tighter and increase brightness
        char_w = max(1, int(char_w * 0.95))
        char_h = max(1, int(char_h * 1.0))
        
        img_w = matrix.width * char_w
        img_h = matrix.height * char_h
        
        logger.info(f"Rendering Raster ASCII ({img_w}x{img_h}) to {out_path}")
        
        img = Image.new("RGBA", (img_w, img_h), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        for y, row in enumerate(matrix.cells):
            for x, cell in enumerate(row):
                if cell.char != " ":
                    # Draw text 3 times to completely eliminate sub-pixel antialiasing dimming 
                    # and ensure maximum saturation/brightness of the character strokes.
                    draw.text((x * char_w, y * char_h), cell.char, font=self.font, fill=cell.color)
                    draw.text((x * char_w, y * char_h), cell.char, font=self.font, fill=cell.color)
                    draw.text((x * char_w, y * char_h), cell.char, font=self.font, fill=cell.color)
                    
        if self.bloom:
            from PIL import ImageChops
            blurred = img.filter(ImageFilter.GaussianBlur(self.bloom_radius))
            # Use Additive blending (Screen) instead of averaging (blend) to preserve and boost peak brightness
            img = ImageChops.screen(img, blurred)
            
        import base64
        from io import BytesIO
        import random

        # WebP lossless to preserve exact colors and avoid chroma subsampling on reds
        buffer = BytesIO()
        img.save(buffer, format="WEBP", lossless=True, quality=100, method=6)
        b64_webp = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # SVG Construction
        target_reveal_time = 1.2
        num_rows = matrix.height
        
        mask_rects = []
        flash_rects = []
        
        for i in range(num_rows):
            y_pos = i * char_h
            base_delay = (i / num_rows) * target_reveal_time
            jitter = random.uniform(0.0, 0.05)
            delay = base_delay + jitter
            
            # Mask rect - add +2 height to eliminate sub-pixel SVG anti-aliasing gaps that darken the image
            mask_rects.append(f'<rect x="0" y="{y_pos}" width="100%" height="{char_h + 2}" fill="white" opacity="0" style="animation: reveal-row 0s linear forwards; animation-delay: {delay:.3f}s;" />')
            
            # Flash rect
            flash_rects.append(f'<rect x="0" y="{y_pos}" width="100%" height="{char_h + 2}" fill="rgba(255,255,255,0.25)" opacity="0" style="animation: flash-row 0.15s ease-out forwards; animation-delay: {delay:.3f}s;" />')

        scanner_delay = target_reveal_time + 0.1
        
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img_w} {img_h}" width="{img_w}" height="{img_h}">
    <defs>
        <style>
            @keyframes reveal-row {{
                0% {{ opacity: 0; }}
                100% {{ opacity: 1; }}
            }}
            @keyframes flash-row {{
                0% {{ opacity: 0; }}
                1% {{ opacity: 1; }}
                100% {{ opacity: 0; }}
            }}
            @keyframes scan-pass {{
                0% {{ transform: translateY(-40px); opacity: 0; }}
                10% {{ opacity: 1; }}
                90% {{ opacity: 1; }}
                100% {{ transform: translateY({img_h}px); opacity: 0; }}
            }}
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
    
    <!-- Base terminal background -->
    <rect width="100%" height="100%" fill="{self.bg_color}" />
    
    <!-- Revealed Portrait -->
    <image href="data:image/webp;base64,{b64_webp}" width="100%" height="100%" mask="url(#reveal)" />
    
    <!-- Brightness Flashes -->
    <g id="flashes">
        {''.join(flash_rects)}
    </g>
    
    <!-- Scanner Pass -->
    <rect width="100%" height="40" fill="url(#scan-grad)" opacity="0" style="animation: scan-pass 0.5s ease-in-out forwards; animation-delay: {scanner_delay:.3f}s;" />
</svg>"""

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
