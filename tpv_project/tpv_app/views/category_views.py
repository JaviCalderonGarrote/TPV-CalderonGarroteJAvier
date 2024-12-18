from django.shortcuts import render, get_object_or_404, redirect  # Para manejo de vistas y objetos
from django.contrib.auth.decorators import login_required  # Para proteger las vistas con autenticación
from django.core.paginator import Paginator, EmptyPage  # Para la paginación
from django.contrib import messages  # Para mensajes en las vistas
from tpv_app.models import Categoria  # Modelo utilizado en las vistas

# === Categorías ===
# Gestión de categorías de productos o servicios.

@login_required
def listar_categorias(request):
    """Lista todas las categorías activas con paginación."""
    categorias = Categoria.objects.filter(activo=True)

    # Paginación para las categorías
    paginator = Paginator(categorias, 8)  # 8 categorías por página
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    return render(request, 'categorias.html', {
        'page_obj': page_obj ,'usuario': request.user
    })

@login_required
def crear_categoria(request):
    """Crea una nueva categoría."""
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        
        if not nombre:
            # Si el nombre no está presente, muestra un mensaje de error
            messages.error(request, 'El nombre de la categoría es obligatorio.')
            return render(request, 'categorias.html', {'nombre': nombre})  # Pasar 'nombre' para que se vea en el formulario
            
        # Crear la nueva categoría
        Categoria.objects.create(nombre=nombre)
        
        # Mensaje de éxito
        messages.success(request, 'Categoría creada exitosamente.')
        return redirect('categorias')
    
    return render(request, 'categorias.html')

@login_required
def borrar_categoria(request, id_categoria):
    """Realiza un borrado lógico de una categoría."""
    categoria = get_object_or_404(Categoria, pk=id_categoria)
    categoria.activo = False
    categoria.save()

    # Mensaje de éxito
    messages.success(request, 'Categoría eliminada exitosamente.')
    return redirect('categorias')

@login_required
def editar_categoria(request, id_categoria):
    """Edita los detalles de una categoría existente."""
    categoria = get_object_or_404(Categoria, pk=id_categoria)

    if request.method == "POST":
        nombre = request.POST.get('nombre')
        
        if not nombre:  # Si el nombre está vacío, muestra un mensaje de error
            messages.error(request, 'El nombre de la categoría es obligatorio.')
            return redirect('editar_categoria', id_categoria=categoria.id_categoria)  # Redirige al formulario de edición

        # Si el nombre es válido, actualiza la categoría
        categoria.nombre = nombre
        categoria.save()

        # Mensaje de éxito
        messages.success(request, 'Categoría actualizada correctamente.')
        return redirect('categorias')  # Redirige a la lista de categorías

    return render(request, 'categorias.html', {'categoria': categoria})
