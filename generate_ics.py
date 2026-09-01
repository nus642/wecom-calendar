import os
import re
from datetime import datetime, timedelta, timezone
from exchangelib import Credentials, Account, Configuration, BASIC, Build
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
    
    # 优先使用配置的 URL 域名，否则使用默认企微服务器
    server = clean_input(CALDAV_URL) if CALDAV_URL else "wecom.work"

    print("================ 开始 Exchange (EAS) 同步 ================")
    print(f"账号: {user}")
    print(f"服务器: {server}")

    credentials = Credentials(username=user, password=password)
    
    # 强制指定 BASIC 认证方式，并锁定 Exchange 2013/2016 协议版本
    config = Configuration(
        server=server,
        credentials=credentials,
        auth_type=BASIC,
        version=Build(15, 0, 0, 0)
    )

    try:
        account = Account(
            primary_smtp_address=user,
            config=config,
            autodiscover=False,
            access_type='delegate'
        )
        print("✅ Exchange 服务器认证成功！")
    except Exception as e:
        print(f"❌ Exchange 连接认证失败: {e}")
        exit(1)

    new_cal = Calendar()
    new_cal.add('prodid', '-//WeCom Exchange to Google Calendar Bridge//CN')
    new_cal.add('version', '2.0')
    new_cal.add('X-WR-CALNAME', '企业微信日程')

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=30)
    end_time = now + timedelta(days=60)

    print("正在拉取日程数据...")
    try:
        # 直接提取日历项
        items = account.calendar.filter(
            start__lt=end_time,
            end__gt=start_time
        )

        count = 0
        for item in items:
            event = Event()
            event.add('summary', item.subject or '无标题')
            if item.start:
                event.add('dtstart', item.start)
            if item.end:
                event.add('dtend', item.end)
            if item.location:
                event.add('location', item.location)
            if item.body:
                event.add('description', str(item.body))

            new_cal.add_component(event)
            count += 1

        print(f"🎉 成功提取到 {count} 条日程！")

    except Exception as e:
        print(f"❌ 获取日历事件失败: {e}")
        exit(1)

    os.makedirs("public", exist_ok=True)
    with open("public/calendar.ics", "wb") as f:
        f.write(new_cal.to_ical())
    print("calendar.ics 生成成功！")

if __name__ == "__main__":
    fetch_and_convert()
