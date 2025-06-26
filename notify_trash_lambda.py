import os
import requests
from datetime import datetime, timedelta, timezone
import json


def get_tomorrow(datetime_str):
    date_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
    # Convert the datetime object to Japan Standard Time (JST)
    jst = timezone(timedelta(hours=9))
    date_obj = date_obj.astimezone(jst)

    # Calculate the next day at 7 AM JST
    next_morning = (date_obj + timedelta(days=1)).replace(
        hour=7, minute=0, second=0, microsecond=0
    )

    return next_morning


def get_week_number(datetime_str):
    # Convert the string to a datetime object
    date_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")

    # Get the week number
    week_number = date_obj.isocalendar().week

    return week_number


def get_cleaner_list(week_number):
    residents = ["{koga}", "{kaede}", "{ryuichiro}", "{nanako}", "{kyoichi}"]
    cleaning_tasks = [
        "🚰洗面所＆キッチン🔪",
        "🧹床掃除(階段も）🧹",
        "🧺共用のタオル🫧",
        "🗑️ゴミ捨て🚮",
        "🧼トイレ＆浴室🚽",
    ]

    # Calculate the starting index based on the week number
    start_index = week_number % len(residents)

    # Rotate the list of residents based on the starting index
    rotated_residents = residents[start_index:] + residents[:start_index]

    # Create the message string
    message_lines = [
        f"①{cleaning_tasks[0]}：{rotated_residents[0]}",
        f"②{cleaning_tasks[1]}：{rotated_residents[1]}",
        f"③{cleaning_tasks[2]}：{rotated_residents[2]}",
        f"④{cleaning_tasks[3]}：{rotated_residents[3]}",
        f"⑤{cleaning_tasks[4]}：{rotated_residents[4]}",
    ]

    # Join the lines into a single string
    message = "\n".join(message_lines)

    return message, rotated_residents[len(residents) - 1]  # Return the last resident as the cleaner


def compose_message(event):
    cleaner_list_message, cleaner = get_cleaner_list(week_number)
    if event["identifier"] == "trash_notification":
        tomorrow = get_tomorrow(
            event.get("time", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        )
        trash_tomorrow = determine_trash(tomorrow)

        if trash_tomorrow is None:
            return

        message = f"{{user}} 明日のゴミは{trash_tomorrow}です。"
        payload = {
            "type": "textV2",
            "text": message,
            "substitution": {
                "user": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": os.environ[cleaner.replace("{","").replace("}","").upper() + "_USER_ID"],
                    },
                }
            },
        }
        return payload
    elif event["identifier"] == "cleaning_duty_schedule":
        # make payload for the cleaning
        week_number = get_week_number(
            event.get("time", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        )
        
        return {
            "type": "textV2",
            "text": cleaner_list_message,
            "substitution": {
                "koga": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user", 
                        "userId": os.environ["KOGA_USER_ID"]},
                },
                "kaede": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": os.environ["KAEDE_USER_ID"],
                    },
                },
                "nanako": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": os.environ["NANAKO_USER_ID"],
                    },
                },
                "ryuichiro": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": os.environ["RYUICHIRO_USER_ID"],
                    }
                },
                "kyoichi": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": os.environ["KYOICHI_USER_ID"],
                    }      
                },
            }  
        }
    elif event["identifier"] == "rent_payment_notification":
        return {
            "type": "textV2",
            "text": "{everyone} 明日25日は家賃の支払日です。忘れないうちに家賃を払いましょう。",
            "substitution": {
                "everyone": {"type": "mention", "mentionee": {"type": "all"}}
            },
        }


def determine_trash(date):
    day_of_week = date.weekday()  # Monday is 0 and Sunday is 6
    day_of_month = date.day

    if day_of_week == 0 or day_of_week == 3:  # Monday or Thursday
        return "🔥 燃えるゴミ Burnables 🔥"
    elif day_of_week == 1:  # Tuesday
        return "♳ プラスチック Plastic ♳"
    elif day_of_week == 2:  # Wednesday
        # Check if it's the 2nd or 4th Wednesday
        week_of_month = (day_of_month - 1) // 7 + 1
        if week_of_month == 2 or week_of_month == 4:
            return "㊎ 燃えないゴミ(金属、電池、ガラス、蛍光灯など) Non burnables 🪫"
    elif day_of_week == 4:  # Friday
        return "🧴 資源(紙、缶、瓶、ペットボトルなど) Recyclables 🗞️"


def lambda_handler(event, context):
    url = "https://api.line.me/v2/bot/message/push"

    payload = json.dumps(
        {
            "to": "{}".format(os.environ["RECIPIENT_ID"]),
            "messages": [compose_message(event)],
        }
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(os.environ["LINE_CHANNEL_ACCESS_TOKEN"]),
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
