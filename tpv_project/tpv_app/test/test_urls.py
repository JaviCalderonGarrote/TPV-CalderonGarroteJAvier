from django.urls import reverse, resolve
from tpv_app.views.auth_user_views import (
    login_view, autenticar_usuario, logout_view, listar_usuarios,
    seleccionar_usuario, gestionar_usuarios, crear_usuario, editar_perfil, borrar_usuario
)
from tpv_app.views.home_views import home
from tpv_app.views.category_views import listar_categorias, crear_categoria, editar_categoria, borrar_categoria
from tpv_app.views.product_views import listar_productos, crear_producto, editar_producto, borrar_producto
from tpv_app.views.service_views import listar_servicios, crear_servicio, editar_servicio, borrar_servicio
from tpv_app.views.venta_views import crear_venta, detalle_venta


# Test para la URL de la página de inicio de sesión
def test_url_login():
    path = reverse('login')  # Genera la URL usando su nombre
    assert resolve(path).func == login_view  # Verifica que resuelve correctamente la vista `login_view`


# Test para la URL que autentica al usuario
def test_url_autenticar_usuario():
    path = reverse('autenticar_usuario')
    assert resolve(path).func == autenticar_usuario


# Test para la URL de cierre de sesión
def test_url_logout():
    path = reverse('logout')
    assert resolve(path).func == logout_view


# Test para la URL de la página principal (home)
def test_url_home():
    path = reverse('home')
    assert resolve(path).func == home


# Test para la URL que lista los usuarios
def test_url_listar_usuarios():
    path = reverse('listar_usuarios')
    assert resolve(path).func == listar_usuarios


# Test para la URL que selecciona un usuario específico por nombre
def test_url_seleccionar_usuario():
    path = reverse('seleccionar_usuario', kwargs={'username': 'testuser'})
    assert resolve(path).func == seleccionar_usuario


# Test para la URL que gestiona usuarios
def test_url_gestionar_usuarios():
    path = reverse('gestionar_usuarios')
    assert resolve(path).func == gestionar_usuarios


# Test para la URL que crea un usuario nuevo
def test_url_crear_usuario():
    path = reverse('crear_usuario')
    assert resolve(path).func == crear_usuario


# Test para la URL que permite editar el perfil del usuario autenticado
def test_url_editar_perfil():
    path = reverse('editar_perfil')
    assert resolve(path).func == editar_perfil


# Test para la URL que elimina un usuario por su ID
def test_url_borrar_usuario():
    path = reverse('borrar_usuario', kwargs={'id': 1})
    assert resolve(path).func == borrar_usuario


# Test para la URL que permite crear una venta
def test_url_crear_venta():
    path = reverse('crear_venta')
    assert resolve(path).func == crear_venta


# Test para la URL que lista todos los servicios
def test_url_listar_servicios():
    path = reverse('servicios')
    assert resolve(path).func == listar_servicios


# Test para la URL que crea un servicio nuevo
def test_url_crear_servicio():
    path = reverse('crear_servicio')
    assert resolve(path).func == crear_servicio


# Test para la URL que edita un servicio específico por su ID
def test_url_editar_servicio():
    path = reverse('editar_servicio', kwargs={'id_servicio': 1})
    assert resolve(path).func == editar_servicio


# Test para la URL que elimina un servicio por su ID
def test_url_borrar_servicio():
    path = reverse('borrar_servicio', kwargs={'id_servicio': 1})
    assert resolve(path).func == borrar_servicio


# Test para la URL que lista todas las categorías
def test_url_listar_categorias():
    path = reverse('categorias')
    assert resolve(path).func == listar_categorias


# Test para la URL que crea una categoría nueva
def test_url_crear_categoria():
    path = reverse('crear_categoria')
    assert resolve(path).func == crear_categoria


# Test para la URL que edita una categoría específica por su ID
def test_url_editar_categoria():
    path = reverse('editar_categoria', kwargs={'id_categoria': 1})
    assert resolve(path).func == editar_categoria


# Test para la URL que elimina una categoría por su ID
def test_url_borrar_categoria():
    path = reverse('borrar_categoria', kwargs={'id_categoria': 1})
    assert resolve(path).func == borrar_categoria


# Test para la URL que lista todos los productos
def test_url_listar_productos():
    path = reverse('productos')
    assert resolve(path).func == listar_productos


# Test para la URL que crea un producto nuevo
def test_url_crear_producto():
    path = reverse('crear_producto')
    assert resolve(path).func == crear_producto


# Test para la URL que edita un producto específico por su ID
def test_url_editar_producto():
    path = reverse('editar_producto', kwargs={'id_producto': 1})
    assert resolve(path).func == editar_producto


# Test para la URL que elimina un producto por su ID
def test_url_borrar_producto():
    path = reverse('borrar_producto', kwargs={'id_producto': 1})
    assert resolve(path).func == borrar_producto


# Test para la URL que muestra los detalles de una venta
def test_url_detalle_venta():
    path = reverse('detalle_venta')
    assert resolve(path).func == detalle_venta
