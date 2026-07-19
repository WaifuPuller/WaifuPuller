from typing import Dict, Any, List

class BasePanelGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.theme = config.get("theme", {})
        self.colors = self.theme.get("colors", {})
        
        self.bg_color = self.colors.get("background", "#121212")
        self.surface_color = self.colors.get("surface", "#1E1E1E")
        self.primary_color = self.colors.get("primary", "#DC143C")
        self.accent_color = self.colors.get("accent", "#FFD700")
        self.text_primary = self.colors.get("text_primary", "#FFFFFF")
        self.text_secondary = self.colors.get("text_secondary", "#A0A0A0")
        
        typography = self.theme.get("typography", {})
        self.font_terminal = typography.get("font_terminal", "monospace")
        
        # Standardized typography scale
        self.font_size_title = 16
        self.font_size_body = 14
        self.font_size_small = 12

    @staticmethod
    def escape_xml(s: Any) -> str:
        """Safely encode strings for XML."""
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def get_svg_wrapper(self, width: int, height: int, title: str, desc: str, inner_elements: List[str], extra_defs: str = "") -> str:
        """Generate the outer SVG container with standard accessibility tags and styles."""
        elements_str = '\n        '.join(inner_elements)
        
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="svg-title svg-desc">
    <title id="svg-title">{self.escape_xml(title)}</title>
    <desc id="svg-desc">{self.escape_xml(desc)}</desc>
    <defs>
        <style>
            text {{
                font-family: {self.font_terminal};
            }}
        </style>
        {extra_defs}
    </defs>
    
    <g>
        {elements_str}
    </g>
</svg>"""

    def get_terminal_tab(self, svg_w: int, tab_title: str) -> List[str]:
        """Generate a standard terminal UI tab header."""
        return [
            f'<rect x="50" y="30" width="{svg_w - 100}" height="40" fill="{self.surface_color}" rx="8" />',
            f'<text x="70" y="55" fill="{self.text_primary}" font-weight="bold" font-size="{self.font_size_title}">{self.escape_xml(tab_title)}</text>'
        ]
