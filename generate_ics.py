import os
import requests
from requests.auth import HTTPBasicAuth

CALDAV_USER = os.environ.get("CALDAV_USER", "").strip()
CALDAV_PASS = os.environ.get("CALDAV_PASS", "").strip()

def direct_test():
    urls = [
        "https://caldav.wecom.work",
        "https://wecom.work"
    ]
    
    headers = {
        "User-Agent": "iOS/16.0 (20A362) calendard/1.0",
        "Content-Type": "text/xml; charset=utf-8"
    }

    body = """<?xml version="1.0" encoding="utf-8" ?>
    <D:propfind xmlns:D="DAV:">
        <D:prop><D:current-user-principal/></D:prop>
    </D:propfind>"""

    print("================ 企微 CalDAV 深入诊断 ================")
    print(f"当前测试账号: {CALDAV_USER}")
    
    for base_url in urls:
        print(f"\n[测试服务器]: {base_url}")
        try:
            res = requests.request(
                "PROPFIND",
                base_url,
                auth=HTTPBasicAuth(CALDAV_USER, CALDAV_PASS),
                data=body,
                headers=headers,
                timeout=10
            )
            print(f"HTTP 状态码: {res.status_code}")
            if res.status_code == 207:
                print(f"✅ {base_url} 认证成功！")
            elif res.status_code == 403:
                print(f"❌ {base_url} 报错 403 Forbidden（可能被企业管理员禁用或密码不正确）")
            elif res.status_code == 401:
                print(f"❌ {base_url} 报错 401 Unauthorized（账号或密码明确错误）")
            else:
                print(f"⚠️ 返回状态: {res.status_code}")
        except Exception as e:
            print(f"网络异常: {e}")

if __name__ == "__main__":
    direct_test()
