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
    print(f"1. 读取到的 URL: {url}")
    print(f"2. 读取到的账号: {CALDAV_USER}")
    print(f"3. 密码长度: {len(CALDAV_PASS)} 位 (已隐去明文)")

    if not url or not CALDAV_USER or not CALDAV_PASS:
        print("❌ 错误：有环境变量未读取到，请检查 Secrets 名字是否完全一致！")
        exit(1)

    try:
        print("\n正在建立 CalDAV 连接...")
        client = DAVClient(url=url, username=CALDAV_USER, password=CALDAV_PASS)
        
        # 尝试连通
        try:
            principal = client.principal()
            calendars = principal.calendars()
        except Exception:
            print("默认路径失败，尝试企微专属路径...")
            user_url = f"{url}/principals/users/{CALDAV_USER}/"
            principal = client.principal(url=user_url)
            calendars = principal.calendars()

        print(f"✅ 认证成功！成功获取到 {len(calendars)} 个日历。")
        print("================ Secrets 验证通过 ================")

    except Exception as e:
        print(f"\n❌ 连接失败，具体错误信息：\n{e}")
        print("==================================================")
        exit(1)

if __name__ == "__main__":
    test_connection()
