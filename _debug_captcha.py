"""调试：查看小米验证码接口返回"""
import time
import sys
sys.path.insert(0, '/root/miui-auto-tasks')
from utils.config import ConfigManager
from utils.request import post as our_post
from utils.utils import get_random_chars_as_string, rsa_encrypt, aes_encrypt
from urllib.parse import parse_qs, urlparse

PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDb3KbHHaBETseIg6fn/H6E9Eo2
Udl7iyPXT0TqE2yC6vxWzGOZBvfaLFr1OSYhi+5PHGz6yYENqM+43n6teBR2hgg0
7m3FY9MFZS6nFkyIGU07SDvpPA/HCmsQirCpV91C0xwPXBUXy/3KIZyHFm8Pz/Rj
nQfmnQhMm32Yy1ndUQIDAQAB
-----END PUBLIC KEY-----"""

ConfigManager.load_config()
account = ConfigManager.data_obj.accounts[0]
cookies = account.cookies
uid = cookies.get("cUserId", "")
print('uid:', repr(uid))

# Build payload
now_ms = round(time.time() * 1000)
payload = {
    "type": 0,
    "startTs": now_ms,
    "endTs": now_ms + 10,
    "env": {**{f"p{i}": "" for i in range(1, 34)}, "p33": []},
    "action": {f"a{i}": [] for i in range(1, 15)},
    "force": False,
    "talkBack": False,
    "uid": uid,
    "nonce": {"t": round(time.time() * 1000), "r": round(time.time() * 1000)},
    "version": "2.0",
    "scene": "GROW_UP_CHECKIN",
}

key = get_random_chars_as_string(16)
params = {
    "k": "3dc42a135a8d45118034d1ab68213073",
    "locale": "zh_CN",
    "_t": round(time.time() * 1000),
}
encrypted = {
    "s": rsa_encrypt(PUBLIC_KEY_PEM, key),
    "d": aes_encrypt(key, str(payload)),
    "a": "GROW_UP_CHECKIN",
}
headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36"}
r = our_post(
    "https://verify.sec.xiaomi.com/captcha/v2/data",
    params=params,
    data=encrypted,
    headers=headers,
)
print('status:', r.status_code)
print('text:', r.text[:1000])
