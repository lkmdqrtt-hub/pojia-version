#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 version.json 的 Ed25519 签名。CI 和本地都能跑。

    python tools/verify_version.py [path/to/version.json]

退出码 0 = 签名有效，1 = 无效或字段缺失。
"""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

# 客户端硬编码的公钥，改动会破坏所有已发布客户端的验签
PUBKEY = bytes.fromhex("f555a4bd832b57b3a9e3d2586b6125b4bfeaa1d054a210b71c60fde20aa1ead6")

p = 2 ** 255 - 19
L = 2 ** 252 + 27742317777372353535851937790883648493
d = -121665 * pow(121666, p - 2, p) % p
I = pow(2, (p - 1) // 4, p)


def _inv(x: int) -> int:
    return pow(x, p - 2, p)


def _add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % p
    B = (P[1] + P[0]) * (Q[1] + Q[0]) % p
    C = 2 * P[3] * Q[3] * d % p
    D = 2 * P[2] * Q[2] % p
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F % p, G * H % p, F * G % p, E * H % p)


def _mul(s: int, P):
    Q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            Q = _add(Q, P)
        P = _add(P, P)
        s >>= 1
    return Q


def _eq(P, Q) -> bool:
    return ((P[0] * Q[2] - Q[0] * P[2]) % p == 0
            and (P[1] * Q[2] - Q[1] * P[2]) % p == 0)


def _rec_x(y: int, sign: int) -> int:
    x2 = (y * y - 1) * _inv(d * y * y + 1) % p
    if x2 == 0:
        if sign:
            raise ValueError("invalid point")
        return 0
    x = pow(x2, (p + 3) // 8, p)
    if (x * x - x2) % p:
        x = x * I % p
    if (x * x - x2) % p:
        raise ValueError("invalid point")
    if (x & 1) != sign:
        x = p - x
    return x


_By = 4 * _inv(5) % p
_Bx = _rec_x(_By, 0)
B = (_Bx, _By, 1, _Bx * _By % p)


def _dec(s: bytes):
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _rec_x(y, sign)
    return (x, y, 1, x * y % p)


def _hint(m: bytes) -> int:
    return int.from_bytes(hashlib.sha512(m).digest(), "little") % L


def verify(pub: bytes, msg: bytes, sig: bytes) -> bool:
    if len(pub) != 32 or len(sig) != 64:
        return False
    try:
        A = _dec(pub)
        R = _dec(sig[:32])
    except ValueError:
        return False
    S = int.from_bytes(sig[32:], "little")
    if S >= L:
        return False
    k = _hint(sig[:32] + pub + msg)
    return _eq(_mul(S, B), _add(R, _mul(k, A)))


def canonical(doc: dict) -> bytes:
    body = {k: v for k, v in doc.items() if k != "sig"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def main(argv) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("version.json")
    if not path.exists():
        print("找不到", path)
        return 1
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print("JSON 解析失败:", e)
        return 1

    sig_b64 = doc.get("sig", "")
    if not sig_b64:
        print("缺少 sig 字段")
        return 1
    try:
        sig = base64.b64decode(sig_b64)
    except Exception:
        print("sig 不是合法 base64")
        return 1

    if not verify(PUBKEY, canonical(doc), sig):
        print("签名无效。不要手改 version.json，用 repo-tools/build_version.py 重新生成。")
        return 1

    for k in ("schema", "issued", "latest_version", "persona"):
        if k not in doc:
            print("缺少字段", k)
            return 1
    sha = (doc.get("persona") or {}).get("sha256", "")
    if len(sha) != 64:
        print("persona.sha256 不是 64 位十六进制")
        return 1

    print("OK  issued=%s  latest=%s  persona=%s..." %
          (doc["issued"], doc["latest_version"], sha[:16]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
