# Сценарии SIPp

SIPp собирается из исходников (`install-sipp.sh`, v3.7.9) на ВМ `provider`
(192.168.56.5 — разрешённый «провайдер» в `inventory/vagrant`).

```bash
vagrant up provider
vagrant ssh provider
```

Внутри ВМ `provider`:

```bash
cd /vagrant/tests/sipp
```

```bash
sipp 192.168.56.10:5060 -sf uac-greeting.xml -s 70000000001 -i 192.168.56.5 -mi 192.168.56.5 -m 1 -trace_logs
```

```bash
sipp 192.168.56.10:5060 -sf uac-unknown-did.xml -s 70000000999 -i 192.168.56.5 -m 1
```

| Сценарий | Ожидается |
|----------|-----------|
| `uac-greeting.xml` | 200 OK, ~7 с приветствия, BYE от Asterisk; `Successful call: 1`. В `uac-greeting_*_logs.log` адрес медиа — **192.168.56.10** (rtpengine edge), не адрес Asterisk |
| `uac-unknown-did.xml` | 404 от SBC; `Successful call: 1` |

Код возврата SIPp: 0 — все вызовы успешны.
