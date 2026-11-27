# Чек-лист тестовых звонков: bii (BI Innovations)

Стенд: `vagrant/`. Номера синтетические. Колонка «Этап» — с какого этапа
пункт должен проходить. Отмечайте результат и дату в MR.

## Этап 2 — SBC → Asterisk, приветствие

| № | Действие | Ожидается | Как проверить |
|---|----------|-----------|---------------|
| 2.1 | Софтфон на хосте звонит `70000000001@192.168.56.10` | Слышно приветствие (рус.), затем отбой | на слух; `vagrant ssh pbx-bii-1 -c "sudo grep welcome /var/log/asterisk/messages.log"` |
| 2.2 | То же для `70000000002` и `70000000003` | То же | то же |
| 2.3 | SIPp `uac-greeting.xml` с ВМ provider | `Successful call: 1`, медиа-адрес 192.168.56.10 | `tests/sipp/README.md` |
| 2.4 | Звонок на `70000000999` | 404 от SBC, Asterisk звонка не видит | SIPp `uac-unknown-did.xml`; на sbc `sudo tcpdump -i any -nn -A udp port 5060` |
| 2.5 | Медиа идёт через rtpengine | В SDP для провайдера — 192.168.56.10, для Asterisk — 192.168.57.10 | `vagrant ssh sbc -c "sudo tcpdump -i any -nn -A -s0 udp port 5060"` → строки `c=IN IP4` в SDP |
| 2.6 | Asterisk виден dispatcher | `pbx-bii-1` активен (FLAGS начинаются с `A`), PRIORITY 10 | `vagrant ssh sbc -c "sudo kamcmd dispatcher.list"` |

## Этап 4 — универсальный входящий движок

Дополняется на этапе 4: график и праздники, чёрный список, нерабочее
время → голосовая почта, уведомление о записи, очередь, автопауза, запись.
