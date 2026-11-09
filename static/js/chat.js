// TechHelp IA - Interactive Chat Controller

document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-messages-container');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const activeConvId = chatContainer ? chatContainer.dataset.convId : null;
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('chat-sidebar');
    const newChatBtn = document.getElementById('new-chat-btn');
    const limitWarning = document.getElementById('limit-warning-modal');

    // Inicializar Markdown & Resaltado de Sintaxis
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    function formatAllCodeBlocks() {
        if (!chatContainer) return;
        chatContainer.querySelectorAll('pre').forEach((pre) => {
            if (pre.querySelector('.copy-code-btn')) return;
            const btn = document.createElement('button');
            btn.className = 'copy-code-btn';
            btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copiar';
            btn.addEventListener('click', () => {
                const code = pre.querySelector('code') ? pre.querySelector('code').innerText : pre.innerText;
                navigator.clipboard.writeText(code).then(() => {
                    btn.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i> ¡Copiado!';
                    setTimeout(() => {
                        btn.innerHTML = '<i class="fa-regular fa-copy"></i> Copiar';
                    }, 2000);
                });
            });
            pre.appendChild(btn);
        });
        document.querySelectorAll('pre code').forEach((el) => {
            hljs.highlightElement(el);
        });
    }

    // Auto-scroll al fondo
    function scrollToBottom() {
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    // Renderizar mensajes existentes con Markdown
    document.querySelectorAll('.ai-content-raw').forEach((el) => {
        const raw = el.textContent;
        el.innerHTML = marked.parse(raw);
        el.classList.remove('ai-content-raw');
    });
    formatAllCodeBlocks();
    scrollToBottom();

    // Auto-ajuste de altura para el textarea
    if (messageInput) {
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight < 160 ? this.scrollHeight : 160) + 'px';
        });

        // Enviar con Enter (sin Shift)
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    // Enviar Mensaje
    if (chatForm && activeConvId) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = messageInput.value.trim();
            if (!text) return;

            // Deshabilitar entrada mientras procesa
            messageInput.value = '';
            messageInput.style.height = 'auto';
            messageInput.disabled = true;
            sendButton.disabled = true;

            // 1. Añadir burbuja de usuario a la UI
            appendUserMessage(text);
            scrollToBottom();

            // 2. Mostrar indicador de "escribiendo..."
            if (typingIndicator) {
                typingIndicator.classList.remove('hidden');
                scrollToBottom();
            }

            try {
                const response = await fetch(`/api/chat/${activeConvId}/send`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: text })
                });

                const data = await response.json();

                if (typingIndicator) {
                    typingIndicator.classList.add('hidden');
                }

                if (response.status === 403 && data.limit_reached) {
                    // Mostrar modal de límite alcanzado
                    showLimitModal(data.error);
                    return;
                }

                if (!response.ok) {
                    appendSystemError(data.error || 'Ocurrió un error al procesar tu solicitud.');
                    return;
                }

                // 3. Renderizar respuesta de la IA
                appendAssistantMessage(data.reply);
                formatAllCodeBlocks();
                scrollToBottom();

                // Actualizar título en la barra superior y lateral si cambió
                if (data.conversation_title) {
                    const titleEl = document.getElementById('active-conversation-title');
                    if (titleEl) titleEl.textContent = data.conversation_title;
                    const sidebarActiveTitle = document.querySelector(`.conv-item[data-id="${activeConvId}"] .conv-title`);
                    if (sidebarActiveTitle) sidebarActiveTitle.textContent = data.conversation_title;
                }

                // Actualizar contador de consultas si existe el elemento
                const countBadge = document.getElementById('daily-queries-badge');
                if (countBadge && data.limit_msg) {
                    countBadge.textContent = data.limit_msg;
                }

            } catch (err) {
                if (typingIndicator) typingIndicator.classList.add('hidden');
                appendSystemError('Error de conexión con el servidor. Revisa tu conexión a internet.');
            } finally {
                messageInput.disabled = false;
                sendButton.disabled = false;
                messageInput.focus();
            }
        });
    }

    // Funciones auxiliares de renderizado de burbujas
    function appendUserMessage(text) {
        const bubble = document.createElement('div');
        bubble.className = 'flex justify-end gap-3 mb-6 animate-fade-in';
        bubble.innerHTML = `
            <div class="max-w-[85%] md:max-w-[75%] rounded-2xl bg-indigo-600 text-white px-4 py-3 shadow-md shadow-indigo-600/20 text-sm">
                <p class="whitespace-pre-wrap">${escapeHtml(text)}</p>
            </div>
            <div class="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs text-indigo-400 font-bold shrink-0">
                <i class="fa-solid fa-user"></i>
            </div>
        `;
        chatContainer.insertBefore(bubble, typingIndicator);
    }

    function appendAssistantMessage(markdownContent) {
        const bubble = document.createElement('div');
        bubble.className = 'flex justify-start gap-3 mb-6 animate-fade-in';
        const parsedHtml = marked.parse(markdownContent);
        bubble.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-emerald-400 p-0.5 shrink-0 shadow-lg shadow-indigo-500/20">
                <div class="w-full h-full bg-slate-950 rounded-full flex items-center justify-center">
                    <i class="fa-solid fa-microchip text-emerald-400 text-xs"></i>
                </div>
            </div>
            <div class="max-w-[90%] md:max-w-[80%] rounded-2xl bg-slate-900 border border-slate-800 text-slate-100 px-5 py-4 shadow-xl prose-techhelp">
                ${parsedHtml}
            </div>
        `;
        chatContainer.insertBefore(bubble, typingIndicator);
    }

    function appendSystemError(errorText) {
        const bubble = document.createElement('div');
        bubble.className = 'flex justify-center mb-6 animate-fade-in';
        bubble.innerHTML = `
            <div class="rounded-xl bg-rose-950/70 border border-rose-800/80 px-4 py-3 text-rose-300 text-xs flex items-center gap-2.5">
                <i class="fa-solid fa-circle-exclamation text-rose-400"></i>
                <span>${escapeHtml(errorText)}</span>
            </div>
        `;
        chatContainer.insertBefore(bubble, typingIndicator);
    }

    function escapeHtml(string) {
        const div = document.createElement('div');
        div.innerText = string;
        return div.innerHTML;
    }

    // Modal de límite alcanzado
    function showLimitModal(msg) {
        if (limitWarning) {
            const msgEl = document.getElementById('limit-modal-msg');
            if (msgEl && msg) msgEl.textContent = msg;
            limitWarning.classList.remove('hidden');
        } else {
            alert(msg || 'Límite diario alcanzado. Por favor suscríbete a Pro para continuar.');
            window.location.href = '/pricing';
        }
    }

    // Botones de sugerencias rápidas
    document.querySelectorAll('.suggestion-chip').forEach((btn) => {
        btn.addEventListener('click', () => {
            if (messageInput) {
                messageInput.value = btn.dataset.prompt;
                messageInput.focus();
            }
        });
    });

    // Crear Nueva Conversación
    if (newChatBtn) {
        newChatBtn.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/conversations', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: 'Nueva incidencia técnica' })
                });
                const data = await res.json();
                if (data.id) {
                    window.location.href = `/chat/${data.id}`;
                }
            } catch (e) {
                console.error("Error creando incidencia:", e);
            }
        });
    }

    // Eliminar Conversación
    document.querySelectorAll('.delete-conv-btn').forEach((btn) => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            e.preventDefault();
            const convId = btn.dataset.id;
            if (confirm('¿Seguro que deseas eliminar este historial de incidencia?')) {
                const res = await fetch(`/api/conversations/${convId}`, { method: 'DELETE' });
                if (res.ok) {
                    window.location.href = '/chat';
                }
            }
        });
    });

    // Toggle Sidebar en móvil
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('-translate-x-full');
        });
    }
});
