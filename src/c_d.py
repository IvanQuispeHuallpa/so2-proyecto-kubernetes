"""Secciones 10 a 14 y anexo."""
import datos
from refs import REFERENCIAS


def seccion_10(r, F):
    r.h1("10. Plan de Implementación")
    r.h2("10.1 Estrategia")
    r.jp("La Tercera Unidad implementará, validará y sustentará **todo lo aquí diseñado** en un entorno de laboratorio a escala (Sección 6.6), con un enfoque "
         "incremental de ocho semanas: primero la base (infraestructura y balanceo), luego el clúster HA, a continuación los servicios de plataforma y, "
         "finalmente, la observabilidad, la seguridad, la aplicación de validación, el respaldo y las pruebas. Todo cambio se versiona en Git y se aplica con "
         "Ansible o Helm; no se incorporarán componentes ajenos al diseño sin una justificación técnica documentada.")
    r.h2("10.2 Actividades")
    r.tabla("Actividades, entregables y responsables", ["ID", "Actividad", "Entregable", "Rol", "Semanas"], [
        ["A1", "Preparación del entorno y repositorio IaC", "Repositorio, inventario Ansible, plantillas Vagrant/Packer, convenciones", "Arquitecto", "S1"],
        ["A2", "Infraestructura base", "VM Rocky Linux 9 endurecidas, redes/VLAN emuladas, chrony, DNS", "Infraestructura", "S1–S2"],
        ["A3", "Balanceo del API", "HAProxy + Keepalived con VIP 10.10.20.10 y pruebas de conmutación", "Infraestructura", "S2"],
        ["A4", "Clúster Kubernetes HA", "3 nodos de control con etcd apilado y 3 workers con kubeadm", "Plataforma", "S2–S3"],
        ["A5", "Servicios de plataforma", "Cilium, MetalLB, Traefik, metrics-server, cert-manager, Longhorn, operador CloudNativePG", "Plataforma", "S3–S4"],
        ["A6", "Observabilidad", "kube-prometheus-stack, Loki/Alloy, Hubble, alertas y paneles", "Operación", "S4–S5"],
        ["A7", "Seguridad", "RBAC, PSA, NetworkPolicy, cifrado de Secrets, auditoría, Trivy, kube-bench", "Seguridad", "S4–S5"],
        ["A8", "Aplicación de validación y CI/CD", "Aplicación de 3 capas, PostgreSQL HA, HPA y pipeline", "Desarrollo", "S5–S6"],
        ["A9", "Respaldo y recuperación", "Snapshots de etcd, Velero, MinIO y runbooks probados", "Operación", "S6"],
        ["A10", "Ejecución del plan de pruebas", "Informe de pruebas con evidencias", "Todos", "S7"],
        ["A11", "Documentación y sustentación", "Documento final, manual de operación y presentación", "Todos", "S7–S8"],
    ], [1.0, 3.8, 7.0, 2.6, 2.0], size=8.5, align_center_cols=(0, 4))
    r.h2("10.3 Recursos necesarios")
    r.tabla("Recursos", ["Tipo", "Detalle"], [
        ["Humanos", "6 integrantes con dedicación de 8–10 h semanales (≈ 400–480 h en total) distribuidos en los roles de arquitectura, infraestructura, plataforma, seguridad, operación y desarrollo"],
        ["Hardware (laboratorio)", "Una estación con ≥ 32 GB de RAM, ≥ 8 núcleos y ≥ 200 GB SSD con virtualización habilitada; opcionalmente un segundo equipo para el servidor de respaldo"],
        ["Software", "Rocky Linux 9, VirtualBox/Vagrant/Packer (o Proxmox anidado), Ansible, kubeadm, containerd, Cilium, MetalLB, Traefik, Longhorn, CloudNativePG, Prometheus/Grafana/Loki, Velero, MinIO, Trivy, kube-bench, Helm, k6, iperf3 (todo de código abierto)"],
        ["Servicios", "Acceso a Internet para repositorios e imágenes; repositorio Git con CI; cuenta de correo o bot de Telegram para alertas"],
        ["Presupuesto", "US$ 0 de adquisición para el laboratorio (uso de equipos existentes); el CapEx de la Sección 12 corresponde al despliegue real"],
    ], [3.4, 13.0], size=8.5, bold_first=True)
    r.h2("10.4 Dependencias")
    r.tabla("Dependencias entre actividades", ["Actividad", "Depende de", "Observación"], [
        ["A2 Infraestructura base", "A1", "Requiere plantillas y convenciones definidas"],
        ["A3 Balanceo del API", "A2", "La VIP debe existir antes de ejecutar kubeadm init"],
        ["A4 Clúster HA", "A2, A3", "kubeadm usa controlPlaneEndpoint = VIP"],
        ["A5 Servicios de plataforma", "A4", "Sin CNI los nodos no quedan Ready"],
        ["A6 Observabilidad", "A5", "Necesita almacenamiento persistente y red operativa"],
        ["A7 Seguridad", "A5", "NetworkPolicy exige Cilium; puede avanzar en paralelo con A6"],
        ["A8 Aplicación y CI/CD", "A5, A6", "Requiere Ingress, almacenamiento y métricas para el HPA"],
        ["A9 Respaldo", "A5, A6", "Depende de Longhorn, CloudNativePG y MinIO"],
        ["A10 Pruebas", "A6, A7, A8, A9", "Todas las funciones deben estar implementadas"],
        ["A11 Documentación", "A10 (parcial)", "Se documenta de forma continua; el cierre depende de los resultados"],
    ], [4.2, 3.2, 9.0], size=8.5)
    r.h2("10.5 Cronograma")
    r.figura(F["gantt"], "Cronograma de implementación en la Tercera Unidad (8 semanas).", 15.5)
    r.h2("10.6 Riesgos del proyecto")
    r.tabla("Riesgos del proyecto y mitigación", ["Riesgo", "Prob.", "Mitigación"], [
        ["Recursos de laboratorio insuficientes para 9 VM", "Media", "Reducir memoria por VM; usar K3s como contingencia documentada (Koziolek y Eskandani, 2023)"],
        ["Incompatibilidad entre versiones de componentes", "Media", "Fijar versiones en el inventario y probar en rama aislada antes de fusionar"],
        ["Retraso por curva de aprendizaje en Cilium o Longhorn", "Alta", "Asignar un responsable por componente y reservar tiempo de holgura en S5–S6"],
        ["Dependencia de Internet para imágenes y paquetes", "Media", "Registro local o caché de imágenes y repositorios espejo"],
        ["Pérdida del laboratorio por error", "Media", "Plantillas Packer, IaC y respaldo de configuración; capacidad de reconstruir en < 4 h"],
    ], [6.4, 1.6, 8.4], size=8.5, align_center_cols=(1,))


def seccion_11(r, pruebas):
    r.h1("11. Plan de Pruebas")
    r.h2("11.1 Estrategia y entorno")
    r.jp("El plan verifica que cada requerimiento (Sección 4) se cumple. Las pruebas se agrupan en infraestructura y red (PI), alta disponibilidad (PH), "
         "seguridad (PS), rendimiento y escalabilidad (PR), respaldo y recuperación (PB), y observabilidad y operación (PO, PM). Se ejecutan en el entorno de "
         "laboratorio, con **tres repeticiones** en las pruebas de falla para obtener tiempos medios, y se conservan evidencias (capturas de paneles, registros y salidas "
         "de comandos). Herramientas: kubectl, etcdctl, kube-bench, Trivy, nmap, iperf3, k6 (carga), Velero y los paneles de Grafana/Hubble.")
    for titulo, filas in pruebas:
        r.h2(titulo)
        r.tabla(titulo, ["ID", "Qué se probará", "Cómo se probará", "Resultado esperado", "Criterio de aceptación"],
                filas, [1.2, 3.0, 4.9, 3.6, 3.7], size=7.8, align_center_cols=(0,))
    r.h2("11.8 Criterios globales de aceptación")
    r.bullets([
        "**100 %** de las pruebas de alta disponibilidad (PH) y de respaldo y recuperación (PB) aprobadas.",
        "**≥ 95 %** del total de casos aprobados, sin defectos críticos abiertos; los defectos menores quedan registrados con plan de corrección.",
        "Las metas de RPO/RTO, disponibilidad y latencia (Sección 4.2) se cumplen en tres corridas consecutivas.",
        "Cada resultado cuenta con evidencia reproducible y un responsable que lo firma.",
    ])


def money(v):
    return f"US$ {v:,}".replace(",", " ")


def seccion_12(r, F):
    r.h1("12. Análisis de Factibilidad")
    r.h2("12.1 Factibilidad técnica")
    r.jp("La propuesta es técnicamente factible porque todos sus componentes son de código abierto, maduros y están documentados en despliegues análogos "
         "de la literatura revisada (Tabla siguiente). Además, el perfil de laboratorio permite validar la lógica completa de alta disponibilidad con un solo equipo.")
    r.tabla("Evidencia de viabilidad técnica en la literatura", ["Fuente", "Qué demuestra", "Relevancia para el diseño"], [
        ["Domínguez (2024)", "Clúster HA de 5 nodos (3 de control, 2 workers) con Ansible, Keepalived, HAProxy y monitoreo", "Base directa del plano de control y del balanceo"],
        ["Jovaní (2023); Jaramillo (2023)", "Clústeres HA con kubeadm en máquinas virtuales y en nube, con HPA y balanceador", "Valida el patrón y permite comparar con la nube"],
        ["Ramírez (2021)", "Clúster HA en nube con Ansible, Prometheus/Grafana y PostgreSQL", "Automatización y despliegue con base de datos"],
        ["Giurgică et al. (2025); Iñesta (2024)", "Clústeres en hardware de bajo costo con MetalLB, Prometheus y Ansible/Helm", "Confirma que la pila es portable a recursos reducidos"],
        ["Padial (2024)", "Infraestructura virtualizada con Proxmox VE sobre un servidor propio", "Respaldo para la capa de virtualización"],
        ["Aguilar y García (2024)", "−77 % en tiempo de despliegue y −60 % en incidencias en una entidad estatal peruana", "Beneficio esperado y contexto local"],
    ], [3.8, 7.4, 5.2], size=8.5)
    r.jp("**Riesgos técnicos:** la complejidad de operar Kubernetes frente a alternativas más simples (Hernández, 2024), la curva de aprendizaje de Cilium y Longhorn, y "
         "la deuda técnica derivada de la rápida evolución de Kubernetes (Maarleveld et al., 2025). Se mitigan con automatización, capacitación, actualización trimestral y "
         "documentación operativa.")
    r.h2("12.2 Factibilidad económica")
    r.jp("Se estiman la inversión inicial (CapEx), el costo operativo anual (OpEx) y la comparación a cinco años con una nube gestionada equivalente. Los valores son "
         "**referenciales del equipo** y no incluyen el costo de personal, que se asume igual en ambas alternativas.")
    r.tabla("Inversión inicial estimada (CapEx)", ["Concepto", "Cant.", "P. unit. (US$)", "Subtotal (US$)"],
            [[c, str(n), f"{p:,}".replace(",", " "), f"{n * p:,}".replace(",", " ")] for c, n, p in datos.CAPEX]
            + [["**Total CapEx**", "", "", f"**{datos.CAPEX_TOTAL:,}**".replace(",", " ")]],
            [9.6, 1.4, 2.7, 2.7], size=8.5, align_center_cols=(1, 2, 3))
    r.tabla("Costo operativo anual estimado (OpEx)", ["Concepto", "US$ / año"],
            [[c, f"{v:,}".replace(",", " ")] for c, v in datos.OPEX] + [["**Total OpEx anual**", f"**{datos.OPEX_TOTAL:,}**".replace(",", " ")]],
            [13.0, 3.4], size=8.5, align_center_cols=(1,))
    r.jp("La nube gestionada equivalente (3 nodos de 8 vCPU y 32 GB, plano de control gestionado, 600 GB de almacenamiento, balanceadores, salida de datos y "
         f"observabilidad) costaría ≈ {money(datos.CLOUD_MES_TOTAL)} al mes bajo demanda y ≈ {money(datos.CLOUD_RESERVADO_MES)} con un compromiso de un año.")
    filas = []
    for i, a in enumerate(datos.AÑOS):
        f = lambda v: f"{v:,}".replace(",", " ")
        filas.append([f"Año {a}", f(datos.TCO_ONPREM[i]), f(datos.TCO_CLOUD[i]), f(datos.TCO_CLOUD_RES[i])])
    r.tabla("Costo total de propiedad acumulado (US$)", ["Horizonte", "On-premise", "Nube bajo demanda", "Nube con compromiso de 1 año"], filas,
            [3.2, 4.0, 4.4, 4.8], size=8.5, align_center_cols=(0, 1, 2, 3))
    r.figura(F["tco"], "Costo total de propiedad acumulado a cinco años (estimación referencial).", 14.5)
    r.jp("**Lectura del resultado.** La opción on-premise supera a la nube bajo demanda a partir del año 4 (US$ 57 100 frente a 61 056) y llega a US$ 64 000 al "
         "año 5 frente a US$ 76 320; sin embargo, con un compromiso de un año la nube resulta más barata en todo el horizonte (US$ 58 680 a cinco años). La ventaja de la "
         "propuesta no es, por tanto, puramente económica: reside en la **soberanía de los datos, el control de la infraestructura, la ausencia de dependencia de proveedor y "
         "el aprendizaje del equipo**, y mejora si la Organización reutiliza hardware existente (con un 50 % de reutilización, el CapEx baja a ≈ US$ 14 750 y el costo a cinco "
         "años a ≈ US$ 49 250). Kim et al. (2026) muestran además que la nube puede abaratarse con instancias spot, a costa de mayor complejidad por interrupciones.")
    r.jp("**Beneficios cuantificables:** si el tiempo de despliegue baja de 45 a 10 minutos (Aguilar y García, 2024) con unos 24 despliegues mensuales, se liberan "
         "≈ 14 horas al mes de trabajo técnico, además de la reducción de incidentes por caídas, cuyo costo depende de la criticidad de cada servicio.")
    r.h2("12.3 Factibilidad operativa")
    r.bullets([
        "**Capacidades del equipo:** se requiere experiencia en Linux, redes y contenedores; se prevé capacitación de 40 horas por administrador y la preparación de la certificación CKA (incluida en el OpEx).",
        "**Procesos:** el modelo operativo (Sección 9) define roles, RACI, mantenimiento e incidentes; la guardia 24×7 solo aplica a incidentes P1.",
        "**Gestión del cambio:** migración gradual por aplicaciones, empezando por servicios internos de baja criticidad y dejando el portal público para el final.",
        "**Sostenibilidad:** automatización completa y documentación reducen la dependencia de personas clave; la actualización trimestral controla la deuda técnica.",
        "**Indicadores de éxito:** disponibilidad ≥ 99,9 %; tiempo de despliegue ≤ 10 min; 100 % de respaldos verificados trimestralmente; MTTR de P1 ≤ 2 h; 0 puertos de administración expuestos.",
    ])


def seccion_13(r):
    r.h1("13. Conclusiones")
    r.numbered([
        "La investigación bibliográfica permitió convertir hallazgos concretos en decisiones de diseño verificables (Tabla de trazabilidad de la Sección 2.4): etcd de tres miembros, bases de datos gestionadas por operador, Kubernetes completo para cargas sostenidas, Cilium para políticas de red y observabilidad basada en Prometheus.",
        "La arquitectura propuesta elimina los puntos únicos de falla lógicos en el plano de control, el balanceo, el cómputo y los datos, repartiéndolos en tres dominios de falla físicos con capacidad N+1, y cuantifica el comportamiento esperado ante cada falla.",
        "El diseño de seguridad aplica defensa en profundidad con base en un análisis de riesgos: tres riesgos críticos iniciales se reducen a niveles medio o bajo y los riesgos residuales aceptados (red de un solo switch y fallas bizantinas) quedan explícitos.",
        "El modelo operativo y el plan de pruebas convierten los requerimientos en criterios medibles (disponibilidad ≥ 99,9 %, RPO ≤ 5 min, RTO ≤ 30 min), lo que hace verificable la implementación de la Tercera Unidad.",
        "Económicamente, la alternativa on-premise (CapEx ≈ US$ 29 500) es comparable a la nube bajo demanda a cinco años, pero no es la más barata frente a la nube con compromiso; su justificación es el control, la soberanía de los datos y el valor formativo, lo que se declara de manera transparente.",
        "Las principales limitaciones son que los costos son estimaciones referenciales, que el escenario es supuesto y que el laboratorio a escala solo valida parcialmente el aislamiento por VLAN y el rendimiento absoluto.",
        "Como trabajo futuro se proponen un segundo switch y firewall en alta disponibilidad, SSO con OIDC, autoescalado predictivo con KEDA (Jiang y Milani, 2026), un portal de desarrolladores (Gómez, 2023), un sitio de recuperación ante desastres en la nube y la evaluación de planificadores basados en aprendizaje (Xu et al., 2024; Jian et al., 2023).",
    ])


def seccion_14(r):
    r.h1("14. Referencias Bibliográficas")
    r.p("Las referencias corresponden a la revisión de la Primera Unidad. Los artículos y tesis se citan en formato APA 7.ª edición adaptado; las entradas sin "
        "DOI provienen de los documentos entregados al equipo.", size=9.5, italic=True)
    for ref in REFERENCIAS:
        par = r.d.add_paragraph()
        r._runs(par, ref, size=9)
        pf = par.paragraph_format
        pf.left_indent = r.d.sections[0].page_width * 0 + __import__("docx").shared.Cm(1.0)
        pf.first_line_indent = -__import__("docx").shared.Cm(1.0)
        pf.space_after = __import__("docx").shared.Pt(2)


def anexo(r):
    r.h1("Anexo A. Fragmentos de configuración de referencia")
    r.jp("Se incluyen fragmentos mínimos que serán la base de la implementación; los valores secretos y las versiones se completarán en la Tercera Unidad.")
    r.code("""frontend k8s-api
    bind 10.10.20.10:6443
    mode tcp
    option tcplog
    default_backend k8s-cp
backend k8s-cp
    mode tcp
    balance roundrobin
    option tcp-check
    default-server inter 3s fall 3 rise 2
    server cp01 10.10.20.21:6443 check
    server cp02 10.10.20.22:6443 check
    server cp03 10.10.20.23:6443 check""", "HAProxy (lb01 y lb02; requiere net.ipv4.ip_nonlocal_bind=1)")
    r.code("""vrrp_script chk_haproxy {
    script "/usr/bin/pidof haproxy"
    interval 2
    weight -20
}
vrrp_instance VI_API {
    state MASTER            # BACKUP en lb02
    interface eth0
    virtual_router_id 51
    priority 110            # 100 en lb02
    advert_int 1
    authentication { auth_type PASS  auth_pass <secreto> }
    virtual_ipaddress { 10.10.20.10/24 }
    track_script { chk_haproxy }
}""", "Keepalived (VIP del API)")
    r.code("""apiVersion: kubeadm.k8s.io/v1beta4
kind: ClusterConfiguration
kubernetesVersion: <versión fijada en A1>
controlPlaneEndpoint: "10.10.20.10:6443"
networking:
  podSubnet: 10.244.0.0/16
  serviceSubnet: 10.96.0.0/12""", "kubeadm: inicialización del primer nodo de control (con --upload-certs)")
    r.code("""apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-all, namespace: prod }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
# Pod Security Admission en el namespace de aplicaciones
# kubectl label ns prod pod-security.kubernetes.io/enforce=restricted""", "Seguridad: denegar por defecto y Pod Security Admission")
