/**
 * Chatbot Tres En Uno - Versión Mejorada
 * Sistema de chat flotante con gestión de estado, respuestas rápidas y API REST
 */
(function () {
  'use strict';

  // ============================================
  // UTILIDADES
  // ============================================
  
  /**
   * Ejecuta función cuando el DOM está listo
   */
  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  /**
   * Debounce para optimizar eventos
   */
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // ============================================
  // INICIALIZACIÓN
  // ============================================
  
  ready(function () {
    // Referencias del DOM
    const root = document.getElementById('cb-root');
    const toggle = document.getElementById('cb-toggle');
    
    // Validar elementos esenciales
    if (!root || !toggle) {
      console.error('Chatbot: Elementos esenciales no encontrados (cb-root o cb-toggle)');
      return;
    }

    const minimizeBtn = root.querySelector('.cb-minimize');
    const messages = document.getElementById('cb-messages');
    const input = document.getElementById('cb-input');
    const send = document.getElementById('cb-send');
    const quickWrap = document.getElementById('cb-quick');

    // Constantes
    const STORAGE_KEY = 'cb_state'; // Estados: 'open' | 'min' | 'hidden'
    const TYPING_DELAY = 800; // Milisegundos antes de mostrar respuesta
    const MAX_MESSAGE_LENGTH = 500; // Caracteres máximos por mensaje

    // Estado del chatbot
    let isProcessing = false;

    // ============================================
    // GESTIÓN DE ESTADO
    // ============================================

    /**
     * Establece el estado visual del chatbot
     * @param {string} state - 'open', 'min' o 'hidden'
     */
    function setState(state) {
      root.classList.remove('cb-hidden', 'cb-min');
      
      if (state === 'open') {
        // Caja visible, FAB oculto por CSS
        input.focus();
      } else if (state === 'min') {
        // Minimizado: oculta la caja, muestra el FAB
        root.classList.add('cb-min');
      } else {
        // Oculto completamente
        root.classList.add('cb-hidden', 'cb-min');
      }
      
      try {
        localStorage.setItem(STORAGE_KEY, state);
      } catch (e) {
        console.warn('No se pudo guardar el estado del chatbot:', e);
      }
    }

    /**
     * Obtiene el estado guardado del chatbot
     * @returns {string} Estado guardado o 'hidden' por defecto
     */
    function getState() {
      try {
        return localStorage.getItem(STORAGE_KEY) || 'hidden';
      } catch (e) {
        console.warn('No se pudo leer el estado del chatbot:', e);
        return 'hidden';
      }
    }

    // Establecer estado inicial
    setState(getState());

    // ============================================
    // FUNCIONES DE UI
    // ============================================

    /**
     * Hace scroll automático al último mensaje
     */
    function scrollBottom() {
      if (messages) {
        requestAnimationFrame(() => {
          messages.scrollTop = messages.scrollHeight;
        });
      }
    }

    /**
     * Crea y muestra una burbuja de mensaje
     * @param {string} text - Texto del mensaje
     * @param {string} who - 'bot' o 'user'
     * @param {boolean} showTime - Mostrar timestamp
     */
    function bubble(text, who, showTime = true) {
      if (!text || !messages) return;

      const row = document.createElement('div');
      row.className = `cb-msg ${who === 'bot' ? 'cb-bot' : 'cb-user'}`;
      
      const bubbleDiv = document.createElement('div');
      bubbleDiv.className = 'cb-bubble';
      bubbleDiv.textContent = text;
      
      row.appendChild(bubbleDiv);

      // Agregar timestamp si está habilitado
      if (showTime) {
        const timeSpan = document.createElement('span');
        timeSpan.className = 'cb-time';
        timeSpan.textContent = new Date().toLocaleTimeString('es-CL', { 
          hour: '2-digit', 
          minute: '2-digit' 
        });
        row.appendChild(timeSpan);
      }

      // Animación de entrada
      row.style.opacity = '0';
      row.style.transform = 'translateY(10px)';
      messages.appendChild(row);
      
      requestAnimationFrame(() => {
        row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        row.style.opacity = '1';
        row.style.transform = 'translateY(0)';
      });

      scrollBottom();
    }

    /**
     * Muestra indicador de "escribiendo..."
     * @returns {HTMLElement} Elemento del indicador
     */
    function showTypingIndicator() {
      const typing = document.createElement('div');
      typing.className = 'cb-typing';
      typing.id = 'cb-typing-indicator';
      typing.innerHTML = `
        <div class="cb-typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      `;
      messages.appendChild(typing);
      scrollBottom();
      return typing;
    }

    /**
     * Oculta y elimina el indicador de escritura
     */
    function hideTypingIndicator() {
      const typing = document.getElementById('cb-typing-indicator');
      if (typing) {
        typing.style.opacity = '0';
        setTimeout(() => typing.remove(), 300);
      }
    }

    /**
     * Renderiza los botones de respuesta rápida
     * @param {Array} list - Array de strings con las opciones
     */
    function renderQuick(list) {
      if (!quickWrap) return;
      
      quickWrap.innerHTML = '';
      
      if (!list || list.length === 0) {
        quickWrap.style.display = 'none';
        return;
      }

      quickWrap.style.display = 'flex';
      
      list.forEach((q) => {
        const chip = document.createElement('button');
        chip.className = 'cb-chip';
        chip.type = 'button';
        chip.textContent = q;
        chip.setAttribute('aria-label', `Pregunta rápida: ${q}`);
        
        chip.addEventListener('click', (e) => {
          e.preventDefault();
          if (!isProcessing) {
            input.value = q;
            sendMessage();
          }
        });
        
        quickWrap.appendChild(chip);
      });
    }

    /**
     * Deshabilita los controles de entrada
     */
    function disableControls() {
      if (input) input.disabled = true;
      if (send) send.disabled = true;
      isProcessing = true;
    }

    /**
     * Habilita los controles de entrada
     */
    function enableControls() {
      if (input) {
        input.disabled = false;
        input.focus();
      }
      if (send) send.disabled = false;
      isProcessing = false;
    }

    // ============================================
    // COMUNICACIÓN CON API
    // ============================================

    /**
     * Envía mensaje al backend y obtiene respuesta
     * @param {string} message - Mensaje del usuario
     * @returns {Promise<Object>} Respuesta del servidor
     */
    async function askAPI(message) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 segundos timeout

      try {
        const res = await fetch('/chatbot/ask/', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message }),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!res.ok) {
          throw new Error(`Error del servidor: ${res.status}`);
        }

        return await res.json();
      } catch (error) {
        if (error.name === 'AbortError') {
          throw new Error('La solicitud tardó demasiado tiempo');
        }
        throw error;
      }
    }

    /**
     * Envía mensaje y procesa respuesta
     * @param {Event} e - Evento del envío (opcional)
     */
    async function sendMessage(e) {
      if (e && e.preventDefault) e.preventDefault();
      
      // Validaciones
      if (isProcessing) return;
      
      const text = (input.value || '').trim();
      
      if (!text) {
        input.focus();
        return;
      }

      if (text.length > MAX_MESSAGE_LENGTH) {
        bubble(`El mensaje es demasiado largo. Máximo ${MAX_MESSAGE_LENGTH} caracteres.`, 'bot', false);
        return;
      }

      // Deshabilitar controles mientras se procesa
      disableControls();
      
      // Mostrar mensaje del usuario
      bubble(text, 'user');
      input.value = '';

      // Mostrar indicador de escritura
      const typingIndicator = showTypingIndicator();

      try {
        // Simular delay para parecer más natural
        await new Promise(resolve => setTimeout(resolve, TYPING_DELAY));
        
        // Llamar a la API
        const data = await askAPI(text);
        
        // Ocultar indicador
        hideTypingIndicator();
        
        // Mostrar respuesta del bot
        if (data.reply) {
          bubble(data.reply, 'bot');
        }
        
        // Actualizar respuestas rápidas si vienen en la respuesta
        if (data.quick && Array.isArray(data.quick)) {
          renderQuick(data.quick);
        }

      } catch (err) {
        console.error('Error en chatbot:', err);
        hideTypingIndicator();
        
        // Mensaje de error amigable
        let errorMsg = 'Lo siento, hubo un problema al procesar tu mensaje. ';
        
        if (err.message.includes('tardó demasiado')) {
          errorMsg += 'El servidor tardó demasiado en responder.';
        } else if (err.message.includes('Network')) {
          errorMsg += 'Verifica tu conexión a internet.';
        } else {
          errorMsg += 'Por favor, intenta nuevamente.';
        }
        
        bubble(errorMsg, 'bot', false);
      } finally {
        // Re-habilitar controles
        enableControls();
      }
    }

    // ============================================
    // EVENT LISTENERS
    // ============================================

    // Abrir chatbot con el FAB
    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      setState('open');
      scrollBottom();
    });

    // Minimizar chatbot
    if (minimizeBtn) {
      minimizeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        setState('min');
      });
    }

    // Enviar mensaje con botón
    if (send) {
      send.addEventListener('click', sendMessage);
    }

    // Enviar mensaje con Enter
    if (input) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage(e);
        }
      });

      // Contador de caracteres (opcional)
      input.addEventListener('input', debounce(() => {
        const remaining = MAX_MESSAGE_LENGTH - input.value.length;
        if (remaining < 50) {
          input.setAttribute('title', `${remaining} caracteres restantes`);
        }
      }, 200));
    }

    // Cerrar con tecla Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && getState() === 'open') {
        setState('min');
      }
    });

    // ============================================
    // INICIALIZACIÓN DE RESPUESTAS RÁPIDAS
    // ============================================

    // Cargar respuestas rápidas iniciales
    const initialQuickReplies = [
      "¿tienes algun contacto de venta?",
      "¿como puedo cancelar mi pedido?",
      "informacion de envio",
      "¿poseen correo?",
      "¿donde encuentro informacion del producto?",
      "olvide mi contraseña."
    ];

    renderQuick(initialQuickReplies);

    // Mensaje de bienvenida si es la primera vez
    try {
      const hasSeenWelcome = localStorage.getItem('cb_welcome_shown');
      if (!hasSeenWelcome && getState() === 'open') {
        setTimeout(() => {
          bubble('¡Hola! 👋 Soy tu asistente virtual. ¿En qué puedo ayudarte?', 'bot');
          localStorage.setItem('cb_welcome_shown', 'true');
        }, 500);
      }
    } catch (e) {
      console.warn('No se pudo verificar mensaje de bienvenida:', e);
    }

    // ============================================
    // MANEJO DE VISIBILIDAD DE PÁGINA
    // ============================================

    // Pausar cuando la pestaña no está visible (optimización)
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        // Página oculta - pausar animaciones si es necesario
      } else {
        // Página visible - reanudar
        scrollBottom();
      }
    });

    console.log('✅ Chatbot Tres En Uno inicializado correctamente');
  });
})();