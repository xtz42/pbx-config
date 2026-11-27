#!/usr/bin/env bash
# Подготовка ВМ стенда к провижинингу ansible_local:
# закреплённая версия ansible-core в /opt/ansible (Python 3.12) и коллекции.
# Запускается Vagrant от root перед ansible_local; повторный запуск безопасен.
set -euo pipefail

ANSIBLE_CORE_VERSION="2.21.6"
REPO="${PBX_REPO:-/vagrant}"
VENV=/opt/ansible
SITE="${VENV}/lib/python3.12/site-packages"

if ! "${VENV}/bin/ansible" --version 2>/dev/null | grep -q "core ${ANSIBLE_CORE_VERSION}"; then
  echo ">>> ansible-core ${ANSIBLE_CORE_VERSION} → ${VENV}"
  dnf -y -q install python3.12 python3.12-pip
  python3.12 -m venv "${VENV}"
  "${VENV}/bin/pip" install -q --upgrade pip
  "${VENV}/bin/pip" install -q "ansible-core==${ANSIBLE_CORE_VERSION}"
fi

# Коллекции — в site-packages окружения: их находит ansible без настроек.
echo ">>> коллекции из ${REPO}/requirements.yml"
ANSIBLE_COLLECTIONS_PATH="${SITE}" "${VENV}/bin/ansible-galaxy" collection install -r "${REPO}/requirements.yml" -p "${SITE}" >/dev/null

for b in "${VENV}"/bin/ansible*; do
  ln -sf "${b}" "/usr/local/bin/$(basename "${b}")"
done
ansible --version | head -1
