# Схема БД Kamailio

Файлы скопированы без изменений из пакета `kamailio-postgresql` 6.1.5
(`/usr/share/kamailio/postgres/`). Применяются ролью `postgresql` к базе
`kamailio` один раз (если нет таблицы `version`).

| Файл | Таблицы |
|------|---------|
| `standard-create.sql` | `version` |
| `usrloc-create.sql` | `location`, `location_attrs` — регистрации операторов |

При обновлении Kamailio: сравнить с новым пакетом; изменения схемы
переносить отдельными миграциями.
