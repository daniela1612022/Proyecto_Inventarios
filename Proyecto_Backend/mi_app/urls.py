from django.urls import path
from .views import registro , listar_usuarios , editar_usuario , eliminar_usuario , login_view , logout_view

urlpatterns = [
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('api/registro/', registro, name='api_registro'),
    path('api/usuarios/', listar_usuarios, name='listar_usuarios'),
    path('api/usuarios/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('api/usuarios/<int:user_id>/eliminar/', eliminar_usuario, name='eliminar_usuario'),
]