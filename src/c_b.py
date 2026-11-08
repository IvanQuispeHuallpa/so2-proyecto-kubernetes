"""Secciones 5 a 7: arquitectura, infraestructura y red."""


def seccion_5(r, F):
    r.h1("5. Diseño de la Arquitectura")
    r.h2("5.1 Principios de diseño")
    r.bullets([
        "**Sin puntos únicos de falla lógicos:** cada capa (acceso, plano de control, cómputo, datos) tiene al menos dos o tres instancias en hosts físicos distintos.",
        "**Declarativo y reproducible:** el estado deseado vive en Git (manifiestos, charts y roles de Ansible); el clúster puede reconstruirse desde cero.",
        "**Defensa en profundidad:** controles en red, clúster, contenedor y código (modelo 4C).",
        "**Observable por defecto:** toda pieza expone métricas, registros y eventos antes de entrar en producción.",
        "**Capacidad N+1:** la carga debe seguir cabiendo si se pierde un nodo de trabajo o un host.",
        "**Simplicidad operativa:** se prefieren componentes maduros y con comunidad amplia; se evita introducir herramientas sin necesidad demostrada.",
    ])
    r.h2("5.2 Arquitectura lógica")
    r.jp("La arquitectura lógica (Figura 1, al final de esta sección) se organiza en capas. Los usuarios y operadores acceden a través de una **capa de acceso** formada por "
         "dos IP virtuales: la del API de Kubernetes (HAProxy + Keepalived) y la de los servicios de aplicación (MetalLB + Traefik). Debajo se "
         "encuentra el **plano de control** (kube-apiserver, scheduler, controller-manager y etcd en tres nodos) y los **nodos de trabajo** donde "
         "se ejecutan los pods. Los **servicios de plataforma** (Cilium, CoreDNS, metrics-server, cert-manager, Longhorn y el operador de base de "
         "datos) dan soporte a las aplicaciones, y tres bloques transversales —observabilidad, seguridad y automatización/respaldo— atraviesan "
         "toda la pila.")
    r.h2("5.3 Decisiones tecnológicas y alternativas evaluadas")
    r.tabla("Componentes seleccionados, alternativas y justificación", ["Capa", "Elegido", "Alternativas consideradas", "Justificación"], [
        ["Distribución de Kubernetes", "Kubernetes upstream con kubeadm", "K3s, MicroK8s, k0s, MicroShift; Docker Swarm",
         "Carga sostenida y HA con 3 nodos de control (Kjorveziroski y Filiposka, 2022; Koziolek y Eskandani, 2023); más flexible que Swarm (Hernández, 2024)"],
        ["Entorno de ejecución", "containerd", "CRI-O, Docker Engine", "Usado en los despliegues HA de referencia (Domínguez, 2024); estándar CRI"],
        ["Red de contenedores (CNI)", "Cilium (eBPF)", "Calico, Flannel, Antrea", "Políticas L3/L7, observabilidad con Hubble y seguridad eBPF (Jiang y Milani, 2026); rendimiento validado (Dakić et al., 2024a)"],
        ["Balanceo del API", "HAProxy + Keepalived (VRRP)", "kube-vip, balanceador del proveedor", "Probado en HA on-premise (Domínguez, 2024); dos nodos dedicados"],
        ["Balanceo de servicios", "MetalLB (modo L2)", "kube-vip, Cilium LB-IPAM", "Failover y balanceo en clústeres sin nube (Giurgică et al., 2025)"],
        ["Ingreso HTTP(S)", "Traefik", "ingress-nginx, HAProxy Ingress", "Soporte de Gateway API y middlewares (límite de tasa, cabeceras); ingress-nginx fue anunciado para retiro (marzo de 2026)"],
        ["Almacenamiento persistente", "Longhorn", "Rook/Ceph, NFS, GlusterFS", "Réplicas por volumen y snapshots nativos; menor complejidad que Ceph para 3 nodos"],
        ["Base de datos", "PostgreSQL con CloudNativePG", "StatefulSet manual, MySQL", "Conmutación automática y archivado de WAL; mitiga la limitación de Vayghan et al. (2020)"],
        ["Métricas y alertas", "Prometheus + Alertmanager + Grafana", "Zabbix, Nagios", "Estándar del ecosistema; usado en Domínguez (2024), Giurgică et al. (2025) y Ramírez (2021)"],
        ["Registros", "Loki + Alloy", "ELK/EFK", "Menor consumo de recursos; integra con Grafana"],
        ["Respaldo", "Velero + snapshots de etcd + MinIO", "Kasten, scripts manuales", "Respaldo de recursos y volúmenes hacia almacenamiento S3 propio"],
        ["Automatización", "Ansible, Vagrant y Packer; Helm", "Terraform, Kubespray", "Ansible ya validado en clústeres HA y de bajo costo (Domínguez, 2024; Iñesta, 2024; Dakić et al., 2024a)"],
        ["Sistema operativo de nodos", "Rocky Linux 9", "Ubuntu LTS, Debian", "Compatible con RHEL y de larga vida; usado en Domínguez (2024); SELinux disponible"],
        ["Hipervisor", "Proxmox VE (KVM)", "VMware ESXi, Hyper-V", "Código abierto con ZFS y VLAN integradas; usado en Padial (2024)"],
    ], [2.6, 3.4, 3.4, 7.0], size=8)
    r.h2("5.4 Arquitectura física")
    r.jp("Físicamente, la plataforma se apoya en **tres servidores idénticos** que actúan como dominios de falla independientes, un firewall "
         "perimetral, un switch core y un servidor de respaldo (Figura 2, al final de esta sección; la red se detalla en la Sección 7). Las máquinas virtuales se reparten de modo que "
         "**ningún host concentre más de un nodo de control, más de un nodo de trabajo ni más de un balanceador**: si cae un host, quedan dos "
         "miembros de etcd (quórum), dos nodos de trabajo y, si corresponde, el otro balanceador.")
    r.h2("5.5 Componentes principales")
    r.tabla("Componentes principales y su ubicación", ["Componente", "Función", "Instancias", "Ubicación"], [
        ["HAProxy + Keepalived", "Publica la VIP 10.10.20.10:6443 y reparte hacia los kube-apiserver con comprobación de salud", "2 (activo/pasivo)", "VM lb01 y lb02 (pve01, pve02)"],
        ["kube-apiserver", "Punto de entrada del clúster; valida y persiste objetos en etcd", "3", "cp01–cp03"],
        ["etcd (apilado)", "Almacén de estado con consenso Raft; tolera 1 falla", "3", "cp01–cp03"],
        ["scheduler y controller-manager", "Colocación de pods y bucles de control (elección de líder)", "3 (1 activo)", "cp01–cp03"],
        ["kubelet + containerd", "Agente de nodo y entorno de ejecución de contenedores", "6", "Todos los nodos"],
        ["Cilium", "Red de pods, NetworkPolicy, balanceo interno y Hubble", "Agente por nodo", "Todos los nodos"],
        ["MetalLB + Traefik", "VIP 10.10.50.100 y enrutamiento HTTP(S) con TLS", "3 (speaker por worker)", "wk01–wk03"],
        ["Longhorn", "Volúmenes replicados (2–3 réplicas) y snapshots", "Gestor por worker", "wk01–wk03"],
        ["CloudNativePG", "PostgreSQL 1 primario + 2 réplicas con failover automático", "3 instancias", "wk01–wk03 (anti-afinidad)"],
        ["kube-prometheus-stack, Loki, Hubble", "Métricas, alertas, paneles, registros y flujos de red", "Según componente", "Workers (afinidad)"],
        ["Velero + MinIO", "Respaldo de recursos y volúmenes hacia S3 en VLAN 60", "1 + 1", "Clúster / servidor de respaldo"],
        ["Bastión (Ansible, kubectl, Helm, WireGuard)", "Único punto de administración remota", "1", "VM en pve01 (respaldada)"],
    ], [3.6, 6.6, 2.5, 3.7], size=8)
    r.h2("5.6 Flujo de información")
    r.jp("La Figura 3 (al final de esta sección) muestra los tres flujos principales. En el **flujo de tráfico de usuario (A)**, el cliente resuelve el nombre por DNS, el "
         "firewall traduce el puerto 443 hacia la VIP de servicios (10.10.50.100, anunciada por MetalLB), Traefik termina TLS y enruta hacia el "
         "servicio; el pod de la aplicación consulta a PostgreSQL, cuyos datos residen en volúmenes Longhorn. En el **flujo de despliegue (B)**, "
         "un commit dispara el pipeline de integración continua (pruebas, escaneo con Trivy y construcción de la imagen), se publica la imagen en el "
         "registro y el despliegue se aplica con Helm a través de la VIP del API, bajo control RBAC y con actualización progresiva. En el **flujo de "
         "observabilidad y respaldo (C)**, los exporters alimentan a Prometheus, que genera alertas y paneles; Alloy envía registros y eventos de auditoría "
         "a Loki, y Velero y los snapshots de etcd se almacenan en MinIO.")
    r.h2("5.7 Diseño de alta disponibilidad")
    r.jp("**Plano de control.** Con tres miembros etcd, el quórum es de dos: el clúster tolera la pérdida de un nodo y se vuelve de solo lectura "
         "si pierde dos. No se usan cinco miembros porque, según Jeffery et al. (2021), la latencia de escritura crece y el rendimiento decrece al aumentar "
         "el tamaño del clúster etcd; se prefieren tres miembros sobre SSD y un monitoreo estricto de latencia de fsync. La topología elegida es **etcd "
         "apilado** (el etcd comparte nodo con el API), que requiere la mitad de máquinas que un etcd externo (Domínguez, 2024) y es suficiente para el escenario.")
    r.jp("**Aplicaciones.** Cada Deployment crítico tiene al menos tres réplicas repartidas con __topologySpreadConstraints__ por host y "
         "__PodDisruptionBudget__ con minAvailable = 2, de modo que el mantenimiento voluntario nunca retire todas las réplicas. Los probes de "
         "readiness y liveness evitan enviar tráfico a pods no listos, y se reduce __tolerationSeconds__ de los taints "
         "not-ready/unreachable (300 s por defecto) a 30–60 s para acelerar la reprogramación.")
    r.jp("**Datos.** CloudNativePG mantiene un primario y dos réplicas síncronas/asíncronas y promueve una réplica si el primario falla. Para evitar "
         "sobre-replicación, la clase de almacenamiento de bases de datos usa **2 réplicas Longhorn** (la replicación lógica ya aporta redundancia), mientras que "
         "la clase general usa 3. El archivado continuo de WAL hacia MinIO habilita la recuperación a un punto en el tiempo.")
    r.tabla("Escenarios de falla y comportamiento esperado", ["Falla", "Efecto", "Mecanismo de recuperación", "Tiempo esperado"], [
        ["Cae lb01 (balanceador activo)", "Ninguno tras la conmutación", "Keepalived mueve la VIP a lb02 (VRRP)", "≤ 10 s"],
        ["Cae un nodo de control", "API disponible; se pierde 1 de 3 miembros etcd", "HAProxy excluye el nodo; elección de líder en etcd", "≤ 10 s (API)"],
        ["Caen 2 nodos de control", "Pérdida de quórum: el API solo lee; las cargas siguen en ejecución", "Restaurar un nodo o recuperar desde snapshot de etcd", "≤ 4 h (RTO)"],
        ["Cae un worker", "Pods reprogramados en los otros dos workers", "Taint + tolerationSeconds; scheduler", "≤ 5 min"],
        ["Cae un host físico", "Pierde 1 CP, 1 worker, 1 LB (y quizá el bastión)", "Redundancia entre hosts (N+1); restaurar VM desde respaldo", "Servicio sin corte; reposición de VM ≤ 4 h"],
        ["Cae el primario de PostgreSQL", "Escrituras detenidas brevemente", "CloudNativePG promueve una réplica", "≤ 30 s"],
        ["Falla un disco de datos", "Volúmenes degradados, sin pérdida", "ZFS espejo + reconstrucción de réplicas Longhorn", "Sin corte"],
        ["Falla el switch core o el firewall", "Corte total de red (SPOF aceptado)", "Equipo de repuesto en frío y configuración respaldada", "≤ 2 h"],
    ], [3.6, 4.4, 5.6, 2.8], size=8)
    r.h2("5.8 Estrategia de ubicación y uso de recursos")
    r.jp("El planificador por defecto es rápido pero no optimiza la colocación ni considera la topología (Senjab et al., 2023; Luca y Eraşcu, 2023; Furnadzhiev "
         "et al., 2025). En un clúster de un solo sitio y tres nodos esto es aceptable si se guía mediante reglas explícitas: (1) todos los pods "
         "declaran __requests__ y __limits__; (2) se usan __PriorityClasses__ (plataforma > aplicaciones críticas > aplicaciones internas > "
         "lotes); (3) las réplicas se reparten por host con __topologySpreadConstraints__ y anti-afinidad; (4) los componentes de observabilidad se "
         "separan con afinidad hacia nodos con recursos libres; y (5) se usan __ResourceQuotas__ y __LimitRanges__ por namespace. Los planificadores "
         "basados en aprendizaje (Xu et al., 2024; Jian et al., 2023; Dakić et al., 2024b) quedan fuera del alcance por su complejidad, y se consideran trabajo futuro.")
    r.figuras_apaisadas([
        (F["arq"], "Arquitectura lógica general de la plataforma."),
        (F["desp"], "Diagrama de despliegue: hosts físicos, máquinas virtuales y cargas."),
        (F["flujo"], "Flujos de información de la plataforma."),
    ])


def seccion_6(r, F, vm_rows):
    r.h1("6. Diseño de Infraestructura")
    r.h2("6.1 Servidores")
    r.tabla("Especificación de los servidores físicos (3 unidades idénticas)", ["Elemento", "Especificación"], [
        ["Formato / función", "Servidor rack de 1U/2U con BMC (iDRAC/iLO); host de virtualización Proxmox VE"],
        ["Procesador", "1 × CPU de 16 núcleos / 32 hilos (clase Xeon Silver/EPYC)"],
        ["Memoria", "128 GB DDR4/DDR5 ECC (uso estimado por host: 40–46 GB; margen para absorber la carga de un host caído)"],
        ["Almacenamiento de sistema", "2 × SSD 480 GB en espejo (ZFS RAID-1) para Proxmox VE"],
        ["Almacenamiento de datos", "2 × SSD 1,92 TB empresarial en espejo ZFS (discos de VM; baja latencia de fsync para etcd)"],
        ["Red", "2 × 10 GbE SFP+ en bond LACP (troncal 802.1Q) + puerto de gestión BMC"],
        ["Energía", "Fuentes redundantes conectadas a UPS online"],
    ], [4.0, 12.4], size=8.5, bold_first=True)
    r.h2("6.2 Equipos de red y soporte")
    r.tabla("Otros equipos", ["Equipo", "Especificación y función"], [
        ["Firewall perimetral", "Appliance x86 con OPNsense: NAT, filtrado entre zonas, IDS/IPS, VPN WireGuard, DNS (Unbound) y NTP"],
        ["Switch core", "Administrable de 24 puertos con 802.1Q, LACP, ACL y puertos SFP+ de 10 GbE; conmuta en L2 (el enrutamiento lo hace el firewall)"],
        ["Servidor de respaldo", "Servidor con 4 × 8 TB (ZFS RAID-Z), 32 GB de RAM; MinIO (S3) en VLAN 60"],
        ["UPS y PDU", "UPS online de 3 kVA con autonomía ≥ 15 min y apagado ordenado; PDU administrable"],
        ["Rack y cableado", "Rack de 12U, DAC SFP+, cableado categoría 6A"],
    ], [4.0, 12.4], size=8.5, bold_first=True)
    r.h2("6.3 Sistemas operativos y virtualización")
    r.bullets([
        "**Hipervisor:** Proxmox VE (Debian, KVM/QEMU) con bridges VLAN-aware sobre bond LACP, ZFS y almacenamiento local por host. No se activa HA de "
        "hipervisor para no duplicar mecanismos: la resiliencia se delega a Kubernetes sobre tres dominios de falla.",
        "**Nodos del clúster:** Rocky Linux 9 (compatible con RHEL, soporte de largo plazo) con SELinux en modo enforcing, firewalld, chrony, "
        "módulos de kernel overlay/br_netfilter, swap desactivado y parámetros sysctl para Kubernetes; imagen base construida con Packer y Vagrant (Domínguez, 2024).",
        "**Firewall:** OPNsense (FreeBSD). **Respaldo:** Rocky Linux 9 con ZFS y MinIO.",
        "**Versiones:** se fijará una versión menor estable de Kubernetes soportada al momento de la implementación y se actualizará trimestralmente.",
    ])
    r.tabla("Catálogo de máquinas virtuales", ["Host", "VM", "Rol", "vCPU", "RAM", "Disco", "IP / VLAN"],
            vm_rows, [1.3, 1.5, 3.8, 1.1, 1.2, 2.6, 4.9], size=8, align_center_cols=(3, 4))
    r.jp("Totales: 54 vCPU y 128 GB de RAM asignados sobre 96 hilos y 384 GB físicos. Los workers (12 vCPU, 32 GB) ofrecen 24 vCPU y 64 GB "
         "con un worker caído, frente a una demanda estimada de 15 vCPU y 36 GB, lo que cumple el criterio N+1.")
    r.h2("6.4 Almacenamiento")
    r.tabla("Niveles de almacenamiento", ["Nivel", "Tecnología", "Capacidad", "Uso y protección"], [
        ["Host", "ZFS espejo (2 × 1,92 TB por host)", "≈ 1,9 TB útiles/host", "Discos de VM; snapshots ZFS; protege contra falla de 1 disco"],
        ["Clúster (persistente)", "Longhorn sobre disco de datos de 200 GB por worker", "600 GB brutos; ≈ 200–300 GB netos", "Clase general: 3 réplicas · clase BD: 2 réplicas; umbral de uso ≤ 70 %"],
        ["Respaldo", "MinIO sobre ZFS RAID-Z (4 × 8 TB)", "≈ 24 TB útiles", "etcd, Velero y WAL de PostgreSQL; retención 14–30 días"],
        ["Fuera de sitio", "Bucket S3 externo o disco rotado", "2 TB", "Copia semanal cifrada (regla 3-2-1)"],
    ], [2.4, 4.8, 3.8, 5.4], size=8.5)
    r.jp("Demanda estimada de Longhorn: bases de datos 3 × 20 GB × 2 réplicas = 120 GB; Prometheus 30 GB × 3 = 90 GB; Loki 30 GB × 3 = 90 GB; "
         "aplicaciones 20 GB × 3 = 60 GB; total ≈ 360 GB brutos (60 % de los 600 GB), con margen para crecimiento.")
    r.h2("6.5 Servicios requeridos")
    r.tabla("Servicios de soporte", ["Servicio", "Implementación", "Observación"], [
        ["DNS", "Unbound en OPNsense (zona interna) + CoreDNS en el clúster", "Registros A para VIP del API y de servicios"],
        ["NTP", "chrony con servidores internos y públicos", "Crítico para etcd y certificados"],
        ["Certificados", "cert-manager con CA interna y ACME para dominios públicos", "Renovación automática"],
        ["Registro de imágenes", "Registro del servidor Git (GitHub/GitLab) o Harbor", "Imágenes versionadas y escaneadas"],
        ["Repositorio Git y CI/CD", "GitHub Actions o GitLab CI", "Un único origen de verdad para manifiestos y roles de Ansible"],
        ["Correo / mensajería de alertas", "Relé SMTP y bot de Telegram", "Canal de alertas de Alertmanager (Domínguez, 2024)"],
        ["Directorio de identidades", "Cuentas locales con certificados y MFA en VPN; SSO OIDC (p. ej. Authentik) como fase 2", "Authentik empleado en Padial (2024)"],
    ], [3.4, 6.8, 6.2], size=8.5)
    r.h2("6.6 Perfil de laboratorio para la Tercera Unidad")
    r.jp("Dado que la implementación se hará sin acceso a tres servidores físicos, se define un **perfil de laboratorio** que conserva la topología "
         "lógica (mismos nombres, roles y direccionamiento) con recursos reducidos, siguiendo el enfoque con Vagrant/VirtualBox de Domínguez (2024).")
    r.tabla("Perfil de laboratorio (una estación con virtualización)", ["VM", "Cantidad", "vCPU", "RAM", "Notas"], [
        ["lb01, lb02", "2", "1", "1 GB", "HAProxy + Keepalived"],
        ["cp01–cp03", "3", "2", "3 GB", "Mínimo recomendado por kubeadm: 2 vCPU"],
        ["wk01–wk03", "3", "2", "4 GB + disco de 30 GB", "Longhorn y cargas de prueba reducidas"],
        ["bastión", "1", "1", "1 GB", "Ansible, kubectl, Helm"],
        ["Total", "9", "15", "≈ 24 GB", "Estación con ≥ 32 GB de RAM, ≥ 8 núcleos y ≥ 200 GB SSD"],
    ], [3.2, 2.0, 1.8, 4.0, 5.4], size=8.5, align_center_cols=(1, 2))
    r.nota("**Qué se puede validar en el laboratorio:** toda la lógica de HA (VIP, quórum de etcd, conmutación de BD), seguridad por software, observabilidad, respaldo y "
           "automatización. **Qué se valida solo parcialmente:** el aislamiento por VLAN 802.1Q (se emula con redes internas del hipervisor), la falla de un host físico "
           "(se simula apagando el grupo de VM de un «host lógico») y los valores absolutos de rendimiento.")


def seccion_7(r, F, vlan_rows, ip_rows, fw_rows):
    r.h1("7. Diseño de Red")
    r.h2("7.1 Topología")
    r.jp("La red usa una topología **en estrella jerárquica** con un firewall perimetral y un switch core que concentra a los tres hosts mediante "
         "troncales 802.1Q en bond LACP (Figura 4, al final de esta sección). El firewall es el gateway de todas las VLAN (subinterfaces sobre la troncal) y controla el tráfico entre zonas y "
         "hacia Internet, mientras que el switch conmuta en L2 y aplica ACL de respaldo. Dentro de cada host, un bridge Proxmox VLAN-aware etiqueta las interfaces de las VM.")
    r.h2("7.2 Segmentación y VLAN")
    r.tabla("Plan de VLAN y subredes", ["VLAN", "Nombre", "Subred", "Gateway", "Propósito"],
            vlan_rows, [1.5, 3.0, 2.8, 2.5, 6.6], size=8.5, align_center_cols=(0,))
    r.jp("La separación entre gestión (10), plano de control (20) y nodos de trabajo (30) impide que un pod comprometido alcance directamente el "
         "API, el kubelet o etcd desde la red de aplicaciones; la VLAN de almacenamiento (40) no tiene gateway y transporta solo replicación de volúmenes; "
         "y la VLAN de servicios (50) es la única que anuncia direcciones hacia los usuarios. Los rangos internos de Kubernetes no se solapan con ninguna VLAN: "
         "pods 10.244.0.0/16 y servicios 10.96.0.0/12.")
    r.h2("7.3 Direccionamiento IP")
    r.tabla("Direcciones fijas principales", ["Elemento", "Dirección", "Red", "Comentario"],
            ip_rows, [4.2, 3.6, 2.4, 6.2], size=8.5)
    r.h2("7.4 Firewall")
    r.jp("La política es **denegar por defecto** entre todas las zonas, con reglas explícitas y registradas. Además del firewall de red, cada nodo "
         "ejecuta firewalld con solo los puertos necesarios y Cilium aplica NetworkPolicy dentro del clúster.")
    r.tabla("Matriz resumida de reglas entre zonas", ["#", "Origen", "Destino", "Puertos", "Acción", "Justificación"],
            fw_rows, [0.8, 2.7, 3.2, 3.3, 1.3, 5.1], size=8, align_center_cols=(0, 4))
    r.h2("7.5 Acceso remoto")
    r.bullets([
        "**VPN WireGuard** terminada en el firewall (UDP 51820), con llaves por usuario y segundo factor (TOTP) en el portal de acceso; la VPN solo permite llegar al bastión (VLAN 10).",
        "**Bastión SSH** como único punto de administración: autenticación con llaves ed25519, contraseña deshabilitada, registro de sesiones y listas de usuarios autorizados.",
        "El API de Kubernetes (6443), la consola de Proxmox (8006) y los BMC **nunca se publican en Internet**; solo son alcanzables desde la VLAN de gestión.",
        "**Administración del clúster:** kubectl se ejecuta desde el bastión o desde estaciones autorizadas por la VPN usando certificados de cliente de vigencia corta.",
        "**Higiene:** tiempo de sesión limitado, revisión trimestral de llaves y accesos, y alerta ante inicios de sesión fuera de horario.",
    ])
    r.figuras_apaisadas([(F["red"], "Topología de red y segmentación por VLAN.")])
