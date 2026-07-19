from utils.logger import setup_logger
from utils.ui_components import BasePanelGenerator
from typing import Dict, Any

logger = setup_logger("tech_stack_panel")

class TechStackGenerator(BasePanelGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tech_config = config.get("tech_stack", {})

    def generate(self, out_path: str):
        categories = self.tech_config.get("categories", [])
        
        svg_w = 1200
        svg_h = 660
        
        logger.info(f"Generating Package Manager SVG ({svg_w}x{svg_h}) to {out_path}")
        
        elements = []
        
        # Background
        elements.append(f'<rect x="0" y="0" width="{svg_w}" height="{svg_h}" fill="{self.bg_color}" />')
        
        # Terminal Tab
        elements.extend(self.get_terminal_tab(svg_w, "~/system/pkg_mgr (tech_stack)"))
        
        start_y = 110
        start_x = 50
        col_w = 530
        col_spacing = 40
        
        current_col = 0
        y_offsets = [start_y, start_y]
        
        for cat in categories:
            name = self.escape_xml(cat.get("name", ""))
            packages = cat.get("packages", [])
            
            x = start_x if current_col == 0 else start_x + col_w + col_spacing
            y = y_offsets[current_col]
            
            # Category Header (Repository Name)
            elements.append(f'<text x="{x}" y="{y}" fill="{self.primary_color}" font-weight="bold" font-size="{self.font_size_title}">Repo: {name}</text>')
            elements.append(f'<line x1="{x}" y1="{y + 8}" x2="{x + col_w}" y2="{y + 8}" stroke="{self.surface_color}" stroke-width="2" />')
            
            y += 35
            
            # Packages
            for pkg in packages:
                pkg_name = self.escape_xml(pkg.get("name", ""))
                status = self.escape_xml(pkg.get("status", "Installed"))
                version = self.escape_xml(pkg.get("version", "latest"))
                
                elements.append(f'<g class="pkg-row">')
                # Hover highlight
                elements.append(f'<rect x="{x - 10}" y="{y - 18}" width="{col_w + 20}" height="24" fill="transparent" class="pkg-bg" rx="4" />')
                
                # Package name
                elements.append(f'<text x="{x}" y="{y}" fill="{self.text_primary}" font-weight="bold" font-size="{self.font_size_body}">{pkg_name}</text>')
                
                # Status & Version
                elements.append(f'<text x="{x + col_w - 120}" y="{y}" fill="{self.text_secondary}" font-size="{self.font_size_small}">[{status}]</text>')
                elements.append(f'<text x="{x + col_w}" y="{y}" fill="{self.accent_color}" font-size="{self.font_size_small}" text-anchor="end">v_{version}</text>')
                elements.append(f'</g>')
                
                y += 28
                
            y_offsets[current_col] = y + 30
            
            # Switch column to balance height
            if y_offsets[0] > y_offsets[1]:
                current_col = 1
            else:
                current_col = 0
                
        extra_defs = f"""
        <style>
            .pkg-row:hover .pkg-bg {{
                fill: {self.surface_color};
            }}
        </style>
        """
        
        svg_content = self.get_svg_wrapper(
            svg_w, svg_h, 
            "Package Manager", 
            "Technical skills presented as system packages",
            elements,
            extra_defs
        )
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        logger.info("Tech Stack SVG generated successfully.")
