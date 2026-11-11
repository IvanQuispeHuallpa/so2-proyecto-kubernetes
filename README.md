# Plataforma Kubernetes de Alta Disponibilidad

Proyecto del curso **Sistemas Operativos II** (Universidad Privada de Tacna, EPIS). Plataforma de orquestación de contenedores con
Kubernetes de alta disponibilidad, sobre 3 hosts Proxmox VE:

- **Plano de control:** 3 nodos con etcd apilado, detrás de HAProxy + Keepalived (VIP del API `10.10.20.10`).
- **Cómputo:** 3 nodos de trabajo; Cilium (CNI y políticas), MetalLB + Traefik, Longhorn y CloudNativePG.
- **Operación:** Prometheus, Grafana y Loki; respaldo con Velero y MinIO; automatización con Ansible.
- **Seguridad:** RBAC, Pod Security Admission, NetworkPolicy, cifrado de Secrets y escaneo de imágenes.

Metas de diseño: disponibilidad ≥ 99,9 %, RPO ≤ 5 min y RTO ≤ 30 min.

## Estructura

```
.
├── infra/                 Configuración de los servicios que rodean al clúster
│   ├── haproxy/             Balanceador del API (lb01 y lb02)
│   └── keepalived/          VIP del API
├── kubernetes/            Manifiestos y configuración del clúster
│   ├── kubeadm/             Inicialización del plano de control
│   └── seguridad/           NetworkPolicy y Pod Security Admission
├── simulacion/            Laboratorio ligero con kind (contenedores Docker en lugar de VM)
└── docs/
    ├── diagramas/         Arquitectura, red, seguridad, despliegue, flujos, cronograma y costos (PNG)
    └── presentacion/      Presentación del proyecto (index.html: abrir en el navegador; fuente/: diapositivas originales)
```

El código de la implementación (Ansible, Vagrant, Helm, etc.) se irá agregando en estas carpetas durante la III Unidad.

## Estado

- **II Unidad (diseño):** completada. El documento técnico se mantiene fuera del repositorio; la presentación está en `docs/presentacion/`.
- **III Unidad (implementación):** en curso; los archivos de `infra/` y `kubernetes/` son el punto de partida tomado del diseño
  (direccionamiento: VLAN 20 para el plano de control, pods `10.244.0.0/16`, servicios `10.96.0.0/12`).

## Notas

- Los valores marcados como `CAMBIAR_SECRETO` o `v1.XX.X` deben completarse antes de usar los archivos; los secretos no se guardan en el repositorio.
- Los costos del diseño son estimaciones referenciales del equipo.
