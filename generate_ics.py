import os
import re
from datetime import datetime, timedelta, timezone
import caldav
from icalendar import Calendar, Event

CALDAV_USER = os.environ.get("CALDAV_USER", "").strip()
CALDAV_PASS = os.environ.get("CALDAV_PASS", "").strip()
CALDAV_URL = os.environ.get("CALDAV_URL", "").strip()

def clean_input(text):
    if not text:
        return ""
    text = re.sub(r'[\[\]"]', '', text).strip()
    text = re.sub(r'^https?://', '', text)
    return text.rstrip('/')

def fetch_and_convert():
    user = clean_input(CALDAV_USER)
    password = clean_input(CALDAV_PASS)
    
    # 按照截图提示，默认服务器地址为 caldav.wecom.work
    server = clean_input(CALDAV_URL) if CALDAV_URL else "caldav.wecom.work"
    url = f"https://{server}/"

    print("================ 开始 CalDAV 动态密码同步 ================")
    print(f"账号: {user}")
    print(f"服务器: {url}")

    try:
        client = caldav.DAVClient(
            url=url,
            username=user,
            password=password
        )
        principal = client.principal()
        calendars = principal.calendars()
        
        if not calendars:
            print("❌ 未找到有效日历对象，请检查动态密码是否已过期。")
            exit(1)
            
        print("✅ CalDAV 动态密码验证成功！")
        calendar = calendars[0]

    except Exception as e:
        print(f"❌ CalDAV 连接失败: {e}")
        print("💡 提示：企业微信 CalDAV 密码为动态密码，生成后请确保第一时间更新 GitHub Secrets 并立即运行。")
        exit(1)

    new_cal = Calendar()
    new_cal.add('prodid', '-//WeCom to Google Calendar Bridge//CN')
    new_cal.add('version', '2.0')
    new_cal.add('X-WR-CALNAME', '企业微信日程')

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=30)
    end_time = now + timedelta(days=60)

    print("正在拉取日程事件...")
    try:
        results = calendar.date_search(start=start_time, end=end_time, expand=True)
        count = 0

        for event in results:
            for component in event.icalendar_instance.walk():
                if component.name == "VEVENT":
                    new_cal.add_component(component)
                    count += 1

        print(f"🎉 成功拉取到 {count} 条日程！")

    except Exception as e:
        print(f"❌ 解析日程失败: {e}")
        exit(1)

    os.makedirs("public", exist_ok=True)
    with open("public/calendar.ics", "wb") as f:
        f.write(new_cal.to_ical())
    print("calendar.ics 文件保存成功！")

if __name__ == "__main__":
    fetch_and_convert()
