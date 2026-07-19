import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from .fetcher import ContributionFetcher

class HeatmapRenderer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.theme = config.get("theme", {})
        self.colors = self.theme.get("colors", {})
        self.username = config.get("profile", {}).get("user", {}).get("github_username", "WaifuPuller")
        
    def generate(self, out_path: str):
        fetcher = ContributionFetcher(self.username)
        data = fetcher.get_contributions()
        
        svg_width = 800
        svg_height = 200
        
        svg = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {svg_width} {svg_height}",
            "width": str(svg_width),
            "height": str(svg_height)
        })
        
        level_colors = {
            0: self.colors.get('surface', '#1E1E1E'),
            1: "#5c0b19",
            2: self.colors.get('secondary', '#8B0000'),
            3: self.colors.get('primary', '#DC143C'),
            4: self.colors.get('accent', '#FFD700')
        }
        
        style = ET.SubElement(svg, "style")
        style.text = f"""
            .bg {{ fill: {self.colors.get('background', '#121212')}; }}
            .cell {{ rx: 3px; stroke: {self.colors.get('background', '#121212')}; stroke-width: 2px; transition: all 0.3s ease; cursor: pointer; }}
            .cell:hover {{ stroke: {self.colors.get('text_primary', '#FFFFFF')}; }}
            .text {{ font-family: {self.theme.get('typography', {}).get('font_ui', 'sans-serif')}; fill: {self.colors.get('text_secondary', '#A0A0A0')}; font-size: 12px; }}
            .title {{ fill: {self.colors.get('text_primary', '#FFFFFF')}; font-weight: bold; font-size: 16px; }}
        """
        
        ET.SubElement(svg, "rect", {"class": "bg", "width": "100%", "height": "100%"})
        ET.SubElement(svg, "text", {"x": "40", "y": "30", "class": "text title"}).text = f"Contribution Activity ({self.username})"
        
        if not data:
            ET.SubElement(svg, "text", {"x": "40", "y": "100", "class": "text"}).text = "No data available."
        else:
            weeks = [data[i:i+7] for i in range(0, len(data), 7)]
            
            box_size = 14
            x_offset = 40
            
            g_graph = ET.SubElement(svg, "g", {"transform": f"translate({x_offset}, 50)"})
            
            for i, week in enumerate(weeks):
                for j, day in enumerate(week):
                    lvl = day.get("level", 0)
                    color = level_colors.get(lvl, level_colors[0])
                    
                    cell = ET.SubElement(g_graph, "rect", {
                        "class": "cell",
                        "x": str(i * box_size),
                        "y": str(j * box_size),
                        "width": str(box_size - 2),
                        "height": str(box_size - 2),
                        "fill": color,
                        "opacity": "0"
                    })
                    
                    ET.SubElement(cell, "title").text = f"{day.get('date')}: Level {lvl}"
                    
                    anim = ET.SubElement(cell, "animate")
                    anim.set("attributeName", "opacity")
                    anim.set("from", "0")
                    anim.set("to", "1")
                    anim.set("begin", f"{i * 20}ms")
                    anim.set("dur", "300ms")
                    anim.set("fill", "freeze")
                    
        tree = ET.ElementTree(svg)
        tree.write(out_path, encoding="utf-8", xml_declaration=True)
