"""Secciones 1 a 4: resumen, problema, objetivos y requerimientos."""


def seccion_1(r):
    r.h1("1. Resumen Ejecutivo")
    r.jp("Este documento presenta el diseño de una **plataforma de orquestación de contenedores basada en Kubernetes con alta "
         "disponibilidad (HA)**, orientada a alojar las aplicaciones web internas y públicas de una organización mediana (en adelante, "
         "«la Organización»). El diseño se deriva de la revisión bibliográfica realizada en la Primera Unidad, que comprendió 43 trabajos: "
         "artículos científicos, tesis de grado y de maestría sobre despliegue, disponibilidad, planificación, autoescalado, seguridad y "
         "monitoreo de clústeres Kubernetes.")
    r.jp("**Problema.** Las aplicaciones de la Organización se ejecutan hoy en máquinas virtuales individuales, sin redundancia, con "
         "despliegues manuales y sin observabilidad centralizada. Cualquier falla de un servidor, una actualización o un error operativo "
         "implica indisponibilidad y tiempos de recuperación impredecibles.")
    r.jp("**Solución propuesta.** Un clúster Kubernetes de **3 nodos de plano de control (etcd apilado) y 3 nodos de trabajo**, "
         "distribuidos en **3 hosts físicos con Proxmox VE** (tres dominios de falla), con un par **HAProxy + Keepalived** que publica una "
         "IP virtual para el API, **MetalLB + Traefik** para exponer servicios, **Cilium** como red de contenedores y motor de políticas, "
         "**Longhorn** para almacenamiento replicado y **CloudNativePG** para bases de datos con conmutación automática. La plataforma se "
         "completa con observabilidad (Prometheus, Grafana, Loki), seguridad en profundidad (RBAC, Pod Security Admission, NetworkPolicy, "
         "cifrado de Secrets, escaneo de imágenes), respaldo 3-2-1 (etcd, Velero, MinIO) y automatización total con Ansible y CI/CD.")
    r.tabla("Indicadores clave de la propuesta", ["Indicador", "Valor de diseño"], [
        ["Disponibilidad objetivo de aplicaciones críticas", "≥ 99,9 % mensual (≤ 43,8 min de indisponibilidad al mes)"],
        ["Tolerancia a fallas", "1 nodo de control, 1 balanceador, 1 worker o 1 host físico completo sin pérdida de servicio (criterio N+1)"],
        ["RPO / RTO", "RPO ≤ 5 min (BD) · RTO ≤ 30 min (restauración de un namespace) · reconstrucción total ≤ 4 h"],
        ["Inversión inicial (CapEx) estimada", "US$ 29 500"],
        ["Costo operativo anual estimado (sin personal)", "US$ 6 900"],
        ["Plazo de implementación (III Unidad)", "8 semanas, en entorno de laboratorio a escala"],
    ], [7.0, 9.4], size=9, bold_first=True)
    r.nota("**Alcance y supuestos.** El enunciado de la II Unidad no fija una organización concreta; por ello se adopta un __escenario de "
           "referencia__ (Tabla 2) y se documentan los supuestos. Los costos de hardware, energía y nube son **estimaciones referenciales** "
           "del equipo (no provienen de los artículos) y deben validarse con cotizaciones antes de una adquisición real.")


def seccion_2(r):
    r.h1("2. Planteamiento del Problema")
    r.h2("2.1 Situación actual")
    r.jp("Para dimensionar la solución se define un escenario de referencia representativo de una entidad mediana, similar al caso de una "
         "entidad estatal estudiado por Aguilar y García (2024), donde el tiempo promedio de despliegue era de 45 minutos y las caídas de sistemas "
         "eran frecuentes.")
    r.tabla("Escenario de referencia y supuestos de dimensionamiento", ["Aspecto", "Situación / supuesto"], [
        ["Usuarios y servicios", "≈ 250 usuarios internos; 12 aplicaciones web internas y 1 portal público; pico estimado de 200 solicitudes/s"],
        ["Arquitectura de las aplicaciones", "Monolitos y servicios en VM individuales, 1 base de datos PostgreSQL por aplicación sin réplica"],
        ["Despliegue", "Manual (copia de archivos y reinicio), 30–45 min por versión, sin reversión automatizada"],
        ["Disponibilidad", "Sin redundancia: una falla de VM o de host implica caída hasta intervención humana"],
        ["Respaldo", "Copias manuales y no verificadas; sin pruebas de restauración"],
        ["Monitoreo", "Revisiones puntuales; sin alertas ni correlación de eventos; sin registros centralizados"],
        ["Seguridad", "Red plana, accesos compartidos, sin segmentación ni escaneo de vulnerabilidades"],
        ["Carga estimada en contenedores", "≈ 36 pods de aplicación (12 apps × 3 réplicas) + bases de datos + pila de monitoreo ≈ 15 vCPU y 36 GB de memoria solicitados"],
    ], [4.4, 12.0], size=9, bold_first=True)
    r.h2("2.2 Necesidad identificada")
    r.bullets([
        "**Continuidad del servicio:** tolerar fallas de componentes y de hardware sin intervención manual (disponibilidad ≥ 99,9 %).",
        "**Agilidad de despliegue:** reducir el tiempo de publicación de nuevas versiones y permitir reversión inmediata.",
        "**Seguridad y cumplimiento:** segmentar la red, controlar accesos por rol y mantener trazabilidad de cambios y accesos.",
        "**Recuperabilidad:** disponer de respaldos verificados y de un procedimiento de restauración con metas RPO/RTO definidas.",
        "**Visibilidad operativa:** detectar degradaciones antes de que las perciban los usuarios.",
        "**Eficiencia:** aprovechar mejor el hardware existente mediante contenedores y autoescalado.",
    ])
    r.h2("2.3 Justificación de la propuesta")
    r.jp("Kubernetes es el estándar de facto para orquestar contenedores: automatiza el despliegue, el escalado y la recuperación de servicios "
         "(Burns et al., 2016; Camacho et al., 2020; Sachdeva, 2023). Los antecedentes revisados muestran beneficios medibles. En una entidad estatal "
         "peruana, la adopción de Kubernetes redujo el tiempo promedio de despliegue de 45 a 10 minutos (−77 %) y las incidencias por caídas de "
         "sistemas en un 60 % (Aguilar y García, 2024). Diversos trabajos de grado documentan despliegues de clústeres de alta disponibilidad "
         "sobre máquinas virtuales locales o nubes públicas, con automatización mediante Ansible (Domínguez, 2024; Ramírez, 2021; Jovaní, 2023; "
         "Jaramillo, 2023), lo que respalda la viabilidad técnica del enfoque.")
    r.jp("La alta disponibilidad no es automática: la investigación advierte que la recuperación nativa de pods con estado deja el servicio "
         "indisponible hasta que el pod se repara (Vayghan et al., 2020), que el almacén etcd limita el rendimiento a medida que crece el número de "
         "miembros (Jeffery et al., 2021) y que Raft tolera fallas por parada pero no comportamientos bizantinos (Diouf et al., 2020). El diseño "
         "debe, por tanto, tomar decisiones explícitas sobre cada uno de estos puntos. Finalmente, se opta por una solución **on-premise** porque el "
         "enunciado exige definir servidores, red, firewall y VLAN, y porque conserva la soberanía de los datos y evita la dependencia de un proveedor; "
         "la comparación económica con la nube se presenta en la Sección 12.")
    r.jp("Otros trabajos revisados completan el panorama: aplicaciones escalables con autoescalado horizontal (López, 2020; Rodríguez, 2022), integración continua y "
         "monitoreo en un Kubernetes gestionado (Montanuy, 2023), un modelo de composición de microservicios sobre Kubernetes en el contexto peruano (Ruelas, 2017), "
         "nubes híbridas con OpenStack y Amazon (Mejía y Barbecho, 2021), bucles de control auto-adaptativos MAPE-K (Blanco, 2021) y plataformas serverless sobre "
         "Kubernetes (Decker et al., 2022). Estos temas se consideran evolución futura y no forman parte del alcance base de este diseño.")
    r.h2("2.4 Síntesis de la investigación bibliográfica y decisiones de diseño")
    r.jp("La Tabla 3 resume los hallazgos de la Primera Unidad que condicionan el diseño y la decisión que se adoptó en cada caso. Esta "
         "trazabilidad se mantiene en las secciones posteriores.")
    r.tabla("Trazabilidad entre hallazgos de la investigación y decisiones de diseño", ["Hallazgo", "Fuente", "Decisión de diseño"], [
        ["Un clúster HA práctico usa 3 nodos de control, balanceador con IP virtual (Keepalived + HAProxy) y automatización con Ansible",
         "Domínguez (2024); Ramírez (2021); Jovaní (2023)", "Plano de control de 3 nodos con etcd apilado; par lb01/lb02; IaC con Ansible"],
        ["Latencia de escritura de etcd aumenta y el rendimiento cae al crecer el clúster; ≈30 % de las solicitudes son escrituras",
         "Jeffery et al. (2021)", "etcd de 3 miembros (no 5); discos SSD dedicados; monitoreo de latencia de etcd"],
        ["Raft solo tolera fallas por parada, no bizantinas",
         "Diouf et al. (2020)", "Riesgo aceptado con mitigación: endurecimiento, RBAC, auditoría y aislamiento de red del plano de control"],
        ["La recuperación nativa de aplicaciones con estado es lenta; un controlador específico mejoró la recuperación ≈50 %",
         "Vayghan et al. (2020)", "BD con operador (CloudNativePG) y conmutación automática en lugar de depender solo de StatefulSet"],
        ["Las distribuciones ligeras (K3s, MicroK8s) rinden bien en borde, pero Kubernetes completo se comporta mejor en cargas sostenidas",
         "Böhm y Wirtz (2021); Kjorveziroski y Filiposka (2022); Koziolek y Eskandani (2023)", "kubeadm (Kubernetes completo) en producción; K3s solo como alternativa de contingencia"],
        ["Docker Swarm consume menos recursos, pero Kubernetes es superior en funciones; su coste puede ser excesivo en casos simples",
         "Hernández (2024)", "Se justifica Kubernetes por los requisitos de HA, autoescalado y políticas, no por moda"],
        ["No hay un CNI óptimo universal: Antrea, Flannel, Cilium y Calico difieren en ancho de banda y latencia",
         "Dakić et al. (2024a)", "Cilium por sus políticas y observabilidad; se valida con iperf3 (PR-03)"],
        ["Una capa eBPF con políticas de red y autoescalado predictivo redujo en 32 % los timeouts ante picos y mitigó el autoescalado inducido por DDoS",
         "Jiang y Milani (2026)", "Cilium (eBPF) + límites de réplicas máximas en HPA + límite de tasa en Ingress"],
        ["HPA se comporta de forma distinta con métricas de recursos y con métricas personalizadas de Prometheus",
         "Nguyen et al. (2020)", "HPA con metrics-server (CPU); métricas personalizadas como mejora posterior"],
        ["MetalLB ofrece balanceo y conmutación en clústeres on-premise; Prometheus + Grafana dan visibilidad de salud y carga",
         "Giurgică et al. (2025); Ramírez (2021); Romero (2022)", "MetalLB en modo L2; kube-prometheus-stack + Loki"],
        ["El planificador por defecto no considera topología ni latencia y puede colocar mal las réplicas",
         "Senjab et al. (2023); Luca y Eraşcu (2023); Furnadzhiev et al. (2025)", "topologySpreadConstraints y anti-afinidad entre los 3 hosts; requests/limits obligatorios"],
        ["La seguridad en Kubernetes requiere gestión de riesgos, modelo 4C, control de privilegios, firmas de imágenes y RBAC",
         "Simón (2021); Guardiola (2020)", "Diseño de seguridad por capas (Sección 8); superficies del API, kubelet y etcd cerradas por red"],
        ["Las políticas PodSecurityPolicy usadas en trabajos previos ya no existen en versiones actuales",
         "Simón (2021); Maarleveld et al. (2025)", "Pod Security Admission; política de actualización trimestral para evitar deuda técnica"],
        ["La monitorización con correlación de eventos permite detectar proactivamente fallas de pods y redes",
         "Tambi (2024)", "Reglas de Alertmanager con agrupación e inhibición; paneles por capa"],
        ["Los patrones de tolerancia a fallas a nivel de aplicación (tiempos de espera y rutas secundarias) complementan a la plataforma",
         "Gustafsson et al. (2025); Javed et al. (2020)", "Probes, timeouts y reintentos en el Ingress; réplicas en dominios de falla distintos"],
        ["Virtualizar con Proxmox VE y replicar almacenamiento (GlusterFS) permite infraestructura propia sobre pocos servidores",
         "Padial (2024)", "Proxmox VE como hipervisor; Longhorn como almacenamiento replicado a nivel de Kubernetes"],
    ], [6.3, 4.4, 5.7], size=8)


def seccion_3(r):
    r.h1("3. Objetivos")
    r.h2("3.1 Objetivo general")
    r.jp("Diseñar una plataforma de orquestación de contenedores basada en Kubernetes, con alta disponibilidad, seguridad, observabilidad y "
         "operación automatizada, que permita a la Organización alojar sus aplicaciones web con una disponibilidad mensual igual o superior al "
         "99,9 %, sustentando cada decisión en los resultados de la investigación bibliográfica.")
    r.h2("3.2 Objetivos específicos")
    r.numbered([
        "Definir los requerimientos funcionales y no funcionales de la plataforma a partir del escenario de referencia y de la literatura revisada.",
        "Diseñar la arquitectura lógica y física del clúster, eliminando puntos únicos de falla en el plano de control, el balanceo y los nodos de trabajo.",
        "Especificar la infraestructura (servidores, virtualización, sistemas operativos, almacenamiento) y la red (VLAN, direccionamiento, firewall y acceso remoto).",
        "Establecer un diseño de seguridad basado en gestión de riesgos, con controles preventivos, detectivos y correctivos, gestión de accesos, respaldo y auditoría.",
        "Definir el modelo operativo (roles, procedimientos, mantenimiento e incidentes) y el plan de implementación y de pruebas verificables.",
        "Evaluar la factibilidad técnica, económica y operativa, comparando la alternativa on-premise con una nube gestionada.",
    ])


def seccion_4(r, rf, rnf):
    r.h1("4. Requerimientos")
    r.h2("4.1 Requerimientos funcionales")
    r.jp("Las funciones principales que debe cumplir la solución se listan en la Tabla 4. Cada requerimiento se vincula con los casos de prueba "
         "de la Sección 11 que permiten verificarlo; la prioridad usa la escala MoSCoW (M = debe, S = debería).")
    r.tabla("Requerimientos funcionales", ["ID", "Requerimiento", "Prior.", "Prueba"],
            rf, [1.3, 11.4, 1.1, 2.6], size=8.5, align_center_cols=(0, 2))
    r.h2("4.2 Requerimientos no funcionales")
    r.jp("Los requerimientos no funcionales se expresan con métricas verificables, de modo que puedan usarse como criterios de aceptación en la "
         "Tercera Unidad.")
    todas = [[f[0], cat, f[1], f[2]] for cat, filas in rnf for f in filas]
    r.tabla("Requerimientos no funcionales", ["ID", "Categoría", "Requerimiento medible", "Prueba"], todas,
            [1.5, 2.3, 10.5, 2.1], size=8.5, align_center_cols=(0,))
    r.h2("4.3 Restricciones")
    r.bullets([
        "Todo el software de la plataforma debe ser de código abierto, sin costos de licenciamiento.",
        "La implementación de la III Unidad se realizará en un laboratorio a escala (una estación con virtualización), conservando la topología lógica.",
        "El clúster no debe exponer directamente a Internet el API (6443), el kubelet (10250), etcd (2379-2380) ni la consola del hipervisor (8006).",
        "Los cambios en la III Unidad deben provenir de este diseño; cualquier componente adicional requerirá justificación técnica documentada.",
    ])
