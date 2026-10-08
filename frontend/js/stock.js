/**
 * LevConnect - Stock Module
 * Real-time 5-Branch Cross-Store Inventory Lookup (O2O Omnichannel)
 */

import { api } from './api.js';

export const StockModule = {
  products: [],
  selectedCategory: 'all',
  searchQuery: '',
  activeStore: 'Charqueadas',
  productSelectedSizes: {}, // { [productId]: size }

  async init() {
    this.bindEvents();
    await this.loadProducts();
  },

  bindEvents() {
    const searchInput = document.getElementById('input-stock-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value;
        this.loadProducts();
      });
    }

    const catContainer = document.getElementById('stock-category-filters');
    if (catContainer) {
      catContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('stock-cat-btn')) {
          catContainer.querySelectorAll('.stock-cat-btn').forEach(b => b.classList.remove('active'));
          e.target.classList.add('active');
          this.selectedCategory = e.target.dataset.cat;
          this.loadProducts();
        }
      });
    }

    const headerStoreSelect = document.getElementById('header-store-select');
    if (headerStoreSelect) {
      headerStoreSelect.addEventListener('change', (e) => {
        this.activeStore = e.target.value;
        this.renderProductsList();
      });
    }
  },

  setActiveStore(storeName) {
    this.activeStore = storeName;
    this.renderProductsList();
  },

  async loadProducts() {
    try {
      const data = await api.getProducts(this.selectedCategory, this.searchQuery);
      this.products = data.products || [];
      
      // Default initial size for each product if not set
      this.products.forEach(p => {
        if (!this.productSelectedSizes[p.id] && p.sizes && p.sizes.length > 0) {
          this.productSelectedSizes[p.id] = p.sizes[0];
        }
      });

      this.renderProductsList();
    } catch (err) {
      console.error('Erro ao carregar estoque:', err);
    }
  },

  syncWithCustomerSize(customer) {
    if (!customer) return;
    this.products.forEach(p => {
      if (p.type === 'shoes' && customer.shoe_size && p.sizes.includes(customer.shoe_size)) {
        this.productSelectedSizes[p.id] = customer.shoe_size;
      } else if (p.type === 'clothing' && customer.clothing_size_top && p.sizes.includes(customer.clothing_size_top)) {
        this.productSelectedSizes[p.id] = customer.clothing_size_top;
      }
    });
    this.renderProductsList();
  },

  renderProductsList() {
    const container = document.getElementById('products-stock-container');
    if (!container) return;

    if (this.products.length === 0) {
      container.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: var(--text-dim); font-size: 0.85rem;">
          Nenhum produto encontrado no catálogo do ERP.
        </div>
      `;
      return;
    }

    const stores = [
      "Charqueadas",
      "Minas do Leão",
      "Encruzilhada do Sul",
      "Pantâno Grande",
      "Rio Pardo"
    ];

    container.innerHTML = this.products.map(product => {
      const selectedSize = this.productSelectedSizes[product.id] || product.sizes[0];
      const localStock = (product.stock[this.activeStore] && product.stock[this.activeStore][selectedSize]) || 0;
      
      // Find other stores that have stock
      const otherStoresWithStock = stores
        .filter(s => s !== this.activeStore)
        .filter(s => (product.stock[s] && product.stock[s][selectedSize]) > 0);

      return `
        <div class="product-stock-card" data-product-id="${product.id}">
          <div class="product-card-top">
            <img src="${product.image}" alt="${product.name}" class="product-thumb">
            <div class="product-info-col">
              <span class="product-sku-tag">SKU: ${product.sku} • ${product.brand}</span>
              <h4 class="product-card-title">${product.name}</h4>
              <span class="product-card-price">R$ ${product.price.toFixed(2).replace('.', ',')}</span>
            </div>
          </div>

          <!-- Size Selector -->
          <div style="display: flex; flex-direction: column; gap: 4px;">
            <span style="font-size: 0.7rem; color: var(--text-dim); font-weight: 700; text-transform: uppercase;">
              Selecione o Tamanho:
            </span>
            <div class="sizes-selector-row">
              ${product.sizes.map(size => {
                const isActive = size === selectedSize ? 'active' : '';
                return `
                  <button class="size-pill-btn ${isActive}" data-product-id="${product.id}" data-size="${size}">
                    ${size}
                  </button>
                `;
              }).join('')}
            </div>
          </div>

          <!-- 5-Store Real-time Stock Matrix -->
          <div class="store-matrix-container">
            <div class="matrix-header">
              <span>Disponibilidade nas 5 Filiais</span>
              <span style="color: #818cf8;">Tam: ${selectedSize}</span>
            </div>

            ${stores.map(storeName => {
              const qty = (product.stock[storeName] && product.stock[storeName][selectedSize]) || 0;
              const isCurrent = storeName === this.activeStore;
              const inStock = qty > 0;

              return `
                <div class="store-stock-row ${isCurrent ? 'is-current-store' : ''}">
                  <span class="store-name-text">
                    ${storeName}
                    ${isCurrent ? '<span class="current-store-indicator">Sua Loja</span>' : ''}
                  </span>
                  <span class="stock-qty-badge ${inStock ? 'in-stock' : 'out-of-stock'}">
                    ${inStock ? `${qty} em estoque` : 'Esgotado'}
                  </span>
                </div>
              `;
            }).join('')}
          </div>

          <!-- Status Highlight & Direct Action -->
          ${localStock > 0 ? `
            <div style="font-size: 0.72rem; color: #34d399; font-weight: 600;">
              <i class="fa-solid fa-circle-check"></i> Pronta entrega na loja de ${this.activeStore} (${localStock} un.)
            </div>
          ` : (otherStoresWithStock.length > 0 ? `
            <div style="font-size: 0.72rem; color: #fbbf24; font-weight: 600;">
              <i class="fa-solid fa-truck-fast"></i> Esgotado aqui! Disponível em: ${otherStoresWithStock.join(', ')}
            </div>
          ` : `
            <div style="font-size: 0.72rem; color: #f87171; font-weight: 600;">
              <i class="fa-solid fa-circle-xmark"></i> Esgotado em todas as 5 filiais da rede.
            </div>
          `)}

          <!-- Card Actions -->
          <div class="product-card-actions">
            <button class="btn-reserve-instant" data-action="reserve" data-product-id="${product.id}" data-size="${selectedSize}">
              <i class="fa-solid fa-cart-shopping"></i> Reservar Peça (Clique & Retire)
            </button>
            <button class="btn-send-to-chat" data-action="send-chat" data-product-id="${product.id}" title="Enviar foto e preço no WhatsApp">
              <i class="fa-solid fa-paper-plane"></i>
            </button>
          </div>
        </div>
      `;
    }).join('');

    // Attach listeners
    container.querySelectorAll('.size-pill-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const pId = btn.dataset.productId;
        const size = btn.dataset.size;
        this.productSelectedSizes[pId] = size;
        this.renderProductsList();
      });
    });

    container.querySelectorAll('[data-action="reserve"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const pId = btn.dataset.productId;
        const size = btn.dataset.size;
        const product = this.products.find(p => p.id === pId);
        window.app.openReservationModalWithProduct(product, size);
      });
    });

    container.querySelectorAll('[data-action="send-chat"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const pId = btn.dataset.productId;
        const product = this.products.find(p => p.id === pId);
        if (product) {
          window.app.ChatModule.sendProductCardToChat(product);
        }
      });
    });
  }
};
