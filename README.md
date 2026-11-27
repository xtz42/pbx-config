# pbx-config

Конфигурация АТС колл-центра на свободном ПО — замена Oktell (эпик NET-475).
Kamailio + rtpengine на краю сети, отдельная пара Asterisk 22 LTS на каждого
тенанта, PostgreSQL для оперативных данных. Всё раскатывается Ansible;
тестовый стенд — Vagrant.

> **Только синтетические данные.** В репозитории нет и не должно быть
> реальных номеров, адресов, имён серверов и паролей компании.
> Чего не хватает — плейсхолдер и запись в [`docs/placeholders.md`](docs/placeholders.md).

## Архитектура вкратце

```
 Провайдер (SIP-транк)        Операторы (браузер, WebRTC/WSS)
          │                              │
          ▼            voice-edge        ▼
   ┌──────────────────────────────────────────┐
   │ SBC: Kamailio + rtpengine (общий)         │  пара в ЦОД 1/2, общий BGP-адрес
   │  dispatcher: DID → набор тенанта,         │
   │  алгоритм 8 (приоритет ЦОД 1), OPTIONS    │
   │  регистратор операторов                   │
   └──────────────────────────────────────────┘
          │            voice-core
          ├──────────────┬──────────────┬─── …
          ▼              ▼              ▼
   pbx-bii-1 (ЦОД 1)  pbx-bii-2 (ЦОД 2)  pbx-alm-1/2 …   пара Asterisk на тенанта
          │              │
          └──────┬───────┘
                 ▼
   PostgreSQL (общий кластер, база на тенанта):
   did_routes, графики, праздники, операторы, очереди, CDR, queue_log
```

Решения и их обоснование — в [`docs/decisions/`](docs/decisions/):
[0001](docs/decisions/0001-almalinux-asterisk-kamailio.md) стек,
[0002](docs/decisions/0002-config-in-git-data-in-postgres.md) что в Git, а что в БД,
[0003](docs/decisions/0003-asterisk-pair-per-tenant.md) пара Asterisk на тенанта.

## Тенанты

| Код     | Тенант           | Статус |
|---------|------------------|--------|
| `bii`   | BI Innovations   | пилот  |
| `bi360` | BI Group 360     | —      |
| `bi330` | BI Group 330     | —      |
| `bif`   | BI Finance       | —      |
| `alm`   | Alemica          | этап 7 (проверка «тенант без нового кода») |

Описание тенанта — `tenants/<код>.yml` (шаблон: [`tenants/_template.yml`](tenants/_template.yml)).
Хосты тенанта — в инвентаре, секреты — в `group_vars/all.vault.yml`,
маршруты DID, графики, операторы и очереди — в базе тенанта.

## Структура

| Каталог | Содержимое | Этап |
|---------|-----------|------|
| `playbooks/` | `sbc.yml`, `pbx.yml`, `db.yml`, `sounds.yml`, `check-drift.yml` | 2–4 |
| `inventory/` | `vagrant/` (стенд), `test/`, `prod/` (только заготовки с плейсхолдерами) | 2 |
| `tenants/` | описания тенантов | 1 |
| `roles/` | `kamailio`, `rtpengine`, `asterisk` (одна на всех тенантов), `postgresql`, `sounds`; служебные `base` (ОС стенда), `tenants` (загрузка `tenants/*.yml`), `rpm_package` (сборка RPM) | 2–4 |
| `db/` | `asterisk-alembic/` (таблицы Asterisk 22), `migrations/` (свои таблицы), `seed/` (праздники РК, причины пауз) | 3–4 |
| `sounds/` | `common/{kk,ru}/`, `tenants/<код>/` — через Git LFS | 2, 4 |
| `rpm/` | `asterisk.spec`, `rtpengine.spec` (+ патч, юнит systemd) | 2 |
| `tests/` | `sipp/` сценарии, `calls/` чек-листы тестовых звонков | 2–5 |
| `ci/` | скрипты проверок для pre-commit и GitLab CI | 1, 6 |
| `vagrant/` | `Vagrantfile` стенда | 2 |
| `docs/` | архитектура, чеклисты ОС и пакетов, сеть, соответствие Oktell, runbooks, ADR | по ходу |

## Стенд Vagrant

VirtualBox + Vagrant, Ansible внутри ВМ (`ansible_local`). Подробно — [`vagrant/README.md`](vagrant/README.md).

```bash
cd vagrant && vagrant up
```

Проверка: звонок софтфоном с хоста на `70000000001@192.168.56.10` или SIPp
с ВМ `provider` — чек-лист [`tests/calls/bii.md`](tests/calls/bii.md).

## Подготовка рабочего места

```bash
git lfs install
```

```bash
pip install pre-commit
```

```bash
pre-commit install
```

```bash
pre-commit run --all-files
```

Хуки: yamllint, ansible-lint, gitleaks и проверка, что `*.vault.yml`
в `inventory/test` и `inventory/prod` зашифрованы Ansible Vault.
Для ansible-lint нужен Python ≥ 3.12.

## Секреты

- Прод и test: только Ansible Vault, файлы `*.vault.yml`, переменные с префиксом `vault_`.
- Пароль от Vault в репозиторий не кладётся (`.vault_pass*` в `.gitignore`).
- Vagrant-стенд: открытые одноразовые тестовые пароли в `inventory/vagrant/` допустимы
  (gitleaks настроен их пропускать только в этом каталоге).

## Правила работы

- Коммит: `NET-475: <что сделано>` — одно логическое изменение на коммит.
- Изменения — через MR по шаблону [`docs/templates/merge_request.md`](docs/templates/merge_request.md).
- Новая линия, оператор, очередь = строки в БД, а не новый код.
- Существенное архитектурное решение — ADR в `docs/decisions/`.
- Изменения записываются в [`CHANGELOG.md`](CHANGELOG.md).

## Статус

| Этап | Содержание | Статус |
|------|-----------|--------|
| 1 | Скелет, линтеры, ADR, описание тенанта | готово |
| 2 | Vagrant: sbc + pbx-bii-1, звонок на DID → приветствие | готово |
| 3 | PostgreSQL, миграции, realtime операторов и очередей, CDR/queue_log | готово |
| 4 | Универсальный входящий движок, чек-лист `tests/calls/bii.md` | — |
| 5 | pbx-bii-2, отказ и возврат через dispatcher | — |
| 6 | GitLab CI | — |
| 7 | Второй тенант `alm` без изменения кода движка | — |
