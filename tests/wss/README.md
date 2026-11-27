# Проверка операторов по WSS (WebRTC)

| Файл | Что | Где запускать |
|------|-----|---------------|
| `softphone.html` | тестовый софтфон в браузере (JsSIP, офлайн, `vendor/`) | открыть файл в Chrome/Firefox на хосте |
| `wss_operator.py` | регистрация по WSS без браузера, проверка SDP входящего INVITE | на `sbc` или любой машине во внутренней сети, Python 3.9+ |
| `webrtc_e2e.js` | автотест: headless Chromium + звонок SIPp, звук в обе стороны | машина с Node.js и Playwright (CI, этап 6) |

## Софтфон в браузере (стенд)

1. Откройте `https://192.168.57.10:8443/` и примите самоподписанный сертификат
   (страница «pbx-sbc: WSS для операторов»).
2. Откройте `tests/wss/softphone.html` из папки репозитория (двойной щелчок).
3. Введите пароль оператора (`docs/runbooks/add-operator.md`) → «Зарегистрироваться».
4. Позвоните на DID `70000000001@192.168.56.10` софтфоном или SIPp: после
   приветствия звонок придёт в браузер → «Ответить». Разрешите микрофон.

## Без браузера

```bash
python3 /vagrant/tests/wss/wss_operator.py --host 192.168.57.10 --port 8443 --user 1001 --password '<пароль>' --domain bii.pbx.test --wait 30
```

Ожидается `REGISTER → 200 OK`, а при звонке из очереди — `INVITE ... transport=ws`
с `RTP/SAVPF`, ICE и DTLS fingerprint в SDP (WebRTC через rtpengine).
