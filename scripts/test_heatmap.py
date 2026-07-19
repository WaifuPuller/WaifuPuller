import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.config_parser import load_all_configs
from heatmap.renderer import HeatmapRenderer

def test():
    configs = load_all_configs()
    
    heatmap = HeatmapRenderer(configs)
    
    Path("assets/generated").mkdir(parents=True, exist_ok=True)
    
    heatmap.generate("assets/generated/heatmap.svg")
    
    print("Heatmap generated successfully.")

if __name__ == "__main__":
    test()
