# MIUI Auto Tasks Damagou

小米社区 / MIUI 自动任务脚本。脚本会读取本地配置文件，按账号配置执行每日任务，结束后可通过 OnePush 推送运行日志。

本项目基于 [0-8-4/miui-auto-tasks](https://github.com/0-8-4/miui-auto-tasks) 修改，主要加入了打码狗验证码适配、配置模板、企业微信推送示例和日志整理。

## 快速开始

1. 安装 Python 依赖：

```powershell
pip install -r requirements.txt
```

2. 复制配置模板：

```powershell
Copy-Item data/config.example.json data/config.json
```

3. 打开 `data/config.json`，填写打码狗 key、账号信息和推送配置。

4. 运行脚本：

```powershell
py -3.12 miuitask.py
```

Windows 也可以直接双击：

```text
启动.bat
```

## 配置文件

推荐配置文件：

```text
data/config.json
```

模板文件：

```text
data/config.example.json
```

上传仓库时只需要保留模板文件。实际运行时，把模板复制成 `data/config.json` 后再填写自己的内容。

配置读取规则：

- 如果存在 `data/config.json`，脚本优先读取 `data/config.json`
- 如果不存在 `data/config.json`，脚本会自动创建并使用 `data/config.yaml`
- 也可以通过环境变量 `MIUITASK_CONFIG_PATH` 指定配置文件路径

如果想直接用自动生成的 YAML 配置，可以先运行一次脚本，让它生成：

```text
data/config.yaml
```

然后再编辑这个文件。

## 打码狗配置

打码狗 `userkey` 只需要填一次：

```json
"preference": {
    "damagou_userkey": "你的打码狗userkey"
}
```

也可以不写进配置文件，改用环境变量：

```powershell
$env:DAMAGOU_USERKEY="你的打码狗userkey"
```

## 账号配置

账号密码登录时，最低建议先填这些字段：

```json
{
    "uid": "小米账号UID",
    "password": "明文密码或32位MD5",
    "login_user_agent": "浏览器登录时使用的User-Agent",
    "deviceId": "浏览器环境里的deviceId"
}
```

`login_user_agent` 和 `deviceId` 尽量使用同一个真实浏览器环境里的值。实际测试中，浏览器先过一次验证后，再用相同登录环境登录，通常更不容易触发手机验证码。

更完整的账号配置示例：

```json
{
    "uid": "小米账号UID",
    "password": "明文密码或32位MD5",
    "cookies": {
        "passToken": "抓包或登录得到的passToken",
        "cUserId": "抓包或登录得到的cUserId",
        "userId": "小米账号UID",
        "passInfo": "login-end"
    },
    "login_user_agent": "登录账号时使用的User-Agent",
    "deviceId": "抓包得到的deviceId",
    "pass_ua": "web",
    "uLocale": "zh_CN",
    "user_agent": "社区接口使用的User-Agent",
    "device": "",
    "device_model": "",
    "CheckIn": true,
    "BrowseUserPage": true,
    "BrowsePost": true,
    "BrowseVideoPost": false,
    "ThumbUp": false,
    "BrowseSpecialPage": false,
    "BoardFollow": false,
    "CarrotPull": true,
    "WxSign": true
}
```

新账号建议先在本机浏览器完成一次真实登录，再把抓到的 `deviceId`、`pass_ua`、`uLocale`、`passToken`、`cUserId`、`userId` 写进配置。

## 推送配置

推送配置在 `ONEPUSH` 节点。企业微信群机器人示例：

```json
"ONEPUSH": {
    "notifier": "wechatworkbot",
    "params": {
        "title": "小米社区自动任务",
        "markdown": false,
        "key": "企业微信群机器人key"
    }
}
```

企业微信机器人的 `key` 是 webhook 最后的那串值：

```text
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=这里这一串
```

不需要推送时，把 `notifier` 留空即可。

## 日志

日志会写到：

```text
logs/
```

当前版本按日期生成日志文件，例如：

```text
logs/2026-06-06.log
```

日志最多保留最近 15 天。

## Linux 定时任务

Linux 可参考 `daily_task.sh`，使用前请确认脚本里的 Python 路径和项目路径适合自己的环境。
