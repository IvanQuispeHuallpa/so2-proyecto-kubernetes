"""Construye el documento técnico de la II Unidad (.docx)."""
import os
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx_plantilla import InformePlantilla
import c_a, c_b, c_c, c_d

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DG = os.path.join(BASE, "diagramas")
F = {
    "arq": os.path.join(DG, "01_arquitectura_general.png"),
    "red": os.path.join(DG, "02_topologia_red.png"),
    "seg": os.path.join(DG, "03_seguridad.png"),
    "desp": os.path.join(DG, "04_despliegue.png"),
    "flujo": os.path.join(DG, "05_flujo_informacion.png"),
    "gantt": os.path.join(DG, "06_cronograma.png"),
    "tco": os.path.join(DG, "07_tco.png"),
}

RF = [
    ["RF01", "Orquestar contenedores de forma declarativa: despliegue, actualización progresiva, reversión y escalado de aplicaciones.", "M", "PH-07, PR-02"],
    ["RF02", "Exponer el API del clúster mediante una IP virtual con balanceo y conmutación automática entre balanceadores.", "M", "PH-01, PH-02"],
    ["RF03", "Autorrecuperar pods y nodos fallidos reprogramando las cargas en nodos sanos.", "M", "PH-04, PH-05"],
    ["RF04", "Publicar aplicaciones mediante una IP virtual de servicios, terminación TLS y enrutamiento por nombre de host y ruta.", "M", "PI-01, PS-06"],
    ["RF05", "Escalar horizontalmente las aplicaciones según la carga (HPA).", "M", "PR-02"],
    ["RF06", "Proveer almacenamiento persistente replicado y con snapshots para cargas con estado.", "M", "PH-05, PH-06"],
    ["RF07", "Ofrecer bases de datos PostgreSQL con réplicas, conmutación automática y archivado de WAL.", "M", "PH-06, PB-03"],
    ["RF08", "Gestionar accesos mediante RBAC, cuentas de servicio y roles diferenciados.", "M", "PS-04"],
    ["RF09", "Restringir el tráfico entre pods y namespaces con políticas de red de denegación por defecto.", "M", "PS-02"],
    ["RF10", "Monitorear métricas, generar alertas y mostrar paneles de estado de la plataforma y las aplicaciones.", "M", "PO-01, PO-02"],
    ["RF11", "Centralizar registros y eventos de auditoría de la API y de los accesos administrativos.", "M", "PO-02"],
    ["RF12", "Respaldar y restaurar el estado de etcd, los recursos de Kubernetes, los volúmenes y las bases de datos.", "M", "PB-01, PB-02, PB-03"],
    ["RF13", "Automatizar la infraestructura (IaC) y el despliegue de aplicaciones mediante un pipeline CI/CD.", "M", "PM-02, PH-07"],
    ["RF14", "Escanear imágenes y aplicar políticas de seguridad de pods (Pod Security Admission).", "M", "PS-03, PS-05"],
    ["RF15", "Permitir la administración remota segura mediante VPN con segundo factor y bastión.", "M", "PS-06"],
    ["RF16", "Actualizar y mantener el clúster (Kubernetes, SO y certificados) sin interrumpir el servicio.", "S", "PM-01, PM-03"],
]

RNF = [
    ("Disponibilidad", [
        ["RNF-D1", "Disponibilidad mensual ≥ 99,9 % para las aplicaciones críticas (≤ 43,8 min de indisponibilidad al mes).", "PH-04, PH-05"],
        ["RNF-D2", "Sin punto único de falla en el balanceo del API, el plano de control, los workers y los datos (se acepta el switch/firewall, ver riesgo R03).", "PH-01…PH-06"],
        ["RNF-D3", "Conmutación de la IP virtual del API en ≤ 10 s; reprogramación de pods tras la caída de un worker en ≤ 5 min.", "PH-01, PH-04"],
        ["RNF-D4", "RPO ≤ 5 min en bases de datos y RTO ≤ 30 min para restaurar un namespace; reconstrucción total en ≤ 4 h.", "PB-01…PB-03"],
    ]),
    ("Seguridad", [
        ["RNF-S1", "Todo acceso administrativo cifrado y autenticado: SSH con llaves, VPN con MFA y TLS en el API; ningún puerto de administración expuesto.", "PS-06"],
        ["RNF-S2", "RBAC de mínimo privilegio; sin cuentas compartidas; exec denegado en producción para desarrolladores.", "PS-04"],
        ["RNF-S3", "Namespaces de aplicaciones con Pod Security Admission restricted y NetworkPolicy default-deny.", "PS-02, PS-03"],
        ["RNF-S4", "Secrets cifrados en reposo; imágenes sin vulnerabilidades críticas con corrección disponible; ≥ 90 % de controles CIS aplicables en PASS.", "PS-01, PS-05, PS-07"],
    ]),
    ("Rendimiento", [
        ["RNF-R1", "Latencia p95 ≤ 500 ms con 200 solicitudes/s sostenidas y tasa de errores < 1 %.", "PR-01"],
        ["RNF-R2", "Latencia p99 del API server ≤ 1 s en operación normal; fsync p99 de etcd < 10 ms.", "PO-02"],
        ["RNF-R3", "Despliegue de una nueva versión de aplicación en ≤ 10 min de extremo a extremo (referencia: Aguilar y García, 2024).", "PH-07"],
        ["RNF-R4", "Ancho de banda pod a pod entre nodos ≥ 80 % del enlace virtual.", "PR-03"],
    ]),
    ("Escalabilidad", [
        ["RNF-E1", "El HPA escala de 3 a 10 réplicas en ≤ 3 min ante un aumento de carga de 4×.", "PR-02"],
        ["RNF-E2", "Agregar un nodo de trabajo en ≤ 30 min mediante Ansible, sin interrupción.", "PM-02"],
        ["RNF-E3", "Capacidad N+1: la carga estimada (15 vCPU, 36 GB) debe caber con un worker caído.", "PH-04"],
    ]),
    ("Mantenibilidad", [
        ["RNF-M1", "100 % de la infraestructura y de la configuración reproducible desde Git y Ansible (idempotente).", "PM-02"],
        ["RNF-M2", "Actualización menor de Kubernetes trimestral sin interrupción; certificados con vigencia > 30 días.", "PM-01, PM-03"],
        ["RNF-M3", "Documentación operativa y runbooks para los seis escenarios de incidente definidos.", "PO-01"],
    ]),
    ("Usabilidad", [
        ["RNF-U1", "Paneles de Grafana por capa (nodos, etcd, aplicaciones, red) accesibles con un único inicio de sesión.", "PO-02"],
        ["RNF-U2", "Despliegue de una aplicación con un comando de Helm o mediante el pipeline, sin pasos manuales adicionales.", "PH-07"],
        ["RNF-U3", "Alertas accionables: cada alerta indica el runbook asociado; documentación y guías rápidas en español.", "PO-01"],
    ]),
]

VM_ROWS = [
    ["pve01", "lb01", "Balanceador API (HAProxy + Keepalived)", "2", "2 GB", "20 GB", "10.10.20.11 · VLAN 20"],
    ["pve01", "cp01", "Plano de control + etcd", "4", "8 GB", "80 GB", "10.10.20.21 · VLAN 20"],
    ["pve01", "wk01", "Nodo de trabajo", "12", "32 GB", "100 + 200 GB", "10.10.30.21 · 40.21 · 50.31"],
    ["pve01", "bastión", "Administración (Ansible, kubectl, WireGuard)", "2", "4 GB", "40 GB", "10.10.10.5 · VLAN 10"],
    ["pve02", "lb02", "Balanceador API (respaldo)", "2", "2 GB", "20 GB", "10.10.20.12 · VLAN 20"],
    ["pve02", "cp02", "Plano de control + etcd", "4", "8 GB", "80 GB", "10.10.20.22 · VLAN 20"],
    ["pve02", "wk02", "Nodo de trabajo", "12", "32 GB", "100 + 200 GB", "10.10.30.22 · 40.22 · 50.32"],
    ["pve03", "cp03", "Plano de control + etcd", "4", "8 GB", "80 GB", "10.10.20.23 · VLAN 20"],
    ["pve03", "wk03", "Nodo de trabajo", "12", "32 GB", "100 + 200 GB", "10.10.30.23 · 40.23 · 50.33"],
]

VLAN_ROWS = [
    ["10", "Gestión", "10.10.10.0/24", "10.10.10.1 (FW)", "Hosts Proxmox, BMC, bastión y firewall; solo accesible por VPN/bastión"],
    ["20", "Plano de control", "10.10.20.0/24", "10.10.20.1 (FW)", "Balanceadores y nodos de control; VIP del API"],
    ["30", "Nodos de trabajo", "10.10.30.0/24", "10.10.30.1 (FW)", "Nodos de trabajo; tráfico de pods (overlay) y kubelet"],
    ["40", "Almacenamiento", "10.10.40.0/24", "Sin gateway", "Replicación de volúmenes Longhorn; no enrutable"],
    ["50", "Servicios / DMZ", "10.10.50.0/24", "10.10.50.1 (FW)", "VIP de servicios anunciada por MetalLB; entrada de usuarios"],
    ["60", "Respaldo", "10.10.60.0/24", "10.10.60.1 (FW)", "MinIO y copias; acceso restringido por reglas"],
    ["100", "Usuarios", "10.10.100.0/23", "10.10.100.1 (FW)", "Estaciones de usuarios internos (DHCP)"],
]

IP_ROWS = [
    ["Firewall OPNsense (gateway)", "10.10.10.1 (.1 en cada VLAN)", "VLAN 10", "Subinterfaces 802.1Q sobre la troncal"],
    ["Bastión", "10.10.10.5", "VLAN 10", "Único punto de administración"],
    ["pve01 – pve03", "10.10.10.11 – .13", "VLAN 10", "Proxmox VE (consola 8006)"],
    ["BMC pve01 – pve03", "10.10.10.21 – .23", "VLAN 10", "iDRAC/iLO"],
    ["VIP del API", "10.10.20.10", "VLAN 20", "Keepalived; puerto 6443"],
    ["lb01 – lb02", "10.10.20.11 – .12", "VLAN 20", "HAProxy"],
    ["cp01 – cp03", "10.10.20.21 – .23", "VLAN 20", "Nodos de control"],
    ["wk01 – wk03 (nodo)", "10.10.30.21 – .23", "VLAN 30", "IP de nodo de Kubernetes"],
    ["wk01 – wk03 (datos)", "10.10.40.21 – .23", "VLAN 40", "Replicación Longhorn"],
    ["wk01 – wk03 (servicios)", "10.10.50.31 – .33", "VLAN 50", "Interfaz de anuncio L2 de MetalLB"],
    ["Pool de MetalLB", "10.10.50.100 – .150", "VLAN 50", "VIP de Ingress: 10.10.50.100"],
    ["Servidor de respaldo (MinIO)", "10.10.60.10", "VLAN 60", "S3 en puerto 9000"],
    ["CIDR de pods / servicios", "10.244.0.0/16 · 10.96.0.0/12", "Interno", "Overlay de Cilium; no enrutados"],
]

FW_ROWS = [
    ["1", "Internet", "VIP servicios 10.10.50.100", "TCP 80, 443", "Permitir", "Publicación de aplicaciones (DNAT)"],
    ["2", "Internet", "Firewall", "UDP 51820", "Permitir", "VPN WireGuard"],
    ["3", "Túnel VPN", "Bastión (VLAN 10)", "TCP 22", "Permitir", "Único acceso administrativo"],
    ["4", "VLAN 100", "VIP servicios", "TCP 80, 443", "Permitir", "Acceso de usuarios a aplicaciones"],
    ["5", "VLAN 100", "Demás VLAN", "Todos", "Denegar", "Segmentación de usuarios"],
    ["6", "Bastión", "VLAN 20 / VIP API", "TCP 22, 6443", "Permitir", "Administración y kubectl"],
    ["7", "Bastión", "VLAN 30 y hosts Proxmox", "TCP 22, 8006", "Permitir", "Administración de nodos e hipervisor"],
    ["8", "VLAN 30 ↔ VLAN 20", "Nodos del clúster", "TCP 6443, 10250; UDP 8472; TCP 4240, 4244-4245", "Permitir", "kubelet–API y overlay/health/Hubble de Cilium"],
    ["9", "VLAN 20 y 30", "MinIO (VLAN 60)", "TCP 9000", "Permitir", "Snapshots de etcd, Velero y WAL"],
    ["10", "VLAN 20 y 30", "Internet", "TCP 80, 443; UDP 53, 123", "Permitir", "Solo destinos de una lista permitida (registros, paquetes, NTP)"],
    ["11", "VLAN 40", "Cualquier otra VLAN", "Todos", "Denegar", "Red de almacenamiento sin enrutamiento"],
    ["12", "Cualquiera", "Cualquiera", "Todos", "Denegar y registrar", "Política por defecto"],
]

RACI = [
    ["Aprobar cambios mayores y presupuesto", "A", "R", "C", "C", "I", "I"],
    ["Desplegar aplicaciones (CI/CD)", "I", "C", "A", "I", "R", "I"],
    ["Parches del SO y mantenimiento", "I", "C", "A/R", "C", "I", "I"],
    ["Actualización de Kubernetes", "I", "A", "R", "C", "I", "I"],
    ["Gestión de accesos (altas y bajas)", "I", "I", "R", "A", "I", "C"],
    ["Reglas de firewall y red", "I", "C", "C", "A/R", "I", "I"],
    ["Respaldo y pruebas de restauración", "I", "C", "A/R", "C", "I", "I"],
    ["Monitoreo y atención de alertas", "I", "I", "A", "C", "C", "R"],
    ["Respuesta a incidentes P1/P2", "I", "C", "A/R", "R", "C", "R"],
    ["Revisión de seguridad y auditoría", "I", "C", "C", "A/R", "I", "I"],
    ["Planificación de capacidad", "I", "A/R", "C", "I", "C", "I"],
]

H = ["ID", "Qué se probará", "Cómo se probará", "Resultado esperado", "Criterio de aceptación"]
PRUEBAS = [
    ("11.2 Infraestructura y red", [
        ["PI-01", "Conectividad, segmentación y servicios base", "Probar con nc/ping los flujos de la matriz de firewall; comprobar DNS y `chronyc tracking`", "Solo pasan los flujos permitidos; hora sincronizada", "100 % de flujos conformes; desfase NTP < 100 ms"],
        ["PI-02", "Línea base del SO", "Ansible en modo --check; verificar SELinux, swap, firewalld y SSH por llaves", "Sin desviaciones respecto a la línea base", "0 desviaciones críticas"],
    ]),
    ("11.3 Alta disponibilidad", [
        ["PH-01", "Conmutación de la VIP del API", "Apagar lb01 mientras `kubectl get nodes` se ejecuta cada segundo", "La VIP pasa a lb02", "Interrupción ≤ 10 s"],
        ["PH-02", "Falla de un nodo de control", "Apagar cp01 con carga activa", "API disponible; etcd con 2 miembros y líder reelegido", "API responde en ≤ 10 s; ningún pod de aplicaciones reiniciado"],
        ["PH-03", "Pérdida de quórum (controlada)", "Apagar cp01 y cp02; comprobar solo lectura y servicio; recuperar quórum", "El API no escribe pero las aplicaciones siguen sirviendo", "0 % de errores en las aplicaciones; recuperación ≤ 30 min"],
        ["PH-04", "Falla de un nodo de trabajo", "Apagar wk01 bajo carga (k6)", "Pods reprogramados en wk02/wk03; PDB respetado", "≥ 99 % de solicitudes exitosas; reprogramación ≤ 5 min"],
        ["PH-05", "Falla de un host (simulada)", "Apagar el grupo de VM de un host lógico (lb + cp + wk)", "El clúster opera con N−1", "Servicio crítico sin corte (≤ 1 % de errores en la conmutación)"],
        ["PH-06", "Conmutación de PostgreSQL", "Eliminar el pod primario con escritura continua", "Una réplica se promueve a primario", "Escrituras detenidas ≤ 30 s; 0 transacciones confirmadas perdidas"],
        ["PH-07", "Actualización progresiva y reversión", "Cambiar la versión de la aplicación bajo carga; ejecutar `helm rollback`", "Sin caída durante la actualización", "0 errores 5xx atribuibles; reversión ≤ 2 min; despliegue total ≤ 10 min"],
    ]),
    ("11.4 Seguridad", [
        ["PS-01", "Cumplimiento CIS", "Ejecutar kube-bench en nodos de control y workers", "Informe de controles", "≥ 90 % aplicables en PASS; FAIL críticos justificados"],
        ["PS-02", "NetworkPolicy", "Intentar conexiones no autorizadas entre namespaces y hacia la BD; observar en Hubble", "Conexiones bloqueadas salvo flujos permitidos", "100 % de intentos no autorizados bloqueados"],
        ["PS-03", "Pod Security Admission", "Crear un pod privilegiado y uno con hostPath en un namespace restricted", "Rechazo por el controlador de admisión", "Rechazo del 100 %"],
        ["PS-04", "RBAC", "`kubectl auth can-i` y operaciones con los roles developer y viewer", "Permisos mínimos efectivos", "0 permisos fuera del rol; exec denegado en producción"],
        ["PS-05", "Escaneo de imágenes", "Construir una imagen con una vulnerabilidad CRITICAL conocida", "El pipeline falla", "La imagen no se publica"],
        ["PS-06", "Exposición de puertos", "Escaneo con nmap desde la VLAN 100 y desde una red externa simulada", "Solo 80/443 en la VIP de servicios", "0 puertos de administración alcanzables (22, 6443, 10250, 2379, 8006)"],
        ["PS-07", "Cifrado de Secrets", "Leer un Secret directamente en etcd con etcdctl", "Valor cifrado (prefijo k8s:enc)", "100 % de Secrets cifrados"],
    ]),
    ("11.5 Rendimiento y escalabilidad", [
        ["PR-01", "Carga base", "k6 a 200 solicitudes/s durante 15 min", "Latencia y errores dentro del objetivo", "p95 ≤ 500 ms; errores < 1 %"],
        ["PR-02", "Autoescalado (HPA)", "Rampa de carga hasta 4× el nivel base", "El número de réplicas crece de 3 a 10", "Escala en ≤ 3 min; vuelve al mínimo tras la estabilización de 5 min"],
        ["PR-03", "Rendimiento de red del CNI", "iperf3 entre pods en nodos distintos", "Medición de ancho de banda y latencia", "≥ 80 % del enlace virtual; resultado documentado"],
    ]),
    ("11.6 Respaldo y recuperación", [
        ["PB-01", "Snapshot y restauración de etcd", "Guardar snapshot, alterar el estado y restaurar", "Estado original recuperado", "Restauración ≤ 4 h; recursos coinciden"],
        ["PB-02", "Respaldo con Velero", "Respaldar un namespace y restaurarlo en otro", "Aplicación funcional con datos íntegros", "RTO ≤ 30 min"],
        ["PB-03", "Recuperación a un punto en el tiempo", "Borrar una tabla y restaurar al instante previo", "Datos recuperados", "RPO ≤ 5 min"],
    ]),
    ("11.7 Observabilidad y operación", [
        ["PO-01", "Alertas", "Forzar NodeNotReady y un respaldo fallido", "Notificación por correo y Telegram", "Alerta recibida en ≤ 2 min"],
        ["PO-02", "Paneles, registros y auditoría", "Revisar paneles; ejecutar `kubectl delete` y buscar el evento", "Evento localizable con usuario, hora y recurso", "Evento visible en Loki; paneles sin huecos"],
        ["PM-01", "Actualización menor de Kubernetes", "Actualizar de n a n+1 nodo por nodo", "Sin interrupción del servicio", "0 corte; todos los nodos en la versión nueva"],
        ["PM-02", "Reconstrucción de un nodo", "Eliminar wk03 y recrearlo con Ansible; repetir la ejecución", "Nodo reincorporado; segunda ejecución sin cambios", "≤ 30 min; ejecución idempotente"],
        ["PM-03", "Certificados", "`kubeadm certs check-expiration` y renovación", "Vigencia y renovación comprobadas", "Sin caducidades < 30 días; renovación sin corte"],
    ]),
]


PLANTILLA = os.path.join(BASE, "Referencias", "Plantilla_portada.docx")

PORTADA = {
    "universidad": "UNIVERSIDAD PRIVADA DE TACNA",
    "facultad": "FACULTAD DE INGENIERÍA",
    "escuela": "Escuela Profesional de Ingeniería de Sistemas",
    "proyecto": "Proyecto Plataforma de orquestación de contenedores con Kubernetes de alta disponibilidad",
    "curso": "Sistemas Operativos II",
    "docente": "Renzo Alberto Taco Coayla",
    "integrantes": [
        ("Cortez Apaza, Sebastian Alejandro", "2023078699"),
        ("Quispe Huallpa, Ivan", "2023078707"),
        ("Vilca Barrientos, Luis Fernando", "2023078329"),
        ("Cutipa Flores, Arturo Sebastian", "código"),
        ("Jimenez Laura, Carlos Rai", "código"),
        ("Ludeña Bedoya, Milagros Shadu", "código"),
    ],
    "titulo_1": "Plataforma de orquestación de contenedores con Kubernetes de alta disponibilidad",
    "titulo_2": "Documento de Diseño de la Solución Tecnológica",
    "version": "II Unidad",
    "titulo_cuerpo": "Diseño de la Solución Tecnológica",
    "autor": "Equipo de proyecto (CQV)",
}


def main():
    r = InformePlantilla(PLANTILLA, PORTADA)
    c_a.seccion_1(r)
    c_a.seccion_2(r)
    c_a.seccion_3(r)
    c_a.seccion_4(r, RF, RNF)
    c_b.seccion_5(r, F)
    c_b.seccion_6(r, F, VM_ROWS)
    c_b.seccion_7(r, F, VLAN_ROWS, IP_ROWS, FW_ROWS)
    c_c.seccion_8(r, F)
    c_c.seccion_9(r, RACI)
    c_d.seccion_10(r, F)
    c_d.seccion_11(r, PRUEBAS)
    c_d.seccion_12(r, F)
    c_d.seccion_13(r)
    c_d.seccion_14(r)
    c_d.anexo(r)
    for sufijo in ("", "_UPT", "_UPT2", "_UPT3", "_UPT4"):  # si el archivo está abierto en Word se usa el siguiente nombre
        out = os.path.join(BASE, "Entregables", f"Documento_Tecnico_II_Unidad{sufijo}.docx")
        try:
            r.guardar(out)
            break
        except PermissionError:
            continue
    print("guardado", out)


if __name__ == "__main__":
    main()
