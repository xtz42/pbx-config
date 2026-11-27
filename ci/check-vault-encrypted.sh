#!/usr/bin/env bash
# Проверяет, что файлы *.vault.yml инвентарей test и prod зашифрованы Ansible Vault.
# Вызывается из pre-commit (список файлов в аргументах) и из CI (без аргументов).
set -euo pipefail

if [ "$#" -eq 0 ]; then
  mapfile -t files < <(git ls-files 'inventory/test/*.vault.yml' 'inventory/prod/*.vault.yml' \
                                    'inventory/test/**/*.vault.yml' 'inventory/prod/**/*.vault.yml' | sort -u)
else
  files=("$@")
fi

rc=0
for f in "${files[@]}"; do
  [ -f "$f" ] || continue
  if ! head -n1 "$f" | grep -q '^\$ANSIBLE_VAULT;'; then
    echo "НЕ ЗАШИФРОВАН: $f  (ansible-vault encrypt $f)" >&2
    rc=1
  fi
done
exit "$rc"
