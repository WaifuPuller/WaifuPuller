import base64
from io import BytesIO
import random
from PIL import Image
from utils.logger import setup_logger

logger = setup_logger("animated_image_renderer")

class AnimatedImageRenderer:
    def __init__(self, config):
        self.config = config
        self.theme = config.get("theme", {})
        self.colors = self.theme.get("colors", {})
        self.bg_color = self.colors.get("background", "#121212")

    def render(self, img: Image.Image, out_path: str):
        img_w, img_h = img.size
        logger.info(f"Rendering Animated Image SVG ({img_w}x{img_h}) to {out_path}")
        
        # Save preprocessed image to lossless WebP buffer
        buffer = BytesIO()
        img.save(buffer, format="WEBP", lossless=True, quality=100, method=6)
        b64_webp = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Generate masking strips for animation (simulate 120 lines of terminal output)
        strip_count = 120
        strip_h = img_h / strip_count
        
        mask_rects = []
        for i in range(strip_count):
            y_pos = i * strip_h
            # Calculate a randomized delay to prevent mechanical wipe, keeping it between 0.1s and 1.3s
            delay = 0.1 + (i / strip_count) * 1.0 + random.uniform(0, 0.2)
            
            # Using strip_h + 2 to prevent sub-pixel gaps from bleeding background color
            mask_rects.append(f'<rect x="0" y="{y_pos}" width="100%" height="{strip_h + 2}" fill="white" opacity="0" style="animation: reveal-row 0s linear forwards; animation-delay: {delay:.2f}s;" />')
            
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img_w} {img_h}" width="{img_w}" height="{img_h}">
    <defs>
        <style>
            @keyframes reveal-row {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
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
    
    <rect width="100%" height="100%" fill="{self.bg_color}" />
    
    <!-- Revealed Portrait -->
    <image href="data:image/webp;base64,{b64_webp}" width="100%" height="100%" mask="url(#reveal)" />
    
    <!-- Scanner Pass -->
    <rect width="100%" height="40" fill="url(#scan-grad)" opacity="0" style="animation: scan-pass 0.6s ease-in-out forwards; animation-delay: 1.5s;" pointer-events="none" />
</svg>"""
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        logger.info("SVG generated successfully.")
