from workers import WorkerEntrypoint, Response, fetch
import json
from notify_trash_lambda import compose_message

class Default(WorkerEntrypoint):
    async def scheduled(self, controller, env, ctx):
        event = {
            "0 12 * * mon-fri": "trash_notification",
            "0 12 * * sun": "cleaning_duty_schedule",
            "0 3 24 * *": "rent_to_habataku",
            "0 3 22 * *": "rent_to_leader",
        }[controller.cron]

        message = compose_message(event, controller.scheduledTime, self.env)

        url = "https://api.line.me/v2/bot/message/push"

        payload = json.dumps(
            {
                "to": self.env.RECIPIENT_ID,
                "messages": [message],
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.env.LINE_CHANNEL_SECRET}"
        }

        # Post Method is invoked if data != None
        return await fetch(url, method='POST', headers=headers, body=payload.encode())
