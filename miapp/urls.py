from django.urls import path
from .views import (
    ClienteRegistroAPIView, 
    ClienteLoginAPIView, 
    VerifyTokenAPIView,
    ClienteDetailAPIView,
    CategoriaListAPIView,
    ProductoListAPIView,
    ProductoDetailAPIView,
    CarritoView,
    CarritoItemView,
    CarritoVaciarView,
    CheckoutAPIView,
    MisPedidosAPIView,
    DetallePedidoAPIView,
    perfil_temporal,
    actualizar_perfil
)
from . import views

urlpatterns = [
    # ===== RUTAS DE PÁGINAS HTML =====
    path('', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('productos/', views.listar_productos, name='listar_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido-confirmado/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('contacto/', views.ventas, name='contacto'),
    path('perfil/', views.perfil_temporal, name='perfil'),
    
    # ===== RUTAS DE AUTENTICACIÓN =====
    path('auth/register', views.cliente_registro_form, name='registro-form'),
    path('auth/login', views.cliente_login_form, name='login-form'),
    
    # ===== API ENDPOINTS - AUTENTICACIÓN =====
    path('api/auth/register', ClienteRegistroAPIView.as_view(), name='cliente-registro'),
    path('api/auth/login', ClienteLoginAPIView.as_view(), name='cliente-login'),
    path('api/auth/verify-token', VerifyTokenAPIView.as_view(), name='verify-token'),
    path('api/clientes/me', ClienteDetailAPIView.as_view(), name='cliente-detail'),
    
    # ===== API ENDPOINTS - CATEGORÍAS (PÚBLICAS) =====
    path('api/public/categories/', CategoriaListAPIView.as_view(), name='api-categorias-list'),
    
    # ===== API ENDPOINTS - PRODUCTOS (PÚBLICOS) =====
    path('api/public/products/', ProductoListAPIView.as_view(), name='productos-list'),
    path('api/public/products/<int:pk>/', ProductoDetailAPIView.as_view(), name='producto-detail'),
    
    # ===== API ENDPOINTS - CARRITO =====
    path('api/cart/', CarritoView.as_view(), name='carrito'),
    path('api/cart/<int:producto_id>/', CarritoItemView.as_view(), name='carrito-item'),
    path('api/cart/clear/', CarritoVaciarView.as_view(), name='carrito-vaciar'),
    
    # ===== API ENDPOINTS - CHECKOUT Y PEDIDOS =====
    path('api/checkout/', CheckoutAPIView.as_view(), name='checkout-api'),
    path('api/mis-pedidos/', MisPedidosAPIView.as_view(), name='mis-pedidos-api'),
    path('api/pedidos/<int:pk>/', DetallePedidoAPIView.as_view(), name='detalle-pedido-api'),

    # ===== CHATBOT =====
    path('chatbot/ask/', views.chatbot_ask, name='chatbot-ask'),
    
    # ===== Perfil =====
    path('perfil/', perfil_temporal, name='perfil'),
    path('api/perfil/actualizar/', actualizar_perfil, name='actualizar-perfil'),
]
