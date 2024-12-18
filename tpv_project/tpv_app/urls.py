from django.contrib import admin
from django.urls import path

# Importación de vistas desde los módulos correspondientes
from tpv_app.views.auth_user_views import editar_perfil,borrar_usuario, login_view, autenticar_usuario, logout_view, listar_usuarios, seleccionar_usuario, gestionar_usuarios, crear_usuario
from tpv_app.views.home_views import home
from tpv_app.views.category_views import listar_categorias, crear_categoria, editar_categoria, borrar_categoria
from tpv_app.views.product_views import listar_productos, crear_producto, editar_producto, borrar_producto
from tpv_app.views.service_views import listar_servicios, crear_servicio, editar_servicio, borrar_servicio
from tpv_app.views.venta_views import crear_venta, detalle_venta 
from tpv_app.views.clientes_views import listar_clientes , crear_cliente , editar_cliente , borrar_cliente

from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación
    path('login', login_view, name='login'),
    path('autenticar/', autenticar_usuario, name='autenticar_usuario'),
    path('logout/', logout_view, name='logout'),

    # Home
    path('home/', home, name='home'),

    # Usuarios
    path('usuarios/', listar_usuarios, name='listar_usuarios'),  
    path('usuarios/seleccionar/<str:username>/', seleccionar_usuario, name='seleccionar_usuario'),
    path('usuarios/gestionar/', gestionar_usuarios, name='gestionar_usuarios'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),  
    path('editar_perfil/', editar_perfil, name='editar_perfil'),
    path('usuario/<int:id>/borrar/', borrar_usuario, name='borrar_usuario'),


  
    # Servicios
    path('servicios/', listar_servicios, name='servicios'),
    path('servicios/crear/', crear_servicio, name='crear_servicio'),
    path('servicios/editar/<int:id_servicio>/', editar_servicio, name='editar_servicio'),
    path('servicios/borrar/<int:id_servicio>/', borrar_servicio, name='borrar_servicio'),

    # Categorías
    path('categorias/', listar_categorias, name='categorias'),
    path('categorias/crear/', crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:id_categoria>/', editar_categoria, name='editar_categoria'),
    path('categorias/borrar/<int:id_categoria>/', borrar_categoria, name='borrar_categoria'),

    # Productos
    path('productos/', listar_productos, name='productos'),
    path('productos/crear/', crear_producto, name='crear_producto'),
    path('productos/editar/<int:id_producto>/', editar_producto, name='editar_producto'),
    path('productos/borrar/<int:id_producto>/', borrar_producto, name='borrar_producto'),

  # URLs de clientes
  path('clientes/', listar_clientes, name='clientes'),
  path('clientes/crear/', crear_cliente, name='crear_cliente'),
  path('clientes/editar/<int:id_cliente>/', editar_cliente, name='editar_cliente'),
  path('clientes/borrar/<int:id_cliente>/', borrar_cliente, name='borrar_cliente'),

  # Ventas
    path('ventas/', crear_venta, name='crear_venta'),
    path('detalle_venta/', detalle_venta, name='detalle_venta'),


]