from django import forms
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from ..models import Profile
from django.utils.html import format_html

def enviar_correo_bienvenida(user):
    subject = '🎉 ¡Bienvenido a Smart Track! 🎉'
    message = format_html(
        """
        <h2 style="color: #2E86C1;">🎉 ¡Bienvenido a <strong>Smart Track</strong>! 🎉</h2>
        <p>Hola {first_name},</p>
        <p>Gracias por registrarte en <strong>Smart Track</strong>, la mejor plataforma de gestión de inventarios y chatbot a tu medida. 🌟</p>
        <p>Estamos emocionados de que te unas a nosotros y estamos seguros de que encontrarás nuestras herramientas increíblemente útiles para optimizar tus procesos.</p>
        <img src="https://img.freepik.com/free-psd/3d-rendering-business-goal-concept_23-2149576395.jpg?t=st=1724203963~exp=1724207563~hmac=d5f876062600c89d04a644c37d5455fb22eb902b4a9ae5e6a4e183f7f6bab7cc&w=1380" alt="Smart Track" style="width:100%;max-width:600px;margin-top:20px;">
        <p style="margin-top:20px;">🚀 ¡Vamos a llevar tu gestión de inventarios al siguiente nivel!</p>
        <p>Si tienes alguna pregunta, no dudes en contactarnos. 📩</p>
        <p>Saludos,</p>
        <p>El equipo de Smart Track</p>
        """,
        first_name=user.first_name
    )
    from_email = 'danispc389@gmail.com'
    recipient_list = [user.email]

    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
            html_message=message  # Importante: Esto indica que el mensaje es en HTML
        )
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requerido. Introduce una dirección de correo válida.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Requerido. Introduce tu nombre.')
    phone = forms.CharField(max_length=10, required=True, help_text='Requerido. Introduce un número de teléfono válido.')
    password1 = forms.CharField(label="Contraseña", strip=False, required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmar Contraseña", strip=False, required=True, widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'phone', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("El número de teléfono debe tener exactamente 10 dígitos.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con este correo electrónico.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super(RegistroForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
            profile = Profile.objects.create(user=user, phone=self.cleaned_data['phone'], role='worker')
            profile.save()

            # Enviar correo de bienvenida
            enviar_correo_bienvenida(user)

        return user

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, help_text='Introduce tu correo electrónico.')
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text='Introduce tu contraseña.')

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError("Correo o contraseña incorrectos.")
            self.cleaned_data['user'] = user
        return self.cleaned_data