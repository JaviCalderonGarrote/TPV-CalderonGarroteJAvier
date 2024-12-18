from django.shortcuts import render, get_object_or_404, redirect  # Manejo de vistas y objetos
from django.contrib.auth.decorators import login_required  # Protección de vistas con autenticación
from tpv_app.models import Usuario, Servicio

@login_required
def home(request):
    """Página principal."""
    # Verifica si el usuario está autenticado usando request.user
    if not request.user.is_authenticated:  # Si el usuario no está autenticado, redirige al login
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=request.user.id)  # Obtiene el usuario actual
    servicio_abierto = Servicio.objects.filter(estado='abierto').exists()  # Verifica si hay un servicio abierto
    return render(request, 'home.html', {'usuario': usuario, 'servicio_abierto': servicio_abierto})
