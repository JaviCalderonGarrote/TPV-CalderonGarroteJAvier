from django.test import TestCase
from django.urls import reverse
from tpv_app.models import Cliente, Usuario
from django.contrib.messages import get_messages

class ClienteViewsTestCase(TestCase):

    def setUp(self):
        # Crear un usuario usando el modelo personalizado Usuario
        self.user = Usuario.objects.create_user(username='testuser', nombre='Test', apellido='User', password='testpassword')
        self.cliente = Cliente.objects.create(
            nombre_empresa='Empresa de Prueba',
            telefono_contacto='123456789',
            email_contacto='prueba@empresa.com',
            nif_cif='12345678A'
        )

    def test_listar_clientes(self):
        """Test para verificar la vista que lista los clientes con paginación."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('clientes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Empresa de Prueba')  # Verifica que el cliente aparece

    def test_crear_cliente(self):
        """Test para verificar que un cliente puede ser creado correctamente."""
        self.client.login(username='testuser', password='testpassword')

        # Datos para crear un cliente
        data = {
            'nombre_empresa': 'Nueva Empresa',
            'telefono_contacto': '987654321',
            'email_contacto': 'nueva@empresa.com',
            'nif_cif': '87654321B'
        }

        # Realizamos el post para crear el cliente
        response = self.client.post(reverse('crear_cliente'), data)

        # Verificamos que el cliente se haya creado correctamente
        self.assertEqual(response.status_code, 302)  # Redirige a la lista de clientes
        self.assertRedirects(response, reverse('clientes'))
        self.assertTrue(Cliente.objects.filter(nombre_empresa='Nueva Empresa').exists())

        # Verificamos el mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cliente creado exitosamente.')

    def test_borrar_cliente(self):
        """Test para verificar que un cliente se puede eliminar correctamente (borrado lógico)."""
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('borrar_cliente', kwargs={'id_cliente': self.cliente.id_cliente}))

        # Verificamos que el cliente ha sido eliminado
        self.assertFalse(Cliente.objects.filter(id_cliente=self.cliente.id_cliente).exists())

        # Verificamos que la redirección y mensaje de éxito
        self.assertRedirects(response, reverse('clientes'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cliente eliminado exitosamente.')

    def test_editar_cliente(self):
        """Test para verificar que un cliente se puede editar correctamente."""
        self.client.login(username='testuser', password='testpassword')

        # Datos para editar el cliente
        data = {
            'nombre_empresa': 'Empresa Editada',
            'telefono_contacto': '111222333',
            'email_contacto': 'editada@empresa.com',
            'nif_cif': '12345678A'
        }

        response = self.client.post(reverse('editar_cliente', kwargs={'id_cliente': self.cliente.id_cliente}), data)

        # Verificamos que el cliente se ha editado correctamente
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nombre_empresa, 'Empresa Editada')
        self.assertEqual(self.cliente.telefono_contacto, '111222333')
        self.assertEqual(self.cliente.email_contacto, 'editada@empresa.com')

        # Verificamos la redirección y mensaje de éxito
        self.assertRedirects(response, reverse('clientes'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Cliente actualizado exitosamente.')
