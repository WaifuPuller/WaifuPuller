import sys
from pathlib import Path

# Add the parent directory to sys.path to allow imports from scripts.*
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import setup_logger
from utils.config_parser import load_all_configs
from utils.svg_builder import inject_metadata_and_minify
from preprocessing.image_processor import ImageProcessor
from cards.hero_panel import HeroPanelGenerator
from cards.info_panel import InfoPanelGenerator
from cards.tech_stack import TechStackGenerator
from cards.projects import ProjectsGenerator
from cards.timeline import TimelineGenerator
from cards.system_monitor import SystemMonitorGenerator

logger = setup_logger()

def main():
    logger.info("Starting WaifuPuller-Profile Generation Pipeline...")
    
    try:
        configs = load_all_configs()
        logger.info("Successfully loaded all configurations.")
        
        out_dir = Path("assets/generated")
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Process Hero Panel
        hero_out = str(out_dir / "hero.svg")
        logger.info(f"Generating Hero Panel to {hero_out}")
        try:
            processor = ImageProcessor(configs)
            img = processor.process(configs.get("portrait", {}).get("source", ""))
            
            # Unified Hero Panel replaces the isolated animated image renderer
            renderer = HeroPanelGenerator(configs)
            renderer.render(img, hero_out)
            inject_metadata_and_minify(hero_out)
        except Exception as e:
            logger.error(f"Failed to generate hero panel: {str(e)}")
        
        # 2. Info Panel
        info_out = str(out_dir / "info_panel.svg")
        logger.info(f"Generating Info Panel to {info_out}")
        InfoPanelGenerator(configs).generate(info_out)
        inject_metadata_and_minify(info_out)
        
        # 3. Tech Stack
        tech_out = str(out_dir / "tech_stack.svg")
        logger.info(f"Generating Tech Stack to {tech_out}")
        TechStackGenerator(configs).generate(tech_out)
        inject_metadata_and_minify(tech_out)
        
        # 4. Projects
        proj_out = str(out_dir / "projects.svg")
        logger.info(f"Generating Projects to {proj_out}")
        ProjectsGenerator(configs).generate(proj_out)
        inject_metadata_and_minify(proj_out)
        
        # 5. Timeline
        timeline_out = str(out_dir / "timeline.svg")
        logger.info(f"Generating Timeline to {timeline_out}")
        TimelineGenerator(configs).generate(timeline_out)
        inject_metadata_and_minify(timeline_out)
        
        # 6. System Monitor
        monitor_out = str(out_dir / "system_monitor.svg")
        logger.info(f"Generating System Monitor to {monitor_out}")
        SystemMonitorGenerator(configs).generate(monitor_out)
        inject_metadata_and_minify(monitor_out)
        
        # 7. Assemble README.md
        logger.info("Assembling README.md")
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# WaifuPuller-Profile\n\n")
            f.write("![Terminal Boot Sequence](assets/generated/hero.svg)\n\n")
            f.write("![Info Panel](assets/generated/info_panel.svg)\n\n")
            f.write("![Tech Stack](assets/generated/tech_stack.svg)\n\n")
            f.write("![Projects](assets/generated/projects.svg)\n\n")
            f.write("![Version Control](assets/generated/timeline.svg)\n\n")
            f.write("![System Diagnostics](assets/generated/system_monitor.svg)\n")
            
        logger.info("Pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
