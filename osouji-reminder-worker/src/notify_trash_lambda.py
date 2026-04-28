from datetime import datetime, timedelta, timezone

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
    residents = ["{koga}", "{kaede}", "{yasuyo}", "{nanako}", "{kyoichi}"]
    cleaning_tasks = [
        "☘️植木に水やり🪴",
        "🧹床掃除(階段も）🧹",
        "🧺共用のタオル🫧",
        "🧼トイレ＆浴室🚽",
        "🗑️ゴミ捨て🚮",
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

    next_week_cleaner = rotated_residents[len(residents) - 1]

    return message, rotated_residents[len(residents) - 2], next_week_cleaner  # Return the last resident as the cleaner


def compose_message(event, time, env):
    dt = datetime.fromtimestamp(time / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    week_number = get_week_number(dt)
    cleaner_list_message, cleaner, next_week_cleaner = get_cleaner_list(week_number)
    if event == "trash_notification":
        tomorrow = get_tomorrow(dt)
        trash_tomorrow = determine_trash(tomorrow)

        if trash_tomorrow is None:
            return

        correct_cleaner = next_week_cleaner if tomorrow.weekday() == 0 else cleaner

        message = f"{{user}} 明日のゴミは{trash_tomorrow}です。"
        payload = {
            "type": "textV2",
            "text": message,
            "substitution": {
                "user": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": env[correct_cleaner.replace("{","").replace("}","").upper() + "_USER_ID"],
                    },
                }
            },
        }
        return payload
    elif event == "cleaning_duty_schedule":
        return {
            "type": "textV2",
            "text": cleaner_list_message,
            "substitution": {
                "koga": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": env.KOGA_USER_ID,
                    },
                },
                "kaede": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": env.KAEDE_USER_ID,
                    },
                },
                "nanako": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": env.NANAKO_USER_ID,
                    },
                },
                "yasuyo": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": env.RYUICHIRO_USER_ID,
                    }
                },
                "kyoichi": {
                    "type": "mention",
                    "mentionee": {
                        "type": "user",
                        "userId": env.KYOICHI_USER_ID,
                    }
                }
            },
        }
    elif event == "rent_to_habataku":
        return {
            "type": "textV2",
            "text": "{leader} 明日25日は家賃の支払日です。ハバタクに振り込みましょう",
            "substitution": {
                "leader": {"type": "mention", "mentionee": {"type": "user", "userId": env.KAEDE_USER_ID}}
            },
        }
    elif event == "rent_to_leader":
        return {
            "type": "textV2",
            "text": "{everyone} 今日は家賃の支払日です。{leader}に振り込みましょう。",
            "substitution": {
                "everyone": {"type": "mention", "mentionee": {"type": "all"}},
                "leader": {"type": "mention", "mentionee": {"type": "user", "userId": env.KAEDE_USER_ID}}
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
