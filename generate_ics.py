import os
import re
import urllib.request
import urllib.error
import base64

CALDAV_USER = os.environ.get("CALDAV_USER", "").strip()
CALDAV_PASS = os.environ.get("CALDAV_PASS", "").strip()

def direct_test():
    urls = [
        "https://caldav.wecom.work",
        "https://wecom.work"
    ]

    body = """<?xml version="1.0" encoding="utf-8" ?>
    <D:propfind xmlns:D="DAV:">
        <D:prop><D:current-user-principal/></D:prop>
    </D:propfind>""".encode('utf-8')

    # 生成 Basic Auth 认证头
    auth_str = f"{CALDAV_USER}:{CALDAV_PASS}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

    headers = {
        "User-Agent": "iOS/16.0 (20A362) calendard/1.0",
        "Content-Type": "text/xml; charset=utf-8",
        "Authorization": f"Basic {auth_b64}"
    }

    print("================ 企微 CalDAV 深入诊断 ================")
    print(f"当前测试账号: {CALDAV_USER}")

    for base_url in urls:
        print(f"\n[测试服务器]: {base_url}")
        req = urllib.request.Request(base_url, data=body, headers=headers, method="PROPFIND")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                status = response.getcode()
                print(f"HTTP 状态码: {status}")
                if status == 207:
                    print(f"✅ {base_url} 认证成功！")
        except urllib.error.HTTPError as e:
            print(f"HTTP 状态码: {e.code}")
            if e.code == 403:
                print(f"❌ {base_url} 报错 403 Forbidden（可能被企业管理员禁用或密码不正确）")
            elif e.code == 401:
                print(f"❌ {base_url} 报错 401 Unauthorized（账号或密码明确错误）")
            else:
                print(f"⚠️ 返回状态: {e.code}")
        except Exception as e:
            print(f"网络异常: {e}")

if __name__ == "__main__":
    direct_test()
