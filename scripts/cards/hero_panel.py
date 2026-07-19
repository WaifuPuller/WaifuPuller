import base64
from io import BytesIO
import random
from PIL import Image
from utils.logger import setup_logger
from utils.ui_components import BasePanelGenerator

logger = setup_logger("hero_panel")

class HeroPanelGenerator(BasePanelGenerator):
    def __init__(self, config):
        super().__init__(config)
        self.profile = config.get("profile", {})

    def render(self, img: Image.Image, out_path: str):
        svg_w = 1200
        svg_h = 640
        
        logger.info(f"Rendering Unified Hero Panel SVG ({svg_w}x{svg_h}) to {out_path}")
        
        # Right Side: Portrait (500x500)
        portrait_w = 500
        portrait_h = 500
        portrait_x = 650
        portrait_y = 90
        
        img_resized = img.resize((portrait_w, portrait_h), Image.Resampling.LANCZOS)
        buffer = BytesIO()
        img_resized.save(buffer, format="WEBP", lossless=True, quality=100, method=6)
        b64_webp = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Mask strips for portrait reveal
        strip_count = 100
        strip_h = portrait_h / strip_count
        mask_rects = []
        for i in range(strip_count):
            y_pos = portrait_y + i * strip_h
            delay = 0.1 + (i / strip_count) * 1.0 + random.uniform(0, 0.2)
            mask_rects.append(f'<rect x="{portrait_x}" y="{y_pos}" width="{portrait_w}" height="{strip_h + 2}" fill="white" opacity="0" style="animation: reveal-row 0s linear forwards; animation-delay: {delay:.2f}s;" />')
            
        # Left Side: Terminal Text
        username = self.escape_xml(self.profile.get("user", {}).get("github_username", "WaifuPuller"))
        bio = self.escape_xml(self.profile.get("user", {}).get("bio", "Senior Software Architect"))
        
        typing_lines = [
            f"> ./initialize_os.sh",
            f"Loading {username} OS v1.0.0...",
            f"Mounting filesystems... OK",
            f"Starting secure shell daemon... OK",
            f"Establishing neural link... OK",
            f"",
            f"Welcome, Operator.",
            f"",
            f"Identity: {username}",
            f"Role: {bio}",
            f"Status: Online",
            f"",
            f"> _"
        ]
        
        text_elements = []
        line_height = 24
        start_y = portrait_y + 20
        start_x = 50
        
        # CSS typing animation logic: Reveal lines sequentially
        for i, line in enumerate(typing_lines):
            delay = 0.2 + (i * 0.15)
            y_pos = start_y + i * line_height
            
            safe_line = self.escape_xml(line)
            
            # Highlight prompt lines or keys
            if line.startswith("&gt;"): # Already escaped
                color = self.accent_color
            elif ":" in line and not line.startswith("Loading"):
                parts = safe_line.split(":", 1)
                text_elements.append(f'<text x="{start_x}" y="{y_pos}" fill="{self.primary_color}" font-weight="bold" font-size="{self.font_size_title}" opacity="0" style="animation: reveal-text 0s forwards; animation-delay: {delay:.2f}s;">{parts[0]}:<tspan fill="{self.text_primary}" font-weight="normal">{parts[1]}</tspan></text>')
                continue
            else:
                color = self.text_primary
                
            text_elements.append(f'<text x="{start_x}" y="{y_pos}" fill="{color}" font-size="{self.font_size_title}" opacity="0" style="animation: reveal-text 0s forwards; animation-delay: {delay:.2f}s;">{safe_line}</text>')
            
        extra_defs = f"""
        <style>
            @keyframes reveal-row {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
            @keyframes reveal-text {{ 0% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
            @keyframes scan-pass {{ 0% {{ transform: translateY(-40px); opacity: 0; }} 10% {{ opacity: 1; }} 90% {{ opacity: 1; }} 100% {{ transform: translateY({portrait_h}px); opacity: 0; }} }}
            @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
        </style>
        <linearGradient id="scan-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="rgba(255,255,255,0)" />
            <stop offset="50%" stop-color="rgba(255,255,255,0.4)" />
            <stop offset="100%" stop-color="rgba(255,255,255,0)" />
        </linearGradient>
        <mask id="reveal">
            {''.join(mask_rects)}
        </mask>
        """
        
        elements = []
        
        # OS Window Background
        elements.append(f'<rect width="100%" height="100%" fill="{self.bg_color}" rx="10" />')
        elements.append(f'<rect width="100%" height="40" fill="{self.surface_color}" rx="10" />')
        # Fix bottom corners of top bar
        elements.append(f'<rect x="0" y="20" width="100%" height="20" fill="{self.surface_color}" />')
        # Fix bottom corners of OS Window to merge seamlessly with next panel
        elements.append(f'<rect x="0" y="{svg_h - 20}" width="100%" height="20" fill="{self.bg_color}" />')
        
        # Window Controls
        elements.append(f'<circle cx="20" cy="20" r="6" fill="#FF5F56" />')
        elements.append(f'<circle cx="40" cy="20" r="6" fill="#FFBD2E" />')
        elements.append(f'<circle cx="60" cy="20" r="6" fill="#27C93F" />')
        elements.append(f'<text x="{svg_w/2}" y="25" fill="{self.text_secondary}" font-size="{self.font_size_body}" text-anchor="middle">terminal ~ {username}</text>')
        
        # Left Side: Terminal Boot Text
        elements.extend(text_elements)
        
        # Right Side: Revealed Portrait
        elements.append(f'<g transform="translate({portrait_x}, {portrait_y})">')
        elements.append(f'<image href="data:image/webp;base64,{b64_webp}" width="{portrait_w}" height="{portrait_h}" mask="url(#reveal)" />')
        elements.append(f'<rect width="{portrait_w}" height="40" fill="url(#scan-grad)" opacity="0" style="animation: scan-pass 0.6s ease-in-out forwards; animation-delay: 1.5s;" pointer-events="none" />')
        elements.append(f'</g>')
        
        svg_content = self.get_svg_wrapper(
            svg_w, svg_h, 
            "OS Boot Sequence", 
            "Terminal booting sequence revealing the user's portrait",
            elements,
            extra_defs
        )
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        logger.info("Hero SVG generated successfully.")
