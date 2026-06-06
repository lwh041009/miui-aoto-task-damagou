#!/bin/bash
cd /root/miui-auto-tasks
source venv/bin/activate
python3 << 'PYEOF'
import sys, os
sys.path.insert(0, '/root/miui-auto-tasks')
os.chdir('/root/miui-auto-tasks')

from utils.config import ConfigManager
from utils.api.sign import BaseSign, CheckIn, BrowsePost, CarrotPull
from utils.utils import get_token

ConfigManager.load_config()
account = ConfigManager.data_obj.accounts[0]

# First renew cookies if needed
from utils.api.login import Login
login_obj = Login(account)

# Try to login with existing passToken
cookies = login_obj.login()
if cookies:
    print("✅ Cookie续期成功")
else:
    print("⚠️ Cookie续期失败，用已有的跑")

# Run tasks that don't need captcha
tasks_done = []

# BrowsePost (doesn't need token)
try:
    obj = BrowsePost(account)
    status, reason = obj.sign()
    if status:
        tasks_done.append("浏览帖子")
        print("✅ 浏览帖子成功")
    else:
        print(f"❌ 浏览帖子: {reason}")
except Exception as e:
    print(f"❌ 浏览帖子: {e}")

# CarrotPull (doesn't need token)
try:
    obj = CarrotPull(account)
    status, reason = obj.sign()
    if status:
        tasks_done.append("拔萝卜")
        print("✅ 拔萝卜成功")
    else:
        print(f"❌ 拔萝卜: {reason}")
except Exception as e:
    print(f"❌ 拔萝卜: {e}")

# Get user info
try:
    sign_obj = BaseSign(account)
    info = sign_obj.user_info()
    print(f"👤 当前成长值: {info.point}")
except:
    pass

PYEOF
