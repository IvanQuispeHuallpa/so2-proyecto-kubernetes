"""Secciones 8 y 9: seguridad y diseño operativo."""

# (id, riesgo, P, I, controles, P_res, I_res)
RIESGOS = [
    ("R01", "Pérdida de quórum de etcd (falla simultánea de 2 nodos de control)", 2, 5,
     "3 nodos de control en 3 hosts distintos; snapshots cada 6 h; runbook de recuperación", 1, 5),
    ("R02", "Falla de un host físico completo", 3, 4, "Capacidad N+1; anti-afinidad entre hosts; VM reconstruibles con Ansible", 3, 2),
    ("R03", "Punto único de falla de red (switch core o firewall)", 2, 5,
     "Equipo de repuesto en frío; configuración respaldada; UPS; segundo switch en fase 2 (riesgo aceptado)", 2, 3),
    ("R04", "Exposición del API, kubelet, etcd o consola del hipervisor", 3, 5,
     "VLAN de gestión/control; firewall deny-by-default; VPN + MFA; kubelet sin acceso anónimo; nunca publicar 6443/10250/2379", 1, 5),
    ("R05", "Privilegios excesivos o credenciales comprometidas", 3, 5,
     "RBAC mínimo privilegio; certificados de vigencia corta; MFA; rotación a 90 días; auditoría de la API", 2, 4),
    ("R06", "Imágenes vulnerables o maliciosas (cadena de suministro)", 4, 4,
     "Trivy en CI (bloquea CRITICAL); registro propio; imágenes mínimas y firmadas; revisión por pull request", 2, 3),
    ("R07", "Movimiento lateral entre pods o escape de contenedor", 3, 4,
     "NetworkPolicy default-deny; Pod Security Admission restricted; no root; rootfs de solo lectura; Falco", 2, 3),
    ("R08", "Saturación por pico legítimo o ataque de denegación de servicio", 3, 3,
     "Límite de tasa en Ingress; HPA con réplicas máximas; ResourceQuota y límites; alertas de saturación", 2, 2),
    ("R09", "Pérdida o corrupción de datos (BD, volúmenes, etcd)", 2, 5,
     "Respaldo 3-2-1; WAL continuo; Velero; pruebas de restauración trimestrales", 1, 4),
    ("R10", "Expiración de certificados del clúster", 3, 4, "Alerta a 30 días; renovación en cada upgrade; cert-manager para certificados de aplicación", 1, 3),
    ("R11", "Nodo de control comprometido o con comportamiento bizantino", 1, 5,
     "Hardening, aislamiento en VLAN 20, auditoría; Raft no cubre fallas bizantinas (Diouf et al., 2020): riesgo aceptado", 1, 5),
    ("R12", "Obsolescencia y deuda técnica (APIs retiradas, versiones sin soporte)", 3, 3,
     "Actualización trimestral; pruebas previas en laboratorio; revisión de notas de versión (Maarleveld et al., 2025)", 2, 2),
    ("R13", "Falla eléctrica o ambiental", 2, 4, "UPS online con apagado ordenado; monitoreo de temperatura y energía", 1, 3),
    ("R14", "Error humano o cambio mal aplicado", 4, 3, "Infraestructura como código; revisión por pull request; ventanas de cambio; reversión con Helm", 2, 2),
]


def nivel(score):
    return "Crítico" if score >= 15 else "Alto" if score >= 10 else "Medio" if score >= 5 else "Bajo"


def filas_riesgos():
    out = []
    for rid, txt, p, i, ctl, pr, ir in RIESGOS:
        s, sr = p * i, pr * ir
        out.append([rid, txt, str(p), str(i), f"{s} · {nivel(s)}", ctl, f"{sr} · {nivel(sr)}"])
    return out


def seccion_8(r, F):
    r.h1("8. Diseño de Seguridad")
    r.h2("8.1 Enfoque")
    r.jp("El diseño sigue la metodología de gestión de riesgos propuesta por Simón (2021) —identificación de activos y amenazas, análisis de riesgos y "
         "tratamiento— y organiza los controles según el modelo de seguridad **4C de Cloud Native** (nube/infraestructura, clúster, contenedor y código). "
         "Las superficies de ataque se alinean con las analizadas en la metodología de pentesting de Guardiola (2020): API server, kubelet, etcd, "
         "panel de administración, contenedores privilegiados y credenciales.")
    r.h2("8.2 Activos")
    r.bullets([
        "**Datos de las aplicaciones** (bases de datos PostgreSQL y volúmenes) y sus respaldos.",
        "**Plano de control** (API, etcd, certificados de la CA del clúster) y credenciales de administración (kubeconfig, llaves SSH, tokens).",
        "**Disponibilidad de los servicios** publicados y de la plataforma de despliegue (Git, CI/CD, registro).",
        "**Infraestructura física y de red** (hosts, firewall, switch, servidor de respaldo).",
    ])
    r.h2("8.3 Riesgos identificados")
    r.jp("La siguiente matriz valora cada riesgo con probabilidad (P) e impacto (I) en escala 1–5; el nivel resulta del producto (≥ 15 crítico, 10–14 alto, "
         "5–9 medio, < 5 bajo). Se muestra también el riesgo residual esperado tras aplicar los controles.")
    r.tabla("Matriz de riesgos (inicial y residual)", ["ID", "Riesgo", "P", "I", "Nivel inicial", "Controles principales", "Residual"],
            filas_riesgos(), [0.9, 3.9, 0.6, 0.6, 1.8, 6.5, 2.1], size=7.5, align_center_cols=(0, 2, 3, 4, 6))
    r.jp("Tras aplicar los controles, ningún riesgo permanece en nivel alto o crítico (los tres riesgos críticos iniciales son R04, R05 y R06). Los riesgos residuales de nivel medio se aceptan de forma explícita y se vigilan con alertas y pruebas periódicas; en particular R03 (punto único de red), cuya mitigación completa exige duplicar equipos y se difiere a una segunda fase, y R11 (falla bizantina), que el protocolo Raft no cubre.")
    r.h2("8.4 Amenazas")
    r.tabla("Catálogo de amenazas (clasificación STRIDE)", ["ID", "Amenaza", "Vector típico", "Componente afectado", "STRIDE"], [
        ["T01", "Atacante externo que explota servicios expuestos", "Escaneo y explotación de Ingress, SSH, VPN", "Perímetro, Ingress", "S, E"],
        ["T02", "Usuario interno con privilegios excesivos o malicioso", "Abuso de RBAC, kubectl exec, lectura de Secrets", "API, namespaces", "E, I"],
        ["T03", "Contenedor comprometido", "Vulnerabilidad de la aplicación, escape a nodo, movimiento lateral", "Pods, nodos", "T, E"],
        ["T04", "Cadena de suministro", "Imagen o dependencia maliciosa en el pipeline", "CI/CD, registro", "T"],
        ["T05", "Robo de credenciales", "kubeconfig, tokens o llaves SSH filtradas", "Bastión, API", "S"],
        ["T06", "Denegación de servicio", "Tráfico volumétrico o agotamiento de recursos, también por autoescalado inducido (Jiang y Milani, 2026)", "Ingress, workers", "D"],
        ["T07", "Ransomware o manipulación de datos y respaldos", "Cifrado de volúmenes y borrado de copias", "Datos, MinIO", "T, D"],
        ["T08", "Interceptación del tráfico interno", "Sniffing en la red de pods o de almacenamiento", "Redes 30/40", "I"],
        ["T09", "Falla de hardware, energía o desastre", "Avería, corte eléctrico, incendio", "Hosts, red", "D"],
        ["T10", "Error operativo o configuración insegura", "Cambio manual sin revisión", "Toda la plataforma", "T, D"],
        ["T11", "Acciones administrativas sin trazabilidad", "Falta de auditoría de la API y de SSH", "API, bastión", "R"],
    ], [1.0, 4.4, 5.6, 3.6, 1.8], size=8, align_center_cols=(0, 4))
    r.h2("8.5 Controles propuestos")
    r.jp("La Figura 5 (al final de esta sección) resume la defensa en profundidad y la ruta de una petición con sus seis puntos de control. La tabla siguiente detalla los controles "
         "por capa y su naturaleza (P = preventivo, D = detectivo, C = correctivo).")
    r.tabla("Controles por capa", ["Capa", "Control", "Tipo", "Riesgos"], [
        ["Infraestructura", "Segmentación en VLAN y firewall con denegación por defecto", "P", "R03, R04, R07"],
        ["Infraestructura", "VPN WireGuard con MFA y bastión SSH con llaves; BMC en red aislada", "P", "R04, R05"],
        ["Infraestructura", "Hardening del SO: SELinux enforcing, firewalld, parches mensuales, chrony", "P", "R04, R10, R12"],
        ["Infraestructura", "UPS, apagado ordenado y monitoreo ambiental", "P", "R13"],
        ["Infraestructura", "IDS/IPS en el firewall y alertas de acceso", "D", "R04, T01"],
        ["Clúster", "RBAC de mínimo privilegio y cuentas de servicio dedicadas", "P", "R05"],
        ["Clúster", "kubelet con autenticación/autorización y sin acceso anónimo; etcd solo accesible desde el plano de control", "P", "R04"],
        ["Clúster", "Pod Security Admission en perfil restricted para namespaces de aplicaciones", "P", "R07"],
        ["Clúster", "NetworkPolicy default-deny y reglas por etiqueta (Cilium); cifrado de tráfico entre nodos con WireGuard de Cilium", "P", "R07, T08"],
        ["Clúster", "Cifrado de Secrets en etcd (EncryptionConfiguration) y TLS en todos los componentes", "P", "R05, R09"],
        ["Clúster", "Auditoría de la API enviada a Loki; kube-bench mensual (CIS)", "D", "R05, R12, T11"],
        ["Contenedor", "Imágenes mínimas, firmadas y de registro propio; escaneo con Trivy; bloqueo de CRITICAL", "P/D", "R06"],
        ["Contenedor", "Usuario no root, rootfs de solo lectura, capacidades mínimas, límites de CPU/memoria", "P", "R07, R08"],
        ["Contenedor", "Detección en tiempo de ejecución con Falco y alertas", "D", "R07"],
        ["Código / CI", "Pipeline con pruebas, escaneo de dependencias y de secretos; revisión por pull request; despliegue solo desde Git", "P", "R06, R14"],
        ["Datos", "Respaldo 3-2-1, WAL continuo, snapshots y pruebas de restauración", "C", "R09, T07"],
        ["Tráfico", "Límite de tasa y tiempos de espera en Traefik; HPA con máximo de réplicas", "P", "R08, T06"],
    ], [2.2, 10.0, 1.1, 3.1], size=8, align_center_cols=(2,))
    r.h2("8.6 Gestión de accesos")
    r.tabla("Roles de acceso a la plataforma", ["Rol", "Alcance y permisos", "Asignado a", "Autenticación"], [
        ["cluster-admin", "Todo el clúster; uso restringido y registrado (break-glass)", "2 administradores de plataforma", "Certificado de cliente de 30 días + MFA en VPN"],
        ["platform-operator", "Nodos, almacenamiento, monitoreo; sin lectura de Secrets de aplicaciones", "Administradores de plataforma", "Certificado de cliente + MFA"],
        ["ns-admin", "Administración total dentro de un namespace", "Líderes de equipo de desarrollo", "Certificado de cliente"],
        ["developer", "edit en dev/staging; solo lectura en producción; sin exec en producción", "Desarrolladores", "Certificado de cliente"],
        ["viewer / auditor", "get/list/watch sin Secrets en todo el clúster", "Soporte N1, auditoría", "Certificado de cliente"],
        ["ci-deployer", "Cuenta de servicio por namespace con permisos solo sobre recursos de aplicación", "Pipeline CI/CD", "Token enlazado de vida corta"],
    ], [2.6, 7.0, 3.6, 3.2], size=8.5)
    r.bullets([
        "Altas y bajas ligadas al proceso de personal; **sin cuentas compartidas**; revisión trimestral de roles, llaves SSH y certificados vigentes.",
        "Rotación de credenciales administrativas cada 90 días y revocación inmediata ante sospecha; evaluación de SSO (OIDC) en una segunda fase.",
        "Los Secrets no se almacenan en Git; se crean fuera del repositorio y se cifran en reposo en etcd.",
    ])
    r.h2("8.7 Respaldo y recuperación")
    r.tabla("Política de respaldo (regla 3-2-1)", ["Elemento", "Herramienta", "Frecuencia", "Retención", "Destino", "RPO"], [
        ["Estado del clúster (etcd)", "etcdctl snapshot + temporizador", "Cada 6 h", "14 días", "MinIO + copia externa", "6 h"],
        ["Recursos y volúmenes", "Velero (snapshots/Kopia)", "Diario (02:00)", "30 días", "MinIO (VLAN 60)", "24 h"],
        ["Bases de datos", "CloudNativePG: base + WAL", "Continuo", "30 días", "MinIO", "≤ 5 min"],
        ["VM de infraestructura", "Respaldo Proxmox + export de OPNsense", "Semanal", "4 semanas", "Servidor de respaldo", "7 días"],
        ["Configuración (IaC)", "Git con espejo remoto", "Continuo", "Indefinida", "Git + espejo", "0"],
        ["Copia fuera de sitio", "restic/rclone cifrado", "Semanal", "8 semanas", "Bucket externo o disco rotado", "7 días"],
    ], [3.2, 3.6, 2.2, 1.8, 3.8, 1.8], size=8)
    r.jp("**Metas de recuperación:** RPO ≤ 5 min para bases de datos; RTO ≤ 30 min para restaurar un namespace con Velero; RTO ≤ 4 h para reconstruir "
         "el clúster desde cero (VM con Ansible, restauración de etcd y Velero). Se ejecutan **pruebas de restauración trimestrales**; un respaldo no "
         "probado no se considera válido. El mismo mecanismo de respaldo cubre la recuperación ante ransomware, al mantener una copia fuera de sitio y con "
         "credenciales distintas.")
    r.h2("8.8 Monitoreo y auditoría")
    r.jp("Se combina monitoreo de métricas, de registros y de flujos de red, con reglas de Alertmanager que agrupan e inhiben alertas para reducir "
         "el ruido y apoyar la correlación de eventos (Tambi, 2024). Las alertas se envían por correo y Telegram (Domínguez, 2024).")
    r.tabla("Alertas mínimas", ["Alerta", "Condición", "Severidad", "Acción"], [
        ["NodeNotReady", "Nodo no listo > 2 min", "P2", "Runbook de nodo caído"],
        ["EtcdNoLeader / EtcdLatencia", "Sin líder o fsync p99 > 25 ms", "P1 / P2", "Runbook de etcd"],
        ["ApiServerLatencia", "Latencia p99 del API > 1 s durante 5 min", "P2", "Revisar etcd y carga"],
        ["VipFailover", "Cambio de estado de Keepalived", "P2", "Verificar el balanceador activo"],
        ["PodCrashLoop / DeploymentIndisponible", "Reinicios repetidos o réplicas < PDB", "P2", "Revisar logs y despliegue"],
        ["VolumenDegradado / DiscoLleno", "Réplica Longhorn degradada o disco > 85 %", "P2 / P3", "Reconstruir o ampliar"],
        ["CertCaduca", "Certificado vence en < 30 días", "P3", "Renovar y verificar"],
        ["BackupFallido", "Velero o etcd sin éxito en la ventana", "P3", "Reintentar y escalar"],
        ["SeguridadFalco / AuditoriaAnomala", "Ejecución en contenedor, exec en producción, acceso fuera de horario", "P1 / P2", "Runbook de seguridad"],
        ["HpaAlLimite", "HPA en el máximo > 15 min", "P3", "Revisar capacidad y posible ataque"],
    ], [4.2, 6.2, 1.8, 4.2], size=8, align_center_cols=(2,))
    r.jp("**Auditoría:** el API server registra eventos con una política de auditoría (nivel Metadata para Secrets, RequestResponse para cambios de RBAC) y los "
         "envía a Loki con retención de 90 días; los accesos SSH y de la VPN se registran en el bastión y el firewall. Se revisan semanalmente los "
         "accesos anómalos y mensualmente el cumplimiento CIS con kube-bench.")
    r.figuras_apaisadas([(F["seg"], "Diagrama de seguridad: defensa en profundidad (modelo 4C) y puntos de control de una petición.")])


def seccion_9(r, raci):
    r.h1("9. Diseño Operativo")
    r.h2("9.1 Roles y responsabilidades")
    r.tabla("Roles del modelo operativo", ["Rol", "Responsabilidades principales"], [
        ["Jefe de TI (patrocinador)", "Aprobar cambios mayores y presupuesto; arbitrar prioridades; recibir informes de incidentes y de capacidad"],
        ["Arquitecto de plataforma", "Mantener el diseño, evaluar nuevas versiones y componentes, planificar capacidad y evolución"],
        ["Administrador de plataforma (2)", "Operar el clúster, parches, actualizaciones, respaldo, automatización y respuesta a incidentes"],
        ["Responsable de redes y seguridad", "Firewall, VLAN, VPN, gestión de accesos, auditoría, kube-bench y respuesta a incidentes de seguridad"],
        ["Equipo de desarrollo", "Construir y desplegar aplicaciones mediante el pipeline; definir probes, recursos y políticas de su namespace"],
        ["Soporte N1 / mesa de ayuda", "Atender solicitudes, clasificar incidentes y escalar según la severidad"],
    ], [4.6, 11.8], size=8.5, bold_first=True)
    r.tabla("Matriz RACI (R = ejecuta, A = aprueba, C = consultado, I = informado)",
            ["Actividad", "Jefe TI", "Arq.", "Adm. plat.", "Red/Seg.", "Desarr.", "N1"], raci,
            [5.8, 1.8, 1.7, 1.9, 1.9, 1.7, 1.6], size=8, align_center_cols=(1, 2, 3, 4, 5, 6))
    r.h2("9.2 Procedimientos de operación")
    r.tabla("Operación periódica", ["Tarea", "Frecuencia", "Herramienta", "Criterio de normalidad"], [
        ["Estado de nodos, pods y alertas abiertas", "Diaria", "Grafana, kubectl", "0 nodos NotReady, 0 CrashLoop, alertas atendidas"],
        ["Verificación de respaldos nocturnos", "Diaria", "Velero, MinIO", "Backups en estado Completed"],
        ["Capacidad de CPU, memoria, disco y volúmenes", "Semanal", "Grafana", "Solicitudes < 70 % de lo asignable; disco < 70 %"],
        ["Latencia de etcd y tamaño de la base", "Semanal", "Prometheus", "fsync p99 < 10 ms; tamaño < 80 % de la cuota"],
        ["Vulnerabilidades de imágenes y nodos", "Semanal", "Trivy", "Sin CRITICAL abiertas con corrección disponible"],
        ["Revisión de auditoría y accesos", "Semanal", "Loki", "Sin accesos anómalos o con justificación"],
    ], [5.8, 2.0, 3.0, 5.6], size=8.5)
    r.h3("Procedimiento de despliegue de una nueva versión")
    r.numbered([
        "El desarrollador integra el cambio mediante pull request; el pipeline ejecuta pruebas, escaneo de dependencias y de la imagen (Trivy) y construye la imagen etiquetada con el commit.",
        "Se publica la imagen en el registro y se actualiza el chart de Helm (valores y versión) en el repositorio.",
        "El despliegue en staging se realiza con `helm upgrade --install`; se ejecutan pruebas de humo.",
        "Tras la aprobación, el mismo artefacto se despliega en producción con actualización progresiva (maxUnavailable = 0) y probes de readiness.",
        "Se observa el panel durante 15 minutos (tasa de errores y latencia); si hay degradación se ejecuta `helm rollback`.",
        "Se registra el cambio (versión, responsable, resultado) en el historial del repositorio.",
    ])
    r.h3("Otros procedimientos")
    r.bullets([
        "**Alta/baja de usuario:** solicitud aprobada → emisión o revocación de certificado de cliente y RoleBinding por Git → confirmación al solicitante.",
        "**Agregar un nodo de trabajo:** clonar plantilla Rocky Linux 9 → ejecutar el rol de Ansible de nodo → `kubeadm join` → verificar etiquetas, taints y Longhorn → liberar al planificador.",
        "**Gestión de cambios:** cambios estándar (preaprobados: despliegue de aplicaciones y parches), normales (aprobación del arquitecto y ventana programada) y de emergencia (autorización del jefe de TI, informe posterior).",
    ])
    r.h2("9.3 Procedimientos de mantenimiento")
    r.tabla("Calendario de mantenimiento", ["Tarea", "Frecuencia", "Procedimiento resumido", "Impacto"], [
        ["Parches del SO", "Mensual", "Nodo por nodo: cordon, drain respetando PDB, parche, reinicio, uncordon; el plano de control se hace de uno en uno comprobando etcd", "Ninguno"],
        ["Actualización menor de Kubernetes", "Trimestral", "Snapshot de etcd; kubeadm upgrade en cp01, luego cp02 y cp03; después workers con drain; sin saltar versiones menores", "Ninguno"],
        ["Hipervisor (Proxmox VE)", "Trimestral", "Host por host y fuera de horas pico; el clúster opera con N−1 durante la ventana", "Redundancia reducida"],
        ["Renovación de certificados", "Automática en upgrade; revisión trimestral", "`kubeadm certs check-expiration`; renovar si quedan < 30 días", "Ninguno"],
        ["Desfragmentación de etcd", "Mensual o > 50 % de fragmentación", "Miembro por miembro, comenzando por los seguidores", "Latencia breve"],
        ["Pruebas de restauración", "Trimestral", "Casos PB-01, PB-02 y PB-03 en un entorno aislado", "Ninguno"],
        ["Revisión de RBAC, llaves y accesos", "Trimestral", "Comparar roles reales contra los aprobados; revocar los no usados", "Ninguno"],
        ["Pruebas de conmutación (game day)", "Semestral", "Apagar un nodo, un balanceador y un host en ventana controlada", "Planificado"],
        ["Revisión de capacidad y costos", "Semestral", "Comparar uso real con el dimensionamiento; planificar ampliación", "Ninguno"],
    ], [3.6, 2.6, 8.0, 2.2], size=8)
    r.h2("9.4 Gestión de incidentes")
    r.tabla("Clasificación de incidentes y objetivos", ["Sev.", "Descripción", "Respuesta", "Resolución objetivo", "Cobertura"], [
        ["P1", "Servicio crítico caído, pérdida de quórum, compromiso de seguridad o riesgo de pérdida de datos", "15 min", "2 h", "24×7 con guardia"],
        ["P2", "Servicio degradado o pérdida de redundancia (un nodo, host o balanceador caído)", "30 min", "8 h", "Horario extendido"],
        ["P3", "Falla parcial sin impacto al usuario (respaldo fallido, certificado próximo a vencer)", "4 h", "3 días", "Horario laboral"],
        ["P4", "Consultas o mejoras", "1 día", "Según planificación", "Horario laboral"],
    ], [1.1, 7.4, 1.9, 3.0, 3.0], size=8.5, align_center_cols=(0, 2, 3))
    r.jp("**Ciclo de gestión:** detección (alerta o reporte) → clasificación y asignación → contención → resolución y verificación → comunicación → "
         "revisión posterior sin culpables en un máximo de cinco días laborales, con causa raíz y acciones preventivas registradas. Se miden el tiempo medio de "
         "detección (MTTD) y de recuperación (MTTR) por severidad.")
    r.tabla("Procedimientos de respuesta (runbooks) para los escenarios principales", ["Escenario", "Detección", "Acciones inmediatas", "Sev."], [
        ["Nodo NotReady", "Alerta NodeNotReady", "Verificar VM y host; cordon y drain; reiniciar kubelet; si no recupera, reponer la VM con Ansible", "P2"],
        ["Pérdida de quórum de etcd", "EtcdNoLeader, API en solo lectura", "Congelar cambios; identificar miembros sanos; restaurar el nodo; si quedan < 2 miembros, restaurar desde snapshot", "P1"],
        ["Conmutación de VIP o HAProxy caído", "VipFailover", "Confirmar balanceador activo; reiniciar servicios; verificar salud de los backends", "P2"],
        ["Volumen degradado o disco lleno", "VolumenDegradado, DiscoLleno", "Reconstruir réplicas o ampliar disco; liberar espacio", "P2/P3"],
        ["Sospecha de compromiso", "Falco o auditoría anómala", "Aislar el namespace con NetworkPolicy; revocar credenciales; preservar evidencias; restaurar desde imagen conocida", "P1"],
        ["Respaldo fallido", "BackupFallido", "Revisar espacio y credenciales; reintentar; escalar si falla dos veces consecutivas", "P3"],
    ], [3.4, 3.0, 8.9, 1.1], size=8, align_center_cols=(3,))
