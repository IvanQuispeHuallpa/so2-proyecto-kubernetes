#!/usr/bin/env bash
# Prepara una máquina virtual Debian (12 o 13, amd64) para la simulación:
# Docker, kind, kubectl y helm, más los límites del kernel que kind necesita con varios nodos.
#
#   bash simulacion/instalar-debian.sh
#
# Al terminar, cerrar sesión y volver a entrar para usar docker sin sudo.
set -euo pipefail

KIND_VERSION="v0.29.0"

echo "== 1. Paquetes base y Docker"
sudo apt-get update
sudo apt-get install -y ca-certificates curl git docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"

echo "== 2. Límites de inotify (sin esto, los nodos de kind fallan con 'too many open files')"
cat <<EOF | sudo tee /etc/sysctl.d/99-kind.conf
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 512
EOF
sudo sysctl --system > /dev/null

echo "== 3. kind ${KIND_VERSION}"
curl -fsSLo /tmp/kind "https://kind.sigs.k8s.io/dl/${KIND_VERSION}/kind-linux-amd64"
sudo install -m 0755 /tmp/kind /usr/local/bin/kind

echo "== 4. kubectl (última versión estable)"
KUBECTL_VERSION="$(curl -fsSL https://dl.k8s.io/release/stable.txt)"
curl -fsSLo /tmp/kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
sudo install -m 0755 /tmp/kubectl /usr/local/bin/kubectl

echo "== 5. helm"
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo
echo "Listo. Versiones instaladas:"
docker --version
kind version
kubectl version --client
helm version --short
echo
echo "Cierra sesión y vuelve a entrar (grupo docker) antes de crear el clúster."
