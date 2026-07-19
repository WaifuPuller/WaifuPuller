from utils.logger import setup_logger
from utils.ui_components import BasePanelGenerator
from typing import Dict, Any

logger = setup_logger("timeline_panel")

class TimelineGenerator(BasePanelGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.timeline_config = config.get("timeline", {})

    def generate(self, out_path: str):
        commits = self.timeline_config.get("commits", [])
        
        # Calculate dynamic height based on number of commits
        # Each commit takes about 80px
        svg_w = 1200
        svg_h = max(140, 100 + (len(commits) * 80) + 40)
        
        logger.info(f"Generating Version Control SVG ({svg_w}x{svg_h}) to {out_path}")
        
        elements = []
        
        # Background
        elements.append(f'<rect x="0" y="0" width="{svg_w}" height="{svg_h}" fill="{self.bg_color}" />')
        
        # Terminal Tab
        elements.extend(self.get_terminal_tab(svg_w, "~/system/version_control (git log --graph)"))
        
        start_y = 120
        line_x = 80
        text_x = 120
        
        # Draw the continuous graph line
        elements.append(f'<line x1="{line_x}" y1="{start_y}" x2="{line_x}" y2="{start_y + (len(commits) - 1) * 80}" stroke="{self.surface_color}" stroke-width="4" />')
        
        y = start_y
        for c in commits:
            hash_val = self.escape_xml(c.get("hash", "0000000"))
            date = self.escape_xml(c.get("date", ""))
            branch = self.escape_xml(c.get("branch", "main"))
            msg = self.escape_xml(c.get("message", ""))
            tech = self.escape_xml(", ".join(c.get("technologies", [])))
            
            # Commit Node
            elements.append(f'<g class="commit-node">')
            elements.append(f'<circle cx="{line_x}" cy="{y}" r="6" fill="{self.accent_color}" class="node-dot" />')
            elements.append(f'<circle cx="{line_x}" cy="{y}" r="12" fill="{self.accent_color}" opacity="0" class="node-glow" />')
            
            # Commit Hash & Date
            elements.append(f'<text x="{text_x}" y="{y - 5}" fill="{self.primary_color}" font-weight="bold" font-size="{self.font_size_body}">* commit {hash_val}</text>')
            elements.append(f'<text x="{text_x + 160}" y="{y - 5}" fill="{self.text_secondary}" font-size="{self.font_size_small}">| {date} | ({branch})</text>')
            
            # Commit Message
            elements.append(f'<text x="{text_x}" y="{y + 15}" fill="{self.text_primary}" font-size="{self.font_size_body}">{msg}</text>')
            
            # Technologies
            if tech:
                elements.append(f'<text x="{text_x}" y="{y + 35}" fill="{self.text_secondary}" font-size="{self.font_size_small}">[ {tech} ]</text>')
            
            elements.append(f'</g>')
            y += 80
            
        extra_defs = f"""
        <style>
            .commit-node:hover .node-glow {{
                opacity: 0.3;
                transition: opacity 0.2s;
            }}
            .commit-node:hover .node-dot {{
                fill: {self.text_primary};
            }}
        </style>
        """
        
        svg_content = self.get_svg_wrapper(
            svg_w, svg_h, 
            "Version Control History", 
            "Git log visualization showing major milestones as commits",
            elements,
            extra_defs
        )
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        logger.info("Timeline SVG generated successfully.")
