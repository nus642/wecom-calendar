import os
import re
from caldav import DAVClient

CALDAV_URL = os.environ.get("CALDAV_URL", "").strip()
CALDAV_USER = os.environ.get("CALDAV_USER", "").strip()
CALDAV_PASS = os.environ.get("CALDAV_PASS", "").strip()

def clean_url(url):
    if not url:
        return ""
    url = re.sub(r'[\[\]"]', '', url).strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url.rstrip('/')

def test_connection():
    url = clean_url(CALDAV_URL)
    print("================ 开始测试 Secrets 配置 ================")
    print(f"1. URL: {url}")
    print(f"2. 账号: {CALDAV_USER}")
    print(f"3. 密码长度: {len(CALDAV_PASS)} 位")

    if not url or not CALDAV_USER or not CALDAV_PASS:
        print("❌ 错误：有环境变量未读取到，请检查 Secrets 命名！")
        exit(1)

    client = DAVClient(url=url, username=CALDAV_USER, password=CALDAV_PASS)

    # 依次尝试不同的入口路径
    test_paths = [
        ("默认 Principal 路径", None),
        ("用户 Principal 路径", f"{url}/principals/users/{CALDAV_USER}/"),
        ("直连 Calendar 路径", f"{url}/calendars/{CALDAV_USER}/")
    ]

    success = False
    for name, path in test_paths:
        print(f"\n正在尝试 [{name}]...")
        try:
            if path:
                principal = client.principal(url=path)
            else:
                principal = client.principal()
            
            calendars = principal.calendars()
            print(f"✅ [{name}] 认证成功！获取到 {len(calendars)} 个日历。")
            success = True
            break
        except Exception as e:
            print(f"❌ [{name}] 失败: {e}")

    if success:
        print("\n================ Secrets 验证通过 ================")
    else:
        print("\n❌ 所有路径均鉴权失败(Forbidden)。请重新在企微获取最新CalDAV密码，并检查账号是否完全一致。")
        print("==================================================")
        exit(1)

if __name__ == "__main__":
    test_connection()
