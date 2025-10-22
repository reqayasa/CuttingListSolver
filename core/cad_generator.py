# """
# cad_generator.py
# Generate DXF drawings with company title block and layer standards.
# Automatically finds template in core/templates/template.dxf
# """

# from pathlib import Path
# from datetime import datetime
import ezdxf
import csv
from pprint import pprint
from dxf_utils import draw_table, create_layout, add_titleblock
from ezdxf.addons import importer

with open('test_data/test_cutting_list_cad.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

# pprint(data, compact=True)

headers = data[0]
data = data[1:]
cell_w = [10, 25, 50, 30, 50, 60, 85]
cell_h = 6
pos = (0, 0)
text_height = 3
# pprint(data)

doc = ezdxf.new('R2007', setup=True, units=4)

layers = doc.layers
styles = doc.styles

styles.new('Table Header', 
    dxfattribs={
        'font': 'Arial.TTF',
        'width': 0.8
    })

styles.new('Table Body', 
    dxfattribs={
        'font': 'Arial.TTF',
        'width': 0.8
    })

text_style = styles.get('Table Header')
text_style.set_extended_font_data(family='Arial', bold=True)

layers.add('IES_Object line', color=ezdxf.colors.WHITE, linetype='Continuous', lineweight=25)
layers.add('IES_Dashed line', color=ezdxf.colors.YELLOW, linetype='DASHED2', lineweight=5)
layers.add('IES_Center line', color=ezdxf.colors.RED, linetype='CENTER2', lineweight=5)
layers.add('IES_Existing', color=150, linetype='Continuous', lineweight=5)
layers.add('IES_Text', color=ezdxf.colors.WHITE, linetype='Continuous', lineweight=5)
layers.add('IES_Dimension', color=ezdxf.colors.RED, linetype='Continuous', lineweight=5)

template_doc = ezdxf.readfile('core/templates/cutting_list_drawing.dxf')
dxf_importer = importer.Importer(template_doc, doc)

ttlb_block_name = 'TTLB_A3'
paper_block_name = 'paper_A3_L'
track_drawing_block_name = 'IES_Straight Track Fab Drawing'
dxf_importer.import_block(ttlb_block_name)
dxf_importer.import_block(paper_block_name)
dxf_importer.import_block(track_drawing_block_name)
dxf_importer.finalize()

msp = doc.modelspace()


dwg_no = ''
dwg_title = ''
stock_length = 5800
order_quantity = 10
material_finish = '(ALUMINUM POWDER COATING CP61 (BLACK COLOR))'

ttlb_att_value = {
    'PROJECT': '8 SHANTON WAY',
    'DRAWING_NO': f"IES-8SW-MONORAIL TRACK-{dwg_no}",
    'DRAWING_TITLE': f"STRAIGHT TRACK AT {dwg_title}",
    'DRAWN_BY': 'RIZQI',
    'CHECKED_BY': 'JOHNSON',
    'DRAWN_DATE': '2025.10.22',
    'CHECKED_DATE': '20'
    '25.10.22',
}

track_att_value = {
    'DRAWING_TITLE': f"%%USTRAIGHT TRACK AT {dwg_title}",
    'OVERALL LENGTH': f"OVERALL LENGTH {stock_length} MM",
    'QTY': f"QTY: {order_quantity} LENGTHS",
    'MATERIAL_FINISH': material_finish,
    'DRAWING_LENGTH': stock_length

}

psp = create_layout(doc, "01")
add_titleblock(doc, "01")



cutting_list_table = draw_table(msp, headers, data, cell_w, cell_h, pos, text_height)

track_drawing_blockref = msp.add_blockref(track_drawing_block_name, (0,  300))
track_drawing_blockref.add_auto_attribs(ttlb_att_value)

# psp.add_blockref(paper_block_name, (420-1.5, 1.5))
# ttlb_blockref = psp.add_blockref(ttlb_block_name, (420-1.5, 1.5))
# ttlb_blockref.add_auto_attribs(ttlb_att_value)

# table viewport
psp.add_viewport(
    center=(cutting_list_table[0] * 0.5 + 1.5, cutting_list_table[1] * (0.5) + 1.5),
    size=cutting_list_table,
    view_center_point=(cutting_list_table[0]*0.5, cutting_list_table[1]*(-0.5)),
    view_height=cutting_list_table[1]
)

psp.add_viewport(
    center=(210, 220),
    size=(417, 147),
    view_center_point=(0, 300),
    view_height=2*147
)


# Panggil fungsi

doc.saveas("output/result_table_manual.dxf")
print("✅ File 'result_table_manual.dxf' berhasil dibuat.")


# class CADGenerator:
#     # otomatis temukan template relatif terhadap file ini
#     TEMPLATE_PATH = Path(__file__).parent / "templates" / "cutting_list_drawing.dxf"

#     def __init__(self, template_path: str = None):
#         """Load company DXF template with title block and layers."""
#         self.template_path = template_path or str(self.TEMPLATE_PATH)
#         self.doc = ezdxf.readfile(self.template_path)
#         self.msp = self.doc.modelspace()
#         print(f"Loaded template from: {self.template_path}")

#     def add_cutting_layout(self, cutting_list, start=(0, 0), spacing=50):
#         """Add cutting rectangles and labels to modelspace."""
#         x0, y0 = start
#         for part in cutting_list:
#             length, width = part["length"], part["width"]
#             rect = [
#                 (x0, y0),
#                 (x0 + length, y0),
#                 (x0 + length, y0 + width),
#                 (x0, y0 + width),
#                 (x0, y0),
#             ]
#             self.msp.add_lwpolyline(rect, close=True, dxfattribs={"layer": "PARTS"})
#             self.msp.add_text(
#                 f"{part['id']} ({length}x{width})",
#                 dxfattribs={"height": 20, "layer": "TEXT"}
#             ).set_pos((x0 + 10, y0 + width / 2))
#             y0 += width + spacing

#     def add_sheet_layout(self, sheet_name: str, project_name: str):
#         """Create a new paperspace layout with title block and viewport."""
#         if sheet_name in self.doc.layouts:
#             layout = self.doc.layouts.get(sheet_name)
#         else:
#             layout = self.doc.layouts.new(sheet_name)

#         # Add title block info (adjust positions as needed)
#         layout.add_text(
#             f"Project: {project_name}",
#             dxfattribs={"height": 5, "layer": "TITLE"}
#         ).set_pos((10, 10))

#         layout.add_text(
#             f"Date: {datetime.now().strftime('%Y-%m-%d')}",
#             dxfattribs={"height": 5, "layer": "TITLE"}
#         ).set_pos((10, 20))

#         # Add viewport to show part of modelspace (optional)
#         layout.add_viewport(
#             center=(150, 100),
#             width=180,
#             height=120,
#             view_center_point=(80, 60),
#             view_height=250,
#         )

#     def update_title_block_attributes(self, block_name: str, attrs: dict):
#         """Update block attributes in modelspace by tag name."""
#         for block_ref in self.msp.query(f'INSERT[name=="{block_name}"]'):
#             for att in block_ref.attribs:
#                 tag = att.dxf.tag
#                 if tag in attrs:
#                     att.dxf.text = str(attrs[tag])

#     def save(self, output_path: str):
#         """Save generated DXF file."""
#         Path(output_path).parent.mkdir(parents=True, exist_ok=True)
