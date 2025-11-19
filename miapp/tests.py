# tests.py - COMPLETO Y CORREGIDO

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Producto, Categoria, Pedido, DetallePedido
import json

User = get_user_model()

class TestsCriticos(TestCase):
    
    def setUp(self):
        """Datos de prueba básicos"""
        self.client = Client()
        self.user = User.objects.create_user(
            correo='test@test.com',
            nombre='Test User',
            password='test123'
        )
        self.categoria = Categoria.objects.create(
            nombre='Test',
            activa=True
        )
        self.producto = Producto.objects.create(
            nombre='Tomate',
            descripcion='Tomate fresco de prueba',
            precio_unitario=1000,
            stock_disponible=10,
            categoria=self.categoria,
            activo=True
        )
    
    # TEST 1: Registro funciona (CORREGIDO)
    def test_registro_usuario(self):
        """Verifica que se puede registrar un nuevo usuario"""
        response = self.client.post('/api/auth/register', 
            data=json.dumps({
                'nombre': 'Nuevo Usuario',
                'correo': 'nuevo@test.com',
                'telefono': '912345678',
                'password': 'testpass123',
                'password2': 'testpass123'
            }),
            content_type='application/json'
        )
        
        # Ver qué pasó (puedes quitar esto después)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 201:
            print(f"Response: {response.content.decode()}")
        
        # Verifica que el usuario fue creado
        self.assertTrue(User.objects.filter(correo='nuevo@test.com').exists())
    
    # TEST 2: Login funciona
    def test_login_usuario(self):
        """Verifica que un usuario puede hacer login"""
        response = self.client.post('/api/auth/login',
            data=json.dumps({
                'correo': 'test@test.com',
                'password': 'test123'
            }),
            content_type='application/json'
        )
        # Verifica que la respuesta es exitosa (200 o 201)
        self.assertIn(response.status_code, [200, 201])
    
    # TEST 3: Agregar al carrito funciona
    def test_agregar_carrito(self):
        """Verifica que se puede agregar un producto al carrito"""
        # Login primero
        self.client.force_login(self.user)
        
        # Agregar producto al carrito via API
        response = self.client.post('/api/cart/',
            data=json.dumps({
                'producto_id': self.producto.id,
                'cantidad': 2
            }),
            content_type='application/json'
        )
        
        # Verifica que fue exitoso
        self.assertIn(response.status_code, [200, 201])
    
    # TEST 4: Ver carrito funciona
    def test_ver_carrito(self):
        """Verifica que se puede ver el carrito"""
        self.client.force_login(self.user)
        
        response = self.client.get('/carrito/')
        
        # Verifica que la página carga
        self.assertEqual(response.status_code, 200)
    
    # TEST 5: Producto sin stock no permite compra
    def test_producto_sin_stock(self):
        """Verifica que un producto sin stock no se puede agregar al carrito"""
        self.client.force_login(self.user)
        
        # Poner stock en 0
        self.producto.stock_disponible = 0
        self.producto.save()
        
        # Intentar agregar al carrito
        response = self.client.post('/api/cart/',
            data=json.dumps({
                'producto_id': self.producto.id,
                'cantidad': 1
            }),
            content_type='application/json'
        )
        
        # Debe fallar (400 o 404)
        self.assertIn(response.status_code, [400, 404, 422])