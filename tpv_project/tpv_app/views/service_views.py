#service_views.pyfrom django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage
from datetime import datetime
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect

# Modelos
from tpv_app.models import Servicio

@login_required
def listar_servicios(request):
    """Lista todos los servicios en el sistema con paginación."""
    servicios = Servicio.objects.all().order_by('-fecha_inicio')

    # Paginación para los servicios
    paginator = Paginator(servicios, 6)  # 6 servicios por página
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    return render(request, 'servicios.html', {
        'page_obj': page_obj,'usuario': request.user
    })

@login_required
def crear_servicio(request):
    """Crea un nuevo servicio en el sistema."""
    if request.method == "POST":
        nombre = request.POST['nombre']
        estado = request.POST['estado']

        # Crear el servicio
        Servicio.objects.create(
            nombre=nombre,
            estado=estado,
            fecha_inicio=datetime.now()
        )
        messages.success(request, 'Servicio creado exitosamente.')
        return redirect('servicios')

    return render(request, 'servicios.html')

@login_required
def editar_servicio(request, id_servicio):
    """Edita los detalles de un servicio existente."""
    servicio = get_object_or_404(Servicio, pk=id_servicio)
    if request.method == "POST":
        servicio.nombre = request.POST['nombre']
        servicio.estado = request.POST['estado']
        servicio.save()
        messages.success(request, 'Servicio actualizado exitosamente.')
        return redirect('servicios')

    return render(request, 'servicios.html', {'servicio': servicio})



@login_required
def borrar_servicio(request, id_servicio):
    """Elimina un servicio del sistema."""
    try:
        servicio = Servicio.objects.get(pk=id_servicio)  # Buscar manualmente
        servicio.delete()
        messages.success(request, 'Servicio eliminado exitosamente.')
    except Servicio.DoesNotExist:
        messages.error(request, 'El servicio que intentas borrar no existe.')
    
    return redirect('servicios')  # Redirige a la lista de servicios
