from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required

from datetime import datetime, timedelta

from .forms import LoginForm, RegistrationForm, ProfileEditForm, DeviceForm
from .models import Device, Profile, Activity, StandUp
from utils.activity_generator import generate_activity_data
from utils.activity_processor import process_activity_data


def home_view(request):
    return render(request, 'main/home.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Перенаправление после успешного входа
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Создаём профиль
            Profile.objects.create(
                user=user,
                email=form.cleaned_data['email'],
                gender=form.cleaned_data.get('gender'),
                birthdate=form.cleaned_data.get('birthdate')
            )

            login(request, user)  # Автоматически авторизуем пользователя
            return redirect('profile')  # Перенаправляем на страницу профиля
    else:
        form = RegistrationForm()

    return render(request, 'main/register.html', {'form': form})


@login_required
def profile_view(request):
    # Генерация и обработка данных активности
    json_path, timestamp = generate_activity_data(
        device_name="default_device",
        device_type="default_type",
        user=request.user
    )
    process_activity_data(json_path, request.user, timestamp)

    user = request.user
    activities = Activity.objects.filter(user=user)
    total_steps = sum(activity.steps for activity in activities)
    total_calories = sum(activity.calories for activity in activities)
    total_distance = sum(activity.distance for activity in activities)

    for device in Device.objects.filter(user=user):
        device.last_import_date = datetime.now()
        device.save()

    # Отображение профиля
    profile = request.user.profile
    context = {
        "profile": profile,
        "total_steps": total_steps,
        "total_calories": total_calories,
        "total_distance": total_distance
    }
    return render(request, 'main/profile.html', context)


@login_required
def edit_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'main/edit_profile.html', {'form': form})


@login_required
def health_view(request):
    return render(request, 'main/heath.html')


@login_required
def devices_view(request):
    devices = Device.objects.filter(user=request.user).order_by('-last_import_date')
    return render(request, 'main/devices.html', {"devices": devices})


@login_required
def add_device_view(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.user = request.user
            device.save()
            return redirect('devices')  # Перенаправление на список устройств
    else:
        form = DeviceForm()
    return render(request, 'main/add_device.html', {'form': form})


@login_required
def sync_device(request, device_id):
    # Получаем устройство по переданному id
    device = get_object_or_404(Device, id=device_id)

    # Проверка, что устройство связано с текущим пользователем
    if device.user != request.user:
        return redirect('devices')  # Перенаправить, если устройство не принадлежит пользователю

    # Генерация и обработка JSON-данных
    json_path, timestamp = generate_activity_data(
        device_name=device.device_name, device_type=device.device_type, user=request.user
    )
    success = process_activity_data(json_path, request.user, timestamp)

    device.last_import_date = datetime.now()
    device.save()

    if success:
        return redirect('devices')  # Перенаправление обратно на страницу устройств
    else:
        # Обработка ошибки синхронизации
        return redirect('devices')


@login_required
def movements_view(request):
    user = request.user
    time_range = request.GET.get('range', 'day')  # По умолчанию "день"
    now = datetime.now()

    if time_range == 'week':
        start_time = now - timedelta(days=6)  # Последние 7 дней
    else:
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)  # Начало текущих суток

    # Фильтрация данных за выбранный промежуток времени
    movements = (
        Activity.objects.filter(user=user, date__gte=start_time, date__lte=now)
        .annotate(hour=F('date__hour'))  # Добавляем час для группировки
        .values('hour')
        .annotate(distance_sum=Sum('distance'))
        .order_by('hour')
    )

    # Формируем данные для графика
    labels = []
    values = []
    if time_range == 'day':
        # Отображаем данные по часам
        for hour in range(24):
            labels.append(f"{hour}:00")
            distance = next((m['distance_sum'] for m in movements if m['hour'] == hour), 0)
            values.append(round(distance, 2))
    elif time_range == 'week':
        # Отображаем данные по дням
        for day_delta in range(7):
            day = now - timedelta(days=day_delta)
            labels.append(day.strftime('%Y-%m-%d'))
            day_distance = Activity.objects.filter(
                user=user, date__date=day.date()
            ).aggregate(Sum('distance'))['distance__sum'] or 0
            values.append(round(day_distance, 2))

    # Суммарные данные
    total_distance = round(sum(values), 2)
    progress_percentage = min((total_distance / (8 if time_range == 'day' else 56)) * 100, 100)

    # Передаем данные в шаблон
    context = {
        'labels': labels,
        'values': values,
        'time_range': time_range,
        'total_distance': total_distance,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'main/movements.html', context)


@login_required
def standups_view(request):
    user = request.user
    time_range = request.GET.get('range', 'day')  # По умолчанию "день"
    now = datetime.now()

    if time_range == 'week':
        start_time = now - timedelta(days=6)  # Последние 7 дней
    else:
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)  # Начало текущих суток

    # Фильтрация данных за выбранный промежуток времени
    standups = (
        StandUp.objects.filter(user=user, timestamp__gte=start_time, timestamp__lte=now)
        .annotate(hour=F('timestamp__hour'))  # Добавляем час для группировки
        .values('hour')
        .annotate(standups_sum=Sum('count'))
        .order_by('hour')
    )

    # Формируем данные для графика
    labels = []
    values = []
    if time_range == 'day':
        # Отображаем данные по часам
        for hour in range(24):
            labels.append(f"{hour}:00")
            count = next((s['standups_sum'] for s in standups if s['hour'] == hour), 0)
            values.append(count)
    elif time_range == 'week':
        # Отображаем данные по дням
        for day_delta in range(7):
            day = now - timedelta(days=day_delta)
            labels.append(day.strftime('%Y-%m-%d'))
            day_standups = StandUp.objects.filter(
                user=user, timestamp__date=day.date()
            ).aggregate(Sum('count'))['count__sum'] or 0
            values.append(day_standups)

    # Суммарные данные
    total_standups = sum(values)
    progress_percentage = min((total_standups / (24 if time_range == 'day' else 168)) * 100, 100)

    # Передаем данные в шаблон
    context = {
        'labels': labels,
        'values': values,
        'time_range': time_range,
        'total_standups': total_standups,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'main/standups.html', context)


@login_required
def steps_view(request):
    user = request.user
    time_range = request.GET.get('range', 'day')  # По умолчанию "день"
    now = datetime.now()

    if time_range == 'week':
        start_time = now - timedelta(days=6)  # Последние 7 дней
    else:
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)  # Начало текущих суток

    # Фильтрация данных за выбранный промежуток времени
    activities = (
        Activity.objects.filter(user=user, date__gte=start_time, date__lte=now)
        .annotate(hour=F('date__hour'))  # Добавляем час для группировки
        .values('hour')
        .annotate(steps_sum=Sum('steps'))
        .order_by('hour')
    )

    # Формируем данные для графика
    labels = []
    values = []
    if time_range == 'day':
        # Отображаем данные по часам
        for hour in range(24):
            labels.append(f"{hour}:00")
            steps = next((activity['steps_sum'] for activity in activities if activity['hour'] == hour), 0)
            values.append(steps)
    elif time_range == 'week':
        # Отображаем данные по дням
        for day_delta in range(7):
            day = now - timedelta(days=day_delta)
            labels.append(day.strftime('%Y-%m-%d'))
            day_steps = activities.filter(date__date=day.date()).aggregate(Sum('steps'))['steps__sum'] or 0
            values.append(day_steps)

    activities = Activity.objects.filter(user=user, date__gte=start_time).order_by('date')
    total_steps = sum(activity.steps for activity in activities)
    total_calories = (
        Activity.objects.filter(user=user, date__gte=start_time, date__lte=now)
        .aggregate(total_calories=Sum('calories'))['total_calories']
        or 0
    )
    progress_percentage = min((total_steps / (10000 if time_range == 'day' else 70000)) * 100, 700)
    # Передаем данные в шаблон

    context = {
        'labels': labels,
        'values': values,
        'time_range': time_range,
        'total_steps': total_steps,
        'total_calories': total_calories,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'main/steps.html', context)
