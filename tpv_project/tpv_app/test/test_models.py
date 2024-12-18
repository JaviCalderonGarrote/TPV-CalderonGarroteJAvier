from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from tpv_app.models import (
    Usuario, Categoria, Producto, Cliente, Servicio, Venta, DetalleVenta
)


class UsuarioModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Usuario.objects.create_user(
            username="testuser",
            nombre="Test",
            apellido="User",
            password="securepassword",
        )

    def test_usuario_creado_correctamente(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.nombre, "Test")
        self.assertTrue(self.user.check_password("securepassword"))

    def test_superusuario_creado_correctamente(self):
        admin = Usuario.objects.create_superuser(
            username="adminuser",
            nombre="Admin",
            apellido="User",
            password="securepassword",
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)


class CategoriaModelTests(TestCase):
    def test_categoria_string_representation(self):
        categoria = Categoria.objects.create(nombre="Electrónica")
        self.assertEqual(str(categoria), "Electrónica")


class ProductoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nombre="Electrónica")
        cls.producto = Producto.objects.create(
            nombre="Laptop",
            precio=1500.00,
            id_categoria=cls.categoria,
            activo=True
        )

    def test_producto_string_representation(self):
        self.assertEqual(str(self.producto), "Laptop")

    def test_producto_categoria(self):
        self.assertEqual(self.producto.id_categoria, self.categoria)


class ClienteModelTests(TestCase):
    def test_cliente_string_representation(self):
        cliente = Cliente.objects.create(nombre_empresa="Mi Empresa")
        self.assertEqual(str(cliente), "Mi Empresa")


class ServicioModelTests(TestCase):
    def test_servicio_crea_correctamente(self):
        servicio = Servicio.objects.create(
            nombre="Servicio Test",
            fecha_inicio=timezone.now(),
            estado="abierto"
        )
        self.assertEqual(servicio.estado, "abierto")
        self.assertEqual(str(servicio), "Servicio Test")


class VentaModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = Usuario.objects.create_user(
            username="testuser",
            nombre="Test",
            apellido="User",
            password="securepassword"
        )
        cls.cliente = Cliente.objects.create(nombre_empresa="Mi Empresa")
        cls.servicio = Servicio.objects.create(
            nombre="Servicio Abierto",
            fecha_inicio=timezone.now(),
            estado="abierto"
        )
        cls.venta = Venta.objects.create(
            id_usuario=cls.usuario,
            id_cliente=cls.cliente,
            id_servicio=cls.servicio,
            total=500.00
        )

    def test_venta_string_representation(self):
        self.assertIn("Venta", str(self.venta))

    def test_venta_clean_sin_servicio_abierto(self):
        Servicio.objects.update(estado="cerrado")
        venta = Venta(id_usuario=self.usuario)
        with self.assertRaises(ValidationError):
            venta.clean()


class DetalleVentaModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.create(nombre="Electrónica")
        cls.producto = Producto.objects.create(
            nombre="Laptop",
            precio=1500.00,
            id_categoria=cls.categoria,
            activo=True
        )
        cls.usuario = Usuario.objects.create_user(
            username="testuser",
            nombre="Test",
            apellido="User",
            password="securepassword"
        )
        cls.servicio = Servicio.objects.create(
            nombre="Servicio Abierto",
            fecha_inicio=timezone.now(),
            estado="abierto"
        )
        cls.venta = Venta.objects.create(
            id_usuario=cls.usuario,
            id_servicio=cls.servicio,
            total=1500.00
        )
        cls.detalle_venta = DetalleVenta.objects.create(
            id_venta=cls.venta,
            id_producto=cls.producto,
            cantidad=1
        )

    def test_detalle_venta_calculo(self):
        self.assertEqual(self.detalle_venta.precio_unitario, 1500.00)
        self.assertEqual(self.detalle_venta.subtotal, 1500.00)

    def test_detalle_venta_producto_inactivo(self):
        self.producto.activo = False
        self.producto.save()
        with self.assertRaises(ValidationError):
            DetalleVenta.objects.create(
                id_venta=self.venta,
                id_producto=self.producto,
                cantidad=1
            )
