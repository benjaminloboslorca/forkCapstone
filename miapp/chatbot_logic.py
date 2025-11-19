# miapp/chatbot_logic.py

# Diccionario de respuestas del chatbot
RESPUESTAS = {
    'contacto_venta': '📞 Puedes contactarnos al correo: ventas@tresenuno.cl o al teléfono +56 9 1234 5678',
    'cancelar_pedido': '❌ Para cancelar tu pedido, ve a "Mis Pedidos" en tu perfil y selecciona la opción "Cancelar". Si ya fue despachado, contacta a soporte.',
    'informacion_envio': '📦 Los envíos se realizan en 3-5 días hábiles. Puedes rastrear tu pedido desde "Mis Pedidos".',
    'correo': '✉️ Nuestro correo de contacto es: info@tresenuno.cl',
    'info_producto': 'ℹ️ Puedes encontrar información detallada de cada producto en su página, incluyendo características, precio y disponibilidad.',
    'recuperar_contraseña': '🔑 Para recuperar tu contraseña, haz clic en "¿Olvidaste tu contraseña?" en la página de inicio de sesión.',
    'saludo': '👋 ¡Hola! Bienvenido a Tres en Uno. ¿En qué puedo ayudarte hoy?',
    'despedida': '👋 ¡Hasta pronto! Que tengas un excelente día.',
    'agradecimiento': '😊 ¡De nada! Estoy aquí para ayudarte en lo que necesites.',
}

# Respuesta por defecto cuando no se entiende la pregunta
FALLBACK = '🤔 Disculpa, no estoy seguro de entender tu pregunta. ¿Podrías reformularla? También puedes elegir una de las opciones sugeridas.'


def best_intent(mensaje):
    """
    Determina la mejor intención basada en el mensaje del usuario.
    Retorna una clave que corresponde a RESPUESTAS o None si no hay coincidencia.
    """
    if not mensaje:
        return None
    
    # Convertir a minúsculas para comparación
    mensaje = mensaje.lower()
    
    # Detección de intenciones basada en palabras clave
    
    # Contacto de venta
    if any(word in mensaje for word in ['contacto', 'venta', 'ventas', 'vendedor', 'telefono', 'teléfono', 'llamar']):
        return 'contacto_venta'
    
    # Cancelar pedido
    if any(word in mensaje for word in ['cancelar', 'anular', 'devolver']) and 'pedido' in mensaje:
        return 'cancelar_pedido'
    
    # Información de envío
    if any(word in mensaje for word in ['envio', 'envío', 'despacho', 'entrega', 'delivery', 'shipping']):
        return 'informacion_envio'
    
    # Correo
    if any(word in mensaje for word in ['correo', 'email', 'mail', 'e-mail']):
        return 'correo'
    
    # Información del producto
    if any(word in mensaje for word in ['producto', 'información', 'informacion', 'detalle', 'caracteristica', 'característica']):
        return 'info_producto'
    
    # Recuperar contraseña
    if any(word in mensaje for word in ['contraseña', 'contrasena', 'password', 'olvidé', 'olvide', 'recuperar']):
        return 'recuperar_contraseña'
    
    # Saludos
    if any(word in mensaje for word in ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos', 'hey', 'hi']):
        return 'saludo'
    
    # Despedidas
    if any(word in mensaje for word in ['adiós', 'adios', 'chao', 'hasta luego', 'nos vemos', 'bye']):
        return 'despedida'
    
    # Agradecimientos
    if any(word in mensaje for word in ['gracias', 'muchas gracias', 'thanks', 'thank you', 'agradezco']):
        return 'agradecimiento'
    
    # Si no coincide con ninguna intención
    return None