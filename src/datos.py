# Datos compartidos entre diagramas, documento y presentación (una sola fuente de verdad).

CAPEX = [
    ("Servidores rack (16 núcleos, 128 GB RAM, 2×480 GB SSD + 2×1,92 TB SSD, 2×10 GbE, BMC)", 3, 6800),
    ("Switch administrable de 24 puertos (802.1Q, LACP, ACL, SFP+ 10 GbE)", 1, 2400),
    ("Firewall perimetral x86 (OPNsense), 4 puertos 2,5 GbE", 1, 900),
    ("Servidor de respaldo (4×8 TB, 32 GB RAM) con MinIO", 1, 2600),
    ("UPS online 3 kVA", 1, 1600),
    ("Rack 12U, PDU y organización de cableado", 1, 950),
    ("Cableado, DAC SFP+ y patch cords", 1, 650),
]
CAPEX_TOTAL = sum(c * p for _, c, p in CAPEX)

OPEX = [
    ("Energía y climatización (≈1,6 kW × 8 760 h × US$ 0,14/kWh)", 1960),
    ("Enlace a Internet simétrico de 100 Mbps", 1800),
    ("Garantía, soporte de hardware y repuestos (≈5 % del hardware)", 1500),
    ("Suscripción de soporte del hipervisor (opcional)", 400),
    ("Capacitación y certificación del equipo (p. ej. CKA/CKS)", 1000),
    ("Almacenamiento externo de respaldo (copia fuera de sitio, 2 TB)", 240),
]
OPEX_TOTAL = sum(v for _, v in OPEX)

# Nube gestionada equivalente (referencia): 3 nodos de 8 vCPU / 32 GB + plano de control gestionado.
CLOUD_MES = [
    ("3 nodos de 8 vCPU / 32 GB (bajo demanda)", 841),
    ("Plano de control gestionado", 73),
    ("Almacenamiento en bloque (600 GB) y snapshots", 68),
    ("Balanceadores de carga (2)", 40),
    ("Salida de datos (egress) y NAT", 150),
    ("Observabilidad y registros gestionados", 100),
]
CLOUD_MES_TOTAL = sum(v for _, v in CLOUD_MES)          # bajo demanda
CLOUD_RESERVADO_MES = CLOUD_MES_TOTAL - round(841 * 0.35)  # compromiso 1 año (-35 % solo en cómputo)

AÑOS = [1, 2, 3, 4, 5]
TCO_ONPREM = [CAPEX_TOTAL + OPEX_TOTAL * a for a in AÑOS]
TCO_CLOUD = [CLOUD_MES_TOTAL * 12 * a for a in AÑOS]
TCO_CLOUD_RES = [CLOUD_RESERVADO_MES * 12 * a for a in AÑOS]

# Cronograma (semana de inicio, duración en semanas) dentro de la III Unidad.
GANTT = [
    ("A1  Preparación del entorno y repositorio IaC", 1, 1),
    ("A2  Infraestructura base (hipervisor, VLAN, VM, SO)", 1, 2),
    ("A3  Balanceo del API (HAProxy + Keepalived)", 2, 1),
    ("A4  Clúster Kubernetes HA (kubeadm, etcd apilado)", 2, 2),
    ("A5  Servicios de plataforma (CNI, MetalLB, Ingress, Longhorn)", 3, 2),
    ("A6  Observabilidad (Prometheus, Grafana, Loki)", 4, 2),
    ("A7  Seguridad (RBAC, PSA, NetworkPolicy, auditoría)", 4, 2),
    ("A8  Aplicación de validación, BD HA, HPA y CI/CD", 5, 2),
    ("A9  Respaldo y recuperación (etcd, Velero, MinIO)", 6, 1),
    ("A10 Ejecución del plan de pruebas", 7, 1),
    ("A11 Documentación y sustentación", 7, 2),
]

if __name__ == "__main__":
    print("CAPEX", CAPEX_TOTAL, "OPEX/año", OPEX_TOTAL, "CLOUD/mes", CLOUD_MES_TOTAL, "RES/mes", CLOUD_RESERVADO_MES)
    print("TCO on-prem", TCO_ONPREM)
    print("TCO cloud  ", TCO_CLOUD)
    print("TCO cloud r", TCO_CLOUD_RES)
