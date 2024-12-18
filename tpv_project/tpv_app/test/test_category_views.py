from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from tpv_app.models import Categoria
from django.contrib.messages import get_messages


class CategoriaViewsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Configuración inicial para las pruebas, crea un usuario y algunas categorías."""
        # Crear un usuario
        cls.user = get_user_model().objects.create_user(
            username='testuser',
            nombre='Test',
            apellido='User',
            password='testpassword'
        )

        # Crear categorías de ejemplo
        Categoria.objects.create(nombre="Categoria 1")
        Categoria.objects.create(nombre="Categoria 2")
        Categoria.objects.create(nombre="Categoria 3")

    def setUp(self):
        """Método de configuración para cada prueba de la clase, como el login."""
        # Iniciar sesión con el usuario creado
        self.client.login(username='testuser', password='testpassword')

    # ------------------------------------
    # Test para listar las categorías
    def test_listar_categorias(self):
        """Verifica que la vista 'listar_categorias' muestre correctamente las categorías y la paginación."""
        url = reverse('categorias')  # URL para listar las categorías
        response = self.client.get(url)

        # Verificar que la respuesta sea exitosa (status 200)
        self.assertEqual(response.status_code, 200)

        # Verificar que las categorías creadas estén en la respuesta
        self.assertContains(response, 'Categoria 1')
        self.assertContains(response, 'Categoria 2')

        # Verificar que la paginación está funcionando
        paginator = response.context['page_obj']
        total_items = paginator.paginator.count
        page_count = total_items // 8 + (1 if total_items % 8 else 0)
        self.assertEqual(len(paginator), 3)  # Verificar que hay 3 categorías por página

    # ------------------------------------
    # Test para la creación de una categoría
    def test_crear_categoria(self):
        """Test para la creación de una nueva categoría."""
        url = reverse('crear_categoria')
        data = {'nombre': 'Categoria Nueva'}
        response = self.client.post(url, data)

        # Verificar que la categoría ha sido creada
        self.assertEqual(response.status_code, 302)  # Redirige a la lista de categorías
        self.assertTrue(Categoria.objects.filter(nombre='Categoria Nueva').exists())

    # ------------------------------------
    # Test para editar una categoría existente
    def test_editar_categoria(self):
        """Test para editar una categoría existente."""
        categoria = Categoria.objects.create(nombre="Categoria a Editar")
        url = reverse('editar_categoria', args=[categoria.id_categoria])
        data = {'nombre': 'Categoria 1 updated'}
        response = self.client.post(url, data)

        # Verificar que la categoría fue actualizada
        self.assertEqual(response.status_code, 302)  # Redirige a la lista de categorías
        categoria.refresh_from_db()
        self.assertEqual(categoria.nombre, 'Categoria 1 updated')

    # ------------------------------------
    # Test para editar una categoría con datos inválidos
    def test_editar_categoria_invalid(self):
        """Test para editar una categoría y proporcionar datos inválidos."""
        categoria = Categoria.objects.create(nombre="Categoria a Editar")
        url = reverse('editar_categoria', args=[categoria.id_categoria])
        data = {'nombre': ''}  # Nombre vacío
        response = self.client.post(url, data)

        # Verificar que la respuesta es un redireccionamiento, lo que indica que la categoría no fue actualizada
        self.assertEqual(response.status_code, 302)  # Redirige a la lista de categorías

        # Verificar que la categoría no fue modificada
        categoria.refresh_from_db()  # Asegurarse de que la categoría no fue modificada
        self.assertEqual(categoria.nombre, 'Categoria a Editar')  # Nombre original

    # ------------------------------------
    # Test para borrar (de manera lógica) una categoría
    def test_borrar_categoria(self):
        """Test para borrar (de manera lógica) una categoría."""
        categoria = Categoria.objects.create(nombre="Categoria a Borrar")
        url = reverse('borrar_categoria', args=[categoria.id_categoria])
        response = self.client.get(url)

        # Verificar que la categoría se ha marcado como inactiva
        self.assertEqual(response.status_code, 302)  # Redirige a la lista de categorías
        categoria.refresh_from_db()
        self.assertFalse(categoria.activo)  # La categoría debe estar inactiva

    # ------------------------------------
    # Test para no permitir la creación de una categoría sin nombre
    def test_no_permitir_crear_categoria_sin_nombre(self):
        """Verifica que al intentar crear una categoría sin nombre se genera un mensaje de error."""
        url = reverse('crear_categoria')
        response = self.client.post(url, {'nombre': ''})

        # Verificar que se muestra un mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'El nombre de la categoría es obligatorio.')
        self.assertEqual(response.status_code, 200)  # Se debe volver a la vista sin redirigir

    # ------------------------------------
    # Test para la creación de una categoría sin nombre (debería fallar)
    def test_crear_categoria_sin_nombre(self):
        """Test para la creación de una categoría sin nombre (debería fallar)."""
        url = reverse('crear_categoria')
        data = {'nombre': ''}  # Nombre vacío
        response = self.client.post(url, data)

        # Verificar que la respuesta es correcta (debería mantenerse en la misma página)
        self.assertEqual(response.status_code, 200)

        # Verificar que el mensaje de error está presente
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'El nombre de la categoría es obligatorio.')
