/**
 * LevConnect - Dashboard & Analytics Module
 * KPIs: Response Time, Conversion Rate, Cross-Store Transfers, Demand by Size
 */

import { api } from './api.js';

export const DashboardModule = {
  async init() {
    await this.loadStats();
  },

  async loadStats() {
    try {
      const data = await api.getDashboardStats();
      if (!data) return;

      this.renderKPIs(data.kpis);
      this.renderStoresTable(data.stores_ranking);
      this.renderDemandHistogram(data.shoe_size_demand);
    } catch (err) {
      console.error('Erro ao carregar estatísticas do dashboard:', err);
    }
  },

  renderKPIs(kpis) {
    if (!kpis) return;

    const avgEl = document.getElementById('kpi-avg-response');
    const convEl = document.getElementById('kpi-conversion');
    const interEl = document.getElementById('kpi-interstore');
    const pipeEl = document.getElementById('kpi-pipeline');

    if (avgEl) avgEl.textContent = kpis.avg_response_time || '2.4 min';
    if (convEl) convEl.textContent = kpis.conversion_rate || '68.2%';
    if (interEl) interEl.textContent = `${kpis.inter_store_reservations} inter-lojas`;
    if (pipeEl) pipeEl.textContent = kpis.total_sales_pipeline || 'R$ 0,00';
  },

  renderStoresTable(stores) {
    const tbody = document.getElementById('table-stores-ranking-body');
    if (!tbody || !stores) return;

    tbody.innerHTML = stores.map(s => `
      <tr>
        <td>
          <div style="font-weight: 700; color: #fff;">${s.store}</div>
          <div style="font-size: 0.65rem; color: var(--text-dim);">Unidade Regional RS</div>
        </td>
        <td>
          <span style="font-weight: 700; color: #818cf8;">${s.reservations_count} reservas</span>
        </td>
        <td>${s.sellers_count} atendentes</td>
        <td>
          <strong style="color: #34d399;">R$ ${s.total_value.toFixed(2).replace('.', ',')}</strong>
        </td>
        <td>
          <span style="display: inline-flex; align-items: center; gap: 4px; font-size: 0.7rem; color: #4ade80;">
            <i class="fa-solid fa-circle-dot" style="font-size: 7px;"></i> Online (ERP Sinc.)
          </span>
        </td>
      </tr>
    `).join('');
  },

  renderDemandHistogram(demands) {
    const container = document.getElementById('demand-bars-container');
    if (!container || !demands) return;

    const sizes = ['35', '36', '37', '38', '39', '40', '41'];
    const maxVal = Math.max(...Object.values(demands), 3);

    container.innerHTML = sizes.map(size => {
      const count = demands[size] || 0;
      const heightPercent = Math.max((count / maxVal) * 100, 15);

      return `
        <div style="flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; height: 100%; justify-content: flex-end;" title="Tamanho ${size}: ${count} clientes cadastrados">
          <span style="font-size: 0.65rem; color: #a5b4fc; font-weight: 700;">${count}</span>
          <div style="width: 100%; max-width: 28px; height: ${heightPercent}%; background: linear-gradient(180deg, #6366f1 0%, #4338ca 100%); border-radius: 4px;"></div>
          <span style="font-size: 0.7rem; color: var(--text-muted); font-weight: 600;">Tam ${size}</span>
        </div>
      `;
    }).join('');
  }
};
