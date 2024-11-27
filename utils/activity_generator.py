from datetime import datetime, timedelta
import random
import json


def generate_activity_data(device_name, device_type, user):
    """Генерирует данные активности за последние 24 часа и сохраняет в JSON-файл."""
    activities = []
    now_time = datetime.now()

    for hour in range(24):
        hour_time = now_time - timedelta(hours=hour)

        # Генерация случайных данных
        steps = random.randint(0, 500)
        standups = random.randint(0, 4)
        movements = random.randint(0, 10)
        calories = round(random.uniform(5, 100), 2)
        distance = round(random.uniform(0.05, 1.5), 2)

        # Добавляем данные в список
        activities.append({
            "date": hour_time.strftime("%Y-%m-%d %H:00"),
            "steps": steps,
            "standups": standups,
            "movements": movements,
            "calories": calories,
            "distance": distance,
        })

    # Генерация структуры JSON
    data = {
        "device_name": device_name,
        "device_type": device_type,
        "activities": activities
    }

    # Формирование имени файла
    timestamp = now_time.strftime("%Y%m%d_%H%M")
    json_filename = f"{user.username}_{timestamp}.json"
    json_path = f"/tmp/{json_filename}"

    # Сохранение JSON-файла
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    return json_path, timestamp
