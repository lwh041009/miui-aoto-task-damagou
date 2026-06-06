"""配置文件"""

import json
import os
import platform
from hashlib import md5
from pathlib import Path
from typing import Literal, Optional, Union

import yaml # pylint: disable=wrong-import-order

from .logger import log

ROOT_PATH = Path(__file__).parent.parent.absolute()

DATA_PATH = ROOT_PATH / "data"
"""数据保存目录"""

CONFIG_TYPE = "json" if os.path.isfile(DATA_PATH / "config.json") else "yaml"
"""数据文件类型"""

CONFIG_PATH = (
    DATA_PATH / f"config.{CONFIG_TYPE}"
    if os.getenv("MIUITASK_CONFIG_PATH") is None
    else Path(str(os.getenv("MIUITASK_CONFIG_PATH")))
)
"""数据文件默认路径"""

os.makedirs(DATA_PATH, exist_ok=True)


def md5_crypto(passwd: str) -> str:
    """MD5加密"""
    return md5(passwd.encode("utf8")).hexdigest().upper()


def cookies_to_dict(cookies: str):
    """将cookies字符串转换为字典"""
    cookies_dict = {}
    if not cookies or "=" not in cookies:
        return cookies_dict
    for cookie in cookies.split(";"):
        key, value = cookie.strip().split("=", 1) # 分割键和值
        cookies_dict[key] = value
    return cookies_dict


def get_platform() -> str:
    """获取当前运行平台"""
    if os.path.exists("/.dockerenv"):
        if os.environ.get("QL_DIR") and os.environ.get("QL_BRANCH"):
            return "qinglong"
        else:
            return "docker"
    return platform.system().lower()


# pylint: disable=too-many-instance-attributes
class Account:
    """账号处理器"""

    # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals
    def __init__(
        self,
        uid="100000",
        password="",
        cookies=None,
        login_user_agent="",
        deviceId="",
        pass_ua="web",
        uLocale="zh_CN",
        user_agent="Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Safari/537.36",
        device="",
        device_model="",
        CheckIn=False,
        BrowseUserPage=False,
        BrowsePost=False,
        BrowseVideoPost=False,
        ThumbUp=False,
        BrowseSpecialPage=False,
        BoardFollow=False,
        CarrotPull=False,
        WxSign=False,
    ):
        self.uid = uid
        self.password = self._password(password)
        self.cookies = self._cookies(cookies) or {}
        self.login_user_agent = login_user_agent
        self.deviceId = deviceId
        self.pass_ua = pass_ua
        self.uLocale = uLocale
        self.user_agent = user_agent
        self.device = device
        self.device_model = device_model
        self.CheckIn = CheckIn
        self.BrowseUserPage = BrowseUserPage
        self.BrowsePost = BrowsePost
        self.BrowseVideoPost = BrowseVideoPost
        self.ThumbUp = ThumbUp
        self.BrowseSpecialPage = BrowseSpecialPage
        self.BoardFollow = BoardFollow
        self.CarrotPull = CarrotPull
        self.WxSign = WxSign

    def _password(self, password: str):
        if len(password) == 32:
            return password
        return md5_crypto(password)

    def _cookies(self, cookies: Union[dict, str]):
        if isinstance(cookies, str):
            return cookies_to_dict(cookies)
        return cookies


class OnePush:
    """推送配置"""

    def __init__(self, notifier="", params=None):
        self.notifier = notifier
        self.params = params or {
            "title": "",
            "markdown": False,
            "token": "",
            "userid": "",
        }


class Preference:
    def __init__(
        self,
        geetest_url="",
        geetest_method: Literal["post", "get"] = "post",
        geetest_params: Optional[dict] = None,
        geetest_data: Optional[dict] = None,
        geetest_validate_path="$.data.validate",
        geetest_challenge_path="$.data.challenge",
        geetest_result_path="$",
        geetest_lot_number_path="$.data.lot_number",
        geetest_pass_token_path="$.data.pass_token",
        geetest_gen_time_path="$.data.gen_time",
        geetest_captcha_output_path="$.data.captcha_output",
        get_geetest_url="",
        get_geetest_method: Literal["post", "get"] = "post",
        get_geetest_params: Optional[dict] = None,
        get_geetest_data: Optional[dict] = None,
        get_geetest_validate_path="$",
        get_geetest_challenge_path="$",
        get_geetest_result_path="$",
        get_geetest_lot_number_path="$.data.lot_number",
        get_geetest_pass_token_path="$.data.pass_token",
        get_geetest_gen_time_path="$.data.gen_time",
        get_geetest_captcha_output_path="$.data.captcha_output",
        get_geetest_try_count=20,
    ):
        self.geetest_url = geetest_url
        self.geetest_method = geetest_method
        self.geetest_params = geetest_params or {}
        self.geetest_data = geetest_data or {}
        self.geetest_validate_path = geetest_validate_path
        self.geetest_challenge_path = geetest_challenge_path
        self.geetest_result_path = geetest_result_path
        self.geetest_lot_number_path = geetest_lot_number_path
        self.geetest_pass_token_path = geetest_pass_token_path
        self.geetest_gen_time_path = geetest_gen_time_path
        self.geetest_captcha_output_path = geetest_captcha_output_path
        self.get_geetest_url = get_geetest_url
        self.get_geetest_method = get_geetest_method
        self.get_geetest_params = get_geetest_params or {}
        self.get_geetest_data = get_geetest_data or {}
        self.get_geetest_validate_path = get_geetest_validate_path
        self.get_geetest_challenge_path = get_geetest_challenge_path
        self.get_geetest_result_path = get_geetest_result_path
        self.get_geetest_lot_number_path = get_geetest_lot_number_path
        self.get_geetest_pass_token_path = get_geetest_pass_token_path
        self.get_geetest_gen_time_path = get_geetest_gen_time_path
        self.get_geetest_captcha_output_path = get_geetest_captcha_output_path
        self.get_geetest_try_count = get_geetest_try_count


class Config:
    def __init__(self, preference=None, accounts=None, onepush=None):
        self.preference = preference or Preference()
        self.accounts = accounts or [Account()]
        self.ONEPUSH = onepush or OnePush()

    def to_dict(self):
        return {
            "preference": vars(self.preference),
            "accounts": [vars(account) for account in self.accounts],
            "ONEPUSH": vars(self.ONEPUSH),
        }

    @classmethod
    def from_dict(cls, data):
        preference = Preference(**data.get("preference", {}))
        accounts = [Account(**account) for account in data.get("accounts", [])]
        onepush = OnePush(**data.get("ONEPUSH", {}))
        return cls(preference, accounts, onepush)


class ConfigManager:
    data_obj = Config()
    platform = "platform_example"

    @classmethod
    def load_config(cls):
        if os.path.exists(CONFIG_PATH) and os.path.isfile(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                    if CONFIG_TYPE == "json":
                        data = json.load(file)
                    else:
                        data = yaml.safe_load(file)
                    cls.data_obj = Config.from_dict(data)
                    cls.write_plugin_data(cls.data_obj)
            except Exception as e:
                log.exception(f"读取数据文件失败，请检查文件格式或权限: {e}")
                raise
        else:
            try:
                if not os.path.exists(DATA_PATH):
                    os.mkdir(DATA_PATH)
                cls.write_plugin_data(cls.data_obj)
            except Exception as e:
                log.exception(f"创建数据文件失败，请检查权限: {e}")
                raise
            log.info(f"数据文件 {CONFIG_PATH} 不存在，已创建默认数据文件。")

    @classmethod
    def write_plugin_data(cls, data: Config = None):
        try:
            if data is None:
                data = cls.data_obj
            if CONFIG_TYPE == "json":
                with open(CONFIG_PATH, "w", encoding="utf-8") as file:
                    json.dump(data.to_dict(), file, indent=4, ensure_ascii=False)
            else:
                with open(CONFIG_PATH, "w", encoding="utf-8") as file:
                    yaml.dump(
                        data.to_dict(),
                        file,
                        indent=4,
                        allow_unicode=True,
                        sort_keys=False,
                    )
            return True
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            log.exception(f"写入数据文件失败: {e}")
            return False


ConfigManager.load_config()
