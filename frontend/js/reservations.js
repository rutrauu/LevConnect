/**
 * LevConnect - Reservations Module (Clique e Retire / O2O Cross-Store)
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

    // Reservation creation form submission
    const btnSubmit = document.getElementById('btn-submit-create-reservation');
    if (btnSubmit) {
      btnSubmit.addEventListener('click', () => this.handleCreateReservation());
    }

    // Listen to changes in source/pickup store select in modal to show warning
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

    container.innerHTML = this.reservations.map(res => {
      const isComplete = res.status === 'concluido';
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

          <!-- Actions -->
          <div class="res-card-actions">
            <button class="btn-res-action" data-action="view-voucher" data-res-id="${res.id}">
              <i class="fa-solid fa-qrcode"></i> Voucher
            </button>
            ${!isComplete ? `
              <button class="btn-res-action complete" data-action="mark-complete" data-res-id="${res.id}">
                <i class="fa-solid fa-check"></i> Concluir Retirada
              </button>
            ` : ''}
          </div>
        </div>
      `;
    }).join('');

    // Attach actions
    container.querySelectorAll('[data-action="view-voucher"]').forEach(btn => {
      btn.addEventListener('click', () => {
        window.app.openVoucherModal(btn.dataset.resId);
      });
    });

    container.querySelectorAll('[data-action="mark-complete"]').forEach(btn => {
      btn.addEventListener('click', async () => {
        try {
          await api.updateReservationStatus(btn.dataset.resId, 'concluido');
          window.app.showToast('Reserva concluída! Peça retirada pelo cliente.');
          this.loadReservations();
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

      const res = await api.createReservation({
        customer_id: customerSelect.value,
        product_id: productSelect.value,
        size: sizeSelect.value,
        pickup_store: pickupSelect.value,
        source_store: sourceSelect.value,
        chat_id: activeChatId,
        seller_name: 'Mariana Santos',
        notes: notesInput.value.trim()
      });

      window.app.closeModal('modal-reservation');
      window.app.showToast(`Ordem de Reserva ${res.reservation.id} criada com sucesso!`);

      // Refresh modules
      await this.loadReservations();
      await window.app.StockModule.loadProducts();
      if (activeChatId) {
        await window.app.ChatModule.selectChat(activeChatId);
      }
    } catch (err) {
      console.error(err);
      window.app.showToast(err.message || 'Erro ao gerar reserva', 'error');
    }
  }
};
