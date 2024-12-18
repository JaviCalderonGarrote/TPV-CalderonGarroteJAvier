import json
from django.test import TestCase, Client
from django.urls import reverse
from tpv_app.models import Usuario, Cliente, Producto, Venta, DetalleVenta, Servicio, Categoria
from django.core.exceptions import ValidationError
from decimal import Decimal

class VentaViewsTests(TestCase):
    """Tests para las vistas relacionadas con ventas."""

    def setUp(self):
        """Configuración inicial para todos los tests."""
        self.client = Client()

        # Crear un usuario administrador y un vendedor
        self.admin = Usuario.objects.create_user(
            username="admin", nombre="Admin", apellido="User", password="admin123", rol="Administrador"
        )
        self.vendedor = Usuario.objects.create_user(
            username="vendedor", nombre="Vendedor", apellido="User", password="password123", rol="Vendedor"
        )

        # Crear una categoría
        self.categoria = Categoria.objects.create(nombre="Electrónica")

        # Crear productos
        self.producto1 = Producto.objects.create(
            nombre="Laptop", precio=Decimal("1000.00"), id_categoria=self.categoria, activo=True
        )
        self.producto2 = Producto.objects.create(
            nombre="Mouse", precio=Decimal("50.00"), id_categoria=self.categoria, activo=True
        )

        # Crear un cliente
        self.cliente = Cliente.objects.create(
            nombre_empresa="Empresa S.A.",
            nif_cif="12345678X",
            nombre_contacto="Juan Pérez",
        )

        # Crear un servicio abierto
        self.servicio = Servicio.objects.create(
            nombre="Servicio General", estado="abierto", fecha_inicio="2024-01-01T10:00:00Z"
        )

    def test_crear_venta_con_usuario_autenticado(self):
        """Un usuario autenticado puede crear una venta exitosamente."""
        self.client.login(username=self.vendedor.username, password="password123")

        data = {
            "id_cliente": self.cliente.id_cliente,
            "producto_ids": [self.producto1.id_producto, self.producto2.id_producto],
            "cantidades": [1, 2],  # Compra de 1 Laptop y 2 Mouse
        }

        response = self.client.post(reverse("crear_venta"), json.dumps(data), content_type="application/json")

        # Validar la respuesta HTTP y la creación de la venta
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Venta.objects.filter(id_cliente=self.cliente).exists())

        # Validar que los detalles de la venta se hayan creado correctamente
        venta = Venta.objects.get(id_cliente=self.cliente)
        detalles = DetalleVenta.objects.filter(id_venta=venta)
        self.assertEqual(detalles.count(), 2)  # Deben existir 2 detalles de venta
        self.assertEqual(venta.total, Decimal("1100.00"))  # Total esperado: 1000 + (2 x 50)

    def test_crear_venta_sin_productos(self):
        """Intentar crear una venta sin productos debe devolver un error."""
        self.client.login(username=self.vendedor.username, password="password123")

        data = {
            "id_cliente": self.cliente.id_cliente,
            "producto_ids": [],
            "cantidades": [],
        }

        response = self.client.post(reverse("crear_venta"), json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Debe incluir al menos un producto", response.json().get("error", ""))

    def test_crear_venta_con_cantidades_invalidas(self):
        """Intentar crear una venta con cantidades inválidas debe devolver un error."""
        self.client.login(username=self.vendedor.username, password="password123")

        data = {
            "id_cliente": self.cliente.id_cliente,
            "producto_ids": [self.producto1.id_producto],
            "cantidades": [-1],  # Cantidad inválida
        }

        response = self.client.post(reverse("crear_venta"), json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Cantidad inválida", response.json().get("error", ""))

   


    def test_detalle_venta_con_ventas(self):
        """Si hay detalles de ventas, estos deben mostrarse correctamente."""
        # Crear una venta con detalles
        venta = Venta.objects.create(
            id_usuario=self.vendedor,
            id_cliente=self.cliente,
            id_servicio=self.servicio,
            total=Decimal("1000.00"),
        )
        DetalleVenta.objects.create(
            id_venta=venta,
            id_producto=self.producto1,
            cantidad=1,
            precio_unitario=self.producto1.precio,
            subtotal=Decimal("1000.00"),
        )

        self.client.login(username=self.vendedor.username, password="password123")

        response = self.client.get(reverse("detalle_venta"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Laptop")  # Producto en el detalle
        self.assertContains(response, "1000.00")  # Subtotal del producto

    def test_crear_venta_sin_servicio_abierto(self):
        """No se debe poder crear una venta si no hay un servicio abierto."""
        # Cerrar el servicio abierto
        self.servicio.estado = "cerrado"
        self.servicio.save()

        self.client.login(username=self.vendedor.username, password="password123")

        data = {
            "id_cliente": self.cliente.id_cliente,
            "producto_ids": [self.producto1.id_producto],
            "cantidades": [1],
        }

        response = self.client.post(reverse("crear_venta"), json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("No hay un servicio abierto", response.json().get("error", ""))

