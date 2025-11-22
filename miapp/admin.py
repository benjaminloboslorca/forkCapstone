from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Count, Sum, Q
from .models import Categoria, Producto, Cliente, Pedido, DetallePedido, Oferta
from django.templatetags.static import static

# ===== CONFIGURACIÓN PARA CATEGORÍA =====
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion_corta', 'total_productos', 'total_productos_con_stock', 'activa_badge', 'fecha_creacion')
    list_display_links = ('id', 'nombre')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'id')
    ordering = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'total_productos')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'activa')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )

    def descripcion_corta(self, obj):
        if obj.descripcion:
            return f"{obj.descripcion[:50]}..." if len(obj.descripcion) > 50 else obj.descripcion
        return "-"
    descripcion_corta.short_description = 'Descripción'
    
    def total_productos(self, obj):
        return obj.productos.count()
    total_productos.short_description = 'Total Productos'
    
    def total_productos_con_stock(self, obj):
        total = obj.productos.filter(stock_disponible__gt=0, activo=True).count()
        return format_html('<span style="color: green; font-weight: bold;">{}</span>', total)
    total_productos_con_stock.short_description = 'Con Stock'
    
    def activa_badge(self, obj):
        if obj.activa:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Activa</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Inactiva</span>'
        )
    activa_badge.short_description = 'Estado'

    actions = ['activar_categorias', 'desactivar_categorias']
    
    def activar_categorias(self, request, queryset):
        updated = queryset.update(activa=True)
        self.message_user(request, f'{updated} categoría(s) activada(s).')
    activar_categorias.short_description = "✓ Activar categorías seleccionadas"
    
    def desactivar_categorias(self, request, queryset):
        updated = queryset.update(activa=False)
        self.message_user(request, f'{updated} categoría(s) desactivada(s).')
    desactivar_categorias.short_description = "✗ Desactivar categorías seleccionadas"


# ===== CONFIGURACIÓN PARA CLIENTE =====
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'correo', 'telefono', 'total_pedidos', 'total_gastado', 'fecha_registro', 'estado_badge')
    list_display_links = ('id', 'nombre', 'correo')
    search_fields = ('nombre', 'correo', 'telefono', 'id')
    list_filter = ('fecha_registro', 'is_active', 'is_staff')
    readonly_fields = ('fecha_registro', 'last_login', 'total_pedidos', 'total_gastado')
    ordering = ('-fecha_registro',)
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('correo', 'nombre', 'telefono')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('total_pedidos', 'total_gastado'),
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_registro', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    def total_pedidos(self, obj):
        return obj.pedidos.count()
    total_pedidos.short_description = 'Total Pedidos'
    
    def total_gastado(self, obj):
        total = obj.pedidos.filter(
            estado_pedido__in=['pagado', 'preparando', 'enviado', 'completado']
        ).aggregate(Sum('total_pedido'))['total_pedido__sum'] or 0
        return f"${total:,.0f}"
    total_gastado.short_description = 'Total Gastado'
    
    def estado_badge(self, obj):
        if obj.is_active:
            if obj.is_staff:
                return format_html('<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">👨‍💼 Staff</span>')
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Activo</span>')
        return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Inactivo</span>')
    estado_badge.short_description = 'Estado'


# ===== CONFIGURACIÓN PARA OFERTA =====
@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'precio_oferta', 'descuento_porcentaje', 'fecha_inicio', 'fecha_fin', 'estado_badge')
    list_display_links = ('id', 'producto')
    list_filter = ('activa', 'fecha_inicio', 'fecha_fin', 'producto__categoria')
    search_fields = ('producto__nombre', 'id')
    date_hierarchy = 'fecha_inicio'
    ordering = ('-fecha_inicio',)
    autocomplete_fields = ['producto']
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Producto', {
            'fields': ('producto',)
        }),
        ('Precio', {
            'fields': ('precio_oferta',)
        }),
        ('Periodo de Vigencia', {
            'fields': ('fecha_inicio', 'fecha_fin', 'activa')
        }),
    )

    def descuento_porcentaje(self, obj):
        porcentaje = obj.descuento_porcentaje
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">-{}%</span>',
            porcentaje
        )
    descuento_porcentaje.short_description = 'Descuento'

    def estado_badge(self, obj):
        if obj.esta_activa:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">🔥 ACTIVA</span>'
            )
        elif obj.fecha_fin < timezone.now():
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">⏱ Vencida</span>'
            )
        elif obj.fecha_inicio > timezone.now():
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">⏳ Programada</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Inactiva</span>'
        )
    estado_badge.short_description = 'Estado'

    actions = ['activar_ofertas', 'desactivar_ofertas']
    
    def activar_ofertas(self, request, queryset):
        updated = queryset.update(activa=True)
        self.message_user(request, f'{updated} oferta(s) activada(s).')
    activar_ofertas.short_description = "✓ Activar ofertas"
    
    def desactivar_ofertas(self, request, queryset):
        updated = queryset.update(activa=False)
        self.message_user(request, f'{updated} oferta(s) desactivada(s).')
    desactivar_ofertas.short_description = "✗ Desactivar ofertas"


# ===== CONFIGURACIÓN PARA PRODUCTO =====
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'precio_unitario', 'stock_badge', 'unidad_medida', 'imagen_preview', 'oferta_badge', 'activo_badge')
    list_display_links = ('id', 'nombre')
    list_filter = ('categoria', 'unidad_medida', 'activo', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion', 'id')
    ordering = ('-fecha_creacion',)
    list_per_page = 20
    autocomplete_fields = ['categoria']
    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'imagen_preview_large')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'categoria', 'unidad_medida', 'activo')
        }),
        ('Inventario y Precios', {
            'fields': ('precio_unitario', 'stock_disponible')
        }),
        ('Imagen', {
            'fields': ('imagen', 'imagen_preview_large'),
            'description': 'Suba una imagen del producto.'
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 5px; object-fit: cover;" />',
                static(f'img/productos/{obj.imagen}')
            )
        return "📷 Sin imagen"
    imagen_preview.short_description = 'Foto'
    
    def imagen_preview_large(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 300px; border-radius: 10px; object-fit: cover; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" />',
                static(f'img/productos/{obj.imagen}')
            )
        return "📷 Sin imagen cargada"
    imagen_preview_large.short_description = 'Vista Previa'
    
    def stock_badge(self, obj):
        if obj.stock_disponible == 0:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">⚠ Agotado</span>'
            )
        elif obj.stock_disponible < 10:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px; font-weight: bold;">⚠ {} unidades</span>',
                obj.stock_disponible
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">✓ {} unidades</span>',
            obj.stock_disponible
        )
    stock_badge.short_description = 'Stock'
    
    def oferta_badge(self, obj):
        if obj.tiene_oferta_activa:
            oferta = obj.ofertas.filter(
                fecha_inicio__lte=timezone.now(),
                fecha_fin__gte=timezone.now(),
                activa=True
            ).first()
            if oferta:
                return format_html(
                    '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">🔥 -{}%</span>',
                    oferta.descuento_porcentaje
                )
        return format_html('<span style="color: #6c757d;">-</span>')
    oferta_badge.short_description = 'Oferta'
    
    def activo_badge(self, obj):
        if obj.activo:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗</span>'
        )
    activo_badge.short_description = 'Activo'

    actions = ['activar_productos', 'desactivar_productos', 'marcar_sin_stock']
    
    def activar_productos(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} producto(s) activado(s).')
    activar_productos.short_description = "✓ Activar productos"
    
    def desactivar_productos(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} producto(s) desactivado(s).')
    desactivar_productos.short_description = "✗ Desactivar productos"
    
    def marcar_sin_stock(self, request, queryset):
        updated = queryset.update(stock_disponible=0)
        self.message_user(request, f'{updated} producto(s) marcado(s) sin stock.')
    marcar_sin_stock.short_description = "⚠ Marcar sin stock"


# ===== CONFIGURACIÓN PARA DETALLE PEDIDO (INLINE) =====
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('precio_compra', 'producto', 'cantidad', 'subtotal_calculado')
    can_delete = False
    fields = ('producto', 'cantidad', 'precio_compra', 'subtotal_calculado')
    
    def subtotal_calculado(self, obj):
        if obj.pk:
            return f"${obj.subtotal:,.0f}"
        return "-"
    subtotal_calculado.short_description = 'Subtotal'


# ===== CONFIGURACIÓN PARA PEDIDO =====
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'correo_cliente', 'fecha_pedido', 'estado_badge', 'total_pedido_formateado', 'metodo_pago', 'tipo_cliente')
    list_display_links = ('id', 'nombre_cliente')
    list_filter = ('estado_pedido', 'metodo_pago', 'fecha_pedido')
    search_fields = ('nombre_cliente', 'correo_cliente', 'telefono_cliente', 'id', 'numero_seguimiento')
    date_hierarchy = 'fecha_pedido'
    inlines = [DetallePedidoInline]
    ordering = ('-fecha_pedido',)
    readonly_fields = ('fecha_pedido', 'total_pedido', 'fecha_pago', 'fecha_envio', 'fecha_entrega')
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('fecha_pedido', 'estado_pedido', 'metodo_pago', 'total_pedido')
        }),
        ('Información del Cliente', {
            'fields': ('usuario', 'nombre_cliente', 'correo_cliente', 'telefono_cliente')
        }),
        ('Dirección de Envío', {
            'fields': ('direccion', 'region', 'comuna', 'codigo_postal', 'referencia_direccion')
        }),
        ('Seguimiento', {
            'fields': ('numero_seguimiento', 'fecha_pago', 'fecha_envio', 'fecha_entrega'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notas_pedido',),
            'classes': ('collapse',)
        }),
    )
    
    def total_pedido_formateado(self, obj):
        return f"${obj.total_pedido:,.0f}"
    total_pedido_formateado.short_description = 'Total'
    total_pedido_formateado.admin_order_field = 'total_pedido'
    
    def tipo_cliente(self, obj):
        if obj.es_invitado():
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">👤 Invitado</span>'
            )
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; border-radius: 3px;">👤 Registrado</span>'
        )
    tipo_cliente.short_description = 'Tipo'
    
    def estado_badge(self, obj):
        colores = {
            'pendiente_pago': '#ffc107',
            'pagado': '#28a745',
            'preparando': '#17a2b8',
            'enviado': '#007bff',
            'completado': '#6c757d',
            'cancelado': '#dc3545',
        }
        iconos = {
            'pendiente_pago': '💳',
            'pagado': '✓',
            'preparando': '📦',
            'enviado': '🚚',
            'completado': '✔',
            'cancelado': '❌',
        }
        color = colores.get(obj.estado_pedido, '#6c757d')
        icono = iconos.get(obj.estado_pedido, '')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{} {}</span>',
            color,
            icono,
            obj.get_estado_pedido_display()
        )
    estado_badge.short_description = 'Estado'
    estado_badge.admin_order_field = 'estado_pedido'
    
    actions = ['marcar_como_pagado', 'marcar_como_enviado', 'marcar_como_completado', 'cancelar_pedidos']
    
    def marcar_como_pagado(self, request, queryset):
        count = 0
        for pedido in queryset.filter(estado_pedido='pendiente_pago'):
            pedido.marcar_como_pagado()
            count += 1
        self.message_user(request, f'{count} pedido(s) marcado(s) como pagado.')
    marcar_como_pagado.short_description = "✅ Marcar como Pagado"
    
    def marcar_como_enviado(self, request, queryset):
        count = 0
        for pedido in queryset.filter(estado_pedido__in=['pagado', 'preparando']):
            pedido.marcar_como_enviado()
            count += 1
        self.message_user(request, f'{count} pedido(s) marcado(s) como enviado.')
    marcar_como_enviado.short_description = "📦 Marcar como Enviado"
    
    def marcar_como_completado(self, request, queryset):
        count = 0
        for pedido in queryset.filter(estado_pedido='enviado'):
            pedido.marcar_como_completado()
            count += 1
        self.message_user(request, f'{count} pedido(s) marcado(s) como completado.')
    marcar_como_completado.short_description = "✔️ Marcar como Completado"
    
    def cancelar_pedidos(self, request, queryset):
        updated = queryset.filter(estado_pedido__in=['pendiente_pago', 'pagado']).update(
            estado_pedido='cancelado'
        )
        self.message_user(request, f'{updated} pedido(s) cancelado(s).')
    cancelar_pedidos.short_description = "❌ Cancelar Pedidos"


# ===== CONFIGURACIÓN PARA DETALLE PEDIDO =====
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'producto', 'cantidad', 'precio_compra', 'subtotal_formateado')
    list_display_links = ('id',)
    list_filter = ('pedido__estado_pedido', 'producto__categoria')
    search_fields = ('pedido__id', 'producto__nombre', 'id')
    ordering = ('-id',)
    autocomplete_fields = ['pedido', 'producto']
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    def subtotal_formateado(self, obj):
        return f'${obj.subtotal:,.0f}'
    subtotal_formateado.short_description = 'Subtotal'


# ===== PERSONALIZACIÓN DEL SITIO ADMIN =====
admin.site.site_header = "Tres En Uno - Panel de Administración"
admin.site.site_title = "Tres En Uno Admin"
admin.site.index_title = "Sistema de Gestión - Dashboard"

# ===== LINK AL DASHBOARD EN EL INDEX DEL ADMIN =====
admin.site.index_template = 'admin/custom_index.html'