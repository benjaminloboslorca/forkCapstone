from rest_framework import serializers
from rest_framework import exceptions 
from .models import Cliente, Producto, Categoria, Oferta, Pedido, DetallePedido
from django.utils import timezone  

class ClienteRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=8,
        help_text="Mínimo 8 caracteres, debe incluir letras y números"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirmar contraseña"
    )

    class Meta:
        model = Cliente
        fields = ('nombre', 'correo', 'telefono', 'password', 'password2')

    def validate_password(self, value):
        """Valida que la contraseña sea segura."""
        if len(value) < 8:
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres."
            )
        
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos una letra."
            )
        
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "La contraseña debe contener al menos un número."
            )
        
        contraseñas_comunes = ['12345678', '123456789', 'password', 'qwerty', 'abc12345']
        if value.lower() in contraseñas_comunes:
            raise serializers.ValidationError(
                "Esta contraseña es demasiado común. Elige una más segura."
            )
        
        return value
    
    def validate_telefono(self, value):
        """Valida y normaliza el formato del teléfono chileno."""
        if not value:
            raise serializers.ValidationError(
                "El teléfono es obligatorio."
            )
        
        telefono_limpio = ''.join(filter(str.isdigit, value))
        
        if len(telefono_limpio) == 9:
            if not telefono_limpio.startswith('9'):
                raise serializers.ValidationError(
                    "El teléfono móvil chileno debe comenzar con 9."
                )
            return f"+56{telefono_limpio}"
        
        elif len(telefono_limpio) == 11:
            if not telefono_limpio.startswith('569'):
                raise serializers.ValidationError(
                    "El teléfono debe tener formato chileno (+56 9...)."
                )
            return f"+{telefono_limpio}"
        
        elif len(telefono_limpio) == 8:
            return f"+56{telefono_limpio}"
        
        else:
            raise serializers.ValidationError(
                "Formato inválido. Ingrese un teléfono chileno válido (móvil: 9 dígitos, fijo: 8 dígitos)."
            )
    
    def validate(self, data):
        """Valida que las contraseñas coincidan."""
        if data.get('password') != data.get('password2'):
            raise serializers.ValidationError({
                'password2': "Las contraseñas no coinciden."
            })
        
        return data

    def create(self, validated_data):
        """Crea el cliente con la contraseña hasheada."""
        validated_data.pop('password2', None)
        
        password = validated_data.pop('password')
        cliente = Cliente.objects.create(**validated_data)
        cliente.set_password(password)
        cliente.save() 
        return cliente


class ClienteLoginSerializer(serializers.Serializer):
    """
    Serializador para recibir credenciales de login y validar al cliente.
    """
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        correo = data.get('correo')
        password = data.get('password')
        
        if not correo or not password:
            raise exceptions.AuthenticationFailed('Debe proporcionar correo y contraseña.')

        try:
            cliente = Cliente.objects.get(correo=correo)
        except Cliente.DoesNotExist:
            raise exceptions.AuthenticationFailed('Credenciales inválidas.')

        if not cliente.check_password(password):
            raise exceptions.AuthenticationFailed('Credenciales inválidas.')

        data['cliente'] = cliente
        return data


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializador simple para exponer datos del cliente (nombre, correo, etc.)
    al frontend cuando está autenticado.
    """
    class Meta:
        model = Cliente
        fields = ('id', 'nombre', 'correo', 'telefono') 
        read_only_fields = fields


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para categorías"""
    total_productos = serializers.IntegerField(read_only=True, source='productos.count')
    
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'activa', 'total_productos']


class OfertaSerializer(serializers.ModelSerializer):
    """Serializer para ofertas activas"""
    esta_activa = serializers.SerializerMethodField()
    descuento_porcentaje = serializers.SerializerMethodField()
    
    class Meta:
        model = Oferta
        fields = ['id', 'precio_oferta', 'fecha_inicio', 'fecha_fin', 'esta_activa', 'descuento_porcentaje']
    
    def get_esta_activa(self, obj):
        """Verifica si la oferta está activa en este momento"""
        return obj.esta_activa
    
    def get_descuento_porcentaje(self, obj):
        """Retorna el porcentaje de descuento"""
        return obj.descuento_porcentaje


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer completo para mostrar un producto con toda su información"""
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        source='categoria',
        write_only=True
    )
    imagen_url = serializers.SerializerMethodField()
    ofertas_activas = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()
    tiene_oferta = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio_unitario',
            'unidad_medida',
            'stock_disponible',
            'categoria',
            'categoria_id',
            'imagen',
            'imagen_url',
            'ofertas_activas',
            'precio_final',
            'tiene_oferta',
            'activo'
        ]
        extra_kwargs = {
            'imagen': {'write_only': True}
        }
    
    def get_imagen_url(self, obj):
        """Retorna la URL completa de la imagen"""
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None
    
    def get_ofertas_activas(self, obj):
        """Obtiene las ofertas activas del producto"""
        now = timezone.now()
        ofertas = obj.ofertas.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now,
            activa=True
        )
        return OfertaSerializer(ofertas, many=True, context=self.context).data
    
    def get_precio_final(self, obj):
        """Calcula el precio final (con oferta si existe)"""
        now = timezone.now()
        oferta = obj.ofertas.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now,
            activa=True
        ).first()
        
        if oferta:
            return float(oferta.precio_oferta)
        return float(obj.precio_unitario)
    
    def get_tiene_oferta(self, obj):
        """Verifica si el producto tiene ofertas activas"""
        return obj.tiene_oferta_activa


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de productos"""
    imagen_url = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()
    tiene_oferta = serializers.SerializerMethodField()
    descuento_porcentaje = serializers.SerializerMethodField()
    ahorro = serializers.SerializerMethodField()
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'precio_unitario',
            'precio_final',
            'tiene_oferta',
            'descuento_porcentaje',
            'ahorro',
            'unidad_medida',
            'stock_disponible',
            'imagen_url',
            'categoria_nombre',
            'activo'
        ]
    
    def get_imagen_url(self, obj):
        """Retorna la URL de la imagen principal"""
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None
    
    def get_precio_final(self, obj):
        """Calcula el precio final (con oferta si existe)"""
        now = timezone.now()
        oferta = obj.ofertas.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now,
            activa=True
        ).first()
        
        if oferta:
            return float(oferta.precio_oferta)
        return float(obj.precio_unitario)
    
    def get_tiene_oferta(self, obj):
        """Verifica si el producto tiene ofertas activas"""
        return obj.tiene_oferta_activa
    
    def get_descuento_porcentaje(self, obj):
        """Retorna el porcentaje de descuento"""
        now = timezone.now()
        oferta = obj.ofertas.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now,
            activa=True
        ).first()
        
        if oferta and obj.precio_unitario > 0:
            descuento = ((obj.precio_unitario - oferta.precio_oferta) / obj.precio_unitario) * 100
            return round(descuento, 0)
        return 0
    
    def get_ahorro(self, obj):
        """Retorna el ahorro en pesos"""
        now = timezone.now()
        oferta = obj.ofertas.filter(
            fecha_inicio__lte=now,
            fecha_fin__gte=now,
            activa=True
        ).first()
        
        if oferta:
            return float(obj.precio_unitario - oferta.precio_oferta)
        return 0


# ===== SERIALIZERS PARA CARRITO =====

class CarritoItemSerializer(serializers.Serializer):
    """Serializer para un ítem individual del carrito"""
    producto_id = serializers.IntegerField()
    nombre = serializers.CharField(read_only=True)
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cantidad = serializers.IntegerField(min_value=1)
    unidad_medida = serializers.CharField(read_only=True)
    imagen_url = serializers.CharField(read_only=True)
    stock_disponible = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    def validate_producto_id(self, value):
        """Valida que el producto exista"""
        try:
            producto = Producto.objects.get(pk=value)
            if not producto.activo:
                raise serializers.ValidationError("Este producto no está disponible.")
        except Producto.DoesNotExist:
            raise serializers.ValidationError("El producto no existe.")
        return value
    
    def validate(self, data):
        """Valida que haya stock suficiente"""
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad')
        
        try:
            producto = Producto.objects.get(pk=producto_id)
            if cantidad > producto.stock_disponible:
                raise serializers.ValidationError({
                    'cantidad': f'Stock insuficiente. Solo hay {producto.stock_disponible} unidades disponibles.'
                })
        except Producto.DoesNotExist:
            raise serializers.ValidationError({'producto_id': 'El producto no existe.'})
        
        return data


class CarritoSerializer(serializers.Serializer):
    """Serializer para el carrito completo"""
    items = CarritoItemSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cantidad_items = serializers.IntegerField(read_only=True)


class CheckoutSerializer(serializers.Serializer):
    """Serializer para procesar el checkout"""
    
    # Datos del cliente
    nombre_cliente = serializers.CharField(max_length=255)
    correo_cliente = serializers.EmailField()
    telefono_cliente = serializers.CharField(max_length=20)
    
    # Dirección de envío
    direccion = serializers.CharField(max_length=500)
    region = serializers.CharField(max_length=100)
    comuna = serializers.CharField(max_length=100)
    codigo_postal = serializers.CharField(max_length=20, required=False, allow_blank=True)
    referencia_direccion = serializers.CharField(required=False, allow_blank=True)
    
    # Información adicional
    notas_pedido = serializers.CharField(required=False, allow_blank=True)
    metodo_pago = serializers.ChoiceField(
        choices=[('transferencia', 'Transferencia Bancaria'), ('webpay', 'Webpay')],
        default='transferencia'
    )
    
    def validate_telefono_cliente(self, value):
        """Valida formato básico del teléfono"""
        # Eliminar espacios y caracteres especiales
        telefono_limpio = ''.join(filter(str.isdigit, value))
        
        if len(telefono_limpio) < 8:
            raise serializers.ValidationError("El teléfono debe tener al menos 8 dígitos.")
        
        return value
    
    def validate(self, data):
        """Validaciones adicionales"""
        return data


class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializer para los detalles del pedido"""
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_imagen = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = ['id', 'cantidad', 'precio_compra', 'producto_nombre', 'producto_imagen', 'subtotal']
    
    def get_producto_imagen(self, obj):
        """Obtiene la URL de la imagen del producto"""
        if obj.producto.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.producto.imagen.url)
            return obj.producto.imagen.url
        return None


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer completo para mostrar un pedido"""
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_pedido_display', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    es_invitado = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = [
            'id',
            'fecha_pedido',
            'total_pedido',
            'estado_pedido',
            'estado_display',
            'metodo_pago',
            'metodo_pago_display',
            'nombre_cliente',
            'correo_cliente',
            'telefono_cliente',
            'direccion',
            'region',
            'comuna',
            'codigo_postal',
            'referencia_direccion',
            'notas_pedido',
            'numero_seguimiento',
            'fecha_pago',
            'fecha_envio',
            'fecha_entrega',
            'detalles',
            'es_invitado'
        ]
    
    def get_es_invitado(self, obj):
        return obj.es_invitado()


class PedidoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar pedidos"""
    estado_display = serializers.CharField(source='get_estado_pedido_display', read_only=True)
    cantidad_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = [
            'id',
            'fecha_pedido',
            'total_pedido',
            'estado_pedido',
            'estado_display',
            'cantidad_items'
        ]
    
    def get_cantidad_items(self, obj):
        """Cuenta la cantidad total de items en el pedido"""
        return sum(detalle.cantidad for detalle in obj.detalles.all())


# ===== SERIALIZER PARA ACTUALIZAR PERFIL =====

class ClienteUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar datos del perfil del cliente
    """
    
    class Meta:
        model = Cliente
        fields = ['correo', 'telefono', 'nombre']
        
    def validate_correo(self, value):
        """Valida que el email sea único"""
        cliente_id = self.instance.id if self.instance else None
        
        # Verificar si el email ya existe (excluyendo el cliente actual)
        if Cliente.objects.filter(correo=value).exclude(id=cliente_id).exists():
            raise serializers.ValidationError(
                "Ya existe un cliente registrado con este correo electrónico."
            )
        
        return value
    
    def validate_telefono(self, value):
        """Valida y normaliza el formato del teléfono chileno"""
        if not value:
            return value
        
        # Eliminar todos los caracteres que no sean dígitos
        telefono_limpio = ''.join(filter(str.isdigit, value))
        
        # Validar longitud (Chile: 9 dígitos o 11 con código país)
        if len(telefono_limpio) == 9:
            # Formato: 912345678
            if not telefono_limpio.startswith('9'):
                raise serializers.ValidationError(
                    "El teléfono móvil chileno debe comenzar con 9."
                )
            # Normalizar a formato: +56912345678
            return f"+56{telefono_limpio}"
        
        elif len(telefono_limpio) == 11:
            # Formato: 56912345678
            if not telefono_limpio.startswith('569'):
                raise serializers.ValidationError(
                    "El teléfono debe tener formato chileno (+56 9...)."
                )
            # Normalizar a formato: +56912345678
            return f"+{telefono_limpio}"
        
        elif len(telefono_limpio) == 8:
            # Teléfono fijo (ej: 22345678)
            # Normalizar a formato: +5622345678
            return f"+56{telefono_limpio}"
        
        else:
            raise serializers.ValidationError(
                "Formato inválido. Ingrese un teléfono chileno válido (ej: 912345678 o 22345678)."
            )