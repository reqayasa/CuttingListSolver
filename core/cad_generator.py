"""
cad_generator.py
Generate DXF drawings with company title block and layer standards.
Automatically finds template in core/templates/template.dxf
"""

from pathlib import Path
from datetime import datetime
import ezdxf


class CADGenerator:
    # otomatis temukan template relatif terhadap file ini
    TEMPLATE_PATH = Path(__file__).parent / "templates" / "cutting_list_drawing.dxf"

    def __init__(self, template_path: str = None):
        """Load company DXF template with title block and layers."""
        self.template_path = template_path or str(self.TEMPLATE_PATH)
        self.doc = ezdxf.readfile(self.template_path)
        self.msp = self.doc.modelspace()
        print(f"Loaded template from: {self.template_path}")

    def add_cutting_layout(self, cutting_list, start=(0, 0), spacing=50):
        """Add cutting rectangles and labels to modelspace."""
        x0, y0 = start
        for part in cutting_list:
            length, width = part["length"], part["width"]
            rect = [
                (x0, y0),
                (x0 + length, y0),
                (x0 + length, y0 + width),
                (x0, y0 + width),
                (x0, y0),
            ]
            self.msp.add_lwpolyline(rect, close=True, dxfattribs={"layer": "PARTS"})
            self.msp.add_text(
                f"{part['id']} ({length}x{width})",
                dxfattribs={"height": 20, "layer": "TEXT"}
            ).set_pos((x0 + 10, y0 + width / 2))
            y0 += width + spacing

    def add_sheet_layout(self, sheet_name: str, project_name: str):
        """Create a new paperspace layout with title block and viewport."""
        if sheet_name in self.doc.layouts:
            layout = self.doc.layouts.get(sheet_name)
        else:
            layout = self.doc.layouts.new(sheet_name)

        # Add title block info (adjust positions as needed)
        layout.add_text(
            f"Project: {project_name}",
            dxfattribs={"height": 5, "layer": "TITLE"}
        ).set_pos((10, 10))

        layout.add_text(
            f"Date: {datetime.now().strftime('%Y-%m-%d')}",
            dxfattribs={"height": 5, "layer": "TITLE"}
        ).set_pos((10, 20))

        # Add viewport to show part of modelspace (optional)
        layout.add_viewport(
            center=(150, 100),
            width=180,
            height=120,
            view_center_point=(80, 60),
            view_height=250,
        )

    def update_title_block_attributes(self, block_name: str, attrs: dict):
        """Update block attributes in modelspace by tag name."""
        for block_ref in self.msp.query(f'INSERT[name=="{block_name}"]'):
            for att in block_ref.attribs:
                tag = att.dxf.tag
                if tag in attrs:
                    att.dxf.text = str(attrs[tag])

    def save(self, output_path: str):
        """Save generated DXF file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
