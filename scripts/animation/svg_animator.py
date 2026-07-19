from xml.etree.ElementTree import Element, SubElement
from typing import Dict, Any, List

class SVGAnimator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("animations", {})

    def apply_staggered_fade(self, text_elements: List[Element], delay_between_ms: int = 50):
        """Applies a fade in to a list of elements sequentially."""
        for i, el in enumerate(text_elements):
            begin_ms = i * delay_between_ms
            el.set("opacity", "0")
            anim = SubElement(el, "animate")
            anim.set("attributeName", "opacity")
            anim.set("from", "0")
            anim.set("to", "1")
            anim.set("begin", f"{begin_ms}ms")
            anim.set("dur", "300ms")
            anim.set("fill", "freeze")
