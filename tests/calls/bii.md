# Чек-лист тестовых звонков: bii (BI Innovations)

Стенд: `vagrant/`. Номера синтетические. Колонка «Этап» — с какого этапа
пункт должен проходить. Отмечайте результат и дату в MR.

## Этап 2 — SBC → Asterisk, приветствие

| № | Действие | Ожидается | Как проверить |
|---|----------|-----------|---------------|
| 2.1 | Софтфон на хосте звонит `70000000001@192.168.56.10` | Слышно приветствие (рус.), затем отбой | на слух; `vagrant ssh pbx-bii-1 -c "sudo grep welcome /var/log/asterisk/messages.log"` |
| 2.2 | То же для `70000000002` и `70000000003` | То же | то же |
| 2.3 | SIPp `uac-call.xml` с ВМ provider | `Successful call: 1`, медиа-адрес 192.168.56.10 | `tests/sipp/README.md` |
| 2.4 | Звонок на `70000000999` | 404 от SBC, Asterisk звонка не видит | SIPp `uac-unknown-did.xml`; на sbc `sudo tcpdump -i any -nn -A udp port 5060` |
| 2.5 | Медиа идёт через rtpengine | В SDP для провайдера — 192.168.56.10, для Asterisk — 192.168.57.10 | `vagrant ssh sbc -c "sudo tcpdump -i any -nn -A -s0 udp port 5060"` → строки `c=IN IP4` в SDP |
| 2.6 | Asterisk виден dispatcher | `pbx-bii-1` активен (FLAGS начинаются с `A`), PRIORITY 10 | `vagrant ssh sbc -c "sudo kamcmd dispatcher.list"` |

Результат на стенде (Windows 11, VirtualBox 7.2, 2026-11-27): 2.1 — пройден
(приветствие слышно в MicroSIP после возврата узла в dispatcher, см. vagrant/README.md).

## Этап 3 — БД, оператор строкой в БД, WSS, очередь

Подготовка: оператор `1001` и очередь `main` добавлены по
`docs/runbooks/add-operator.md` (функции `pbx_add_*`).

| № | Действие | Ожидается | Как проверить |
|---|----------|-----------|---------------|
| 3.1 | Базы на `db` | базы `bii` и `kamailio`; таблицы Asterisk + `pbx_schema_migrations` (0001, 0002) | `sudo -u postgres psql -d bii -c '\dt'` |
| 3.2 | Asterisk видит оператора и очередь из БД | `1001` (realtime) в очереди `main` | `sudo asterisk -rx "queue show main"` на `pbx-bii-1` |
| 3.3 | Браузер: `tests/wss/softphone.html`, регистрация `1001@bii.pbx.test` по WSS | «зарегистрирован» | `sudo kamcmd ul.dump brief` на `sbc`; строка в `kamailio.location` |
| 3.4 | Звонок софтфоном с хоста на `70000000001@192.168.56.10` | приветствие → звонок в браузере → «Ответить» → слышно друг друга | на слух |
| 3.5 | Неверный пароль / чужой домен | регистрация не проходит (401 / 403) | `tests/wss/wss_operator.py` |
| 3.6 | Регистрация снаружи (адрес voice-edge) | 403 | `curl -k https://192.168.57.10:8443/` с адреса 192.168.56.x → 403 |
| 3.7 | CDR и queue_log | строки последнего звонка в `cdr` и `queue_log` (ENTERQUEUE, CONNECT, COMPLETE…) | `sudo -u postgres psql -d bii -c 'select * from queue_log order by id desc limit 5'` |
| 3.8 | Отказ БД при старте SBC | Kamailio стартует (регистрации в памяти), звонки провайдера идут | остановить postgresql на `db`, `sudo systemctl restart kamailio` на `sbc`, в журнале «NO_LOCATION_DB» |

Результаты в контейнере на AlmaLinux 9 (без VirtualBox, 2026-11-28): 3.1–3.8 пройдены
скриптами SIPp, `wss_operator.py` и `webrtc_e2e.js` (headless Chromium: ICE и DTLS
`connected`, RTP в обе стороны).

## Этап 4 — универсальный входящий движок

Дополняется на этапе 4: график и праздники, чёрный список, нерабочее
время → голосовая почта, уведомление о записи, очередь, автопауза, запись.
