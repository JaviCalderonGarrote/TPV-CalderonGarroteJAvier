import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from django.test import Client
from tpv_app.models import Usuario
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator  # Asegúrate de que esta línea esté presente
from django.contrib import admin
from django.urls import path

# === Test Cases ===

@pytest.fixture
def crear_usuario_fixture():
    """Crea un usuario para las pruebas"""
    usuario = Usuario.objects.create_user(
        username="testuser", password="testpassword", nombre="Test", apellido="User"
    )
    return usuario

@pytest.fixture
def cliente():
    """Crea un cliente de prueba"""
    client = Client()
    return client

@pytest.mark.django_db
def test_editar_perfil_get(cliente, crear_usuario_fixture):
    """Prueba la vista GET para editar perfil"""
    usuario = crear_usuario_fixture
    cliente.login(username='testuser', password='testpassword')
    response = cliente.get(reverse('editar_perfil'))
    
    assert response.status_code == 200  # La página debe cargar correctamente
    assert 'usuario' in response.context  # El contexto debe contener el usuario
    assert response.context['usuario'] == usuario  # El usuario en contexto debe ser el usuario actual

@pytest.mark.django_db
def test_editar_perfil_post(cliente, crear_usuario_fixture):
    """Prueba la vista POST para editar perfil"""
    usuario = crear_usuario_fixture
    cliente.login(username='testuser', password='testpassword')
    response = cliente.post(reverse('editar_perfil'), {
        'username': 'newusername',
        'nombre': 'NewName',
        'apellido': 'NewLastName',
    })

    usuario.refresh_from_db()  # Recargamos el objeto de la base de datos para verificar cambios
    assert response.status_code == 302  # Redirige después de editar
    assert usuario.username == 'newusername'
    assert usuario.nombre == 'NewName'
    assert usuario.apellido == 'NewLastName'


@pytest.mark.django_db
def test_editar_perfil_post_contra_no_coincide(cliente, crear_usuario_fixture):
    """Prueba la vista POST para editar perfil con contraseñas no coincidentes"""
    usuario = crear_usuario_fixture
    cliente.login(username='testuser', password='testpassword')
    response = cliente.post(reverse('editar_perfil'), {
        'username': 'newusername',
        'nombre': 'NewName',
        'apellido': 'NewLastName',
        'password': '1234',
        'confirm_password': '12345',  # Contraseñas no coinciden
    })

    messages = list(get_messages(response.wsgi_request))  # Capturamos los mensajes
    assert len(messages) == 1
    assert str(messages[0]) == "Las contraseñas no coinciden."

@pytest.mark.django_db
def test_login_view_post_success(cliente, crear_usuario_fixture):
    """Prueba la vista POST para login con datos correctos"""
    usuario = crear_usuario_fixture
    response = cliente.post(reverse('login'), {
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 302  # Redirige al home después de login exitoso
    assert response.url == reverse('home')  # La redirección debe ser a la página principal
    assert '_auth_user_id' in cliente.session  # La sesión debe contener el ID de usuario autenticado


@pytest.mark.django_db
def test_login_view_post_failure(cliente, crear_usuario_fixture):
    """Prueba la vista POST para login con datos incorrectos"""
    response = cliente.post(reverse('login'), {
        'username': 'wronguser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 200  # Debe retornar al formulario de login
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == "Usuario o contraseña incorrectos."

@pytest.mark.django_db
def test_logout_view(cliente, crear_usuario_fixture):
    """Prueba la vista de logout"""
    usuario = crear_usuario_fixture
    cliente.login(username='testuser', password='testpassword')
    response = cliente.get(reverse('logout'))
    
    assert response.status_code == 302  # Debe redirigir después de hacer logout
    assert response.url == reverse('login')  # Redirige a la página de login
    assert '_auth_user_id' not in cliente.session  # El usuario debe ser eliminado de la sesión


@pytest.mark.django_db
def test_listar_usuarios(cliente, crear_usuario_fixture):
    """Prueba la vista para listar usuarios"""
    usuario = crear_usuario_fixture
    cliente.login(username='testuser', password='testpassword')

    # Creamos más usuarios para comprobar la paginación
    Usuario.objects.create_user(username="testuser2", password="testpassword", nombre="User", apellido="Two")
    
    response = cliente.get(reverse('listar_usuarios'))
    assert response.status_code == 200  # La página debe cargar correctamente
    assert 'page_obj' in response.context  # El contexto debe contener la paginación
    assert response.context['page_obj'].paginator.count > 1  # Debe haber más de un usuario listado


@pytest.mark.django_db
def test_crear_usuario_post(cliente):
    """Prueba la creación de un nuevo usuario"""
    cliente.login(username='testuser', password='testpassword')

    response = cliente.post(reverse('crear_usuario'), {
        'username': 'newuser',
        'nombre': 'New',
        'apellido': 'User',
        'password': 'newpassword',
        'confirm_password': 'newpassword',
        'rol': 'Vendedor',
    })

    # Verificamos que el usuario haya sido creado correctamente
    new_user = Usuario.objects.get(username='newuser')
    assert new_user.username == 'newuser'
    assert response.status_code == 302  # Redirige después de la creación
    assert response.url == reverse('listar_usuarios')  # Redirige a la página de usuarios


@pytest.mark.django_db
def test_borrar_usuario(cliente, crear_usuario_fixture):
    """Prueba la eliminación de un usuario"""
    usuario = crear_usuario_fixture
    cliente.login(username='testuser', password='testpassword')

    response = cliente.post(reverse('borrar_usuario', args=[usuario.id]))
    assert response.status_code == 302  # Debe redirigir después de la eliminación
    with pytest.raises(Usuario.DoesNotExist):
        Usuario.objects.get(id=usuario.id)  # El usuario debe ser eliminado de la base de datos

@pytest.mark.django_db
def test_seleccionar_usuario(cliente, crear_usuario_fixture):
    """Prueba la selección de un usuario"""
    usuario = crear_usuario_fixture
    cliente.login(username='testuser', password='testpassword')

    response = cliente.get(reverse('seleccionar_usuario', args=[usuario.username]))
    assert response.status_code == 302  # Debe redirigir después de seleccionar el usuario
    assert cliente.session['usuario_id'] == usuario.id  # El ID del usuario debe estar en la sesión


# === Views ===

# Vista para editar perfil
def editar_perfil(request):
    if request.method == 'POST':
        username = request.POST['username']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        usuario = request.user
        usuario.username = username
        usuario.nombre = nombre
        usuario.apellido = apellido

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password:
            if password != confirm_password:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect('editar_perfil')

            if not password.isdigit() or len(password) < 4:
                messages.error(request, "La contraseña debe ser numérica y tener al menos 4 dígitos.")
                return redirect('editar_perfil')

            usuario.set_password(password)

        usuario.save()

        if password:
            update_session_auth_hash(request, usuario)

        messages.success(request, "Perfil actualizado exitosamente.")
        return redirect('editar_perfil')

    else:
        return render(request, 'editar_perfil.html', {'usuario': request.user})

# Vista de login
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            messages.success(request, 'Inicio de sesión exitoso.')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')

# Vista de logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('login')

# Vista para listar usuarios
@login_required
def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    paginator = Paginator(usuarios, 6)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except:
        page_obj = paginator.get_page(1)

    return render(request, 'listar_usuarios', {'page_obj': page_obj})

# Vista para crear un usuario
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        rol = request.POST.get('rol')

        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect('crear_usuario')

        usuario = Usuario.objects.create_user(username=username, password=password, nombre=nombre, apellido=apellido)
        usuario.rol = rol
        usuario.save()
        messages.success(request, "Usuario creado exitosamente.")
        return redirect('listar_usuarios')
    
    return render(request, 'crear_usuario.html')

