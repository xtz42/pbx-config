# Пакеты

## Базовые (все серверы)

`chrony firewalld policycoreutils-python-utils tar bzip2 rsync tcpdump bind-utils git`
(`sngrep` в EPEL 9 нет; SIP смотрим `tcpdump -i any -nn -A -s0 udp port 5060`).

## SBC

| Пакет | Откуда | Версия |
|-------|--------|--------|
| kamailio, kamailio-utils, kamailio-tls, kamailio-websocket, kamailio-postgresql | rpm.kamailio.org, репозиторий конкретного выпуска | 6.1.5 |
| ngcp-rtpengine | **собственный RPM** `rpm/rtpengine.spec` (тег mr13.5.1.33, без транскодирования и модуля ядра) | 13.5.1.33-1.pbx |

## АТС (Asterisk)

| Пакет | Откуда | Версия |
|-------|--------|--------|
| asterisk | **собственный RPM** `rpm/asterisk.spec` (pjproject 2.17 встроенный) | 22.12.0-1.pbx |

Зависимости собственных RPM — из BaseOS/AppStream, CRB и EPEL
(для rtpengine: libwebsockets, hiredis, mosquitto, libjwt, pandoc при сборке).

Дополнительно на АТС: `unixODBC`, `postgresql-odbc` (AppStream).

## PostgreSQL

| Пакет | Откуда | Версия |
|-------|--------|--------|
| `@postgresql:18/server`, postgresql-contrib | AppStream (модуль) | 18 |
| python3-psycopg2 | AppStream | для модулей Ansible community.postgresql |
| Alembic, SQLAlchemy, psycopg2-binary | PyPI, окружение `/opt/pbx-db-migrate` | `db/requirements.txt` |

## Сборка собственных RPM

Стенд: роль `rpm_package` (вызывается ролями `asterisk` и `rtpengine`)
собирает пакет по spec, если его нет в кэше (`vagrant/cache/rpms/`):
исходники проверяются по sha256 (Asterisk, pjproject) или по коммиту тега (rtpengine).

Прод (`rpm_source: repo`): пакеты ставятся из внутреннего репозитория dnf —
**плейсхолдер**, репозиторий и процесс публикации пакетов будут определены
вместе с CI (этап 6).
