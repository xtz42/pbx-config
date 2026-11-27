# Сеть

## Сегменты

| Сегмент | Назначение | Стенд Vagrant | Прод |
|---------|-----------|---------------|------|
| voice-edge | провайдер (транк), снаружи SBC | 192.168.56.0/24 | плейсхолдер: публичный BGP-адрес SBC, адреса провайдера |
| voice-core | SBC ↔ Asterisk ↔ PostgreSQL | 192.168.57.0/24 | плейсхолдер |

Где регистрируются операторы (WebRTC/WSS) — какой сегмент и адрес
слушает Kamailio для WSS — решается на этапе 3 (`docs/placeholders.md`).

## Адреса стенда

| Хост | voice-edge | voice-core |
|------|-----------|-----------|
| хост (Windows), софтфон | 192.168.56.1 | 192.168.57.1 |
| provider (SIPp) | 192.168.56.5 | — |
| sbc | 192.168.56.10 | 192.168.57.10 |
| pbx-bii-1 | — | 192.168.57.21 |
| pbx-bii-2 (этап 5) | — | 192.168.57.22 |
| db (этап 3) | — | 192.168.57.30 |

## Порты

| Хост | Порт | Зона firewalld | Что |
|------|------|----------------|-----|
| sbc | 5060/udp | voice-edge, voice-core | SIP (Kamailio) |
| sbc | 30000–40000/udp | voice-edge, voice-core | RTP (rtpengine) |
| sbc | 127.0.0.1:2223/udp | — | ng-протокол Kamailio ↔ rtpengine |
| pbx-* | 5060/udp | voice-core | SIP (Asterisk ← SBC) |
| pbx-* | 10000–20000/udp | voice-core | RTP Asterisk |

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

DSCP: сигнализация CS3 (Asterisk `tos = cs3`), медиа EF (rtpengine `tos = 184`).
