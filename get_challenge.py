import json
import time
import base64
import os
import random
import string
from urllib.parse import urlparse, parse_qsl
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
import requests


PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArxfNLkuAQ/BYHzkzVwtu
g+0abmYRBVCEScSzGxJIOsfxVzcuqaKO87H2o2wBcacD3bRHhMjTkhSEqxPjQ/FE
XuJ1cdbmr3+b3EQR6wf/cYcMx2468/QyVoQ7BADLSPecQhtgGOllkC+cLYN6Md34
Uii6U+VJf0p0q/saxUTZvhR2ka9fqJ4+6C6cOghIecjMYQNHIaNW+eSKunfFsXVU
+QfMD0q2EM9wo20aLnos24yDzRjh9HJc6xfr37jRlv1/boG/EABMG9FnTm35xWrV
R0nw3cpYF7GZg13QicS/ZwEsSd4HyboAruMxJBPvK3Jdr4ZS23bpN0cavWOJsBqZ
VwIDAQAB
-----END PUBLIC KEY-----"""

headers = {
    "Accept": "*/*",
    "Content-type": "application/x-www-form-urlencoded",
    "Origin": "https://web.vip.miui.com",
    "Referer": "https://web.vip.miui.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}
def get_random_chars_as_string(length, chars=None):
    if chars is None:
        chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(length))
def aes_encrypt(key, data):
    iv = "0102030405060708".encode("utf-8")
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv)
    padded_data = pad(data.encode("utf-8"), AES.block_size, style="pkcs7")
    return base64.b64encode(cipher.encrypt(padded_data)).decode("utf-8")
def rsa_encrypt(key, data):
    public_key = RSA.import_key(key)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(base64.b64encode(data.encode("utf-8")))
    return base64.b64encode(ciphertext).decode("utf-8")

def get_fresh_captcha_challenge(uid):
    """
    向小米验证服务器发送type=0请求，从返回的验证码URL中提取
    gt(c参数) 和 challenge(l参数)
    返回: (gt, challenge, e_param) 或 (None, None, None)
    """
    ts = round(time.time() * 1000)

    data_payload = {
        "type": 0,
        "startTs": ts,
        "endTs": ts,
        "env": {**{f"p{i}": "" for i in range(1, 35) if i not in (27, 33)}, "p27": "", "p33": []},
        "action": {f"a{i}": [] for i in range(1, 15)},
        "force": False,
        "talkBack": False,
        "uid": uid,
        "nonce": {"t": round(time.time()), "r": round(time.time())},
        "version": "2.0",
        "scene": "GROW_UP_CHECKIN",
    }

    key = get_random_chars_as_string(16)
    params = {
        "k": "3dc42a135a8d45118034d1ab68213073",
        "locale": "zh_CN",
        "_t": ts,
    }
    encrypted = {
        "s": rsa_encrypt(PUBLIC_KEY_PEM,key),
        "d": aes_encrypt(key, str(data_payload)),
        "a": "GROW_UP_CHECKIN",
    }
    url = "https://verify.sec.xiaomi.com/captcha/v2/data"
    r = requests.post(url, params=params, headers=headers, data=encrypted, timeout=15)
    result = r.json()

    if result.get("data", {}).get("result") == False:
        verify_url = result["data"].get("url", "")
        if verify_url:
            q = dict(parse_qsl(urlparse(verify_url).query))
            gt = q.get("c", "")
            challenge = q.get("l", "")
            e_param = q.get("e", "")
            return gt, challenge, e_param

    return None, None, None
if __name__ == "__main__":
    uid = os.getenv("MIUITASK_TEST_CUSERID", "")
    if not uid:
        raise SystemExit("请先设置 MIUITASK_TEST_CUSERID 环境变量")
    gt, challenge, e_param = get_fresh_captcha_challenge(uid)
    print(f"gt: {gt}")
    print(f"challenge: {challenge}")
    print(f"e_param: {e_param}")
