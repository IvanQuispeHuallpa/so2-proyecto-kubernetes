"""Construye la presentación de la II Unidad (.pptx, 14 diapositivas)."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
import datos

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DG = os.path.join(BASE, "diagramas")
C = lambda h: RGBColor.from_string(h)
NAVY, BLUE, TEAL, ORANGE, RED, GREEN, PURPLE, GRAY, INK = (C(x) for x in
    ("1F3A5F", "2E6FBA", "1A9E8F", "E08A1E", "C0392B", "3C9D5D", "7B5EA7", "6B7280", "1B2430"))
LIGHT = C("F3F6FA")
FONT = "Garamond"
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
n_slide = [0]


def tb(slide, x, y, w, h, text="", size=14, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size, r.font.bold, r.font.italic, r.font.color.rgb, r.font.name = Pt(size), bold, italic, color, FONT
    return box


def bullets(slide, x, y, w, h, items, size=15, color=INK, gap=6, bullet_color=BLUE):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        dot = p.add_run()
        dot.text = "■  "
        dot.font.size, dot.font.color.rgb, dot.font.name = Pt(size - 6), bullet_color, FONT
        if isinstance(it, tuple):
            b = p.add_run()
            b.text = it[0] + " "
            b.font.bold, b.font.size, b.font.color.rgb, b.font.name = True, Pt(size), NAVY, FONT
            it = it[1]
        r = p.add_run()
        r.text = it
        r.font.size, r.font.color.rgb, r.font.name = Pt(size), color, FONT
    return box


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    return s


def nueva(titulo, subtitulo=None, notas=None):
    s = prs.slides.add_slide(BLANK)
    n_slide[0] += 1
    rect(s, 0, 0, 13.333, 0.12, NAVY, shape=MSO_SHAPE.RECTANGLE)
    tb(s, 0.6, 0.32, 12.1, 0.7, titulo, 28, True, NAVY)
    if subtitulo:
        tb(s, 0.6, 0.98, 12.1, 0.4, subtitulo, 14, False, GRAY, italic=True)
    rect(s, 0.65, 1.42, 0.9, 0.05, BLUE, shape=MSO_SHAPE.RECTANGLE)
    tb(s, 0.6, 7.08, 9, 0.3, "Sistemas Operativos II · II Unidad · Plataforma Kubernetes de Alta Disponibilidad", 10, False, GRAY)
    tb(s, 12.0, 7.08, 0.8, 0.3, str(n_slide[0]), 10, True, GRAY, PP_ALIGN.RIGHT)
    if notas:
        s.notes_slide.notes_text_frame.text = notas
    return s


def imagen(slide, nombre, x, y, max_w, max_h):
    path = os.path.join(DG, nombre)
    w, h = Image.open(path).size
    ancho = min(max_w, max_h * w / h)
    alto = ancho * h / w
    pic = slide.shapes.add_picture(path, Inches(x + (max_w - ancho) / 2), Inches(y + (max_h - alto) / 2), Inches(ancho), Inches(alto))
    pic.line.color.rgb = C("D5D9E0")
    pic.line.width = Pt(0.75)
    return pic


def tarjeta(slide, x, y, w, h, grande, etiqueta, color):
    rect(slide, x, y, w, h, LIGHT)
    rect(slide, x, y, 0.09, h, color, shape=MSO_SHAPE.RECTANGLE)
    tb(slide, x + 0.2, y + 0.08, w - 0.3, h * 0.55, grande, 28, True, color, anchor=MSO_ANCHOR.MIDDLE)
    tb(slide, x + 0.2, y + h * 0.58, w - 0.3, h * 0.4, etiqueta, 12, False, INK)


def tabla(slide, x, y, w, filas, anchos, size=12, alto_fila=0.4, cabecera=True):
    shape = slide.shapes.add_table(len(filas), len(filas[0]), Inches(x), Inches(y), Inches(w), Inches(alto_fila * len(filas)))
    t = shape.table
    for j, aw in enumerate(anchos):
        t.columns[j].width = Inches(aw)
    for i, fila in enumerate(filas):
        t.rows[i].height = Inches(alto_fila)
        for j, val in enumerate(fila):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.08)
            c.margin_top = c.margin_bottom = Inches(0.04)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            if i == 0 and cabecera:
                c.fill.fore_color.rgb = NAVY
            else:
                c.fill.fore_color.rgb = LIGHT if i % 2 == 0 else C("FFFFFF")
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = str(val)
            r.font.size, r.font.name = Pt(size), FONT
            if i == 0 and cabecera:
                r.font.bold, r.font.color.rgb = True, C("FFFFFF")
            else:
                r.font.color.rgb = INK
                if j == 0:
                    r.font.bold = True
    return t


def money(v):
    return f"US$ {v:,}".replace(",", " ")


# ------------------------------------------------------------------ 1 portada (formato de la plantilla)
s = prs.slides.add_slide(BLANK)
n_slide[0] += 1
s.shapes.add_picture(os.path.join(ASSETS, "logo_upt.png"), Inches(6.2), Inches(0.25), Inches(0.95), Inches(1.28))
CEN = PP_ALIGN.CENTER
tb(s, 0.5, 1.6, 12.3, 0.55, "UNIVERSIDAD PRIVADA DE TACNA", 28, True, INK, CEN)
tb(s, 0.5, 2.15, 12.3, 0.45, "FACULTAD DE INGENIERÍA", 22, True, INK, CEN)
tb(s, 0.5, 2.6, 12.3, 0.4, "Escuela Profesional de Ingeniería de Sistemas", 20, True, INK, CEN)
tb(s, 1.2, 3.2, 10.9, 0.9, "Proyecto Plataforma de orquestación de contenedores con Kubernetes de alta disponibilidad", 22, True, INK, CEN)
bl = tb(s, 0.5, 4.2, 12.3, 0.4, "", 18, False, INK, CEN)
p = bl.text_frame.paragraphs[0]
for txt, neg in (("Curso: ", True), ("Sistemas Operativos II", False)):
    r = p.add_run()
    r.text = txt
    r.font.size, r.font.bold, r.font.name, r.font.color.rgb = Pt(18), neg, FONT, INK
bl = tb(s, 0.5, 4.6, 12.3, 0.4, "", 18, False, INK, CEN)
p = bl.text_frame.paragraphs[0]
for txt, neg in (("Docente: ", True), ("Renzo Alberto Taco Coayla", False)):
    r = p.add_run()
    r.text = txt
    r.font.size, r.font.bold, r.font.name, r.font.color.rgb = Pt(18), neg, FONT, INK
tb(s, 1.2, 5.1, 3, 0.35, "Integrantes:", 16, True, INK)
izq = ["Cortez Apaza, Sebastian Alejandro  (2023078699)", "Quispe Huallpa, Ivan  (2023078707)", "Vilca Barrientos, Luis Fernando  (2023078329)"]
der = ["Ludeña Bedoya, Milagros Shadu  (código)", "Jimenez Laura, Carlos Rai  (código)", "Cutipa Flores, Arturo Sebastian  (código)"]
for k, lista in enumerate((izq, der)):
    cuadro = tb(s, 1.2 + k * 5.6, 5.45, 5.5, 1.0, "", 13, False, INK)
    tf = cuadro.text_frame
    for i, nombre in enumerate(lista):
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = par.add_run()
        r.text = nombre
        r.font.size, r.font.name, r.font.color.rgb = Pt(13), FONT, INK
tb(s, 0.5, 6.6, 12.3, 0.4, "Tacna – Perú  ·  2026", 18, True, INK, CEN)
s.notes_slide.notes_text_frame.text = "Portada según la plantilla institucional. Completar los códigos de los integrantes pendientes."

# ------------------------------------------------------------------ 2 problema
s = nueva("El problema y el objetivo", "Escenario de referencia: organización mediana con ≈ 250 usuarios y 13 aplicaciones web",
          "El escenario es supuesto (el enunciado no fija una organización) y está documentado como tal en el informe, Tabla 2. Los datos de despliegue de 45 min provienen del caso de una entidad estatal peruana (Aguilar y García, 2024).")
rect(s, 0.6, 1.75, 5.9, 4.95, LIGHT)
tb(s, 0.8, 1.85, 5.5, 0.4, "Situación actual", 18, True, RED)
bullets(s, 0.8, 2.35, 5.55, 4.3, [
    "Aplicaciones en VM individuales, sin redundancia",
    "Despliegues manuales de 30–45 min, sin reversión",
    "Respaldos manuales y sin pruebas de restauración",
    "Sin monitoreo centralizado ni alertas",
    "Red plana, accesos compartidos, sin escaneo",
], 15, gap=9, bullet_color=RED)
rect(s, 6.85, 1.75, 5.9, 2.35, LIGHT)
tb(s, 7.05, 1.85, 5.5, 0.4, "Necesidad", 18, True, TEAL)
bullets(s, 7.05, 2.3, 5.55, 1.8, ["Continuidad: disponibilidad ≥ 99,9 %", "Agilidad de despliegue y reversión inmediata",
                                  "Seguridad, trazabilidad y recuperabilidad"], 15, gap=5, bullet_color=TEAL)
rect(s, 6.85, 4.3, 5.9, 2.4, NAVY)
tb(s, 7.05, 4.4, 5.5, 0.4, "Objetivo general", 18, True, C("9FC3EC"))
tb(s, 7.05, 4.85, 5.5, 1.8, "Diseñar una plataforma Kubernetes con alta disponibilidad, seguridad, observabilidad y operación automatizada, sustentando cada decisión en la investigación bibliográfica.", 16, False, C("FFFFFF"))

# ------------------------------------------------------------------ 3 investigación → diseño
s = nueva("De la investigación al diseño", "Hallazgos de la I Unidad y la decisión que originan",
          "Trazabilidad completa en la Tabla 3 del informe (16 filas). Aquí se muestran los hallazgos con más peso en la arquitectura.")
filas = [["Hallazgo", "Fuente", "Decisión de diseño"],
         ["etcd pierde rendimiento al crecer el clúster", "Jeffery et al., 2021", "etcd de 3 miembros sobre SSD"],
         ["Raft no tolera fallas bizantinas", "Diouf et al., 2020", "Riesgo aceptado + hardening y auditoría"],
         ["Recuperación nativa de apps con estado es lenta (−50 % con controlador)", "Vayghan et al., 2020", "PostgreSQL con operador CloudNativePG"],
         ["Kubernetes completo rinde mejor con carga sostenida", "Kjorveziroski, 2022; Koziolek, 2023", "kubeadm (K3s solo contingencia)"],
         ["Capa eBPF + límites mitigan DDoS y picos (−32 % timeouts)", "Jiang y Milani, 2026", "Cilium + HPA con tope + límite de tasa"],
         ["Patrón HA: 3 nodos de control + Keepalived/HAProxy + Ansible", "Domínguez, 2024; Jovaní, 2023", "Plano de control y balanceo del diseño"],
         ["Seguridad por capas 4C y gestión de riesgos", "Simón, 2021; Guardiola, 2020", "Diseño de seguridad en 4 capas"]]
tabla(s, 0.6, 1.8, 12.1, filas, [5.6, 3.1, 3.4], size=13, alto_fila=0.62)

# ------------------------------------------------------------------ 4 requerimientos
s = nueva("Requerimientos medibles", "16 funcionales y 21 no funcionales, cada uno con una prueba asociada",
          "Los requerimientos no funcionales son criterios de aceptación para la III Unidad. Referencia de despliegue ≤ 10 min: Aguilar y García (2024).")
tarjeta(s, 0.6, 1.85, 2.9, 1.5, "≥ 99,9 %", "Disponibilidad mensual\n(≤ 43,8 min de caída)", GREEN)
tarjeta(s, 3.7, 1.85, 2.9, 1.5, "≤ 5 min", "RPO de bases de datos\n(WAL continuo)", TEAL)
tarjeta(s, 6.8, 1.85, 2.9, 1.5, "≤ 30 min", "RTO de un namespace\n(reconstrucción total ≤ 4 h)", BLUE)
tarjeta(s, 9.9, 1.85, 2.8, 1.5, "≤ 500 ms", "Latencia p95 a 200 req/s\n(errores < 1 %)", ORANGE)
tarjeta(s, 0.6, 3.55, 2.9, 1.5, "≤ 10 s", "Conmutación de la IP\nvirtual del API", PURPLE)
tarjeta(s, 3.7, 3.55, 2.9, 1.5, "3 → 10", "Réplicas del HPA en\n≤ 3 min (carga 4×)", NAVY)
tarjeta(s, 6.8, 3.55, 2.9, 1.5, "N+1", "Capacidad con un worker\no un host caído", RED)
tarjeta(s, 9.9, 3.55, 2.8, 1.5, "≥ 90 %", "Controles CIS aplicables\nen PASS (kube-bench)", GREEN)
bullets(s, 0.6, 5.3, 12.1, 1.6, [
    ("Funcionales:", "orquestación, API con VIP, autorrecuperación, almacenamiento replicado, BD con failover, RBAC, NetworkPolicy, observabilidad, respaldo, CI/CD."),
    ("Restricciones:", "100 % código abierto; laboratorio a escala en la III Unidad; API, kubelet y etcd nunca expuestos a Internet."),
], 14, gap=6)

# ------------------------------------------------------------------ 5 arquitectura
s = nueva("Arquitectura lógica", "Capas de acceso, plano de control, cómputo y servicios; observabilidad, seguridad y automatización transversales",
          "Tres nodos de control con etcd apilado, tres workers, dos balanceadores. Cilium como CNI, MetalLB + Traefik para servicios, Longhorn para almacenamiento y CloudNativePG para bases de datos.")
imagen(s, "01_arquitectura_general.png", 0.5, 1.65, 8.9, 5.3)
rect(s, 9.6, 1.75, 3.2, 5.0, LIGHT)
tb(s, 9.75, 1.82, 2.9, 0.4, "Decisiones clave", 16, True, NAVY)
bullets(s, 9.75, 2.3, 2.95, 4.4, [
    "kubeadm + containerd sobre Rocky Linux 9",
    "etcd apilado de 3 miembros",
    "HAProxy + Keepalived: VIP del API",
    "MetalLB + Traefik: VIP de servicios",
    "Cilium: red y NetworkPolicy",
    "Longhorn y CloudNativePG",
    "Prometheus, Grafana y Loki",
], 12, gap=4)

# ------------------------------------------------------------------ 6 HA
s = nueva("Alta disponibilidad: qué pasa cuando algo falla", "Tres dominios de falla físicos y capacidad N+1",
          "Cada fila corresponde a una prueba del plan (PH-01 a PH-06). La pérdida de quórum es un escenario controlado que se prueba en PH-03.")
filas = [["Falla", "Efecto", "Mecanismo", "Tiempo"],
         ["lb01 (balanceador activo)", "Ninguno", "Keepalived mueve la VIP (VRRP)", "≤ 10 s"],
         ["Un nodo de control", "API disponible", "HAProxy lo excluye; etcd reelige líder", "≤ 10 s"],
         ["Un worker", "Pods reprogramados", "tolerationSeconds + scheduler", "≤ 5 min"],
         ["Un host físico", "Sin corte del servicio", "Réplicas en otros hosts (N+1)", "Sin corte"],
         ["Primario de PostgreSQL", "Escrituras en pausa", "CloudNativePG promueve réplica", "≤ 30 s"],
         ["2 nodos de control", "API solo lectura; apps siguen", "Restaurar nodo o snapshot de etcd", "≤ 4 h"],
         ["Switch / firewall", "Corte de red (SPOF aceptado)", "Equipo de repuesto en frío", "≤ 2 h"]]
tabla(s, 0.6, 1.8, 8.2, filas, [2.3, 1.9, 2.9, 1.1], size=12, alto_fila=0.58)
rect(s, 9.1, 1.8, 3.65, 4.65, LIGHT)
tb(s, 9.25, 1.88, 3.4, 0.4, "Reglas de ubicación", 16, True, NAVY)
bullets(s, 9.25, 2.35, 3.4, 4.0, [
    "≥ 3 réplicas repartidas por host (topologySpread)",
    "PodDisruptionBudget: minAvailable = 2",
    "BD: 1 primario + 2 réplicas; volumen con 2 copias",
    "requests/limits y PriorityClasses obligatorios",
    "Capacidad: 15 vCPU / 36 GB caben con un worker caído",
], 13, gap=6)

# ------------------------------------------------------------------ 7 infraestructura
s = nueva("Infraestructura y despliegue", "3 hosts Proxmox VE · 9 máquinas virtuales · Rocky Linux 9",
          "Cada host aloja como máximo un nodo de control, un worker y un balanceador. Hardware y precios son estimaciones referenciales del equipo.")
imagen(s, "04_despliegue.png", 0.5, 1.65, 7.4, 5.3)
tabla(s, 8.15, 1.75, 4.6, [["Recurso", "Especificación"],
                           ["Hosts (×3)", "16 núcleos · 128 GB ECC · 2×10 GbE"],
                           ["Disco por host", "2×480 GB SO + 2×1,92 TB (ZFS espejo)"],
                           ["Control (×3)", "4 vCPU · 8 GB · 80 GB"],
                           ["Worker (×3)", "12 vCPU · 32 GB · 100+200 GB"],
                           ["Balanceador (×2)", "2 vCPU · 2 GB"],
                           ["Respaldo", "4×8 TB ZFS · MinIO (S3)"],
                           ["Energía", "UPS online 3 kVA"]], [1.55, 3.05], size=11.5, alto_fila=0.52)
tb(s, 8.15, 6.05, 4.6, 0.8, "Perfil de laboratorio (III Unidad): 9 VM, 15 vCPU y ≈ 24 GB en una estación de ≥ 32 GB.", 12, False, GRAY, italic=True)

# ------------------------------------------------------------------ 8 red
s = nueva("Diseño de red", "Segmentación en 7 VLAN, firewall con denegación por defecto y acceso remoto por VPN + bastión",
          "El firewall es el gateway de todas las VLAN. API (6443), kubelet (10250), etcd (2379-2380) y consola de Proxmox (8006) nunca se publican en Internet.")
imagen(s, "02_topologia_red.png", 0.5, 1.65, 8.0, 5.3)
tabla(s, 8.75, 1.75, 4.05, [["VLAN", "Uso", "Subred"],
                            ["10", "Gestión", "10.10.10.0/24"],
                            ["20", "Plano de control", "10.10.20.0/24"],
                            ["30", "Workers", "10.10.30.0/24"],
                            ["40", "Almacenamiento", "10.10.40.0/24"],
                            ["50", "Servicios (MetalLB)", "10.10.50.0/24"],
                            ["60", "Respaldo", "10.10.60.0/24"],
                            ["100", "Usuarios", "10.10.100.0/23"]], [0.7, 1.75, 1.6], size=11.5, alto_fila=0.42)
bullets(s, 8.75, 5.25, 4.05, 1.7, ["VIP del API 10.10.20.10 · VIP de servicios 10.10.50.100",
                                   "Pods 10.244.0.0/16 · Servicios 10.96.0.0/12",
                                   "VPN WireGuard + MFA → bastión SSH"], 12, gap=3)

# ------------------------------------------------------------------ 9 seguridad
s = nueva("Diseño de seguridad", "Gestión de riesgos y defensa en profundidad (modelo 4C)",
          "Tres riesgos críticos iniciales (R04, R05, R06) bajan a nivel medio o bajo; se aceptan explícitamente el punto único de red (R03) y la falla bizantina (R11), que Raft no cubre (Diouf et al., 2020).")
imagen(s, "03_seguridad.png", 0.5, 1.65, 8.3, 5.3)
tarjeta(s, 9.05, 1.75, 1.75, 1.2, "14", "riesgos valorados", RED)
tarjeta(s, 11.0, 1.75, 1.75, 1.2, "11", "amenazas (STRIDE)", ORANGE)
bullets(s, 9.05, 3.2, 3.75, 3.7, [
    ("Riesgo → controles:", "3 críticos pasan a nivel medio o bajo"),
    ("Accesos:", "RBAC mínimo privilegio, certificados de 30 días, MFA"),
    ("Clúster:", "PSA restricted, NetworkPolicy default-deny, Secrets cifrados"),
    ("Contenedor:", "Trivy, no root, rootfs de solo lectura, Falco"),
    ("Aceptados:", "switch único (R03) y falla bizantina (R11)"),
], 12.5, gap=5)

# ------------------------------------------------------------------ 10 operación y respaldo
s = nueva("Operación, respaldo y monitoreo", "Roles definidos, regla 3-2-1 y alertas accionables",
          "Metas: RPO ≤ 5 min (BD), RTO ≤ 30 min (namespace), reconstrucción ≤ 4 h. Las pruebas de restauración son trimestrales.")
filas = [["Elemento", "Herramienta", "Frecuencia", "RPO"],
         ["Estado del clúster", "etcd snapshot", "Cada 6 h", "6 h"],
         ["Recursos y volúmenes", "Velero + MinIO", "Diario", "24 h"],
         ["Bases de datos", "CNPG base + WAL", "Continuo", "≤ 5 min"],
         ["VM de infraestructura", "Respaldo Proxmox", "Semanal", "7 días"],
         ["Copia fuera de sitio", "restic/rclone", "Semanal", "7 días"]]
tb(s, 0.6, 1.7, 6.3, 0.4, "Respaldo y recuperación", 17, True, NAVY)
tabla(s, 0.6, 2.15, 6.3, filas, [2.1, 1.8, 1.3, 1.1], size=12, alto_fila=0.48)
tb(s, 7.2, 1.7, 5.5, 0.4, "Modelo operativo", 17, True, NAVY)
bullets(s, 7.2, 2.15, 5.5, 2.6, [
    ("Roles:", "jefe de TI, arquitecto, 2 administradores, redes/seguridad, desarrollo y soporte N1 (matriz RACI)"),
    ("Mantenimiento:", "parches mensuales, upgrade trimestral, pruebas de restauración trimestrales, game day semestral"),
    ("Incidentes:", "P1 respuesta 15 min / resolución 2 h; 6 runbooks y revisión sin culpables"),
], 13, gap=6)
rect(s, 0.6, 5.3, 12.15, 1.55, LIGHT)
tb(s, 0.8, 5.35, 11.8, 0.4, "Observabilidad: Prometheus + Alertmanager · Grafana · Loki + Alloy · Hubble", 15, True, PURPLE)
tb(s, 0.8, 5.85, 11.8, 0.95, "10 alertas mínimas (nodo no listo, etcd sin líder, latencia del API, failover de VIP, volumen degradado, certificado por vencer, respaldo fallido, eventos de Falco…) enviadas por correo y Telegram, con auditoría de la API retenida 90 días.", 13, False, INK)

# ------------------------------------------------------------------ 11 plan de implementación
s = nueva("Plan de implementación (III Unidad)", "8 semanas · 11 actividades · entorno de laboratorio a escala con la topología lógica completa",
          "Dependencias: A2→A3→A4→A5, luego A6 y A7 en paralelo, A8 y A9, y finalmente A10 y A11. Todo cambio se versiona en Git; no se añaden componentes ajenos al diseño sin justificación documentada.")
imagen(s, "06_cronograma.png", 0.5, 1.7, 8.4, 4.4)
rect(s, 9.15, 1.75, 3.6, 4.9, LIGHT)
tb(s, 9.3, 1.82, 3.3, 0.4, "Recursos", 16, True, NAVY)
bullets(s, 9.3, 2.3, 3.35, 4.3, [
    "6 integrantes, 8–10 h por semana (≈ 400–480 h)",
    "Estación con ≥ 32 GB de RAM y ≥ 8 núcleos",
    "Todo el software es de código abierto",
    "Git como origen único: Ansible + Helm",
    "Hitos: HA operativa (S3), plataforma (S4), seguridad y observabilidad (S5), respaldo (S6), pruebas (S7)",
], 12.5, gap=5)
tb(s, 0.6, 6.25, 8.4, 0.6, "Ruta crítica: A2 → A3 → A4 → A5 → A8 → A10 → A11.", 13, True, NAVY)

# ------------------------------------------------------------------ 12 pruebas
s = nueva("Plan de pruebas", "27 casos que verifican cada requerimiento · 3 repeticiones en las pruebas de falla",
          "Cada caso tiene: qué se prueba, cómo, resultado esperado y criterio de aceptación (Sección 11 del informe).")
grupos = [("PI", "2", "Infraestructura\ny red", GRAY), ("PH", "7", "Alta\ndisponibilidad", GREEN), ("PS", "7", "Seguridad", RED),
          ("PR", "3", "Rendimiento y\nescalabilidad", ORANGE), ("PB", "3", "Respaldo y\nrecuperación", PURPLE), ("PO/PM", "5", "Observabilidad\ny operación", BLUE)]
for i, (cod, n, et, col) in enumerate(grupos):
    x = 0.6 + i * 2.05
    rect(s, x, 1.8, 1.9, 1.7, LIGHT)
    rect(s, x, 1.8, 1.9, 0.09, col, shape=MSO_SHAPE.RECTANGLE)
    tb(s, x, 1.95, 1.9, 0.7, n, 34, True, col, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    tb(s, x, 2.65, 1.9, 0.8, f"{et}\n({cod})", 11.5, False, INK, PP_ALIGN.CENTER)
filas = [["Prueba", "Cómo", "Criterio de aceptación"],
         ["PH-01 Conmutación de VIP", "Apagar lb01 con kubectl en bucle", "Interrupción ≤ 10 s"],
         ["PH-04 Falla de worker", "Apagar wk01 bajo carga (k6)", "≥ 99 % de éxito; reprogramación ≤ 5 min"],
         ["PS-02 NetworkPolicy", "Conexiones no autorizadas entre namespaces", "100 % bloqueadas (Hubble)"],
         ["PR-01 Carga base", "k6 a 200 req/s, 15 min", "p95 ≤ 500 ms; errores < 1 %"],
         ["PB-03 Recuperación a un punto en el tiempo", "Borrar tabla y restaurar", "RPO ≤ 5 min"]]
tabla(s, 0.6, 3.75, 12.1, filas, [3.7, 4.5, 3.9], size=12.5, alto_fila=0.45)
tb(s, 0.6, 6.55, 12.1, 0.45, "Aceptación global: 100 % de PH y PB aprobadas, ≥ 95 % del total, sin defectos críticos abiertos y con evidencia reproducible.", 13, True, NAVY)

# ------------------------------------------------------------------ 13 factibilidad
s = nueva("Factibilidad técnica, económica y operativa", "Comparación a 5 años con una nube gestionada equivalente (estimaciones referenciales)",
          "Costos del equipo, no de los artículos; deben validarse con cotizaciones. La opción on-premise supera a la nube bajo demanda desde el año 4, pero la nube con compromiso de 1 año es más barata; la justificación es soberanía de datos, control y aprendizaje.")
imagen(s, "07_tco.png", 0.5, 1.7, 6.9, 3.8)
tarjeta(s, 7.7, 1.75, 2.4, 1.3, money(datos.CAPEX_TOTAL).replace("US$ ", "US$ "), "Inversión inicial (CapEx)", NAVY)
tarjeta(s, 10.3, 1.75, 2.45, 1.3, money(datos.OPEX_TOTAL), "OpEx anual (sin personal)", TEAL)
tarjeta(s, 7.7, 3.2, 2.4, 1.3, money(datos.TCO_ONPREM[-1]), "On-premise, 5 años", GREEN)
tarjeta(s, 10.3, 3.2, 2.45, 1.3, money(datos.TCO_CLOUD[-1]), "Nube bajo demanda, 5 años", ORANGE)
bullets(s, 0.6, 5.65, 12.1, 1.4, [
    ("Técnica:", "componentes abiertos y maduros, con despliegues análogos en la literatura (Domínguez, Jovaní, Ramírez, Giurgică, Padial)."),
    ("Económica:", "comparable a la nube; mejora con hardware reutilizado (−50 % CapEx → ≈ US$ 49 250 a 5 años). Beneficio esperado: −77 % en tiempo de despliegue (Aguilar y García, 2024)."),
    ("Operativa:", "capacitación de 40 h por administrador, guardia 24×7 solo para P1 y migración gradual por aplicaciones."),
], 12.5, gap=4)

# ------------------------------------------------------------------ 14 conclusiones
s = nueva("Conclusiones y trabajo futuro", None,
          "Cierre: el diseño es trazable a la investigación, verificable mediante el plan de pruebas e implementable en la III Unidad en un laboratorio a escala.")
bullets(s, 0.6, 1.75, 7.4, 5.1, [
    ("Trazable:", "cada decisión se apoya en un hallazgo de la investigación (43 trabajos)."),
    ("Resiliente:", "sin puntos únicos de falla lógicos; tres dominios de falla con capacidad N+1."),
    ("Seguro:", "defensa en profundidad con riesgos críticos tratados y riesgos residuales aceptados de forma explícita."),
    ("Verificable:", "requerimientos con métricas (99,9 %, RPO ≤ 5 min, RTO ≤ 30 min) y 27 pruebas."),
    ("Transparente:", "el costo es comparable a la nube; el valor está en control, soberanía y aprendizaje."),
], 15, gap=10)
rect(s, 8.3, 1.75, 4.45, 3.2, LIGHT)
tb(s, 8.5, 1.82, 4.1, 0.4, "Trabajo futuro", 17, True, NAVY)
bullets(s, 8.5, 2.3, 4.15, 2.6, ["Segundo switch y firewall en HA", "SSO con OIDC", "Autoescalado predictivo con KEDA", "Sitio de recuperación en la nube",
                                 "Portal de desarrolladores (Backstage)"], 13, gap=4)
rect(s, 8.3, 5.15, 4.45, 1.7, NAVY)
tb(s, 8.5, 5.25, 4.1, 0.4, "Siguiente paso", 15, True, C("9FC3EC"))
tb(s, 8.5, 5.65, 4.1, 1.15, "Implementar y validar en la III Unidad exactamente lo diseñado; todo componente nuevo requerirá justificación técnica documentada.", 13, False, C("FFFFFF"))

for sufijo in ("", "_UPT", "_UPT2"):  # si el archivo está abierto se usa el siguiente nombre
    out = os.path.join(BASE, "Entregables", f"Presentacion_II_Unidad{sufijo}.pptx")
    try:
        prs.save(out)
        break
    except PermissionError:
        continue
print("guardado", out, "diapositivas:", len(prs.slides))
