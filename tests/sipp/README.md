# Сценарии SIPp

SIPp собирается из исходников (`install-sipp.sh`, v3.7.9) на ВМ `provider`
(192.168.56.5 — разрешённый «провайдер» в `inventory/vagrant`).

| Сценарий | Кто | Ожидается |
|----------|-----|-----------|
| `uac-call.xml` | провайдер → DID, держит линию `-d` мс и кладёт трубку | `Successful call: 1`; в `-trace_logs` адрес медиа 192.168.56.10 (rtpengine edge) |
| `uac-call-audio.xml` | то же, со звуком G.711 из pcap (через 9 с после ответа) | двусторонний звук с оператором |
| `uac-unknown-did.xml` | провайдер → чужой DID | 404 от SBC |
| `uac-register.xml` | оператор регистрируется (UDP) с паролем из БД | 401 → 200 OK |
| `uas-operator.xml` | оператор принимает звонок из очереди | 180/200, ждёт BYE |

Код возврата SIPp: 0 — все вызовы успешны.

## Этап 2 — звонок на DID (ВМ provider)

```bash
cd /vagrant/tests/sipp && sipp 192.168.56.10:5060 -sf uac-call.xml -s 70000000001 -d 10000 -i 192.168.56.5 -mi 192.168.56.5 -m 1 -trace_logs
```

## Этап 3 — оператор получает звонок из очереди

SIPp-оператор работает во внутренней сети. На стенде удобно запустить его на
ВМ `pbx-bii-1` или `sbc` (адреса 192.168.57.x входят в сеть операторов);
в примере — на `sbc` (`sudo bash /vagrant/tests/sipp/install-sipp.sh` один раз).

1. Регистрация оператора 1001 (на `sbc`):

```bash
cd /vagrant/tests/sipp && sipp 192.168.57.10:5060 -sf uac-register.xml -s 1001 -au 1001 -ap '<пароль>' -key domain bii.pbx.test -i 192.168.57.10 -p 5090 -m 1
```

2. Оператор ждёт звонок (на `sbc`, тот же порт):

```bash
cd /vagrant/tests/sipp && sipp -sf uas-operator.xml -i 192.168.57.10 -p 5090 -mi 192.168.57.10 -mp 7000 -m 1
```

3. Звонок провайдера (на `provider`):

```bash
cd /vagrant/tests/sipp && sipp 192.168.56.10:5060 -sf uac-call.xml -s 70000000001 -d 15000 -i 192.168.56.5 -mi 192.168.56.5 -m 1
```

Оба SIPp должны завершиться с `Successful call: 1`.
