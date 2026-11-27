#!/usr/bin/env bash
# Провижининг ВМ стенда изнутри самой ВМ — то же, что делает Vagrant
# (bootstrap.sh + ansible_local), но без Vagrant на хосте:
#   sudo bash /vagrant/vagrant/provision.sh            # имя хоста = имя ВМ
#   sudo bash /vagrant/vagrant/provision.sh pbx-bii-1 -v
# Дополнительные аргументы передаются ansible-playbook.
set -euo pipefail

REPO="${PBX_REPO:-/vagrant}"
HOST="${1:-$(hostname -s)}"
[ "$#" -gt 0 ] && shift

PBX_REPO="${REPO}" bash "${REPO}/vagrant/bootstrap.sh"

cd "${REPO}"
ANSIBLE_CONFIG="${REPO}/ansible.cfg" /opt/ansible/bin/ansible-playbook \
  -i inventory/vagrant/hosts.yml site.yml --limit "${HOST}" "$@"
