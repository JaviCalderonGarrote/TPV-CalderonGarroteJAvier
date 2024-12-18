from django.test import TestCase
from django.urls import reverse
from tpv_app.models import Servicio, Usuario
from django.contrib.auth import get_user_model

class ServicioViewsTestCase(TestCase):

    def setUp(self):
        """Preparar datos para las pruebas."""
        # Crear un usuario usando el modelo personalizado
        self.user = Usuario.objects.create_user(
            username='testuser',
            password='testpassword',
            nombre='Javier',  # Añadido el campo 'nombre'
            apellido='Calderon'  # Añadido el campo 'apellido'
        )
        self.servicio = Servicio.objects.create(
            nombre='Servicio Test',
            estado='activo',
            fecha_inicio='2024-01-01'
        )
        # Iniciar sesión con el usuario personalizado
        self.client.login(username='testuser', password='testpassword')

    def test_listar_servicios(self):
        """Probar la vista para listar los servicios."""
        url = reverse('servicios')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'servicios.html')
        self.assertContains(response, 'Servicio Test')

    def test_crear_servicio(self):
        """Probar la vista para crear un nuevo servicio."""
        url = reverse('crear_servicio')
        data = {'nombre': 'Nuevo Servicio', 'estado': 'activo'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('servicios'))  # Redirige a la lista de servicios
        self.assertEqual(Servicio.objects.count(), 2)  # Verifica que se haya creado el nuevo servicio

    def test_editar_servicio(self):
        """Probar la vista para editar un servicio existente."""
        url = reverse('editar_servicio', args=[self.servicio.id_servicio])
        data = {'nombre': 'Servicio Editado', 'estado': 'inactivo'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('servicios'))  # Redirige a la lista de servicios
        self.servicio.refresh_from_db()  # Recargar el servicio para ver los cambios
        self.assertEqual(self.servicio.nombre, 'Servicio Editado')
        self.assertEqual(self.servicio.estado, 'inactivo')

    def test_borrar_servicio(self):
        """Probar la vista para borrar un servicio existente."""
        url = reverse('borrar_servicio', args=[self.servicio.id_servicio])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('servicios'))  # Redirige a la lista de servicios
        # Verifica que el servicio haya sido eliminado
        self.assertEqual(Servicio.objects.count(), 0)

    def test_borrar_servicio_no_existente(self):
        """Probar el comportamiento de la vista de borrar cuando el servicio no existe."""
        url = reverse('borrar_servicio', args=[9999])  # ID que no existe
        response = self.client.post(url)
        self.assertRedirects(response, reverse('servicios'))  # Redirige a la lista de servicios
        # Verifica que no se hayan eliminado servicios
        self.assertEqual(Servicio.objects.count(), 1)
