# Changelog

Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версии — по тегам выкатки (формат тегов будет определён на этапе 6).

## [Unreleased]

### Added — этап 3
- ВМ `db` (PostgreSQL 18), роль `postgresql`: база на тенанта с ролями `<код>_owner`/`<код>_asterisk`,
  база `kamailio`, изоляция в `pg_hba.conf` по парам база/пользователь/адрес.
- Миграции: Alembic Asterisk 22 (`db/asterisk-alembic`, вендор), свои `db/migrations` (0001 операторы,
  0002 очереди) и `db/migrate.sh`; функции `pbx_add_operator`, `pbx_add_queue`, `pbx_add_queue_member`.
- Asterisk: ODBC realtime для PJSIP-операторов и очередей, CDR (cdr_adaptive_odbc) и queue_log в БД;
  в заглушке движка — очередь `main`; лишние модули отключены.
- Kamailio: регистратор операторов (UDP и WSS :8443 во внутренней сети), пароли из базы тенанта
  (заменяемый блок под SSO/AD), регистрации в БД; звонки Asterisk → оператор с изоляцией по тенанту;
  WebRTC через rtpengine; старт без БД (регистрации в памяти).
- Тесты: SIPp (регистрация, оператор, звонок со звуком), `tests/wss` (софтфон JsSIP, WSS-клиент,
  e2e WebRTC на Playwright); runbook `docs/runbooks/add-operator.md`; чек-лист этапа 3.

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
