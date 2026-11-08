"""Informe construido sobre Referencias/Plantilla_portada.docx.

Conserva de la plantilla la portada (logo UPT), la carátula con el logo del equipo, el control de versiones, el
índice general, la cabecera y el pie, y reproduce su formato de cuerpo (Garamond 11, sangría de 0,5 cm, párrafos
justificados, tablas con borde negro y encabezado gris, rótulos «Tabla N.» en negrita).
"""
import copy
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image
from docx_lib import Informe

GAR = "Garamond"
NEGRO = RGBColor(0, 0, 0)


def _fuente(run, size=None, bold=None, italic=None, color=None, nombre=GAR):
    run.font.name = nombre
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), nombre)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def _set_text(par, texto, run_idx=0):
    """Reemplaza el texto de un párrafo conservando el formato del run indicado."""
    runs = [r for r in par.runs]
    objetivo = runs[run_idx]
    objetivo.text = texto
    for i, r in enumerate(runs):
        if i != run_idx and i > run_idx:
            r.text = ""


class InformePlantilla(Informe):
    def __init__(self, plantilla, datos_portada):
        self.d = Document(plantilla)
        self.n_fig = 0
        self.n_tab = 0
        self._portada(datos_portada)

    # ------------------------------------------------------------- portada y carátula
    def _portada(self, dp):
        body = self.d.element.body
        kids = list(body.iterchildren())
        P = self.d.paragraphs
        # carátula (hoja 1)
        for idx, clave in ((2, "universidad"), (4, "facultad"), (6, "escuela")):
            P[idx].runs[0].text = dp[clave]
            for extra_run in P[idx].runs[1:]:
                extra_run.text = ""
        for r in P[9].runs[1:]:
            r.text = ""
        P[9].runs[0].text = dp["proyecto"]
        _set_text(P[11], " " + dp["curso"], 1)
        _set_text(P[14], dp["docente"], 1)
        # integrantes: reutiliza el formato de la plantilla y añade filas
        base = P[21]._p
        filas = dp["integrantes"]
        for par, (nom, cod) in zip((P[19], P[20], P[21]), filas[:3]):
            self._integrante(par._p, nom, cod)
        anterior = base
        for nom, cod in filas[3:]:
            nuevo = copy.deepcopy(base)
            anterior.addnext(nuevo)
            self._integrante(nuevo, nom, cod)
            anterior = nuevo
        # compensar las filas añadidas quitando párrafos vacíos antes de «Tacna – Perú»
        extra = max(0, len(filas) - 3)
        vacios = [p for p in P[22:27] if not p.text.strip()]
        for p in vacios[:extra]:
            p._p.getparent().remove(p._p)
        # hoja de título de la plantilla (kids 31-46: relleno, títulos y salto de página): no se usa
        for k in kids[31:47]:
            body.remove(k)
        # control de versiones
        tbl = self.d.tables[0]  # control de versiones de la plantilla: no se usa
        tbl._tbl.getparent().remove(tbl._tbl)
        # índice: niveles 1-2
        for it in self.d.element.iter(qn("w:instrText")):
            if it.text and "TOC" in it.text:
                it.text = ' TOC \\o "1-2" \\h \\z \\u'
        # título previo al cuerpo y limpieza del contenido de ejemplo
        kids = list(body.iterchildren())
        titulo = next(k for k in kids if "Informe de Factibilidad" in "".join(t.text or "" for t in k.iter(qn("w:t"))) and k.tag == qn("w:p")
                      and "w:u" in k.xml and "single" in k.xml)
        pos = kids.index(titulo)
        for t in titulo.iter(qn("w:t")):
            t.text = dp["titulo_cuerpo"]
        for k in kids[pos + 2:-1]:
            body.remove(k)
        # cabecera: se retiran los dos logos de la plantilla (equipo y cliente)
        hdr = self.d.sections[0].header
        for dibujo in list(hdr._element.iter(qn("w:drawing"))):
            rids = re.findall(r'r:embed="(\w+)"', __import__("lxml.etree", fromlist=["x"]).tostring(dibujo).decode())
            corrida = dibujo.getparent()
            corrida.getparent().remove(corrida)
            for rid in rids:
                hdr.part.drop_rel(rid)
        cp = self.d.core_properties
        cp.title = dp["titulo_1"]
        cp.subject = dp["titulo_2"]
        cp.author = dp["autor"]
        cp.last_modified_by = dp["autor"]
        cp.comments = ""

    @staticmethod
    def _integrante(p, nombre, codigo):
        run = p.find(qn("w:r"))
        for hijo in list(run):
            if hijo.tag != qn("w:rPr"):
                run.remove(hijo)
        t1 = OxmlElement("w:t")
        t1.set(qn("xml:space"), "preserve")
        t1.text = nombre
        tab = OxmlElement("w:tab")
        t2 = OxmlElement("w:t")
        t2.set(qn("xml:space"), "preserve")
        t2.text = f"({codigo})"
        for e in (t1, tab, t2):
            run.append(e)

    # ------------------------------------------------------------- texto
    def _runs(self, p, text, size=11, color=None, bold_all=False):
        for part in re.split(r"(\*\*.+?\*\*|__.+?__)", text):
            if not part:
                continue
            negrita = bold_all
            cursiva = None
            if part.startswith("**"):
                part, negrita = part[2:-2], True
            elif part.startswith("__"):
                part, cursiva = part[2:-2], True
            r = p.add_run(part)
            _fuente(r, size or 10.5, negrita or None, cursiva, color)
        return p

    @staticmethod
    def _fmt(p, izq=0.5, antes=2, despues=5, linea=1.05, alineacion=WD_ALIGN_PARAGRAPH.JUSTIFY):
        pf = p.paragraph_format
        pf.left_indent = Cm(izq)
        pf.space_before, pf.space_after, pf.line_spacing = Pt(antes), Pt(despues), linea
        p.alignment = alineacion

    def _enc(self, t, nivel):
        h = self.d.add_heading("", nivel)
        _fuente(h.add_run(t), 12 if nivel < 3 else 11, True, nivel == 3, NEGRO)
        return h

    def h1(self, t):
        return self._enc(t, 1)

    def h2(self, t):
        return self._enc(t, 2)

    def h3(self, t):
        return self._enc(t, 3)

    def p(self, t, align=None, size=None, after=None, italic=False, color=None):
        par = self.d.add_paragraph()
        self._runs(par, t, size or 10.5, color)
        self._fmt(par, despues=after if after is not None else 5,
                  alineacion=WD_ALIGN_PARAGRAPH.CENTER if align == "c" else WD_ALIGN_PARAGRAPH.JUSTIFY)
        if italic:
            for r in par.runs:
                r.italic = True
        return par

    def _item(self, marca, t, izq):
        par = self.d.add_paragraph()
        pf = par.paragraph_format
        pf.left_indent, pf.first_line_indent = Cm(izq), Cm(-0.635)
        pf.space_before, pf.space_after, pf.line_spacing = Pt(0), Pt(2), 1.05
        pf.tab_stops.add_tab_stop(Cm(izq))
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r = par.add_run(marca + "\t")
        _fuente(r, 11)
        self._runs(par, t, 11)
        return par

    def bullets(self, items, style=None):
        for it in items:
            self._item("•", it, 1.136)

    def numbered(self, items):
        for i, it in enumerate(items, 1):
            self._item(f"{i}.", it, 1.136)

    def nota(self, t):
        tbl = self.d.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = tbl.rows[0].cells[0]
        self._bg(c, "F2F2F2")
        self._borders(c, "000000", 6)
        c.paragraphs[0].text = ""
        self._runs(c.paragraphs[0], t, 10)
        pf = c.paragraphs[0].paragraph_format
        pf.space_before, pf.space_after, pf.line_spacing = Pt(2), Pt(2), 1.1
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        sp = self.d.add_paragraph()
        sp.paragraph_format.space_after = Pt(2)

    # ------------------------------------------------------------- tablas y figuras
    def tabla(self, titulo, headers, rows, widths, size=8.5, align_center_cols=(), bold_first=False):
        self.n_tab += 1
        cap = self.d.add_paragraph()
        _fuente(cap.add_run(f"Tabla {self.n_tab}. {titulo}"), 10, True)
        cap.paragraph_format.keep_with_next = True
        cap.paragraph_format.space_before, cap.paragraph_format.space_after = Pt(6), Pt(3)
        cap.paragraph_format.line_spacing = 1.0
        t = self.d.add_table(rows=1, cols=len(headers))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        t._tbl.tblPr.append(lay)
        tam = max(size, 8.5) if size >= 8.5 else size + 0.25
        for i, h in enumerate(headers):
            c = t.rows[0].cells[i]
            c.width = Cm(widths[i])
            self._bg(c, "D9D9D9")
            self._borders(c, "000000", 6)
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            par = c.paragraphs[0]
            par.text = ""
            _fuente(par.add_run(h), min(tam, 9.5), True)
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_after = Pt(0)
            par.paragraph_format.line_spacing = 1.0
        trPr = t.rows[0]._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        trPr.append(th)
        for row in rows:
            cells = t.add_row().cells
            trPr = t.rows[-1]._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit")
            cs.set(qn("w:val"), "true")
            trPr.append(cs)
            for i, val in enumerate(row):
                c = cells[i]
                c.width = Cm(widths[i])
                self._borders(c, "000000", 6)
                c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                for li, line in enumerate(str(val).split("\n")):
                    par = c.paragraphs[0] if li == 0 else c.add_paragraph()
                    self._runs(par, line, tam, bold_all=bold_first and i == 0)
                    par.paragraph_format.space_after = Pt(0)
                    par.paragraph_format.line_spacing = 1.0
                    par.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in align_center_cols else WD_ALIGN_PARAGRAPH.LEFT
        sp = self.d.add_paragraph()
        sp.paragraph_format.space_after = Pt(4)
        sp.paragraph_format.line_spacing = 0.8
        return t

    def figura(self, path, titulo, ancho_cm=15.0):
        self.n_fig += 1
        par = self.d.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.space_after = Pt(0)
        par.add_run().add_picture(path, width=Cm(min(ancho_cm, 15.0)) if ancho_cm <= 15.5 else Cm(ancho_cm))
        cap = self.d.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _fuente(cap.add_run(f"Figura {self.n_fig}. {titulo}"), 10, True)
        cap.paragraph_format.space_before, cap.paragraph_format.space_after = Pt(3), Pt(8)

    def figuras_apaisadas(self, items, max_w_cm=23.0, max_h_cm=14.6):
        super().figuras_apaisadas(items, max_w_cm, max_h_cm)

    def figura_apaisada(self, path, titulo, max_w_cm=23.0, max_h_cm=14.6):
        super().figura_apaisada(path, titulo, max_w_cm, max_h_cm)

    def _orient(self, landscape):
        sec = self.d.add_section(WD_SECTION.NEW_PAGE)
        if landscape:
            sec.orientation = WD_ORIENT.LANDSCAPE
            sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
            sec.left_margin = sec.right_margin = Cm(2.5)
            sec.top_margin, sec.bottom_margin = Cm(2.2), Cm(1.8)
        else:
            sec.orientation = WD_ORIENT.PORTRAIT
            sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
            sec.left_margin = sec.right_margin = Cm(3.0)
            sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.5)
        sec.different_first_page_header_footer = False
        for pg in sec._sectPr.findall(qn("w:pgNumType")):
            sec._sectPr.remove(pg)
        sec.header.is_linked_to_previous = True
        sec.footer.is_linked_to_previous = True
