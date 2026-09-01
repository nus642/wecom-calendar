import os
import re
import urllib.request
import urllib.error
import base64

CALDAV_USER = os.environ.get("CALDAV_USER", "").strip()
CALDAV_PASS = os.environ.get("CALDAV_PASS", "").strip()
CALDAV_URL = os.environ.get("CALDAV_URL", "").strip()

def clean_input(text):
    if not text:
        return ""
    text = re.sub(r'[\[\]"]', '', text).strip()
    return text

def fetch_and_convert():
    user = clean_input(CALDAV_USER)
    password = clean_input(CALDAV_PASS)
    custom_url = clean_input(CALDAV_URL)

    print("================ 开始企业微信 ICS 直连同步 ================")
    print(f"账号: {user}")

    # 构造可能的直连 ICS / WebDAV 订阅地址
    candidate_urls = []
    if custom_url:
        if not custom_url.startswith("http"):
            custom_url = "https://" + custom_url
        candidate_urls.append(custom_url)
    
    # 企微与腾讯企邮常见的日历导出节点
    candidate_urls.extend([
        f"https://ex.qq.com/ical/calendar.ics",
        f"https://wecom.work/dav/calendars/{user}/",
        f"https://caldav.wecom.work/calendars/{user}/",
        f"https://ex.qq.com/exchange/{user}/Calendar"
    ])

    auth_str = f"{user}:{password}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    headers = {
        "User-Agent": "iOS/16.0 (20A362) calendard/1.0",
        "Authorization": f"Basic {auth_b64}"
    }

    ics_content = None
    for url in candidate_urls:
        print(f"尝试抓取节点: {url}")
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                if response.getcode() in [200, 207]:
                    data = response.read()
                    if b"BEGIN:VCALENDAR" in data:
                        ics_content = data
                        print(f"✅ 成功从 {url} 抓取到 ICS 日历数据！")
                        break
                    else:
                        print("⚠️ 节点响应成功但未返回有效 ICS 结构。")
        except urllib.error.HTTPError as e:
            print(f"❌ 节点返回 HTTP {e.code}")
        except Exception as e:
            print(f"❌ 连接失败: {e}")

    if not ics_content:
        print("\n❌ 所有默认节点均未直接导出 ICS 数据。")
        print("💡 请打开手机企业微信 -> 日程 -> 右上角菜单 -> 同步至其他日历/导出日历，查看显示的专用【订阅链接/URL】并填入 GitHub Secrets 的 CALDAV_URL 中。")
        exit(1)

    os.makedirs("public", exist_ok=True)
    with open("public/calendar.ics", "wb") as f:
        f.write(ics_content)
    print("🎉 calendar.ics 生成并保存成功！")

if __name__ == "__main__":
    fetch_and_convert()
