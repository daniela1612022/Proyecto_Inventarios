from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from mi_app.models import Profile
from .Forms.forms import RegistroForm 
from django.contrib.auth import authenticate, login , logout
import json

@csrf_exempt
def registro(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        form = RegistroForm(data)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Usuario registrado con éxito."}, status=201)
        else:
            return JsonResponse(form.errors, status=400)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)

def listar_usuarios(request):
    if request.method == 'GET':
        usuarios = User.objects.all()
        lista_usuarios = []
        for usuario in usuarios:
            lista_usuarios.append({
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "first_name": usuario.first_name,
                "phone": usuario.profile.phone,
                "role": usuario.profile.role  # Incluir el rol en la salida
            })
        return JsonResponse(lista_usuarios, safe=False)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)
    
@csrf_exempt
def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)

    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        if 'username' in data:
            usuario.username = data['username']
        if 'email' in data:
            usuario.email = data['email']
        if 'first_name' in data:
            usuario.first_name = data['first_name']
        if 'phone' in data:
            usuario.profile.phone = data['phone']
        if 'role' in data:
            usuario.profile.role = data['role']

        usuario.save()
        usuario.profile.save()

        return JsonResponse({"message": "Usuario actualizado con éxito."}, status=200)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)

@csrf_exempt
def eliminar_usuario(request, user_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "No estás autenticado."}, status=401)

    usuario = get_object_or_404(User, id=user_id)

    if request.method == 'DELETE':
        try:
            perfil = request.user.profile
        except Profile.DoesNotExist:
            return JsonResponse({"error": "El perfil del usuario no existe."}, status=400)

        if perfil.role != 'admin':
            return JsonResponse({"error": "No tienes permisos para realizar esta acción."}, status=403)

        usuario.delete()
        return JsonResponse({"message": "Usuario eliminado con éxito."}, status=200)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Inicio de sesión exitoso."}, status=200)
            else:
                return JsonResponse({"error": "Correo o contraseña incorrectos."}, status=400)
        except User.DoesNotExist:
            return JsonResponse({"error": "Correo o contraseña incorrectos."}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)

@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({"message": "Sesión cerrada con éxito."}, status=200)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)