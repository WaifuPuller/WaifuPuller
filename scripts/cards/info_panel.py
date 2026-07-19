import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import re
from typing import Dict, Any

from utils.logger import setup_logger
from utils.ui_components import BasePanelGenerator

logger = setup_logger("info_panel")

class InfoPanelGenerator(BasePanelGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.profile = config.get("profile", {})

    def generate(self, out_path: str):
        svg_w = 1200
        svg_h = 400
        
        logger.info(f"Generating Neofetch Info Panel SVG ({svg_w}x{svg_h}) to {out_path}")
        
        # 1. ASCII Art (Waifu Logo)
        ascii_logo = [
            r"      /|\       ",
            r"    /  |  \     ",
            r"   /___|___\    ",
            r"  |  ^   ^  |   ",
            r"  |  0   0  |   ",
            r"   \   _   /    ",
            r"    |_____|     ",
            r"   /       \    ",
            r"  /  |   |  \   ",
            r" /___|___|___\  "
        ]
        
        elements = []
        
        # Background
        elements.append(f'<rect width="100%" height="100%" fill="{self.bg_color}" />')
        
        elements.append(f'<g style="animation: fade-in 1s ease-in-out forwards; animation-delay: 2.2s;" opacity="0">')
        
        # ASCII Logo
        ascii_start_x = 50
        ascii_start_y = 120
        line_height = 18
        
        for i, line in enumerate(ascii_logo):
            y_pos = ascii_start_y + i * line_height
            elements.append(f'<text x="{ascii_start_x}" y="{y_pos}" fill="{self.primary_color}" font-weight="bold" font-size="{self.font_size_body}" xml:space="preserve">{line}</text>')
            
        # Info Block
        info_start_x = 350
        info_start_y = 100
        
        user_info = self.profile.get("user", {})
        username = self.escape_xml(user_info.get("github_username", "WaifuPuller"))
        name = self.escape_xml(user_info.get("name", "Operator"))
        
        elements.append(f'<text x="{info_start_x}" y="{info_start_y}" fill="{self.accent_color}" font-weight="bold" font-size="{self.font_size_title}">{username}@{name}</text>')
        elements.append(f'<line x1="{info_start_x}" y1="{info_start_y + 10}" x2="{info_start_x + 300}" y2="{info_start_y + 10}" stroke="{self.surface_color}" stroke-width="2" />')
        
        details = [
            ("OS", "Luxury Terminal OS v1.0.0"),
            ("Host", "GitHub Profile Server"),
            ("Uptime", "Online"),
            ("Packages", "7 (dpkg)"),
            ("Shell", "zsh 5.8"),
            ("Resolution", "1200x2800"),
            ("Terminal", "SVG-Term"),
            ("CPU", "Waifu Neural Engine"),
            ("Memory", "64GB / 128GB")
        ]
        
        detail_y = info_start_y + 40
        for key, val in details:
            elements.append(f'<text x="{info_start_x}" y="{detail_y}" fill="{self.primary_color}" font-weight="bold" font-size="{self.font_size_body}">{self.escape_xml(key)}: <tspan fill="{self.text_secondary}" font-weight="normal">{self.escape_xml(val)}</tspan></text>')
            detail_y += 24
            
        # Color Palette blocks
        palette_colors = [
            self.bg_color, self.surface_color, self.primary_color, self.accent_color,
            "#4CAF50", "#2196F3", "#9C27B0", "#FF9800"
        ]
        
        palette_y = detail_y + 20
        for i, color in enumerate(palette_colors):
            elements.append(f'<rect x="{info_start_x + (i * 35)}" y="{palette_y}" width="30" height="15" fill="{color}" />')
            
        elements.append('</g>')
        
        extra_defs = """
        <style>
            @keyframes fade-in {
                0% { opacity: 0; transform: translateY(10px); }
                100% { opacity: 1; transform: translateY(0); }
            }
        </style>
        """
        
        svg_content = self.get_svg_wrapper(
            svg_w, svg_h, 
            "Identity Panel", 
            "Neofetch style system information panel",
            elements,
            extra_defs
        )
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        logger.info("Info Panel SVG generated successfully.")
