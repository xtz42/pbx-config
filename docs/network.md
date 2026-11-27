# Сеть

## Сегменты

| Сегмент | Назначение | Стенд Vagrant | Прод |
|---------|-----------|---------------|------|
| voice-edge | провайдер (транк), снаружи SBC | 192.168.56.0/24 | плейсхолдер: публичный BGP-адрес SBC, адреса провайдера |
| voice-core | SBC ↔ Asterisk ↔ PostgreSQL | 192.168.57.0/24 | плейсхолдер |

Операторы — во внутренней сети (удалённые — через VPN): Kamailio принимает
регистрации и WSS только на voice-core и только из `sbc_operator_networks`.

## Адреса стенда

| Хост | voice-edge | voice-core |
|------|-----------|-----------|
| хост (Windows), софтфон | 192.168.56.1 | 192.168.57.1 |
| provider (SIPp) | 192.168.56.5 | — |
| sbc | 192.168.56.10 | 192.168.57.10 |
| pbx-bii-1 | — | 192.168.57.21 |
| pbx-bii-2 (этап 5) | — | 192.168.57.22 |
| db | — | 192.168.57.30 |

## Порты

| Хост | Порт | Зона firewalld | Что |
|------|------|----------------|-----|
| sbc | 5060/udp | voice-edge, voice-core | SIP (Kamailio) |
| sbc | 30000–40000/udp | voice-edge, voice-core | RTP (rtpengine) |
| sbc | 127.0.0.1:2223/udp | — | ng-протокол Kamailio ↔ rtpengine |
| sbc | 8443/tcp | voice-core | WSS операторов (и HTTPS для принятия сертификата) |
| pbx-* | 5060/udp | voice-core | SIP (Asterisk ← SBC) |
| pbx-* | 10000–20000/udp | voice-core | RTP Asterisk |
| db | 5432/tcp | voice-core | PostgreSQL (доступ — по парам база/пользователь/адрес в pg_hba) |

Зоны firewalld `voice-edge` / `voice-core` привязаны к подсетям-источникам
(роль `base`, переменные `net_voice_edge` / `net_voice_core`), порты в них
открывают роли сервисов.

## Поток звонка от провайдера

```
провайдер ──INVITE──► sbc:edge (Kamailio)
                       │ permissions: источник в группе 1 (провайдеры)?  нет → 403
                       │ DID → тенант (tenants.cfg)                       нет → 404
                       │ dispatcher: набор тенанта, алгоритм 8 (ЦОД 1)    нет узлов → 503
                       │ rtpengine offer: edge → core
                       ▼
                     sbc:core ──INVITE──► pbx-<тенант>-1 (Asterisk, контекст from-sbc)
                       ◄──200 OK── rtpengine answer: core → edge
                     нет ответа за 2 с / 5xx → ds_mark_dst + ds_next_dst()
```

## Поток звонка оператору

```
Asterisk тенанта ──INVITE sip:1001@sbc──► sbc:core (Kamailio)
                    │ адрес Asterisk → домен тенанта (bii.pbx.test): чужих операторов не видно
                    │ lookup(location) по 1001@bii.pbx.test         нет регистрации → 480
                    │ WebSocket? rtpengine: RTP ↔ DTLS-SRTP + ICE (оба плеча на core)
                    ▼
                  браузер оператора (WSS :8443)  или  SIP-телефон (UDP :5060)
```

Регистрация оператора: REGISTER на домен тенанта → пароль из представления
`sip_operator_auth` базы тенанта (только чтение) → `location` в базе `kamailio`.

DSCP: сигнализация CS3 (Asterisk `tos = cs3`), медиа EF (rtpengine `tos = 184`).
