"""Genera los diagramas técnicos de la II Unidad (PNG, 200 dpi)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import datos

plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]
OUT = os.path.join(os.path.dirname(__file__), "..", "diagramas")
os.makedirs(OUT, exist_ok=True)

NAVY, BLUE, TEAL, ORANGE, RED, GREEN, PURPLE, GRAY = (
    "#1F3A5F", "#2E6FBA", "#1A9E8F", "#E08A1E", "#C0392B", "#3C9D5D", "#7B5EA7", "#6B7280")
INK = "#1b2430"
K = 1.22  # factor de legibilidad de fuentes
TITULOS = False  # los títulos van como pie de figura en el documento
L = {  # rellenos claros
    "blue": "#E6EFFA", "teal": "#DDF3EF", "orange": "#FCEBD3", "red": "#F9DEDA",
    "green": "#E1F2E6", "purple": "#EBE5F4", "gray": "#EEF0F3", "navy": "#D9E2EF", "white": "#FFFFFF"}


def canvas(w, h, title=None):
    fig = plt.figure(figsize=(w / 17, h / 17), dpi=220)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    if title and TITULOS:
        ax.text(w / 2, h - 2.4, title, ha="center", va="center", fontsize=13 * K, fontweight="bold", color=NAVY)
    return fig, ax


def box(ax, x, y, w, h, text="", fc=L["blue"], ec=BLUE, fs=8, bold=False, tc=INK, lw=1.2,
        ls="-", r=0.9, va="center", ha="center", z=2):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec,
                       lw=lw, ls=ls, zorder=z)
    ax.add_patch(p)
    if text:
        tx = x + w / 2 if ha == "center" else x + 1.2
        ty = y + h / 2 if va == "center" else y + h - 1.0
        ax.text(tx, ty, text, ha=ha, va=va if va != "center" else "center", fontsize=fs * K,
                fontweight="bold" if bold else "normal", color=tc, zorder=z + 1, linespacing=1.25)
    return p


def label(ax, x, y, text, fs=8, color=INK, bold=False, ha="center", va="center", z=5, rot=0, style="normal"):
    ax.text(x, y, text, fontsize=fs * K, color=color, fontweight="bold" if bold else "normal",
            ha=ha, va=va, zorder=z, rotation=rot, fontstyle=style, linespacing=1.25)


def arrow(ax, p1, p2, color=GRAY, lw=1.4, ls="-", style="-|>", rad=0.0, z=4, ms=9):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms, color=color, lw=lw, ls=ls,
                        connectionstyle=f"arc3,rad={rad}", zorder=z, shrinkA=0, shrinkB=0)
    ax.add_patch(a)


def badge(ax, x, y, n, color=NAVY):
    ax.add_patch(plt.Circle((x, y), 1.5, fc=color, ec="white", lw=1, zorder=8))
    ax.text(x, y, str(n), ha="center", va="center", fontsize=7.5 * K, color="white", fontweight="bold", zorder=9)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)
    print("ok", name)


# ---------------------------------------------------------------- 1. Arquitectura general
def arquitectura_general():
    W, H = 200, 128
    fig, ax = canvas(W, H, "Figura 1. Arquitectura lógica general de la plataforma")

    # Usuarios
    box(ax, 4, 108, 38, 11, "Usuarios internos\n(LAN corporativa / VPN)", L["gray"], GRAY, 8.5, True)
    box(ax, 46, 108, 38, 11, "Desarrolladores\n(Git, CI/CD, kubectl)", L["gray"], GRAY, 8.5, True)
    box(ax, 88, 108, 38, 11, "Operadores\n(bastión, VPN + MFA)", L["gray"], GRAY, 8.5, True)
    box(ax, 130, 108, 66, 11, "Internet (servicios publicados)\nvía firewall perimetral (DNAT 80/443)", L["gray"], GRAY, 8.5, True)

    # Capa de acceso
    box(ax, 4, 89, 192, 15, "", L["orange"], ORANGE, lw=1.5)
    label(ax, 8, 101.6, "CAPA DE ACCESO Y BALANCEO", 8, ORANGE, True, "left")
    box(ax, 8, 90.8, 56, 7, "VIP del API  10.10.20.10\nHAProxy + Keepalived (2 nodos)", L["white"], ORANGE, 7.8)
    box(ax, 70, 90.8, 56, 7, "VIP de servicios  10.10.50.100\nMetalLB (modo L2)", L["white"], ORANGE, 7.8)
    box(ax, 132, 90.8, 60, 7, "Controlador Ingress (Traefik)\nTLS · límites de tasa · enrutamiento", L["white"], ORANGE, 7.8)

    # Plano de control
    box(ax, 4, 56, 92, 31, "", L["blue"], BLUE, lw=1.5)
    label(ax, 8, 85.2, "PLANO DE CONTROL (3 nodos, etcd apilado)", 8, BLUE, True, "left")
    for i, n in enumerate(["cp01", "cp02", "cp03"]):
        x = 8 + i * 29.5
        box(ax, x, 59, 27.5, 23.5, "", L["white"], BLUE, lw=1)
        label(ax, x + 13.75, 79.6, n, 8.5, BLUE, True)
        for j, t in enumerate(["kube-apiserver", "scheduler", "controller-manager", "etcd (Raft)"]):
            box(ax, x + 1.2, 60.2 + (3 - j) * 4.6, 25.1, 4.0, t, L["blue"], BLUE, 6.8, r=0.5, lw=0.7)

    # Workers
    box(ax, 100, 56, 96, 31, "", L["green"], GREEN, lw=1.5)
    label(ax, 104, 85.2, "NODOS DE TRABAJO (3 nodos)", 8, GREEN, True, "left")
    for i, n in enumerate(["wk01", "wk02", "wk03"]):
        x = 104 + i * 30.7
        box(ax, x, 59, 29, 23.5, "", L["white"], GREEN, lw=1)
        label(ax, x + 14.5, 79.6, n, 8.5, GREEN, True)
        for j, t in enumerate(["Pods: frontend · API", "PostgreSQL (CNPG)", "Longhorn (réplica)", "kubelet · containerd"]):
            box(ax, x + 1.2, 60.2 + (3 - j) * 4.6, 26.6, 4.0, t, L["green"], GREEN, 6.8, r=0.5, lw=0.7)

    # Servicios de plataforma
    box(ax, 4, 39, 192, 14.5, "", L["teal"], TEAL, lw=1.5)
    label(ax, 8, 51.0, "SERVICIOS DE PLATAFORMA", 8, TEAL, True, "left")
    for i, t in enumerate(["Cilium (CNI, eBPF,\nNetworkPolicy, Hubble)", "CoreDNS", "metrics-server\n+ HPA", "cert-manager",
                           "Longhorn\n(almacenamiento)", "CloudNativePG\n(operador BD)"]):
        box(ax, 8 + i * 31.3, 40.4, 29.3, 6.6, t, L["white"], TEAL, 7.2)

    # Transversales
    box(ax, 4, 11, 62, 24, "", L["purple"], PURPLE, lw=1.5)
    label(ax, 8, 32.6, "OBSERVABILIDAD", 8, PURPLE, True, "left")
    for i, t in enumerate(["Prometheus + Alertmanager", "Grafana (paneles)", "Loki + Alloy (logs y auditoría)", "Hubble (flujos de red)"]):
        box(ax, 8, 24.6 - i * 4.4, 54, 3.8, t, L["white"], PURPLE, 7.2, r=0.5)
    box(ax, 69, 11, 62, 24, "", L["red"], RED, lw=1.5)
    label(ax, 73, 32.6, "SEGURIDAD", 8, RED, True, "left")
    for i, t in enumerate(["RBAC + Pod Security Admission", "NetworkPolicy (zero-trust)", "Cifrado de Secrets · TLS", "Trivy · kube-bench · Falco"]):
        box(ax, 73, 24.6 - i * 4.4, 54, 3.8, t, L["white"], RED, 7.2, r=0.5)
    box(ax, 134, 11, 62, 24, "", L["navy"], NAVY, lw=1.5)
    label(ax, 138, 32.6, "AUTOMATIZACIÓN, CI/CD Y RESPALDO", 8, NAVY, True, "left")
    for i, t in enumerate(["Git → CI → Registro → Helm", "Ansible / Vagrant / Packer (IaC)", "Velero + snapshots de etcd", "MinIO (S3) en servidor de respaldo"]):
        box(ax, 138, 24.6 - i * 4.4, 54, 3.8, t, L["white"], NAVY, 7.2, r=0.5)

    # Infraestructura
    box(ax, 4, 1.5, 192, 7.5, "INFRAESTRUCTURA BASE: 3 hosts Proxmox VE (VM con Rocky Linux 9) · ZFS · VLAN 802.1Q · OPNsense · UPS",
        L["gray"], GRAY, 8, True, lw=1.5)

    # flechas
    for x in (23, 65, 107):
        arrow(ax, (x, 108), (x, 103.3), GRAY)
    arrow(ax, (163, 108), (163, 103.3), GRAY)
    arrow(ax, (50, 89), (50, 87.3), ORANGE)
    arrow(ax, (150, 89), (150, 87.3), ORANGE)
    arrow(ax, (50, 56), (50, 53.6), BLUE)
    arrow(ax, (150, 56), (150, 53.6), GREEN)
    arrow(ax, (98, 71), (100, 71), GRAY, style="<|-|>")
    for x in (35, 100, 165):
        arrow(ax, (x, 35), (x, 39), GRAY, ls="--", style="<|-|>")
    save(fig, "01_arquitectura_general.png")


# ---------------------------------------------------------------- 2. Topología de red
def topologia_red():
    W, H = 200, 138
    fig, ax = canvas(W, H, "Figura 2. Topología de red y segmentación por VLAN")

    for cx, cy, r in ((100, 128, 5.5), (94, 126.5, 4.2), (106, 126.5, 4.2)):
        ax.add_patch(plt.Circle((cx, cy), r, fc=L["gray"], ec=GRAY, zorder=2))
    ax.add_patch(Rectangle((90, 122.2), 20, 5, fc=L["gray"], ec="none", zorder=3))
    label(ax, 100, 126, "Internet / ISP", 8.5, INK, True)
    box(ax, 142, 120, 54, 11, "Teletrabajo · VPN WireGuard\n(UDP 51820) → VLAN 10", L["white"], GRAY, 7.8)
    arrow(ax, (142, 126), (112, 126), GRAY, ls="--", style="<|-|>")

    box(ax, 62, 102, 76, 13, "Firewall OPNsense · gateway de todas las VLAN\nNAT · IDS · VPN · DNS · NTP", L["red"], RED, 8.3, True)
    arrow(ax, (100, 122), (100, 115.3), GRAY)
    label(ax, 107, 118.5, "WAN", 7, GRAY)

    box(ax, 40, 82, 120, 12, "Switch core (802.1Q, LACP) · conmutación L2 con ACL de respaldo", L["navy"], NAVY, 8.5, True)
    arrow(ax, (100, 102), (100, 94.3), NAVY, lw=2)
    label(ax, 113, 98, "troncal 802.1Q", 7, NAVY)

    box(ax, 4, 100, 46, 16, "VLAN 100 · Usuarios\n10.10.100.0/23 · oficinas", L["gray"], GRAY, 7.8)
    arrow(ax, (50, 104), (62, 106), GRAY)
    arrow(ax, (27, 100), (55, 94.3), GRAY)

    cols = [(4, "Host pve01 · 10.10.10.11"), (71, "Host pve02 · 10.10.10.12"), (138, "Host pve03 · 10.10.10.13")]
    vms = [
        [("lb01", "VLAN 20", L["orange"], ORANGE), ("cp01", "VLAN 20", L["blue"], BLUE),
         ("wk01", "VLAN 30·40·50", L["green"], GREEN), ("bastión", "VLAN 10", L["gray"], GRAY)],
        [("lb02", "VLAN 20", L["orange"], ORANGE), ("cp02", "VLAN 20", L["blue"], BLUE),
         ("wk02", "VLAN 30·40·50", L["green"], GREEN)],
        [("cp03", "VLAN 20", L["blue"], BLUE), ("wk03", "VLAN 30·40·50", L["green"], GREEN)],
    ]
    for (x, title), vm in zip(cols, vms):
        box(ax, x, 30, 58, 46, "", "#FAFBFD", NAVY, lw=1.4)
        label(ax, x + 29, 72.8, title, 8, NAVY, True)
        label(ax, x + 29, 69.0, "Proxmox VE · bridge VLAN-aware · bond0 2×10 GbE", 6.3, GRAY)
        yy = 65
        for n, vlan, fc, ec in vm:
            box(ax, x + 4, yy - 6, 50, 6.4, n, fc, ec, 7.6, True, ha="left")
            label(ax, x + 52, yy - 2.8, vlan, 6.6, ec, ha="right")
            yy -= 8
    for xs, xe in ((33, 62), (100, 100), (167, 138)):
        ax.plot([xs, xe], [76, 82], color=NAVY, lw=1.8, zorder=3)
    label(ax, 38, 79.6, "LACP", 6.5, NAVY)
    label(ax, 162, 79.6, "LACP", 6.5, NAVY)

    box(ax, 4, 3, 46, 22, "UPS 3 kVA + PDU\nBMC/iDRAC en VLAN 10\nSyslog y NTP internos", L["gray"], GRAY, 7.8)
    box(ax, 150, 3, 46, 22, "Servidor de respaldo\nMinIO (S3) · ZFS RAID-Z\nVLAN 60 · 10.10.60.10", L["purple"], PURPLE, 7.8, True)
    arrow(ax, (170, 25), (170, 30), PURPLE, ls="--", style="<|-|>")

    box(ax, 54, 2, 92, 26, "", "#FFFFFF", GRAY, lw=0.8)
    label(ax, 100, 25.0, "Plan de direccionamiento y segmentación", 8, NAVY, True)
    filas = [("VLAN 10", "Gestión", "10.10.10.0/24", GRAY), ("VLAN 20", "Plano de control", "10.10.20.0/24", BLUE),
             ("VLAN 30", "Nodos de trabajo", "10.10.30.0/24", GREEN), ("VLAN 40", "Almacenamiento (sin gateway)", "10.10.40.0/24", TEAL),
             ("VLAN 50", "Servicios / DMZ (MetalLB)", "10.10.50.0/24", ORANGE), ("VLAN 60", "Respaldo", "10.10.60.0/24", PURPLE),
             ("VLAN 100", "Usuarios", "10.10.100.0/23", GRAY)]
    for i, (v, n, c, col) in enumerate(filas):
        yy = 21.2 - i * 2.9
        ax.add_patch(Rectangle((57, yy - 1.0), 2.4, 2.0, fc=col, ec="none", zorder=4))
        label(ax, 61, yy, v, 6.8, INK, True, "left")
        label(ax, 76, yy, n, 6.8, INK, False, "left")
        label(ax, 143, yy, c, 6.8, INK, False, "right")
    save(fig, "02_topologia_red.png")


# ---------------------------------------------------------------- 3. Seguridad
def seguridad():
    import textwrap
    W, H = 200, 128
    fig, ax = canvas(W, H, "Figura 3. Diagrama de seguridad: defensa en profundidad (modelo 4C) y puntos de control")

    layers = [
        (4, 10, 116, 100, "NUBE / INFRAESTRUCTURA", L["gray"], GRAY,
         ["Firewall perimetral y segmentación en VLAN", "VPN WireGuard con MFA y bastión SSH con llaves",
          "Hardening del SO: SELinux, firewalld, chrony", "UPS y BMC en una red de gestión aislada"]),
        (8, 13, 108, 74, "CLÚSTER", L["blue"], BLUE,
         ["RBAC de mínimo privilegio y cuentas de servicio", "Pod Security Admission (perfil restricted)",
          "Cifrado de Secrets en etcd y TLS/mTLS", "Auditoría de la API y kube-bench (CIS)",
          "NetworkPolicy con denegación por defecto"]),
        (12, 16, 100, 45, "CONTENEDOR", L["orange"], ORANGE,
         ["Imágenes mínimas, firmadas y escaneadas (Trivy)", "Usuario no root y sistema de archivos de solo lectura",
          "Límites de CPU/memoria y cuotas por namespace", "Detección en tiempo de ejecución (Falco)"]),
        (16, 19, 92, 20, "CÓDIGO", L["green"], GREEN,
         ["Pipeline CI con pruebas y escaneo de dependencias", "Secretos fuera del repositorio",
          "Revisión por pull request y versiones fijadas"]),
    ]
    for x, y, w, h, t, fc, ec, items in layers:
        box(ax, x, y, w, h, "", fc, ec, lw=1.6, r=1.6, z=1)
        label(ax, x + 3, y + h - 3.2, t, 8.8, ec, True, "left")
        for k, it in enumerate(items):
            label(ax, x + 3, y + h - 7.4 - k * 3.0, "•  " + it, 7.6, INK, False, "left")

    box(ax, 124, 6, 72, 112, "", "#FFFFFF", GRAY, lw=0.9, r=1.6)
    label(ax, 160, 113, "Puntos de control en la ruta de una petición", 8.3, NAVY, True)
    pasos = [("Usuario / Internet", "TLS 1.2+ extremo a extremo", GRAY),
             ("Firewall perimetral", "Solo 80/443 al VIP · IDS", RED),
             ("Ingress (Traefik)", "Terminación TLS · límite de tasa", ORANGE),
             ("NetworkPolicy (Cilium)", "Denegar por defecto, permitir por etiqueta", BLUE),
             ("Pod de aplicación", "PSA restricted · no root · cuotas", GREEN),
             ("Base de datos (CNPG)", "TLS · credenciales en Secret", TEAL)]
    for i, (a, b, c) in enumerate(pasos):
        y = 100 - i * 13.5
        box(ax, 131, y - 5, 59, 10, "", L["white"], c, lw=1.3)
        label(ax, 134, y + 2.2, a, 7.8, c, True, "left")
        label(ax, 134, y - 2.2, b, 6.7, INK, False, "left")
        badge(ax, 128, y, i + 1, c)
        if i < len(pasos) - 1:
            arrow(ax, (160, y - 5), (160, y - 8.5), GRAY)
    box(ax, 131, 10, 59, 14, "", L["purple"], PURPLE, lw=1.3)
    label(ax, 160.5, 20.5, "Detección y respuesta (transversal)", 7.4, PURPLE, True)
    label(ax, 160.5, 14.5, "Prometheus · Alertmanager · Loki\nHubble · Falco · auditoría de la API", 6.6)
    save(fig, "03_seguridad.png")


# ---------------------------------------------------------------- 4. Despliegue
def despliegue():
    W, H = 200, 134
    fig, ax = canvas(W, H, "Figura 4. Diagrama de despliegue (hosts, máquinas virtuales y cargas)")
    hosts = [(4, "pve01", ["lb01", "cp01", "wk01", "bastion"]), (71, "pve02", ["lb02", "cp02", "wk02"]), (138, "pve03", ["cp03", "wk03"])]
    box(ax, 40, 119, 120, 9, "VIP del API 10.10.20.10:6443 (Keepalived · VRRP) flota entre lb01 y lb02", L["orange"], ORANGE, 7.8, True)
    arrow(ax, (60, 119), (35, 114.3), ORANGE)
    arrow(ax, (140, 119), (100, 114.3), ORANGE)
    for x, nm, vms in hosts:
        box(ax, x, 22, 58, 92, "", "#FAFBFD", NAVY, lw=1.6, r=1.4)
        label(ax, x + 29, 110.2, f"Host físico {nm}", 8.6, NAVY, True)
        label(ax, x + 29, 106.2, "Proxmox VE · ZFS espejo · 16 núcleos · 128 GB", 6.4, GRAY)
        yy = 103
        for v in vms:
            if v.startswith("lb"):
                box(ax, x + 3, yy - 8, 52, 8.5, "", L["orange"], ORANGE, lw=1.1, r=0.7)
                label(ax, x + 5, yy - 2.2, f"VM {v} · 2 vCPU · 2 GB", 6.8, ORANGE, True, "left")
                label(ax, x + 5, yy - 6.0, "Rocky Linux 9 · HAProxy · Keepalived", 6.3, INK, False, "left")
                yy -= 10
            elif v.startswith("cp"):
                box(ax, x + 3, yy - 17.5, 52, 18, "", L["blue"], BLUE, lw=1.1, r=0.7)
                label(ax, x + 5, yy - 2.2, f"VM {v} · 4 vCPU · 8 GB · 80 GB", 6.8, BLUE, True, "left")
                for k, t in enumerate(["kube-apiserver · scheduler", "controller-manager", "etcd (Raft) · kubelet"]):
                    box(ax, x + 5, yy - 7.4 - k * 3.4, 48, 3.0, t, L["white"], BLUE, 6.1, r=0.4, lw=0.6)
                yy -= 20
            elif v.startswith("wk"):
                alto = 40
                box(ax, x + 3, yy - alto, 52, alto, "", L["green"], GREEN, lw=1.1, r=0.7)
                label(ax, x + 5, yy - 2.2, f"VM {v} · 12 vCPU · 32 GB · 100+200 GB", 6.6, GREEN, True, "left")
                pods = ["Traefik · MetalLB speaker", "Frontend ×N · API ×N (HPA)", "PostgreSQL (CNPG) primario/réplica",
                        "Longhorn (réplica de volumen)", "Prometheus · Loki · Grafana*", "Cilium agent · containerd"]
                for k, t in enumerate(pods):
                    box(ax, x + 5, yy - 8.4 - k * 5.0, 48, 4.2, t, L["white"], GREEN, 6.3, r=0.4, lw=0.6)
                yy -= alto + 2
            elif v == "bastion":
                box(ax, x + 3, yy - 8, 52, 8.5, "", L["gray"], GRAY, lw=1.1, r=0.7)
                label(ax, x + 5, yy - 2.2, "VM bastión · 2 vCPU · 4 GB", 6.8, GRAY, True, "left")
                label(ax, x + 5, yy - 6.0, "Ansible · kubectl · Helm · WireGuard", 6.3, INK, False, "left")
                yy -= 10
    label(ax, 167, 32, "Capacidad libre:\ncon un host caído, los\notros dos absorben\nla carga (criterio N+1)", 6.6, GRAY, style="italic")
    box(ax, 4, 2, 56, 15, "Repositorio Git + CI/CD\nRegistro de imágenes", L["navy"], NAVY, 7.6, True)
    box(ax, 72, 2, 56, 15, "Servidor de respaldo (VLAN 60)\nMinIO: etcd · Velero · WAL de BD", L["purple"], PURPLE, 7.6, True)
    box(ax, 140, 2, 56, 15, "OPNsense + switch core\nVLAN 10/20/30/40/50/60/100", L["red"], RED, 7.6, True)
    for xm in (32, 100, 168):
        arrow(ax, (xm, 17), (xm, 22), GRAY, ls="--", style="<|-|>")
    label(ax, 100, 27, "* Observabilidad con afinidad a" + chr(10) + "nodos con recursos libres", 6.2, GRAY, style="italic")
    save(fig, "04_despliegue.png")


# ---------------------------------------------------------------- 5. Flujo de información
def flujo():
    W, H = 200, 112
    fig, ax = canvas(W, H, "Figura 5. Flujos de información de la plataforma")
    lanes = [("A. Tráfico de usuario", 76, ORANGE, L["orange"]),
             ("B. Despliegue continuo (CI/CD)", 44, NAVY, L["navy"]),
             ("C. Observabilidad y respaldo", 12, PURPLE, L["purple"])]
    for t, y, c, f in lanes:
        box(ax, 3, y - 8, 194, 29, "", "#FFFFFF", c, lw=1.1, r=1.2, z=1)
        label(ax, 6, y + 17.5, t, 8.2, c, True, "left")

    def chain(y, items, c, f, w=26.5, gap=5.3, x0=6):
        xs = []
        for i, t in enumerate(items):
            x = x0 + i * (w + gap)
            box(ax, x, y, w, 11, t, f, c, 6.9, True)
            badge(ax, x + 1.2, y + 11, i + 1, c)
            xs.append(x)
            if i:
                arrow(ax, (xs[i - 1] + w, y + 5.5), (x, y + 5.5), c)

    chain(76 - 1, ["Cliente\nresuelve DNS", "Firewall\nDNAT 443 → VIP", "MetalLB\nVIP 10.10.50.100", "Traefik\nTLS + enrutado", "Servicio →\nPod frontend", "API → PostgreSQL\nprimario / réplicas"], ORANGE, L["orange"])
    label(ax, 100, 70.2, "Los datos persisten en volúmenes Longhorn (3 réplicas, VLAN 40) · el HPA ajusta las réplicas según CPU", 6.7, INK, style="italic")
    chain(44 - 1, ["Desarrollador\nhace commit", "CI: pruebas,\nTrivy y build", "Registro de\nimágenes", "Helm / manifiestos\nversionados en Git", "kubectl vía VIP\ndel API (RBAC)", "Rolling update +\nreadiness probe"], NAVY, L["navy"])
    label(ax, 100, 38.2, "Reversión inmediata con «helm rollback»; la infraestructura se modifica con Ansible desde el bastión", 6.7, INK, style="italic")
    chain(12 - 1, ["Exporters\nnode · kube-state", "Prometheus\n(scrape 30 s)", "Alertmanager →\ne-mail / Telegram", "Grafana\npaneles", "Loki ← Alloy\nlogs y auditoría", "Velero + etcd\n→ MinIO (VLAN 60)"], PURPLE, L["purple"])
    label(ax, 100, 6.2, "Respaldo: etcd cada 6 h · Velero diario · WAL de PostgreSQL continuo · copia fuera de sitio semanal", 6.7, INK, style="italic")
    save(fig, "05_flujo_informacion.png")


# ---------------------------------------------------------------- 6. Gantt
def gantt():
    fig, ax = plt.subplots(figsize=(7.4, 3.7), dpi=220)
    n = len(datos.GANTT)
    cols = [NAVY, NAVY, ORANGE, BLUE, TEAL, PURPLE, RED, GREEN, NAVY, GRAY, GRAY]
    for i, (t, s, d) in enumerate(datos.GANTT):
        ax.barh(n - 1 - i, d, left=s - 1, color=cols[i % len(cols)], height=0.58, edgecolor="white")
    ax.set_yticks(range(n))
    ax.set_yticklabels([g[0] for g in datos.GANTT][::-1], fontsize=7.4)
    ax.set_xticks([i + 0.5 for i in range(8)])
    ax.set_xticklabels([f"S{i + 1}" for i in range(8)], fontsize=8)
    ax.set_xlim(0, 8)
    for i in range(9):
        ax.axvline(i, color="#D5D9E0", lw=0.6, zorder=0)
    ax.tick_params(length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, "06_cronograma.png")


# ---------------------------------------------------------------- 7. TCO
def tco():
    fig, ax = plt.subplots(figsize=(7.0, 3.5), dpi=220)
    yrs = datos.AÑOS
    ax.plot(yrs, [v / 1000 for v in datos.TCO_ONPREM], "-o", color=NAVY, lw=2.2, label="On-premise (esta propuesta)")
    ax.plot(yrs, [v / 1000 for v in datos.TCO_CLOUD], "-s", color=ORANGE, lw=2.2, label="Nube gestionada (bajo demanda)")
    ax.plot(yrs, [v / 1000 for v in datos.TCO_CLOUD_RES], "--^", color=TEAL, lw=2.0, label="Nube gestionada (compromiso 1 año)")
    for series, col, dy in ((datos.TCO_ONPREM, NAVY, 2.2), (datos.TCO_CLOUD, ORANGE, 2.2), (datos.TCO_CLOUD_RES, TEAL, -4.6)):
        ax.annotate(f"{series[-1] / 1000:.1f}", (5, series[-1] / 1000), textcoords="offset points", xytext=(8, 0), fontsize=8, color=col, va="center")
    ax.set_xticks(yrs)
    ax.set_xticklabels([f"Año {y}" for y in yrs], fontsize=8)
    ax.set_ylabel("Costo acumulado (miles de US$)", fontsize=8.5)
    ax.set_xlim(0.7, 5.6)
    ax.grid(axis="y", color="#E2E5EA", lw=0.7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    save(fig, "07_tco.png")


if __name__ == "__main__":
    arquitectura_general()
    topologia_red()
    seguridad()
    despliegue()
    flujo()
    gantt()
    tco()
