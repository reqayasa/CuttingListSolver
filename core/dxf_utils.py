import ezdxf
from ezdxf.layouts import Modelspace, Paperspace
from ezdxf.document import Drawing
from ezdxf.enums import TextEntityAlignment


def draw_table(msp: Modelspace, headers: list[str], data: list[str], cell_w: list[float], cell_h=8, pos=(0, 0), text_height=3):
    """
    Menggambar tabel manual (garis + teks) ke dalam modelspace DXF.

    Parameters
    ----------
    msp : ezdxf.layout.Modelspace
        Modelspace dari dokumen DXF.
    headers : list[str]
        Daftar nama kolom (baris pertama).
    data : list[list]
        Data baris tabel.
    cell_w : list[float]
        Lebar tiap kolom.
    cell_h : float
        Tinggi tiap baris.
    pos : tuple(float, float)
        Posisi pojok kiri atas tabel (default (0,0)).
    text_height : float
        Tinggi teks dalam tabel.
    """

    x0, y0 = pos
    rows = len(data) + 1
    cols = len(headers)
    line_attribs = {'layer': 'IES_Existing'}
    text_header_attribs = {'layer': 'IES_Text', 'style': 'Table Header',}
    text_body_attribs = {'layer': 'IES_Text', 'style': 'Table Body',}

    # Gambar garis horizontal
    for r in range(rows + 1):
        y = y0 - r * cell_h
        msp.add_line((x0, y), (x0 + sum(cell_w), y), dxfattribs=line_attribs)
    
    # Gambar garis vertikal
    x = x0
    y = y0 - rows * cell_h
    for c in range(cols):
        msp.add_line((x, y0), (x, y), dxfattribs=line_attribs)
        x = x + cell_w[c]
    msp.add_line((x, y0), (x, y), dxfattribs=line_attribs)


    # Isi header
    x = 0
    y = 0
    for c, h in enumerate(headers):
        if c == 0:
            x = x + cell_w[c] / 2
        else:
            x = x + cell_w[c-1] / 2 + cell_w[c] / 2
        y = x0 - cell_h / 2
        msp.add_text(
            str(h), dxfattribs=text_header_attribs
        ).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Isi data
    x = 0
    y = 0
    for r, row_data in enumerate(data, start=1):
        x = 0
        for c, value in enumerate(row_data):
            if c == 0:
                x = x + cell_w[c] / 2
            else:
                x = x + cell_w[c-1] / 2 + cell_w[c] / 2
            y = y0 - (r + 0.5) * cell_h
            msp.add_text(
                str(value), dxfattribs=text_body_attribs
            ).set_placement((x, y), align=TextEntityAlignment.MIDDLE_CENTER)

    # Opsional: kembalikan total tinggi tabel
    total_height = rows * cell_h
    total_width = sum(cell_w)
    return total_width, total_height

def create_layout(doc: Drawing, name: str, orientation="landscape"):
    # Create a new layout (this creates both layout record + paperspace)
    doc.layouts.new(name)
    layout = doc.layouts.get(name)  # <-- Layout wrapper

    # Set up page
    size = (420, 297) if orientation == "landscape" else (297, 420)
    layout.page_setup(
        size=size,
        units="mm",
        scale=(1, 1),
        device="DWG To PDF.pc3",
    )
    layout.set_plot_style("monochrome.ctb", True)

    return layout  # <-- return Layout object

def add_titleblock(doc: Drawing, layout_name: str, orientation="landscape"):
    layout = doc.layout(layout_name)

    layout.add_lwpolyline([
        (0, 0),
        (420, 0),
        (420, 297),
        (0, 297),
        (0, 0),
    ], close=True, dxfattribs={"layer": "Defpoints"})

    if orientation == "landscape":
        layout.add_lwpolyline([
            (1.5, 1.5),
            (420 - 1.5, 1.5),
            (420 - 1.5, 297 - 1.5),
            (1.5, 297 - 1.5),
            (1.5, 1.5),
        ], close=True, dxfattribs={"layer": "IES_Object line"})
    else:
        layout.add_lwpolyline([
            (1.5, 1.5),
            (297 - 1.5, 1.5),
            (297 - 1.5, 420 - 1.5),
            (1.5, 420 - 1.5),
            (1.5, 1.5),
        ], close=True, dxfattribs={"layer": "IES_Object line"})
            