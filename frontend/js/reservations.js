/**
 * LevConnect - Reservations & Inter-Store Malote Logistics Module
 */

import { api } from './api.js';

export const ReservationsModule = {
  reservations: [],
  currentStatusFilter: 'all',

  async init() {
    this.bindEvents();
    await this.loadReservations();
  },

  bindEvents() {
    const filterSelect = document.getElementById('select-res-status-filter');
    if (filterSelect) {
      filterSelect.addEventListener('change', (e) => {
        this.currentStatusFilter = e.target.value;
        this.loadReservations();
      });
    }

    const btnSubmit = document.getElementById('btn-submit-create-reservation');
    if (btnSubmit) {
      btnSubmit.addEventListener('click', () => this.handleCreateReservation());
    }

    const pickupSelect = document.getElementById('res-modal-pickup-store');
    const sourceSelect = document.getElementById('res-modal-source-store');
    const alertBox = document.getElementById('res-transfer-alert-box');

    const checkTransferAlert = () => {
      if (pickupSelect && sourceSelect && alertBox) {
        if (pickupSelect.value !== sourceSelect.value) {
          alertBox.style.display = 'block';
        } else {
          alertBox.style.display = 'none';
        }
      }
    };

    if (pickupSelect) pickupSelect.addEventListener('change', checkTransferAlert);
    if (sourceSelect) sourceSelect.addEventListener('change', checkTransferAlert);
  },

  async loadReservations() {
    try {
      const data = await api.getReservations('all', this.currentStatusFilter);
      this.reservations = data.reservations || [];
      this.renderReservationsList();

      const badge = document.getElementById('tab-res-badge');
      if (badge) {
        badge.textContent = this.reservations.length;
      }
    } catch (err) {
      console.error('Erro ao carregar reservas:', err);
    }
  },

  renderReservationsList() {
    const container = document.getElementById('reservations-list-container');
    if (!container) return;

    if (this.reservations.length === 0) {
      container.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: var(--text-dim); font-size: 0.85rem;">
          Nenhuma ordem de reserva ativa.
        </div>
      `;
      return;
    }

    const statusLabelMap = {
      'aguardando_separacao': 'Aguardando Separação',
      'em_transito': 'Em Trânsito Inter-Lojas',
      'pronto_retirada': 'Pronta para Retirada',
      'concluido': 'Retirada Concluída'
    };

    const stepOrder = ['aguardando_separacao', 'em_transito', 'pronto_retirada', 'concluido'];

    container.innerHTML = this.reservations.map(res => {
      const currentStepIdx = stepOrder.indexOf(res.status);
      let nextStatus = null;
      let nextLabel = '';
      let nextIcon = 'fa-check';

      if (res.status === 'aguardando_separacao') {
        nextStatus = res.is_inter_store ? 'em_transito' : 'pronto_retirada';
        nextLabel = res.is_inter_store ? 'Despachar Malote' : 'Confirmar no Balcão';
        nextIcon = res.is_inter_store ? 'fa-truck-fast' : 'fa-box-open';
      } else if (res.status === 'em_transito') {
        nextStatus = 'pronto_retirada';
        nextLabel = 'Confirmar Chegada (Avisar Whats)';
        nextIcon = 'fa-bell';
      } else if (res.status === 'pronto_retirada') {
        nextStatus = 'concluido';
        nextLabel = 'Concluir Retirada';
        nextIcon = 'fa-check-double';
      }

      return `
        <div class="res-card" data-res-id="${res.id}">
          <div class="res-card-header">
            <span class="res-id-badge">${res.id}</span>
            <span class="res-status-tag ${res.status}">${statusLabelMap[res.status] || res.status}</span>
          </div>

          <div class="res-product-summary">
            <img src="${res.product_image || '/assets/bota-coturno.jpg'}" alt="${res.product_name}" class="res-thumb">
            <div>
              <div class="res-product-name">${res.product_name}</div>
              <div class="res-detail-pill">
                Tam: <strong>${res.size}</strong> • R$ ${Number(res.price).toFixed(2).replace('.', ',')}
              </div>
              <div style="font-size: 0.72rem; color: #818cf8; font-weight: 600;">
                Cliente: ${res.customer_name}
              </div>
            </div>
          </div>

          <!-- Transfer Route -->
          <div class="res-transfer-route">
            ${res.is_inter_store ? `
              <span>Origem: <strong>${res.source_store}</strong></span>
              <span class="route-arrow">➔</span>
              <span>Retirada: <strong>${res.pickup_store}</strong></span>
            ` : `
              <span><i class="fa-solid fa-store"></i> Retirada Local: <strong>${res.pickup_store}</strong></span>
            `}
          </div>

          <!-- 4-Step Logistics Stepper -->
          <div class="logistics-stepper">
            <div class="step-item ${currentStepIdx >= 0 ? 'done' : ''}">
              <span class="step-dot">1</span>
              <span class="step-lbl">Separação</span>
            </div>
            <div class="step-line ${currentStepIdx >= 1 ? 'done' : ''}"></div>
            <div class="step-item ${currentStepIdx >= 1 ? 'done' : ''}">
              <span class="step-dot">2</span>
              <span class="step-lbl">Malote</span>
            </div>
            <div class="step-line ${currentStepIdx >= 2 ? 'done' : ''}"></div>
            <div class="step-item ${currentStepIdx >= 2 ? 'done' : ''}">
              <span class="step-dot">3</span>
              <span class="step-lbl">Na Loja</span>
            </div>
            <div class="step-line ${currentStepIdx >= 3 ? 'done' : ''}"></div>
            <div class="step-item ${currentStepIdx >= 3 ? 'done' : ''}">
              <span class="step-dot">4</span>
              <span class="step-lbl">Entregue</span>
            </div>
          </div>

          <!-- Actions -->
          <div class="res-card-actions">
            <button class="btn-res-action" data-action="view-voucher" data-res-id="${res.id}">
              <i class="fa-solid fa-qrcode"></i> Voucher
            </button>
            ${nextStatus ? `
              <button class="btn-res-action complete" data-action="advance-status" data-res-id="${res.id}" data-next-status="${nextStatus}">
                <i class="fa-solid ${nextIcon}"></i> ${nextLabel}
              </button>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');

    container.querySelectorAll('[data-action="view-voucher"]').forEach(btn => {
      btn.addEventListener('click', () => {
        window.app.openVoucherModal(btn.dataset.resId);
      });
    });

    container.querySelectorAll('[data-action="advance-status"]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const resId = btn.dataset.resId;
        const nextStatus = btn.dataset.nextStatus;
        try {
          const result = await api.updateReservationStatus(resId, nextStatus);
          if (result.auto_notification) {
            window.app.showToast('Status logístico atualizado e cliente notificado no WhatsApp!');
          } else {
            window.app.showToast('Status da ordem atualizado!');
          }
          await this.loadReservations();
          if (window.app.ChatModule.currentChatId) {
            await window.app.ChatModule.selectChat(window.app.ChatModule.currentChatId);
            await window.app.ChatModule.loadChats(false);
          }
        } catch (err) {
          console.error(err);
        }
      });
    });
  },

  async handleCreateReservation() {
    const customerSelect = document.getElementById('res-modal-customer-select');
    const productSelect = document.getElementById('res-modal-product-select');
    const sizeSelect = document.getElementById('res-modal-size-select');
    const pickupSelect = document.getElementById('res-modal-pickup-store');
    const sourceSelect = document.getElementById('res-modal-source-store');
    const notesInput = document.getElementById('res-modal-notes');

    if (!customerSelect || !productSelect || !sizeSelect || !pickupSelect || !sourceSelect) return;

    try {
      const activeChatId = window.app.ChatModule.currentChatId;
      const sellerName = (window.app.currentSeller && window.app.currentSeller.name) || 'Mariana Santos';

      const res = await api.createReservation({
        customer_id: customerSelect.value,
        product_id: productSelect.value,
        size: sizeSelect.value,
        pickup_store: pickupSelect.value,
        source_store: sourceSelect.value,
        chat_id: activeChatId,
        seller_name: sellerName,
        notes: notesInput.value.trim()
      });

      window.app.closeModal('modal-reservation');
      window.app.showToast(`Ordem de Reserva ${res.reservation.id} criada e persistida no SQLite!`);

      await this.loadReservations();
      await window.app.StockModule.loadProducts();
      if (activeChatId) {
        await window.app.ChatModule.selectChat(activeChatId);
        await window.app.ChatModule.loadChats(false);
      }
    } catch (err) {
      console.error(err);
      window.app.showToast(err.message || 'Erro ao gerar reserva', 'error');
    }
  }
};
