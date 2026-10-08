/**
 * LevConnect - Centralized API Service
 */

const API_BASE = '/api';

export const api = {
  async getStores() {
    const res = await fetch(`${API_BASE}/stores`);
    return res.json();
  },

  async getChats(status = 'all', search = '') {
    const params = new URLSearchParams();
    if (status && status !== 'all') params.append('status_filter', status);
    if (search) params.append('search', search);
    const res = await fetch(`${API_BASE}/chats?${params.toString()}`);
    return res.json();
  },

  async getChat(chatId) {
    const res = await fetch(`${API_BASE}/chats/${chatId}`);
    return res.json();
  },

  async sendMessage(chatId, messageData) {
    const res = await fetch(`${API_BASE}/chats/${chatId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(messageData)
    });
    return res.json();
  },

  async updateChatStatus(chatId, newStatus) {
    const res = await fetch(`${API_BASE}/chats/${chatId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    return res.json();
  },

  async getCustomers() {
    const res = await fetch(`${API_BASE}/customers`);
    return res.json();
  },

  async getCustomer(customerId) {
    const res = await fetch(`${API_BASE}/customers/${customerId}`);
    return res.json();
  },

  async updateCustomer(customerId, data) {
    const res = await fetch(`${API_BASE}/customers/${customerId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async getProducts(category = 'all', query = '') {
    const params = new URLSearchParams();
    if (category && category !== 'all') params.append('category', category);
    if (query) params.append('query', query);
    const res = await fetch(`${API_BASE}/products?${params.toString()}`);
    return res.json();
  },

  async getProduct(productId) {
    const res = await fetch(`${API_BASE}/products/${productId}`);
    return res.json();
  },

  async getReservations(store = 'all', statusFilter = 'all') {
    const params = new URLSearchParams();
    if (store && store !== 'all') params.append('store', store);
    if (statusFilter && statusFilter !== 'all') params.append('status_filter', statusFilter);
    const res = await fetch(`${API_BASE}/reservations?${params.toString()}`);
    return res.json();
  },

  async createReservation(reservationData) {
    const res = await fetch(`${API_BASE}/reservations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reservationData)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Erro ao criar reserva');
    }
    return res.json();
  },

  async updateReservationStatus(resId, status) {
    const res = await fetch(`${API_BASE}/reservations/${resId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    return res.json();
  },

  async simulateIncoming(scenarioData) {
    const res = await fetch(`${API_BASE}/simulate-incoming`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scenarioData)
    });
    return res.json();
  },

  async getDashboardStats() {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    return res.json();
  }
};
