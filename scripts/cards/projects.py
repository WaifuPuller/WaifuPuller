from utils.logger import setup_logger
from utils.ui_components import BasePanelGenerator
from typing import Dict, Any

logger = setup_logger("projects_panel")

class ProjectsGenerator(BasePanelGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.projects_config = config.get("projects", {})

    def generate(self, out_path: str):
        projects = self.projects_config.get("repositories", [])
        
        svg_w = 1200
        svg_h = 460
        
        logger.info(f"Generating Repository Explorer SVG ({svg_w}x{svg_h}) to {out_path}")
        
        elements = []
        
        # Background
        elements.append(f'<rect x="0" y="0" width="{svg_w}" height="{svg_h}" fill="{self.bg_color}" />')
        
        # Terminal Tab
        elements.extend(self.get_terminal_tab(svg_w, "~/system/explorer (projects)"))
        
        start_y = 110
        start_x = 50
        card_w = 530
        card_h = 140
        padding = 40
        
        for i, proj in enumerate(projects):
            x = start_x if i % 2 == 0 else start_x + card_w + padding
            y = start_y + (i // 2) * (card_h + padding)
            
            name = self.escape_xml(proj.get("name", ""))
            desc = self.escape_xml(proj.get("description", ""))
            lang = self.escape_xml(proj.get("language", ""))
            stars = self.escape_xml(str(proj.get("stars", 0)))
            forks = self.escape_xml(str(proj.get("forks", 0)))
            
            # Card background
            elements.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" fill="{self.surface_color}" rx="8" />')
            
            # Icon
            elements.append(f'<text x="{x + 20}" y="{y + 35}" fill="{self.primary_color}" font-size="20">📁</text>')
            
            # Name
            elements.append(f'<text x="{x + 55}" y="{y + 32}" fill="{self.text_primary}" font-weight="bold" font-size="{self.font_size_title}">{name}</text>')
            
            # Language/Stats
            elements.append(f'<text x="{x + card_w - 20}" y="{y + 32}" fill="{self.text_secondary}" font-size="{self.font_size_small}" text-anchor="end">{lang} | ⭐ {stars} | ⑂ {forks}</text>')
            
            # Description (Word wrap approximation)
            words = desc.split()
            line1, line2 = "", ""
            for w in words:
                if len(line1) + len(w) < 45: line1 += w + " "
                elif len(line2) + len(w) < 45: line2 += w + " "
                
            elements.append(f'<text x="{x + 20}" y="{y + 70}" fill="{self.text_secondary}" font-size="{self.font_size_body}">{line1.strip()}</text>')
            if line2:
                elements.append(f'<text x="{x + 20}" y="{y + 95}" fill="{self.text_secondary}" font-size="{self.font_size_body}">{line2.strip()}</text>')
                
            # Interactive Buttons (Visual only)
            elements.append(f'<g class="btn-hover">')
            elements.append(f'<rect x="{x + 20}" y="{y + card_h - 40}" width="90" height="26" fill="{self.bg_color}" rx="4" class="btn-bg" />')
            elements.append(f'<text x="{x + 65}" y="{y + card_h - 22}" fill="{self.accent_color}" font-size="{self.font_size_small}" text-anchor="middle" class="btn-text">Source</text>')
            elements.append(f'</g>')
            
            elements.append(f'<g class="btn-hover">')
            elements.append(f'<rect x="{x + 120}" y="{y + card_h - 40}" width="90" height="26" fill="{self.bg_color}" rx="4" class="btn-bg" />')
            elements.append(f'<text x="{x + 165}" y="{y + card_h - 22}" fill="{self.accent_color}" font-size="{self.font_size_small}" text-anchor="middle" class="btn-text">Demo</text>')
            elements.append(f'</g>')
            
        extra_defs = f"""
        <style>
            .btn-hover:hover .btn-bg {{
                fill: {self.primary_color};
            }}
            .btn-hover:hover .btn-text {{
                fill: {self.text_primary};
            }}
        </style>
        """
        
        svg_content = self.get_svg_wrapper(
            svg_w, svg_h, 
            "Projects Explorer", 
            "GitHub repository explorer application showing active projects",
            elements,
            extra_defs
        )
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        logger.info("Projects SVG generated successfully.")
