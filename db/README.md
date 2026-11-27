# База данных

Общий кластер PostgreSQL (на стенде — ВМ `db`, 192.168.57.30), в нём:

| База | Владелец | Кто подключается | Что внутри |
|------|----------|------------------|-----------|
| `<код тенанта>` (`bii`, …) | `<код>_owner` (NOLOGIN) | Asterisk тенанта (`<код>_asterisk`), Kamailio только чтение (`kamailio_ro`) | таблицы Asterisk (realtime PJSIP, очереди, CDR, queue_log) + свои таблицы |
| `kamailio` | `kamailio` | Kamailio | регистрации операторов (`location`) |

Доступ ограничен в `pg_hba.conf` парами «база — пользователь — адрес хоста».

## Каталоги

- `asterisk-alembic/` — миграции таблиц Asterisk 22 (копия `contrib/ast-db-manage`, см. `VENDORED.md`);
  применяются деревья `config`, `cdr`, `queue_log`.
- `migrations/` — свои миграции `NNNN_имя.up.sql` / `.down.sql`, применяет `migrate.sh`
  (учёт в `pbx_schema_migrations`).
- `kamailio/` — схема Kamailio из пакета `kamailio-postgresql`.
- `seed/` — справочные данные (праздники РК, причины пауз) — этап 4.
- `requirements.txt` — версии Alembic/SQLAlchemy/psycopg2.

Всё применяет роль `postgresql` (`playbooks/db.yml`).

## Операторы и очереди — строками в БД

```sql
SELECT pbx_add_operator('1001', 'пароль-не-короче-8', 'Фамилия Имя');
SELECT pbx_add_queue_member('main', '1001');
SELECT pbx_remove_operator('1001');
```

Подробно — `docs/runbooks/add-operator.md`.
