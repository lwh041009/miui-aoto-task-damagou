"""
打码狗 Geetest 验证码解算适配器 (修正版)
"""
import requests
import time
import os
from collections import namedtuple
from get_challenge import get_fresh_captcha_challenge
from urllib.parse import quote

from utils.data_model import GeetestResult as DataModelResult
from utils.captcha_solver import CaptchaTask
from utils.config import ConfigManager
from utils.logger import log

# 本地用的 Result（solve_with_damagou 内部用）
_Result = namedtuple('_Result', ['challenge', 'validate'])

def get_damagou_userkey():
    """Read the Damagou user key from env or config."""
    return (
        os.getenv("DAMAGOU_USERKEY")
        or getattr(ConfigManager.data_obj.preference, "damagou_userkey", "")
        or ConfigManager.data_obj.preference.geetest_params.get("userkey")
        or ConfigManager.data_obj.preference.get_geetest_params.get("userkey")
        or ""
    )

def solve_with_damagou(gt, challenge):
    """使用打码狗 API 解验证码"""
    for attempt in range(3):
        try:
            secchua = '"Android WebView";v="125", "Chromium";v="125", "Not.A/Brand";v="24"'
            UserAgent = 'Mozilla/5.0 (Linux; Android 11; redroid11_x86_64 Build/RD2A.211001.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.113 Mobile Safari/537.36XiaoMi/HybridView/ app/vipaccount/dev.260106'
            secchuaplatform = "Android"
            Referer = 'https://web.vip.miui.com/'

            headers_str = f"{quote('sec-ch-ua')}${quote('User-Agent')}${quote('sec-ch-ua-platform')}${quote('Referer')}|{quote(secchua)}${quote(UserAgent)}${quote(secchuaplatform)}${quote(Referer)}"
            url = "http://api.damagou.top/apiv1/jiyanRecognize.html"
            userkey = get_damagou_userkey()
            if not userkey:
                print("未配置打码狗 userkey，请在 data/config.json 或 DAMAGOU_USERKEY 环境变量中填写")
                return _Result(challenge="", validate="")

            params = {"userkey": userkey, "gt": gt, "challenge": challenge, "isJson": "2", "headers": headers_str}
            r = requests.get(url, params=params, timeout=30)
            result = r.json()

            if result.get('status') == '0':
                data = result.get('data', '')
                if '|' in data:
                    parts = data.split('|')
                    new_challenge = parts[0]
                    validate = parts[1]
                    print("打码狗解验证码成功!")
                    return _Result(challenge=new_challenge, validate=validate)
            elif 'not proof' in str(result):
                print("验证码已过期，重试中...")
                return _Result(challenge="", validate="")
            else:
                print(f"打码狗返回: {result}")
            time.sleep(2)
        except Exception as e:
            print(f"打码狗出错: {e}")
            time.sleep(2)

    return _Result(challenge="", validate="")

class DamagouSolver:
    """打码狗解算器 - 注册到 captcha.py SOLVERS"""
    name = "damagou"

    def solve(self, task: CaptchaTask) -> DataModelResult:
        result = solve_with_damagou(task.gt, task.challenge)
        if result.validate:
            log.success("打码狗极验3代解码成功")
            return DataModelResult(challenge=result.challenge, validate=result.validate)
        log.error("打码狗解码失败")
        return DataModelResult(challenge="", validate="")

def get_token_with_damagou(account):
    """完整流程：获取挑战→打码狗解→返回结果与e参数"""
    gt, challenge, e_param = get_fresh_captcha_challenge(account)
    if not gt or not challenge:
        print("无法获取验证码挑战")
        return False

    print(f"获取到验证码 gt={gt[:20]}..., challenge={challenge[:20]}...")

    # 解算验证码
    result = solve_with_damagou(gt, challenge)
    if result.validate:
        return result, challenge, e_param
    else:
        print("重新获取验证码挑战...")
        time.sleep(1)
        gt, challenge, e_param = get_fresh_captcha_challenge(account)
        if gt and challenge:
            result = solve_with_damagou(gt, challenge)
            if result.validate:
                return result, challenge, e_param

    print("打码狗解验证码失败")
    return False

# 本地抓包与过验测试入口
if __name__ == "__main__":
    print("开始进行抓包对齐验证测试...")
    uid = os.getenv("MIUITASK_TEST_CUSERID", "")
    if not uid:
        raise SystemExit("请先设置 MIUITASK_TEST_CUSERID 环境变量")
    res = get_token_with_damagou(uid)
    if res:
        result_obj, raw_challenge, e_param = res
        print(f"✅ 打码狗获取成功! 开始拼装接口数据提交给小米...")

        verify_data = {
            "e": e_param,
            "challenge": raw_challenge,
            "seccode": f"{result_obj.validate}|jordan"
        }

        verify_params = {
            "k": "3dc42a135a8d45118034d1ab68213073",
            "locale": "zh_CN",
            "_t": round(time.time() * 1000),
        }

        headers = {
            'sec-ch-ua': '"Android WebView";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'sec-ch-ua-platform': "Android",
            'user-agent': 'Mozilla/5.0 (Linux; Android 11; redroid11_x86_64 Build/RD2A.211001.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.113 Mobile Safari/537.36XiaoMi/HybridView/ app/vipaccount/dev.260106',
            'content-type': 'application/x-www-form-urlencoded',
            'referer': 'https://web.vip.miui.com/'
        }

        response = requests.post(
            "https://verify.sec.xiaomi.com/captcha/v2/gt/dk/verify",
            params=verify_params,
            headers=headers,
            data=verify_data,
        )
        print(f"小米验证接口返回结果: {response.text}")
    else:
        print("❌ 流程在打码狗阶段就失败了，请检查网络或打码狗余额/KEY")
