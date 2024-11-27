from django import forms
from django.contrib.auth.models import User

from .models import Profile, Device


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class RegistrationForm(forms.ModelForm):
    phone = forms.CharField(max_length=20, required=False, label='Номер телефона')
    email = forms.EmailField(required=True, label='Электронная почта')
    gender = forms.ChoiceField(choices=[('M', 'Мужчина'), ('F', 'Женщина')], required=False, label='Пол')
    birthdate = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Дата рождения')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают.")


class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(max_length=20, required=True, label='Имя пользователя')
    phone = forms.CharField(max_length=20, required=False, label='Номер телефона')
    email = forms.EmailField(required=True, label='Электронная почта')
    gender = forms.ChoiceField(choices=[('M', 'Мужчина'), ('F', 'Женщина')], required=False, label='Пол')
    birthdate = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Дата рождения')

    class Meta:
        model = Profile
        fields = ['profile_image', 'gender', 'birthdate', 'phone', 'email']

    def __init__(self, *args, **kwargs):
        user = kwargs.get('user')
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['phone'].initial = user.profile.phone
            self.fields['email'].initial = user.profile.email
            self.fields['gender'].initial = user.profile.gender
            self.fields['birthdate'].initial = user.profile.birthdate

    def save(self, commit=True):
        profile = super().save(commit=False)

        user = profile.user
        user.username = self.cleaned_data['username']
        user.save()

        if commit:
            profile.save()

        return profile


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_name', 'device_type']
        labels = {
            'device_name': 'Название устройства',
            'device_type': 'Тип устройства',
        }
