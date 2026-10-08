# LevConnect • Plataforma de CRM e Vendas Omnichannel para Varejo Regional

**Projeto de Desenvolvimento II**  
**Aluno:** Artur Raguse  
**Professor:** Luciano Zanuz  
**Estudo de Caso:** Lojas Lev (Rio Grande do Sul)  

---

## 1. Visão Geral do Projeto

O **LevConnect** é uma solução de CRM e gestão omnichannel desenvolvida sob medida para as **Lojas Lev**, uma rede regional de moda e calçados com 5 filiais no Rio Grande do Sul:
- **Charqueadas** (Filial piloto)
- **Minas do Leão**
- **Encruzilhada do Sul**
- **Pantâno Grande**
- **Rio Pardo**

### O Problema Identificado no Discovery
As Lojas Lev atraem forte engajamento através das redes sociais (Instagram e Facebook), porém o processo de conversão no WhatsApp enfrentava um severo gargalo operacional:
1. **Desconexão de Estoque:** Vendedores perdiam tempo verificando manualmente o estoque físico ou acionando colegas de outras filiais via rádio/mensagens, gerando lentidão e perda de vendas quando uma numeração esgotava localmente.
2. **Atendimento Desestruturado:** Falta de triagem centralizada e múltiplos atendentes operando em celulares avulsos.
3. **Ausência de Histórico de Moda:** Perda do registro de numerações (tamanho de calçado e roupas), preferências e marcas prediletas do cliente.
4. **Comportamento Regional O2O (Online to Offline):** Os clientes da região preferem reservar a peça online, mas provar e finalizar o pagamento na loja física ("Clique e Retire" / Reserva inter-lojas).

---

## 2. Escopo do MVP Implementado

Em alinhamento direto com o documento de visão de produto e artefato "É / Não É / Faz / Não Faz", foram implementadas as funcionalidades essenciais:

| Módulo | Descrição Implementada |
| :--- | :--- |
| **Cockpit Omnichannel Unificado** | Interface web moderna em 3 colunas (Inbox, Chat WhatsApp, Cockpit de Ação) permitindo que o vendedor atenda, consulte estoque e emita reservas sem sair da tela. |
| **Caixa de Entrada Multi-Atendente** | Gestão de conversas por status (`Aberto`, `Em Atendimento`, `Reservado`, `Finalizado`), contador de não-lidas e busca por cliente/telefone. |
| **Estoque Global em Tempo Real (5 Filiais)** | Consulta instantânea da disponibilidade de calçados e vestuário por SKU, marca e numeração nas 5 filiais da rede, destacando estoque local vs. inter-lojas. |
| **Ficha Inteligente do Cliente (CRM)** | Perfil com foto, LTV, total de compras, grade de numerações personalizadas (Calçado, Roupa Top e Bottom), marcas prediletas, tags VIP e anotações editáveis. |
| **Ordem de Reserva (Clique e Retire)** | Geração em 1 clique de ordens de reserva com validação de malote inter-lojas, emissão de voucher com QR Code para balcão e prazo de 48h. |
| **Simulador de Interações WhatsApp** | Módulo de simulação com cenários reais guiados (ex: consulta de bota coturno esgotada em Charqueadas com reserva de Minas do Leão). |
| **Dashboard Gerencial** | Métricas de impacto: redução do tempo de resposta de 45 min para 2.4 min (-94.6%), taxa de conversão (68.2%), ranking das 5 filiais e demanda por numeração. |

---

## 3. Arquitetura da Solução

```text
LevConnect/
├── backend/
│   ├── main.py              # API FastAPI, rotas RESTful e servidor estático
│   └── database.py          # Dados simulados e modelo relacional em memória
├── frontend/
│   ├── index.html           # Interface do Cockpit Omnichannel (HTML5 semântico)
│   ├── css/
│   │   └── style.css        # Sistema de design moderno (Glassmorphism, dark/slate, CSS Variables)
│   ├── js/
│   │   ├── api.js           # Camada de comunicação assíncrona com o backend
│   │   ├── app.js           # Orquestrador da aplicação, modais e eventos globais
│   │   ├── chat.js          # Módulo de conversas e mensagens com visual WhatsApp
│   │   ├── customer.js      # CRM inteligente de moda e atualização de medidas
│   │   ├── stock.js         # Matriz de estoque cruzado das 5 filiais
│   │   ├── reservations.js  # Gestão de ordens Clique e Retire e vouchers
│   │   └── dashboard.js     # Indicadores executivos e gráficos de demanda
│   └── assets/              # Imagens reais de catálogo de calçados e vestuário
├── run.py                   # Script de inicialização facilitada
└── README.md                # Documentação técnica do projeto
```

---

## 4. Como Executar o Projeto

### Pré-requisitos
- Python 3.10 ou superior
- Bibliotecas: `fastapi` e `uvicorn` (já instaladas no ambiente)

### Passo a Passo

1. **Inicie o servidor:**
   ```powershell
   python run.py
   ```
   *Ou diretamente via uvicorn:*
   ```powershell
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Acesse no navegador:**
   Abra: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 5. Principais Rotas da API RESTful

- `GET /api/stores` - Lista as 5 filiais ativas da rede.
- `GET /api/chats` - Lista conversas com filtros por status (`open`, `in_progress`, `reserved`, `closed`).
- `GET /api/chats/{chat_id}` - Retorna conversa completa, histórico de mensagens e cliente vinculado.
- `POST /api/chats/{chat_id}/messages` - Envia mensagem de vendedor ou cliente.
- `GET /api/products` - Consulta catálogo e saldo de estoque por filial.
- `POST /api/reservations` - Cria reserva Clique e Retire, decrementando o estoque da filial de origem e gerando voucher no chat.
- `GET /api/reservations` - Lista reservas ativas com filtro de filial e status.
- `PUT /api/customers/{id}` - Atualiza a ficha inteligente de medidas e notas de atendimento.
- `POST /api/simulate-incoming` - Simula recebimento de mensagem WhatsApp com cenários reais de varejo.
- `GET /api/dashboard/stats` - Retorna indicadores de performance (KPIs).

---

## 6. Validação e Demonstração do Fluxo O2O

1. **Atendimento Rápido:** Selecione o chat de **Juliana Silveira**.
2. **Consulta de Estoque:** No painel lateral, abra a aba **Estoque 5 Filiais** e veja a **Bota Coturno Tratorada**.
3. **Reserva Inter-Lojas:** Note que em Charqueadas o tamanho 37 está zerado, mas há saldo em Minas do Leão.
4. **Geração com 1 Clique:** Clique em **Reservar Peça**, selecione Retirada em Charqueadas e Origem Minas do Leão.
5. **Resultado Instantâneo:** O comprovante de reserva é gerado no chat com código `#RES-XXXX` e prazo de 48h, sem sair da tela e sem perder a venda.
