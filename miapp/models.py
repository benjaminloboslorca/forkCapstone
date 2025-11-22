from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ClienteManager(BaseUserManager):
    
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El Cliente debe tener un correo.')
        
        correo = self.normalize_email(correo)
        cliente = self.model(correo=correo, **extra_fields)
        
        cliente.set_password(password) 
        cliente.save(using=self._db)
        return cliente

    def create_superuser(self, correo, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
            
        return self.create_user(correo, password, **extra_fields)


# ------------------------------------------------
# MODELO CLIENTE 
# ------------------------------------------------
class Cliente(AbstractBaseUser, PermissionsMixin):
    
    # ------------------ Campos de Datos ------------------
    nombre = models.CharField(max_length=255, verbose_name="Nombre completo")
    correo = models.EmailField(unique=True, db_index=True, verbose_name="Correo electrónico")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    # ------------------ Campos de Permisos ------------------
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_staff = models.BooleanField(default=False, verbose_name="Es staff")
    is_superuser = models.BooleanField(default=False, verbose_name="Es superusuario")

    @property
    def email(self):
        """Permite que el sistema de autenticación de Django acceda a 'correo' usando el atributo 'email'."""
        return self.correo

    # ------------------ Configuración de Autenticación ------------------
    USERNAME_FIELD = 'correo' 
    REQUIRED_FIELDS = ['nombre'] 

    objects = ClienteManager() 

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre} ({self.correo})"


# ------------------------------------------------
# MODELO CATEGORIA
# ------------------------------------------------
class Categoria(models.Model):
    nombre = models.CharField(
        max_length=100, 
        unique=True,
        db_index=True,
        verbose_name="Nombre de categoría",
        help_text="Nombre único de la categoría"
    )
    descripcion = models.TextField(
        blank=True, 
        verbose_name="Descripción",
        help_text="Descripción detallada de la categoría"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si la categoría está activa"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    class Meta:
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        # Normalizar el nombre (trim y capitalizar)
        if self.nombre:
            self.nombre = self.nombre.strip()
            
            # Verificar duplicados (case-insensitive)
            qs = Categoria.objects.filter(nombre__iexact=self.nombre)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({
                    'nombre': 'Ya existe una categoría con este nombre.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def total_productos(self):
        """Retorna el total de productos en esta categoría"""
        return self.productos.count()

    @property
    def total_productos_activos(self):
        """Retorna el total de productos con stock disponible"""
        return self.productos.filter(stock_disponible__gt=0).count()


# ------------------------------------------------
# MODELO PRODUCTO
# ------------------------------------------------
class Producto(models.Model):
    
    UNIDADES_MEDIDA = [
        ('unidad', 'Unidad'),
        ('kg', 'Kilogramo'),
        ('gr', 'Gramo'),
        ('lt', 'Litro'),
        ('ml', 'Mililitro'),
        ('paquete', 'Paquete'),
        ('caja', 'Caja'),
    ]
    
    nombre = models.CharField(
        max_length=100, 
        db_index=True,
        verbose_name="Nombre del producto"
    )
    descripcion = models.TextField(
        max_length=500,
        verbose_name="Descripción"
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio unitario",
        help_text="Precio en pesos chilenos"
    )
    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDADES_MEDIDA,
        default='unidad',
        verbose_name="Unidad de medida"
    )
    stock_disponible = models.IntegerField(
        default=0,
        verbose_name="Stock disponible",
        help_text="Cantidad disponible en inventario"
    )
    
    # ForeignKey corregida (sin prefijo id_)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,  # PROTECT en lugar de CASCADE
        related_name='productos',
        verbose_name="Categoría"
    )
    
    # Imagen simplificada (sin modelo separado)
    imagen = models.CharField(max_length=255, default='default.jpg')

    def get_imagen_url(self):
        from django.templatetags.static import static
        return static(f'img/productos/{self.imagen}')
    
    # Campos de auditoría
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el producto está activo para venta"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['categoria', 'activo']),
            models.Index(fields=['-fecha_creacion']),
        ]

    def __str__(self):
        return f"{self.nombre} - ${self.precio_unitario:,.0f}"

    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        if self.precio_unitario and self.precio_unitario <= 0:
            raise ValidationError({
                'precio_unitario': 'El precio debe ser mayor a 0.'
            })
        
        if self.stock_disponible < 0:
            raise ValidationError({
                'stock_disponible': 'El stock no puede ser negativo.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def tiene_stock(self):
        """Retorna True si hay stock disponible"""
        return self.stock_disponible > 0

    @property
    def precio_formateado(self):
        """Retorna el precio formateado"""
        return f"${self.precio_unitario:,.0f}"

    @property
    def tiene_oferta_activa(self):
        """Verifica si tiene alguna oferta activa"""
        from django.utils import timezone
        now = timezone.now()
        return self.ofertas.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now
        ).exists()

    def reducir_stock(self, cantidad):
        """Reduce el stock del producto"""
        if cantidad > self.stock_disponible:
            raise ValidationError(
                f'No hay suficiente stock. Disponible: {self.stock_disponible}'
            )
        self.stock_disponible -= cantidad
        self.save(update_fields=['stock_disponible'])

    def aumentar_stock(self, cantidad):
        """Aumenta el stock del producto"""
        self.stock_disponible += cantidad
        self.save(update_fields=['stock_disponible'])


# ------------------------------------------------
# MODELO PEDIDO
# ------------------------------------------------
class Pedido(models.Model):
    
    ESTADOS = [
        ('pendiente_pago', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('preparando', 'Preparando Envío'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('transferencia', 'Transferencia Bancaria'),
        ('webpay', 'Webpay'),
        ('efectivo', 'Efectivo'),
    ]
    
    # Información básica del pedido
    fecha_pedido = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del pedido")
    total_pedido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total del pedido"
    )
    estado_pedido = models.CharField(
        max_length=50,
        choices=ESTADOS,
        default='pendiente_pago',
        db_index=True,
        verbose_name="Estado del pedido"
    )
    metodo_pago = models.CharField(
        max_length=50,
        choices=METODOS_PAGO,
        default='transferencia',
        verbose_name="Método de pago"
    )
    
    # Cliente registrado o invitado
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos',
        verbose_name="Usuario"
    )
    
    # Datos del cliente (snapshot para histórico)
    nombre_cliente = models.CharField(max_length=255, verbose_name="Nombre del cliente")
    correo_cliente = models.EmailField(verbose_name="Correo del cliente")
    telefono_cliente = models.CharField(max_length=20, verbose_name="Teléfono del cliente")
    
    # Dirección de envío
    direccion = models.CharField(max_length=500, verbose_name="Dirección")
    region = models.CharField(max_length=100, verbose_name="Región")
    comuna = models.CharField(max_length=100, verbose_name="Comuna")
    codigo_postal = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Código postal"
    )
    referencia_direccion = models.TextField(
        blank=True,
        verbose_name="Referencia",
        help_text="Referencias adicionales para encontrar la dirección"
    )
    
    # Información adicional
    notas_pedido = models.TextField(
        blank=True,
        verbose_name="Notas del pedido",
        help_text="Notas o comentarios del cliente"
    )
    
    # Datos de seguimiento
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de pago")
    fecha_envio = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de envío")
    fecha_entrega = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de entrega")
    numero_seguimiento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Número de seguimiento",
        help_text="Número de seguimiento del envío"
    )

    class Meta:
        db_table = 'pedidos'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']
        indexes = [
            models.Index(fields=['-fecha_pedido']),
            models.Index(fields=['estado_pedido']),
            models.Index(fields=['usuario', '-fecha_pedido']),
        ]

    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente} - {self.get_estado_pedido_display()}"
    
    def es_invitado(self):
        """Retorna True si el pedido fue hecho por un invitado"""
        return self.usuario is None
    
    def puede_cancelar(self):
        """Determina si el pedido puede ser cancelado"""
        return self.estado_pedido in ['pendiente_pago', 'pagado']
    
    def marcar_como_pagado(self):
        """Marca el pedido como pagado y registra la fecha"""
        from django.utils import timezone
        self.estado_pedido = 'pagado'
        self.fecha_pago = timezone.now()
        self.save(update_fields=['estado_pedido', 'fecha_pago'])
    
    def marcar_como_enviado(self, numero_seguimiento=None):
        """Marca el pedido como enviado"""
        from django.utils import timezone
        self.estado_pedido = 'enviado'
        self.fecha_envio = timezone.now()
        if numero_seguimiento:
            self.numero_seguimiento = numero_seguimiento
        self.save(update_fields=['estado_pedido', 'fecha_envio', 'numero_seguimiento'])

    def marcar_como_completado(self):
        """Marca el pedido como completado"""
        from django.utils import timezone
        self.estado_pedido = 'completado'
        self.fecha_entrega = timezone.now()
        self.save(update_fields=['estado_pedido', 'fecha_entrega'])


# ------------------------------------------------
# MODELO DETALLE PEDIDO
# ------------------------------------------------
class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Pedido"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,  # PROTECT para mantener histórico
        related_name='detalles_pedido',
        verbose_name="Producto"
    )
    cantidad = models.IntegerField(verbose_name="Cantidad")
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio de compra",
        help_text="Precio al momento de la compra (snapshot)"
    )

    class Meta:
        db_table = 'detalle_pedidos'
        verbose_name = 'Detalle de pedido'
        verbose_name_plural = 'Detalles de pedidos'
        indexes = [
            models.Index(fields=['pedido']),
            models.Index(fields=['producto']),
        ]

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} - Pedido #{self.pedido.id}"

    @property
    def subtotal(self):
        """Calcula el subtotal del detalle"""
        return self.cantidad * self.precio_compra

    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        if self.cantidad <= 0:
            raise ValidationError({
                'cantidad': 'La cantidad debe ser mayor a 0.'
            })


# ------------------------------------------------
# MODELO OFERTA
# ------------------------------------------------
class Oferta(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='ofertas',
        verbose_name="Producto"
    )
    precio_oferta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio de oferta"
    )
    fecha_inicio = models.DateTimeField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateTimeField(verbose_name="Fecha de fin")
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si la oferta está activa"
    )

    class Meta:
        db_table = 'ofertas'
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['producto', 'fecha_inicio', 'fecha_fin']),
        ]

    def __str__(self):
        return f"Oferta: {self.producto.nombre} - ${self.precio_oferta:,.0f}"

    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        if self.precio_oferta <= 0:
            raise ValidationError({
                'precio_oferta': 'El precio de oferta debe ser mayor a 0.'
            })
        
        if self.producto and self.precio_oferta >= self.producto.precio_unitario:
            raise ValidationError({
                'precio_oferta': 'El precio de oferta debe ser menor al precio normal.'
            })
        
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })

    @property
    def esta_activa(self):
        """Verifica si la oferta está activa en este momento"""
        from django.utils import timezone
        now = timezone.now()
        return self.activa and self.fecha_inicio <= now <= self.fecha_fin

    @property
    def descuento_porcentaje(self):
        """Calcula el porcentaje de descuento"""
        if self.producto:
            descuento = ((self.producto.precio_unitario - self.precio_oferta) / 
                        self.producto.precio_unitario) * 100
            return round(descuento, 2)
        return 0