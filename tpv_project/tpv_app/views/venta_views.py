from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from tpv_app.models import Cliente, Producto, Venta, DetalleVenta, Servicio, Categoria
from django.core.exceptions import ValidationError
import json
from django.db.models import Sum, Count


# Vista para crear una nueva venta
@login_required
def crear_venta(request):
    if request.method == "POST":
        try:
            # Recibimos los datos del cuerpo de la solicitud
            body = json.loads(request.body)
            cliente_id = body.get('id_cliente')  # Cliente puede ser None
            producto_ids = body.get('producto_ids', [])
            cantidades = body.get('cantidades', [])

            # Validación de los productos y cantidades
            if not producto_ids or not cantidades:
                return JsonResponse({'success': False, 'error': 'Debe incluir al menos un producto y su cantidad.'}, status=400)

            if len(producto_ids) != len(cantidades):
                return JsonResponse({'success': False, 'error': 'La cantidad de productos y las cantidades no coinciden.'}, status=400)

            # Obtener el cliente si existe, sino None
            cliente = get_object_or_404(Cliente, pk=cliente_id) if cliente_id else None

            # Obtener el servicio abierto (únicamente uno activo)
            servicio = Servicio.objects.filter(estado='abierto').first()
            if not servicio:
                return JsonResponse({'success': False, 'error': 'No hay un servicio abierto.'}, status=400)

            # Usamos la instancia del servicio
            id_servicio = servicio

            # Iniciar una transacción atómica para crear la venta
            with transaction.atomic():
                venta = Venta.objects.create(
                    id_usuario=request.user,
                    id_servicio=id_servicio,  # Instancia completa de servicio
                    id_cliente=cliente,  # Si no hay cliente, se asigna None
                    total=0
                )

                # Verificar si la venta se guardó correctamente
                if not venta.id_venta:
                    raise ValueError("La venta no se guardó correctamente en la base de datos.")

                total_venta = 0
                for producto_id, cantidad in zip(producto_ids, cantidades):
                    producto = get_object_or_404(Producto, pk=producto_id)
                    cantidad = int(cantidad)

                    # Validar la cantidad
                    if cantidad <= 0:
                        raise ValidationError(f'Cantidad inválida para el producto {producto.nombre}')

                    subtotal = producto.precio * cantidad
                    total_venta += subtotal

                    # Crear los detalles de la venta
                    DetalleVenta.objects.create(
                        id_venta=venta,
                        id_producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio,
                        subtotal=subtotal
                    )

                # Actualizar el total de la venta
                venta.total = total_venta
                venta.save()

            return JsonResponse({'success': True, 'venta_id': venta.id_venta})

        except ValidationError as ve:
            return JsonResponse({'success': False, 'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    else:
        # Renderizar el formulario de venta en caso de que sea una solicitud GET
        clientes = Cliente.objects.all()
        categorias = Categoria.objects.all()
        productos = Producto.objects.filter(activo=True)  # Solo productos activos
        return render(request, 'venta.html', {'clientes': clientes, 'categorias': categorias, 'productos': productos})
# Vista para mostrar los detalles de la venta

from django.core.paginator import Paginator

@login_required
def detalle_venta(request):
    # Obtener productos más vendidos
    productos_data = (
        DetalleVenta.objects
        .filter(id_producto__activo=True)
        .values('id_producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')
    )[:6]  # Obtener los 6 productos más vendidos

    # Obtener los 5 clientes con más ventas realizadas directamente desde Venta
    clientes_data = (
        Venta.objects
        .values('id_cliente__nombre_empresa')
        .annotate(total_ventas=Count('id_venta'))  # Contamos el número de ventas por cliente
        .order_by('-total_ventas')
    )[:5]  # Obtener los 5 clientes con más ventas

    # Obtener los servicios con más ventas (por cantidad de ventas)
    servicios_data = (
        Venta.objects
        .values('id_servicio__nombre')
        .annotate(total_ventas=Count('id_venta'))  # Usamos Count para contar la cantidad de ventas
        .order_by('-total_ventas')
    )[:5]  # Obtener los 5 servicios con más ventas (por cantidad de ventas)

    # Obtener los detalles de venta para mostrar en la tabla con paginación
    detalles_venta = DetalleVenta.objects.all()
    
    # Paginación
    paginator = Paginator(detalles_venta, 6)  # 10 detalles por página
    page_number = request.GET.get('page')  # Obtener el número de página
    page_obj = paginator.get_page(page_number)

    # Preparar datos para los gráficos
    productos_labels = [item['id_producto__nombre'] for item in productos_data if item['id_producto__nombre']] if productos_data else []
    productos_values = [item['total_vendido'] for item in productos_data] if productos_data else []
    
    clientes_labels = [item['id_cliente__nombre_empresa'] for item in clientes_data if item['id_cliente__nombre_empresa']] if clientes_data else []
    clientes_values = [item['total_ventas'] for item in clientes_data if item['id_cliente__nombre_empresa']] if clientes_data else []

    servicios_labels = [item['id_servicio__nombre'] for item in servicios_data if item['id_servicio__nombre']] if servicios_data else []
    servicios_values = [item['total_ventas'] for item in servicios_data] if servicios_data else []

    # Pasar los datos a la plantilla
    return render(request, 'detalle_venta.html', {
        'productos_labels': productos_labels,
        'productos_values': productos_values,
        'clientes_labels': clientes_labels,
        'clientes_values': clientes_values,
        'servicios_labels': servicios_labels,
        'servicios_values': servicios_values,
        'page_obj': page_obj,  # Paginación de los detalles de venta
        'no_disponible_productos': not productos_data,
        'no_disponible_clientes': not clientes_data,
        'no_disponible_servicios': not servicios_data,
        'usuario': request.user
    })
