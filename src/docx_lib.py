"""Utilidades para construir el documento técnico con python-docx."""
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
BLUE = RGBColor(0x2E, 0x6F, 0xBA)
GRAY = RGBColor(0x55, 0x5F, 0x6D)
FONT = "Calibri"


def _font(style, name=FONT, size=None, bold=None, color=None, italic=None):
    f = style.font
    f.name = name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(a), name)
    if size:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color is not None:
        f.color.rgb = color


class Informe:
    def __init__(self):
        self.d = Document()
        self.n_fig = 0
        self.n_tab = 0
        self._estilos()
        sec = self.d.sections[0]
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        sec.left_margin = sec.right_margin = Cm(2.3)
        sec.top_margin, sec.bottom_margin = Cm(2.3), Cm(2.2)
        sec.different_first_page_header_footer = True
        self._cabecera_pie(sec)

    # ---------------------------------------------------------- estilos
    def _estilos(self):
        st = self.d.styles
        _font(st["Normal"], size=10.5)
        pf = st["Normal"].paragraph_format
        pf.space_after, pf.space_before, pf.line_spacing = Pt(5), Pt(0), 1.12
        for nm, sz, col, sb, sa in (("Heading 1", 16, NAVY, 16, 6), ("Heading 2", 12.5, BLUE, 11, 4), ("Heading 3", 11, NAVY, 8, 3)):
            _font(st[nm], size=sz, bold=True, color=col)
            st[nm].paragraph_format.space_before = Pt(sb)
            st[nm].paragraph_format.space_after = Pt(sa)
            st[nm].paragraph_format.keep_with_next = True
        for nm in ("List Bullet", "List Number"):
            _font(st[nm], size=10.5)
            st[nm].paragraph_format.space_after = Pt(2)
            st[nm].paragraph_format.line_spacing = 1.08
        from docx.enum.style import WD_STYLE_TYPE
        for nm, sz, bold, ind in (("toc 1", 10, True, 0), ("toc 2", 9.5, False, 0.6)):
            try:
                e = st[nm]
            except KeyError:
                e = st.add_style(nm, WD_STYLE_TYPE.PARAGRAPH)
                e.base_style = st["Normal"]
            _font(e, size=sz, bold=bold)
            e.paragraph_format.space_after = Pt(1)
            e.paragraph_format.space_before = Pt(3 if bold else 0)
            e.paragraph_format.left_indent = Cm(ind)
            e.paragraph_format.line_spacing = 1.0
        _font(st["Caption"], size=9, bold=False, italic=True, color=GRAY)
        st["Caption"].paragraph_format.space_after = Pt(8)
        st["Caption"].paragraph_format.space_before = Pt(3)

    def _campo(self, par, instr):
        r = par.add_run()
        for t, txt in (("begin", None), (None, instr), ("separate", None), ("end", None)):
            if t:
                fc = OxmlElement("w:fldChar")
                fc.set(qn("w:fldCharType"), t)
                r._r.append(fc)
            else:
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = txt
                r._r.append(it)
        return r

    def _cabecera_pie(self, sec):
        h = sec.header
        h.is_linked_to_previous = False
        p = h.paragraphs[0]
        p.text = ""
        r = p.add_run("Diseño de la Solución Tecnológica · Plataforma Kubernetes de Alta Disponibilidad")
        r.font.size, r.font.color.rgb, r.italic = Pt(8.5), GRAY, True
        pPr = p._p.get_or_add_pPr()
        bd = OxmlElement("w:pBdr")
        b = OxmlElement("w:bottom")
        for k, v in (("w:val", "single"), ("w:sz", "4"), ("w:space", "1"), ("w:color", "9AA5B4")):
            b.set(qn(k), v)
        bd.append(b)
        pPr.append(bd)
        f = sec.footer
        f.is_linked_to_previous = False
        p = f.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run("Sistemas Operativos II · II Unidad · Página ")
        r.font.size, r.font.color.rgb = Pt(8.5), GRAY
        rr = self._campo(p, "PAGE")
        rr.font.size, rr.font.color.rgb = Pt(8.5), GRAY

    # ---------------------------------------------------------- texto
    def _runs(self, p, text, size=None, color=None):
        for part in re.split(r"(\*\*.+?\*\*|__.+?__)", text):
            if not part:
                continue
            if part.startswith("**"):
                r = p.add_run(part[2:-2])
                r.bold = True
            elif part.startswith("__"):
                r = p.add_run(part[2:-2])
                r.italic = True
            else:
                r = p.add_run(part)
            if size:
                r.font.size = Pt(size)
            if color is not None:
                r.font.color.rgb = color
        return p

    def h1(self, t):
        return self.d.add_heading(t, 1)

    def h2(self, t):
        return self.d.add_heading(t, 2)

    def h3(self, t):
        return self.d.add_heading(t, 3)

    def p(self, t, align=None, size=None, after=None, italic=False, color=None):
        par = self.d.add_paragraph()
        self._runs(par, t, size, color)
        if align == "j":
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif align == "c":
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if after is not None:
            par.paragraph_format.space_after = Pt(after)
        if italic:
            for r in par.runs:
                r.italic = True
        return par

    def jp(self, t):
        return self.p(t, "j")

    def bullets(self, items, style="List Bullet"):
        for it in items:
            par = self.d.add_paragraph(style=style)
            self._runs(par, it)
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    def numbered(self, items):
        """Lista numerada que reinicia en 1 en cada llamada."""
        numbering = self.d.part.numbering_part.numbering_definitions._numbering
        base_id = self.d.styles["List Number"].element.pPr.numPr.numId.val
        abstract_id = numbering.num_having_numId(base_id).abstractNumId.val
        nuevo = numbering.add_num(abstract_id)
        nuevo.add_lvlOverride(ilvl=0).add_startOverride(1)
        for it in items:
            par = self.d.add_paragraph(style="List Number")
            self._runs(par, it)
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            numPr = par._p.get_or_add_pPr().get_or_add_numPr()
            numPr.get_or_add_ilvl().val = 0
            numPr.get_or_add_numId().val = nuevo.numId

    def nota(self, t):
        """Recuadro de nota / supuesto."""
        tbl = self.d.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = tbl.rows[0].cells[0]
        self._bg(c, "EAF1FB")
        self._borders(c, "2E6FBA", left=18, others=0)
        c.paragraphs[0].text = ""
        self._runs(c.paragraphs[0], t, size=9.5)
        c.paragraphs[0].paragraph_format.space_after = Pt(2)
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)

    def code(self, texto, titulo=None):
        if titulo:
            cp = self.d.add_paragraph()
            cp.paragraph_format.keep_with_next = True
            cp.paragraph_format.space_after = Pt(2)
            rr = cp.add_run(titulo)
            rr.bold, rr.font.size, rr.font.color.rgb = True, Pt(9), NAVY
        tbl = self.d.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = tbl.rows[0].cells[0]
        self._bg(c, "F4F5F7")
        self._borders(c, "C9CED6")
        for i, line in enumerate(texto.strip("\n").split("\n")):
            par = c.paragraphs[0] if i == 0 else c.add_paragraph()
            run = par.add_run(line if line else " ")
            run.font.name = "Consolas"
            run._r.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Consolas")
            run.font.size = Pt(7.5)
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = 1.0
        sp = self.d.add_paragraph()
        sp.paragraph_format.space_after = Pt(3)

    def salto(self):
        self.d.add_page_break()

    # ---------------------------------------------------------- tablas
    def _bg(self, cell, hexcolor):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), hexcolor)
        tcPr.append(shd)

    def _borders(self, cell, color="B8C2D0", sz=4, left=None, others=None):
        tcPr = cell._tc.get_or_add_tcPr()
        b = OxmlElement("w:tcBorders")
        for side in ("top", "left", "bottom", "right"):
            e = OxmlElement(f"w:{side}")
            size = sz
            if side == "left" and left is not None:
                size = left
            elif others is not None and side != "left":
                size = others
            e.set(qn("w:val"), "single" if size else "nil")
            e.set(qn("w:sz"), str(size))
            e.set(qn("w:color"), color)
            b.append(e)
        tcPr.append(b)

    def tabla(self, titulo, headers, rows, widths, size=8.5, align_center_cols=(), bold_first=False):
        self.n_tab += 1
        cap = self.d.add_paragraph(style="Caption")
        r = cap.add_run(f"Tabla {self.n_tab}. ")
        r.bold = True
        cap.add_run(titulo)
        cap.paragraph_format.keep_with_next = True
        cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cap.paragraph_format.space_after = Pt(3)
        t = self.d.add_table(rows=1, cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        tblPr = t._tbl.tblPr
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        tblPr.append(lay)
        for i, h in enumerate(headers):
            c = t.rows[0].cells[i]
            c.width = Cm(widths[i])
            self._bg(c, "1F3A5F")
            self._borders(c, "1F3A5F")
            c.paragraphs[0].text = ""
            rr = c.paragraphs[0].add_run(h)
            rr.bold, rr.font.size, rr.font.color.rgb = True, Pt(size), RGBColor(255, 255, 255)
            c.paragraphs[0].paragraph_format.space_after = Pt(1)
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        trPr = t.rows[0]._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        trPr.append(th)
        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            trPr = t.rows[-1]._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit")
            cs.set(qn("w:val"), "true")
            trPr.append(cs)
            for i, val in enumerate(row):
                c = cells[i]
                c.width = Cm(widths[i])
                self._bg(c, "F3F6FA" if ri % 2 else "FFFFFF")
                self._borders(c)
                c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                lines = str(val).split("\n")
                c.paragraphs[0].text = ""
                for li, line in enumerate(lines):
                    par = c.paragraphs[0] if li == 0 else c.add_paragraph()
                    self._runs(par, line, size=size)
                    par.paragraph_format.space_after = Pt(1)
                    par.paragraph_format.line_spacing = 1.0
                    if i in align_center_cols:
                        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    if bold_first and i == 0:
                        for rn in par.runs:
                            rn.bold = True
        sp = self.d.add_paragraph()
        sp.paragraph_format.space_after = Pt(4)
        return t

    # ---------------------------------------------------------- figuras
    def figura(self, path, titulo, ancho_cm=16.0):
        self.n_fig += 1
        par = self.d.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.space_after = Pt(0)
        par.add_run().add_picture(path, width=Cm(ancho_cm))
        cap = self.d.add_paragraph(style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(f"Figura {self.n_fig}. ")
        r.bold = True
        cap.add_run(titulo)

    def figura_apaisada(self, path, titulo, max_w_cm=24.5, max_h_cm=15.3):
        """Inserta la figura en una página horizontal dedicada y vuelve a vertical."""
        self._orient(landscape=True)
        w, h = Image.open(path).size
        ancho = min(max_w_cm, max_h_cm * w / h)
        self.figura(path, titulo, ancho)
        self._orient(landscape=False)

    def figuras_apaisadas(self, items, max_w_cm=24.5, max_h_cm=15.3):
        """Varias figuras seguidas en páginas horizontales (una por página)."""
        self._orient(landscape=True)
        for i, (path, titulo) in enumerate(items):
            if i:
                self.d.add_page_break()
            w, h = Image.open(path).size
            self.figura(path, titulo, min(max_w_cm, max_h_cm * w / h))
        self._orient(landscape=False)

    def _orient(self, landscape):
        sec = self.d.add_section(WD_SECTION.NEW_PAGE)
        if landscape:
            sec.orientation = WD_ORIENT.LANDSCAPE
            sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
            sec.left_margin = sec.right_margin = Cm(2.0)
            sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(1.8)
        else:
            sec.orientation = WD_ORIENT.PORTRAIT
            sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
            sec.left_margin = sec.right_margin = Cm(2.3)
            sec.top_margin, sec.bottom_margin = Cm(2.3), Cm(2.2)
        sec.different_first_page_header_footer = False
        sec.header.is_linked_to_previous = True
        sec.footer.is_linked_to_previous = True

    # ---------------------------------------------------------- índice
    def toc(self):
        par = self.d.add_paragraph()
        self._campo(par, 'TOC \\o "1-2" \\h \\z \\u')

    def guardar(self, ruta):
        self.d.save(ruta)
