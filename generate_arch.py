import os
import subprocess

html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 24px;
    background: #0f172a;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    color: #f8fafc;
    width: 900px;
  }
  .title {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 24px;
    letter-spacing: -0.5px;
  }
  .title span { color: #f97316; }
  .grid {
    display: grid;
    grid-template-columns: 240px 1fr 240px;
    gap: 20px;
    align-items: stretch;
  }
  .col {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
  }
  .card.highlight {
    border-color: #3b82f6;
    background: linear-gradient(145deg, #1e293b, #172554);
  }
  .card.accent {
    border-color: #f97316;
    background: linear-gradient(145deg, #1e293b, #431407);
  }
  .card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 10px;
    color: #93c5fd;
  }
  .card.accent .card-header { color: #fdba74; }
  .badge {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    background: #3b82f6;
    color: white;
    margin-left: auto;
  }
  .card.accent .badge { background: #f97316; }
  .item-list {
    margin: 0;
    padding-left: 18px;
    font-size: 11.5px;
    color: #cbd5e1;
    line-height: 1.6;
  }
  .connector {
    text-align: center;
    font-size: 11px;
    color: #94a3b8;
    margin: -6px 0;
  }
  .center-box {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .sub-box {
    background: rgba(15, 23, 42, 0.6);
    border: 1px dashed #475569;
    border-radius: 8px;
    padding: 12px;
  }
  .sub-title {
    font-size: 12px;
    font-weight: 600;
    color: #38bdf8;
    margin-bottom: 6px;
  }
</style>
</head>
<body>
  <div class="title">Arquitetura da Solução <span>LevConnect</span> • Visão Técnica de Integração</div>
  <div class="grid">
    <!-- Coluna 1: Canais & Clientes -->
    <div class="col">
      <div class="card highlight">
        <div class="card-header">
          <span>Canais Digitais Externos</span>
          <span class="badge">Cliente</span>
        </div>
        <ul class="item-list">
          <li>Instagram / Facebook Ads</li>
          <li>WhatsApp Business Cloud API</li>
          <li>Mensagens & Áudios de Clientes</li>
          <li>Webhooks de Entrada (JSON)</li>
        </ul>
      </div>

      <div class="connector">⬇ Webhook / HTTPS REST</div>

      <div class="card">
        <div class="card-header">
          <span>Operador de Loja</span>
          <span class="badge">Vendedor</span>
        </div>
        <ul class="item-list">
          <li>Interface Web Responsiva (SPA)</li>
          <li>Consulta em Tela Única</li>
          <li>Respostas Rápidas</li>
          <li>Geração de Reserva 1-clique</li>
        </ul>
      </div>
    </div>

    <!-- Coluna 2: Núcleo LevConnect -->
    <div class="col center-box">
      <div class="card highlight" style="flex: 1;">
        <div class="card-header">
          <span>LevConnect Core Platform</span>
          <span class="badge">Back-end & Front-end</span>
        </div>
        
        <div class="sub-box">
          <div class="sub-title">Camada de Apresentação (Frontend SPA)</div>
          <ul class="item-list">
            <li>Inbox Triagem (Aberto, Em Atendimento, Reservado)</li>
            <li>Feed de Chat WhatsApp em tempo real</li>
            <li>Ficha Inteligente CRM (Medidas, Marcas, LTV)</li>
            <li>Matriz de Estoque Inter-filiais 5 Lojas</li>
          </ul>
        </div>

        <div style="height: 8px;"></div>

        <div class="sub-box">
          <div class="sub-title">Camada de Aplicação & APIs (FastAPI)</div>
          <ul class="item-list">
            <li>Rotas RESTful: /api/chats, /api/products, /api/reservations</li>
            <li>Simulador de Webhooks & Gerador de Vouchers</li>
            <li>Regras de Negócio: Reserva 48h, Débito de Estoque</li>
            <li>In-Memory State Relacional / Módulos de Domínio</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Coluna 3: Lojas Físicas & Logística -->
    <div class="col">
      <div class="card accent">
        <div class="card-header">
          <span>5 Filiais Lojas Lev</span>
          <span class="badge">Estoques</span>
        </div>
        <ul class="item-list">
          <li><strong>Charqueadas</strong> (Filial Piloto)</li>
          <li><strong>Minas do Leão</strong></li>
          <li><strong>Encruzilhada do Sul</strong></li>
          <li><strong>Pantâno Grande</strong></li>
          <li><strong>Rio Pardo</strong></li>
        </ul>
      </div>

      <div class="connector">⬇ Malote Inter-lojas</div>

      <div class="card accent">
        <div class="card-header">
          <span>Módulo Clique e Retire</span>
          <span class="badge">O2O</span>
        </div>
        <ul class="item-list">
          <li>Voucher Digital com QR Code</li>
          <li>Prazo de Retirada de 48 horas</li>
          <li>Separação Balcão / Etiqueta</li>
          <li>Finalização e Prova Presencial</li>
        </ul>
      </div>
    </div>
  </div>
</body>
</html>
"""

os.makedirs('d:/Faculdade/LevConnect/figures', exist_ok=True)
arch_html_path = 'd:/Faculdade/LevConnect/figures/arch_temp.html'
arch_png_path = 'd:/Faculdade/LevConnect/figures/architecture_diagram.png'

with open(arch_html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
cmd = [
    edge,
    '--headless',
    '--disable-gpu',
    '--window-size=950,530',
    f'--screenshot={arch_png_path}',
    arch_html_path
]
subprocess.run(cmd, check=True)
print(f'Architecture diagram created successfully! Size: {os.path.getsize(arch_png_path)} bytes')
