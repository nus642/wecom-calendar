import os
from datetime import datetime, timedelta, timezone
from caldav import DAVClient
from icalendar import Calendar, Event

# 从环境变量中读取密码配置
CALDAV_URL = os.environ.get("CALDAV_URL")
CALDAV_USER = os.environ.get("CALDAV_USER")
CALDAV_PASS = os.environ.get("CALDAV_PASS")

def fetch_and_convert():
    # 连接企业微信 CalDAV
    client = DAVClient(url=CALDAV_URL, username=CALDAV_USER, password=CALDAV_PASS)
    principal = client.principal()
    calendars = principal.calendars()

    if not calendars:
        print("未找到任何日历")
        return

    # 创建一个新的标准 ics 日历对象
    new_cal = Calendar()
    new_cal.add('prodid', '-//WeCom to Google Calendar Bridge//CN')
    new_cal.add('version', '2.0')
    new_cal.add('X-WR-CALNAME', '企业微信日程')

    # 获取前后 30 天的日程，避免范围过大
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=30)
    end_time = now + timedelta(days=60)

    # 遍历所有日历事件并拉取
    for cal in calendars:
        events = cal.date_search(start=start_time, end=end_time)
        for event in events:
            try:
                # 解析原始 ics 事件
                parsed_cal = Calendar.from_ical(event.data)
                for component in parsed_cal.walk():
                    if component.name == "VEVENT":
                        new_cal.add_component(component)
            except Exception as e:
                print(f"解析日程出错: {e}")

    # 将合并后的 ics 保存为文件
    os.makedirs("public", exist_ok=True)
    with open("public/calendar.ics", "wb") as f:
        f.write(new_cal.to_ical())
    print("calendar.ics 生成成功！")

if __name__ == "__main__":
    fetch_and_convert()
