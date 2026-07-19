import xml.etree.ElementTree as ET
from datetime import datetime
import re
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("svg_builder")

def inject_metadata_and_minify(svg_path: str):
    logger.debug(f"Injecting metadata and minifying SVG: {svg_path}")
    
    tree = ET.parse(svg_path)
    root = tree.getroot()
    
    metadata = ET.Element("metadata")
    gen_info = ET.SubElement(metadata, "waifupuller-profile")
    gen_info.set("version", "1.0.0")
    gen_info.set("timestamp", datetime.utcnow().isoformat() + "Z")
    root.insert(0, metadata)
    
    xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")
    
    # Basic minification by stripping newlines (safe outside text nodes if we don't have multiline text nodes)
    # The SVG renderer uses xml:space="preserve" in tspan, but newlines between tags can be stripped.
    xml_str = xml_str.replace('\n', '')
    
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(xml_str)
