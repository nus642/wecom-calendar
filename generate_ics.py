import os
import re
from datetime import datetime, timedelta, timezone
from caldav import DAVClient
from icalendar import Calendar

CALDAV_URL = os.environ.get("CALDAV_URL", "").strip()
CALDAV_USER = os.environ.get("CALDAV_USER", "").strip()
CALDAV_PASS = os.environ.get("CALDAV_PASS", "").strip()

def format_url(url):
    if not url:
        return ""
    url = re.sub(r'[\[\]"]', '', url).strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url.rstrip('/')

def fetch_and_convert():
    clean_url = format_url(CALDAV_URL)
    print(f"正在连接 CalDAV 服务器: {clean_url}")
    
    client = DAVClient(url=clean_url, username=CALDAV_USER, password=CALDAV_PASS)
    
    calendars = []
    try:
        principal = client.principal()
        calendars = principal.calendars()
    except Exception as e:
        print(f"尝试默认 principal 失败，改用用户路径: {e}")
        user_principal_url = f"{clean_url}/principals/users/{CALDAV_USER}/"
        my_principal = client.principal(url=user_principal_url)
        calendars = my_principal.calendars()

    if not calendars:
        print("未找到任何日历")
        return

    new_cal = Calendar()
    new_cal.add('prodid', '-//WeCom to Google Calendar Bridge//CN')
    new_cal.add('version', '2.0')
    new_cal.add('X-WR-CALNAME', '企业微信日程')

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=30)
    end_time = now + timedelta(days=60)

    for cal in calendars:
        events = cal.date_search(start=start_time, end=end_time)
        for event in events:
            try:
                parsed_cal = Calendar.from_ical(event.data)
                for component in parsed_cal.walk():
                    if component.name == "VEVENT":
                        new_cal.add_component(component)
            except Exception as e:
                print(f"解析日程出错: {e}")

    os.makedirs("public", exist_ok=True)
    with open("public/calendar.ics", "wb") as f:
        f.write(new_cal.to_ical())
    print("calendar.ics 生成成功！")

if __name__ == "__main__":
    fetch_and_convert()
