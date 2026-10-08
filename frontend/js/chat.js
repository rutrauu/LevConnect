/**
 * LevConnect - Chat Module
 * WhatsApp Multi-Agent Inbox & Real-time Messaging feed
 */

import { api } from './api.js';

export const ChatModule = {
  currentChatId: null,
  chats: [],
  currentFilter: 'all',
  searchQuery: '',

  async init(onChatSelectedCallback) {
    this.onChatSelected = onChatSelectedCallback;
    this.bindEvents();
    await this.loadChats();
    
    // Select first chat by default
    if (this.chats.length > 0) {
      this.selectChat(this.chats[0].id);
    }
  },

  bindEvents() {
    // Search input
    const searchInput = document.getElementById('input-search-chats');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value;
        this.loadChats();
      });
    }

    // Filter chips
    const filterContainer = document.getElementById('inbox-status-filters');
    if (filterContainer) {
      filterContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('filter-chip')) {
          filterContainer.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
          e.target.classList.add('active');
          this.currentFilter = e.target.dataset.status;
          this.loadChats();
        }
      });
    }

    // Message composer form
    const formComposer = document.getElementById('form-chat-composer');
    if (formComposer) {
      formComposer.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleSendMessage();
      });
    }

    // Quick reply pills
    document.querySelectorAll('.quick-reply-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        const replyText = btn.dataset.reply;
        const inputMsg = document.getElementById('input-composer-text');
        if (inputMsg) {
          inputMsg.value = replyText;
          inputMsg.focus();
        }
      });
    });

    // Chat status dropdown change
    const statusSelect = document.getElementById('select-active-chat-status');
    if (statusSelect) {
      statusSelect.addEventListener('change', async (e) => {
        if (!this.currentChatId) return;
        try {
          await api.updateChatStatus(this.currentChatId, e.target.value);
          window.app.showToast('Status do atendimento atualizado!');
          this.loadChats(false);
        } catch (err) {
          console.error(err);
        }
      });
    }
  },

  async loadChats(autoSelectFirstIfEmpty = false) {
    try {
      const data = await api.getChats(this.currentFilter, this.searchQuery);
      this.chats = data.chats || [];
      this.renderChatsList();
      
      const counter = document.getElementById('inbox-total-counter');
      if (counter) {
        counter.textContent = `${this.chats.length} conversas`;
      }

      if (autoSelectFirstIfEmpty && !this.currentChatId && this.chats.length > 0) {
        this.selectChat(this.chats[0].id);
      }
    } catch (err) {
      console.error('Erro ao carregar chats:', err);
    }
  },

  renderChatsList() {
    const container = document.getElementById('chats-list-container');
    if (!container) return;

    if (this.chats.length === 0) {
      container.innerHTML = `
        <div style="padding: 2rem 1rem; text-align: center; color: var(--text-dim); font-size: 0.85rem;">
          <i class="fa-regular fa-comment-dots" style="font-size: 2rem; margin-bottom: 0.5rem; display: block; opacity: 0.4;"></i>
          Nenhum atendimento encontrado com este filtro.
        </div>
      `;
      return;
    }

    container.innerHTML = this.chats.map(chat => {
      const isActive = chat.id === this.currentChatId ? 'active' : '';
      const statusLabelMap = {
        'open': 'Aberto',
        'in_progress': 'Atendendo',
        'reserved': 'Reservado',
        'closed': 'Finalizado'
      };

      return `
        <div class="chat-item ${isActive}" data-chat-id="${chat.id}">
          <div class="chat-avatar-wrapper">
            <img src="${chat.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100'}" alt="${chat.customer_name}" class="chat-avatar">
            <span class="wa-indicator-badge"><i class="fa-brands fa-whatsapp"></i></span>
          </div>

          <div class="chat-content-meta">
            <div class="chat-row-top">
              <span class="chat-customer-name">${chat.customer_name}</span>
              <span class="chat-time">${chat.last_time || ''}</span>
            </div>

            <div class="chat-row-mid">
              <span class="chat-preview-text">${chat.last_message || 'Iniciou a conversa'}</span>
              ${chat.unread > 0 ? `<span class="badge-unread">${chat.unread}</span>` : ''}
            </div>

            <div class="chat-row-bottom">
              <span class="chat-store-tag">
                <i class="fa-solid fa-store" style="font-size: 9px;"></i> ${chat.seller_store || 'Charqueadas'}
              </span>
              <span class="status-badge ${chat.status}">${statusLabelMap[chat.status] || chat.status}</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Attach click events
    container.querySelectorAll('.chat-item').forEach(item => {
      item.addEventListener('click', () => {
        const chatId = item.dataset.chatId;
        this.selectChat(chatId);
      });
    });
  },

  async selectChat(chatId) {
    this.currentChatId = chatId;
    
    // Update active highlight in list
    document.querySelectorAll('.chat-item').forEach(item => {
      if (item.dataset.chatId === chatId) {
        item.classList.add('active');
        const badge = item.querySelector('.badge-unread');
        if (badge) badge.remove();
      } else {
        item.classList.remove('active');
      }
    });

    try {
      const data = await api.getChat(chatId);
      const chat = data.chat;
      const customer = data.customer;

      this.renderChatHeader(chat, customer);
      this.renderMessagesFeed(chat.messages || []);

      // Notify parent app to update Customer Profile and Stock context
      if (this.onChatSelected && customer) {
        this.onChatSelected(customer, chat);
      }
    } catch (err) {
      console.error('Erro ao abrir conversa:', err);
    }
  },

  renderChatHeader(chat, customer) {
    const avatar = document.getElementById('chat-avatar-current');
    const name = document.getElementById('chat-customer-name-display');
    const phone = document.getElementById('chat-customer-phone-display');
    const city = document.getElementById('chat-customer-city-display');
    const vipTag = document.getElementById('chat-vip-tag');
    const statusSelect = document.getElementById('select-active-chat-status');

    if (avatar) avatar.src = chat.avatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100';
    if (name) name.textContent = chat.customer_name;
    if (phone) phone.textContent = chat.customer_phone;
    if (city) city.textContent = (customer && customer.city) ? customer.city : (chat.seller_store || 'Charqueadas');
    
    if (vipTag) {
      vipTag.style.display = (customer && customer.vip_status) ? 'inline-block' : 'none';
    }

    if (statusSelect) {
      statusSelect.value = chat.status;
    }
  },

  renderMessagesFeed(messages) {
    const feed = document.getElementById('chat-messages-feed');
    if (!feed) return;

    if (messages.length === 0) {
      feed.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: var(--text-dim); font-size: 0.85rem;">
          Inicie o atendimento com este cliente.
        </div>
      `;
      return;
    }

    let html = `
      <div class="message-date-separator">Hoje • Atendimento Conectado</div>
    `;

    messages.forEach(msg => {
      if (msg.type === 'reservation_voucher' && msg.payload) {
        const p = msg.payload;
        html += `
          <div class="message-bubble reservation-voucher">
            <div class="voucher-card-inner">
              <div class="voucher-header">
                <span class="voucher-title">
                  <i class="fa-solid fa-circle-check"></i> ORDEM DE RESERVA (CLIQUE E RETIRE)
                </span>
                <span class="voucher-code">${p.res_id}</span>
              </div>
              <div class="voucher-grid">
                <div>
                  <div class="voucher-item-lbl">Produto:</div>
                  <div class="voucher-item-val">${p.product_name}</div>
                </div>
                <div>
                  <div class="voucher-item-lbl">Tamanho / Numeração:</div>
                  <div class="voucher-item-val" style="color: #818cf8; font-size: 1rem;">${p.size}</div>
                </div>
                <div>
                  <div class="voucher-item-lbl">Valor na Loja:</div>
                  <div class="voucher-item-val" style="color: #34d399;">${p.price}</div>
                </div>
                <div>
                  <div class="voucher-item-lbl">Loja de Retirada:</div>
                  <div class="voucher-item-val">${p.pickup_store}</div>
                </div>
                ${p.is_inter_store ? `
                  <div class="voucher-inter-badge">
                    <i class="fa-solid fa-truck-ramp-box"></i>
                    Transferência Inter-Lojas: Enviado de ${p.source_store} para ${p.pickup_store}
                  </div>
                ` : ''}
              </div>
              <button class="btn-voucher-action" data-res-id="${p.res_id}">
                <i class="fa-solid fa-qrcode"></i> Visualizar Voucher / QR Code de Balcão
              </button>
            </div>
          </div>
        `;
      } else if (msg.type === 'product_card' && msg.payload) {
        const p = msg.payload;
        html += `
          <div class="message-bubble seller" style="max-width: 80%;">
            <div style="display: flex; gap: 10px; align-items: center; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 8px; margin-bottom: 6px;">
              <img src="${p.image}" alt="${p.name}" style="width: 50px; height: 50px; border-radius: 6px; object-fit: cover;">
              <div>
                <div style="font-weight: 700; font-size: 0.82rem;">${p.name}</div>
                <div style="color: #34d399; font-weight: 800; font-size: 0.85rem;">R$ ${p.price.toFixed(2).replace('.', ',')}</div>
              </div>
            </div>
            <div>${msg.text}</div>
            <div class="message-footer">
              <span>${msg.time}</span>
              <span class="wa-checks"><i class="fa-solid fa-check-double"></i></span>
            </div>
          </div>
        `;
      } else {
        const isSeller = msg.sender === 'seller';
        html += `
          <div class="message-bubble ${isSeller ? 'seller' : 'customer'}">
            <div>${msg.text}</div>
            <div class="message-footer">
              <span>${msg.time}</span>
              ${isSeller ? '<span class="wa-checks"><i class="fa-solid fa-check-double"></i></span>' : ''}
            </div>
          </div>
        `;
      }
    });

    feed.innerHTML = html;
    feed.scrollTop = feed.scrollHeight;

    // Attach voucher modal triggers
    feed.querySelectorAll('.btn-voucher-action').forEach(btn => {
      btn.addEventListener('click', () => {
        const resId = btn.dataset.resId;
        window.app.openVoucherModal(resId);
      });
    });
  },

  async handleSendMessage() {
    const input = document.getElementById('input-composer-text');
    if (!input || !input.value.trim() || !this.currentChatId) return;

    const text = input.value.trim();
    input.value = '';

    try {
      await api.sendMessage(this.currentChatId, {
        sender: 'seller',
        text: text,
        type: 'text'
      });

      // Reload chat feed
      await this.selectChat(this.currentChatId);
      this.loadChats(false);
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
      window.app.showToast('Erro ao enviar mensagem', 'error');
    }
  },

  async sendProductCardToChat(product) {
    if (!this.currentChatId) {
      window.app.showToast('Selecione uma conversa para enviar o produto', 'error');
      return;
    }

    try {
      await api.sendMessage(this.currentChatId, {
        sender: 'seller',
        text: `Aqui está o produto que você procurava: ${product.name} (${product.sku}). Temos disponível para reserva!`,
        type: 'product_card',
        payload: {
          product_id: product.id,
          name: product.name,
          sku: product.sku,
          price: product.price,
          image: product.image
        }
      });

      await this.selectChat(this.currentChatId);
      window.app.showToast('Card do produto enviado no WhatsApp!');
    } catch (err) {
      console.error(err);
    }
  }
};
