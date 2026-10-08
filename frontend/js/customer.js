/**
 * LevConnect - Customer Module (CRM de Moda & Ficha Inteligente)
 */

import { api } from './api.js';

export const CustomerModule = {
  currentCustomer: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    const btnSave = document.getElementById('btn-save-crm-customer');
    if (btnSave) {
      btnSave.addEventListener('click', () => this.handleSaveCustomer());
    }
  },

  setCustomer(customer) {
    this.currentCustomer = customer;
    this.renderCustomerProfile();
  },

  renderCustomerProfile() {
    if (!this.currentCustomer) return;

    const c = this.currentCustomer;

    const avatar = document.getElementById('crm-customer-avatar');
    const name = document.getElementById('crm-customer-name');
    const vip = document.getElementById('crm-vip-badge');
    const phone = document.getElementById('crm-customer-phone');
    const store = document.getElementById('crm-customer-store');
    const purchases = document.getElementById('crm-total-purchases');
    const ltv = document.getElementById('crm-ltv-value');
    
    const inputShoe = document.getElementById('crm-input-shoe-size');
    const inputTop = document.getElementById('crm-input-top-size');
    const inputBottom = document.getElementById('crm-input-bottom-size');
    
    const brandsList = document.getElementById('crm-brands-list');
    const notesTextarea = document.getElementById('crm-customer-notes');
    const historyList = document.getElementById('crm-history-list');

    if (avatar) avatar.src = c.avatar || 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100';
    if (name) name.textContent = c.name;
    if (vip) vip.style.display = c.vip_status ? 'inline-block' : 'none';
    if (phone) phone.textContent = c.phone;
    if (store) store.textContent = c.preferred_store || 'Charqueadas';
    if (purchases) purchases.textContent = `${c.total_purchases || 0} compras`;
    if (ltv) ltv.textContent = `R$ ${(c.lifetime_value || 0).toFixed(2).replace('.', ',')}`;

    if (inputShoe) inputShoe.value = c.shoe_size || '';
    if (inputTop) inputTop.value = c.clothing_size_top || '';
    if (inputBottom) inputBottom.value = c.clothing_size_bottom || '';

    if (brandsList) {
      const brands = c.favorite_brands || ['Lev Collection', 'Vizzano'];
      brandsList.innerHTML = brands.map(b => `<span class="brand-chip">${b}</span>`).join('');
    }

    if (notesTextarea) {
      notesTextarea.value = c.notes || '';
    }

    if (historyList) {
      const history = c.history || [];
      if (history.length === 0) {
        historyList.innerHTML = `
          <div style="font-size: 0.72rem; color: var(--text-dim); padding: 4px;">
            Nenhuma compra registrada anteriormente.
          </div>
        `;
      } else {
        historyList.innerHTML = history.map(item => `
          <div class="history-item-row">
            <div class="history-item-left">
              <span class="history-item-name">${item.item}</span>
              <span class="history-item-date">${item.date} • Filial ${item.store}</span>
            </div>
            <span class="history-item-price">R$ ${item.price.toFixed(2).replace('.', ',')}</span>
          </div>
        `).join('');
      }
    }
  },

  async handleSaveCustomer() {
    if (!this.currentCustomer) return;

    const shoeSize = document.getElementById('crm-input-shoe-size').value.trim();
    const topSize = document.getElementById('crm-input-top-size').value.trim();
    const bottomSize = document.getElementById('crm-input-bottom-size').value.trim();
    const notes = document.getElementById('crm-customer-notes').value.trim();

    try {
      const res = await api.updateCustomer(this.currentCustomer.id, {
        shoe_size: shoeSize,
        clothing_size_top: topSize,
        clothing_size_bottom: bottomSize,
        notes: notes
      });

      this.currentCustomer = res.customer;
      window.app.showToast('Ficha do cliente atualizada com sucesso!');
      
      // Sync stock matrix highlight with new customer size
      window.app.StockModule.syncWithCustomerSize(this.currentCustomer);
    } catch (err) {
      console.error(err);
      window.app.showToast('Erro ao atualizar cliente', 'error');
    }
  }
};
