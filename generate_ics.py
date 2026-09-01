import os
import re
from datetime import datetime, timedelta, timezone
from exchangelib import Credentials, Account, Configuration, DEEP, FileAttachment
from icalendar import Calendar, Event

# 从 Secrets 获取配置
CALDAV_USER = os.environ.get("CALDAV_USER", "").strip()  # 企微/企业邮箱账号 (例: user@company.com)
CALDAV_PASS = os.environ.get("CALDAV_PASS", "").strip()  # 客户端专用密码/邮箱密码
# Exchange 服务器地址，腾讯企业邮/企微通常为 ex.qq.com
EXCHANGE_SERVER = "wecom.work"

def clean_input(text):
    if not text:
        return ""
    return re.sub(r'[\[\]"]', '', text).strip()

def fetch_and_convert():
    user = clean_input(CALDAV_USER)
    password = clean_input(CALDAV_PASS)

    print(f"================ 开始尝试 Exchange (EAS) 同步 ================")
    print(f"账号: {user}")
    print(f"服务器: {EXCHANGE_SERVER}")

    # 1. 建立 Exchange 认证与连接
    credentials = Credentials(username=user, password=password)
    config = Configuration(server=EXCHANGE_SERVER, credentials=credentials)
    
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

    # 2. 获取日历中的日程事件
    new_cal = Calendar()
    new_cal.add('prodid', '-//WeCom Exchange to Google Calendar Bridge//CN')
    new_cal.add('version', '2.0')
    new_cal.add('X-WR-CALNAME', '企业微信日程')

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=30)
    end_time = now + timedelta(days=60)

    print("正在拉取日程数据...")
    try:
        # 查询指定时间范围内的 Exchange 日程项
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

        print(f"✅ 成功提取到 {count} 条日程！")

    except Exception as e:
        print(f"❌ 获取日历事件失败: {e}")
        exit(1)

    # 3. 保存为 public/calendar.ics
    os.makedirs("public", exist_ok=True)
    with open("public/calendar.ics", "wb") as f:
        f.write(new_cal.to_ical())
    print("🎉 calendar.ics 生成成功！")

if __name__ == "__main__":
    fetch_and_convert()
