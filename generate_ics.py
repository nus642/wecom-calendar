import os
from datetime import datetime, timedelta, timezone
from caldav import DAVClient
from icalendar import Calendar

# 从环境变量中读取配置
CALDAV_URL = os.environ.get("CALDAV_URL", "").strip()
CALDAV_USER = os.environ.get("CALDAV_USER", "").strip()
CALDAV_PASS = os.environ.get("CALDAV_PASS", "").strip()

def format_url(url):
    """确保 URL 包含 https:// 前缀且末尾不带斜杠"""
    if not url:
        return ""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url.rstrip('/')

def fetch_and_convert():
    clean_url = format_url(CALDAV_URL)
    
    # 连接企业微信 CalDAV
    client = DAVClient(url=clean_url, username=CALDAV_USER, password=CALDAV_PASS)
    
    calendars = []
    try:
        principal = client.principal()
        calendars = principal.calendars()
    except Exception as e:
        print(f"尝试默认 principal 获取失败: {e}，改用用户路径获取...")
        user_principal_url = f"{clean_url}/principals/users/{CALDAV_USER}/"
        my_principal = client.principal(url=user_principal_url)
        calendars = my_principal.calendars()

    if not calendars:
        print("未找到任何日历")
        return

    # 创建标准 ics 日历对象
    new_cal = Calendar()
    new_cal.add('prodid', '-//WeCom to Google Calendar Bridge//CN')
    new_cal.add('version', '2.0')
    new_cal.add('X-WR-CALNAME', '企业微信日程')

    # 获取前后 30 天/60 天的日程
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=30)
    end_time = now + timedelta(days=60)

    # 遍历所有日历事件
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

    # 保存文件到 public 目录
    os.makedirs("public", exist_ok=True)
    with open("public/calendar.ics", "wb") as f:
        f.write(new_cal.to_ical())
    print("calendar.ics 生成成功！")

if __name__ == "__main__":
    fetch_and_convert()
