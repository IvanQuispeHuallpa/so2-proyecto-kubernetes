# Simulación del clúster

La implementación se hace como **simulación ligera**: los nodos son contenedores Docker creados con
[kind](https://kind.sigs.k8s.io/) en lugar de máquinas virtuales, para que corra en cualquier equipo.
El diseño completo (3 hosts Proxmox, 9 VM, VLAN) se mantiene en el documento técnico y en la presentación.

## Equivalencias con el diseño

| Diseño (producción)                 | Simulación                                         |
|-------------------------------------|----------------------------------------------------|
| 3 hosts Proxmox y 9 VM              | Contenedores Docker (kind)                         |
| HAProxy + Keepalived (VIP del API)  | Contenedor HAProxy que kind crea automáticamente   |
| 3 nodos de control con etcd apilado | 3 nodos de control con etcd apilado (igual)        |
| 3 workers                           | 2 workers                                          |
| Cilium sin kube-proxy               | Cilium sin kube-proxy (igual, sin Hubble UI)       |
| MetalLB + Traefik                   | Traefik por NodePort, publicado en `localhost:8080` |
| Longhorn                            | local-path (almacenamiento incluido en kind)       |
| CloudNativePG (1 primario + 2 réplicas) | Igual, con poca memoria por instancia           |
| Prometheus, Grafana, Loki           | Opcional (perfil de monitoreo)                     |
| Velero + MinIO                      | MinIO de una sola instancia                        |

## Perfiles

| Perfil | Archivo             | Nodos              | RAM aproximada |
|--------|---------------------|--------------------|----------------|
| HA     | `kind-cluster.yaml` | 3 control + 2 workers | 3-4 GB      |
| Mínimo | `kind-minimo.yaml`  | 1 control + 1 worker  | 1,5-2 GB    |

## Entorno: máquina virtual Debian

La simulación corre dentro de una VM Debian 12 o 13 (amd64). Recursos sugeridos para la VM:

| Perfil | vCPU | RAM  | Disco |
|--------|------|------|-------|
| HA     | 4    | 6 GB | 30 GB |
| Mínimo | 2    | 4 GB | 20 GB |

## Paso 0: preparar la VM

Dentro de la VM, clonar el repositorio y ejecutar el script de instalación (Docker, kind, kubectl y helm):

```bash
git clone https://github.com/IvanQuispeHuallpa/so2-proyecto-kubernetes.git && cd so2-proyecto-kubernetes
bash simulacion/instalar-debian.sh
```

Luego cerrar sesión y volver a entrar para que el usuario quede en el grupo `docker`, y comprobar con
`docker ps` (sin `sudo`).

## Paso 1: crear el clúster

```bash
kind create cluster --config simulacion/kind-cluster.yaml
kubectl get nodes
```

Los nodos aparecen como `NotReady` hasta instalar Cilium (paso 2): es lo esperado, porque el clúster se
crea sin red de pods.

Para borrarlo: `kind delete cluster --name so2-ha`.
