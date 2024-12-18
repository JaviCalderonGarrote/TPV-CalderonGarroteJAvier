from django.contrib import admin
from .models import Usuario, Categoria, Producto, Cliente, Servicio, Venta, DetalleVenta

# Registro de los modelos de la aplicación

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre', 'apellido', 'rol', 'is_active', 'is_staff', 'fecha_creacion', 'fecha_modificacion')
    search_fields = ('username', 'nombre', 'apellido')
    list_filter = ('is_active', 'rol', 'is_staff')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id_categoria', 'nombre')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre', 'precio', 'activo', 'id_categoria')
    list_filter = ('activo', 'id_categoria')
    search_fields = ('nombre',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'nombre_empresa', 'nombre_contacto', 'telefono_contacto', 'email_contacto')
    search_fields = ('nombre_empresa', 'nombre_contacto')

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id_servicio', 'nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'cantidad_tickets', 'total_ingresos')
    list_filter = ('estado',)
    search_fields = ('nombre',)

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id_venta', 'id_usuario', 'id_cliente', 'fecha', 'total')
    search_fields = ('id_usuario__username', 'id_cliente__nombre_empresa')
    list_filter = ('fecha',)

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('id_detalle', 'id_venta', 'id_producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('id_venta__id_venta', 'id_producto__nombre')
