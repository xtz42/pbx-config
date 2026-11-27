# Changelog

Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версии — по тегам выкатки (формат тегов будет определён на этапе 6).

## [Unreleased]

### Added — этап 2
- `rpm/asterisk.spec` (Asterisk 22.12.0, pjproject 2.17) и `rpm/rtpengine.spec`
  (mr13.5.1.33, userspace, без транскодирования); роль `rpm_package` со сборкой и кэшем.
- Инвентарь `inventory/vagrant/`, `ansible.cfg`, `site.yml`, плейбуки `sbc`, `pbx`, `db`, `sounds`.
- Роли `base`, `tenants`, `rtpengine`, `kamailio` (DID → набор dispatcher тенанта,
  алгоритм 8, failover через `ds_next_dst()`), `asterisk`, `sounds`.
- Заглушка входящего движка: ответ и приветствие тенанта; временные приветствия bii (ru, kk).
- `vagrant/Vagrantfile` (VirtualBox, ansible_local), `vagrant/bootstrap.sh`.
- SIPp: сборка из исходников, сценарии `uac-greeting`, `uac-unknown-did`; чек-лист `tests/calls/bii.md`.
- Документация: `docs/network.md`, `docs/os-setup.md`, `docs/packages.md`, `vagrant/README.md`.

### Added — этап 1
- Скелет репозитория, `.gitignore`, `.gitattributes` (LF, звуки через Git LFS).
- pre-commit: yamllint, ansible-lint, gitleaks, проверка шифрования `*.vault.yml` в test/prod.
- ADR 0001–0003, список плейсхолдеров и открытых вопросов.
- Шаблон описания тенанта и описание пилотного тенанта `bii`.
- README, CODEOWNERS (плейсхолдеры), шаблон MR.
