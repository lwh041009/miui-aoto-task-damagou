# MIUI Auto Tasks

小米社区 / MIUI 自动任务脚本。脚本会读取 `data/config.json` 中的账号配置，登录后执行已启用的每日任务，并在结束时通过 OnePush 推送运行日志。

## 功能

- 多账号自动执行任务
- 支持 cookie 有效时跳过登录
- 支持账号密码登录补全 cookie
- 支持极验验证码接口配置
- 支持 OnePush 推送，例如企业微信机器人

## 环境要求

- Python 3.11 或更高版本
- Windows 推荐 Python 3.12

安装依赖：

```powershell
pip install -r requirements.txt
```

## 配置账号

账号配置文件是：

```text
data/config.json
```

首次使用时，可以先复制模板：

```powershell
Copy-Item data/config.example.json data/config.json
```

`data/config.json` 包含真实账号、cookie、token 和推送 key，已经被 `.gitignore` 忽略；`data/config.example.json` 是安全模板，可以提交到仓库。

打码狗 `userkey` 填在 `preference.damagou_userkey`，也可以通过环境变量 `DAMAGOU_USERKEY` 提供。

每个账号主要需要这些字段：

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

新账号建议先在本机浏览器完成一次真实登录，抓取 `deviceId`、`pass_ua`、`uLocale`、`passToken`、`cUserId`、`userId` 等字段后再写入配置。不同账号尽量使用各自真实环境里的 `deviceId`。

## 配置推送

推送配置同样在 `data/config.json` 的 `ONEPUSH` 节点。

企业微信群机器人示例：

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

`key` 是企业微信群机器人 webhook 最后的那串值：

```text
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=这里这一串
```

## 运行

Windows 双击：

```text
启动.bat
```

或在项目目录执行：

```powershell
py -3.12 miuitask.py
```

Linux / 定时任务可参考 `daily_task.sh`，运行前请确认 Python 路径和项目路径正确。

## 日志

运行日志会写入：

```text
logs/
```

脚本结束后会把本次运行日志内容推送出去。如果未配置推送，任务仍会正常执行，只是最后不会发送通知。

## 安全提醒

`data/config.json` 里包含账号、cookie、token、推送 key 等敏感信息，不要上传到公开仓库，也不要发给别人。
