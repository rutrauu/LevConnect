/**
 * LevConnect - Application Controller
 * Case Study: Lojas Lev (Rio Grande do Sul)
 */

import { api } from './api.js';
import { ChatModule } from './chat.js';
import { StockModule } from './stock.js';
import { CustomerModule } from './customer.js';
import { ReservationsModule } from './reservations.js';
import { DashboardModule } from './dashboard.js';

class LevConnectApp {
  constructor() {
    this.ChatModule = ChatModule;
    this.StockModule = StockModule;
    this.CustomerModule = CustomerModule;
    this.ReservationsModule = ReservationsModule;
    this.DashboardModule = DashboardModule;
    this.sellers = [];
    this.currentSeller = {
      id: 'SEL-01',
      name: 'Mariana Santos',
      store: 'Charqueadas',
      role: 'Vendedora Digital',
      avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80'
    };
  }

  async init() {
    console.log('Inicializando LevConnect Omnichannel Cockpit v2.0 (SQLite + Copilot)...');

    // Load Sellers for Multi-Branch Profile Switching
    try {
      const sellersData = await api.getSellers();
      this.sellers = sellersData.sellers || [];
      if (this.sellers.length > 0) {
        this.currentSeller = this.sellers[0];
      }
    } catch (e) {
      console.error('Erro ao carregar vendedores:', e);
    }

    // Initialize modules
    await this.ChatModule.init((customer, chat) => {
      this.CustomerModule.setCustomer(customer);
      this.StockModule.syncWithCustomerSize(customer);
    });

    await this.StockModule.init();
    this.CustomerModule.init();
    await this.ReservationsModule.init();

    this.bindGlobalEvents();
    this.setupAutoPolling();
  }

  bindGlobalEvents() {
    // Column 3 Tabs Navigation
    document.querySelectorAll('.action-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetTabId = btn.dataset.tab;
        
        // Update nav buttons
        document.querySelectorAll('.action-tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
          panel.classList.toggle('active', panel.id === targetTabId);
        });
      });
    });

    // Header Store Change
    const headerStoreSelect = document.getElementById('header-store-select');
    if (headerStoreSelect) {
      headerStoreSelect.addEventListener('change', (e) => {
        const store = e.target.value;
        this.StockModule.setActiveStore(store);
        this.showToast(`Filial ativa alterada para: ${store}`);
      });
    }

    // Seller Profile Switcher Modal Trigger
    const sellerSwitcher = document.getElementById('seller-profile-switcher');
    if (sellerSwitcher) {
      sellerSwitcher.addEventListener('click', () => {
        this.renderSellersSwitchModal();
        this.openModal('modal-seller-switch');
      });
    }

    // SQLite Demo Reset button inside Dashboard
    const btnResetDb = document.getElementById('btn-reset-demo-db');
    if (btnResetDb) {
      btnResetDb.addEventListener('click', async () => {
        try {
          await api.resetDatabase();
          await this.ChatModule.loadChats(true);
          await this.StockModule.loadProducts();
          await this.ReservationsModule.loadReservations();
          await this.DashboardModule.loadStats();
          this.showToast('Banco SQLite restaurado para o estado original de demonstração!');
        } catch (err) {
          console.error(err);
          this.showToast('Erro ao restaurar banco SQLite', 'error');
        }
      });
    }

    // Auto-activate tab or modal via URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    if (tabParam) {
      const tabBtn = document.querySelector(`.action-tab-btn[data-tab="tab-${tabParam}"]`);
      if (tabBtn) tabBtn.click();
    }
    if (urlParams.get('modal') === 'dashboard') {
      setTimeout(() => {
        document.getElementById('btn-open-dashboard')?.click();
      }, 500);
    }

    // Modal Triggers from Header
    const btnSim = document.getElementById('btn-open-simulator');
    if (btnSim) btnSim.addEventListener('click', () => this.openModal('modal-simulator'));

    const btnQuickSim = document.getElementById('btn-quick-simulate');
    if (btnQuickSim) btnQuickSim.addEventListener('click', () => this.openModal('modal-simulator'));

    const btnDash = document.getElementById('btn-open-dashboard');
    if (btnDash) {
      btnDash.addEventListener('click', () => {
        this.DashboardModule.loadStats();
        this.openModal('modal-dashboard');
      });
    }

    const btnNewRes = document.getElementById('btn-header-new-res');
    if (btnNewRes) {
      btnNewRes.addEventListener('click', () => {
        this.openReservationModalWithProduct();
      });
    }

    // Modal Close buttons
    document.querySelectorAll('[data-close]').forEach(btn => {
      btn.addEventListener('click', () => {
        const modalId = btn.dataset.close;
        this.closeModal(modalId);
      });
    });

    // Close on overlay backdrop click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          overlay.classList.remove('active');
        }
      });
    });

    // Simulator Scenario Cards
    document.querySelectorAll('.scenario-card').forEach(card => {
      card.addEventListener('click', async () => {
        const scenario = card.dataset.scenario;
        await this.runSimulation(scenario);
      });
    });

    // Custom Simulator Message
    const btnSendCustomSim = document.getElementById('btn-send-custom-sim');
    const inputCustomSim = document.getElementById('input-custom-sim-text');
    if (btnSendCustomSim && inputCustomSim) {
      btnSendCustomSim.addEventListener('click', async () => {
        const msg = inputCustomSim.value.trim();
        if (!msg) return;
        inputCustomSim.value = '';
        await this.runSimulation('custom', msg);
      });
    }

    // Attach Catalog Product to Chat button in Composer
    const btnAttach = document.getElementById('btn-attach-catalog-product');
    if (btnAttach) {
      btnAttach.addEventListener('click', () => {
        const stockTabBtn = document.querySelector('[data-tab="tab-stock"]');
        if (stockTabBtn) stockTabBtn.click();
        this.showToast('Selecione um produto no estoque e clique no ícone de aviãozinho para enviar ao cliente.');
      });
    }
  }

  renderSellersSwitchModal() {
    const container = document.getElementById('sellers-switch-list');
    if (!container) return;

    container.innerHTML = this.sellers.map(s => {
      const isCurrent = this.currentSeller && this.currentSeller.id === s.id;
      return `
        <div class="seller-switch-item ${isCurrent ? 'active' : ''}" data-seller-id="${s.id}">
          <img src="${s.avatar || 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=100'}" alt="${s.name}" class="seller-avatar">
          <div style="flex: 1;">
            <div style="font-weight: 700; font-size: 0.85rem; color: #fff;">${s.name}</div>
            <div style="font-size: 0.72rem; color: var(--text-muted);">${s.role} • Filial <strong>${s.store}</strong></div>
          </div>
          ${isCurrent ? `<span class="status-badge reserved">Logado</span>` : `<button class="btn-res-action">Selecionar</button>`}
        </div>
      `;
    }).join('');

    container.querySelectorAll('.seller-switch-item').forEach(item => {
      item.addEventListener('click', () => {
        const sellerId = item.dataset.sellerId;
        const chosen = this.sellers.find(s => s.id === sellerId);
        if (chosen) {
          this.switchSeller(chosen);
        }
      });
    });
  }

  switchSeller(seller) {
    this.currentSeller = seller;

    const avatarEl = document.getElementById('header-seller-avatar');
    const nameEl = document.getElementById('header-seller-name');
    const roleEl = document.getElementById('header-seller-role');
    const headerStoreSelect = document.getElementById('header-store-select');

    if (avatarEl && seller.avatar) avatarEl.src = seller.avatar;
    if (nameEl) nameEl.innerHTML = `${seller.name} <i class="fa-solid fa-caret-down" style="font-size: 0.7rem; opacity: 0.7;"></i>`;
    if (roleEl) roleEl.textContent = `${seller.store} • Online`;

    if (headerStoreSelect) {
      headerStoreSelect.value = seller.store;
    }

    this.StockModule.setActiveStore(seller.store);
    this.closeModal('modal-seller-switch');
    this.showToast(`Operador alterado para ${seller.name} (Filial ${seller.store})`);
  }

  openModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.add('active');
  }

  closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) el.classList.remove('active');
  }

  showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `
      <i class="fa-solid ${type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-check'}" style="color: ${type === 'error' ? '#ef4444' : '#10b981'};"></i>
      <span>${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  async openReservationModalWithProduct(product = null, preSelectedSize = null) {
    const custSelect = document.getElementById('res-modal-customer-select');
    const prodSelect = document.getElementById('res-modal-product-select');
    const pickupSelect = document.getElementById('res-modal-pickup-store');

    const customersData = await api.getCustomers();
    const customers = customersData.customers || [];

    const activeCustId = this.CustomerModule.currentCustomer ? this.CustomerModule.currentCustomer.id : null;

    if (custSelect) {
      custSelect.innerHTML = customers.map(c => `
        <option value="${c.id}" ${c.id === activeCustId ? 'selected' : ''}>
          ${c.name} (${c.phone}) - Prefere ${c.preferred_store}
        </option>
      `).join('');
    }

    const products = this.StockModule.products || [];
    const selectedProd = product || (products.length > 0 ? products[0] : null);

    if (prodSelect) {
      prodSelect.innerHTML = products.map(p => `
        <option value="${p.id}" ${selectedProd && p.id === selectedProd.id ? 'selected' : ''}>
          ${p.name} - R$ ${p.price.toFixed(2).replace('.', ',')}
        </option>
      `).join('');

      prodSelect.onchange = () => {
        const p = products.find(prod => prod.id === prodSelect.value);
        this.updateModalSizesAndSources(p, null);
      };
    }

    if (pickupSelect) {
      const preferred = this.CustomerModule.currentCustomer ? this.CustomerModule.currentCustomer.preferred_store : this.StockModule.activeStore;
      pickupSelect.value = preferred || 'Charqueadas';
    }

    this.updateModalSizesAndSources(selectedProd, preSelectedSize);

    this.openModal('modal-reservation');
  }

  updateModalSizesAndSources(product, preferredSize) {
    if (!product) return;
    const sizeSelect = document.getElementById('res-modal-size-select');

    const chosenSize = preferredSize || product.sizes[0];

    if (sizeSelect) {
      sizeSelect.innerHTML = product.sizes.map(s => `
        <option value="${s}" ${s === chosenSize ? 'selected' : ''}>${s}</option>
      `).join('');

      sizeSelect.onchange = () => {
        this.populateSourceStores(product, sizeSelect.value);
      };
    }

    this.populateSourceStores(product, chosenSize);
  }

  populateSourceStores(product, size) {
    const sourceSelect = document.getElementById('res-modal-source-store');
    const pickupSelect = document.getElementById('res-modal-pickup-store');
    const alertBox = document.getElementById('res-transfer-alert-box');
    if (!sourceSelect) return;

    const stores = ["Charqueadas", "Minas do Leão", "Encruzilhada do Sul", "Pantâno Grande", "Rio Pardo"];
    
    const options = stores.map(st => {
      const qty = (product.stock[st] && product.stock[st][size]) || 0;
      return { store: st, qty };
    });

    sourceSelect.innerHTML = options.map(o => `
      <option value="${o.store}" ${o.qty === 0 ? 'disabled' : ''}>
        ${o.store} - Saldo: ${o.qty} ${o.qty === 0 ? '(Esgotado)' : 'disponível(is)'}
      </option>
    `).join('');

    // Prefer local pickup store if it has stock > 0, otherwise first store with stock > 0
    const pickupStoreVal = pickupSelect ? pickupSelect.value : this.StockModule.activeStore;
    const localWithStock = options.find(o => o.store === pickupStoreVal && o.qty > 0);
    const firstWithStock = localWithStock || options.find(o => o.qty > 0);
    if (firstWithStock) {
      sourceSelect.value = firstWithStock.store;
    }

    if (pickupSelect && alertBox) {
      alertBox.style.display = (pickupSelect.value !== sourceSelect.value) ? 'block' : 'none';
    }
  }

  async openVoucherModal(resId) {
    const reservations = this.ReservationsModule.reservations || [];
    let res = reservations.find(r => r.id === resId);

    if (!res) {
      const data = await api.getReservations();
      res = (data.reservations || []).find(r => r.id === resId);
    }

    if (!res) return;

    const codeEl = document.getElementById('voucher-code-display');
    const custEl = document.getElementById('voucher-customer-display');
    const itemEl = document.getElementById('voucher-item-display');
    const sizeEl = document.getElementById('voucher-size-display');
    const priceEl = document.getElementById('voucher-price-display');
    const pickupEl = document.getElementById('voucher-pickup-display');
    const expiresEl = document.getElementById('voucher-expires-display');

    if (codeEl) codeEl.textContent = res.id;
    if (custEl) custEl.textContent = `${res.customer_name} • ${res.customer_phone}`;
    if (itemEl) itemEl.textContent = res.product_name;
    if (sizeEl) sizeEl.textContent = res.size;
    if (priceEl) priceEl.textContent = `R$ ${Number(res.price).toFixed(2).replace('.', ',')}`;
    if (pickupEl) pickupEl.textContent = `Lojas Lev - Filial ${res.pickup_store}`;
    
    const expDate = new Date(res.expires_at || Date.now() + 48 * 3600 * 1000);
    if (expiresEl) expiresEl.textContent = expDate.toLocaleString('pt-BR');

    this.openModal('modal-voucher');
  }

  async runSimulation(scenario, customMsg = null) {
    try {
      this.closeModal('modal-simulator');
      this.showToast('Simulando nova mensagem do WhatsApp...');

      const result = await api.simulateIncoming({
        scenario: scenario,
        custom_message: customMsg
      });

      await this.ChatModule.loadChats();
      if (result.chat_id) {
        await this.ChatModule.selectChat(result.chat_id);
      }

      this.showToast(`Nova mensagem recebida no WhatsApp!`);
    } catch (err) {
      console.error(err);
      this.showToast('Erro ao executar simulação', 'error');
    }
  }

  setupAutoPolling() {
    setInterval(async () => {
      try {
        await this.ChatModule.loadChats(false);
      } catch (e) {
        // silent
      }
    }, 12000);
  }
}

window.app = new LevConnectApp();
document.addEventListener('DOMContentLoaded', () => {
  window.app.init();
});
