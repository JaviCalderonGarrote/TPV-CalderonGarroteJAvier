from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tpv_app.models import Cliente

@login_required
def listar_clientes(request):
    """Lista todos los clientes con paginación."""
    clientes = Cliente.objects.all()

    # Paginación para los clientes
    paginator = Paginator(clientes, 6)  # 6 clientes por página
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    return render(request, 'clientes.html', {
        'page_obj': page_obj,
        'usuario': request.user
    })

@login_required
def crear_cliente(request):
    """Crea o edita un cliente."""
    if request.method == "POST":
        nombre_empresa = request.POST['nombre_empresa']
        telefono_contacto = request.POST['telefono_contacto']
        email_contacto = request.POST.get('email_contacto', '')

        # Si hay id_cliente, estamos editando el cliente existente
        id_cliente = request.POST.get('id_cliente')
        if id_cliente:
            cliente = get_object_or_404(Cliente, pk=id_cliente)
            cliente.nombre_empresa = nombre_empresa
            cliente.telefono_contacto = telefono_contacto
            cliente.email_contacto = email_contacto
            cliente.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
        else:
            # Si no hay id, estamos creando un cliente nuevo
            Cliente.objects.create(
                nombre_empresa=nombre_empresa,
                telefono_contacto=telefono_contacto,
                email_contacto=email_contacto
            )
            messages.success(request, 'Cliente creado exitosamente.')

        return redirect('clientes')

    return render(request, 'clientes.html')

@login_required
def borrar_cliente(request, id_cliente):
    """Realiza un borrado lógico de un cliente."""
    cliente = get_object_or_404(Cliente, pk=id_cliente)
    cliente.delete()  # Eliminación lógica en este caso
    messages.success(request, 'Cliente eliminado exitosamente.')
    return redirect('clientes')

@login_required
def editar_cliente(request, id_cliente):
    """Edita un cliente existente."""
    cliente = get_object_or_404(Cliente, pk=id_cliente)
    if request.method == "POST":
        cliente.nombre_empresa = request.POST['nombre_empresa']
        cliente.telefono_contacto = request.POST['telefono_contacto']
        cliente.email_contacto = request.POST.get('email_contacto', '')
        cliente.save()
        messages.success(request, 'Cliente actualizado exitosamente.')
        return redirect('clientes')

    return render(request, 'clientes.html', {'cliente': cliente})
