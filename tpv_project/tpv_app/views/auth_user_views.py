from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from tpv_app.models import Usuario
from django.core.paginator import Paginator  # Asegúrate de que esta línea esté presente


# === Autenticación ===

def editar_perfil(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.POST['username']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        
        # Obtener el usuario actual
        usuario = request.user

        # Guardar los otros cambios en el perfil (sin importar la contraseña)
        usuario.username = username
        usuario.nombre = nombre
        usuario.apellido = apellido

        # Si se ha introducido una nueva contraseña
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validación de contraseñas solo si se ha ingresado alguna
        if password:
            if password != confirm_password:
                messages.error(request, "Las contraseñas no coinciden.")
                return redirect('editar_perfil')  # Redirigir al formulario para corregir

            # Verificar que la contraseña sea numérica y tenga al menos 4 dígitos
            if not password.isdigit() or len(password) < 4:
                messages.error(request, "La contraseña debe ser numérica y tener al menos 4 dígitos.")
                return redirect('editar_perfil')

            # Actualizar la contraseña
            usuario.set_password(password)
        
        # Guardar los cambios del perfil en la base de datos
        usuario.save()

        # Si la contraseña fue cambiada, actualizar la sesión para evitar que se cierre
        if password:
            update_session_auth_hash(request, usuario)  # Para que no se cierre la sesión del usuario

        messages.success(request, "Perfil actualizado exitosamente.")
        return redirect('editar_perfil')  # Redirigir de nuevo al formulario después de guardar los cambios

    else:
        # Si el método es GET, mostrar el formulario
        return render(request, 'editar_perfil.html', {'usuario': request.user})


def login_view(request):
    """Muestra el formulario de login."""
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
    
    # Obtener los usuarios para mostrar en el login
    usuarios = Usuario.objects.all()  # Cambiado a Usuario en lugar de User
    return render(request, 'login.html', {'usuarios': usuarios})


def logout_view(request):
    """Cierra la sesión del usuario."""
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('login')


def autenticar_usuario(request):
    """Autentica a un usuario con nombre de usuario y contraseña."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autenticar usuario
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)  # Inicia sesión
            request.session['usuario_id'] = usuario.id  # Guarda el usuario en la sesión
            return redirect('home')  # Redirige al home en caso de éxito
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('login')  # Redirige a login si falla

    return redirect('login')  # Si no es POST, redirige a login


# === Gestión de Usuarios ===

@login_required
def listar_usuarios(request):
    """Lista todos los usuarios registrados."""
    
    # Obtener todos los usuarios
    usuarios = Usuario.objects.all()

    # Paginación para los usuarios
    paginator = Paginator(usuarios, 6)  # 6 usuarios por página
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    return render(request, 'usuarios.html', {'page_obj': page_obj, 'usuario': request.user })  # Cambiado a 'usuarios.html'


@login_required
def editar_usuario(request, usuario_id):
    """Edita los detalles de un usuario."""
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        usuario.username = request.POST.get('username')
        usuario.nombre = request.POST.get('nombre')
        usuario.apellido = request.POST.get('apellido')
        usuario.rol = request.POST.get('rol')
        usuario.save()
        messages.success(request, f'Usuario {usuario.username} actualizado exitosamente.')
        return redirect('listar_usuarios')
    return render(request, 'usuario.html', {'usuario': usuario})


def crear_usuario(request):
    if request.method == 'POST':
        id_usuario = request.POST.get('id_usuario', None)
        username = request.POST.get('username')
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        rol = request.POST.get('rol')

        if id_usuario:  # Editar usuario
            usuario = get_object_or_404(Usuario, id=id_usuario)
            usuario.username = username
            usuario.nombre = nombre  # Corregido: Usar el campo `nombre` del modelo
            usuario.apellido = apellido  # Corregido: Usar el campo `apellido` del modelo
            usuario.rol = rol  # Asignar el rol
            usuario.save()
            messages.success(request, 'Usuario actualizado correctamente.')
        else:  # Crear usuario
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password == confirm_password:
                # Llamada corregida a `create_user`
                usuario = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    nombre=nombre,  # Obligatorio según `create_user`
                    apellido=apellido,  # Obligatorio según `create_user`
                    rol=rol
                )
                messages.success(request, 'Usuario creado correctamente.')
            else:
                messages.error(request, 'Las contraseñas no coinciden.')

        return redirect('listar_usuarios')  # Redirigir a la página de usuarios después de crear o editar


def borrar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    usuario.delete()
    messages.success(request, 'Usuario eliminado correctamente.')
    return redirect('listar_usuarios')

@login_required
def gestionar_usuarios(request):
    """Interfaz para gestionar usuarios."""
    usuarios = Usuario.objects.all()  # Obtener todos los usuarios
    paginator = Paginator(usuarios, 10)  # Paginación: 10 usuarios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'usuarios.html', {'page_obj': page_obj})  # Cambiado a 'usuarios.html'


@login_required
def seleccionar_usuario(request, username):
    """Selecciona un usuario y lo guarda en la sesión."""
    usuario = get_object_or_404(Usuario, username=username)
    request.session['usuario_id'] = usuario.id
    messages.success(request, f'Usuario {usuario.username} seleccionado.')
    return redirect('home')

