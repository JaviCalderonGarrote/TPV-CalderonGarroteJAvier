from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Group, Permission
from django.db import models


# -----------------------------
# Modelo de Usuario
# -----------------------------
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UsuarioManager(BaseUserManager):
    def create_user(self, username, nombre, apellido, password=None, **extra_fields):
        if not username:
            raise ValueError("El usuario debe tener un nombre de usuario.")
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(username=username, nombre=nombre, apellido=apellido, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, nombre, apellido, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('Administrador', 'Administrador'),
        ('Vendedor', 'Vendedor'),
    ]
    username = models.CharField(max_length=150, unique=True, verbose_name="Nombre de usuario")
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    apellido = models.CharField(max_length=150, verbose_name="Apellido")
    rol = models.CharField(max_length=15, choices=ROLES, default='Vendedor', verbose_name="Rol")
    is_active = models.BooleanField(default=True, verbose_name="¿Está activo?")
    is_staff = models.BooleanField(default=False, verbose_name="¿Es staff?")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    objects = UsuarioManager()

    def __str__(self):
        return f"{self.username} ({self.rol})"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

# -----------------------------
# Modelo de Categorías
# -----------------------------

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)  # Campo para borrado lógico

    def __str__(self):
        return self.nombre


# -----------------------------
# Modelo de Productos
# -----------------------------

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    id_categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.SET_NULL)
    activo = models.BooleanField(default=True)  # Campo para borrado lógico

    def __str__(self):
        return self.nombre


# -----------------------------
# Modelo de Clientes
# -----------------------------

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre_empresa = models.CharField(null=True, max_length=255, verbose_name="Nombre de la empresa")
    nombre_contacto = models.CharField(max_length=100, null=True, blank=True, verbose_name="Nombre de contacto")
    direccion_fiscal = models.CharField(max_length=255, null=True, blank=True, verbose_name="Dirección fiscal")
    telefono_contacto = models.CharField(null=True, max_length=15, verbose_name="Teléfono de contacto")
    email_contacto = models.EmailField(null=True, blank=True, verbose_name="Email de contacto")
    nif_cif = models.CharField(max_length=20, null=True, unique=True, verbose_name="NIF/CIF")
    pagina_web = models.URLField(max_length=200, null=True, blank=True, verbose_name="Página web")

    def __str__(self):
        return self.nombre_empresa


# -----------------------------
# Modelo de Servicios
# -----------------------------

class Servicio(models.Model):
    ESTADO = [
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado')
    ]

    id_servicio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    cantidad_tickets = models.IntegerField(default=0, editable=False)
    total_ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    estado = models.CharField(max_length=10, choices=ESTADO)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.estado == 'abierto':
                Servicio.objects.filter(estado='abierto').update(estado='cerrado', fecha_fin=timezone.now())
            elif self.estado == 'cerrado' and not self.fecha_fin:
                self.fecha_fin = timezone.now()
                ventas = Venta.objects.filter(id_servicio=self.id_servicio)
                self.cantidad_tickets = ventas.count()
                self.total_ingresos = sum(venta.total for venta in ventas)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


# -----------------------------
# Modelo de Ventas
# -----------------------------

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)  # Clave primaria generada automáticamente
    fecha = models.DateTimeField(auto_now_add=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    id_servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def clean(self):
        if not Servicio.objects.filter(estado='abierto').exists():
            raise ValidationError("No hay ningún servicio abierto para realizar una venta.")
        if not self.id_servicio:
            servicio_abierto = Servicio.objects.filter(estado='abierto').first()
            if servicio_abierto:
                self.id_servicio = servicio_abierto
            else:
                raise ValidationError("No se puede realizar la venta sin un servicio abierto.")

    def update_total(self):
        with transaction.atomic():
            self.total = sum(detalle.subtotal for detalle in self.detalleventa_set.all())
            self.save(update_fields=['total'])

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.id_servicio:
                servicio = self.id_servicio
                servicio.cantidad_tickets += 1
                servicio.save()

    def __str__(self):
        return f"Venta {self.id_venta} - {self.fecha}"


# -----------------------------
# Modelo de Detalles de la Venta
# -----------------------------

class DetalleVenta(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        if not self.id_producto.activo:
            raise ValidationError("El producto está inactivo y no puede usarse en la venta.")
        self.precio_unitario = self.id_producto.precio
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad} x {self.id_producto.nombre}"


# -----------------------------
# Señales para manejar la eliminación de categorías
# -----------------------------

@receiver(post_delete, sender=Categoria)
def update_producto_categoria_null(sender, instance, **kwargs):
    """Cuando se borra una categoría, ponemos a NULL los productos asociados a ella y los marcamos como inactivos"""
    Producto.objects.filter(id_categoria=instance).update(id_categoria=None, activo=False)
    
# Señales para manejar la actualización de ingresos de servicio cuando se guarda o elimina una venta

@receiver(post_save, sender=Venta)
def actualizar_ingresos_al_guardar(sender, instance, **kwargs):
    """Actualiza los ingresos totales del servicio cuando se guarda una venta."""
    servicio = instance.id_servicio
    if servicio:
        ventas = Venta.objects.filter(id_servicio=servicio.id_servicio)
        servicio.cantidad_tickets = ventas.count()
        servicio.total_ingresos = sum(venta.total for venta in ventas)
        servicio.save(update_fields=['cantidad_tickets', 'total_ingresos'])


@receiver(post_delete, sender=Venta)
def actualizar_ingresos_al_eliminar(sender, instance, **kwargs):
    """Actualiza los ingresos totales del servicio cuando se elimina una venta."""
    servicio = instance.id_servicio
    if servicio:
        ventas = Venta.objects.filter(id_servicio=servicio.id_servicio)
        servicio.cantidad_tickets = ventas.count()
        servicio.total_ingresos = sum(venta.total for venta in ventas)
        servicio.save(update_fields=['cantidad_tickets', 'total_ingresos'])
