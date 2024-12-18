#product_views.py
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from tpv_app.models import Producto, Categoria

@login_required
def listar_productos(request):
    """Lista todos los productos activos y sus categorías con paginación."""
    productos = Producto.objects.filter(activo=True)
    categorias = Categoria.objects.filter(activo=True)  # Solo categorías activas

    # Paginación para los productos
    paginator = Paginator(productos, 6)  # 6 productos por página
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)

    return render(request, 'productos.html', {
        'page_obj': page_obj,
        'categorias': categorias,'usuario': request.user
    })

@login_required
def crear_producto(request):
    """Crea o edita un producto en el sistema."""
    if request.method == "POST":
        nombre = request.POST['nombre']
        precio = request.POST['precio']
        categoria_id = request.POST['categoria']
        categoria = get_object_or_404(Categoria, pk=categoria_id)

        # Si hay un id_producto, estamos editando el producto existente
        id_producto = request.POST.get('id_producto')
        if id_producto:
            producto = get_object_or_404(Producto, pk=id_producto)
            producto.nombre = nombre
            producto.precio = precio
            producto.id_categoria = categoria  # Asociamos la categoría
            producto.save()
            messages.success(request, 'Producto actualizado exitosamente.')
        else:
            # Si no hay id, estamos creando un producto nuevo
            Producto.objects.create(
                nombre=nombre,
                precio=precio,
                id_categoria=categoria  # Asociamos la categoría
            )
            messages.success(request, 'Producto creado exitosamente.')

        return redirect('productos')  # Cambiar a 'productos'

    # Si es GET, preparamos el formulario para crear un producto
    categorias = Categoria.objects.filter(activo=True)  # Solo categorías activas
    return render(request, 'productos.html', {'categorias': categorias})

@login_required
def borrar_producto(request, id_producto):
    """Realiza un borrado lógico de un producto."""
    producto = get_object_or_404(Producto, pk=id_producto)
    producto.activo = False
    producto.save()
    messages.success(request, 'Producto eliminado exitosamente.')
    return redirect('productos')  # Cambiar a 'productos'

@login_required
def editar_producto(request, id_producto):
    """Edita un producto existente."""
    producto = get_object_or_404(Producto, pk=id_producto)
    if request.method == "POST":
        producto.nombre = request.POST['nombre']
        producto.precio = request.POST['precio']
        producto.id_categoria = get_object_or_404(Categoria, pk=request.POST['categoria'])
        producto.save()
        messages.success(request, 'Producto actualizado exitosamente.')
        return redirect('productos')  # Cambiar a 'productos'

    categorias = Categoria.objects.filter(activo=True)  # Solo categorías activas
    return render(request, 'productos.html', {
        'producto': producto,
        'categorias': categorias
    })
