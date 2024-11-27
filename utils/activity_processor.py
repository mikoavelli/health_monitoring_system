import json
from main.models import Activity, StandUp, Movement, Device
from datetime import datetime, timedelta


def process_activity_data(json_file_path, user, timestamp) -> bool:
    if not Device.objects.filter(user=user).exists():
        return False

    if isinstance(timestamp, str):
        timestamp = datetime.strptime(timestamp, "%Y%m%d_%H%M")

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    activities = data.get("activities", [])

    for activity in activities:
        date_str = activity["date"]
        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        date = date.replace(second=0, microsecond=0)

        # Проверяем, существуют ли записи
        if Activity.objects.filter(date=date, user=user).exists():
            continue
        if StandUp.objects.filter(timestamp=date, user=user).exists():
            continue
        if Movement.objects.filter(timestamp=date, user=user).exists():
            continue

        # Создаем записи
        Activity.objects.create(
            date=date,
            steps=activity["steps"],
            calories=activity["calories"],
            distance=activity["distance"],
            user=user
        )
        StandUp.objects.create(
            count=activity["standups"],
            timestamp=date,
            user=user
        )
        Movement.objects.create(
            count=activity["movements"],
            timestamp=date,
            user=user
        )

    return True
