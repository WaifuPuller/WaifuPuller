import re
from pathlib import Path

def polish_module(file_path, is_top=False, is_bottom=False):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Align margins to x="50"
    content = content.replace('x="40" y="30"', 'x="50" y="30"') # Tab header
    content = content.replace('width="{svg_w - 80}"', 'width="{svg_w - 100}"') # Tab width
    content = content.replace('x="60" y="55"', 'x="70" y="55"') # Tab text
    content = content.replace('x="{svg_w - 60}"', 'x="{svg_w - 70}"') # Tab right text
    
    # Update grid alignments for 50px margins (1200 - 100 = 1100 total width)
    content = content.replace('start_x = 40', 'start_x = 50')
    content = content.replace('col1_x = 40', 'col1_x = 50')
    
    # Specific adjustments
    if 'projects.py' in file_path:
        content = content.replace('card_w = 540', 'card_w = 530') # 1100/2 - 20 padding
    if 'tech_stack.py' in file_path:
        content = content.replace('col_w = 540', 'col_w = 530')
        content = content.replace('bar_w = 800', 'bar_w = 810')
    if 'system_monitor.py' in file_path:
        content = content.replace('col2_x = 400', 'col2_x = 410')
        content = content.replace('col3_x = 760', 'col3_x = 770')
        content = content.replace('x="40" y="{dist_y}"', 'x="50" y="{dist_y}"')
        content = content.replace('x="40" y="{proc_y}"', 'x="50" y="{proc_y}"')
        content = content.replace('bar_x = 240', 'bar_x = 250')
        content = content.replace('header_x_offsets = [40, 100', 'header_x_offsets = [50, 110')
        content = content.replace('x="40" y="{table_y - 18}"', 'x="50" y="{table_y - 18}"')
        content = content.replace('x="40" y="{row_y - 16}"', 'x="50" y="{row_y - 16}"')
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# Apply to all cards
cards_dir = Path("d:/WaifuPuller-Profile/scripts/cards")
for py_file in cards_dir.glob("*.py"):
    is_top = (py_file.name == "hero_panel.py")
    is_bottom = (py_file.name == "system_monitor.py")
    polish_module(str(py_file), is_top, is_bottom)

print("Applied 50px margin alignment across all modules.")
