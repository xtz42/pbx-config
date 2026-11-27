#!/usr/bin/env python3
"""Проверка регистрации оператора по WSS (как браузерный софтфон) без браузера.

Только стандартная библиотека Python 3.9+. Подключается к Kamailio по WSS,
регистрирует оператора (digest из базы тенанта) и, если задан --wait, ждёт
входящий INVITE из очереди: печатает признаки WebRTC в SDP (RTP/SAVPF, ICE,
DTLS fingerprint) и отвечает 486 Busy — разговор без браузера невозможен.

  python3 wss_operator.py --host 192.168.57.10 --port 8443 \\
      --user 1001 --password '...' --domain bii.pbx.test [--wait 30]

Код возврата: 0 — регистрация (и ожидание INVITE, если задано) успешны.
"""
import argparse
import base64
import hashlib
import os
import random
import re
import socket
import ssl
import struct
import sys
import time


def ws_connect(host, port):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # стенд: самоподписанный сертификат
    sock = ctx.wrap_socket(socket.create_connection((host, port), timeout=10), server_hostname=host)
    key = base64.b64encode(os.urandom(16)).decode()
    sock.sendall((
        f"GET / HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
        f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Protocol: sip\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = sock.recv(4096)
        if not chunk:
            break
        resp += chunk
    status = resp.split(b"\r\n", 1)[0].decode(errors="replace")
    if " 101 " not in status:
        raise SystemExit(f"WebSocket: рукопожатие отклонено: {status}")
    return sock


def ws_send(sock, text):
    data = text.encode()
    mask = os.urandom(4)
    header = bytes([0x81])
    n = len(data)
    if n < 126:
        header += bytes([0x80 | n])
    elif n < 65536:
        header += bytes([0x80 | 126]) + struct.pack("!H", n)
    else:
        header += bytes([0x80 | 127]) + struct.pack("!Q", n)
    sock.sendall(header + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def ws_recv(sock, timeout):
    sock.settimeout(timeout)

    def read(n):
        buf = b""
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("соединение закрыто")
            buf += chunk
        return buf

    while True:
        b1, b2 = read(2)
        opcode, n = b1 & 0x0F, b2 & 0x7F
        if n == 126:
            n = struct.unpack("!H", read(2))[0]
        elif n == 127:
            n = struct.unpack("!Q", read(8))[0]
        payload = read(n)
        if opcode == 0x9:  # ping → pong
            sock.sendall(bytes([0x8A, len(payload)]) + payload)
            continue
        if opcode in (0x1, 0x2):
            return payload.decode(errors="replace")
        if opcode == 0x8:
            raise ConnectionError("сервер закрыл WebSocket")


def digest(user, password, realm, nonce, method, uri, qop):
    ha1 = hashlib.md5(f"{user}:{realm}:{password}".encode()).hexdigest()
    ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()
    if qop:
        cnonce, nc = os.urandom(8).hex(), "00000001"
        resp = hashlib.md5(f"{ha1}:{nonce}:{nc}:{cnonce}:auth:{ha2}".encode()).hexdigest()
        return (f'Digest username="{user}", realm="{realm}", nonce="{nonce}", uri="{uri}", '
                f'response="{resp}", algorithm=MD5, qop=auth, nc={nc}, cnonce="{cnonce}"')
    resp = hashlib.md5(f"{ha1}:{nonce}:{ha2}".encode()).hexdigest()
    return (f'Digest username="{user}", realm="{realm}", nonce="{nonce}", uri="{uri}", '
            f'response="{resp}", algorithm=MD5')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", required=True)
    ap.add_argument("--port", type=int, default=8443)
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--wait", type=int, default=0, help="ждать входящий INVITE, секунд")
    a = ap.parse_args()

    sock = ws_connect(a.host, a.port)
    print(f"WSS: соединение с {a.host}:{a.port} установлено (101 Switching Protocols)")

    inst = f"{random.getrandbits(32):08x}.invalid"
    callid, tag, uri = os.urandom(8).hex(), os.urandom(4).hex(), f"sip:{a.domain}"
    auth, cseq = None, 1
    for _ in range(2):
        msg = (f"REGISTER {uri} SIP/2.0\r\n"
               f"Via: SIP/2.0/WSS {inst};branch=z9hG4bK{os.urandom(6).hex()}\r\n"
               f"Max-Forwards: 70\r\nTo: <sip:{a.user}@{a.domain}>\r\n"
               f"From: <sip:{a.user}@{a.domain}>;tag={tag}\r\nCall-ID: {callid}\r\n"
               f"CSeq: {cseq} REGISTER\r\n"
               f"Contact: <sip:{a.user}@{inst};transport=ws>;expires=600\r\n"
               + (f"Authorization: {auth}\r\n" if auth else "")
               + "User-Agent: pbx-config wss_operator.py\r\nContent-Length: 0\r\n\r\n")
        ws_send(sock, msg)
        reply = ws_recv(sock, 10)
        status = reply.split("\r\n", 1)[0]
        print(f"REGISTER (CSeq {cseq}) → {status}")
        if status.startswith("SIP/2.0 200"):
            break
        m = re.search(r"WWW-Authenticate:\s*Digest\s+(.*)", reply, re.I)
        if not status.startswith("SIP/2.0 401") or not m or auth:
            raise SystemExit("регистрация не удалась")
        params = dict(re.findall(r'(\w+)="?([^",]+)"?', m.group(1)))
        auth = digest(a.user, a.password, params["realm"], params["nonce"], "REGISTER", uri, params.get("qop"))
        cseq += 1
    else:
        raise SystemExit("регистрация не удалась")

    if not a.wait:
        return 0

    print(f"Жду входящий INVITE до {a.wait} с ...")
    deadline = time.time() + a.wait
    while time.time() < deadline:
        try:
            msg = ws_recv(sock, max(1, deadline - time.time()))
        except socket.timeout:
            break
        first = msg.split("\r\n", 1)[0]
        if not first.startswith("INVITE "):
            continue
        sdp = msg.split("\r\n\r\n", 1)[1] if "\r\n\r\n" in msg else ""
        print(f"Получен {first}")
        checks = {
            "профиль RTP/SAVPF (SRTP для WebRTC)": "RTP/SAVPF" in sdp,
            "кандидаты ICE": "a=candidate" in sdp,
            "DTLS fingerprint": "a=fingerprint" in sdp,
            "адрес медиа rtpengine": re.search(r"c=IN IP4 (\S+)", sdp).group(1) if "c=IN" in sdp else "-",
        }
        for k, v in checks.items():
            print(f"  {k}: {v}")
        hdrs = {h.split(":", 1)[0].lower(): h for h in msg.split("\r\n\r\n", 1)[0].split("\r\n")[1:] if ":" in h}
        reply = ("SIP/2.0 486 Busy Here\r\n" + "\r\n".join(
            v for k, v in hdrs.items() if k in ("via", "from", "call-id", "cseq"))
            + f"\r\n{hdrs['to']};tag={os.urandom(4).hex()}\r\nContent-Length: 0\r\n\r\n")
        ws_send(sock, reply)
        print("Ответил 486 Busy Here (разговор без браузера невозможен)")
        return 0 if all(v for v in list(checks.values())[:3]) else 2
    print("INVITE не пришёл")
    return 1


if __name__ == "__main__":
    sys.exit(main())
