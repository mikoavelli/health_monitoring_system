from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    gender = models.CharField(max_length=1, null=False)
    birthdate = models.DateField(null=False)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=False)
    profile_image = models.ImageField(upload_to='profile/', null=True, blank=True, default='profile/default.jpg')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Activity(models.Model):
    calories = models.IntegerField(null=False)
    date = models.DateTimeField(null=False)
    distance = models.FloatField(null=False)
    steps = models.IntegerField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = 'Действие'
        verbose_name_plural = 'Действия'

        unique_together = ('user', 'date')


class Device(models.Model):
    device_name = models.CharField(max_length=50, null=False)
    device_type = models.CharField(max_length=50, null=False)
    last_import_date = models.DateTimeField(auto_now_add=True, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return (f"Устройство: {self.device_name}\n"
                f"Время последней синхронизации: {self.last_import_date}\n")

    class Meta:
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'


class StandUp(models.Model):
    count = models.IntegerField(null=False)
    timestamp = models.DateTimeField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = 'Вставание'
        verbose_name_plural = 'Вставания'


class Movement(models.Model):
    count = models.IntegerField(null=False)
    timestamp = models.DateTimeField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = 'Движение'
        verbose_name_plural = 'Движения'
