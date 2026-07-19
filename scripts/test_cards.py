import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.config_parser import load_all_configs
from cards.info_panel import InfoPanelGenerator
from cards.tech_stack import TechStackGenerator
from cards.projects import ProjectsGenerator

def test():
    configs = load_all_configs()
    
    info = InfoPanelGenerator(configs)
    tech = TechStackGenerator(configs)
    proj = ProjectsGenerator(configs)
    
    Path("assets/generated").mkdir(parents=True, exist_ok=True)
    
    info.generate("assets/generated/info_panel.svg")
    tech.generate("assets/generated/tech_stack.svg")
    proj.generate("assets/generated/projects.svg")
    
    print("Cards generated successfully.")

if __name__ == "__main__":
    test()
