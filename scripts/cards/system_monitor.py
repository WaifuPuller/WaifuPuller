from utils.logger import setup_logger
from utils.ui_components import BasePanelGenerator
from typing import Dict, Any

logger = setup_logger("system_monitor_panel")

class SystemMonitorGenerator(BasePanelGenerator):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.sys_config = config.get("system_monitor", {})

    def generate(self, out_path: str):
        metrics = self.sys_config.get("metrics", {})
        runtime = self.sys_config.get("runtime_distribution", [])
        processes = self.sys_config.get("running_processes", [])
        
        svg_w = 1200
        svg_h = 500
        
        logger.info(f"Generating System Monitor SVG ({svg_w}x{svg_h}) to {out_path}")
        
        elements = []
        
        # Background
        elements.append(f'<rect x="0" y="0" width="{svg_w}" height="{svg_h}" fill="{self.bg_color}" rx="10" />')
        elements.append(f'<rect x="0" y="0" width="{svg_w}" height="20" fill="{self.bg_color}" />')
        
        # Terminal Tab
        elements.extend(self.get_terminal_tab(svg_w, "~/system/diagnostics (htop)"))
        
        start_y = 110
        
        # Metrics block
        m_keys = [
            ("Installed Projects", metrics.get("installed_projects", 0)),
            ("Process Count", metrics.get("process_count", 0)),
            ("Active Connections", metrics.get("active_connections", 0)),
            ("Performance Rating", metrics.get("performance_rating", "Unknown")),
            ("System Uptime", metrics.get("system_uptime", "0 days"))
        ]
        
        col1_x = 50
        col2_x = 410
        col3_x = 770
        
        for i, (k, v) in enumerate(m_keys):
            x = col1_x if i % 3 == 0 else (col2_x if i % 3 == 1 else col3_x)
            y_offset = (i // 3) * 40
            
            elements.append(f'<text x="{x}" y="{start_y + y_offset}" fill="{self.text_secondary}" font-size="15">{self.escape_xml(k)}: <tspan fill="{self.text_primary}" font-weight="bold">{self.escape_xml(v)}</tspan></text>')
            
        # Runtime Distribution
        dist_y = start_y + ((len(m_keys) // 3) + 1) * 40 + 20
        elements.append(f'<text x="50" y="{dist_y}" fill="{self.primary_color}" font-weight="bold" font-size="{self.font_size_title}">Runtime Distribution:</text>')
        
        bar_x = 250
        bar_w = 800
        elements.append(f'<rect x="{bar_x}" y="{dist_y - 12}" width="{bar_w}" height="16" fill="{self.surface_color}" rx="4" />')
        
        curr_x = bar_x
        lang_colors = [self.primary_color, self.accent_color, "#4CAF50", "#2196F3"]
        legend_elements = []
        
        for i, rt in enumerate(runtime):
            lang = self.escape_xml(rt.get("language", ""))
            usage_str = str(rt.get("usage", "0%"))
            usage_pct = float(usage_str.strip("%"))
            
            width = (usage_pct / 100.0) * bar_w
            color = lang_colors[i % len(lang_colors)]
            
            elements.append(f'<rect x="{curr_x}" y="{dist_y - 12}" width="{width}" height="16" fill="{color}" />')
            legend_elements.append(f'<text x="{bar_x + (i * 180)}" y="{dist_y + 25}" fill="{color}" font-size="{self.font_size_body}">■ {lang} ({usage_pct}%)</text>')
            curr_x += width
            
        elements.extend(legend_elements)
        
        # Running Processes (Table)
        proc_y = dist_y + 70
        elements.append(f'<text x="50" y="{proc_y}" fill="{self.accent_color}" font-weight="bold" font-size="{self.font_size_title}">Running Processes:</text>')
        
        table_y = proc_y + 30
        headers = ["PID", "USER", "PRI", "NI", "VIRT", "RES", "SHR", "S", "CPU%", "MEM%", "TIME+", "Command"]
        header_x_offsets = [50, 110, 190, 240, 290, 360, 430, 490, 530, 610, 690, 790]
        
        # Draw table header
        elements.append(f'<rect x="50" y="{table_y - 18}" width="{svg_w - 100}" height="24" fill="{self.surface_color}" />')
        for i, h in enumerate(headers):
            elements.append(f'<text x="{header_x_offsets[i]}" y="{table_y}" fill="{self.text_secondary}" font-weight="bold" font-size="{self.font_size_body}">{self.escape_xml(h)}</text>')
            
        row_y = table_y + 30
        for p in processes:
            name = self.escape_xml(p.get("name", ""))
            pid = self.escape_xml(p.get("pid", ""))
            status = self.escape_xml(p.get("status", "S"))
            cpu = self.escape_xml(p.get("cpu", "0.0%"))
            mem = self.escape_xml(p.get("mem", "0.0%"))
            
            row_data = [
                pid, "waifu", "20", "0", "1.2G", mem, "4K", status[0] if status else "S", cpu, "1.4%", "1:23.45", f"./{name}"
            ]
            
            elements.append(f'<g class="process-row">')
            # Hover highlight
            elements.append(f'<rect x="50" y="{row_y - 16}" width="{svg_w - 100}" height="20" fill="transparent" class="row-bg" />')
            for i, d in enumerate(row_data):
                color = self.text_primary if i == len(row_data) - 1 else self.text_secondary
                elements.append(f'<text x="{header_x_offsets[i]}" y="{row_y}" fill="{color}" font-size="{self.font_size_body}">{self.escape_xml(d)}</text>')
            elements.append(f'</g>')
            
            row_y += 24
            
        extra_defs = f"""
        <style>
            .process-row:hover .row-bg {{
                fill: {self.surface_color};
            }}
            .process-row:hover text {{
                fill: {self.text_primary};
            }}
        </style>
        """
        
        svg_content = self.get_svg_wrapper(
            svg_w, svg_h, 
            "System Monitor", 
            "System diagnostic panel showing performance and active processes",
            elements,
            extra_defs
        )
        
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
            
        logger.info("System Monitor SVG generated successfully.")
