from django.test import TestCase
from django.urls import reverse
from tpv_app.models import Producto, Categoria, Usuario
from django.contrib.messages import get_messages

class ProductoViewsTestCase(TestCase):

    def setUp(self):
        # Crear un usuario usando el modelo personalizado Usuario
        self.user = Usuario.objects.create_user(username='testuser', nombre='Test', apellido='User', password='testpassword')
        self.categoria = Categoria.objects.create(nombre='Electrónica', activo=True)
        self.producto = Producto.objects.create(
            nombre='Laptop',
            precio=1000.00,
            id_categoria=self.categoria,
            activo=True
        )

    def test_listar_productos(self):
        """Test para verificar la vista que lista los productos con paginación."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('productos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')  # Verifica que el producto aparece
        self.assertContains(response, 'Electrónica')  # Verifica que la categoría aparece

    def test_crear_producto(self):
        """Test para verificar que un producto puede ser creado correctamente."""
        self.client.login(username='testuser', password='testpassword')

        # Datos para crear un producto
        data = {
            'nombre': 'Smartphone',
            'precio': '600.00',
            'categoria': self.categoria.id_categoria
        }

        # Realizamos el post para crear el producto
        response = self.client.post(reverse('crear_producto'), data)

        # Verificamos que el producto se haya creado correctamente
        self.assertEqual(response.status_code, 302)  # Redirige a la lista de productos
        self.assertRedirects(response, reverse('productos'))
        self.assertTrue(Producto.objects.filter(nombre='Smartphone').exists())

        # Verificamos el mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Producto creado exitosamente.')

    def test_borrar_producto(self):
        """Test para verificar que un producto se puede eliminar correctamente (borrado lógico)."""
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('borrar_producto', kwargs={'id_producto': self.producto.id_producto}))
        
        # Verificamos que el producto ahora está inactivo
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.activo)

        # Verificamos que la redirección y mensaje de éxito
        self.assertRedirects(response, reverse('productos'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Producto eliminado exitosamente.')

    def test_editar_producto(self):
        """Test para verificar que un producto se puede editar correctamente."""
        self.client.login(username='testuser', password='testpassword')

        # Datos para editar el producto
        data = {
            'nombre': 'Laptop Pro',
            'precio': '1200.00',
            'categoria': self.categoria.id_categoria
        }

        response = self.client.post(reverse('editar_producto', kwargs={'id_producto': self.producto.id_producto}), data)

        # Verificamos que el producto se ha editado correctamente
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Laptop Pro')
        self.assertEqual(self.producto.precio, 1200.00)

        # Verificamos la redirección y mensaje de éxito
        self.assertRedirects(response, reverse('productos'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Producto actualizado exitosamente.')
